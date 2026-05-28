"""Perform statistical analysis on CSV/Excel and output summary results.
Configure inputs and outputs in CONFIG."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


CONFIG = {
    "input_file": "input.xlsx",
    "sheet_name": None,
    "groupby_column": None,
    "agg_column": None,
    "output_file": "analysis_output.xlsx",
    "csv_encoding": "utf-8",
}


def read_input(path: str) -> pd.DataFrame:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(file_path, encoding=CONFIG["csv_encoding"])
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path, sheet_name=CONFIG["sheet_name"])
    raise ValueError(f"Unsupported file types: {file_path}")


def main() -> None:
    df = read_input(CONFIG["input_file"])

    summary = df.describe(include="all").transpose()
    output_path = Path(CONFIG["output_file"])

    if output_path.suffix.lower() in {".xlsx", ".xls"}:
        with pd.ExcelWriter(output_path) as writer:
            summary.to_excel(writer, sheet_name="summary")
            df.head(100).to_excel(writer, sheet_name="sample", index=False)
    elif output_path.suffix.lower() == ".csv":
        summary.to_csv(output_path, encoding="utf-8")
    elif output_path.suffix.lower() == ".json":
        records = summary.reset_index().to_dict(orient="records")
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(records, handle, ensure_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported output format: {output_path}")

    if CONFIG["groupby_column"] and CONFIG["agg_column"]:
        grouped = df.groupby(CONFIG["groupby_column"])[CONFIG["agg_column"]].sum()
        print(grouped.sort_values(ascending=False).head(10))

    print(f"Analysis completed: {output_path}")


if __name__ == "__main__":
    main()
