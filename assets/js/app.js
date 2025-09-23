// app.js - functions to render categories and handle filters/pagination
async function loadJsonOrFallback(path, fallback) {
    try {
        const res = await fetch(path, {
            cache: 'no-store'
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const j = await res.json();
        if (Array.isArray(j)) return j;
        if (j && Array.isArray(j.deals)) return j.deals;
        return fallback;
    } catch (e) {
        console.warn('loadJsonOrFallback', e);
        return fallback;
    }
}

function shorten(text, max = 90) {
    if (!text) return '';
    return text.length > max ? text.slice(0, max) + '…' : text;
}

function parsePrice(v) {
    if (!v) return 0;
    try {
        return parseFloat(String(v).replace(/[^0-9,\.]/g, '').replace(',', '.'))
    } catch (e) {
        return 0
    }
}

function calcDiscount(price, original) {
    let p = parsePrice(price);
    let o = parsePrice(original);
    if (!p || !o) return null;
    return Math.round((1 - p / o) * 100);
}

function renderCategory(opts) {
    const {
        data,
        containerId,
        pagerId,
        pageSizeSelectId,
        sortSelectId,
        minPriceInputId,
        maxPriceInputId,
        perPageDefault = 12
    } = opts;
    const container = document.getElementById(containerId);
    const pager = document.getElementById(pagerId);
    const pageSizeSelect = pageSizeSelectId ? document.getElementById(pageSizeSelectId) : null;
    const sortSelect = sortSelectId ? document.getElementById(sortSelectId) : null;
    const minInput = minPriceInputId ? document.getElementById(minPriceInputId) : null;
    const maxInput = maxPriceInputId ? document.getElementById(maxPriceInputId) : null;
    if (!container) return;
    let page = 1;

    function getPageSize() {
        return pageSizeSelect ? parseInt(pageSizeSelect.value) || perPageDefault : perPageDefault
    }

    function applyFilters(items) {
        let list = items.slice();
        const min = minInput ? parseFloat(minInput.value) || 0 : 0;
        const max = maxInput ? parseFloat(maxInput.value) || Infinity : Infinity;
        list = list.filter(i => {
            const p = parsePrice(i.price);
            return p >= min && p <= max
        });
        if (sortSelect && sortSelect.value === 'price-asc') list.sort((a, b) => parsePrice(a.price) - parsePrice(b.price));
        if (sortSelect && sortSelect.value === 'price-desc') list.sort((a, b) => parsePrice(b.price) - parsePrice(a.price));
        return list;
    }

    function draw() {
        const items = applyFilters(data);
        const pageSize = getPageSize();
        const total = items.length;
        const pages = Math.max(1, Math.ceil(total / pageSize));
        if (page > pages) page = pages;
        const start = (page - 1) * pageSize;
        const slice = items.slice(start, start + pageSize);
        container.innerHTML = '';
        if (slice.length === 0) {
            container.innerHTML = '<li class="note">Nessun risultato</li>';
            pager.innerHTML = '';
            return;
        }
        slice.forEach(item => {
            const li = document.createElement('li');
            li.className = 'item';
            const discount = calcDiscount(item.price, item.original_price);
            li.innerHTML = ` <div class="thumb"><img src="${item.image||'assets/img/placeholder.png'}" alt="${item.title||''}"> ${discount?'<span class="badge">-'+discount+'%</span>':''}</div> <div class="meta"> <h3>${shorten(item.title,100)}</h3> <div class="review">${item.review||'Recensione non disponibile.'}</div> <div class="price"><span class="current">${item.price?item.price+' €':''}</span>${item.original_price?'<span class="orig"> '+item.original_price+' €</span>':''}</div> <div class="actions"><a class="btn primary" href="${item.link}" target="_blank" rel="noopener noreferrer">Vai su Amazon</a> <button class="btn" onclick="shareItem('${(item.link||'')}', '${(item.title||'').replace(/'/g,"\\'")}' )">Condividi</button></div> </div>`;
            container.appendChild(li);
        });
        pager.innerHTML = '';
        for (let p = 1; p <= pages; p++) {
            const b = document.createElement('button');
            b.textContent = p;
            b.className = 'page-btn' + (p === page ? ' active' : '');
            b.onclick = () => {
                page = p;
                draw();
            };
            pager.appendChild(b);
        }
    }
    if (pageSizeSelect) pageSizeSelect.onchange = () => {
        page = 1;
        draw()
    };
    if (sortSelect) sortSelect.onchange = () => {
        page = 1;
        draw()
    };
    if (minInput) minInput.oninput = () => {
        page = 1;
        draw()
    };
    if (maxInput) maxInput.oninput = () => {
        page = 1;
        draw()
    };
    draw();
}

function shareItem(url, title) {
    const tag = 'tag=YOUR_ASSOCIATE_TAG';
    const full = url.includes('?') ? url + '&' + tag : url + '?' + tag;
    if (navigator.share) {
        navigator.share({
            title,
            url: full
        }).catch(() => {});
    } else {
        navigator.clipboard.writeText(full).then(() => alert('Link copiato negli appunti'));
    }
}
