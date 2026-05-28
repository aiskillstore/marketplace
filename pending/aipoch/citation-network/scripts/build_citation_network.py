#!/usr/bin/env python3
"""Citation network building script (CSV)

How to use:
- Run first: python scripts/init_run.py (generate running directory and configuration)
- Modify config.json in the running directory
- Run: python scripts/build_citation_network.py

Description:
- Depends on pandas, networkx
- Output GEXF and network metrics JSON"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

RUNS_DIR = Path("outputs/runs")

CONFIG: dict = {}


def require_packages():
    try:
        import pandas as pd  # noqa: F401
        import networkx as nx  # noqa: F401
    except Exception as exc:  # pragma: no cover
        print("[ERROR] Missing dependency package: pandas/networkx.")
        raise SystemExit(1) from exc


def load_run_dir():
    if not RUNS_DIR.exists():
        print("[ERROR] The running directory was not found, please run scripts/init_run.py first.")
        raise SystemExit(1)
    candidates = [path for path in RUNS_DIR.iterdir() if path.is_dir()]
    if not candidates:
        print("[ERROR] No available run directory found, please run scripts/init_run.py first.")
        raise SystemExit(1)
    run_dir = max(candidates, key=lambda path: path.stat().st_mtime).resolve()
    return run_dir


def ensure_within_run(path: Path, run_dir: Path) -> Path:
    run_dir_resolved = run_dir.resolve()
    path_resolved = path.resolve()
    try:
        path_resolved.relative_to(run_dir_resolved)
    except ValueError:
        print(f"[ERROR] The path exceeds the scope of the running directory: {path_resolved}")
        raise SystemExit(1)
    return path_resolved


def resolve_path(value: str, run_dir: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = run_dir / path
    return ensure_within_run(path, run_dir)


def load_config(run_dir: Path):
    config_path = run_dir / "config.json"
    if not config_path.exists():
        print(f"[ERROR] Configuration file not found: {config_path}")
        raise SystemExit(1)
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    config["input_csv"] = resolve_path(config["input_csv"], run_dir)
    config["output_gexf"] = resolve_path(config["output_gexf"], run_dir)
    config["output_json"] = resolve_path(config["output_json"], run_dir)
    return config


def load_edges():
    import pandas as pd

    path = CONFIG["input_csv"]
    if not path.exists():
        print(f"[ERROR] Input CSV not found: {path}")
        raise SystemExit(1)
    encodings = get_input_encodings()
    last_error = None
    for encoding in encodings:
        try:
            df = pd.read_csv(path, encoding=encoding)
            if (
                CONFIG["source_col"] not in df.columns
                or CONFIG["target_col"] not in df.columns
            ):
                print("[ERROR] Missing source/target columns in input CSV.")
                raise SystemExit(1)
            return df[[CONFIG["source_col"], CONFIG["target_col"]]]
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
    tried = ", ".join(encodings)
    print(f"[ERROR] Unable to decode CSV using encodings: {tried}")
    if last_error:
        print(f"[ERROR] Last decode error: {last_error}")
    raise SystemExit(1)


def get_input_encodings():
    value = CONFIG.get("input_encoding")
    if not value:
        return ["utf-8", "utf-8-sig", "gb18030"]
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    print("[ERROR] input_encoding must be a string or list of strings.")
    raise SystemExit(1)


def build_graph(edges_df):
    import networkx as nx

    graph = nx.DiGraph()
    graph.add_edges_from(edges_df.itertuples(index=False, name=None))
    return graph


def compute_metrics(graph):
    import networkx as nx

    metrics = {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "density": nx.density(graph),
        "top_degree": sorted(graph.degree, key=lambda x: x[1], reverse=True)[:10],
    }
    return metrics


def write_outputs(graph, metrics):
    output_gexf = CONFIG["output_gexf"]
    output_json = CONFIG["output_json"]
    output_gexf.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    import networkx as nx

    nx.write_gexf(graph, output_gexf)
    with output_json.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, ensure_ascii=False, indent=2)


def run_export_html(run_dir: Path) -> None:
    export_script = Path("scripts/export_gexf_html.py")
    if not export_script.exists():
        print("[WARN] export_gexf_html.py not found. Skip HTML export.")
        return
    try:
        spec = importlib.util.spec_from_file_location("export_gexf_html", export_script)
        if spec is None or spec.loader is None:
            print("[WARN] Unable to load export_gexf_html module. Skip HTML export.")
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        export_func = getattr(module, "export_html", None)
        if export_func is None:
            print("[WARN] export_html() missing. Skip HTML export.")
            return
        export_func(run_dir=run_dir)
    except Exception as exc:
        print(f"[WARN] HTML export failed: {exc}")


def main():
    require_packages()
    run_dir = load_run_dir()
    global CONFIG
    CONFIG = load_config(run_dir)
    edges_df = load_edges()
    graph = build_graph(edges_df)
    metrics = compute_metrics(graph)
    write_outputs(graph, metrics)
    run_export_html(run_dir)
    print("[OK] Citation network output generated.")


if __name__ == "__main__":
    main()
