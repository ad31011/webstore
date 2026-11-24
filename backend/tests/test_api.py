from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def auth_header(username="admin", password="admin123"):
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_login_wrong_password():
    r = client.post("/api/auth/login", json={"username": "admin", "password": "gabim"})
    assert r.status_code == 401


def test_search_by_gender():
    r = client.get("/api/products/search", params={"gender": "men"})
    assert r.status_code == 200
    assert all(p["gender"] == "Men" for p in r.json())


def test_real_time_quantity():
    r = client.get("/api/products/1/quantity")
    d = r.json()
    assert d["current_quantity"] == d["initial_quantity"] - d["sold_quantity"]


def test_reports_need_auth():
    assert client.get("/api/reports/daily-earnings").status_code in (401, 403)


def test_simple_user_cannot_see_reports():
    r = client.get("/api/reports/daily-earnings", headers=auth_header("simple", "simple123"))
    assert r.status_code == 403


def test_admin_reports():
    r = client.get("/api/reports/top-products", headers=auth_header())
    assert r.status_code == 200