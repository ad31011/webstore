"""Autentikimi me JWT dhe kontrolli i qasjes sipas roleve (RBAC)."""
import os
import datetime as dt
import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = "HS256"
TOKEN_MINUTES = 120

bearer = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "role": user.role.name,
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=TOKEN_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def user_to_dict(u: User) -> dict:
    return {"id": u.id, "username": u.username, "email": u.email,
            "role": u.role.name, "is_active": u.is_active, "created_at": u.created_at}


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer),
                     db: Session = Depends(get_db)) -> User:
    """Lexon tokenin nga header-i 'Authorization: Bearer ...'."""
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token i pavlefshëm ose i skaduar")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Përdoruesi nuk ekziston ose është joaktiv")
    return user


def require_roles(*roles):
    """Dependency që lejon vetëm rolet e dhëna, p.sh. require_roles('admin')."""
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role.name not in roles:
            raise HTTPException(status_code=403, detail="Nuk keni leje për këtë veprim")
        return user
    return checker