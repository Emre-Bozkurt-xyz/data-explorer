from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import Dataset


def list_datasets(
    db: Session,
    search: Optional[str],
    page: int,
    limit: int,
) -> Tuple[List[Dataset], int]:
    # Base query
    query = select(Dataset)
    count_query = select(func.count()).select_from(Dataset)

    if search:
        pattern = f"%{search}%"
        query = query.where(Dataset.name.ilike(pattern))
        count_query = count_query.where(Dataset.name.ilike(pattern))

    # Total count
    total: int = db.scalar(count_query) or 0

    # Pagination + default sort: updated_at desc
    query = (
        query.order_by(Dataset.updated_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    items = db.scalars(query).all()
    return items, total
