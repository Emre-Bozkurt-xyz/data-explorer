from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict


class RecordSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payload: Dict[str, Any]


class PaginatedRecords(BaseModel):
    items: List[RecordSummary]
    page: int
    limit: int
    total: int


class RecordDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: str
    payload: Dict[str, Any]
