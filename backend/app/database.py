"""Lidhja me databazën PostgreSQL."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """Hap një sesion për çdo kërkesë dhe e mbyll në fund."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()