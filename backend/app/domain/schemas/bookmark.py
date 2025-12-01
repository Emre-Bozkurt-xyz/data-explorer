from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Bookmark(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    dataset_id: str
    record_id: int
    note: str
    created_at: datetime


class BookmarkCreate(BaseModel):
    dataset_id: str
    record_id: int
    note: Optional[str] = ""


class PaginatedBookmarks(BaseModel):
    items: List[Bookmark]
    page: int
    limit: int
    total: int
