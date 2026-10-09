import sqlite3
from datetime import datetime

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import app.api.orders as routes
from app.main import app
from app.core.config import settings
from app.schemas.order import Order

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "database_path", tmp_path / "data" / "orders.sqlite3")


@pytest.fixture
def extracted_order(monkeypatch):
    order = Order(
        summary="Dvije pizze",
        items=[dict(name="Pizza", quantity=2, unit=None, details=[])],
        customer=dict(name=None, phone=None, address=None),
        fulfillment=None,
        requested_time=None,
        notes=[],
        questions=[],
    )

    async def fake_extract(text):
        assert text == "Dvije pizze"
        return order

    monkeypatch.setattr(routes, "extract_order", fake_extract)
    return order


def test_initial_orders_empty():
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_blank_transcript():
    assert client.post("/api/orders/extract", json={"text": "   "}).status_code == 422
    assert client.get("/api/orders").json() == []


def test_long_transcript():
    assert client.post("/api/orders/extract", json={"text": "a" * 15001}).status_code == 422
    assert client.get("/api/orders").json() == []


def test_missing_key(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")
    assert client.post("/api/orders/extract", json={"text": "Dvije pizze"}).status_code == 503
    assert client.get("/api/orders").json() == []


def test_success_is_saved_and_listed(extracted_order):
    response = client.post("/api/orders/extract", json={"text": " Dvije pizze "})
    assert response.status_code == 200
    saved = response.json()
    assert saved["id"]
    assert datetime.fromisoformat(saved["created_at"].replace("Z", "+00:00")).tzinfo is not None
    assert saved["completed"] is False
    assert saved["order"] == extracted_order.model_dump()
    assert client.get("/api/orders").json() == [saved]


def test_newest_order_is_first(extracted_order):
    first = client.post("/api/orders/extract", json={"text": "Dvije pizze"}).json()
    second = client.post("/api/orders/extract", json={"text": "Dvije pizze"}).json()
    assert first["id"] != second["id"]
    assert client.get("/api/orders").json() == [second, first]


def test_completion_persists_and_can_be_reopened(extracted_order):
    saved = client.post("/api/orders/extract", json={"text": "Dvije pizze"}).json()
    endpoint = f"/api/orders/{saved['id']}"
    response = client.patch(endpoint, json={"completed": True})
    assert response.status_code == 200
    assert response.json() == {**saved, "completed": True}

    # A fresh connection reads the committed status from disk.
    with sqlite3.connect(settings.database_path) as connection:
        assert connection.execute(
            "SELECT completed FROM orders WHERE id = ?", (saved["id"],)
        ).fetchone() == (1,)
    with TestClient(app) as fresh_client:
        assert fresh_client.get("/api/orders").json() == [{**saved, "completed": True}]
        response = fresh_client.patch(endpoint, json={"completed": False})
        assert response.status_code == 200
        assert response.json() == saved
    assert client.get("/api/orders").json() == [saved]


def test_unknown_order_returns_404():
    response = client.patch("/api/orders/missing", json={"completed": True})
    assert response.status_code == 404
    assert client.get("/api/orders").json() == []


def test_invalid_completion_does_not_change_order(extracted_order):
    saved = client.post("/api/orders/extract", json={"text": "Dvije pizze"}).json()
    response = client.patch(f"/api/orders/{saved['id']}", json={"completed": "false"})
    assert response.status_code == 422
    assert client.get("/api/orders").json() == [saved]


def test_failed_extraction_is_not_saved(monkeypatch):
    async def failed_extract(text):
        raise HTTPException(502, "Obrada nije uspjela.")

    monkeypatch.setattr(routes, "extract_order", failed_extract)
    assert client.post("/api/orders/extract", json={"text": "Dvije pizze"}).status_code == 502
    assert client.get("/api/orders").json() == []


def test_empty_extraction_is_not_saved(extracted_order):
    extracted_order.items = []
    response = client.post("/api/orders/extract", json={"text": "Dvije pizze"})
    assert response.status_code == 422
    assert "nisu pronađene stavke" in response.json()["detail"]
    assert client.get("/api/orders").json() == []


def test_cors_allows_completion_updates():
    response = client.options(
        "/api/orders/example",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert "PATCH" in response.headers["access-control-allow-methods"]
