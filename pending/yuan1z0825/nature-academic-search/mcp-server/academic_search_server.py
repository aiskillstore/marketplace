"""Academic search MCP server.

Unified entry point exposing multi-source search and source-specific tools for
CrossRef, PubMed, arXiv, Scopus, and ScienceDirect.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from mcp.server import FastMCP

from sources import (
    ArxivSource,
    CrossRefSource,
    PubMedSource,
    ScienceDirectSource,
    ScopusSource,
)
from utils import AcademicSearchError, DataSourceError, setup_logging

mcp = FastMCP("academic-search")
logger = setup_logging()

# Singleton source instances (shared across tool calls)
_crossref = CrossRefSource()
_pubmed = PubMedSource()
_arxiv = ArxivSource()
_scopus = ScopusSource()
_sciencedirect = ScienceDirectSource()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_id_type(id: str) -> str:
    """Auto-detect identifier type.

    Returns one of: "doi", "pmid", "arxiv".
    Raises ValueError when detection fails.
    """
    id = id.strip()
    if id.startswith("10.") and "/" in id:
        return "doi"
    if re.match(r"^\d{7,8}$", id):
        return "pmid"
    if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", id):
        return "arxiv"
    raise ValueError(f"Cannot detect ID type for: {id}")


def _resolve_id_type(id: str, id_type: str) -> str:
    """Resolve the effective ID type.

    If id_type is "auto", delegate to _detect_id_type.
    Otherwise normalise the explicit type string.
    """
    if id_type == "auto":
        return _detect_id_type(id)
    normalised = id_type.lower().strip()
    if normalised in ("doi", "pmid", "arxiv"):
        return normalised
    raise ValueError(f"Unsupported id_type: {id_type}")


def _json_ok(data: Any) -> str:
    """Serialize a successful result to JSON string."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def _json_error(message: str, source: str | None = None) -> str:
    """Serialize an error result to JSON string."""
    payload: dict[str, Any] = {"error": message}
    if source:
        payload["source"] = source
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Async wrappers for synchronous sources
# ---------------------------------------------------------------------------

async def _search_crossref(query: str, rows: int, filter_type: str | None) -> dict:
    return await asyncio.to_thread(_crossref.search, query, rows, filter_type)


async def _search_pubmed(query: str, rows: int) -> dict:
    return await asyncio.to_thread(_pubmed.search, query, rows)


async def _search_arxiv(query: str, rows: int) -> dict:
    return await asyncio.to_thread(_arxiv.search, query, rows)


async def _search_scopus(query: str, rows: int) -> dict:
    return await asyncio.to_thread(_scopus.search, query, rows)


async def _search_sciencedirect(query: str, rows: int) -> dict:
    return await asyncio.to_thread(_sciencedirect.search, query, rows)


