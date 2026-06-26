#!/usr/bin/env python3
"""Render patent-style black-and-white flowchart SVGs from draft JSON."""

import argparse
import html
import json
import re
import textwrap
from pathlib import Path


STEP_PATTERN = re.compile(r"\bS\s*(\d+)\b", re.IGNORECASE)
ASCII_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
VAGUE_FINAL_RESULT = re.compile(r"(技术结果|处理结果|最终结果)")


def normalize_step(value: str) -> str:
    match = STEP_PATTERN.fullmatch(str(value).strip())
    return f"S{match.group(1)}" if match else str(value).strip()


def claim_step_map(claims: list[dict]) -> dict[int, set[str]]:
    result = {}
    for claim in claims:
        number = claim.get("number")
        result[number] = {f"S{value}" for value in STEP_PATTERN.findall(claim.get("text", ""))}
    return result


def validate_figure(
    figure: dict,
    steps_by_claim: dict[int, set[str]],
    descriptions: list[str],
) -> list[str]:
    errors = []
    figure_type = figure.get("type")
    if figure_type not in {"flowchart", "methodology"}:
        errors.append("type must be 'flowchart' or 'methodology'")
    if figure.get("orientation", "vertical") not in {"vertical", "horizontal"}:
        errors.append("orientation must be 'vertical' or 'horizontal'")
    claim_number = figure.get("claim_number", 1)
    available_steps = set()
    if figure_type == "flowchart":
        if claim_number not in steps_by_claim:
            errors.append(f"claim_number {claim_number!r} does not exist")
        available_steps = steps_by_claim.get(claim_number, set())

    nodes = figure.get("nodes", [])
    if not nodes:
        errors.append("at least one node is required")
    ids = [str(node.get("id", "")) for node in nodes]
    if len(ids) != len(set(ids)):
        errors.append("node ids must be unique")
    for node in nodes:
        node_id = str(node.get("id", ""))
        if not ASCII_ID.fullmatch(node_id):
            errors.append(f"invalid node id: {node_id!r}")
        if not str(node.get("label", "")).strip():
            errors.append(f"node {node_id!r} has an empty label")
        step = normalize_step(node.get("claim_step", ""))
        if figure_type == "flowchart" and step and step not in available_steps:
            errors.append(
                f"node {node_id!r} references step {step!r}, not found in claim {claim_number}"
            )

    node_steps = {
        normalize_step(node.get("claim_step", ""))
        for node in nodes
        if str(node.get("claim_step", "")).strip()
    }
    if figure_type == "flowchart" and figure.get("complete_claim_flow") and node_steps != available_steps:
        missing = sorted(available_steps - node_steps)
        extra = sorted(node_steps - available_steps)
        if missing:
            errors.append(f"complete claim flow is missing steps: {missing}")
        if extra:
            errors.append(f"complete claim flow contains extra steps: {extra}")

    figure_token = f"图{figure.get('number')}"
    if not any(figure_token in str(description) for description in descriptions):
        errors.append(f"figure description does not reference {figure_token}")

    id_set = set(ids)
    incoming = {node_id: 0 for node_id in ids}
    outgoing = {node_id: 0 for node_id in ids}
    for edge in figure.get("edges", []):
        source = str(edge.get("from", ""))
        target = str(edge.get("to", ""))
        if source not in id_set:
            errors.append(f"edge source {source!r} does not exist")
        if target not in id_set:
            errors.append(f"edge target {target!r} does not exist")
        if source == target and source:
            errors.append(f"self-loop is not allowed for node {source!r}")
        if source in outgoing:
            outgoing[source] += 1
        if target in incoming:
            incoming[target] += 1

    if len(nodes) > 1 and not figure.get("edges"):
        errors.append("multiple nodes require edges")
    if len(nodes) > 1:
        if not any(value == 0 for value in incoming.values()):
            errors.append("flowchart has no start node")
        if not any(value == 0 for value in outgoing.values()):
            errors.append("flowchart has no end node")
        starts = [node_id for node_id, count in incoming.items() if count == 0]
        adjacency = {node_id: set() for node_id in ids}
        for edge in figure.get("edges", []):
            source = str(edge.get("from", ""))
            target = str(edge.get("to", ""))
            if source in adjacency and target in id_set:
                adjacency[source].add(target)
        reachable = set(starts)
        pending = list(starts)
        while pending:
            current = pending.pop()
            for target in adjacency[current]:
                if target not in reachable:
                    reachable.add(target)
                    pending.append(target)
        disconnected = sorted(id_set - reachable)
        if disconnected:
            errors.append(f"unreachable nodes from any start node: {disconnected}")
    for node in nodes:
        node_id = str(node.get("id", ""))
        if outgoing.get(node_id) == 0 and VAGUE_FINAL_RESULT.search(str(node.get("label", ""))):
            errors.append(
                f"end node {node_id!r} uses a vague result name; state the specific detection, "
                "estimation, classification, positioning, or control result"
            )
    return errors


