# tests/api/test_datasets_api.py
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Dataset
from app.main import app


def test_list_datasets_empty(client: TestClient):
    resp = client.get("/api/v1/datasets?page=1&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_and_get_dataset(client: TestClient):
    # Insert a dataset directly using the test DB session override
    from tests.conftest import TestingSessionLocal

    db: Session = TestingSessionLocal()
    ds = Dataset(
      id="11111111-1111-1111-1111-111111111111",
      name="genes_test",
      description="Test dataset",
      row_count=42,
    )
    db.add(ds)
    db.commit()

    # List
    resp = client.get("/api/v1/datasets?page=1&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "genes_test"

    # Detail
    ds_id = data["items"][0]["id"]
    resp2 = client.get(f"/api/v1/datasets/{ds_id}")
    assert resp2.status_code == 200
    detail = resp2.json()
    assert detail["name"] == "genes_test"
    assert detail["row_count"] == 42
