from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Table:
    columns: List[str]
    rows: List[Dict[str, Any]]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return len(self.columns)

    def column_values(self, column: str) -> List[Any]:
        return [row.get(column) for row in self.rows]
