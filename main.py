from fastapi import FastAPI, Request
import json

app = FastAPI()

# Carica il file delle offerte (puoi aggiornarlo a mano ogni volta)
def load_deals():
    with open("deals.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/deals")
def get_deals(page: int = 1, per_page: int = 10):
    # Carica tutte le offerte
    deals = load_deals()
    start = (page - 1) * per_page
    end = start + per_page
    paginated_deals = deals[start:end]
    total_deals = len(deals)

    return {
        "deals": paginated_deals,
        "total": total_deals,
        "page": page,
        "per_page": per_page,
        "total_pages": (total_deals + per_page - 1) // per_page
    }

@app.get("/")
def index():
    return {"message": "Funko Pop! offerte in corso!"}
