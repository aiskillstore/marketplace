#!/usr/bin/env python3
"""
Journal Latest Issue Digest
Fetch latest issue TOC and abstracts, output Markdown/CSV.
"""

import argparse
import csv
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2

ALLOWED_HOSTS = {
    "doi.org",
    "api.crossref.org",
    "crossref.org",
    "eutils.ncbi.nlm.nih.gov",
    "pubmed.ncbi.nlm.nih.gov",
    "www.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov",
    "pmc.ncbi.nlm.nih.gov",
    "www.nature.com",
    "nature.com",
    "rss.sciencedirect.com",
    "www.sciencedirect.com",
    "sciencedirect.com",
}

KNOWN_RSS = {
    "nature": "https://www.nature.com/nature.rss",
    "cell": "https://rss.sciencedirect.com/publication/science/00928674",
}


@dataclass
class JournalItem:
    journal: str
    title: str
    doi: str | None
    url: str | None
    abstract: str | None
    issue: str | None
    summary_zh: str


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: Dict[str, List[str]] = {}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        if tag.lower() != "meta":
            return
        attr_dict = {k.lower(): v for k, v in attrs}
        name = attr_dict.get("name") or attr_dict.get("property")
        content = attr_dict.get("content")
        if not name or not content:
            return
        name = name.lower()
        self.meta.setdefault(name, []).append(content.strip())


def is_allowed(url: str, allow_all: bool) -> bool:
    if allow_all:
        return True
    host = urllib.parse.urlparse(url).netloc.lower()
    return host in ALLOWED_HOSTS


def fetch_url(url: str, allow_all: bool) -> bytes:
    if not is_allowed(url, allow_all):
        raise ValueError("Host not in allowlist. Use --allow-all to override.")
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "JournalDigest/1.0",
                    "Accept": "application/json, text/html",
                    "mailto": "contact@example.com",
                },
            )
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SECONDS) as resp:
                final_url = resp.geturl()
                if not is_allowed(final_url, allow_all):
                    raise ValueError("Final host not in allowlist. Use --allow-all.")
                return resp.read()
        except urllib.error.HTTPError as e:
            if 500 <= e.code < 600 and attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise
    if last_error:
        raise last_error
    raise RuntimeError("Request failed")


def parse_rss(content: bytes) -> List[Dict[str, str]]:
    text = content.decode("utf-8", errors="ignore")
    items = []
    for about, item in re.findall(
        r"<item[^>]*rdf:about=\"(.*?)\"[^>]*>(.*?)</item>", text, flags=re.S
    ):
        title = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", item)
        if not title:
            title = re.search(r"<title>(.*?)</title>", item)
        link = re.search(r"<link>(.*?)</link>", item)
        items.append(
            {
                "title": title.group(1).strip() if title else "",
                "link": link.group(1).strip() if link else about,
            }
        )

    if items:
        return items

    for item in re.findall(r"<item[^>]*>(.*?)</item>", text, flags=re.S):
        title = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", item)
        if not title:
            title = re.search(r"<title>(.*?)</title>", item)
        link = re.search(r"<link>(.*?)</link>", item)
        items.append(
            {
                "title": title.group(1).strip() if title else "",
                "link": link.group(1).strip() if link else "",
            }
        )
    return items


def parse_meta_items(html: bytes) -> List[Dict[str, str]]:
    parser = MetaParser()
    parser.feed(html.decode("utf-8", errors="ignore"))
    titles = parser.meta.get("citation_title", [])
    dois = parser.meta.get("citation_doi", [])
    abstracts = parser.meta.get("citation_abstract", [])
    urls = parser.meta.get("citation_fulltext_html_url", [])
    items = []
    count = len(titles)
    for i in range(count):
        items.append(
            {
                "title": titles[i] if i < len(titles) else "",
                "doi": dois[i] if i < len(dois) else "",
                "abstract": abstracts[i] if i < len(abstracts) else "",
                "url": urls[i] if i < len(urls) else "",
            }
        )
    return items


def crossref_search(journal: str, allow_all: bool) -> List[Dict[str, str]]:
    query = urllib.parse.quote(journal)
    url = (
        "https://api.crossref.org/works"
        f"?query.container-title={query}&rows=20&sort=published&order=desc"
    )
    data = json.loads(fetch_url(url, allow_all).decode("utf-8"))
    return data.get("message", {}).get("items", [])


def extract_abstract_from_landing(url: str, allow_all: bool) -> Optional[str]:
    try:
        html = fetch_url(url, allow_all)
    except Exception:
        return None
    parser = MetaParser()
    parser.feed(html.decode("utf-8", errors="ignore"))
    abstracts = parser.meta.get("citation_abstract", [])
    if abstracts:
        return abstracts[0]
    for key in (
        "dc.description",
        "dc.description.abstract",
        "description",
        "og:description",
        "twitter:description",
    ):
        values = parser.meta.get(key, [])
        if values:
            return values[0]

    text = html.decode("utf-8", errors="ignore")
    jsonld_abstract = extract_jsonld_abstract(text)
    if jsonld_abstract:
        return jsonld_abstract
    return extract_abstract_block(text)


