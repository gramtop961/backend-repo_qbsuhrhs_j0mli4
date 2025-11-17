"""
Database Schemas for Galaxy Bites Menu

Each Pydantic model maps to a MongoDB collection (lowercased class name).
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class MenuCategory(BaseModel):
    name: str = Field(..., description="Display name, e.g., Burgers, Fries, Coffees")
    slug: str = Field(..., description="URL-friendly unique slug")
    emoji: Optional[str] = Field(None, description="Fun emoji for UI")
    color: Optional[str] = Field(None, description="Tailwind color hint, e.g., rose, amber")
    featured: bool = Field(False, description="Whether this category is featured on home")

class AddOn(BaseModel):
    name: str
    price: float = Field(..., ge=0)

class MenuItem(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0, description="Base price for small/default size")
    category_slug: str = Field(..., description="Category slug reference")
    image: Optional[str] = Field(None, description="Image URL")
    tags: List[str] = Field(default_factory=list)
    sizes: Optional[List[Literal['S','M','L']]] = Field(default=None, description="Available sizes")
    size_price_delta: Optional[dict] = Field(default=None, description="{ 'M': +0.5, 'L': +1.0 }")
    addons: Optional[List[AddOn]] = Field(default=None, description="Optional add-ons")
    featured: bool = Field(False)

class OrderItem(BaseModel):
    item_id: str
    title: str
    quantity: int = Field(..., ge=1)
    base_price: float
    size: Optional[Literal['S','M','L']] = None
    addons: List[AddOn] = Field(default_factory=list)
    subtotal: float = Field(..., ge=0)

class Order(BaseModel):
    items: List[OrderItem]
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    total: float = Field(..., ge=0)
    status: Literal['received','preparing','ready','completed'] = 'received'