async def _search_all(
    query: str,
    sources: list[str],
    rows: int,
    filter_type: str | None,
) -> dict:
    """Dispatch concurrent searches and merge results."""
    tasks: list[asyncio.Task] = []
    source_order: list[str] = []

    if "crossref" in sources:
        tasks.append(asyncio.create_task(_search_crossref(query, rows, filter_type)))
        source_order.append("crossref")
    if "pubmed" in sources:
        tasks.append(asyncio.create_task(_search_pubmed(query, rows)))
        source_order.append("pubmed")
    if "arxiv" in sources:
        tasks.append(asyncio.create_task(_search_arxiv(query, rows)))
        source_order.append("arxiv")
    if "scopus" in sources:
        tasks.append(asyncio.create_task(_search_scopus(query, rows)))
        source_order.append("scopus")
    if "sciencedirect" in sources:
        tasks.append(asyncio.create_task(_search_sciencedirect(query, rows)))
        source_order.append("sciencedirect")

    if not tasks:
        return {"total": 0, "results": [], "errors": []}

    outcomes = await asyncio.gather(*tasks, return_exceptions=True)

    merged_results: list[dict] = []
    errors: list[dict] = []
    total = 0

    for src, outcome in zip(source_order, outcomes):
        if isinstance(outcome, BaseException):
            logger.error("Source %s failed: %s", src, outcome)
            errors.append({"source": src, "error": str(outcome)})
            continue
        total += outcome.get("total", 0)
        merged_results.extend(outcome.get("results", []))

    return {
        "total": total,
        "sources_queried": source_order,
        "result_count": len(merged_results),
        "results": merged_results,
        "errors": errors if errors else None,
    }


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def search_papers(
    query: str,
    sources: list[str] | None = None,
    rows: int = 5,
    type: str | None = None,
) -> str:
    """Search academic papers across multiple sources.

    Args:
        query: Search keywords or query string.
        sources: List of source names to query. Defaults to CrossRef, PubMed,
            and arXiv. Add "scopus" and/or "sciencedirect" explicitly to use
            Elsevier-backed providers; they require local pybliometrics config
            and may consume Elsevier API quota.
        rows: Number of results per source (max 50), not total result count.
        type: Optional CrossRef-only work type filter (e.g. "journal-article").

    Returns:
        JSON string with total count, merged results, and any per-source errors.
    """
    if not query or not query.strip():
        return _json_error("Empty search query")

    if sources is None:
        sources = ["crossref", "pubmed", "arxiv"]

    # Validate source names
    valid_sources = {"crossref", "pubmed", "arxiv", "scopus", "sciencedirect"}
    invalid = [s for s in sources if s not in valid_sources]
    if invalid:
        return _json_error(f"Invalid sources: {invalid}. Valid: {sorted(valid_sources)}")

    rows = max(1, min(rows, 50))

    logger.info("search_papers called", extra={
        "tool": "search_papers",
        "query": query,
        "sources": sources,
        "rows": rows,
    })

    try:
        result = await _search_all(query, sources, rows, type)
    except Exception as exc:
        logger.exception("search_papers failed")
        return _json_error(f"Search failed: {exc}")

    return _json_ok(result)


