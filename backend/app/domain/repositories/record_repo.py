from typing import Optional, Tuple, List

from sqlalchemy import select, func, Text, cast
from sqlalchemy.orm import Session

from app.db.models import Record


def list_records(
    db: Session,
    dataset_id: str,
    page: int,
    limit: int,
    search: Optional[str],
) -> Tuple[List[Record], int]:
    # Base query for this dataset
    base = select(Record).where(Record.dataset_id == dataset_id)
    count_base = select(func.count()).select_from(Record).where(
        Record.dataset_id == dataset_id
    )

    # Simple search: match JSON payload as text
    if search:
        pattern = f"%{search}%"
        base = base.where(cast(Record.payload, Text).ilike(pattern))
        count_base = count_base.where(cast(Record.payload, Text).ilike(pattern))

    total: int = db.scalar(count_base) or 0

    query = (
        base.order_by(Record.id.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    items = db.scalars(query).all()
    return items, total


def get_record_by_id(
    db: Session,
    dataset_id: str,
    record_id: int,
) -> Optional[Record]:
    stmt = select(Record).where(
        Record.dataset_id == dataset_id,
        Record.id == record_id,
    )
    return db.scalars(stmt).first()
