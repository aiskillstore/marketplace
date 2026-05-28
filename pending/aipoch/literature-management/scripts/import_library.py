import argparse
import hashlib
import json
import pathlib
import re
import shutil
import uuid
from datetime import datetime

try:
    from pypdf import PdfReader
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing dependency. Run: pip install -r scripts/requirements.txt") from exc

YEAR_RE = re.compile(r"(19|20)\d{2}")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)

SUPPORTED_EXTS = {".pdf", ".bib", ".ris", ".csv", ".txt"}


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_doi(value):
    if not value:
        return None
    value = value.strip()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    return value.lower()


def normalize_title(value):
    value = normalize_whitespace(value)
    return value.lower() if value else None


def normalize_journal(value):
    value = normalize_whitespace(value)
    if not value:
        return None
    value = value.rstrip(".,")
    if value.isupper() or value.islower():
        value = value.title()
    return value


def safe_dir_name(value, fallback):
    if not value:
        return fallback
    value = re.sub(r"[\/:*?\"<>|]", "_", value)
    value = value.strip().strip(".")
    return value or fallback


def parse_keywords(value):
    if not value:
        return []
    separators = [";", ",", "|", "/"]
    for sep in separators:
        if sep in value:
            parts = [normalize_whitespace(p) for p in value.split(sep)]
            return [p for p in parts if p]
    return [normalize_whitespace(value)] if value else []


def extract_years(text):
    return [int(m.group(0)) for m in YEAR_RE.finditer(text or "")]


def extract_doi(text):
    if not text:
        return None
    match = DOI_RE.search(text)
    return match.group(0) if match else None


def hash_file(path):
    sha1 = hashlib.sha1()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            sha1.update(chunk)
    return sha1.hexdigest()


def read_pdf_metadata(path):
    reader = PdfReader(str(path))
    metadata = reader.metadata or {}
    first_page_text = ""
    if reader.pages:
        try:
            first_page_text = reader.pages[0].extract_text() or ""
        except Exception:
            first_page_text = ""
    return metadata, first_page_text


def parse_pdf(path):
    metadata, first_page_text = read_pdf_metadata(path)
    title = metadata.get("/Title") or None
    journal = metadata.get("/Journal") or metadata.get("/Subject") or None
    authors = metadata.get("/Author") or None
    keywords = metadata.get("/Keywords") or None

    year = None
    text_for_year = " ".join([str(v) for v in metadata.values() if v])
    years = extract_years(text_for_year)
    if years:
        year = str(years[0])
    else:
        years = extract_years(first_page_text)
        if years:
            year = str(years[0])

    doi = extract_doi(first_page_text) or extract_doi(text_for_year)

    return {
        "title": normalize_whitespace(title) if title else None,
        "year": year,
        "journal": normalize_journal(journal),
        "authors": [normalize_whitespace(a) for a in re.split(r";|,", authors) if normalize_whitespace(a)]
        if authors
        else [],
        "keywords": parse_keywords(keywords),
        "doi": normalize_doi(doi),
    }


def parse_bibtex(text):
    entries = re.split(r"\n@", text)
    results = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        title = re.search(r"\btitle\s*=\s*\{([^}]+)\}", entry, re.IGNORECASE)
        year = re.search(r"\byear\s*=\s*\{?([0-9]{4})\}?", entry, re.IGNORECASE)
        journal = re.search(r"\bjournal\s*=\s*\{([^}]+)\}", entry, re.IGNORECASE)
        author = re.search(r"\bauthor\s*=\s*\{([^}]+)\}", entry, re.IGNORECASE)
        keywords = re.search(r"\bkeywords\s*=\s*\{([^}]+)\}", entry, re.IGNORECASE)
        doi = re.search(r"\bdoi\s*=\s*\{([^}]+)\}", entry, re.IGNORECASE)
        results.append(
            {
                "title": normalize_whitespace(title.group(1)) if title else None,
                "year": year.group(1) if year else None,
                "journal": normalize_journal(journal.group(1)) if journal else None,
                "authors": [normalize_whitespace(a) for a in (author.group(1).split(" and ") if author else []) if a],
                "keywords": parse_keywords(keywords.group(1)) if keywords else [],
                "doi": normalize_doi(doi.group(1)) if doi else None,
            }
        )
    return results


