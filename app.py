# app.py
import os
import time
import asyncio
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

# importa le funzioni esistenti
from bot import fetch_funko_deals, load_config

app = FastAPI(title="Offerte Funko Pop")
templates = Jinja2Templates(directory="templates")

cfg = load_config()  # carica AMAZON_ACCESS_KEY, etc. dalle env vars

# CORS: per semplicità apriamo a tutti (se vuoi, metti solo il tuo dominio GitHub Pages)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# semplice cache in memoria per limitare chiamate PA-API
CACHE_TTL = int(os.getenv("CACHE_TTL", "900"))  # default 900s = 15min
_cache = {"deals": None, "ts": 0}

def ensure_affiliate_tag(url: str, tag: str) -> str:
    """Se manca il param 'tag' nell'URL Amazon, lo aggiunge."""
    if not url or not tag:
        return url
    try:
        p = urlparse(url)
        qs = dict(parse_qsl(p.query, keep_blank_values=True))
        if "tag" not in qs or not qs.get("tag"):
            qs["tag"] = tag
            new_q = urlencode(qs, doseq=True)
            return urlunparse((p.scheme, p.netloc, p.path, p.params, new_q, p.fragment))
        return url
    except Exception:
        return url

def deal_to_dict(d):
    return {
        "title": getattr(d, "title", None),
        "url": ensure_affiliate_tag(getattr(d, "url", None), cfg.associate_tag),
        "price": getattr(d, "price", None),
        "currency": getattr(d, "currency", None),
        "list_price": getattr(d, "list_price", None),
        "discount_pct": getattr(d, "discount_pct", None),
        "image": getattr(d, "image", None),
    }

async def _refresh_deals_if_needed():
    now = time.time()
    if _cache["deals"] and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["deals"]
    # chiama la funzione che usa PA-API (definita in bot.py)
    deals = await fetch_funko_deals(cfg)
    data = [deal_to_dict(d) for d in deals]
    _cache["deals"] = data
    _cache["ts"] = now
    return data

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # pagina di debug base (opzionale)
    return templates.TemplateResponse("index_dynamic.html", {"request": request, "api_origin": os.getenv("API_ORIGIN", "")})

@app.get("/deals")
async def get_deals():
    try:
        data = await _refresh_deals_if_needed()
        return JSONResponse({"deals": data})
    except Exception as e:
        # log reale su Render: print o logging
        print("Errore /deals:", e)
        return JSONResponse({"deals": [], "error": str(e)}, status_code=500)

@app.get("/health")
async def health():
    return {"status": "ok"}
