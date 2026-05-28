#!/usr/bin/env python3
"""Reference Finder - Automatically find PubMed references for scientific research texts

How to use:
1. Install dependencies: pip install requests
2. Run: python scripts/find_refs.py "your scientific research text"

Description:
- Automatically search relevant literature based on PubMed API
- Return the 3 most relevant documents for each sentence
- No API key required"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# API configuration
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
API_TIMEOUT = 30
REQUEST_INTERVAL = 0.5


def require_requests():
    """Check the requests library"""
    try:
        import requests

        return requests
    except ImportError:
        print("[ERROR] The requests library is missing.")
        print("[Tip] Please run: pip install requests")
        raise SystemExit(1)


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text"""
    keywords = set()

    # Priority: match professional terms
    patterns = [
        r"[A-Z][a-z]+-[A-Z][a-z]+",  # CRISPR-Cas9, muscle-wasting
        r"\w+osis\b",  # atrophy, necrosis
        r"\w+emia\b",  # anemia
        r"\w+oma\b",  # carcinoma, sarcoma
        r"\w+itis\b",  # myocarditis
        r"\w+penia\b",  # neutropenia
        r"[A-Z]{2,}",  # DNA, RNA, ATP, mRNA, PCR
        r"\w+ therapy\b",  # chemotherapy, therapy
        r"\w+ treatment\b",  # treatment
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.update(matches)

    # Core word matching (independent words)
    core_words = [
        "muscle",
        "wasting",
        "atrophy",
        "cachexia",
        "cancer",
        "chemotherapy",
        "treatment",
        "efficacy",
        "toxicity",
        "morbidity",
    ]
    for word in core_words:
        if re.search(r"\b" + word + r"\b", text, re.IGNORECASE):
            keywords.add(word)

    # Filter: Exclude common English stop words
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "while",
        "enables",
        "decreases",
        "thus",
        "enabling",
        "increasing",
        "continuous",
    }
    keywords = {k for k in keywords if k.lower() not in stopwords}

    return list(keywords)[:5]


def search_pubmed(query: str, max_results: int = 10) -> List[str]:
    """Search PubMed, return PMID list"""
    import urllib.parse
    import urllib.request
    import json

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance",
    }

    query_string = urllib.parse.urlencode(params)
    url = f"{ESEARCH_URL}?{query_string}"

    try:
        with urllib.request.urlopen(url, timeout=API_TIMEOUT) as response:
            data = json.loads(response.read().decode())
            return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"[warn] PubMed Search failed: {e}")
        return []


def fetch_details(pmid_list: List[str]) -> List[Dict[str, Any]]:
    """Get document details"""
    import urllib.parse
    import urllib.request
    import xml.etree.ElementTree as ET

    if not pmid_list:
        return []

    ids = ",".join(pmid_list)
    params = {"db": "pubmed", "id": ids, "retmode": "xml"}

    query_string = urllib.parse.urlencode(params)
    url = f"{EFETCH_URL}?{query_string}"

    papers = []
    try:
        with urllib.request.urlopen(url, timeout=API_TIMEOUT) as response:
            xml_data = response.read().decode()
            root = ET.fromstring(xml_data)

            for article in root.findall(".//PubmedArticle"):
                paper = {}

                medline_citation = article.find("MedlineCitation")
                article_data = medline_citation.find("Article")

                # PMID
                pmid_node = medline_citation.find("PMID")
                paper["pmid"] = pmid_node.text if pmid_node is not None else "Unknown"

                # Title
                title_node = article_data.find("ArticleTitle")
                paper["title"] = (
                    title_node.text if title_node is not None else "No title"
                )

                # DOI
                doi_node = article_data.find("ELocationID")
                if doi_node is not None and "doi" in doi_node.get("doi", "").lower():
                    paper["doi"] = doi_node.text
                else:
                    paper["doi"] = ""

                # Year
                journal = article_data.find("Journal")
                pub_date = journal.find("JournalIssue").find("PubDate")
                year = pub_date.find("Year")
                paper["year"] = year.text if year is not None else "Unknown"

                papers.append(paper)

    except Exception as e:
        print(f"[warn] Failed to obtain document details: {e}")

    return papers


