from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .profiling import ProfileResult
from .quality_tests import DimensionResult
from .types import Table


class ReportingEngine:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_json(self, name: str, payload: Dict) -> str:
        p = self.output_dir / name
        p.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return str(p)

    def _save_svg(self, name: str, content: str) -> str:
        p = self.output_dir / name
        p.write_text(content, encoding="utf-8")
        return str(p)

    def _missingness_svg(self, table: Table) -> str:
        cell = 16
        w = 150 + cell * max(table.column_count, 1)
        h = 80 + cell * max(min(table.row_count, 150), 1)
        rects: List[str] = [f"<text x='10' y='20' font-size='14'>Missingness Map (first 150 rows)</text>"]
        for cidx, col in enumerate(table.columns):
            x = 140 + cidx * cell
            rects.append(f"<text x='{x}' y='40' font-size='10' transform='rotate(60 {x},40)'>{col}</text>")
        for ridx, row in enumerate(table.rows[:150]):
            y = 55 + ridx * cell
            for cidx, col in enumerate(table.columns):
                x = 140 + cidx * cell
                missing = row.get(col) is None
                color = "#d62728" if missing else "#2ca02c"
                rects.append(f"<rect x='{x}' y='{y}' width='{cell-1}' height='{cell-1}' fill='{color}' />")
        return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>{''.join(rects)}</svg>"

    def _distribution_svg(self, table: Table, numeric_cols: List[str]) -> str:
        cols = numeric_cols[:4]
        w, h = 900, 240 * max(len(cols), 1)
        parts = ["<text x='10' y='20' font-size='16'>Distribution Histograms</text>"]
        for i, col in enumerate(cols):
            vals = [v for v in table.column_values(col) if isinstance(v, (int, float))]
            if not vals:
                continue
            lo, hi = min(vals), max(vals)
            bins = 12
            step = (hi - lo) / bins if hi != lo else 1
            counts = [0] * bins
            for v in vals:
                idx = min(int((v - lo) / step), bins - 1) if step > 0 else 0
                counts[idx] += 1
            maxc = max(counts) or 1
            y0 = 60 + i * 210
            parts.append(f"<text x='10' y='{y0}' font-size='13'>{col}</text>")
            for b, cnt in enumerate(counts):
                bh = int(120 * cnt / maxc)
                x = 120 + b * 55
                y = y0 + 150 - bh
                parts.append(f"<rect x='{x}' y='{y}' width='45' height='{bh}' fill='#1f77b4' />")
        return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>{''.join(parts)}</svg>"

    def _drift_svg(self, stability_metrics: Dict) -> str | None:
        if not stability_metrics.get("applicable"):
            return None
        psi = stability_metrics.get("psi", {})
        if not psi:
            return None
        w, h = 900, 360
        parts = ["<text x='10' y='20' font-size='16'>Drift PSI Overview</text>"]
        cols = list(psi.keys())[:12]
        maxv = max((psi[c]["psi"] for c in cols), default=0.3)
        for i, c in enumerate(cols):
            val = psi[c]["psi"]
            bh = int(220 * (val / max(maxv, 0.25)))
            x = 80 + i * 65
            y = 280 - bh
            color = "#d62728" if val > 0.25 else "#ff7f0e" if val > 0.1 else "#2ca02c"
            parts.append(f"<rect x='{x}' y='{y}' width='45' height='{bh}' fill='{color}' />")
            parts.append(f"<text x='{x}' y='300' font-size='10' transform='rotate(45 {x},300)'>{c}</text>")
        parts.append("<line x1='60' y1='200' x2='850' y2='200' stroke='orange' stroke-dasharray='4' />")
        parts.append("<line x1='60' y1='120' x2='850' y2='120' stroke='red' stroke-dasharray='4' />")
        return f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>{''.join(parts)}</svg>"

    def generate(self, table: Table, profile: ProfileResult, dimensions: Dict[str, DimensionResult], summary: Dict) -> Dict[str, str]:
        payload = {
            "profile": profile.__dict__,
            "dimensions": {k: {"score": v.score, "metrics": v.metrics} for k, v in dimensions.items()},
            "summary": summary,
        }
        artifacts = {
            "metrics_json": self._save_json("metrics.json", payload),
            "missingness_map": self._save_svg("missingness_map.svg", self._missingness_svg(table)),
            "distribution_plot": self._save_svg("distributions.svg", self._distribution_svg(table, profile.numeric_columns)),
        }
        drift_svg = self._drift_svg(dimensions["stability"].metrics)
        if drift_svg:
            artifacts["drift_visual"] = self._save_svg("drift_psi.svg", drift_svg)

        conclusions = {
            "key_risks_identified": summary["risk_flags"],
            "data_fitness_assessment": "Fit for production analytics" if summary["go_caution_no_go"] == "GO" else "Conditionally fit with remediation" if summary["go_caution_no_go"] == "CAUTION" else "Not fit for reliable analytics",
            "recommended_actions": [
                "Address high-missingness columns.",
                "Resolve cross-field inconsistencies and schema violations.",
                "Monitor detected drift and reassess model assumptions.",
            ],
            "signal": summary["go_caution_no_go"],
        }
        artifacts["conclusions_json"] = self._save_json("conclusions.json", conclusions)

        report_lines = [
            "# Automated Exploratory Data Quality & Analytics Report",
            "",
            "## Executive summary",
            f"- Overall data quality score: **{summary['overall_data_quality_score']:.3f}**",
            f"- Decision signal: **{summary['go_caution_no_go']}**",
            f"- Dataset size: **{profile.row_count} rows x {profile.column_count} columns**",
            "",
            "## Per-dimension scores",
        ]
        for d, s in summary["dimension_scores"].items():
            report_lines.append(f"- {d}: **{s:.3f}**")
        report_lines.extend(["", "## Key risks"])
        if summary["risk_flags"]:
            report_lines.extend([f"- {r}" for r in summary["risk_flags"]])
        else:
            report_lines.append("- No critical risks were triggered.")
        report_lines.extend([
            "",
            "## Test methodology",
            "- Outlier tests: robust Z-score and IQR fences.",
            "- Drift tests: KS statistic, PSI, and chi-square indicators.",
            "- Confidence assumptions: 95% threshold approximations (alpha=0.05).",
            "",
            "## Artifacts",
        ])
        for k, v in artifacts.items():
            report_lines.append(f"- {k}: `{v}`")
        report_lines.append("")
        artifacts["human_report"] = str(self.output_dir / "report.md")
        (self.output_dir / "report.md").write_text("\n".join(report_lines), encoding="utf-8")
        return artifacts
