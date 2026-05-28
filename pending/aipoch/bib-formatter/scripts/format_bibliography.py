#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import requests


def parse_args():
    parser = argparse.ArgumentParser(
        prog="format_bibliography.py",
        description="Reference formatting script (CSL style)",
    )
    parser.add_argument(
        "--input",
        "-i",
        default="-",
        help="Enter the file path. If omitted, it will be read from STDIN.",
    )
    parser.add_argument(
        "--input-format",
        "-f",
        choices=["auto", "ris", "bibtex", "text", "csljson"],
        default="auto",
        help="Input format",
    )
    style_group = parser.add_mutually_exclusive_group(required=True)
    style_group.add_argument(
        "--style",
        "-s",
        help="CSL style file path (.csl)",
    )
    style_group.add_argument(
        "--journal",
        help="Journal name, automatic retrieval CSL style",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path, if omitted, it will be written to STDOUT",
    )
    parser.add_argument(
        "--mode",
        choices=["bibliography", "citations"],
        default="bibliography",
        help="Output mode: bibliography=reference list, citations=text citations",
    )
    parser.add_argument(
        "--cite-keys",
        help="Text citation entry IDs, comma separated, only used in citations mode",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding",
    )
    return parser.parse_args()


def read_text(path, encoding):
    if not path or path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding=encoding) as handle:
        return handle.read()


def write_text(path, text, encoding):
    if not path:
        sys.stdout.write(text)
        return
    with open(path, "w", encoding=encoding) as handle:
        handle.write(text)


def detect_format(path, input_format, text):
    if input_format != "auto":
        return input_format
    if path and path != "-":
        _, ext = os.path.splitext(path.lower())
        if ext == ".ris":
            return "ris"
        if ext == ".bib":
            return "bibtex"
        if ext == ".json":
            return "csljson"
    if re.search(r"\bTY\s+-", text):
        return "ris"
    if re.search(r"@\w+\s*\{", text):
        return "bibtex"
    if text.lstrip().startswith("{") or text.lstrip().startswith("["):
        return "csljson"
    return "text"


def parse_year(value):
    if not value:
        return None
    match = re.search(r"(\d{4})", str(value))
    if not match:
        return None
    return int(match.group(1))


def build_issued(year):
    if not year:
        return None
    return {"date-parts": [[year]]}


def parse_name(name):
    if not name:
        return None
    name = name.strip()
    if not name:
        return None
    if "," in name:
        family, given = [part.strip() for part in name.split(",", 1)]
        if family and given:
            return {"family": family, "given": given}
        if family:
            return {"family": family}
    parts = name.split()
    if len(parts) == 1:
        return {"literal": name}
    family = parts[-1]
    given = " ".join(parts[:-1])
    return {"family": family, "given": given}


def parse_author_list(authors):
    result = []
    for author in authors:
        item = parse_name(author)
        if item:
            result.append(item)
        else:
            result.append({"literal": author})
    return result


def ris_type_map(value):
    if not value:
        return "article-journal"
    value = value.strip().upper()
    mapping = {
        "JOUR": "article-journal",
        "BOOK": "book",
        "CHAP": "chapter",
        "CONF": "paper-conference",
        "RPRT": "report",
        "THES": "thesis",
    }
    return mapping.get(value, "article-journal")


