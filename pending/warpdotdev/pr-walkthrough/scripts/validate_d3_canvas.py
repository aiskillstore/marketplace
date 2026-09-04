#!/usr/bin/env python3
"""Validate a generated pr-walkthrough multi-graph tour HTML canvas."""

from __future__ import annotations

import argparse
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

REQUIRED_GRAPHS = {"system-overview", "data-flow", "code-dependency", "user-action"}
DIRECTED_EDGE_GRAPHS = {"data-flow", "code-dependency", "user-action"}
REQUIRED_CONTROLS = (
    "Fit to view",
    "Reset zoom",
    "System overview",
    "Data flow graph",
    "Code dependency graph",
    "User action graph",
    "Previous tour step",
    "Next tour step",
    "Restart tour",
)


class DataScriptExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script" and dict(attrs).get("id") == "pr-walkthrough-data":
            self.capture = True
            self.parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.capture:
            self.capture = False

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.parts.append(data)


def extract_graph_data(html_text: str) -> dict:
    parser = DataScriptExtractor()
    parser.feed(html_text)
    if parser.parts:
        raw = "".join(parser.parts)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return json.loads(html.unescape(raw))
    match = re.search(r"window\.PR_WALKTHROUGH_D3_DATA\s*=\s*(\{.*?\});", html_text, re.S)
    if not match:
        raise ValueError("Missing inline D3 graph data")
    return json.loads(match.group(1))


def static_validate(html_text: str, data: dict) -> list[str]:
    errors: list[str] = []
    lower = html_text.lower()
    if "d3@7.9.0/dist/d3.min.js" not in html_text:
        errors.append("HTML does not reference the pinned D3 7.9.0 CDN URL")
    if "d3@latest" in lower or "/d3/latest" in lower:
        errors.append("HTML uses an unpinned D3 `latest` runtime")
    if "fetch(" in html_text:
        errors.append("HTML uses fetch(); inline graph data is required for file:// usage")
    if 'id="pr-walkthrough-canvas"' not in html_text:
        errors.append("Missing #pr-walkthrough-canvas SVG")
    if "marker-end" not in html_text or "d3-arrowhead" not in html_text:
        errors.append("HTML does not include visible directed edge arrowhead rendering")
    for label in REQUIRED_CONTROLS:
        if label not in html_text:
            errors.append(f"Missing required control label: {label}")

    graphs = data.get("graphs", [])
    graph_ids = {graph.get("id") for graph in graphs}
    missing = REQUIRED_GRAPHS - graph_ids
    if missing:
        errors.append(f"Missing required graphs: {', '.join(sorted(missing))}")
    extra = graph_ids - REQUIRED_GRAPHS
    if extra:
        errors.append(f"Graph data includes unexpected graph ids: {', '.join(sorted(str(item) for item in extra))}")
    if graph_ids != REQUIRED_GRAPHS:
        errors.append("Graph data must include exactly system-overview, data-flow, code-dependency, and user-action")

    for graph in graphs:
        graph_id = graph.get("id")
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        tour = graph.get("tour", [])
        if not graph.get("label"):
            errors.append(f"Graph {graph_id} missing label")
        if not nodes:
            errors.append(f"Graph {graph_id} has no nodes")
        if graph_id in DIRECTED_EDGE_GRAPHS and not edges:
            errors.append(f"Graph {graph_id} has no edges")
        if not tour:
            errors.append(f"Graph {graph_id} has no guided tour")
        node_ids = {node.get("id") for node in nodes}
        for node in nodes:
            if not node.get("id"):
                errors.append(f"Graph {graph_id} has node missing id")
            if not node.get("title"):
                errors.append(f"Graph {graph_id} node {node.get('id')} missing title")
            if not node.get("summary") and not node.get("details"):
                errors.append(f"Graph {graph_id} node {node.get('id')} missing explanatory text")
        for edge in edges:
            if not edge.get("label"):
                errors.append(f"Graph {graph_id} edge {edge.get('id') or edge.get('source')} missing directional label")
            if edge.get("source") not in node_ids:
                errors.append(f"Graph {graph_id} edge references unknown source: {edge.get('source')}")
            if edge.get("target") not in node_ids:
                errors.append(f"Graph {graph_id} edge references unknown target: {edge.get('target')}")
        for index, step in enumerate(tour):
            if step.get("nodeId") not in node_ids:
                errors.append(f"Graph {graph_id} tour step {index + 1} references unknown node: {step.get('nodeId')}")
            if not step.get("title") or not step.get("body"):
                errors.append(f"Graph {graph_id} tour step {index + 1} missing title/body")
    return errors


