#!/usr/bin/env python3
"""PubMed journal recommendation script.
Enter the title and abstract, extract keywords to search PubMed, count journal frequencies and output a recommendation list."""
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
    "EMAIL": "your_email@example.com",
    "TOOL": "pubmed-journal-recommender",
    "API_KEY": "",
    "RETMAX": 50,
    "TOP_N": 10,
    "TIMEOUT": 20,
    "RATE_LIMIT_SECONDS": 0.35,
    "INPUT_JSON": "",
    "OUTPUT_DIR": Path("outputs/pubmed_journal_recommendation"),
    "OUTPUT_BASENAME": "pubmed_journal_recommendation",
    "OUTPUT_CSV": True,
    "KEYWORD_COUNT": 10,
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
    if isinstance(input_path, (str, Path)) and str(input_path).strip():
        path = Path(input_path)
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
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
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\\-]{1,}", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def extract_keywords(title: str, abstract: str, count: int) -> List[str]:
    text = f"{title} {abstract}".strip()
    if not text:
        return []
    tokens = tokenize(text)
    freq = Counter(tokens)
    return [word for word, _ in freq.most_common(count)]


def build_query(title: str, keywords: List[str]) -> str:
    parts = []
    if title:
        parts.append(f"\"{title}\"[Title]")
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
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
        params
    )
    data = fetch_json(url)
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmids: List[str]) -> Dict[str, Dict]:
    if not pmids:
        return {}
    params = build_params(",".join(pmids))
    params.update({"id": ",".join(pmids)})
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
        params
    )
    data = fetch_json(url)
    return data.get("result", {})


def collect_journals(summary: Dict[str, Dict], pmids: List[str]) -> Counter:
    counter = Counter()
    for pmid in pmids:
        item = summary.get(pmid, {})
        journal = item.get("fulljournalname") or item.get("source", "")
        if journal:
            counter[journal] += 1
    return counter


def save_json(payload: Dict) -> Path:
    out_dir = CONFIG["OUTPUT_DIR"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{CONFIG['OUTPUT_BASENAME']}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def save_csv(journals: List[Dict[str, str]]) -> Path:
    out_dir = CONFIG["OUTPUT_DIR"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{CONFIG['OUTPUT_BASENAME']}.csv"
    fieldnames = ["journal", "count"]
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in journals:
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
    journal_counts = collect_journals(summary, pmids)
    top_journals = journal_counts.most_common(CONFIG["TOP_N"])

    output = {
        "query": term,
        "keywords": keywords,
        "count": len(pmids),
        "top_journals": [
            {"journal": name, "count": count} for name, count in top_journals
        ],
    }
    json_path = save_json(output)
    csv_path = save_csv(output["top_journals"]) if CONFIG["OUTPUT_CSV"] else None

    print(f"Analysis completed：{len(pmids)} documents。")
    print("Recommended journals:")
    for item in output["top_journals"]:
        print(f"- {item['journal']} ({item['count']})")
    print(f"JSON output：{json_path}")
    if csv_path:
        print(f"CSV output：{csv_path}")


if __name__ == "__main__":
    main()
