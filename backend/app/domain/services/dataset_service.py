from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.domain.repositories.dataset_repo import (
    list_datasets as repo_list_datasets,
    get_dataset_with_fields as repo_get_dataset_with_fields,
)

from fastapi import HTTPException, status

def list_datasets(
    db: Session,
    search: Optional[str],
    page: int,
    limit: int,
) -> Dict[str, Any]:
    items, total = repo_list_datasets(db, search, page, limit)
    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
    }

def get_dataset_detail(db: Session, dataset_id: str) -> Any:
    dataset = repo_get_dataset_with_fields(db, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found",
        )
    return dataset