def ris_to_csl(entry, index):
    item = {
        "id": entry.get("id") or entry.get("ID") or f"item-{index}",
        "type": ris_type_map(entry.get("type_of_reference")),
    }
    title = (
        entry.get("title")
        or entry.get("primary_title")
        or entry.get("secondary_title")
    )
    if title:
        item["title"] = title
    journal = (
        entry.get("journal_name")
        or entry.get("periodical_name")
        or entry.get("secondary_title")
        or entry.get("journal")
    )
    if journal:
        item["container-title"] = journal
    authors = (
        entry.get("authors")
        or entry.get("primary_authors")
        or entry.get("first_authors")
        or []
    )
    if authors:
        item["author"] = parse_author_list(authors)
    year = parse_year(entry.get("publication_year") or entry.get("year") or entry.get("date"))
    issued = build_issued(year)
    if issued:
        item["issued"] = issued
    volume = entry.get("volume")
    if volume:
        item["volume"] = str(volume)
    issue = entry.get("issue")
    if issue:
        item["issue"] = str(issue)
    start_page = entry.get("start_page") or entry.get("first_page")
    end_page = entry.get("end_page") or entry.get("last_page")
    pages = entry.get("pages")
    if start_page and end_page:
        item["page"] = f"{start_page}-{end_page}"
    elif pages:
        item["page"] = str(pages)
    doi = entry.get("doi")
    if doi:
        item["DOI"] = doi
    url = entry.get("url")
    if url:
        item["URL"] = url
    publisher = entry.get("publisher")
    if publisher:
        item["publisher"] = publisher
    return item


def bibtex_type_map(value):
    if not value:
        return "article-journal"
    value = value.strip().lower()
    mapping = {
        "article": "article-journal",
        "book": "book",
        "inbook": "chapter",
        "incollection": "chapter",
        "inproceedings": "paper-conference",
        "proceedings": "book",
        "phdthesis": "thesis",
        "mastersthesis": "thesis",
        "techreport": "report",
        "misc": "article-journal",
    }
    return mapping.get(value, "article-journal")


def parse_bibtex_authors(value):
    if not value:
        return []
    parts = [part.strip() for part in value.replace("\n", " ").split(" and ") if part.strip()]
    return parse_author_list(parts)


def bibtex_to_csl(entry, index):
    item = {
        "id": entry.get("ID") or f"item-{index}",
        "type": bibtex_type_map(entry.get("ENTRYTYPE")),
    }
    title = entry.get("title")
    if title:
        item["title"] = title
    journal = entry.get("journal") or entry.get("booktitle")
    if journal:
        item["container-title"] = journal
    authors = parse_bibtex_authors(entry.get("author"))
    if authors:
        item["author"] = authors
    year = parse_year(entry.get("year"))
    issued = build_issued(year)
    if issued:
        item["issued"] = issued
    volume = entry.get("volume")
    if volume:
        item["volume"] = str(volume)
    number = entry.get("number")
    if number:
        item["issue"] = str(number)
    pages = entry.get("pages")
    if pages:
        item["page"] = pages
    doi = entry.get("doi")
    if doi:
        item["DOI"] = doi
    url = entry.get("url")
    if url:
        item["URL"] = url
    publisher = entry.get("publisher")
    if publisher:
        item["publisher"] = publisher
    return item


def parse_ris(text):
    try:
        import rispy
    except ImportError:
        print("The dependency rispy is missing, please install it first: pip install rispy", file=sys.stderr)
        sys.exit(2)
    entries = rispy.loads(text)
    return [ris_to_csl(entry, index + 1) for index, entry in enumerate(entries)]


def parse_bibtex(text):
    try:
        import bibtexparser
    except ImportError:
        print("The dependency bibtexparser is missing, please install it first: pip install bibtexparser", file=sys.stderr)
        sys.exit(2)
    database = bibtexparser.loads(text)
    return [bibtex_to_csl(entry, index + 1) for index, entry in enumerate(database.entries)]


def parse_csljson(text):
    data = json.loads(text)
    if isinstance(data, dict) and "items" in data:
        items = data["items"]
    elif isinstance(data, list):
        items = data
    else:
        print("CSL-JSON format invalid, expecting list or object containing items", file=sys.stderr)
        sys.exit(2)
    result = []
    for index, item in enumerate(items, start=1):
        if "id" not in item:
            item["id"] = f"item-{index}"
        result.append(item)
    return result