def parse_ris(text):
    parts = re.split(r"\nER\s*-\s*\n", text)
    results = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = [line.strip() for line in part.splitlines() if line.strip()]

        def field(tags):
            for line in lines:
                for tag in tags:
                    if line.startswith(tag + "  -") or line.startswith(tag + " -"):
                        value = line.split("-", 1)[-1].strip()
                        if value:
                            return value
            return None
        title = field(("TI", "T1"))
        year = field(("PY", "Y1"))
        if year:
            match = YEAR_RE.search(year)
            year = match.group(0) if match else None
        journal = field(("JO", "JF", "T2"))
        doi = field(("DO",))
        authors = [line.split("-", 1)[-1].strip() for line in lines if line.startswith("AU")]
        keywords = [line.split("-", 1)[-1].strip() for line in lines if line.startswith("KW")]

        results.append(
            {
                "title": normalize_whitespace(title) if title else None,
                "year": year,
                "journal": normalize_journal(journal) if journal else None,
                "authors": [normalize_whitespace(a) for a in authors if normalize_whitespace(a)],
                "keywords": [normalize_whitespace(k) for k in keywords if normalize_whitespace(k)],
                "doi": normalize_doi(doi) if doi else None,
            }
        )
    return results


def parse_csv(text):
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = [h.strip().lower() for h in lines[0].split(",")]
    results = []
    for row in lines[1:]:
        cols = [c.strip() for c in row.split(",")]
        record = dict(zip(header, cols))
        results.append(
            {
                "title": normalize_whitespace(record.get("title")),
                "year": record.get("year"),
                "journal": normalize_journal(record.get("journal")),
                "authors": parse_keywords(record.get("authors")),
                "keywords": parse_keywords(record.get("keywords")),
                "doi": normalize_doi(record.get("doi")),
            }
        )
    return results


def parse_plain_text(text):
    entries = [e.strip() for e in text.split("\n\n") if e.strip()]
    results = []
    for entry in entries:
        years = extract_years(entry)
        year = str(years[0]) if years else None
        doi = extract_doi(entry)
        results.append(
            {
                "title": None,
                "year": year,
                "journal": None,
                "authors": [],
                "keywords": [],
                "doi": normalize_doi(doi),
            }
        )
    return results


def dedup_key_for(record, file_hash=None):
    if record.get("doi"):
        return f"doi:{record['doi']}", "doi"
    title = normalize_title(record.get("title"))
    year = record.get("year")
    if title and year:
        return f"title_year:{title}|{year}", "title_year"
    if file_hash:
        return f"hash:{file_hash}", "file_hash"
    return f"unknown:{uuid.uuid4().hex}", "unknown"


def load_existing_keys(index_path):
    keys = set()
    if not index_path.exists():
        return keys
    with index_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = data.get("dedup_key")
            if key:
                keys.add(key)
    return keys


