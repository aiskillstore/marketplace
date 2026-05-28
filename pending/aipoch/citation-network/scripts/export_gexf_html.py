#!/usr/bin/env python3
"""
Export a GEXF graph to a self-contained HTML visualization using vis-network CDN.

Usage:
  python scripts/export_gexf_html.py
  python scripts/export_gexf_html.py --run-dir outputs/runs/20260206_140203
  python scripts/export_gexf_html.py --input outputs/citation_network.gexf --output outputs/citation_network.html
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RUNS_DIR = Path("outputs/runs")


def load_latest_run_dir() -> Path:
    if not RUNS_DIR.exists():
        raise SystemExit(
            "[ERROR] outputs/runs not found. Run scripts/init_run.py first."
        )
    candidates = [path for path in RUNS_DIR.iterdir() if path.is_dir()]
    if not candidates:
        raise SystemExit("[ERROR] No run directories found under outputs/runs.")
    return max(candidates, key=lambda path: path.stat().st_mtime).resolve()


def ensure_within_run(path: Path, run_dir: Path) -> Path:
    run_dir_resolved = run_dir.resolve()
    path_resolved = path.resolve()
    try:
        path_resolved.relative_to(run_dir_resolved)
    except ValueError:
        raise SystemExit(f"[ERROR] Path is outside run directory: {path_resolved}")
    return path_resolved


def resolve_path(value: str, run_dir: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = run_dir / path
    return ensure_within_run(path, run_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export GEXF to HTML for browser viewing."
    )
    parser.add_argument(
        "--run-dir", help="Run directory under outputs/runs/<timestamp>/"
    )
    parser.add_argument(
        "--input",
        default="outputs/citation_network.gexf",
        help="GEXF input path (relative to run dir).",
    )
    parser.add_argument(
        "--output",
        default="outputs/citation_network.html",
        help="HTML output path (relative to run dir).",
    )
    return parser.parse_args()


def export_html(
    run_dir: Path,
    input_rel: str = "outputs/citation_network.gexf",
    output_rel: str = "outputs/citation_network.html",
) -> Path:
    try:
        import networkx as nx
    except Exception as exc:  # pragma: no cover
        raise SystemExit("[ERROR] Missing dependency: networkx.") from exc

    input_path = resolve_path(input_rel, run_dir)
    output_path = resolve_path(output_rel, run_dir)

    if not input_path.exists():
        raise SystemExit(f"[ERROR] Input GEXF not found: {input_path}")

    graph = nx.read_gexf(input_path)
    payload = build_payload(graph)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(payload), encoding="utf-8")
    print(f"[OK] HTML exported: {output_path}")
    return output_path


def build_payload(graph) -> dict:
    nodes = []
    for node_id, data in graph.nodes(data=True):
        label = data.get("label", node_id)
        nodes.append({"id": str(node_id), "label": str(label)})
    edges = [{"from": str(u), "to": str(v)} for u, v in graph.edges()]
    return {"nodes": nodes, "edges": edges}


def render_html(payload: dict) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Citation Network</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f4f6f8;
    }}
    #network {{
      width: 100vw;
      height: 100vh;
    }}
  </style>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
</head>
<body>
  <div id="network"></div>
  <script>
    const payload = {payload_json};
    const container = document.getElementById("network");
    const data = {{
      nodes: new vis.DataSet(payload.nodes),
      edges: new vis.DataSet(payload.edges),
    }};
    const options = {{
      edges: {{
        arrows: {{ to: true }},
        color: {{ color: "#9aa4b2" }},
      }},
      nodes: {{
        shape: "dot",
        size: 12,
        font: {{ size: 14 }},
        color: {{ background: "#2563eb", border: "#1d4ed8" }},
      }},
      physics: {{
        solver: "forceAtlas2Based",
        stabilization: true,
      }},
      interaction: {{
        hover: true,
        multiselect: true,
      }},
    }};
    new vis.Network(container, data, options);
  </script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve() if args.run_dir else load_latest_run_dir()
    export_html(run_dir=run_dir, input_rel=args.input, output_rel=args.output)


if __name__ == "__main__":
    main()
