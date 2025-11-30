from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.domain.repositories.dataset_repo import list_datasets as repo_list_datasets


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
