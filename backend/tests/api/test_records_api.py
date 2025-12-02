# tests/api/test_records_api.py
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models import Dataset, Record
from tests.conftest import TestingSessionLocal


def _seed_dataset_with_records() -> str:
    db: Session = TestingSessionLocal()

    ds = Dataset(
        id="22222222-2222-2222-2222-222222222222",
        name="assays_test",
        description="Assays test dataset",
        row_count=2,
    )
    db.add(ds)
    db.flush()  # assign PKs

    dataset_id = ds.id  # capture before commit

    db.add_all(
        [
            Record(dataset_id=dataset_id, payload={"name": "A1", "value": 1.0}),
            Record(dataset_id=dataset_id, payload={"name": "A2", "value": 2.0}),
        ]
    )
    db.commit()
    db.close()

    return dataset_id


def test_list_records_basic(client: TestClient):
    dataset_id = _seed_dataset_with_records()

    resp = client.get(
        f"/api/v1/datasets/{dataset_id}/records?page=1&limit=25"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    payloads = [item["payload"]["name"] for item in data["items"]]
    assert "A1" in payloads and "A2" in payloads
