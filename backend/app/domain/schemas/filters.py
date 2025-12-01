# app/domain/schemas/filters.py

from dataclasses import dataclass
from typing import Literal, Any


Op = Literal["eq", "ne", "lt", "gt", "le", "ge", "like"]


@dataclass
class FilterClause:
    name: str
    op: Op
    value: Any
