from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import LoginIn
from ..auth import verify_password, create_token, get_current_user, user_to_dict

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    """Kthen një token JWT nëse username/password janë të sakta."""
    user = db.query(User).filter_by(username=data.username).first()
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username ose fjalëkalim i gabuar")
    return {"access_token": create_token(user), "token_type": "bearer", "user": user_to_dict(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user_to_dict(user)