# tests/domain/test_record_service.py
from sqlalchemy.orm import Session

from app.domain.services.record_service import list_records
from app.db.models import Dataset, Record
from tests.conftest import TestingSessionLocal


def test_list_records_service():
    db: Session = TestingSessionLocal()

    ds = Dataset(
        id="33333333-3333-3333-3333-333333333333",
        name="experiments_test",
        description="Experiments",
        row_count=3,
    )
    db.add(ds)
    db.flush()

    db.add_all(
        [
            Record(dataset_id=ds.id, payload={"symbol": "TP53", "value": 1.1}),
            Record(dataset_id=ds.id, payload={"symbol": "BRCA1", "value": 2.2}),
            Record(dataset_id=ds.id, payload={"symbol": "EGFR", "value": 3.3}),
        ]
    )
    db.commit()

    result = list_records(
        db=db,
        dataset_id=ds.id,
        page=1,
        limit=10,
        search=None,
        sort=None,
        filter_str=None,
    )

    assert result["total"] == 3
    assert len(result["items"]) == 3
