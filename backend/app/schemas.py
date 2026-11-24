"""Skemat Pydantic: validojnë JSON-in që vjen në API."""
from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

RoleName = Literal["admin", "advanced", "simple"]
OrderStatus = Literal["pending", "confirmed", "shipped", "delivered", "cancelled"]


class LookupIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class LookupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    price: float = Field(ge=0)
    initial_quantity: int = Field(ge=0)
    gender_id: Optional[int] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    color_id: Optional[int] = None
    size_id: Optional[int] = None


class StockUpdate(BaseModel):
    initial_quantity: int = Field(ge=0)


class DiscountIn(BaseModel):
    percentage: float = Field(gt=0, le=100)
    start_date: date
    end_date: date


class LoginIn(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=6)
    role: RoleName = "simple"


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)
    role: Optional[RoleName] = None
    is_active: Optional[bool] = None


class ClientIn(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderIn(BaseModel):
    client_id: int
    items: List[OrderItemIn] = Field(min_length=1)


class StatusUpdate(BaseModel):
    status: OrderStatus