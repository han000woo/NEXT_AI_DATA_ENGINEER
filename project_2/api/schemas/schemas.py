from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 상품 스키마
class ProductBase(BaseModel):
    name: str
    category : str = "Etc"
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# 주문 스키마
class OrderCreate(BaseModel):
    product_id: int
    quantity: int

class Order(OrderCreate):
    id: int
    total_price: float
    created_at: datetime
    class Config:
        from_attributes = True

class BulkOrderCreate(BaseModel) :
    orders: List[OrderCreate]
