#!/usr/bin/env python3
"""Create local evidence for safe PDF redesigns.

Outputs:
- extracted-text.txt
- manifest.json
- pages/page-001.png ...
- images/image-001.<ext> ...
"""

from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path

try:
    import fitz
except ImportError as exc:
    raise SystemExit("PyMuPDF is required for this helper. Install with: python -m pip install pymupdf") from exc


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def add_fact(facts: list[dict], category: str, label: str, value: str) -> None:
    value = re.sub(r"\s+", " ", value).strip(" :#-\n\t")
    if len(value) < 2:
        return
    key = (category, label.lower(), normalize_text(value))
    if any((f["category"], f["label"].lower(), normalize_text(f["value"])) == key for f in facts):
        return
    facts.append({"category": category, "label": label, "value": value, "preserve_exactly": True})


def extract_critical_facts(text: str) -> list[dict]:
    compact = re.sub(r"\s+", " ", text)
    compact = re.sub(r"(\d{1,2}[-/]\d{1,2}[-/])\s+(\d{2,4})", r"\1\2", compact)
    facts: list[dict] = []
    is_rta_receipt = "e-Receipt For Online Driving License Application" in text

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    label_re = re.compile(
        r"^(UID|GSTIN|PAN|Application\s+(?:Number|No\.?)|Reference\s+(?:Number|No\.?)|Invoice\s+(?:Number|No\.?)|Receipt\s+(?:Number|No\.?)|Booking\s+(?:Number|No\.?|ID)|Order\s+(?:Number|No\.?)|DL\s+(?:Number|No\.?)|License\s+(?:Number|No\.?)|Bank\s+Reference\s+No|Transaction\s+ID|CPG\s+TrnID)\s*:?\s*(.*)$",
        flags=re.IGNORECASE,
    )
    known_labels = {
        "office name",
        "applicant name",
        "date of birth",
        "application no",
        "receipt no",
        "bank / gateway",
        "bank reference no",
        "transaction id",
        "cpg trnid",
        "fee amount",
        "total",
    }

    if not is_rta_receipt:
        for index, line in enumerate(lines):
            match = label_re.match(line)
            if not match:
                continue
            label, value = match.group(1), match.group(2)
            if not value and index + 1 < len(lines):
                value = lines[index + 1]
            if value.strip().lower() not in known_labels and re.search(r"\d", value):
                add_fact(facts, "identifier", label, value)

    receipt_patterns = {
        "Application No": r"\b\d{10}\b",
        "Receipt No": r"\b[A-Z]{2}\d{2}[A-Z]/\d+\b",
        "Bank Reference No": r"\b\d{12,16}\b",
        "Transaction ID": r"\b[A-Z]{2}\d{4}[A-Z]\d{10}\b",
        "CPG TrnID": r"\b[A-Z]{3}\d{13}\b",
    }
    if is_rta_receipt:
        for label, pattern in receipt_patterns.items():
            for match in re.findall(pattern, compact):
                add_fact(facts, "identifier", label, match)

    for value in re.findall(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", compact):
        add_fact(facts, "date", "Date", value)
    for value in re.findall(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?(?:-\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:AM|PM|am|pm)?)?\b", compact):
        add_fact(facts, "time", "Time", value)
    for value in re.findall(r"\b\d{1,2}\.\d{2}\s*(?:AM|PM|am|pm)(?:-\d{1,2}\.\d{2}\s*(?:AM|PM|am|pm))?\b", compact):
        add_fact(facts, "time", "Time", value)
    for value in re.findall(r"(?:Rs\.?|₹|\$|€|£)?\s?\b\d{1,3}(?:,\d{3})*(?:\.\d{2})\b", compact):
        if re.search(r"\d+\.\d{2}", value):
            add_fact(facts, "amount", "Amount", value)

    return facts[:50]


def looks_machine_readable(image_bytes: bytes, width: int, height: int) -> bool:
    try:
        from PIL import Image
        import io
    except ImportError:
        return False

    aspect = width / max(height, 1)
    if width <= 0 or height <= 0 or not (0.05 <= aspect <= 18):
        return False

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        img.thumbnail((96, 96))
        data = img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata()
        pixels = list(data)
    except Exception:
        return False

    if not pixels:
        return False
    total = len(pixels)
    dark = sum(1 for px in pixels if px < 55) / total
    light = sum(1 for px in pixels if px > 200) / total
    mid = 1 - dark - light
    return dark >= 0.05 and light >= 0.35 and mid <= 0.55


def classify_image(page_rect: fitz.Rect, bbox: tuple[float, float, float, float], width: int, height: int, image_bytes: bytes) -> str:
    x0, y0, x1, y1 = bbox
    rendered_width = max(x1 - x0, 1)
    rendered_height = max(y1 - y0, 1)
    is_top = y0 <= page_rect.height * 0.28
    is_right = x0 >= page_rect.width * 0.58
    is_left = x1 <= page_rect.width * 0.35
    area = rendered_width * rendered_height
    page_area = page_rect.width * page_rect.height

    if looks_machine_readable(image_bytes, width, height) and (is_right or not is_left):
        return "machine_code"
    if is_top and is_left:
        return "logo_or_seal"
    if area >= page_area * 0.06:
        return "watermark_or_stamp"
    return "source_image"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract PDF evidence for safe prettification.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--render-scale", type=float, default=2.0)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    pages_dir = args.out / "pages"
    images_dir = args.out / "images"
    pages_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    doc = fitz.open(args.pdf)
    page_texts = []
    images = []
    seen = set()

    for page_index, page in enumerate(doc):
        page_texts.append(page.get_text("text"))
        pix = page.get_pixmap(matrix=fitz.Matrix(args.render_scale, args.render_scale), alpha=False)
        pix.save(pages_dir / f"page-{page_index + 1:03d}.png")

        for info in page.get_image_info(xrefs=True):
            xref = info.get("xref")
            if not xref or (page_index, xref) in seen:
                continue
            seen.add((page_index, xref))
            extracted = doc.extract_image(xref)
            image_bytes = extracted.get("image", b"")
            if not image_bytes:
                continue
            ext = (extracted.get("ext") or "png").lower()
            image_id = f"image-{len(images) + 1:03d}"
            image_path = images_dir / f"{image_id}.{ext}"
            image_path.write_bytes(image_bytes)
            bbox = tuple(round(v, 2) for v in info.get("bbox", (0, 0, 0, 0)))
            role = classify_image(page.rect, bbox, info.get("width", 0), info.get("height", 0), image_bytes)
            images.append({
                "id": image_id,
                "role": role,
                "page": page_index + 1,
                "width": info.get("width"),
                "height": info.get("height"),
                "bbox": bbox,
                "path": str(image_path),
                "data_uri_preview": "data:image/%s;base64,%s" % (ext, base64.b64encode(image_bytes[:32]).decode("ascii")),
            })

    text = "\n\n".join(page_texts).strip()
    (args.out / "extracted-text.txt").write_text(text, encoding="utf-8")
    manifest = {
        "source_pdf": str(args.pdf),
        "page_count": doc.page_count,
        "critical_facts": extract_critical_facts(text),
        "preserved_images": images,
        "rendered_pages_dir": str(pages_dir),
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    doc.close()

    print(args.out / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
