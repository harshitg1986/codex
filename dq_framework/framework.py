from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Optional

from .loader import DataLike, DatasetLoader
from .profiling import DataProfiler
from .quality_tests import QualityTestEngine
from .reporting import ReportingEngine
from .scoring import ScoringEngine


class DataQualityFramework:
    def __init__(self, output_dir: str = "output", alpha: float = 0.05):
        self.loader = DatasetLoader()
        self.profiler = DataProfiler()
        self.tester = QualityTestEngine(alpha=alpha)
        self.scorer = ScoringEngine()
        self.reporter = ReportingEngine(output_dir)

    def run(self, data: DataLike, sheet_name: Optional[int | str] = 0) -> Dict[str, object]:
        table = self.loader.load(data, sheet_name=sheet_name)
        if table.row_count == 0 or table.column_count == 0:
            raise ValueError("Input dataset is empty.")

        profile = self.profiler.profile(table)
        dimensions = self.tester.evaluate(table, profile)
        summary = self.scorer.compute(dimensions)
        artifacts = self.reporter.generate(table, profile, dimensions, summary)

        return {
            "profile": asdict(profile),
            "summary": summary,
            "artifacts": artifacts,
        }


def run_framework(data: DataLike, output_dir: str = "output", sheet_name: Optional[int | str] = 0, alpha: float = 0.05) -> Dict[str, object]:
    return DataQualityFramework(output_dir=output_dir, alpha=alpha).run(data=data, sheet_name=sheet_name)
