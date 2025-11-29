"""
Pydantic Models for Request/Response
These define the "shapes" of data we send and receive
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Book related models
class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    price: float
    stock: int

class FindBooksRequest(BaseModel):
    q: str  # search query
    by: str = "title"  # search by "title" or "author"

class BookResponse(BaseModel):
    isbn: str
    title: str
    author: str
    price: float
    stock: int

# Order related models
class OrderItem(BaseModel):
    isbn: str
    qty: int

class CreateOrderRequest(BaseModel):
    customer_id: int
    items: List[OrderItem]

class OrderStatusResponse(BaseModel):
    order_id: int
    customer_name: str
    status: str
    total_amount: float
    items: List[Dict]

# Inventory models
class RestockBookRequest(BaseModel):
    isbn: str
    qty: int

class UpdatePriceRequest(BaseModel):
    isbn: str
    price: float

class InventorySummaryResponse(BaseModel):
    low_stock_books: List[Dict]

# Chat models
class ChatMessage(BaseModel):
    session_id: str
    role: str
    content: str

class ToolCallRecord(BaseModel):
    session_id: str
    name: str
    args_json: str
    result_json: str

# Agent tool input models
class OrderStatusInput(BaseModel):
    order_id: int

class InventorySummaryInput(BaseModel):
    # No fields needed - empty input
    pass