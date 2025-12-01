from typing import List, Tuple, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import Bookmark


def list_bookmarks_for_user(
    db: Session,
    user_id: str,
    dataset_id: Optional[str],
    page: int,
    limit: int,
) -> Tuple[List[Bookmark], int]:
    base = select(Bookmark).where(Bookmark.user_id == user_id)
    count_base = select(func.count()).select_from(Bookmark).where(
        Bookmark.user_id == user_id
    )

    if dataset_id:
        base = base.where(Bookmark.dataset_id == dataset_id)
        count_base = count_base.where(Bookmark.dataset_id == dataset_id)

    total: int = db.scalar(count_base) or 0

    query = (
        base.order_by(Bookmark.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    items = db.scalars(query).all()
    return items, total


def get_bookmark_by_id(
    db: Session,
    bookmark_id: int,
    user_id: str,
) -> Optional[Bookmark]:
    stmt = select(Bookmark).where(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == user_id,
    )
    return db.scalars(stmt).first()


def get_bookmark_by_user_and_record(
    db: Session,
    user_id: str,
    record_id: int,
) -> Optional[Bookmark]:
    stmt = select(Bookmark).where(
        Bookmark.user_id == user_id,
        Bookmark.record_id == record_id,
    )
    return db.scalars(stmt).first()
