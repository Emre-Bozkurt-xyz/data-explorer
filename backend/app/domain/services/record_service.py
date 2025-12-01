# app/domain/services/record_service.py

from typing import Optional, Dict, Any, List
from io import StringIO
import csv

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.domain.repositories.record_repo import (
    list_records as repo_list_records,
    get_record_by_id as repo_get_record_by_id,
    FilterClause,
    list_all_records as repo_list_all_records,
)


def parse_filter_string(filter_str: Optional[str]) -> List[FilterClause]:
    """
    Parse filter query string into a list of FilterClause.

    Example input:
      "length:gt:1000,symbol:like:TP"
    """
    if not filter_str:
        return []

    clauses: List[FilterClause] = []

    for raw in filter_str.split(","):
        if not raw:
            continue

        parts = raw.split(":", 2)
        if len(parts) != 3:
            continue

        name, op, value = parts

        if op in ("gt", "ge", "lt", "le", "eq", "ne"):
            try:
                parsed_val: Any = float(value)
            except ValueError:
                parsed_val = value
        else:
            parsed_val = value

        clauses.append(FilterClause(name=name, op=op, value=parsed_val))

    return clauses



def list_records(
    db: Session,
    dataset_id: str,
    page: int,
    limit: int,
    search: Optional[str],
    sort: Optional[str],
    filter_str: Optional[str],
) -> Dict[str, Any]:
    filters = parse_filter_string(filter_str)

    items, total = repo_list_records(
        db=db,
        dataset_id=dataset_id,
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
    )

    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total,
    }



def get_record_detail(
    db: Session,
    dataset_id: str,
    record_id: int,
) -> Any:
    record = repo_get_record_by_id(db, dataset_id=dataset_id, record_id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record {record_id} not found in dataset {dataset_id}",
        )
    return record


def export_records_csv(
    db: Session,
    dataset_id: str,
    page: int,
    limit: int,
    search: Optional[str],
    sort: Optional[str],
    filter_str: Optional[str],
) -> StringIO:
    """
    Build a CSV for ALL matching records (ignores page/limit),
    using the same search/sort/filter as the grid.
    """
    filters = parse_filter_string(filter_str)

    items = repo_list_all_records(
        db=db,
        dataset_id=dataset_id,
        search=search,
        sort=sort,
        filters=filters,
    )

    buf = StringIO()
    writer = csv.writer(buf)

    if not items:
        return buf

    first_payload = items[0].payload or {}
    payload_keys = list(first_payload.keys())

    header = ["id"] + payload_keys
    writer.writerow(header)

    for rec in items:
        payload = rec.payload or {}
        row = [rec.id] + [payload.get(k, "") for k in payload_keys]
        writer.writerow(row)

    return buf

