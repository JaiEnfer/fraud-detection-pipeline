import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
def test_store_transaction_in_db() -> None:
    payload = {
        "id": f"evt_{uuid.uuid4().hex}",
        "user_id": "u1",
        "merchant_id": "m1",
        "amount": 10.5,
        "currency": "EUR",
    }

    with TestClient(app) as client:
        resp = client.post("/transactions", json=payload)

    assert resp.status_code == 200
    assert resp.json()["status"] == "stored"
