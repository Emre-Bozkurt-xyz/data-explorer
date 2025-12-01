from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.domain.schemas.dataset import (
    PaginatedDatasets,
    DatasetDetail,
)
from app.domain.schemas.record import PaginatedRecords, RecordDetail
from app.domain.services.dataset_service import (
    list_datasets as svc_list_datasets,
    get_dataset_detail as svc_get_dataset_detail,
)
from app.domain.services.record_service import (
    list_records as svc_list_records,
    get_record_detail as svc_get_record_detail,
)

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
    return svc_list_datasets(db=db, search=search, page=page, limit=limit)


@router.get("/{dataset_id}", response_model=DatasetDetail)
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
):
    """
    Get dataset detail including schema fields.
    """
    return svc_get_dataset_detail(db=db, dataset_id=dataset_id)


@router.get("/{dataset_id}/records", response_model=PaginatedRecords)
def get_dataset_records(
    dataset_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(
        None, description="Simple text search against record payload"
    ),
    db: Session = Depends(get_db),
):
    """
    List records for a dataset with pagination and simple text search.
    """
    return svc_list_records(
        db=db,
        dataset_id=dataset_id,
        page=page,
        limit=limit,
        search=search,
    )


@router.get("/{dataset_id}/records/{record_id}", response_model=RecordDetail)
def get_dataset_record_detail(
    dataset_id: str,
    record_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single record by id for a dataset.
    """
    return svc_get_record_detail(
        db=db,
        dataset_id=dataset_id,
        record_id=record_id,
    )
