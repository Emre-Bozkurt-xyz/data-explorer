from dataclasses import dataclass
from typing import Optional, Tuple, List, Any, Literal

from sqlalchemy import select, func, Text, cast, text
from sqlalchemy.orm import Session

from app.db.models import Record


# ---- Filter model ---- #

Op = Literal["eq", "ne", "lt", "gt", "le", "ge", "like"]


@dataclass
class FilterClause:
    name: str
    op: Op
    value: Any


# ---- Helpers ---- #

def _apply_filters(query, filters: Optional[List[FilterClause]]):
    """
    Apply JSONB-based filters on Record.payload.

    We treat payload as JSON and access fields with payload->>'field'.
    """
    if not filters:
        return query

    for f in filters:
        col = text(f"(payload->>'{f.name}')")

        if f.op == "like":
            # case-insensitive substring match
            query = query.where(text(f"{col} ILIKE :v")).params(v=f"%{f.value}%")
        elif f.op in ("eq", "ne"):
            sql_op = "=" if f.op == "eq" else "!="
            query = query.where(text(f"{col} {sql_op} :v")).params(v=str(f.value))
        elif f.op in ("gt", "ge", "lt", "le"):
            sql_op = {
                "gt": ">",
                "ge": ">=",
                "lt": "<",
                "le": "<=",
            }[f.op]
            # cast to numeric and compare; if cast fails, Postgres will error (OK for MVP)
            query = query.where(
                text(f"({col})::numeric {sql_op} :v")
            ).params(v=f.value)

    return query


def _apply_sort(query, sort: Optional[str]):
    """
    sort: "field:asc" | "field:desc"

    - If None/invalid -> default ORDER BY id ASC
    - If field == "id" -> sort on Record.id
    - Otherwise -> sort on payload->>'field' as text
    """
    if not sort:
        return query.order_by(Record.id.asc())

    try:
        field, direction = sort.split(":", 1)
    except ValueError:
        return query.order_by(Record.id.asc())

    direction = direction.lower()
    asc = direction == "asc"

    if field == "id":
        return query.order_by(Record.id.asc() if asc else Record.id.desc())

    col = text(f"(payload->>'{field}')")
    if asc:
        return query.order_by(text(f"{col} ASC"))
    else:
        return query.order_by(text(f"{col} DESC"))


# ---- Public API ---- #

def list_all_records(
    db: Session,
    dataset_id: str,
    search: Optional[str],
    sort: Optional[str],
    filters: Optional[List[FilterClause]] = None,
) -> List[Record]:
    """
    Return ALL records for a dataset matching search + filters,
    sorted according to 'sort'. No pagination.
    """
    base = select(Record).where(Record.dataset_id == dataset_id)

    if search:
        pattern = f"%{search}%"
        base = base.where(cast(Record.payload, Text).ilike(pattern))

    base = _apply_filters(base, filters)
    stmt = _apply_sort(base, sort)

    return db.scalars(stmt).all()

def list_records(
    db: Session,
    dataset_id: str,
    page: int,
    limit: int,
    search: Optional[str],
    sort: Optional[str] = None,
    filters: Optional[List[FilterClause]] = None,
) -> Tuple[List[Record], int]:
    """
    List records for a dataset with:
      - optional full-text search over payload (existing behavior)
      - optional field-based filters (FilterClause)
      - optional sort "field:asc|desc"

    Returns (items, total_after_filters).
    """

    # Base query for this dataset
    base = select(Record).where(Record.dataset_id == dataset_id)

    # Simple full-text search: cast JSON payload to text
    if search:
        pattern = f"%{search}%"
        base = base.where(cast(Record.payload, Text).ilike(pattern))

    # Apply field-level filters to the base query
    base = _apply_filters(base, filters)

    # Count after search + filters
    count_query = select(func.count()).select_from(base.subquery())
    total: int = db.scalar(count_query) or 0

    # Sort + paginate
    query = _apply_sort(base, sort)
    query = (
        query.offset((page - 1) * limit)
        .limit(limit)
    )

    items = db.scalars(query).all()
    return items, total


def get_record_by_id(
    db: Session,
    dataset_id: str,
    record_id: int,
) -> Optional[Record]:
    stmt = select(Record).where(
        Record.dataset_id == dataset_id,
        Record.id == record_id,
    )
    return db.scalars(stmt).first()