def browser_validate(html_path: Path, timeout_ms: int) -> tuple[bool, str]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return False, f"Playwright is unavailable: {exc}"

    url = html_path.resolve().as_uri()
    with sync_playwright() as playwright:
        browser = None
        launch_errors: list[str] = []
        for label, kwargs in (("bundled Chromium", {}), ("system Chrome", {"channel": "chrome"}), ("system Chromium", {"channel": "chromium"})):
            try:
                browser = playwright.chromium.launch(**kwargs)
                break
            except Exception as exc:
                launch_errors.append(f"{label}: {exc}")
        if browser is None:
            return False, "Unable to launch a Playwright browser. " + " | ".join(launch_errors)
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 960})
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_function("""
                () => document.body.classList.contains('d3-canvas-ready') ||
                      document.body.classList.contains('d3-canvas-error')
            """, timeout=timeout_ms)
            initial = page.evaluate("""
                () => ({
                  ready: document.body.classList.contains('d3-canvas-ready'),
                  error: document.body.classList.contains('d3-canvas-error'),
                  nodes: document.querySelectorAll('.d3-node').length,
                  edges: document.querySelectorAll('.d3-edge').length,
                  arrows: document.querySelectorAll('.d3-edge path[marker-end]').length,
                  detailHasContent: Boolean(document.querySelector('#pr-walkthrough-details')?.textContent?.trim()),
                  tourText: document.querySelector('.d3-tour-step-label')?.textContent || '',
                  controls: Array.from(document.querySelectorAll('button')).map((button) => button.textContent.trim()),
                })
            """)
            graph_results = []
            for graph_id in ["system-overview", "data-flow", "code-dependency", "user-action"]:
                page.click(f'[data-graph-id="{graph_id}"]')
                page.wait_for_timeout(150)
                before = page.text_content('.d3-tour-step-label') or ''
                page.click('[data-d3-action="tour-next"]')
                page.wait_for_timeout(120)
                after = page.text_content('.d3-tour-step-label') or ''
                graph_results.append(page.evaluate("""
                    (args) => ({
                      graphId: args.graphId,
                      before: args.before,
                      after: args.after,
                      nodes: document.querySelectorAll('.d3-node').length,
                      edges: document.querySelectorAll('.d3-edge').length,
                      arrows: document.querySelectorAll('.d3-edge path[marker-end]').length,
                      selected: document.querySelectorAll('.d3-node.is-tour-node').length,
                      pressed: document.querySelector(`[data-graph-id="${args.graphId}"]`)?.getAttribute('aria-pressed'),
                    })
                """, {"graphId": graph_id, "before": before, "after": after}) )
        except Exception as exc:
            return False, f"browser validation failed while loading or inspecting the page: {exc}"
        finally:
            browser.close()

    if initial["error"] or not initial["ready"]:
        return False, "D3 canvas reported an error state"
    if initial["nodes"] == 0:
        return False, "Initial graph did not render nodes"
    if not initial["detailHasContent"]:
        return False, "Detail panel did not render content"
    missing_controls = [label for label in REQUIRED_CONTROLS if label not in initial["controls"]]
    if missing_controls:
        return False, f"Missing browser-visible controls: {', '.join(missing_controls)}"
    for result in graph_results:
        if result["nodes"] == 0:
            return False, f"Graph {result['graphId']} did not render nodes"
        if result["graphId"] in DIRECTED_EDGE_GRAPHS and result["edges"] == 0:
            return False, f"Graph {result['graphId']} did not render directed edges"
        if result["graphId"] in DIRECTED_EDGE_GRAPHS and result["arrows"] != result["edges"]:
            return False, f"Graph {result['graphId']} did not render an arrowhead for every edge"
        if result["selected"] == 0:
            return False, f"Graph {result['graphId']} did not mark a tour node"
        if result["pressed"] != "true":
            return False, f"Graph {result['graphId']} toggle did not become active"
    return True, "browser rendered all 4 graphs, directed arrows, and tour controls successfully"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a pr-walkthrough generated HTML file.")
    parser.add_argument("--html", required=True, type=Path, help="Path to .warp/pr-walkthrough/index.html")
    parser.add_argument("--require-browser", action="store_true", help="Fail if browser validation cannot be performed.")
    parser.add_argument("--timeout-ms", type=int, default=15000, help="Browser validation timeout.")
    args = parser.parse_args()

    html_text = args.html.read_text()
    data = extract_graph_data(html_text)
    errors = static_validate(html_text, data)
    if errors:
        for error in errors:
            print(f"FAIL - {error}")
        return 1
    graph_count = len(data.get("graphs", []))
    node_count = sum(len(graph.get("nodes", [])) for graph in data.get("graphs", []))
    edge_count = sum(len(graph.get("edges", [])) for graph in data.get("graphs", []))
    print(f"Static validation passed: {graph_count} graph(s), {node_count} node(s), {edge_count} edge(s).")
    ok, message = browser_validate(args.html, args.timeout_ms)
    if ok:
        print(f"PASS - {message}")
        return 0
    prefix = "FAIL" if args.require_browser else "WARN"
    print(f"{prefix} - {message}")
    return 1 if args.require_browser else 0


if __name__ == "__main__":
    raise SystemExit(main())
