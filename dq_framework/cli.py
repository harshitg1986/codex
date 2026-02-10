from __future__ import annotations

import argparse
import json

from .framework import run_framework


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Automated exploratory data quality and analytics framework"
    )
    parser.add_argument("--input", required=True, help="Path to input CSV/XLS/XLSX dataset")
    parser.add_argument("--output-dir", default="output", help="Directory for report artifacts")
    parser.add_argument("--sheet", default="0", help="Excel sheet name or index (default: 0)")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level for statistical tests")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
    result = run_framework(
        data=args.input,
        output_dir=args.output_dir,
        sheet_name=sheet,
        alpha=args.alpha,
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
