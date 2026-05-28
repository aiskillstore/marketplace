import argparse
import pathlib
import re
from collections import Counter

try:
    from pypdf import PdfReader
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing dependency. Run: pip install -r scripts/requirements.txt") from exc

YEAR_RE = re.compile(r"(19|20)\d{2}")
JOURNAL_HINTS = ("journal", "proceedings", "transactions")


def extract_years(text):
    if not text:
        return []
    return [int(m.group(0)) for m in YEAR_RE.finditer(text)]


def extract_year_from_text(text):
    years = extract_years(text)
    if not years:
        return None, False
    unique_years = sorted(set(years))
    return years[0], len(unique_years) > 1


def extract_year_from_metadata(metadata):
    if not metadata:
        return None, False
    values = []
    for val in metadata.values():
        if val is None:
            continue
        values.append(str(val))
    if not values:
        return None, False
    text = " ".join(values)
    return extract_year_from_text(text)


def extract_journal_from_text(text):
    if not text:
        return None, False
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates = []
    for line in lines:
        lowered = line.lower()
        if any(hint in lowered for hint in JOURNAL_HINTS):
            if 4 <= len(line) <= 120:
                candidates.append(line)
    if not candidates:
        return None, False
    unique = list(dict.fromkeys(candidates))
    return unique[0], len(unique) > 1


def extract_journal_from_metadata(metadata):
    if not metadata:
        return None, False
    for key in ("/Journal", "/Subject", "/Title"):
        val = metadata.get(key)
        if val:
            return str(val), False
    return None, False


def normalize_journal(name):
    if not name:
        return name
    value = re.sub(r"\s+", " ", name.strip()).rstrip(".,")
    if value.isupper() or value.islower():
        value = value.title()
    return value


def format_table(rows, headers):
    table = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["----"] * len(headers)) + " |"]
    for row in rows:
        table.append("| " + " | ".join(row) + " |")
    return "\n".join(table)


def main():
    parser = argparse.ArgumentParser(description="Compute year and journal distributions from PDFs")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output", default=None, help="Output markdown file path")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories")
    args = parser.parse_args()

    input_dir = pathlib.Path(args.input_dir).expanduser()
    if not input_dir.is_dir():
        raise SystemExit("Input directory not found")

    pattern = "**/*.pdf" if args.recursive else "*.pdf"
    pdf_paths = sorted(input_dir.glob(pattern))
    if not pdf_paths:
        raise SystemExit("No PDF files found in the directory")

    year_counts = Counter()
    journal_counts = Counter()
    unknown_year = 0
    unknown_journal = 0
    ambiguous_year = 0
    ambiguous_journal = 0

    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(str(pdf_path))
        except Exception:
            unknown_year += 1
            unknown_journal += 1
            continue

        metadata = reader.metadata or {}
        first_page_text = ""
        if reader.pages:
            try:
                first_page_text = reader.pages[0].extract_text() or ""
            except Exception:
                first_page_text = ""

        year, year_amb = extract_year_from_metadata(metadata)
        if year is None:
            year, year_amb_text = extract_year_from_text(first_page_text)
            year_amb = year_amb or year_amb_text

        journal, journal_amb = extract_journal_from_metadata(metadata)
        if journal is None:
            journal, journal_amb_text = extract_journal_from_text(first_page_text)
            journal_amb = journal_amb or journal_amb_text

        if year is None:
            unknown_year += 1
            year_key = "Unknown"
        else:
            year_key = str(year)
        if journal is None:
            unknown_journal += 1
            journal_key = "Unknown"
        else:
            journal_key = normalize_journal(journal)

        if year_amb:
            ambiguous_year += 1
        if journal_amb:
            ambiguous_journal += 1

        year_counts[year_key] += 1
        journal_counts[journal_key] += 1

    total = sum(year_counts.values())

    def rows_from_counts(counter):
        items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
        rows = []
        for key, count in items:
            percent = (count / total * 100) if total else 0
            rows.append([str(key), str(count), f"{percent:.2f}%"])
        return rows

    year_table = format_table(rows_from_counts(year_counts), ["Year", "Count", "Percent"])
    journal_table = format_table(rows_from_counts(journal_counts), ["Journal", "Count", "Percent"])

    summary_lines = [
        f"- Total items: {total}",
        f"- Unknown year: {unknown_year}",
        f"- Unknown journal: {unknown_journal}",
    ]
    if ambiguous_year:
        summary_lines.append(f"- Ambiguous year: {ambiguous_year}")
    if ambiguous_journal:
        summary_lines.append(f"- Ambiguous journal: {ambiguous_journal}")

    output = "\n".join(
        [
            "Year distribution:",
            "",
            year_table,
            "",
            "Journal distribution:",
            "",
            journal_table,
            "",
            "Summary:",
            "\n".join(summary_lines),
        ]
    )

    if args.output:
        output_path = pathlib.Path(args.output)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
