#!/usr/bin/env python3
"""Convert OCR word boxes into image text-layer layout JSON."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable


@dataclass
class Word:
    text: str
    bbox: tuple[float, float, float, float]
    confidence: float | None = None

    @property
    def x0(self) -> float:
        return self.bbox[0]

    @property
    def y0(self) -> float:
        return self.bbox[1]

    @property
    def x1(self) -> float:
        return self.bbox[2]

    @property
    def y1(self) -> float:
        return self.bbox[3]

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def height(self) -> float:
        return max(1.0, self.y1 - self.y0)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def comparable(text: str) -> str:
    return re.sub(r"\W+", "", text, flags=re.UNICODE).lower()


def is_cjk(ch: str) -> bool:
    return "\u3400" <= ch <= "\u9fff" or "\uf900" <= ch <= "\ufaff"


def join_words(words: list[Word]) -> str:
    out = ""
    for word in words:
        text = word.text.strip()
        if not text:
            continue
        if not out:
            out = text
            continue
        prev = out[-1]
        first = text[0]
        if is_cjk(prev) and is_cjk(first):
            out += text
        elif first in ",.;:!?)]}%":
            out += text
        elif prev in "([{":
            out += text
        else:
            out += " " + text
    return normalize_text(out)


def bbox_union(words: Iterable[Word]) -> list[float]:
    items = list(words)
    return [
        min(word.x0 for word in items),
        min(word.y0 for word in items),
        max(word.x1 for word in items),
        max(word.y1 for word in items),
    ]


def bbox_from_any(obj: dict[str, Any]) -> tuple[float, float, float, float] | None:
    if "bbox" in obj and isinstance(obj["bbox"], list) and len(obj["bbox"]) == 4:
        x0, y0, x1, y1 = [float(v) for v in obj["bbox"]]
        return x0, y0, x1, y1
    if {"x", "y", "width", "height"} <= set(obj):
        x = float(obj["x"])
        y = float(obj["y"])
        return x, y, x + float(obj["width"]), y + float(obj["height"])
    vertices = None
    if "boundingPoly" in obj:
        vertices = obj["boundingPoly"].get("vertices") or obj["boundingPoly"].get("normalizedVertices")
    elif "boundingBox" in obj and isinstance(obj["boundingBox"], dict):
        vertices = obj["boundingBox"].get("vertices")
    elif "polygon" in obj:
        vertices = obj["polygon"]
    if vertices:
        xs: list[float] = []
        ys: list[float] = []
        for point in vertices:
            if isinstance(point, dict):
                xs.append(float(point.get("x", 0)))
                ys.append(float(point.get("y", 0)))
            else:
                xs.append(float(point[0]))
                ys.append(float(point[1]))
        return min(xs), min(ys), max(xs), max(ys)
    return None


def text_from_any(obj: dict[str, Any]) -> str:
    for key in ("text", "description", "value", "content"):
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def confidence_from_any(obj: dict[str, Any]) -> float | None:
    for key in ("confidence", "score"):
        value = obj.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def iter_word_objects(data: Any) -> Iterable[dict[str, Any]]:
    if isinstance(data, list):
        for item in data:
            yield from iter_word_objects(item)
        return
    if not isinstance(data, dict):
        return

    if "words" in data and isinstance(data["words"], list):
        for word in data["words"]:
            if isinstance(word, dict):
                yield word
    if "items" in data and isinstance(data["items"], list):
        for item in data["items"]:
            if isinstance(item, dict):
                yield item
    if "textAnnotations" in data and isinstance(data["textAnnotations"], list):
        for item in data["textAnnotations"][1:]:
            if isinstance(item, dict):
                yield item

    for key in ("pages", "blocks", "paragraphs", "lines"):
        value = data.get(key)
        if isinstance(value, list):
            for child in value:
                yield from iter_word_objects(child)


def load_words(path: Path, min_confidence: float | None) -> list[Word]:
    data = json.loads(path.read_text(encoding="utf-8"))
    words: list[Word] = []
    for obj in iter_word_objects(data):
        text = text_from_any(obj)
        bbox = bbox_from_any(obj)
        confidence = confidence_from_any(obj)
        if not text or bbox is None:
            continue
        if min_confidence is not None and confidence is not None and confidence < min_confidence:
            continue
        x0, y0, x1, y1 = bbox
        if x1 <= x0 or y1 <= y0:
            continue
        words.append(Word(text=text, bbox=(x0, y0, x1, y1), confidence=confidence))
    return words


def group_lines(words: list[Word], y_tolerance: float | None) -> list[list[Word]]:
    words = sorted(words, key=lambda word: (word.cy, word.x0))
    lines: list[list[Word]] = []
    for word in words:
        placed = False
        for line in lines:
            median_height = sorted(w.height for w in line)[len(line) // 2]
            tolerance = y_tolerance if y_tolerance is not None else max(6.0, median_height * 0.55)
            line_cy = sum(w.cy for w in line) / len(line)
            if abs(word.cy - line_cy) <= tolerance:
                line.append(word)
                placed = True
                break
        if not placed:
            lines.append([word])
    for line in lines:
        line.sort(key=lambda word: word.x0)
    return sorted(lines, key=lambda line: (min(w.y0 for w in line), min(w.x0 for w in line)))


def clean_latexish_line(line: str) -> str:
    line = re.sub(r"%.*$", "", line).strip()
    if not line:
        return ""
    line = re.sub(r"\\externalhref\{[^{}]*\}\{([^{}]*)\}", r"\1", line)
    for _ in range(4):
        line = re.sub(r"\\(?:textbf|texttt|emph)\{([^{}]*)\}", r"\1", line)
    line = re.sub(r"\\(?:item|datedline|dateRange|logosection|quad|,|;|small|fa[A-Za-z]+)\b", " ", line)
    line = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", line)
    line = line.replace("{", " ").replace("}", " ")
    line = line.replace("$", " ")
    return normalize_text(line)


def source_lines(path: Path | None) -> list[str]:
    if not path:
        return []
    lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = clean_latexish_line(raw_line)
        if len(comparable(line)) >= 4:
            lines.append(line)
    return lines


def correct_with_source(text: str, candidates: list[str], threshold: float) -> str:
    key = comparable(text)
    if not key or not candidates:
        return text
    best_line = text
    best_score = 0.0
    for candidate in candidates:
        score = SequenceMatcher(None, key, comparable(candidate)).ratio()
        if score > best_score:
            best_score = score
            best_line = candidate
    return best_line if best_score >= threshold else text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ocr", required=True, type=Path, help="OCR JSON path")
    parser.add_argument("--output", required=True, type=Path, help="Layout JSON output path")
    parser.add_argument("--image-width", type=int, help="Source image width in pixels")
    parser.add_argument("--image-height", type=int, help="Source image height in pixels")
    parser.add_argument("--source-text", type=Path, help="Authoritative source text file")
    parser.add_argument("--source-match-threshold", type=float, default=0.82)
    parser.add_argument("--min-confidence", type=float)
    parser.add_argument("--y-tolerance", type=float, help="Override line grouping y tolerance in pixels")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    words = load_words(args.ocr, args.min_confidence)
    if not words:
        raise SystemExit("no OCR words with text and boxes were found")
    candidates = source_lines(args.source_text)
    lines = []
    for line_words in group_lines(words, args.y_tolerance):
        text = join_words(line_words)
        text = correct_with_source(text, candidates, args.source_match_threshold)
        lines.append({"text": text, "bbox": bbox_union(line_words)})

    result: dict[str, Any] = {"units": "px", "items": lines}
    if args.image_width:
        result["image_width"] = args.image_width
    if args.image_height:
        result["image_height"] = args.image_height
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(lines)} layout items to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