def wrap_label(label: str, width: int = 18) -> list[str]:
    chunks = []
    for paragraph in str(label).splitlines() or [""]:
        chunks.extend(textwrap.wrap(paragraph, width=width) or [""])
    return chunks


def layout(figure: dict) -> tuple[dict[str, tuple[int, int, int, int]], int, int]:
    orientation = figure.get("orientation", "vertical")
    nodes = figure["nodes"]
    box_width = 360
    gap = 90
    margin = 70
    positions = {}
    max_height = 0
    heights = []
    for node in nodes:
        line_count = len(wrap_label(node["label"]))
        height = max(72, 34 + line_count * 24)
        heights.append(height)
        max_height = max(max_height, height)

    if orientation == "vertical":
        y = margin + 45
        for node, height in zip(nodes, heights):
            positions[node["id"]] = (margin, y, box_width, height)
            y += height + gap
        width = box_width + margin * 2
        height = y - gap + margin
    else:
        x = margin
        for node, height in zip(nodes, heights):
            positions[node["id"]] = (x, margin + 45, box_width, height)
            x += box_width + gap
        width = x - gap + margin
        height = max_height + margin * 2 + 45
    return positions, width, height


def anchor(box: tuple[int, int, int, int], side: str) -> tuple[float, float]:
    x, y, width, height = box
    points = {
        "top": (x + width / 2, y),
        "bottom": (x + width / 2, y + height),
        "left": (x, y + height / 2),
        "right": (x + width, y + height / 2),
    }
    return points[side]


def render(figure: dict) -> str:
    positions, width, height = layout(figure)
    orientation = figure.get("orientation", "vertical")
    title = f"图{figure['number']} {figure.get('title', '方法流程图')}"
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        "<defs>",
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
        'markerHeight="8" orient="auto-start-reverse">',
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#000"/>',
        "</marker>",
        "</defs>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<text x="{width / 2}" y="28" text-anchor="middle" '
        'font-family="SimSun, Songti SC, serif" font-size="20">'
        f"{html.escape(title)}</text>",
    ]

    for edge in figure.get("edges", []):
        source_box = positions[edge["from"]]
        target_box = positions[edge["to"]]
        source_side, target_side = (
            ("bottom", "top") if orientation == "vertical" else ("right", "left")
        )
        x1, y1 = anchor(source_box, source_side)
        x2, y2 = anchor(target_box, target_side)
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            'stroke="#000" stroke-width="2" marker-end="url(#arrow)"/>'
        )
        label = str(edge.get("label", "")).strip()
        if label:
            parts.append(
                f'<text x="{(x1 + x2) / 2 + 8}" y="{(y1 + y2) / 2 - 8}" '
                'font-family="SimSun, Songti SC, serif" font-size="16">'
                f"{html.escape(label)}</text>"
            )

    for node in figure["nodes"]:
        x, y, box_width, box_height = positions[node["id"]]
        parts.append(
            f'<rect x="{x}" y="{y}" width="{box_width}" height="{box_height}" '
            'rx="0" fill="#fff" stroke="#000" stroke-width="2"/>'
        )
        lines = wrap_label(node["label"])
        start_y = y + box_height / 2 - (len(lines) - 1) * 12
        for index, line in enumerate(lines):
            parts.append(
                f'<text x="{x + box_width / 2}" y="{start_y + index * 24}" '
                'text-anchor="middle" dominant-baseline="middle" '
                'font-family="SimSun, Songti SC, serif" font-size="18">'
                f"{html.escape(line)}</text>"
            )

    parts.append("</svg>")
    return "\n".join(parts)


