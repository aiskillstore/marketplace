"""Data source modules for academic search."""

from .crossref import CrossRefSource
from .pubmed import PubMedSource
from .arxiv import ArxivSource
from .scopus import ScopusSource
from .sciencedirect import ScienceDirectSource

__all__ = [
    "CrossRefSource",
    "PubMedSource",
    "ArxivSource",
    "ScopusSource",
    "ScienceDirectSource",
]
