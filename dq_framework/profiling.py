from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from .types import Table


@dataclass
class ProfileResult:
    row_count: int
    column_count: int
    dtype_map: Dict[str, str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    candidate_primary_keys: List[str]
    candidate_time_columns: List[str]
    metadata: Dict[str, object]


class DataProfiler:
    def _is_number(self, v: object) -> bool:
        return isinstance(v, (int, float)) and not isinstance(v, bool)

    def _is_datetime(self, v: object) -> bool:
        if isinstance(v, datetime):
            return True
        if not isinstance(v, str):
            return False
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d-%m-%Y"):
            try:
                datetime.strptime(v, fmt)
                return True
            except Exception:
                continue
        return False

    def profile(self, table: Table) -> ProfileResult:
        dtype_map: Dict[str, str] = {}
        numeric, categorical, datetime_cols = [], [], []

        for col in table.columns:
            values = [v for v in table.column_values(col) if v is not None]
            if not values:
                dtype_map[col] = "unknown"
                categorical.append(col)
                continue
            num_ratio = sum(1 for v in values if self._is_number(v)) / len(values)
            dt_ratio = sum(1 for v in values if self._is_datetime(v)) / len(values)
            if num_ratio >= 0.8:
                dtype_map[col] = "numeric"
                numeric.append(col)
            elif dt_ratio >= 0.8:
                dtype_map[col] = "datetime"
                datetime_cols.append(col)
            else:
                dtype_map[col] = "categorical"
                categorical.append(col)

        candidate_primary_keys = []
        for col in table.columns:
            vals = table.column_values(col)
            non_null = [v for v in vals if v is not None]
            if len(non_null) == len(vals) and len(set(map(str, vals))) >= int(0.98 * max(len(vals), 1)):
                candidate_primary_keys.append(col)

        name_based_time = [
            c for c in table.columns if any(t in c.lower() for t in ["date", "time", "timestamp", "dt"])
        ]
        candidate_time_columns = sorted(set(datetime_cols + name_based_time))

        duplicate_rows = len(table.rows) - len({tuple(str(r.get(c)) for c in table.columns) for r in table.rows})
        missing = sum(1 for r in table.rows for c in table.columns if r.get(c) is None)

        return ProfileResult(
            row_count=table.row_count,
            column_count=table.column_count,
            dtype_map=dtype_map,
            numeric_columns=numeric,
            categorical_columns=categorical,
            datetime_columns=datetime_cols,
            candidate_primary_keys=candidate_primary_keys,
            candidate_time_columns=candidate_time_columns,
            metadata={
                "duplicate_rows": duplicate_rows,
                "sparsity": (missing / (max(table.row_count * max(table.column_count, 1), 1))),
            },
        )
