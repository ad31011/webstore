from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product, Discount, Order, OrderItem, Gender, Category, Brand, Size, Color
from ..schemas import ProductIn, StockUpdate, DiscountIn
from ..auth import require_roles
from ..services import SOLD_STATUSES, sold_quantity, product_to_dict, commit_or_409

router = APIRouter(prefix="/api/products", tags=["products"])
ALL_STAFF = require_roles("admin", "advanced", "simple")
MANAGERS = require_roles("admin", "advanced")
ADMIN = require_roles("admin")


def get_or_404(db, product_id):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Produkti nuk u gjet")
    return p


def norm(value: str) -> str:
    """'tommy_hilfiger' -> 'tommy hilfiger'"""
    return value.replace("_", " ").strip().lower()


@router.get("")
def list_products(db: Session = Depends(get_db)):
    return [product_to_dict(db, p) for p in db.query(Product).order_by(Product.id).all()]


# KUJDES: /search duhet të jetë PARA /{product_id}
@router.get("/search")
def search_products(q: Optional[str] = None, gender: Optional[str] = None,
                    category: Optional[str] = None, brand: Optional[str] = None,
                    size: Optional[str] = None, color: Optional[str] = None,
                    price_min: Optional[float] = None, price_max: Optional[float] = None,
                    availability: Optional[str] = None,  # in_stock | out_of_stock
                    db: Session = Depends(get_db)):
    """Kërkim i avancuar; filtrat mund të kombinohen."""
    # Nën-query: sa është shitur nga secili produkt
    sold_sq = (db.query(OrderItem.product_id.label("pid"),
                        func.sum(OrderItem.quantity).label("sold"))
                 .join(Order, Order.id == OrderItem.order_id)
                 .filter(Order.status.in_(SOLD_STATUSES))
                 .group_by(OrderItem.product_id).subquery())
    current = Product.initial_quantity - func.coalesce(sold_sq.c.sold, 0)

    query = db.query(Product).outerjoin(sold_sq, sold_sq.c.pid == Product.id)

    for value, model, fk in [(gender, Gender, Product.gender_id),
                             (category, Category, Product.category_id),
                             (brand, Brand, Product.brand_id),
                             (size, Size, Product.size_id),
                             (color, Color, Product.color_id)]:
        if value:
            query = query.join(model, model.id == fk).filter(func.lower(model.name) == norm(value))

    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)
    if availability == "in_stock":
        query = query.filter(current > 0)
    elif availability == "out_of_stock":
        query = query.filter(current <= 0)

    return [product_to_dict(db, p) for p in query.order_by(Product.id).all()]


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_to_dict(db, get_or_404(db, product_id))


@router.get("/{product_id}/quantity")
def get_quantity(product_id: int, db: Session = Depends(get_db)):
    """Stoku në kohë reale = fillestar - i shitur."""
    p = get_or_404(db, product_id)
    sold = sold_quantity(db, p.id)
    return {"product_id": p.id, "name": p.name, "initial_quantity": p.initial_quantity,
            "sold_quantity": sold, "current_quantity": p.initial_quantity - sold}


@router.post("", status_code=201)
def create_product(data: ProductIn, db: Session = Depends(get_db), _=Depends(ALL_STAFF)):
    p = Product(**data.model_dump())
    db.add(p)
    commit_or_409(db, "ID e pavlefshme për kategori/brend/masë/ngjyrë/gjini")
    db.refresh(p)
    return product_to_dict(db, p)


@router.put("/{product_id}")
def update_product(product_id: int, data: ProductIn, db: Session = Depends(get_db), _=Depends(ALL_STAFF)):
    p = get_or_404(db, product_id)
    for key, value in data.model_dump().items():
        setattr(p, key, value)
    commit_or_409(db, "ID e pavlefshme për kategori/brend/masë/ngjyrë/gjini")
    db.refresh(p)
    return product_to_dict(db, p)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), _=Depends(MANAGERS)):
    db.delete(get_or_404(db, product_id))
    commit_or_409(db, "Produkti ka porosi, nuk mund të fshihet")


@router.patch("/{product_id}/stock")
def update_stock(product_id: int, data: StockUpdate, db: Session = Depends(get_db), _=Depends(ALL_STAFF)):
    p = get_or_404(db, product_id)
    sold = sold_quantity(db, p.id)
    if data.initial_quantity < sold:
        raise HTTPException(400, f"Sasia s'mund të jetë më e vogël se e shitura ({sold})")
    p.initial_quantity = data.initial_quantity
    db.commit()
    db.refresh(p)
    return product_to_dict(db, p)


def discount_to_dict(d):
    return {"id": d.id, "product_id": d.product_id, "percentage": float(d.percentage),
            "start_date": d.start_date, "end_date": d.end_date, "is_active": d.is_active}


@router.get("/{product_id}/discounts")
def list_discounts(product_id: int, db: Session = Depends(get_db)):
    return [discount_to_dict(d) for d in get_or_404(db, product_id).discounts]


@router.post("/{product_id}/discounts", status_code=201)
def add_discount(product_id: int, data: DiscountIn, db: Session = Depends(get_db), _=Depends(ADMIN)):
    p = get_or_404(db, product_id)
    if data.end_date < data.start_date:
        raise HTTPException(400, "end_date duhet të jetë pas start_date")
    d = Discount(product_id=p.id, **data.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return discount_to_dict(d)


@router.delete("/{product_id}/discounts/{discount_id}", status_code=204)
def delete_discount(product_id: int, discount_id: int, db: Session = Depends(get_db), _=Depends(ADMIN)):
    d = db.get(Discount, discount_id)
    if not d or d.product_id != product_id:
        raise HTTPException(404, "Zbritja nuk u gjet")
    db.delete(d)
    db.commit()