"""MCP dispatch tests for academic_search_server tools."""

from __future__ import annotations

import asyncio
import json


def _call_tool_json(tool_name: str, arguments: dict) -> dict:
    from academic_search_server import mcp

    content, _metadata = asyncio.run(mcp.call_tool(tool_name, arguments))
    return json.loads(content[0].text)


def test_search_papers_mcp_dispatch_uses_default_sources(monkeypatch):
    import academic_search_server

    captured = {}

    async def fake_search_all(query, sources, rows, filter_type):
        captured.update({
            "query": query,
            "sources": list(sources),
            "rows": rows,
            "filter_type": filter_type,
        })
        return {
            "total": 0,
            "sources_queried": list(sources),
            "result_count": 0,
            "results": [],
            "errors": None,
        }

    monkeypatch.setattr(academic_search_server, "_search_all", fake_search_all)

    payload = _call_tool_json("search_papers", {"query": "graphene", "rows": 100})

    assert payload["sources_queried"] == ["crossref", "pubmed", "arxiv"]
    assert "error" not in payload
    assert captured == {
        "query": "graphene",
        "sources": ["crossref", "pubmed", "arxiv"],
        "rows": 50,
        "filter_type": None,
    }


def test_search_papers_mcp_dispatch_accepts_elsevier_sources(monkeypatch):
    import academic_search_server

    captured = {}

    async def fake_search_all(query, sources, rows, filter_type):
        captured.update({
            "query": query,
            "sources": list(sources),
            "rows": rows,
            "filter_type": filter_type,
        })
        return {
            "total": 2,
            "sources_queried": list(sources),
            "result_count": 2,
            "results": [
                {"source": "scopus", "title": "Scopus result"},
                {"source": "sciencedirect", "title": "ScienceDirect result"},
            ],
            "errors": None,
        }

    monkeypatch.setattr(academic_search_server, "_search_all", fake_search_all)

    payload = _call_tool_json(
        "search_papers",
        {
            "query": "bridge scour",
            "sources": ["scopus", "sciencedirect"],
            "rows": 1,
            "type": "journal-article",
        },
    )

    assert payload["sources_queried"] == ["scopus", "sciencedirect"]
    assert {item["source"] for item in payload["results"]} == {
        "scopus",
        "sciencedirect",
    }
    assert captured == {
        "query": "bridge scour",
        "sources": ["scopus", "sciencedirect"],
        "rows": 1,
        "filter_type": "journal-article",
    }
