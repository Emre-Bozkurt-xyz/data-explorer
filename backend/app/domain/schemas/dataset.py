from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DatasetSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    row_count: int
    updated_at: datetime


class PaginatedDatasets(BaseModel):
    items: List[DatasetSummary]
    page: int
    limit: int
    total: int


class DatasetFieldSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    null_frac: float
    distinct_count: Optional[int] = None
    example_value: Optional[dict] = None


class DatasetDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    row_count: int
    updated_at: datetime
    fields: List[DatasetFieldSummary]
