import argparse
import csv
import pathlib
import sys

try:
    from pypdf import PdfReader, PdfWriter
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing dependency. Run: pip install -r scripts/requirements.txt") from exc

try:
    import pdfplumber
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing dependency. Run: pip install -r scripts/requirements.txt") from exc

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing dependency. Run: pip install -r scripts/requirements.txt") from exc


def parse_page_range(value, max_pages):
    if not value:
        return list(range(max_pages))
    parts = value.split(",")
    pages = []
    for part in parts:
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start = int(start) - 1
            end = int(end) - 1
            pages.extend(list(range(start, end + 1)))
        else:
            pages.append(int(part) - 1)
    pages = [p for p in pages if 0 <= p < max_pages]
    return pages


def merge_pdfs(inputs, output):
    writer = PdfWriter()
    for path in inputs:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output, "wb") as handle:
        writer.write(handle)
    return {"pages": len(writer.pages)}


def split_pdf(input_path, output_dir):
    reader = PdfReader(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = output_dir / f"page_{i}.pdf"
        with open(out_path, "wb") as handle:
            writer.write(handle)
        count += 1
    return {"pages": count}


def extract_pages(input_path, output_path, page_range):
    reader = PdfReader(input_path)
    pages = parse_page_range(page_range, len(reader.pages))
    writer = PdfWriter()
    for idx in pages:
        writer.add_page(reader.pages[idx])
    with open(output_path, "wb") as handle:
        writer.write(handle)
    return {"pages": len(pages)}


def extract_text(input_path, output_path, page_range):
    reader = PdfReader(input_path)
    pages = parse_page_range(page_range, len(reader.pages))
    texts = []
    for idx in pages:
        texts.append(reader.pages[idx].extract_text() or "")
    output_path.write_text("\n".join(texts), encoding="utf-8")
    return {"pages": len(pages)}


def extract_tables(input_path, output_dir, page_range):
    output_dir.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(input_path) as pdf:
        pages = parse_page_range(page_range, len(pdf.pages))
        table_count = 0
        for idx in pages:
            page = pdf.pages[idx]
            tables = page.extract_tables() or []
            for t_index, table in enumerate(tables, start=1):
                out_path = output_dir / f"page_{idx + 1}_table_{t_index}.csv"
                with open(out_path, "w", encoding="utf-8", newline="") as handle:
                    writer = csv.writer(handle)
                    for row in table:
                        writer.writerow(row)
                table_count += 1
    return {"tables": table_count}


def create_pdf_from_text(input_txt, output_pdf):
    content = input_txt.read_text(encoding="utf-8")
    c = canvas.Canvas(str(output_pdf), pagesize=letter)
    width, height = letter
    y = height - 72
    for line in content.splitlines():
        c.drawString(72, y, line)
        y -= 14
        if y < 72:
            c.showPage()
            y = height - 72
    c.save()
    return {"pages": "unknown"}


def main():
    parser = argparse.ArgumentParser(description="Basic PDF processing tool")
    parser.add_argument("--operation", required=True, help="merge|split|extract-pages|extract-text|extract-tables|create")
    parser.add_argument("--inputs", nargs="*", default=[], help="Input PDF paths")
    parser.add_argument("--input", help="Single input path")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--output-dir", help="Output directory")
    parser.add_argument("--pages", help="Page range like 1-3,5")
    args = parser.parse_args()

    op = args.operation

    if op == "merge":
        if not args.inputs or not args.output:
            raise SystemExit("merge requires --inputs and --output")
        result = merge_pdfs([pathlib.Path(p) for p in args.inputs], pathlib.Path(args.output))
    elif op == "split":
        if not args.input or not args.output_dir:
            raise SystemExit("split requires --input and --output-dir")
        result = split_pdf(pathlib.Path(args.input), pathlib.Path(args.output_dir))
    elif op == "extract-pages":
        if not args.input or not args.output:
            raise SystemExit("extract-pages requires --input and --output")
        result = extract_pages(pathlib.Path(args.input), pathlib.Path(args.output), args.pages)
    elif op == "extract-text":
        if not args.input or not args.output:
            raise SystemExit("extract-text requires --input and --output")
        result = extract_text(pathlib.Path(args.input), pathlib.Path(args.output), args.pages)
    elif op == "extract-tables":
        if not args.input or not args.output_dir:
            raise SystemExit("extract-tables requires --input and --output-dir")
        result = extract_tables(pathlib.Path(args.input), pathlib.Path(args.output_dir), args.pages)
    elif op == "create":
        if not args.input or not args.output:
            raise SystemExit("create requires --input (txt) and --output (pdf)")
        result = create_pdf_from_text(pathlib.Path(args.input), pathlib.Path(args.output))
    else:
        raise SystemExit("Unsupported operation")

    summary = {"operation": op, "result": result}
    print(summary)


if __name__ == "__main__":
    main()
