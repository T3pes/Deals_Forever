// assets/js/render.js

function renderCategory({ dataFile, containerId, pagerId, perPage = 12 }) {
  const container = document.getElementById(containerId);
  const pager = document.getElementById(pagerId);

  if (!container) return;

  fetch(dataFile)
    .then(res => res.json())
    .then(data => {
      if (!Array.isArray(data)) {
        container.innerHTML = "<li>❌ Formato JSON non valido</li>";
        return;
      }

      let page = 1;
      const total = data.length;
      const pages = Math.ceil(total / perPage);

      function renderPage() {
        const start = (page - 1) * perPage;
        const end = start + perPage;
        const items = data.slice(start, end);

        container.innerHTML = "";

        items.forEach(item => {
          const li = document.createElement("li");
          li.className = "card item";

          const discount = item.original_price && item.price
            ? Math.round(((parseFloat(item.original_price) - parseFloat(item.price)) / parseFloat(item.original_price)) * 100)
            : null;

          li.innerHTML = `
            <div class="thumb">
              <img src="${item.image}" alt="${item.title}">
              ${discount ? `<span class="badge">-${discount}%</span>` : ""}
            </div>
            <div class="meta">
              <h3>${shorten(item.title, 90)}</h3>
              <p class="review">${item.review || "⭐ Breve recensione non disponibile"}</p>
              <p>
                <strong>💰 ${item.price}</strong>
                ${item.original_price ? `<span class="old">${item.original_price}</span>` : ""}
              </p>
              <div class="actions">
                <a href="${item.link}" class="btn primary" target="_blank" rel="nofollow noopener">Vai su Amazon</a>
                <button class="btn secondary" onclick="shareLink('${item.link}')">Condividi</button>
              </div>
            </div>
          `;
          container.appendChild(li);
        });

        // Paginazione
        pager.innerHTML = "";
        for (let i = 1; i <= pages; i++) {
          const b = document.createElement("button");
          b.textContent = i;
          b.className = i === page ? "active" : "";
          b.addEventListener("click", () => {
            page = i;
            renderPage();
          });
          pager.appendChild(b);
        }
      }

      renderPage();
    })
    .catch(err => {
      console.error("Errore caricamento JSON:", err);
      container.innerHTML = "<li>❌ Errore nel caricamento delle offerte</li>";
    });
}

// ✂️ accorcia titolo
function shorten(text, max = 100) {
  return text.length > max ? text.slice(0, max) + "…" : text;
}

// 📲 condivisione con referral Amazon
function shareLink(url) {
  const tag = "?tag=iltuoid-21"; // 🔗 inserisci qui il tuo Associate Tag
  const fullUrl = url.includes("?") ? url + "&" + tag.slice(1) : url + tag;

  if (navigator.share) {
    navigator.share({
      title: "Dai un'occhiata a questa offerta!",
      url: fullUrl
    });
  } else {
    navigator.clipboard.writeText(fullUrl);
    alert("🔗 Link copiato negli appunti!");
  }
}

// === Avvio rendering categorie ===
document.addEventListener("DOMContentLoaded", () => {
  renderCategory({ dataFile: "data/funko.json", containerId: "funko-list", pagerId: "funko-pager" });
  renderCategory({ dataFile: "data/tech.json", containerId: "tech-list", pagerId: "tech-pager" });
  renderCategory({ dataFile: "data/casa.json", containerId: "casa-list", pagerId: "casa-pager" });
  renderCategory({ dataFile: "data/sport.json", containerId: "sport-list", pagerId: "sport-pager" });
});