def extract_jsonld_abstract(text: str) -> Optional[str]:
    scripts = re.findall(
        r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        text,
        flags=re.I | re.S,
    )
    for script in scripts:
        payload = script.strip()
        if not payload:
            continue
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            continue
        abstract = extract_abstract_from_jsonld(data)
        if abstract:
            return abstract
    return None


def extract_abstract_from_jsonld(data: object) -> Optional[str]:
    if isinstance(data, dict):
        for key in ("abstract", "description"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for key in ("@graph", "hasPart", "mainEntity"):
            value = data.get(key)
            abstract = extract_abstract_from_jsonld(value)
            if abstract:
                return abstract
    elif isinstance(data, list):
        for item in data:
            abstract = extract_abstract_from_jsonld(item)
            if abstract:
                return abstract
    return None


def extract_abstract_block(text: str) -> Optional[str]:
    match = re.search(
        r"<(section|div)[^>]*(id|class)=[\"'][^\"']*abstract[^\"']*[\"'][^>]*>(.*?)</\1>",
        text,
        flags=re.I | re.S,
    )
    if not match:
        return None
    block = match.group(3)
    block = re.sub(r"<[^>]+>", " ", block)
    block = html.unescape(block)
    block = re.sub(r"\s+", " ", block).strip()
    return block or None


def summarize_zh(title: str, abstract: Optional[str]) -> str:
    if abstract:
        snippet = abstract.strip()
        snippet = re.sub(r"\s+", " ", snippet)
        if len(snippet) > 160:
            snippet = snippet[:160] + "..."
        return f"Chinese essentials（untranslated）：{title}。Summary excerpt：{snippet}"
    return f"Chinese essentials（untranslated）：{title}。No abstract yet。"


def clean_abstract(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def crossref_lookup_by_title(
    journal: str, title: str, allow_all: bool
) -> Tuple[Optional[str], Optional[str]]:
    query_title = urllib.parse.quote(title)
    query_journal = urllib.parse.quote(journal)
    url = (
        "https://api.crossref.org/works"
        f"?query.title={query_title}&query.container-title={query_journal}&rows=1"
    )
    data = json.loads(fetch_url(url, allow_all).decode("utf-8"))
    items = data.get("message", {}).get("items", [])
    if not items:
        return None, None
    item = items[0]
    doi = item.get("DOI")
    abstract = item.get("abstract")
    if isinstance(abstract, str):
        abstract = clean_abstract(abstract)
    return doi, abstract


def pubmed_lookup_abstract(journal: str, title: str, allow_all: bool) -> Optional[str]:
    term = f"{title}[Title] AND {journal}[Journal]"
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term={urllib.parse.quote(term)}&retmode=json"
    )
    data = json.loads(fetch_url(url, allow_all).decode("utf-8"))
    ids = data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return None
    fetch_url_xml = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=pubmed&id={ids[0]}&retmode=xml"
    )
    xml_bytes = fetch_url(fetch_url_xml, allow_all)
    root = ET.fromstring(xml_bytes)
    parts = []
    for node in root.findall(".//AbstractText"):
        if node.text:
            parts.append(node.text.strip())
    if not parts:
        return None
    return " ".join(parts)


def collect_from_sources(
    journal: str,
    rss: Optional[str],
    toc: Optional[str],
    allow_all: bool,
    max_items: int,
    fetch_abstracts: bool,
) -> List[JournalItem]:
    items: List[JournalItem] = []

    if not rss and not toc:
        rss = KNOWN_RSS.get(journal.strip().lower())

    if rss:
        rss_items = parse_rss(fetch_url(rss, allow_all))
        if max_items > 0:
            rss_items = rss_items[:max_items]
        for index, it in enumerate(rss_items):
            title = it.get("title") or ""
            url = it.get("link") or ""
            abstract = None
            if fetch_abstracts and url and index < max_items:
                abstract = extract_abstract_from_landing(url, allow_all)
            doi = None
            if fetch_abstracts and not abstract and title:
                doi, abstract = crossref_lookup_by_title(journal, title, allow_all)
            if fetch_abstracts and not abstract and title:
                abstract = pubmed_lookup_abstract(journal, title, allow_all)
            items.append(
                JournalItem(
                    journal=journal,
                    title=title,
                    doi=doi,
                    url=url,
                    abstract=abstract,
                    issue=None,
                    summary_zh=summarize_zh(title, abstract),
                )
            )

    if toc:
        toc_items = parse_meta_items(fetch_url(toc, allow_all))
        if max_items > 0:
            toc_items = toc_items[:max_items]
        for index, it in enumerate(toc_items):
            title = it.get("title") or ""
            doi = it.get("doi") or None
            url = it.get("url") or None
            abstract = it.get("abstract") or None
            if fetch_abstracts and not abstract and url and index < max_items:
                abstract = extract_abstract_from_landing(url, allow_all)
            items.append(
                JournalItem(
                    journal=journal,
                    title=title,
                    doi=doi,
                    url=url,
                    abstract=abstract,
                    issue=None,
                    summary_zh=summarize_zh(title, abstract),
                )
            )

    if not items:
        works = crossref_search(journal, allow_all)
        issue = None
        works_list = works if max_items <= 0 else works[:max_items]
        for index, w in enumerate(works_list):
            title = w.get("title", [""])[0]
            doi = w.get("DOI")
            url = w.get("URL")
            if issue is None:
                vol = w.get("volume")
                iss = w.get("issue")
                issue = f"vol {vol} issue {iss}" if vol or iss else None
            abstract = w.get("abstract")
            if fetch_abstracts and not abstract and doi:
                abstract = extract_abstract_from_landing(
                    f"https://doi.org/{doi}", allow_all
                )
            items.append(
                JournalItem(
                    journal=journal,
                    title=title,
                    doi=doi,
                    url=url,
                    abstract=abstract,
                    issue=issue,
                    summary_zh=summarize_zh(title, abstract),
                )
            )
    return items


