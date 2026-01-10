#!/usr/bin/env python3
"""
Citation Management System
Tracks sources, generates citations, and maintains bibliography
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse
import hashlib


@dataclass
class Citation:
    """Represents a single citation"""
    id: str
    title: str
    url: str
    authors: Optional[List[str]] = None
    publication_date: Optional[str] = None
    retrieved_date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    source_type: str = "web"  # web, academic, documentation, book, paper
    doi: Optional[str] = None
    citation_count: int = 0

    def to_apa(self, index: int) -> str:
        """Generate APA format citation"""
        author_str = ""
        if self.authors:
            if len(self.authors) == 1:
                author_str = f"{self.authors[0]}."
            elif len(self.authors) == 2:
                author_str = f"{self.authors[0]} & {self.authors[1]}."
            else:
                author_str = f"{self.authors[0]} et al."

        date_str = f"({self.publication_date})" if self.publication_date else "(n.d.)"

        return f"[{index}] {author_str} {date_str}. {self.title}. Retrieved {self.retrieved_date}, from {self.url}"

    def to_inline(self, index: int) -> str:
        """Generate inline citation [index]"""
        return f"[{index}]"

    def to_markdown(self, index: int) -> str:
        """Generate markdown link format"""
        return f"[{index}] [{self.title}]({self.url}) (Retrieved: {self.retrieved_date})"


class CitationManager:
    """Manages citations and bibliography"""

    def __init__(self):
        self.citations: Dict[str, Citation] = {}
        self.citation_order: List[str] = []

    def add_source(
        self,
        url: str,
        title: str,
        authors: Optional[List[str]] = None,
        publication_date: Optional[str] = None,
        source_type: str = "web",
        doi: Optional[str] = None
    ) -> str:
        """Add a source and return its citation ID"""
        # Generate unique ID based on URL
        citation_id = hashlib.md5(url.encode()).hexdigest()[:8]

        if citation_id not in self.citations:
            citation = Citation(
                id=citation_id,
                title=title,
                url=url,
                authors=authors,
                publication_date=publication_date,
                source_type=source_type,
                doi=doi
            )
            self.citations[citation_id] = citation
            self.citation_order.append(citation_id)

        # Increment citation count
        self.citations[citation_id].citation_count += 1

        return citation_id

    def get_citation_number(self, citation_id: str) -> Optional[int]:
        """Get the citation number for a given ID"""
        try:
            return self.citation_order.index(citation_id) + 1
        except ValueError:
            return None

    def get_inline_citation(self, citation_id: str) -> str:
        """Get inline citation marker [n]"""
        num = self.get_citation_number(citation_id)
        return f"[{num}]" if num else "[?]"

    def generate_bibliography(self, style: str = "markdown") -> str:
        """Generate full bibliography"""
        if style == "markdown":
            lines = ["## Bibliography\n"]
            for i, citation_id in enumerate(self.citation_order, 1):
                citation = self.citations[citation_id]
                lines.append(citation.to_markdown(i))
            return "\n".join(lines)

        elif style == "apa":
            lines = ["## Bibliography\n"]
            for i, citation_id in enumerate(self.citation_order, 1):
                citation = self.citations[citation_id]
                lines.append(citation.to_apa(i))
            return "\n".join(lines)

        return "Unsupported citation style"

    def get_statistics(self) -> Dict[str, any]:
        """Get citation statistics"""
        return {
            'total_sources': len(self.citations),
            'total_citations': sum(c.citation_count for c in self.citations.values()),
            'source_types': self._count_by_type(),
            'most_cited': self._get_most_cited(5),
            'uncited': self._get_uncited()
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count sources by type"""
        counts = {}
        for citation in self.citations.values():
            counts[citation.source_type] = counts.get(citation.source_type, 0) + 1
        return counts

    def _get_most_cited(self, n: int = 5) -> List[tuple]:
        """Get most cited sources"""
        sorted_citations = sorted(
            self.citations.items(),
            key=lambda x: x[1].citation_count,
            reverse=True
        )
        return [(self.get_citation_number(cid), c.title, c.citation_count)
                for cid, c in sorted_citations[:n]]

    def _get_uncited(self) -> List[str]:
        """Get sources that were added but never cited"""
        return [c.title for c in self.citations.values() if c.citation_count == 0]

    def export_to_file(self, filepath: str, style: str = "markdown"):
        """Export bibliography to file"""
        with open(filepath, 'w') as f:
            f.write(self.generate_bibliography(style))


# Example usage
if __name__ == '__main__':
    manager = CitationManager()

    # Add sources
    id1 = manager.add_source(
        url="https://example.com/article1",
        title="Understanding Deep Research",
        authors=["Smith, J.", "Johnson, K."],
        publication_date="2025"
    )

    id2 = manager.add_source(
        url="https://example.com/article2",
        title="AI Research Methods",
        source_type="academic"
    )

    # Use citations
    print(f"Inline citation: {manager.get_inline_citation(id1)}")
    print(f"\nBibliography:\n{manager.generate_bibliography()}")
    print(f"\nStatistics:\n{manager.get_statistics()}")
