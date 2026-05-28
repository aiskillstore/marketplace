#!/usr/bin/env python3
"""PubMed literature search script.

Enter the title and abstract, automatically extract keywords and search PubMed, and output structured results."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

CONFIG = {
    "EMAIL": "researcher@example.com",
    "TOOL": "pubmed-literature-search",
    "API_KEY": "",
    "RETMAX": 20,
    "TIMEOUT": 30,
    "RATE_LIMIT_SECONDS": 0.35,
    "INPUT_JSON": Path(__file__).parent.parent / "outputs" / "query.json",
    "OUTPUT_DIR": Path(__file__).parent.parent / "outputs" / "pubmed_search",
    "OUTPUT_BASENAME": "pubmed_search_results",
    "OUTPUT_CSV": True,
    "KEYWORD_COUNT": 8,
}

STOPWORDS = {
    "the",
    "and",
    "or",
    "of",
    "to",
    "in",
    "for",
    "with",
    "a",
    "an",
    "on",
    "by",
    "from",
    "at",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "this",
    "that",
    "these",
    "those",
    "we",
    "our",
    "using",
    "use",
    "used",
    "study",
    "studies",
    "results",
    "method",
    "methods",
    "analysis",
    "data",
    "based",
    "effect",
    "effects",
    "model",
    "models",
    "new",
    "novel",
}


def load_input() -> Tuple[str, str]:
    input_path = CONFIG["INPUT_JSON"]
    if input_path and input_path.exists():
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        title = str(payload.get("title", "")).strip()
        abstract = str(payload.get("abstract", "")).strip()
        return title, abstract

    print("Please enter a title (end with blank line):")
    title_lines: List[str] = []
    while True:
        line = input().rstrip("\n")
        if not line:
            break
        title_lines.append(line)
    print("Please enter a summary (end with blank line):")
    abstract_lines: List[str] = []
    while True:
        line = input().rstrip("\n")
        if not line:
            break
        abstract_lines.append(line)
    return " ".join(title_lines).strip(), " ".join(abstract_lines).strip()


def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]{1,}", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def extract_keywords(title: str, abstract: str, count: int) -> List[str]:
    text = f"{title} {abstract}".strip()
    if not text:
        return []
    tokens = tokenize(text)
    freq = Counter(tokens)
    keywords = [word for word, _ in freq.most_common(count)]
    return keywords


def build_query(title: str, keywords: List[str]) -> str:
    parts = []
    if title:
        parts.append(f'"{title}"[Title]')
    for word in keywords:
        parts.append(f"{word}[Title/Abstract]")
    return " AND ".join(parts) if parts else ""


def build_params(term: str) -> Dict[str, str]:
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": str(CONFIG["RETMAX"]),
        "tool": CONFIG["TOOL"],
        "email": CONFIG["EMAIL"],
    }
    if CONFIG["API_KEY"]:
        params["api_key"] = CONFIG["API_KEY"]
    return params


def fetch_json(url: str) -> Dict:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=CONFIG["TIMEOUT"]) as resp:
        payload = resp.read().decode("utf-8")
    time.sleep(CONFIG["RATE_LIMIT_SECONDS"])
    return json.loads(payload)


def esearch(term: str) -> List[str]:
    params = build_params(term)
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        + urllib.parse.urlencode(params)
    )
    data = fetch_json(url)
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmids: List[str]) -> Dict[str, Dict]:
    if not pmids:
        return {}
    ids = ",".join(pmids)
    params = build_params(ids)
    params.update({"id": ids, "retmode": "xml"})
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
        + urllib.parse.urlencode(params)
    )

    result = {}
    try:
        import xml.etree.ElementTree as ET

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=CONFIG["TIMEOUT"]) as resp:
            xml_data = resp.read().decode()
            root = ET.fromstring(xml_data)
            time.sleep(CONFIG["RATE_LIMIT_SECONDS"])

            for article in root.findall(".//PubmedArticle"):
                medline = article.find("MedlineCitation")
                pmid_node = medline.find("PMID")
                pmid = pmid_node.text if pmid_node is not None else ""

                article_data = medline.find("Article")
                title_node = article_data.find("ArticleTitle")
                title = title_node.text if title_node is not None else ""

                journal_node = article_data.find("Journal")
                journal = ""
                if journal_node is not None:
                    journal_title = journal_node.find("Title")
                    journal = journal_title.text if journal_title is not None else ""

                pubdate = ""
                journal_issue = (
                    journal_node.find("JournalIssue") if journal_node else None
                )
                if journal_issue is not None:
                    pub_date = journal_issue.find("PubDate")
                    if pub_date is not None:
                        year_node = pub_date.find("Year")
                        pubdate = year_node.text if year_node is not None else ""

                author_list = article_data.find("AuthorList") if article_data else None
                authors = []
                if author_list is not None:
                    for author in author_list.findall("Author"):
                        last = author.find("LastName")
                        fore = author.find("ForeName")
                        if last is not None:
                            name = last.text
                            if fore is not None:
                                name = f"{fore.text} {name}"
                            authors.append(name)

                result[pmid] = {
                    "title": title,
                    "fulljournalname": journal,
                    "pubdate": pubdate,
                    "authors": authors,
                }
    except Exception as e:
        print(f"[warn] Failed to obtain document details: {e}")

    return result


def parse_records(summary: Dict[str, Dict], pmids: List[str]) -> List[Dict[str, str]]:
    records = []
    for pmid in pmids:
        item = summary.get(pmid, {})
        title = item.get("title", "").rstrip(".") if item.get("title") else ""
        journal = item.get("fulljournalname", "") or item.get("source", "")
        pubdate = item.get("pubdate", "")
        authors_list = item.get("authors", [])
        if isinstance(authors_list, list):
            authors = ", ".join(authors_list)
        else:
            authors = str(authors_list)
        records.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "pubdate": pubdate,
                "authors": authors,
            }
        )
    return records


def save_json(payload: Dict) -> Path:
    out_dir = CONFIG["OUTPUT_DIR"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{CONFIG['OUTPUT_BASENAME']}.json"
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out_path


def save_csv(records: List[Dict[str, str]]) -> Path:
    out_dir = CONFIG["OUTPUT_DIR"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{CONFIG['OUTPUT_BASENAME']}.csv"
    fieldnames = ["pmid", "title", "journal", "pubdate", "authors"]
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return out_path


def main() -> None:
    title, abstract = load_input()
    keywords = extract_keywords(title, abstract, CONFIG["KEYWORD_COUNT"])
    term = build_query(title, keywords)
    if not term:
        raise ValueError("Missing search content: Please provide a title or abstract.")

    pmids = esearch(term)
    summary = esummary(pmids)
    records = parse_records(summary, pmids)

    output = {
        "query": term,
        "keywords": keywords,
        "count": len(records),
        "records": records,
    }
    json_path = save_json(output)
    csv_path = save_csv(records) if CONFIG["OUTPUT_CSV"] else None

    print(f"Search completed：{len(records)} results")
    print(f"JSON output：{json_path}")
    if csv_path:
        print(f"CSV output：{csv_path}")


if __name__ == "__main__":
    main()
