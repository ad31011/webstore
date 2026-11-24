"""Funksione ndihmëse: stoku në kohë reale, zbritjet, ruajtja."""
from datetime import date
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from .models import Order, OrderItem, Product

# Vetëm këto statuse llogariten si "të shitura"
SOLD_STATUSES = ("confirmed", "shipped", "delivered")


def sold_quantity(db, product_id: int) -> int:
    """Totali i njësive të shitura në porositë e konfirmuara."""
    return (db.query(func.coalesce(func.sum(OrderItem.quantity), 0))
              .select_from(OrderItem)
              .join(Order, Order.id == OrderItem.order_id)
              .filter(OrderItem.product_id == product_id, Order.status.in_(SOLD_STATUSES))
              .scalar())


def active_discount(p: Product):
    today = date.today()
    for d in p.discounts:
        if d.is_active and d.start_date <= today <= d.end_date:
            return d
    return None


def final_price(p: Product) -> float:
    d = active_discount(p)
    price = float(p.price)
    return round(price * (1 - float(d.percentage) / 100), 2) if d else price


def product_to_dict(db, p: Product) -> dict:
    sold = sold_quantity(db, p.id)
    d = active_discount(p)
    return {
        "id": p.id, "name": p.name, "description": p.description,
        "price": float(p.price),
        "discount_percent": float(d.percentage) if d else 0,
        "final_price": final_price(p),
        "initial_quantity": p.initial_quantity,
        "sold_quantity": sold,
        "current_quantity": p.initial_quantity - sold,
        "gender": p.gender.name if p.gender else None,
        "category": p.category.name if p.category else None,
        "brand": p.brand.name if p.brand else None,
        "color": p.color.name if p.color else None,
        "size": p.size.name if p.size else None,
        "gender_id": p.gender_id, "category_id": p.category_id, "brand_id": p.brand_id,
        "color_id": p.color_id, "size_id": p.size_id,
    }


def commit_or_409(db, msg="Të dhëna dublikatë ose të lidhura me rekorde të tjera"):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=msg)