def load_font(size: int):
    from PIL import ImageFont

    candidates = (
        Path(r"C:\Windows\Fonts\simsun.ttc"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def render_png(figure: dict, output: Path) -> None:
    from PIL import Image, ImageDraw

    positions, width, height = layout(figure)
    scale = 2
    image = Image.new("RGB", (width * scale, height * scale), "white")
    draw = ImageDraw.Draw(image)
    title_font = load_font(20 * scale)
    body_font = load_font(18 * scale)
    edge_font = load_font(16 * scale)

    def point(value: float) -> int:
        return int(round(value * scale))

    title = f"图{figure['number']} {figure.get('title', '方法流程图')}"
    title_box = draw.textbbox((0, 0), title, font=title_font)
    title_x = (width * scale - (title_box[2] - title_box[0])) / 2
    draw.text((title_x, point(8)), title, fill="black", font=title_font)

    orientation = figure.get("orientation", "vertical")
    for edge in figure.get("edges", []):
        source_box = positions[edge["from"]]
        target_box = positions[edge["to"]]
        source_side, target_side = (
            ("bottom", "top") if orientation == "vertical" else ("right", "left")
        )
        x1, y1 = anchor(source_box, source_side)
        x2, y2 = anchor(target_box, target_side)
        draw.line((point(x1), point(y1), point(x2), point(y2)), fill="black", width=4)
        if orientation == "vertical":
            arrow = [
                (point(x2), point(y2)),
                (point(x2 - 7), point(y2 - 12)),
                (point(x2 + 7), point(y2 - 12)),
            ]
        else:
            arrow = [
                (point(x2), point(y2)),
                (point(x2 - 12), point(y2 - 7)),
                (point(x2 - 12), point(y2 + 7)),
            ]
        draw.polygon(arrow, fill="black")
        label = str(edge.get("label", "")).strip()
        if label:
            draw.text(
                (point((x1 + x2) / 2 + 8), point((y1 + y2) / 2 - 20)),
                label,
                fill="black",
                font=edge_font,
            )

    for node in figure["nodes"]:
        x, y, box_width, box_height = positions[node["id"]]
        draw.rectangle(
            (point(x), point(y), point(x + box_width), point(y + box_height)),
            fill="white",
            outline="black",
            width=4,
        )
        lines = wrap_label(node["label"])
        line_height = 24 * scale
        total_height = line_height * len(lines)
        text_y = point(y + box_height / 2) - total_height / 2
        for line in lines:
            text_box = draw.textbbox((0, 0), line, font=body_font)
            text_width = text_box[2] - text_box[0]
            text_x = point(x + box_width / 2) - text_width / 2
            draw.text((text_x, text_y), line, fill="black", font=body_font)
            text_y += line_height

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", dpi=(300, 300))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path, help="UTF-8 patent draft JSON")
    parser.add_argument("--output-dir", type=Path, required=True, help="SVG output directory")
    parser.add_argument("--png", action="store_true", help="Also render PNG files")
    args = parser.parse_args()

    data = json.loads(args.draft.read_text(encoding="utf-8"))
    figures = data.get("figures", [])
    if not figures:
        parser.error("draft contains no figures")
    numbers = [figure.get("number") for figure in figures]
    if numbers != list(range(1, len(figures) + 1)):
        parser.error(f"figure numbers must be consecutive starting at 1: {numbers}")

    steps = claim_step_map(data.get("claims", []))
    descriptions = data.get("specification", {}).get("figure_descriptions", [])
    all_errors = []
    for figure in figures:
        errors = validate_figure(figure, steps, descriptions)
        all_errors.extend(f"Figure {figure.get('number')}: {error}" for error in errors)
    if all_errors:
        for error in all_errors:
            print(f"ERROR\t{error}")
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for figure in figures:
        output = args.output_dir / f"figure-{figure['number']}.svg"
        output.write_text(render(figure), encoding="utf-8")
        print(output)
        if args.png:
            try:
                import PIL
            except ImportError as error:
                raise SystemExit(
                    "PNG output requires Pillow: python -m pip install pillow"
                ) from error
            png_output = args.output_dir / f"figure-{figure['number']}.png"
            render_png(figure, png_output)
            print(png_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
