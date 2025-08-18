import asyncio
import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

try:
    from paapi5_python_sdk.api.default_api import DefaultApi
    from paapi5_python_sdk.search_items_request import SearchItemsRequest
    from paapi5_python_sdk.search_items_resource import SearchItemsResource
    from paapi5_python_sdk.api_client import ApiClient
    from paapi5_python_sdk.configuration import Configuration
except Exception:
    DefaultApi = None

@dataclass
class Config:
    associate_tag: str
    access_key: str
    secret_key: str
    marketplace: str = "www.amazon.it"
    min_discount_pct: int = 20
    max_results: int = 12

@dataclass
class DealItem:
    title: str
    url: str
    price: Optional[float]
    currency: Optional[str]
    list_price: Optional[float]
    discount_pct: Optional[int]
    image: Optional[str]

def load_config() -> Config:
    load_dotenv()
    missing = [k for k in ["AMAZON_ASSOCIATE_TAG", "AMAZON_ACCESS_KEY", "AMAZON_SECRET_KEY"] if not os.getenv(k)]
    if missing:
        raise RuntimeError("Variabili d'ambiente mancanti: " + ", ".join(missing))
    return Config(
        associate_tag=os.getenv("AMAZON_ASSOCIATE_TAG"),
        access_key=os.getenv("AMAZON_ACCESS_KEY"),
        secret_key=os.getenv("AMAZON_SECRET_KEY"),
        marketplace=os.getenv("AMAZON_MARKETPLACE", "www.amazon.it"),
        min_discount_pct=int(os.getenv("MIN_DISCOUNT_PCT", "20")),
        max_results=int(os.getenv("MAX_RESULTS", "12")),
    )

def build_paapi_client(cfg: Config):
    if DefaultApi is None:
        raise RuntimeError("paapi5-python-sdk non è installato.")
    configuration = Configuration()
    configuration.host = f"webservices.amazon.{cfg.marketplace.split('.')[-1]}"
    configuration.access_key = cfg.access_key
    configuration.secret_key = cfg.secret_key
    configuration.region = "eu-west-1" if cfg.marketplace.endswith(".it") else "us-east-1"
    api_client = ApiClient(configuration=configuration)
    return DefaultApi(api_client)

def compute_discount(list_price: Optional[float], price: Optional[float]) -> Optional[int]:
    if list_price and price and list_price > 0 and price <= list_price:
        return int(round((1 - price / list_price) * 100))
    return None

async def fetch_funko_deals(cfg: Config) -> List[DealItem]:
    api = build_paapi_client(cfg)
    resources = [
        SearchItemsResource.ITEMINFO_TITLE,
        SearchItemsResource.IMAGES_PRIMARY_MEDIUM,
        SearchItemsResource.OFFERS_LISTINGS_PRICE,
        SearchItemsResource.OFFERS_LISTINGS_SAVINGBASIS,
        SearchItemsResource.DETAILPAGEURL,
    ]
    collected: List[DealItem] = []
    max_pages = int(os.getenv("MAX_PAGES", "5"))

    for page in range(1, max_pages + 1):
        req = SearchItemsRequest(
            partner_tag=cfg.associate_tag,
            partner_type="Associates",
            marketplace=cfg.marketplace,
            keywords="Funko Pop",
            search_index="All",
            item_page=page,
            resources=resources,
        )
        resp = await asyncio.to_thread(api.search_items, req)
        items = getattr(resp, "search_result", None)
        if not items or not items.items:
            break
        for it in items.items:
            title = getattr(getattr(it, "item_info", None), "title", None)
            title = getattr(title, "display_value", None) if title else None
            url = getattr(it, "detail_page_url", None)
            image = getattr(it.images.primary.medium, "url", None) if getattr(it, "images", None) else None

            price, currency, list_price = None, None, None
            offers = getattr(it, "offers", None)
            if offers and offers.listings:
                listing = offers.listings[0]
                if listing.price:
                    price = float(listing.price.amount)
                    currency = listing.price.currency
                if listing.saving_basis:
                    list_price = float(listing.saving_basis.amount)
            discount_pct = compute_discount(list_price, price)

            if title and url and price and discount_pct and discount_pct >= cfg.min_discount_pct:
                collected.append(DealItem(title, url, price, currency, list_price, discount_pct, image))

    collected.sort(key=lambda d: (d.discount_pct or 0, -(d.price or 0)), reverse=True)
    return collected[: cfg.max_results]