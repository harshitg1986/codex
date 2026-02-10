from __future__ import annotations

from typing import Dict

from .quality_tests import DimensionResult


class ScoringEngine:
    """Aggregate per-dimension quality scores into final judgment."""

    DEFAULT_WEIGHTS = {
        "accuracy": 0.16,
        "completeness": 0.14,
        "consistency": 0.13,
        "validity": 0.12,
        "plausibility": 0.10,
        "stability": 0.10,
        "uniqueness": 0.10,
        "timeliness": 0.08,
        "traceability_auditability": 0.07,
    }

    def __init__(self, weights: Dict[str, float] | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def compute(self, dimensions: Dict[str, DimensionResult]) -> Dict[str, object]:
        weighted_score = 0.0
        for name, result in dimensions.items():
            weighted_score += result.score * self.weights.get(name, 0.0)

        if weighted_score >= 0.85:
            signal = "GO"
        elif weighted_score >= 0.65:
            signal = "CAUTION"
        else:
            signal = "NO-GO"

        risks = []
        for dim, result in dimensions.items():
            if result.score < 0.7:
                risks.append(f"{dim} score is below threshold (0.70): {result.score:.3f}")

        return {
            "overall_data_quality_score": float(round(weighted_score, 4)),
            "go_caution_no_go": signal,
            "dimension_scores": {k: float(round(v.score, 4)) for k, v in dimensions.items()},
            "risk_flags": risks,
        }
