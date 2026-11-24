from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import require_roles

router = APIRouter(prefix="/api/reports", tags=["reports"],
                   dependencies=[Depends(require_roles("admin", "advanced"))])


@router.get("/daily-earnings")
def daily_earnings(start: Optional[date] = None, end: Optional[date] = None, db: Session = Depends(get_db)):
    sql, params = "SELECT * FROM daily_earnings WHERE 1=1", {}
    if start:
        sql += " AND day >= :start"
        params["start"] = start
    if end:
        sql += " AND day <= :end"
        params["end"] = end
    sql += " ORDER BY day DESC"
    return [dict(r) for r in db.execute(text(sql), params).mappings()]


@router.get("/monthly-earnings")
def monthly_earnings(db: Session = Depends(get_db)):
    return [dict(r) for r in db.execute(text("SELECT * FROM monthly_earnings ORDER BY month DESC")).mappings()]


@router.get("/top-products")
def top_products(limit: int = 5, db: Session = Depends(get_db)):
    sql = text("SELECT * FROM top_selling_products ORDER BY total_sold DESC LIMIT :limit")
    return [dict(r) for r in db.execute(sql, {"limit": limit}).mappings()]