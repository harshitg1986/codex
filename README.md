# Automated Exploratory Data Quality & Analytics Framework

This project provides an end-to-end data quality and exploratory analytics framework that runs from a **single command**.

## What it does

Given a tabular dataset (CSV, optional Excel, or DataFrame-like input), it automatically:

- Profiles schema, inferred types, candidate keys, and temporal fields.
- Evaluates mandatory quality dimensions:
  - Accuracy
  - Completeness
  - Consistency
  - Validity / Conformance
  - Plausibility
  - Stability
  - Uniqueness
  - Timeliness
  - Traceability & Auditability
- Applies quantitative diagnostics and statistical tests (where applicable):
  - Z-score (robust MAD variant)
  - IQR
  - KS statistic
  - PSI
  - Chi-square indicator
- Produces:
  - Per-column metrics
  - Per-dimension scores
  - Overall quality score
  - GO / CAUTION / NO-GO signal
  - Human-readable executive report
  - Visual summaries (SVG): missingness, distributions, drift

## Architecture

- `dq_framework/loader.py` — input ingestion layer.
- `dq_framework/profiling.py` — schema + metadata inference layer.
- `dq_framework/quality_tests.py` — modular quality test layer.
- `dq_framework/scoring.py` — scoring and risk aggregation layer.
- `dq_framework/reporting.py` — reporting & visualization layer.
- `dq_framework/framework.py` — orchestration and public API.
- `dq_framework/cli.py` — one-command execution.

## Quick start

```bash
python -m dq_framework --input sample_data/retail_orders_sample.csv --output-dir output/example_run
```

The command prints summary JSON and writes artifacts to the output folder:

- `metrics.json`
- `conclusions.json`
- `report.md`
- `missingness_map.svg`
- `distributions.svg`
- `drift_psi.svg` (when temporal drift is applicable)

> Note: generated outputs are intentionally ignored by git (`output/`) so each run is reproducible locally without polluting version history.

## Python API

```python
from dq_framework import run_framework

result = run_framework("sample_data/retail_orders_sample.csv", output_dir="output/my_run")
print(result["summary"])
```

## Example execution

Sample dataset included at:

- `sample_data/retail_orders_sample.csv`

Run:

```bash
python -m dq_framework --input sample_data/retail_orders_sample.csv --output-dir output/example_run
```

## Extensibility

To add a new data quality rule or test:

1. Implement logic in `QualityTestEngine` (`dq_framework/quality_tests.py`).
2. Return metrics in the relevant dimension payload.
3. Update weights/thresholds in `ScoringEngine` if needed.
4. Optionally surface the metric in `ReportingEngine`.

## Notes

- Core runtime uses only Python standard library for portability.
- Excel support requires optional `openpyxl`.
- Confidence assumptions are explicitly logged in generated artifacts.


## Test

```bash
python -m unittest discover -s tests -v
```
