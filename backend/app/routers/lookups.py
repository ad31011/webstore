from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import LookupIn, LookupOut
from ..auth import require_roles
from ..services import commit_or_409


def make_lookup_router(model, prefix: str) -> APIRouter:
    """Krijon GET/POST/PUT/DELETE për një tabelë të thjeshtë (id, name)."""
    router = APIRouter(prefix=f"/api/{prefix}", tags=[prefix])
    managers = require_roles("admin", "advanced")

    def get_or_404(db, item_id):
        obj = db.get(model, item_id)
        if not obj:
            raise HTTPException(404, "Nuk u gjet")
        return obj

    @router.get("", response_model=List[LookupOut])
    def list_items(db: Session = Depends(get_db)):
        return db.query(model).order_by(model.id).all()

    @router.post("", response_model=LookupOut, status_code=201)
    def create_item(data: LookupIn, db: Session = Depends(get_db), _=Depends(managers)):
        obj = model(name=data.name)
        db.add(obj)
        commit_or_409(db, "Ky emër ekziston")
        db.refresh(obj)
        return obj

    @router.put("/{item_id}", response_model=LookupOut)
    def update_item(item_id: int, data: LookupIn, db: Session = Depends(get_db), _=Depends(managers)):
        obj = get_or_404(db, item_id)
        obj.name = data.name
        commit_or_409(db, "Ky emër ekziston")
        db.refresh(obj)
        return obj

    @router.delete("/{item_id}", status_code=204)
    def delete_item(item_id: int, db: Session = Depends(get_db), _=Depends(managers)):
        db.delete(get_or_404(db, item_id))
        commit_or_409(db, "Përdoret nga produktet, nuk mund të fshihet")

    return router