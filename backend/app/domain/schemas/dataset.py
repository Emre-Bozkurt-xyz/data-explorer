from datetime import datetime
from typing import List

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
