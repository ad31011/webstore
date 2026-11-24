from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Client
from ..schemas import ClientIn
from ..auth import require_roles
from ..services import commit_or_409

router = APIRouter(prefix="/api/clients", tags=["clients"])
MANAGERS = require_roles("admin", "advanced")


def client_to_dict(c):
    return {"id": c.id, "first_name": c.first_name, "last_name": c.last_name,
            "email": c.email, "phone": c.phone, "address": c.address}


def get_or_404(db, client_id):
    c = db.get(Client, client_id)
    if not c:
        raise HTTPException(404, "Klienti nuk u gjet")
    return c


@router.post("")
def create_client(data: ClientIn, db: Session = Depends(get_db)):
    """Publik: nëse emaili ekziston, kthen klientin ekzistues."""
    existing = db.query(Client).filter_by(email=data.email).first()
    if existing:
        return client_to_dict(existing)
    c = Client(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return client_to_dict(c)


@router.get("")
def list_clients(db: Session = Depends(get_db), _=Depends(MANAGERS)):
    return [client_to_dict(c) for c in db.query(Client).order_by(Client.id).all()]


@router.get("/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db), _=Depends(MANAGERS)):
    return client_to_dict(get_or_404(db, client_id))


@router.put("/{client_id}")
def update_client(client_id: int, data: ClientIn, db: Session = Depends(get_db), _=Depends(MANAGERS)):
    c = get_or_404(db, client_id)
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    commit_or_409(db, "Email ekziston")
    db.refresh(c)
    return client_to_dict(c)


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    db.delete(get_or_404(db, client_id))
    commit_or_409(db, "Klienti ka porosi, nuk mund të fshihet")