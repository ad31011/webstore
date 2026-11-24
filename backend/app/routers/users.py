from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Role
from ..schemas import UserCreate, UserUpdate
from ..auth import require_roles, hash_password, user_to_dict
from ..services import commit_or_409

router = APIRouter(prefix="/api/users", tags=["users"])
admin_only = require_roles("admin")


def get_role(db, name):
    role = db.query(Role).filter_by(name=name).first()
    if not role:
        raise HTTPException(400, "Rol i panjohur")
    return role


def get_user_or_404(db, user_id):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "Përdoruesi nuk u gjet")
    return u


@router.get("")
def list_users(db: Session = Depends(get_db), _=Depends(admin_only)):
    return [user_to_dict(u) for u in db.query(User).order_by(User.id).all()]


@router.post("", status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(admin_only)):
    u = User(username=data.username, email=data.email,
             password_hash=hash_password(data.password), role_id=get_role(db, data.role).id)
    db.add(u)
    commit_or_409(db, "Username ose email ekziston")
    db.refresh(u)
    return user_to_dict(u)


@router.put("/{user_id}")
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(admin_only)):
    u = get_user_or_404(db, user_id)
    if data.email is not None:
        u.email = data.email
    if data.password:
        u.password_hash = hash_password(data.password)
    if data.role:
        u.role_id = get_role(db, data.role).id
    if data.is_active is not None:
        u.is_active = data.is_active
    commit_or_409(db)
    db.refresh(u)
    return user_to_dict(u)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current=Depends(admin_only)):
    if user_id == current.id:
        raise HTTPException(400, "Nuk mund ta fshini veten")
    db.delete(get_user_or_404(db, user_id))
    db.commit()