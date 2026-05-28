"""Merge multiple CSV/Excel files and output deduplication results and conflict reports.
Configure inputs, primary keys, column aliases, and output paths in the CONFIG area."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


CONFIG = {
    "input_files": [
        "C:/Users/xuw/Desktop/test.xlsx",
        "C:/Users/xuw/Desktop/test2.xlsx",
    ],
    "primary_key": ["_source"],
    "column_aliases": {},
    "dedup_strategy": "keep_all",  # keep_first | keep_last | keep_longest | keep_all
    "add_source_column": True,
    "source_column": "_source",
    "csv_encoding": "utf-8",
    "output_file": "C:/Users/xuw/Desktop/merged.xlsx",
    "conflicts_file": "",
}


def normalize_column_name(name: object) -> str:
    normalized = str(name).strip().lower()
    normalized = normalized.replace(" ", "_").replace("-", "_")
    return normalized


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    return df


def is_na_value(value: object) -> bool:
    result = pd.isna(value)
    if isinstance(result, (pd.Series, pd.Index, pd.DataFrame)):
        return bool(result.to_numpy().all())
    if isinstance(result, np.ndarray):
        return bool(result.all())
    if isinstance(result, np.generic):
        return bool(result)
    return bool(result)


def build_alias_map(aliases: dict[str, list[str]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for target, alias_list in aliases.items():
        normalized_target = normalize_column_name(target)
        for alias in alias_list:
            mapping[normalize_column_name(alias)] = normalized_target
    return mapping


def apply_column_aliases(df: pd.DataFrame, aliases: dict[str, list[str]]) -> pd.DataFrame:
    if not aliases:
        return df
    alias_map = build_alias_map(aliases)
    rename_map = {
        col: alias_map[col]
        for col in df.columns
        if col in alias_map and alias_map[col] != col
    }
    return df.rename(columns=rename_map)


def merge_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    unique_cols = list(dict.fromkeys(df.columns))
    if len(unique_cols) == len(df.columns):
        return df
    merged_data: dict[str, pd.Series] = {}
    for col in unique_cols:
        dup_cols = df.loc[:, df.columns == col]
        if dup_cols.shape[1] == 1:
            merged_data[col] = dup_cols.iloc[:, 0]
        else:
            merged_data[col] = dup_cols.bfill(axis=1).iloc[:, 0]
    return pd.DataFrame(merged_data)


def read_file(path: str, encoding: str) -> pd.DataFrame:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix in {".csv"}:
        return pd.read_csv(file_path, encoding=encoding)
    if suffix in {".tsv"}:
        return pd.read_csv(file_path, encoding=encoding, sep="\t")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)
    raise ValueError(f"Unsupported file types: {file_path}")


def detect_conflicts(df: pd.DataFrame, key_cols: list[str]) -> pd.DataFrame:
    non_key_cols = [col for col in df.columns if col not in key_cols]
    conflicts: list[dict[str, str]] = []
    grouped = df.groupby(key_cols, dropna=False)
    for key, group in grouped:
        conflict_cols = []
        for col in non_key_cols:
            values = group[col].dropna().astype(str).str.strip()
            values = values[values != ""].unique()
            if len(values) > 1:
                conflict_cols.append(col)
        if conflict_cols:
            record: dict[str, str] = {}
            if isinstance(key, tuple):
                for col, value in zip(key_cols, key):
                    record[col] = "" if is_na_value(value) else str(value)
            else:
                record[key_cols[0]] = "" if is_na_value(key) else str(key)
            record["conflict_columns"] = ";".join(conflict_cols)
            conflicts.append(record)
    return pd.DataFrame(conflicts)


def deduplicate(df: pd.DataFrame, key_cols: list[str], strategy: str) -> pd.DataFrame:
    if strategy == "keep_all":
        return df
    if strategy == "keep_first":
        return df.drop_duplicates(subset=key_cols, keep="first")
    if strategy == "keep_last":
        return df.drop_duplicates(subset=key_cols, keep="last")
    if strategy == "keep_longest":
        grouped = df.groupby(key_cols, dropna=False, sort=False)

        def choose_longest(group: pd.DataFrame) -> pd.DataFrame:
            lengths = group.apply(
                lambda row: sum(
                    len(str(value).strip()) for value in row if pd.notna(value)
                ),
                axis=1,
            )
            return group.loc[[lengths.idxmax()]]

        return grouped.apply(choose_longest).reset_index(drop=True)
    raise ValueError(f"Unknown deduplication strategy: {strategy}")


def write_output(df: pd.DataFrame, output_path: str, encoding: str) -> None:
    output_file = Path(output_path)
    suffix = output_file.suffix.lower()
    if suffix == ".csv":
        df.to_csv(output_file, index=False, encoding=encoding)
        return
    if suffix in {".xlsx", ".xls"}:
        df.to_excel(output_file, index=False)
        return
    if suffix == ".json":
        records = df.to_dict(orient="records")
        with open(output_file, "w", encoding="utf-8") as handle:
            json.dump(records, handle, ensure_ascii=False, indent=2)
        return
    if suffix == ".parquet":
        df.to_parquet(output_file, index=False)
        return
    raise ValueError(f"Unsupported output format: {output_file}")


def main() -> None:
    input_files = CONFIG["input_files"]
    if not input_files:
        print("Please fill in input_files in CONFIG.")
        return

    dfs: list[pd.DataFrame] = []
    for file_path in input_files:
        df = read_file(file_path, CONFIG["csv_encoding"])
        df = normalize_columns(df)
        df = apply_column_aliases(df, CONFIG["column_aliases"])
        if CONFIG["add_source_column"]:
            df[CONFIG["source_column"]] = Path(file_path).name
        dfs.append(df)

    merged = pd.concat(dfs, ignore_index=True, sort=False)
    merged = merge_duplicate_columns(merged)

    conflict_df = detect_conflicts(merged, CONFIG["primary_key"])
    if not conflict_df.empty and CONFIG["conflicts_file"]:
        conflict_df.to_csv(CONFIG["conflicts_file"], index=False, encoding="utf-8")

    merged = deduplicate(merged, CONFIG["primary_key"], CONFIG["dedup_strategy"])
    write_output(merged, CONFIG["output_file"], CONFIG["csv_encoding"])

    print(f"Merge completed: {CONFIG['output_file']}")
    print(f"Total number of rows: {len(merged)}")
    if not conflict_df.empty:
        print(f"Conflict record: {len(conflict_df)} (See {CONFIG['conflicts_file']})")
    else:
        print("Conflict records: 0")


if __name__ == "__main__":
    main()
