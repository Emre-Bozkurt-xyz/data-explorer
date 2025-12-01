from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.api.deps import get_current_user_id
from app.domain.schemas.bookmark import (
    PaginatedBookmarks,
    Bookmark,
    BookmarkCreate,
)
from app.domain.services.bookmark_service import (
    list_bookmarks as svc_list_bookmarks,
    create_bookmark as svc_create_bookmark,
    delete_bookmark as svc_delete_bookmark,
)

router = APIRouter(prefix="/api/v1/bookmarks", tags=["bookmarks"])


@router.get("", response_model=PaginatedBookmarks)
def get_bookmarks(
    dataset_id: Optional[str] = Query(
        None, description="Filter bookmarks by dataset id"
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    List bookmarks for current user, optionally filtered by dataset.
    """
    return svc_list_bookmarks(
        db=db,
        user_id=user_id,
        dataset_id=dataset_id,
        page=page,
        limit=limit,
    )


@router.post("", response_model=Bookmark, status_code=status.HTTP_201_CREATED)
def post_bookmark(
    payload: BookmarkCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a bookmark for the current user.
    """
    return svc_create_bookmark(
        db=db,
        user_id=user_id,
        payload=payload,
    )


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark_endpoint(
    bookmark_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a bookmark owned by the current user.
    """
    svc_delete_bookmark(
        db=db,
        user_id=user_id,
        bookmark_id=bookmark_id,
    )
    return
