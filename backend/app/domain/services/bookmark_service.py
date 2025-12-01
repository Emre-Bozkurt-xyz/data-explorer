from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models import Bookmark
from app.domain.schemas.bookmark import BookmarkCreate
from app.domain.repositories.bookmark_repo import (
    list_bookmarks_for_user as repo_list_bookmarks_for_user,
    get_bookmark_by_id as repo_get_bookmark_by_id,
    get_bookmark_by_user_and_record as repo_get_bookmark_by_user_and_record,
)


def list_bookmarks(
    db: Session,
    user_id: str,
    dataset_id: Optional[str],
    page: int,
    limit: int,
) -> Dict[str, Any]:
    items, total = repo_list_bookmarks_for_user(
        db=db,
        user_id=user_id,
        dataset_id=dataset_id,
        page=page,
        limit=limit,
    )
    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
    }


def create_bookmark(
    db: Session,
    user_id: str,
    payload: BookmarkCreate,
) -> Bookmark:
    # Enforce uniqueness per (user, record)
    existing = repo_get_bookmark_by_user_and_record(
        db=db,
        user_id=user_id,
        record_id=payload.record_id,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bookmark already exists for this record",
        )

    bm = Bookmark(
        user_id=user_id,
        dataset_id=payload.dataset_id,
        record_id=payload.record_id,
        note=payload.note or "",
    )
    db.add(bm)
    db.commit()
    db.refresh(bm)
    return bm


def delete_bookmark(
    db: Session,
    user_id: str,
    bookmark_id: int,
) -> None:
    bm = repo_get_bookmark_by_id(db, bookmark_id=bookmark_id, user_id=user_id)
    if not bm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    db.delete(bm)
    db.commit()