@mcp.tool()
def search_scopus(
    query: str,
    rows: int = 5,
    view: str | None = None,
    subscriber: bool = True,
) -> str:
    """Search Scopus documents using a Scopus advanced-search query.

    Args:
        query: Scopus advanced search query.
        rows: Number of normalized results to return (max 50).
        view: Optional Scopus view ("STANDARD" or "COMPLETE").
        subscriber: Whether to use subscriber cursor navigation.
    """
    try:
        return _json_ok(_scopus.search(query, rows, view=view, subscriber=subscriber))
    except DataSourceError as exc:
        logger.error("search_scopus failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("search_scopus failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def get_scopus_abstract(
    identifier: str,
    id_type: str | None = None,
    view: str = "META_ABS",
) -> str:
    """Retrieve Scopus abstract metadata.

    Args:
        identifier: EID, Scopus ID, DOI, PMID, or PII.
        id_type: Optional pybliometrics ID type; auto-detected when omitted.
        view: Scopus abstract view, usually "META_ABS".
    """
    try:
        return _json_ok(_scopus.get_abstract(identifier, id_type=id_type, view=view))
    except DataSourceError as exc:
        logger.error("get_scopus_abstract failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_scopus_abstract failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def get_scopus_citation_overview(
    identifiers: list[str],
    id_type: str = "scopus_id",
    date: str | None = None,
    citation: str | None = None,
) -> str:
    """Retrieve Scopus citation overview for one or more documents.

    Args:
        identifiers: Document identifiers.
        id_type: Identifier type, e.g. "scopus_id", "doi", or "eid".
        date: Optional year range such as "2020-2025".
        citation: Optional exclusion mode, e.g. "exclude-self".
    """
    try:
        result = _scopus.get_citation_overview(
            identifiers,
            id_type=id_type,
            date=date,
            citation=citation,
        )
        return _json_ok(result)
    except DataSourceError as exc:
        logger.error("get_scopus_citation_overview failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_scopus_citation_overview failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def search_scopus_authors(query: str, rows: int = 5) -> str:
    """Search Scopus author profiles."""
    try:
        return _json_ok(_scopus.search_authors(query, rows))
    except DataSourceError as exc:
        logger.error("search_scopus_authors failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("search_scopus_authors failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def get_scopus_author(author_id: str, view: str = "ENHANCED") -> str:
    """Retrieve a Scopus author profile by author ID."""
    try:
        return _json_ok(_scopus.get_author(author_id, view=view))
    except DataSourceError as exc:
        logger.error("get_scopus_author failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_scopus_author failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def search_scopus_affiliations(query: str, rows: int = 5) -> str:
    """Search Scopus affiliations."""
    try:
        return _json_ok(_scopus.search_affiliations(query, rows))
    except DataSourceError as exc:
        logger.error("search_scopus_affiliations failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("search_scopus_affiliations failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def get_scopus_affiliation(affiliation_id: str, view: str = "STANDARD") -> str:
    """Retrieve a Scopus affiliation by affiliation ID."""
    try:
        return _json_ok(_scopus.get_affiliation(affiliation_id, view=view))
    except DataSourceError as exc:
        logger.error("get_scopus_affiliation failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_scopus_affiliation failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def search_scopus_serial_titles(
    title: str | None = None,
    issn: str | None = None,
    publisher: str | None = None,
    subject: str | None = None,
    subject_code: str | None = None,
    content: str | None = None,
    open_access: str | None = None,
    rows: int = 5,
    view: str = "ENHANCED",
) -> str:
    """Search Scopus serial titles.

    Args:
        title: Serial title query.
        issn: ISSN query.
        publisher: Publisher query.
        subject: Subject-area query.
        subject_code: Subject-area code query.
        content: Content type query.
        open_access: Open-access filter.
        rows: Number of results to return.
        view: Scopus serial title view.
    """
    query = {
        "title": title,
        "issn": issn,
        "pub": publisher,
        "subj": subject,
        "subjCode": subject_code,
        "content": content,
        "oa": open_access,
    }
    try:
        return _json_ok(_scopus.search_serial_titles(query, rows=rows, view=view))
    except DataSourceError as exc:
        logger.error("search_scopus_serial_titles failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("search_scopus_serial_titles failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def get_scopus_serial_title(
    issn: str,
    view: str = "ENHANCED",
    years: str | None = None,
) -> str:
    """Retrieve a Scopus serial title by ISSN."""
    try:
        return _json_ok(_scopus.get_serial_title(issn, view=view, years=years))
    except DataSourceError as exc:
        logger.error("get_scopus_serial_title failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_scopus_serial_title failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def get_scopus_plumx_metrics(identifier: str, id_type: str) -> str:
    """Retrieve PlumX metrics for a document identifier."""
    try:
        return _json_ok(_scopus.get_plumx_metrics(identifier, id_type))
    except DataSourceError as exc:
        logger.error("get_scopus_plumx_metrics failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_scopus_plumx_metrics failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def search_sciencedirect(
    query: str,
    rows: int = 5,
    view: str | None = None,
) -> str:
    """Search ScienceDirect article metadata."""
    try:
        return _json_ok(_sciencedirect.search(query, rows=rows, view=view))
    except DataSourceError as exc:
        logger.error("search_sciencedirect failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("search_sciencedirect failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def get_sciencedirect_article_metadata(
    query: str,
    rows: int = 5,
    view: str | None = None,
) -> str:
    """Retrieve ScienceDirect article metadata with a metadata API query."""
    try:
        result = _sciencedirect.get_article_metadata(query, rows=rows, view=view)
        return _json_ok(result)
    except DataSourceError as exc:
        logger.error("get_sciencedirect_article_metadata failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_sciencedirect_article_metadata failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


@mcp.tool()
def get_paper_by_id(id: str, id_type: str = "auto") -> str:
    """Get paper details by identifier (DOI, PMID, or arXiv ID).

    Args:
        id: Paper identifier. Auto-detected if id_type is "auto":
            - Starts with "10." -> DOI (CrossRef)
            - 7-8 digit number -> PMID (PubMed)
            - YYMM.NNNNN format -> arXiv ID (arXiv)
        id_type: Force identifier type ("doi", "pmid", "arxiv", or "auto").

    Returns:
        JSON string with detailed paper metadata.
    """
    if not id or not id.strip():
        return _json_error("Empty identifier")

    try:
        resolved_type = _resolve_id_type(id, id_type)
    except ValueError as exc:
        return _json_error(str(exc))

    logger.info("get_paper_by_id called", extra={
        "tool": "get_paper_by_id",
        "id": id,
        "id_type": resolved_type,
    })

    try:
        if resolved_type == "doi":
            result = _crossref.get_by_doi(id.strip())
        elif resolved_type == "pmid":
            result = _pubmed.get_by_pmid(id.strip())
        elif resolved_type == "arxiv":
            result = _arxiv.get_by_id(id.strip())
        else:
            return _json_error(f"Unsupported ID type: {resolved_type}")
    except DataSourceError as exc:
        logger.error("get_paper_by_id failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_paper_by_id failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")

    return _json_ok(result)


@mcp.tool()
def get_citation(id: str, id_type: str = "auto", style: str = "apa") -> str:
    """Get formatted citation for a paper.

    Uses CrossRef content negotiation for DOI-based citations.
    For PMID/arXiv IDs, fetches metadata first then generates a basic citation.

    Args:
        id: Paper identifier (DOI, PMID, or arXiv ID).
        id_type: Force identifier type ("doi", "pmid", "arxiv", or "auto").
        style: Citation style. Supported: apa, nature, ieee, harvard,
               vancouver, chicago, mla.

    Returns:
        JSON string with the formatted citation.
    """
    if not id or not id.strip():
        return _json_error("Empty identifier")

    try:
        resolved_type = _resolve_id_type(id, id_type)
    except ValueError as exc:
        return _json_error(str(exc))

    logger.info("get_citation called", extra={
        "tool": "get_citation",
        "id": id,
        "id_type": resolved_type,
        "style": style,
    })

    try:
        if resolved_type == "doi":
            citation = _crossref.get_citation(id.strip(), style=style)
            return _json_ok({"id": id, "style": style, "citation": citation})

        # For non-DOI IDs, fetch metadata and build a basic citation
        if resolved_type == "pmid":
            paper = _pubmed.get_by_pmid(id.strip())
        elif resolved_type == "arxiv":
            paper = _arxiv.get_by_id(id.strip())
        else:
            return _json_error(f"Unsupported ID type: {resolved_type}")

        citation = _format_basic_citation(paper, style)
        return _json_ok({"id": id, "style": style, "citation": citation})

    except DataSourceError as exc:
        logger.error("get_citation failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("get_citation failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")


def _format_basic_citation(paper: dict, style: str) -> str:
    """Generate a basic citation string from unified paper metadata.

    This is a fallback for non-DOI papers where CrossRef content
    negotiation is not available.
    """
    authors = paper.get("authors", [])
    title = paper.get("title", "Untitled")
    year = paper.get("year", "n.d.")
    journal = paper.get("journal", "")
    doi = paper.get("doi", "")
    arxiv_id = paper.get("arxiv_id", "")
    pmid = paper.get("pmid", "")

    # Author formatting
    if len(authors) > 3:
        author_str = f"{authors[0]} et al."
    elif authors:
        author_str = ", ".join(authors)
    else:
        author_str = "Unknown"

    if style == "nature":
        parts = [f"{author_str}. {title}."]
        if journal:
            parts.append(f" *{journal}*.")
        if year:
            parts.append(f" ({year}).")
        if doi:
            parts.append(f" https://doi.org/{doi}")
        return "".join(parts)

    if style == "ieee":
        ref = f"{author_str}, \"{title}\""
        if journal:
            ref += f", *{journal}*"
        if year:
            ref += f", {year}"
        ref += "."
        if doi:
            ref += f" doi: {doi}."
        return ref

    # Default APA-like
    parts = [f"{author_str} ({year}). {title}."]
    if journal:
        parts.append(f" *{journal}*.")
    if doi:
        parts.append(f" https://doi.org/{doi}")
    elif arxiv_id:
        parts.append(f" arXiv:{arxiv_id}")
    elif pmid:
        parts.append(f" PMID:{pmid}")
    return "".join(parts)


@mcp.tool()
def lookup_mesh(term: str) -> str:
    """Lookup MeSH (Medical Subject Headings) terms.

    Queries the MeSH database via NCBI E-utilities to find matching
    descriptor names and unique IDs.

    Args:
        term: Search term to look up in the MeSH vocabulary.

    Returns:
        JSON string with matching MeSH descriptors.
    """
    if not term or not term.strip():
        return _json_error("Empty MeSH lookup term")

    logger.info("lookup_mesh called", extra={
        "tool": "lookup_mesh",
        "term": term,
    })

    try:
        result = _pubmed.lookup_mesh(term.strip())
    except DataSourceError as exc:
        logger.error("lookup_mesh failed: %s", exc)
        return _json_error(str(exc), source=exc.source)
    except Exception as exc:
        logger.exception("lookup_mesh failed unexpectedly")
        return _json_error(f"Unexpected error: {exc}")

    return _json_ok(result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
