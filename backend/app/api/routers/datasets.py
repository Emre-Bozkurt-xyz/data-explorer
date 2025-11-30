from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.domain.schemas.dataset import PaginatedDatasets
from app.domain.services.dataset_service import list_datasets

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])


@router.get("", response_model=PaginatedDatasets)
def get_datasets(
    search: Optional[str] = Query(None, description="Search by dataset name"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    List datasets with simple search + pagination.
    """
    return list_datasets(db=db, search=search, page=page, limit=limit)
