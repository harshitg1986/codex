from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .types import Table

DataLike = Union[Table, List[Dict[str, Any]], str, Path, Any]


class DatasetLoader:
    """Load tabular datasets from CSV, Excel (optional), or DataFrame-like objects."""

    @staticmethod
    def _coerce_scalar(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            v = value.strip()
            if v == "" or v.lower() in {"na", "null", "none", "nan"}:
                return None
            try:
                if "." in v:
                    return float(v)
                return int(v)
            except ValueError:
                return v
        return value

    def _from_records(self, records: List[Dict[str, Any]]) -> Table:
        if not records:
            return Table(columns=[], rows=[])
        columns = list(records[0].keys())
        rows = [{k: self._coerce_scalar(v) for k, v in row.items()} for row in records]
        return Table(columns=columns, rows=rows)

    def load(self, data: DataLike, sheet_name: Optional[Union[str, int]] = 0) -> Table:
        if isinstance(data, Table):
            return data
        if isinstance(data, list):
            return self._from_records(data)
        if hasattr(data, "to_dict") and hasattr(data, "columns"):
            records = data.to_dict(orient="records")
            return self._from_records(records)

        path = Path(data)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        if path.suffix.lower() in {".csv", ".txt"}:
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                records = [dict(r) for r in reader]
            return self._from_records(records)

        if path.suffix.lower() in {".xlsx", ".xls"}:
            try:
                import openpyxl  # type: ignore
            except Exception as exc:
                raise ValueError("Excel support requires openpyxl installed.") from exc

            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb[sheet_name] if isinstance(sheet_name, str) else wb.worksheets[int(sheet_name)]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                return Table(columns=[], rows=[])
            columns = [str(c) for c in rows[0]]
            records = [dict(zip(columns, row)) for row in rows[1:]]
            return self._from_records(records)

        raise ValueError("Unsupported file type. Use CSV/TXT/XLS/XLSX or DataFrame-like input.")
