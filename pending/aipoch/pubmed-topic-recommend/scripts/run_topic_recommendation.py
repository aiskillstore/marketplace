#!/usr/bin/env python3
"""Generate topic recommendations based on PubMed search results.

How to use:
1. Fill in the direction, keywords and filter conditions in the configuration area
2. Run: python scripts/run_topic_recommendation.py
3. View the result JSON in output/"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


CONFIG = {
    "direction": "",
    "requirements": "",
    "keywords": [],
    "exclude_keywords": [],
    "article_types": [],
    "start_date": "2019/01/01",
    "end_date": "2024/12/31",
    "max_results": 60,
    "sort": "relevance",
    "api_key": "",
    "email": "",
    "tool": "pubmed-topic-recommend",
    "recommendation_count": 5,
    "output_dir": "output",
    "output_filename": "topic_recommendations.json",
}


PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


STOPWORDS = {
    "and",
    "with",
    "from",
    "into",
    "that",
    "this",
    "these",
    "those",
    "using",
    "based",
    "study",
    "studies",
    "analysis",
    "effects",
    "effect",
    "impact",
    "approach",
    "methods",
    "method",
    "role",
    "via",
    "for",
    "the",
    "a",
    "an",
    "in",
    "on",
    "of",
    "to",
    "by",
    "after",
    "before",
    "between",
    "during",
    "across",
    "toward",
    "towards",
    "within",
    "over",
    "under",
}


ARTICLE_TYPE_MAP = {
    "review": "review[Publication Type]",
    "systematic review": "systematic review[Publication Type]",
    "meta-analysis": "meta-analysis[Publication Type]",
    "clinical trial": "clinical trial[Publication Type]",
    "randomized controlled trial": "randomized controlled trial[Publication Type]",
}


def _clean_list(values):
    return [item.strip() for item in values if item and item.strip()]


def _quote_term(term):
    term = term.strip()
    if not term:
        return ""
    return f"\"{term}\""


def build_query(config):
    keywords = _clean_list(config.get("keywords", []))
    exclude_keywords = _clean_list(config.get("exclude_keywords", []))
    direction = config.get("direction", "").strip()
    extra_terms = _clean_list([direction]) if direction else []

    term_parts = []

    if keywords:
        keyword_terms = [
            f"{_quote_term(keyword)}[Title/Abstract]" for keyword in keywords
        ]
        term_parts.append("(" + " OR ".join(keyword_terms) + ")")

    if extra_terms:
        extra_terms = [
            f"{_quote_term(term)}[Title/Abstract]" for term in extra_terms
        ]
        term_parts.append("(" + " OR ".join(extra_terms) + ")")

    if exclude_keywords:
        exclude_terms = [
            f"{_quote_term(keyword)}[Title/Abstract]" for keyword in exclude_keywords
        ]
        term_parts.append("NOT (" + " OR ".join(exclude_terms) + ")")

    article_types = _clean_list(config.get("article_types", []))
    if article_types:
        mapped = []
        for item in article_types:
            key = item.strip().lower()
            mapped.append(ARTICLE_TYPE_MAP.get(key, f"{_quote_term(item)}[Publication Type]"))
        term_parts.append("(" + " OR ".join(mapped) + ")")

    if not term_parts:
        raise ValueError("The keyword is empty, please fill in keywords or direction in CONFIG.")

    return " AND ".join(term_parts)


def _build_common_params(config):
    params = {
        "db": "pubmed",
        "tool": config.get("tool", ""),
        "email": config.get("email", ""),
    }
    api_key = config.get("api_key", "").strip()
    if api_key:
        params["api_key"] = api_key
    return params


def _http_get(url, params):
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v})
    full_url = f"{url}?{query}"
    with urllib.request.urlopen(full_url, timeout=30) as response:
        return response.read()


def fetch_pubmed_ids(config, term):
    params = _build_common_params(config)
    params.update(
        {
            "term": term,
            "retmax": str(config.get("max_results", 60)),
            "retmode": "xml",
            "sort": config.get("sort", "relevance"),
            "datetype": "pdat",
            "mindate": config.get("start_date", ""),
            "maxdate": config.get("end_date", ""),
        }
    )
    response = _http_get(PUBMED_BASE + "esearch.fcgi", params)
    root = ET.fromstring(response)
    return [elem.text for elem in root.findall(".//IdList/Id") if elem.text]


def fetch_pubmed_summaries(config, ids):
    params = _build_common_params(config)
    params.update(
        {
            "id": ",".join(ids),
            "retmode": "json",
        }
    )
    response = _http_get(PUBMED_BASE + "esummary.fcgi", params)
    data = json.loads(response.decode("utf-8"))
    result = data.get("result", {})
    summaries = []
    for uid in result.get("uids", []):
        item = result.get(uid, {})
        summaries.append(
            {
                "uid": uid,
                "title": item.get("title", ""),
                "pubdate": item.get("pubdate", ""),
                "source": item.get("source", ""),
                "authors": [author.get("name", "") for author in item.get("authors", [])],
            }
        )
    return summaries


def _extract_tokens(text):
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text)
    cleaned = []
    for token in tokens:
        lower = token.lower()
        if lower in STOPWORDS:
            continue
        if len(lower) < 4:
            continue
        cleaned.append(token)
    return cleaned


def _build_keyword_pool(articles, fallback_keywords):
    counts = {}
    for article in articles:
        for token in _extract_tokens(article.get("title", "")):
            key = token.lower()
            counts[key] = counts.get(key, 0) + 1
    sorted_tokens = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    tokens = [token for token, _ in sorted_tokens]
    if not tokens:
        tokens = [item.lower() for item in fallback_keywords]
    return tokens


def _select_supporting_articles(articles, keyword_a, keyword_b):
    matches = []
    pattern_a = re.compile(re.escape(keyword_a), re.IGNORECASE)
    pattern_b = re.compile(re.escape(keyword_b), re.IGNORECASE)
    for article in articles:
        title = article.get("title", "")
        if pattern_a.search(title) or pattern_b.search(title):
            matches.append(article)
        if len(matches) >= 2:
            break
    if matches:
        return matches
    return articles[:2]


def build_recommendations(config, articles):
    keywords = _clean_list(config.get("keywords", []))
    pool = _build_keyword_pool(articles, keywords)
    if not pool:
        pool = ["topic", "method"]

    templates = [
        "Research on the crossover mechanism of {kw1} and {kw2}",
        "{kw2} prediction model and evaluation for {kw1}",
        "{kw1} related {kw2} intervention strategy optimization",
        "Clinical/application verification of {kw2} in the {kw1} scenario",
        "Exploration of new indicators or new methods based on {kw2}",
    ]

    recommendations = []
    count = max(1, int(config.get("recommendation_count", 5)))
    for index in range(count):
        kw1 = pool[(index * 2) % len(pool)]
        kw2 = pool[(index * 2 + 1) % len(pool)]
        title = templates[index % len(templates)].format(kw1=kw1, kw2=kw2)
        supporting = _select_supporting_articles(articles, kw1, kw2)
        support_titles = [
            f"{item.get('title', '')} ({item.get('pubdate', '')})"
            for item in supporting
        ]
        direction = config.get("direction", "").strip()
        requirements = config.get("requirements", "").strip()
        rationale_parts = []
        if direction:
            rationale_parts.append(f"focus direction：{direction}")
        if requirements:
            rationale_parts.append(f"Require：{requirements}")
        rationale_parts.append("It is consistent with the theme of recent literature and has room for expansion.")
        recommendations.append(
            {
                "title": title,
                "rationale": "；".join(rationale_parts),
                "supporting_articles": support_titles,
            }
        )
    return recommendations


def main():
    term = build_query(CONFIG)
    print(f"search query：{term}")

    ids = fetch_pubmed_ids(CONFIG, term)
    if not ids:
        print("No documents were found, please relax the conditions and try again.")
        return

    time.sleep(0.4)
    summaries = fetch_pubmed_summaries(CONFIG, ids)
    recommendations = build_recommendations(CONFIG, summaries)

    output_dir = CONFIG.get("output_dir", "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, CONFIG.get("output_filename", "topic_recommendations.json"))

    payload = {
        "query": {
            "term": term,
            "direction": CONFIG.get("direction", ""),
            "requirements": CONFIG.get("requirements", ""),
            "keywords": CONFIG.get("keywords", []),
            "exclude_keywords": CONFIG.get("exclude_keywords", []),
            "article_types": CONFIG.get("article_types", []),
            "date_range": {
                "start": CONFIG.get("start_date", ""),
                "end": CONFIG.get("end_date", ""),
            },
            "sort": CONFIG.get("sort", ""),
        },
        "articles": summaries,
        "topic_recommendations": recommendations,
    }

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    print(f"Results generated：{output_path}")


if __name__ == "__main__":
    main()
