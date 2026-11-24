from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Order, OrderItem, Product, Client
from ..schemas import OrderIn, StatusUpdate
from ..auth import require_roles
from ..services import SOLD_STATUSES, sold_quantity, final_price

router = APIRouter(prefix="/api/orders", tags=["orders"])
MANAGERS = require_roles("admin", "advanced")


def order_to_dict(o: Order) -> dict:
    return {
        "id": o.id, "client_id": o.client_id,
        "client_name": f"{o.client.first_name} {o.client.last_name}",
        "status": o.status, "total_amount": float(o.total_amount), "created_at": o.created_at,
        "items": [{"product_id": i.product_id, "product_name": i.product.name,
                   "quantity": i.quantity, "unit_price": float(i.unit_price)} for i in o.items],
    }


def get_or_404(db, order_id):
    o = db.get(Order, order_id)
    if not o:
        raise HTTPException(404, "Porosia nuk u gjet")
    return o


@router.post("", status_code=201)
def place_order(data: OrderIn, db: Session = Depends(get_db)):
    """Publik: klienti bën porosi. Kontrollon stokun dhe llogarit totalin."""
    if not db.get(Client, data.client_id):
        raise HTTPException(404, "Klienti nuk u gjet")
    order = Order(client_id=data.client_id, status="pending")
    total = 0.0
    for item in data.items:
        p = db.get(Product, item.product_id)
        if not p:
            raise HTTPException(404, f"Produkti {item.product_id} nuk u gjet")
        available = p.initial_quantity - sold_quantity(db, p.id)
        if item.quantity > available:
            raise HTTPException(400, f"Stok i pamjaftueshëm për '{p.name}' (në dispozicion: {available})")
        price = final_price(p)  # përfshin zbritjen aktive
        order.items.append(OrderItem(product_id=p.id, quantity=item.quantity, unit_price=price))
        total += price * item.quantity
    order.total_amount = round(total, 2)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order_to_dict(order)


@router.get("")
def list_orders(status: Optional[str] = None, db: Session = Depends(get_db), _=Depends(MANAGERS)):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    return [order_to_dict(o) for o in q.order_by(Order.id.desc()).all()]


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db), _=Depends(MANAGERS)):
    return order_to_dict(get_or_404(db, order_id))


@router.patch("/{order_id}/status")
def update_status(order_id: int, data: StatusUpdate, db: Session = Depends(get_db), _=Depends(MANAGERS)):
    o = get_or_404(db, order_id)
    # Kur porosia konfirmohet, kontrollo sërish stokun
    if data.status in SOLD_STATUSES and o.status not in SOLD_STATUSES:
        for it in o.items:
            available = it.product.initial_quantity - sold_quantity(db, it.product_id)
            if it.quantity > available:
                raise HTTPException(400, f"Stok i pamjaftueshëm për '{it.product.name}'")
    o.status = data.status
    db.commit()
    db.refresh(o)
    return order_to_dict(o)