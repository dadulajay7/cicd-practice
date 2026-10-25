import pytest
from fastapi.testclient import TestClient

from app.main import add, app, divide, multiply

client = TestClient(app)


# --- Unit tests: plain functions, no HTTP ---


def test_add():
    assert add(2, 3) == 5


def test_divide():
    assert divide(10, 4) == 2.5


def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        divide(1, 0)


# --- API tests: exercise the HTTP layer ---


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_add_endpoint():
    response = client.get("/add", params={"a": 1, "b": 2})
    assert response.status_code == 200
    assert response.json() == {"result": 3}


def test_divide_by_zero_returns_400():
    response = client.get("/divide", params={"a": 1, "b": 0})
    assert response.status_code == 400


def test_multiply():
    assert multiply(3, 4) == 12


def test_multiply_endpoint():
    response = client.get("/multiply", params={"a": 3, "b": 4})
    assert response.status_code == 200
    assert response.json() == {"result": 12}