def write_markdown(items: List[JournalItem], output: Path) -> None:
    lines = ["# A quick overview of the current issue of the journal", ""]
    grouped: Dict[str, List[JournalItem]] = {}
    for item in items:
        grouped.setdefault(item.journal, []).append(item)

    for journal, j_items in grouped.items():
        lines.append(f"## {journal}")
        for idx, it in enumerate(j_items, start=1):
            lines.append(f"- serial number: {idx}")
            lines.append(f"  - title: {it.title}")
            if it.doi:
                lines.append(f"  - DOI: {it.doi}")
            if it.url:
                lines.append(f"  - URL: {it.url}")
            if it.abstract:
                lines.append(f"  - summary: {it.abstract}")
                lines.append(f"  - Chinese essentials: {it.summary_zh}")
        lines.append("")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(items: List[JournalItem], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["index", "journal", "title", "doi", "url", "abstract", "summary_zh"]
        )
        for idx, it in enumerate(items, start=1):
            writer.writerow(
                [
                    idx,
                    it.journal,
                    it.title,
                    it.doi or "",
                    it.url or "",
                    it.abstract or "",
                    it.summary_zh,
                ]
            )


def load_config(path: str) -> List[Dict[str, str]]:
    data = json.load(open(path, "r", encoding="utf-8"))
    return data.get("journals", [])


def load_items_from_csv(path: str) -> List[JournalItem]:
    items: List[JournalItem] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("title") or "").strip()
            abstract = (row.get("abstract") or "").strip() or None
            summary = (row.get("summary_zh") or "").strip()
            items.append(
                JournalItem(
                    journal=(row.get("journal") or "").strip(),
                    title=title,
                    doi=(row.get("doi") or "").strip() or None,
                    url=(row.get("url") or "").strip() or None,
                    abstract=abstract,
                    issue=None,
                    summary_zh=summary or summarize_zh(title, abstract),
                )
            )
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Journal Latest Issue Digest")
    parser.add_argument("--journal", action="append", default=[])
    parser.add_argument("--rss", action="append", default=[])
    parser.add_argument("--toc", action="append", default=[])
    parser.add_argument("--json")
    parser.add_argument("--input-csv")
    parser.add_argument("--out-md", default="output.md")
    parser.add_argument("--out-csv", default="output.csv")
    parser.add_argument("--allow-all", action="store_true")
    parser.add_argument("--max-items", type=int, default=20)
    parser.add_argument("--fetch-abstracts", action="store_true")
    parser.add_argument("--select", default="")
    args = parser.parse_args()

    allow_all = args.allow_all
    max_items = args.max_items
    fetch_abstracts = args.fetch_abstracts
    select_raw = args.select
    targets = []

    all_items: List[JournalItem] = []
    if args.input_csv:
        all_items = load_items_from_csv(args.input_csv)
    else:
        if args.json:
            targets = load_config(args.json)
        else:
            if not args.journal:
                raise SystemExit("No journal specified")
            for idx, name in enumerate(args.journal):
                rss = args.rss[idx] if idx < len(args.rss) else None
                toc = args.toc[idx] if idx < len(args.toc) else None
                targets.append({"name": name, "rss": rss, "toc": toc})

        for t in targets:
            all_items.extend(
                collect_from_sources(
                    t["name"],
                    t.get("rss"),
                    t.get("toc"),
                    allow_all,
                    max_items,
                    fetch_abstracts,
                )
            )

    if select_raw:
        selected_indices = set()
        for token in select_raw.split(","):
            token = token.strip()
            if not token:
                continue
            try:
                selected_indices.add(int(token))
            except ValueError:
                continue

        for idx, item in enumerate(all_items, start=1):
            if idx not in selected_indices:
                item.abstract = None
                item.summary_zh = summarize_zh(item.title, None)
                continue
            if not item.abstract:
                if item.url:
                    item.abstract = extract_abstract_from_landing(item.url, allow_all)
                elif item.doi:
                    item.abstract = extract_abstract_from_landing(
                        f"https://doi.org/{item.doi}", allow_all
                    )
            item.summary_zh = summarize_zh(item.title, item.abstract)

    write_markdown(all_items, Path(args.out_md))
    write_csv(all_items, Path(args.out_csv))
    print("DONE")


if __name__ == "__main__":
    main()
