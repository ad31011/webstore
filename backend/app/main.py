"""Pika hyrëse e API-së. Dokumentimi automatik: http://localhost:8000/docs"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import Gender, Category, Brand, Size, Color
from .routers import auth_routes, users, products, clients, orders, reports
from .routers.lookups import make_lookup_router

app = FastAPI(title="Web Store API", version="1.0",
              description="RESTful API për dyqanin online të rrobave")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

for r in (auth_routes.router, users.router, products.router,
          clients.router, orders.router, reports.router):
    app.include_router(r)

for model, prefix in [(Gender, "genders"), (Category, "categories"),
                      (Brand, "brands"), (Size, "sizes"), (Color, "colors")]:
    app.include_router(make_lookup_router(model, prefix))


@app.get("/")
def root():
    return {"message": "Web Store API funksionon. Dokumentimi: /docs"}