def append_record(index_path, record):
    with index_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def copy_file(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        counter = 1
        while True:
            candidate = dest.with_name(f"{stem}_{counter}{suffix}")
            if not candidate.exists():
                dest = candidate
                break
            counter += 1
    shutil.copy2(src, dest)
    return dest


def move_file(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        counter = 1
        while True:
            candidate = dest.with_name(f"{stem}_{counter}{suffix}")
            if not candidate.exists():
                dest = candidate
                break
            counter += 1
    shutil.move(src, dest)
    return dest

def main():
    parser = argparse.ArgumentParser(description="Import local literature into a managed library")
    parser.add_argument("--source-dir", required=True, help="Directory containing source files")
    parser.add_argument("--library-dir", required=True, help="Target library directory")
    parser.add_argument("--tag", action="append", default=[], help="Manual tag to apply (repeatable)")
    parser.add_argument("--move", action="store_true", help="Move files instead of copy")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing")
    parser.add_argument("--no-auto-tags", action="store_true", help="Disable auto tags from metadata keywords")
    args = parser.parse_args()

    source_dir = pathlib.Path(args.source_dir).expanduser()
    library_dir = pathlib.Path(args.library_dir).expanduser()
    if not source_dir.is_dir():
        raise SystemExit("Source directory not found")
    library_dir.mkdir(parents=True, exist_ok=True)
    index_path = library_dir / "index.jsonl"

    existing_keys = load_existing_keys(index_path)
    imported = 0
    skipped = 0
    errors = 0

    pattern = "**/*" if args.recursive else "*"
    files = [p for p in source_dir.glob(pattern) if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]

    for path in files:
        try:
            if path.suffix.lower() == ".pdf":
                record = parse_pdf(path)
                file_hash = hash_file(path)
                record["source_type"] = "pdf"
            else:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if path.suffix.lower() == ".bib":
                    records = parse_bibtex(text)
                elif path.suffix.lower() == ".ris":
                    records = parse_ris(text)
                elif path.suffix.lower() == ".csv":
                    records = parse_csv(text)
                else:
                    records = parse_plain_text(text)
                for rec in records:
                    key, rule = dedup_key_for(rec)
                    if key in existing_keys:
                        skipped += 1
                        continue
                    rec_tags = list(dict.fromkeys([t for t in args.tag if t]))
                    if not args.no_auto_tags:
                        rec_tags.extend([k for k in rec.get("keywords", []) if k])
                        rec_tags = list(dict.fromkeys(rec_tags))
                    record_out = {
                        "id": uuid.uuid4().hex,
                        "title": rec.get("title"),
                        "year": rec.get("year"),
                        "journal": rec.get("journal"),
                        "authors": rec.get("authors", []),
                        "keywords": rec.get("keywords", []),
                        "doi": rec.get("doi"),
                        "tags": rec_tags,
                        "source_type": path.suffix.lower().lstrip("."),
                        "source_path": str(path),
                        "file_path": None,
                        "dedup_key": key,
                        "dedup_rule": rule,
                        "imported_at": datetime.utcnow().isoformat() + "Z",
                    }
                    if not args.dry_run:
                        append_record(index_path, record_out)
                        existing_keys.add(key)
                    imported += 1
                continue

            key, rule = dedup_key_for(record, file_hash=file_hash)
            if key in existing_keys:
                skipped += 1
                continue

            year_dir = safe_dir_name(record.get("year"), "UnknownYear")
            journal_dir = safe_dir_name(record.get("journal"), "UnknownJournal")
            target_dir = library_dir / "files" / year_dir / journal_dir
            target_path = target_dir / path.name

            if args.dry_run:
                file_path = str(target_path)
            else:
                if args.move:
                    file_path = str(move_file(path, target_path))
                else:
                    file_path = str(copy_file(path, target_path))

            tags = list(dict.fromkeys([t for t in args.tag if t]))
            if not args.no_auto_tags:
                tags.extend([k for k in record.get("keywords", []) if k])
                tags = list(dict.fromkeys(tags))

            record_out = {
                "id": uuid.uuid4().hex,
                "title": record.get("title"),
                "year": record.get("year"),
                "journal": record.get("journal"),
                "authors": record.get("authors", []),
                "keywords": record.get("keywords", []),
                "doi": record.get("doi"),
                "tags": tags,
                "source_type": "pdf",
                "source_path": str(path),
                "file_path": file_path,
                "dedup_key": key,
                "dedup_rule": rule,
                "imported_at": datetime.utcnow().isoformat() + "Z",
            }
            if not args.dry_run:
                append_record(index_path, record_out)
                existing_keys.add(key)
            imported += 1
        except Exception:
            errors += 1

    summary = {
        "imported": imported,
        "skipped_duplicates": skipped,
        "errors": errors,
        "index_path": str(index_path),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
