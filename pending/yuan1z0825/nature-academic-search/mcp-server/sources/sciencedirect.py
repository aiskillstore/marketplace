"""ScienceDirect data source via pybliometrics."""

from __future__ import annotations

from typing import Any

from pybliometrics.utils import URLS, get_content

from utils.errors import DataSourceError

from .elsevier_common import ensure_pybliometrics_config, year_from_date


SOURCE_NAME = "sciencedirect"


class ScienceDirectSource:
    """pybliometrics-backed ScienceDirect metadata operations."""

    SOURCE_NAME = SOURCE_NAME

    def search(
        self,
        query: str,
        rows: int = 5,
        view: str | None = None,
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Search ScienceDirect article metadata and return the requested page."""
        if not query or not query.strip():
            raise DataSourceError(SOURCE_NAME, "Empty search query")

        rows = max(1, min(rows, 50))

        def run() -> dict[str, Any]:
            data = self._search_api(
                "ScienceDirectSearch",
                {
                    "query": query.strip(),
                    "count": rows,
                    "start": 0,
                    "view": view or "STANDARD",
                },
            )
            records = _search_entries(data)
            return {
                "total": _total_results(data),
                "query": query,
                "source": SOURCE_NAME,
                "results": [self._normalize_search_entry(r) for r in records[:rows]],
            }

        return self._run("ScienceDirect search", run)

    def get_article_metadata(
        self,
        query: str,
        rows: int = 5,
        view: str | None = None,
        refresh: bool | int = False,
    ) -> dict[str, Any]:
        """Retrieve ScienceDirect article metadata using a metadata API query."""
        if not query or not query.strip():
            raise DataSourceError(SOURCE_NAME, "Empty article metadata query")

        rows = max(1, min(rows, 50))

        def run() -> dict[str, Any]:
            data = self._search_api(
                "ArticleMetadata",
                {
                    "query": query.strip(),
                    "count": rows,
                    "start": 0,
                    "view": view or "STANDARD",
                },
            )
            records = _search_entries(data)
            return {
                "total": _total_results(data),
                "query": query,
                "source": SOURCE_NAME,
                "results": [self._normalize_metadata_entry(r) for r in records[:rows]],
            }

        return self._run("ScienceDirect article metadata retrieval", run)

    def _run(self, operation: str, callback):
        ensure_pybliometrics_config(SOURCE_NAME)
        try:
            return callback()
        except DataSourceError:
            raise
        except Exception as exc:
            raise DataSourceError(
                SOURCE_NAME,
                f"{operation} failed: {exc}",
                original_error=exc,
            ) from exc

    @staticmethod
    def _search_api(api: str, params: dict[str, Any]) -> dict[str, Any]:
        response = get_content(URLS[api], api, params=params)
        return response.json()

    @staticmethod
    def _normalize_search_entry(data: dict[str, Any]) -> dict[str, Any]:
        links = _links(data.get("link"))
        return {
            "title": data.get("dc:title"),
            "authors": _authors(data),
            "year": year_from_date(data.get("prism:coverDate")),
            "doi": _doi(data),
            "pii": data.get("pii"),
            "journal": data.get("prism:publicationName"),
            "volume": data.get("prism:volume"),
            "pages": _join_pages(data.get("prism:startingPage"), data.get("prism:endingPage")),
            "openaccess_status": data.get("openaccess"),
            "link": links.get("scidir"),
            "api_link": links.get("self") or data.get("prism:url"),
            "source": SOURCE_NAME,
        }

    @staticmethod
    def _normalize_metadata_entry(data: dict[str, Any]) -> dict[str, Any]:
        links = _links(data.get("link"))
        return {
            "title": data.get("dc:title"),
            "authors": _authors(data),
            "year": year_from_date(data.get("prism:coverDate")),
            "doi": _doi(data),
            "eid": data.get("eid"),
            "pii": data.get("pii"),
            "abstract": data.get("dc:description"),
            "journal": data.get("prism:publicationName"),
            "pages": _join_pages(data.get("prism:startingPage"), data.get("prism:endingPage")),
            "aggregation_type": data.get("prism:aggregationType"),
            "publication_type": data.get("prism:publicationType"),
            "author_keywords": data.get("authkeywords"),
            "openaccess_status": data.get("openaccess"),
            "link": links.get("scidir") or links.get("self"),
            "api_link": links.get("self") or data.get("prism:url"),
            "source": SOURCE_NAME,
        }


def _search_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    entries = data.get("search-results", {}).get("entry", [])
    return [
        entry
        for entry in _as_list(entries)
        if isinstance(entry, dict)
        and (entry.get("dc:title") or entry.get("prism:doi") or entry.get("pii"))
    ]


def _total_results(data: dict[str, Any]) -> int:
    total = data.get("search-results", {}).get("opensearch:totalResults", 0)
    return _int_or_none(total) or 0


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _authors(data: dict[str, Any]) -> list[str]:
    authors = []
    author_data = data.get("authors", {}).get("author", [])
    for item in _as_list(author_data):
        name = item.get("$") if isinstance(item, dict) else item
        if name:
            authors.append(name)
    creator = data.get("dc:creator")
    if isinstance(creator, list):
        authors.extend(item.get("$") for item in creator if isinstance(item, dict))
    elif isinstance(creator, str) and not authors:
        authors.append(creator)
    return [a for a in authors if a]


def _links(value: Any) -> dict[str, str]:
    out = {}
    for item in _as_list(value):
        if not isinstance(item, dict):
            continue
        ref = item.get("@ref") or item.get("rel")
        href = item.get("@href") or item.get("href")
        if ref and href:
            out[ref] = href
    return out


def _doi(data: dict[str, Any]) -> str | None:
    if data.get("prism:doi"):
        return data["prism:doi"]
    identifier = data.get("dc:identifier")
    if isinstance(identifier, str) and identifier.startswith("doi:"):
        return identifier[4:]
    return None


def _join_pages(start: str | None, end: str | None) -> str:
    if start and end:
        return f"{start}-{end}"
    return start or end or ""


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