def parse_text_list(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    result = []
    for index, line in enumerate(lines, start=1):
        result.append({
            "id": f"item-{index}",
            "type": "article-journal",
            "title": line,
        })
    return result


def normalize_style_key(name):
    name = name.strip()
    if not name:
        return ""
    name = name.lower()
    if name.endswith(".csl"):
        name = name[:-4]
    name = name.replace("&", "and")
    name = re.sub(r"[\s_]+", "-", name)
    name = re.sub(r"[^a-z0-9\-]+", "", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name


def journal_to_filename(journal):
    name = normalize_style_key(journal)
    if not name:
        name = journal.strip().lower()
    return f"{name}.csl"


def try_download_direct(journal, style_dir):
    filename = journal_to_filename(journal)
    os.makedirs(style_dir, exist_ok=True)
    local_path = os.path.join(style_dir, filename)
    if os.path.exists(local_path):
        return local_path
    style_name = filename[:-4]
    url = f"https://www.zotero.org/styles/{style_name}"
    try:
        response = requests.get(url, timeout=20)
    except requests.RequestException as exc:
        print(f"Direct download of styles failed：{exc}", file=sys.stderr)
        sys.exit(2)
    if response.status_code == 200:
        with open(local_path, "wb") as handle:
            handle.write(response.content)
        return local_path
    if response.status_code == 404:
        return None
    print(f"Direct download of styles failed，HTTP {response.status_code}。", file=sys.stderr)
    sys.exit(2)


def fetch_style_index():
    url = "https://www.zotero.org/styles-files/styles.json"
    try:
        response = requests.get(url, timeout=30)
    except requests.RequestException as exc:
        print(f"Failed to retrieve styles：{exc}", file=sys.stderr)
        sys.exit(2)
    if response.status_code != 200:
        print(f"Failed to retrieve styles，HTTP {response.status_code}。", file=sys.stderr)
        sys.exit(2)
    try:
        data = response.json()
    except ValueError:
        print("Retrieval of style failed and the returned content could not be parsed.", file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, list):
        print("Failed to retrieve styles, the style index format is abnormal.", file=sys.stderr)
        sys.exit(2)
    return data


def search_style_candidates(journal):
    query = journal.strip()
    if not query:
        print("Journal name cannot be empty.", file=sys.stderr)
        sys.exit(2)
    query_lower = query.lower()
    query_norm = normalize_style_key(query)
    items = fetch_style_index()
    exact = []
    fuzzy = []
    seen = set()

    def add_candidate(bucket, item):
        key = item.get("name") or item.get("href") or item.get("title")
        if key and key not in seen:
            bucket.append(item)
            seen.add(key)

    for item in items:
        name = item.get("name", "")
        title = item.get("title", "")
        name_lower = name.lower()
        title_lower = title.lower()
        name_norm = normalize_style_key(name)
        title_norm = normalize_style_key(title)
        if query_lower == name_lower or query_lower == title_lower:
            add_candidate(exact, item)
            continue
        if query_norm and (query_norm == name_norm or query_norm == title_norm):
            add_candidate(exact, item)
            continue
        if query_lower in name_lower or query_lower in title_lower:
            add_candidate(fuzzy, item)
            continue
        if query_norm and (query_norm in name_norm or query_norm in title_norm):
            add_candidate(fuzzy, item)

    return exact or fuzzy


def choose_style_candidate(journal, items):
    if not items:
        print(f"No name found {journal} journal style", file=sys.stderr)
        sys.exit(2)
    normalized = normalize_style_key(journal)
    exact = []
    for item in items:
        name = item.get("name", "")
        title = item.get("title", "")
        if normalize_style_key(name) == normalized:
            exact.append(item)
            continue
        if normalize_style_key(title) == normalized:
            exact.append(item)
    if exact:
        return exact[0]
    if len(items) > 1:
        print("Multiple matching styles found, please provide a more precise name", file=sys.stderr)
        for item in items:
            name = item.get("name")
            title = item.get("title")
            if name and title:
                print(f"- {title} ({name})", file=sys.stderr)
            elif name:
                print(f"- {name}", file=sys.stderr)
            elif title:
                print(f"- {title}", file=sys.stderr)
        sys.exit(2)
    candidate = items[0]
    if not candidate.get("name"):
        print("The search results do not have a valid style file name.", file=sys.stderr)
        sys.exit(2)
    return candidate


def download_style_file(candidate, style_dir):
    name = candidate.get("name")
    if not name:
        print("The search results do not have a valid style file name.", file=sys.stderr)
        sys.exit(2)
    filename = f"{name}.csl"
    url = candidate.get("href") or f"https://www.zotero.org/styles/{name}"
    os.makedirs(style_dir, exist_ok=True)
    local_path = os.path.join(style_dir, filename)
    if os.path.exists(local_path):
        return local_path
    try:
        response = requests.get(url, timeout=20)
    except requests.RequestException as exc:
        print(f"Download style failed：{exc}", file=sys.stderr)
        sys.exit(2)
    if response.status_code != 200:
        print(f"Download style failed，HTTP {response.status_code}。", file=sys.stderr)
        sys.exit(2)
    with open(local_path, "wb") as handle:
        handle.write(response.content)
    return local_path


def resolve_style_path(style_path, journal):
    if style_path:
        return style_path
    style_dir = os.path.join(os.getcwd(), "styles")
    direct_path = try_download_direct(journal, style_dir)
    if direct_path:
        return direct_path
    items = search_style_candidates(journal)
    candidate = choose_style_candidate(journal, items)
    return download_style_file(candidate, style_dir)


def load_style(style_path):
    if not os.path.exists(style_path):
        print(f"not found CSL style file：{style_path}", file=sys.stderr)
        sys.exit(2)
    try:
        from citeproc import CitationStylesStyle
    except ImportError:
        print("The dependency citeproc-py is missing, please install it first: pip install citeproc-py", file=sys.stderr)
        sys.exit(2)
    return CitationStylesStyle(style_path, validate=False)


def format_bibliography(items, style):
    from citeproc import Citation, CitationItem, CitationStylesBibliography, formatter
    from citeproc.source.json import CiteProcJSON

    source = CiteProcJSON(items)
    bibliography = CitationStylesBibliography(style, source, formatter.plain)
    for item in items:
        bibliography.register(Citation([CitationItem(item["id"])]))
    return "\n".join(str(entry) for entry in bibliography.bibliography())


def format_citations(items, style, cite_keys):
    from citeproc import Citation, CitationItem, CitationStylesBibliography, formatter
    from citeproc.source.json import CiteProcJSON

    source = CiteProcJSON(items)
    bibliography = CitationStylesBibliography(style, source, formatter.plain)
    citation = Citation([CitationItem(key) for key in cite_keys])
    bibliography.register(citation)
    return str(bibliography.cite(citation, warn=True))


def main():
    args = parse_args()
    raw_text = read_text(args.input, args.encoding)
    input_format = detect_format(args.input, args.input_format, raw_text)

    if input_format == "ris":
        items = parse_ris(raw_text)
    elif input_format == "bibtex":
        items = parse_bibtex(raw_text)
    elif input_format == "csljson":
        items = parse_csljson(raw_text)
    else:
        items = parse_text_list(raw_text)

    if not items:
        print("No available entries were parsed, please check the input format.", file=sys.stderr)
        sys.exit(2)

    style_path = resolve_style_path(args.style, args.journal)
    style = load_style(style_path)

    if args.mode == "citations":
        if not args.cite_keys:
            print("citations mode requires the --cite-keys parameter.", file=sys.stderr)
            sys.exit(2)
        cite_keys = [key.strip() for key in args.cite_keys.split(",") if key.strip()]
        if not cite_keys:
            print("--cite-keys is empty, please provide at least one entry ID.", file=sys.stderr)
            sys.exit(2)
        output = format_citations(items, style, cite_keys)
    else:
        output = format_bibliography(items, style)

    write_text(args.output, output, args.encoding)


if __name__ == "__main__":
    main()
