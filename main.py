import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import MenuCategory, MenuItem, Order

app = FastAPI(title="Galaxy Bites API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Galaxy Bites backend ready"}

@app.get("/test")
def test_database():
    resp = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            resp["database"] = "✅ Available"
            resp["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            resp["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            try:
                resp["collections"] = db.list_collection_names()
                resp["database"] = "✅ Connected & Working"
                resp["connection_status"] = "Connected"
            except Exception as e:
                resp["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            resp["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        resp["database"] = f"❌ Error: {str(e)[:80]}"
    return resp

# Seed data models
class SeedResponse(BaseModel):
    inserted_categories: int
    inserted_items: int

@app.post("/api/seed", response_model=SeedResponse)
def seed_menu():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    categories = [
        {"name":"Cosmic Burgers","slug":"burgers","emoji":"🍔","color":"rose","featured":True},
        {"name":"Astro Fries","slug":"fries","emoji":"🍟","color":"amber","featured":True},
        {"name":"Rocket Shakes","slug":"shakes","emoji":"🥤","color":"violet","featured":True},
        {"name":"Starlite Coffee","slug":"coffee","emoji":"☕","color":"stone","featured":True},
        {"name":"Nebula Treats","slug":"treats","emoji":"🍩","color":"pink","featured":False},
    ]

    items = [
        {"title":"Meteor Mac","description":"Double patty, comet sauce, star pickles","price":6.99,"category_slug":"burgers","tags":["popular"],"sizes":["S","M","L"],"size_price_delta":{"M":1.0,"L":2.0},"featured":True},
        {"title":"Lunar Crisps","description":"Shoestring fries dusted with moon salt","price":2.99,"category_slug":"fries","tags":["vegan"],"sizes":["S","M","L"],"size_price_delta":{"M":0.7,"L":1.4}},
        {"title":"Milky Way Shake","description":"Vanilla base with galaxy swirl","price":4.49,"category_slug":"shakes","sizes":["M","L"],"size_price_delta":{"L":0.8}},
        {"title":"Supernova Latte","description":"Bold espresso with stardust foam","price":3.99,"category_slug":"coffee","sizes":["S","M","L"],"size_price_delta":{"M":0.6,"L":1.1}},
        {"title":"Comet Donut","description":"Glazed ring with meteor crumble","price":1.99,"category_slug":"treats","tags":["sweet"],"featured":True},
    ]

    inserted_c = 0
    for c in categories:
        existing = db["menucategory"].find_one({"slug": c["slug"]})
        if not existing:
            create_document("menucategory", MenuCategory(**c))
            inserted_c += 1

    inserted_i = 0
    for it in items:
        existing = db["menuitem"].find_one({"title": it["title"]})
        if not existing:
            create_document("menuitem", MenuItem(**it))
            inserted_i += 1

    return SeedResponse(inserted_categories=inserted_c, inserted_items=inserted_i)

@app.get("/api/categories")
def list_categories():
    cats = get_documents("menucategory")
    for c in cats:
        c["_id"] = str(c["_id"])  # serialize
    return cats

@app.get("/api/items")
@app.get("/api/items/{category_slug}")
def list_items(category_slug: Optional[str] = None):
    filt = {"category_slug": category_slug} if category_slug else {}
    items = get_documents("menuitem", filt)
    for it in items:
        it["_id"] = str(it["_id"])  # serialize
    return items

class OrderRequest(Order):
    pass

@app.post("/api/order")
def create_order(order: OrderRequest):
    order_id = create_document("order", order)
    return {"order_id": order_id, "status": "received"}
