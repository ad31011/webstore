"""Krijon 3 përdorues testues: admin, advanced, simple."""
from app.database import SessionLocal
from app.models import User, Role
from app.auth import hash_password

db = SessionLocal()
for username, role_name in [("admin", "admin"), ("advanced", "advanced"), ("simple", "simple")]:
    if not db.query(User).filter_by(username=username).first():
        role = db.query(Role).filter_by(name=role_name).first()
        db.add(User(username=username, email=f"{username}@store.com",
                    password_hash=hash_password(f"{username}123"), role_id=role.id))
db.commit()
print("Përdoruesit u krijuan: admin/admin123, advanced/advanced123, simple/simple123")