def calculate_relevance(paper: Dict, keywords: List[str]) -> int:
    """Calculate relevance score"""
    score = 0

    title_lower = paper.get("title", "").lower()

    for keyword in keywords:
        if keyword.lower() in title_lower:
            score += 10

    # Year weight (higher in the past 5 years)
    try:
        year = int(paper.get("year", 0))
        if year >= 2020:
            score += 5
        elif year >= 2015:
            score += 3
    except ValueError:
        pass

    return score


def find_references(text: str, max_refs: int = 3) -> List[Dict[str, Any]]:
    """Find references for text

    Args:
        text: input scientific research text
        max_refs: The maximum number of documents returned per sentence

    Returns:
        Related literature list"""
    requests = require_requests()

    # Extract keywords
    keywords = extract_keywords(text)
    if not keywords:
        print("[Warning] Failed to extract keywords, full text search will be used")
        keywords = text.split()[:5]

    print(f"[information] keywords: {', '.join(keywords)}")

    # Search PubMed
    query = " ".join(keywords)
    time.sleep(REQUEST_INTERVAL)

    pmids = search_pubmed(query, max_results=max_refs * 3)
    if not pmids:
        print("[Warning] No relevant documents found")
        return []

    # Get details
    time.sleep(REQUEST_INTERVAL)
    papers = fetch_details(pmids)

    # Calculate relevance and sort
    for paper in papers:
        paper["relevance_score"] = calculate_relevance(paper, keywords)

    papers.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Return top N
    results = []
    for paper in papers[:max_refs]:
        results.append(
            {
                "pmid": paper.get("pmid", ""),
                "title": paper.get("title", ""),
                "doi": paper.get("doi", ""),
                "year": paper.get("year", ""),
                "reason": f"keywords '{keywords[0]}' High degree of matching",
            }
        )

    return results


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences"""
    sentences = re.split(r"[.!?\n]+", text)
    return [s.strip() for s in sentences if s.strip()]


def interactive_mode():
    """interactive mode"""
    print("=" * 60)
    print("Reference Finder - automatic reference search")
    print("=" * 60)

    print("Please enter scientific research text (example of use by pressing enter):")

    text = sys.stdin.read().strip()
    if not text:
        text = "CRISPR-Cas9 gene editing has revolutionized biomedical research. It enables precise modifications of DNA sequences."

    print(f"\n[information] Processing text...")
    print("-" * 60)

    # split sentence
    sentences = split_into_sentences(text)

    all_references = {}

    for i, sentence in enumerate(sentences, 1):
        if not sentence:
            continue

        print(f"\nsentence {i}: {sentence[:80]}...")
        references = find_references(sentence)

        for ref in references:
            pmid = ref.get("pmid", "")
            if pmid and pmid not in all_references:
                all_references[pmid] = ref

        print(f"turn up {len(references)} documents")

    # Remove duplicates and output
    print("\n" + "=" * 60)
    print("Summary of references ({} in total):".format(len(all_references)))
    print("=" * 60)

    for i, (pmid, ref) in enumerate(all_references.items(), 1):
        print(f"\n{i}. {ref['title']}")
        print(f"   PMID: {ref['pmid']}")
        print(f"   Year: {ref['year']}")
        print(f"   DOI: {ref['doi']}")

    return all_references


def main():
    # Check command line parameters
    if len(sys.argv) > 1:
        # command line mode
        text = " ".join(sys.argv[1:])
        print(f"[information] Find literature: {text[:50]}...")
        references = find_references(text)

        print(f"\nturn up {len(references)} related documents：\n")
        for i, ref in enumerate(references, 1):
            print(f"{i}. {ref['title']}")
            print(f"   PMID: {ref['pmid']}")
            print(f"   Year: {ref['year']}")
            print(f"   DOI: {ref['doi']}")
            print(f"   reason: {ref['reason']}")
            print()
    else:
        # interactive mode
        interactive_mode()

    print("\n" + "=" * 60)
    print("Query completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
