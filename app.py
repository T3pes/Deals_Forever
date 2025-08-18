import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bot import fetch_funko_deals, load_config

app = FastAPI(title="Offerte Funko Pop")
templates = Jinja2Templates(directory="templates")

cfg = load_config()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    deals = await fetch_funko_deals(cfg)
    return templates.TemplateResponse("index.html", {"request": request, "deals": deals})