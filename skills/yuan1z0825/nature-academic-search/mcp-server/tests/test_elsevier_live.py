"""Live API tests for Scopus and ScienceDirect.

These tests intentionally call Elsevier APIs through the local pybliometrics
configuration. They are not mocked.
"""

from __future__ import annotations

import asyncio
import json
import os

import pytest
from sources import ScienceDirectSource, ScopusSource


pytestmark = pytest.mark.skipif(
    os.getenv("NATURE_ACADEMIC_SEARCH_LIVE_ELSEVIER") != "1",
    reason="set NATURE_ACADEMIC_SEARCH_LIVE_ELSEVIER=1 to run live Elsevier API tests",
)

ELSEVIER_DOI = "10.1016/j.istruc.2024.107944"
ELSEVIER_TITLE_QUERY = (
    "Seismic performance continuous rigid-frame bridges flood-induced scour"
)


def _call_tool_json(tool_name: str, arguments: dict) -> dict:
    from academic_search_server import mcp

    content, _metadata = asyncio.run(mcp.call_tool(tool_name, arguments))
    return json.loads(content[0].text)


def test_scopus_live_search_exact_doi():
    result = ScopusSource().search(f"DOI({ELSEVIER_DOI})", rows=1)

    assert result["source"] == "scopus"
    assert result["total"] >= 1
    assert len(result["results"]) == 1
    assert result["results"][0]["doi"] == ELSEVIER_DOI


def test_sciencedirect_live_search_title_query():
    result = ScienceDirectSource().search(ELSEVIER_TITLE_QUERY, rows=1)

    assert result["source"] == "sciencedirect"
    assert result["total"] >= 1
    assert len(result["results"]) == 1
    assert result["results"][0]["doi"] == ELSEVIER_DOI


def test_sciencedirect_live_article_metadata_doi_query():
    result = ScienceDirectSource().get_article_metadata(
        f"doi({ELSEVIER_DOI})",
        rows=1,
    )

    assert result["source"] == "sciencedirect"
    assert result["total"] >= 1
    assert len(result["results"]) == 1
    assert result["results"][0]["doi"] == ELSEVIER_DOI


def test_default_search_papers_uses_free_sources_only():
    payload = _call_tool_json(
        "search_papers",
        {"query": ELSEVIER_TITLE_QUERY, "rows": 1},
    )

    assert payload["sources_queried"] == ["crossref", "pubmed", "arxiv"]
    assert "scopus" not in payload["sources_queried"]
    assert "sciencedirect" not in payload["sources_queried"]


def test_explicit_search_papers_includes_elsevier_sources():
    payload = _call_tool_json(
        "search_papers",
        {
            "query": ELSEVIER_TITLE_QUERY,
            "sources": ["scopus", "sciencedirect"],
            "rows": 1,
        },
    )

    assert payload["sources_queried"] == ["scopus", "sciencedirect"]
    assert any(item["source"] == "scopus" for item in payload["results"])
    assert any(item["source"] == "sciencedirect" for item in payload["results"])
