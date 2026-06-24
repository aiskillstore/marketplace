# -*- coding: utf-8 -*-
"""
Format converters for academic citations.
Supports: MEDLINE/.nbib -> RIS/BibTeX/ENW, CrossRef JSON -> RIS/BibTeX/ENW, arXiv XML -> RIS/BibTeX/ENW.

Each converter accepts parsed data and returns a formatted string.
"""

import re


def ris_escape(text):
    """Strip HTML tags and normalize whitespace for safe RIS field output."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_medline_fields(nbib_text):
    """Parse MEDLINE text into a dict of tag -> [values]."""
    fields = {}
    current_tag = None
    current_value = []

    for line in nbib_text.split("\n"):
        if len(line) >= 6 and line[0:4] != "    " and line[4:6] == "- ":
            if current_tag:
                fields.setdefault(current_tag, []).append(" ".join(current_value))
            current_tag = line[0:4].strip()
            current_value = [line[6:].strip()]
        elif line.startswith("      ") and current_tag:
            current_value.append(line[6:].strip())
        elif not line.strip():
            if current_tag:
                fields.setdefault(current_tag, []).append(" ".join(current_value))
            current_tag = None
            current_value = []

    if current_tag:
        fields.setdefault(current_tag, []).append(" ".join(current_value))

    return fields


def _get_first(fields, tag):
    vals = fields.get(tag, [])
    return vals[0] if vals else ""


def _extract_doi(fields):
    # MEDLINE often emits the PII variant of LID/AID before the DOI variant
    # (e.g. ScienceDirect/Cell Press records); scan every value, not just the
    # first one, so the DOI is not silently dropped.
    for tag in ("LID", "AID"):
        for val in fields.get(tag, []):
            if val and "[doi]" in val:
                return val.replace(" [doi]", "")
    return ""


def _extract_year(fields):
    dp = _get_first(fields, "DP")
    return dp[:4] if dp else ""


# ── MEDLINE -> RIS ──────────────────────────────────────────────

def medline_to_ris(fields):
    lines = ["TY  - JOUR"]

    for au in fields.get("AU", []):
        lines.append(f"AU  - {ris_escape(au)}")

    ti = _get_first(fields, "TI")
    if ti:
        lines.append(f"TI  - {ris_escape(ti)}")

    jt = _get_first(fields, "JT")
    ta = _get_first(fields, "TA")
    if jt:
        lines.append(f"JO  - {ris_escape(jt)}")
        lines.append(f"T2  - {ris_escape(jt)}")
    if ta:
        lines.append(f"JA  - {ris_escape(ta)}")

    year = _extract_year(fields)
    if year:
        lines.append(f"PY  - {year}")

    vi = _get_first(fields, "VI")
    ip = _get_first(fields, "IP")
    if vi:
        lines.append(f"VL  - {vi}")
    if ip:
        lines.append(f"IS  - {ip}")

    pg = _get_first(fields, "PG")
    if pg and "-" in pg:
        sp, ep = pg.split("-", 1)
        lines.append(f"SP  - {sp.strip()}")
        lines.append(f"EP  - {ep.strip()}")
    elif pg:
        lines.append(f"SP  - {pg}")

    doi = _extract_doi(fields)
    if doi:
        lines.append(f"DO  - {doi}")
        lines.append(f"UR  - https://doi.org/{doi}")

    ab = _get_first(fields, "AB")
    if ab:
        lines.append(f"N2  - {ris_escape(ab)[:500]}")

    for mh in fields.get("MH", []):
        lines.append(f"KW  - {ris_escape(mh)}")

    pmid = _get_first(fields, "PMID")
    if pmid:
        lines.append(f"AN  - PMID:{pmid}")

    lines.append("DB  - PubMed")
    lines.append("ER  - ")
    return "\n".join(lines) + "\n"


# ── MEDLINE -> BibTeX ────────────────────────────────────────────

def medline_to_bib(fields):
    pmid = _get_first(fields, "PMID")
    citation_key = f"pmid{pmid}" if pmid else "unknown"

    lines = [f"@article{{{citation_key},"]

    aus = fields.get("AU", [])
    if aus:
        lines.append(f"  author  = {{ {' and '.join(aus)} }},")

    ti = _get_first(fields, "TI")
    if ti:
        lines.append(f"  title   = {{{{{ti}}}}},")

    jt = _get_first(fields, "JT")
    if jt:
        lines.append(f"  journal = {{{jt}}},")

    year = _extract_year(fields)
    if year:
        lines.append(f"  year    = {{{year}}},")

    vi = _get_first(fields, "VI")
    if vi:
        lines.append(f"  volume  = {{{vi}}},")

    ip = _get_first(fields, "IP")
    if ip:
        lines.append(f"  number  = {{{ip}}},")

    pg = _get_first(fields, "PG")
    if pg:
        lines.append(f"  pages   = {{{pg.replace('-', '--')}}},")

    doi = _extract_doi(fields)
    if doi:
        lines.append(f"  doi     = {{{doi}}},")

    ab = _get_first(fields, "AB")
    if ab:
        lines.append(f"  abstract = {{{ab}}},")

    if pmid:
        lines.append(f"  pmid    = {{{pmid}}},")

    lines.append("}")
    return "\n".join(lines) + "\n"


# ── CrossRef JSON -> RIS ─────────────────────────────────────────

def crossref_to_ris(data):
    """Convert CrossRef API JSON response to RIS format."""
    msg = data.get("message", data)
    lines = ["TY  - JOUR"]

    for author in msg.get("author", []):
        family = author.get("family", "")
        given = author.get("given", "")
        if family:
            lines.append(f"AU  - {ris_escape(family)}, {ris_escape(given)}")

    title = msg.get("title", [])
    if title:
        lines.append(f"TI  - {ris_escape(title[0])}")

    container = msg.get("container-title", [])
    short_container = msg.get("short-container-title", [])
    if container:
        lines.append(f"JO  - {ris_escape(container[0])}")
        lines.append(f"T2  - {ris_escape(container[0])}")
    if short_container:
        lines.append(f"JA  - {ris_escape(short_container[0])}")

    issued = msg.get("issued", {})
    date_parts = issued.get("date-parts", [[None]])[0]
    year = str(date_parts[0]) if date_parts and date_parts[0] else ""
    if year:
        lines.append(f"PY  - {year}")

    volume = msg.get("volume", "")
    issue = msg.get("issue", "")
    if volume:
        lines.append(f"VL  - {volume}")
    if issue:
        lines.append(f"IS  - {issue}")

    page = msg.get("page", "")
    if page and "-" in page:
        sp, ep = page.split("-", 1)
        lines.append(f"SP  - {sp.strip()}")
        lines.append(f"EP  - {ep.strip()}")
    elif page:
        lines.append(f"SP  - {page}")

    doi = msg.get("DOI", "")
    if doi:
        lines.append(f"DO  - {doi}")
        lines.append(f"UR  - https://doi.org/{doi}")

    abstract = msg.get("abstract", "")
    if abstract:
        abstract = re.sub(r"<[^>]+>", "", abstract)
        lines.append(f"N2  - {ris_escape(abstract)[:500]}")

    lines.append("DB  - CrossRef")
    lines.append("ER  - ")
    return "\n".join(lines) + "\n"


# ── CrossRef JSON -> BibTeX ──────────────────────────────────────

def crossref_to_bib(data):
    """Convert CrossRef API JSON response to BibTeX format."""
    msg = data.get("message", data)

    first_author = msg.get("author", [{}])[0].get("family", "unknown") if msg.get("author") else "unknown"
    issued = msg.get("issued", {})
    date_parts = issued.get("date-parts", [[None]])[0]
    year = str(date_parts[0]) if date_parts and date_parts[0] else ""
    citation_key = f"{first_author.lower()}{year}"

    lines = [f"@article{{{citation_key},"]

    authors = []
    for author in msg.get("author", []):
        family = author.get("family", "")
        given = author.get("given", "")
        if family:
            authors.append(f"{family}, {given}")
    if authors:
        lines.append(f"  author  = {{ {' and '.join(authors)} }},")

    title = msg.get("title", [])
    if title:
        lines.append(f"  title   = {{{{{title[0]}}}}},")

    container = msg.get("container-title", [])
    if container:
        lines.append(f"  journal = {{{container[0]}}},")

    if year:
        lines.append(f"  year    = {{{year}}},")

    volume = msg.get("volume", "")
    if volume:
        lines.append(f"  volume  = {{{volume}}},")

    issue = msg.get("issue", "")
    if issue:
        lines.append(f"  number  = {{{issue}}},")

    page = msg.get("page", "")
    if page:
        lines.append(f"  pages   = {{{page.replace('-', '--')}}},")

    doi = msg.get("DOI", "")
    if doi:
        lines.append(f"  doi     = {{{doi}}},")

    abstract = msg.get("abstract", "")
    if abstract:
        abstract = re.sub(r"<[^>]+>", "", abstract)
        lines.append(f"  abstract = {{{abstract}}},")

    lines.append("}")
    return "\n".join(lines) + "\n"


# ── arXiv XML -> RIS ─────────────────────────────────────────────

def arxiv_to_ris(root):
    """Convert arXiv API Atom XML response (xml.etree root) to RIS format."""
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    entry = root.find("atom:entry", ns)
    if entry is None:
        return ""

    lines = ["TY  - JOUR"]

    for author in entry.findall("atom:author", ns):
        name = author.find("atom:name", ns)
        if name is not None and name.text:
            parts = name.text.rsplit(" ", 1)
            if len(parts) == 2:
                lines.append(f"AU  - {ris_escape(parts[1])}, {ris_escape(parts[0])}")
            else:
                lines.append(f"AU  - {ris_escape(name.text)}")

    title_el = entry.find("atom:title", ns)
    title = title_el.text.strip() if title_el is not None and title_el.text else ""
    if title:
        lines.append(f"TI  - {ris_escape(title)}")

    lines.append("JO  - arXiv preprint")
    lines.append("T2  - arXiv preprint")

    published = entry.find("atom:published", ns)
    year = published.text[:4] if published is not None and published.text else ""
    if year:
        lines.append(f"PY  - {year}")

    arxiv_id_el = entry.find("atom:id", ns)
    arxiv_id = arxiv_id_el.text.strip() if arxiv_id_el is not None and arxiv_id_el.text else ""
    if "/abs/" in arxiv_id:
        arxiv_id = arxiv_id.split("/abs/")[-1]
    if arxiv_id:
        lines.append(f"DO  - {arxiv_id}")
        lines.append(f"UR  - https://arxiv.org/abs/{arxiv_id}")

    summary_el = entry.find("atom:summary", ns)
    abstract = summary_el.text.strip() if summary_el is not None and summary_el.text else ""
    if abstract:
        lines.append(f"N2  - {ris_escape(abstract)[:500]}")

    lines.append("DB  - arXiv")
    lines.append("ER  - ")
    return "\n".join(lines) + "\n"


# ── arXiv XML -> BibTeX ──────────────────────────────────────────

def arxiv_to_bib(root):
    """Convert arXiv API Atom XML response to BibTeX format."""
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    entry = root.find("atom:entry", ns)
    if entry is None:
        return ""

    arxiv_id_el = entry.find("atom:id", ns)
    arxiv_id = arxiv_id_el.text.strip() if arxiv_id_el is not None and arxiv_id_el.text else ""
    if "/abs/" in arxiv_id:
        arxiv_id = arxiv_id.split("/abs/")[-1]
    citation_key = arxiv_id.replace(".", "").replace("/", "") if arxiv_id else "unknown"

    lines = [f"@article{{{citation_key},"]

    authors = []
    for author in entry.findall("atom:author", ns):
        name = author.find("atom:name", ns)
        if name is not None and name.text:
            parts = name.text.rsplit(" ", 1)
            if len(parts) == 2:
                authors.append(f"{parts[1]}, {parts[0]}")
            else:
                authors.append(name.text)
    if authors:
        lines.append(f"  author  = {{ {' and '.join(authors)} }},")

    title_el = entry.find("atom:title", ns)
    title = title_el.text.strip() if title_el is not None and title_el.text else ""
    if title:
        lines.append(f"  title   = {{{{{title}}}}},")

    lines.append("  journal = {arXiv preprint},")

    published = entry.find("atom:published", ns)
    year = published.text[:4] if published is not None and published.text else ""
    if year:
        lines.append(f"  year    = {{{year}}},")

    if arxiv_id:
        lines.append(f"  doi     = {{{arxiv_id}}},")
        lines.append(f"  url     = {{https://arxiv.org/abs/{arxiv_id}}},")

    summary_el = entry.find("atom:summary", ns)
    abstract = summary_el.text.strip() if summary_el is not None and summary_el.text else ""
    if abstract:
        lines.append(f"  abstract = {{{abstract}}},")

    lines.append("}")
    return "\n".join(lines) + "\n"


# ── MEDLINE -> ENW ───────────────────────────────────────────────

def medline_to_enw(fields):
    lines = ["%0 Journal Article"]

    ti = _get_first(fields, "TI")
    if ti:
        lines.append(f"%T {ris_escape(ti)}")

    for au in fields.get("AU", []):
        lines.append(f"%A {ris_escape(au)}")

    jt = _get_first(fields, "JT")
    if jt:
        lines.append(f"%J {ris_escape(jt)}")

    vi = _get_first(fields, "VI")
    if vi:
        lines.append(f"%V {vi}")

    ip = _get_first(fields, "IP")
    if ip:
        lines.append(f"%N {ip}")

    pg = _get_first(fields, "PG")
    if pg:
        lines.append(f"%P {pg}")

    year = _extract_year(fields)
    if year:
        lines.append(f"%D {year}")

    doi = _extract_doi(fields)
    if doi:
        lines.append(f"%R {doi}")
        lines.append(f"%U https://doi.org/{doi}")

    ab = _get_first(fields, "AB")
    if ab:
        lines.append(f"%X {ris_escape(ab)[:500]}")

    return "\n".join(lines) + "\n"


# ── CrossRef JSON -> ENW ──────────────────────────────────────────

def crossref_to_enw(data):
    msg = data.get("message", data)
    lines = ["%0 Journal Article"]

    title = msg.get("title", [])
    if title:
        lines.append(f"%T {ris_escape(title[0])}")

    for author in msg.get("author", []):
        family = author.get("family", "")
        given = author.get("given", "")
        if family:
            lines.append(f"%A {ris_escape(family)}, {ris_escape(given)}")

    container = msg.get("container-title", [])
    if container:
        lines.append(f"%J {ris_escape(container[0])}")

    volume = msg.get("volume", "")
    if volume:
        lines.append(f"%V {volume}")

    issue = msg.get("issue", "")
    if issue:
        lines.append(f"%N {issue}")

    page = msg.get("page", "")
    if page:
        lines.append(f"%P {page}")

    issued = msg.get("issued", {})
    date_parts = issued.get("date-parts", [[None]])[0]
    year = str(date_parts[0]) if date_parts and date_parts[0] else ""
    if year:
        lines.append(f"%D {year}")

    doi = msg.get("DOI", "")
    if doi:
        lines.append(f"%R {doi}")
        lines.append(f"%U https://doi.org/{doi}")

    abstract = msg.get("abstract", "")
    if abstract:
        abstract = re.sub(r"<[^>]+>", "", abstract)
        lines.append(f"%X {ris_escape(abstract)[:500]}")

    return "\n".join(lines) + "\n"


# ── arXiv XML -> ENW ──────────────────────────────────────────────

def arxiv_to_enw(root):
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    entry = root.find("atom:entry", ns)
    if entry is None:
        return ""

    lines = ["%0 Journal Article"]

    title_el = entry.find("atom:title", ns)
    title = title_el.text.strip() if title_el is not None and title_el.text else ""
    if title:
        lines.append(f"%T {ris_escape(title)}")

    for author in entry.findall("atom:author", ns):
        name = author.find("atom:name", ns)
        if name is not None and name.text:
            parts = name.text.rsplit(" ", 1)
            if len(parts) == 2:
                lines.append(f"%A {ris_escape(parts[1])}, {ris_escape(parts[0])}")
            else:
                lines.append(f"%A {ris_escape(name.text)}")

    lines.append("%J arXiv preprint")

    published = entry.find("atom:published", ns)
    year = published.text[:4] if published is not None and published.text else ""
    if year:
        lines.append(f"%D {year}")

    arxiv_id_el = entry.find("atom:id", ns)
    arxiv_id = arxiv_id_el.text.strip() if arxiv_id_el is not None and arxiv_id_el.text else ""
    if "/abs/" in arxiv_id:
        arxiv_id = arxiv_id.split("/abs/")[-1]
    if arxiv_id:
        lines.append(f"%R {arxiv_id}")
        lines.append(f"%U https://arxiv.org/abs/{arxiv_id}")

    summary_el = entry.find("atom:summary", ns)
    abstract = summary_el.text.strip() if summary_el is not None and summary_el.text else ""
    if abstract:
        lines.append(f"%X {ris_escape(abstract)[:500]}")

    return "\n".join(lines) + "\n"


# ── Format dispatch ─────────────────────────────────────────────

def convert_from_medline(nbib_text, fmt):
    """Convert MEDLINE/.nbib text to RIS, BibTeX, or ENW."""
    fields = parse_medline_fields(nbib_text)
    if fmt == "ris":
        return medline_to_ris(fields)
    elif fmt == "bib":
        return medline_to_bib(fields)
    elif fmt == "enw":
        return medline_to_enw(fields)
    return nbib_text


def convert_from_crossref(json_data, fmt):
    """Convert CrossRef JSON to RIS, BibTeX, or ENW."""
    if fmt == "ris":
        return crossref_to_ris(json_data)
    elif fmt == "bib":
        return crossref_to_bib(json_data)
    elif fmt == "enw":
        return crossref_to_enw(json_data)
    raise ValueError(f"Unsupported CrossRef format: {fmt}")


def convert_from_arxiv(xml_root, fmt):
    """Convert arXiv Atom XML to RIS, BibTeX, or ENW."""
    if fmt == "ris":
        return arxiv_to_ris(xml_root)
    elif fmt == "bib":
        return arxiv_to_bib(xml_root)
    elif fmt == "enw":
        return arxiv_to_enw(xml_root)
    raise ValueError(f"Unsupported arXiv format: {fmt}")


def get_extension(fmt):
    return {"nbib": ".nbib", "ris": ".ris", "bib": ".bib", "enw": ".enw"}.get(fmt, ".nbib")
