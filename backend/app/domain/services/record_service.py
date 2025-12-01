from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domain.repositories.record_repo import (
    list_records as repo_list_records,
    get_record_by_id as repo_get_record_by_id,
)


def list_records(
    db: Session,
    dataset_id: str,
    page: int,
    limit: int,
    search: Optional[str],
) -> Dict[str, Any]:
    items, total = repo_list_records(
        db=db,
        dataset_id=dataset_id,
        page=page,
        limit=limit,
        search=search,
    )

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
    }


def get_record_detail(
    db: Session,
    dataset_id: str,
    record_id: int,
) -> Any:
    record = repo_get_record_by_id(db, dataset_id=dataset_id, record_id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record {record_id} not found in dataset {dataset_id}",
        )
    return record
