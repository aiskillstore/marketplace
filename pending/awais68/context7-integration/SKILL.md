---
name: context7-integration
description: |
  Use when integrating Context7 (knowledge/context store) for document ingestion,
  semantic search, or scoped context retrieval.
  Triggers for: uploading documents, searching knowledge base, filtering by role/tenant,
  or providing AI with document-grounded context.
  NOT for: general database queries, file storage without context semantics, or non-document content.
---

# Context7 Integration Skill

Expert integration of Context7 for document ingestion, semantic search, and role-scoped context retrieval in ERP applications.

## Quick Reference

| Task | Method/Endpoint |
|------|-----------------|
| Ingest document | `context7_client.ingest_document()` |
| Batch ingest | `context7_client.ingest_batch()` |
| Search context | `context7_client.search()` |
| Get document | `context7_client.get_document()` |
| Delete document | `context7_client.delete_document()` |

## Project Structure

```
backend/
├── app/
│   ├── services/
│   │   └── context7_client.py    # Core Context7 client
│   ├── api/
│   │   └── knowledge/
│   │       └── routes.py         # Knowledge API endpoints
│   └── schemas/
│       └── knowledge.py          # Pydantic schemas
frontend/
├── hooks/
│   └── useContext7Search.ts     # Search hook
└── components/
    └── knowledge/
        └── ContextSearch.tsx    # Search component
docs/
├── policies/                     # Source documents
├── faq/                          # FAQ documents
└── procedures/                   # Procedure documents
```

## Context7 Client

### Core Client Class

```python
# backend/app/services/context7_client.py
import os
from typing import Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class DocumentType(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    TEXT = "text"


class DocumentMetadata(BaseModel):
    """Metadata for context documents."""
    title: str
    description: Optional[str] = None
    # Role-based access
    allowed_roles: list[str] = []  # Empty = all roles
    # Organization scope
    school_id: Optional[str] = None
    # Content categorization
    module: str  # e.g., "fees", "attendance", "policies"
    category: Optional[str] = None  # e.g., "faq", "procedure", "policy"
    # Language
    language: str = "en"
    # Versioning
    version: str = "1.0"
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    # Source tracking
    source_file: Optional[str] = None
    source_url: Optional[str] = None


class ContextDocument(BaseModel):
    """Document in Context7."""
    id: str
    content: str
    metadata: DocumentMetadata
    chunk_id: Optional[str] = None
    similarity_score: Optional[float] = None


class Context7Client:
    """Client for Context7 knowledge store."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_namespace: str = "default",
    ):
        self.api_key = api_key or os.getenv("CONTEXT7_API_KEY")
        self.base_url = base_url or os.getenv("CONTEXT7_API_URL", "https://api.context7.com")
        self.default_namespace = default_namespace
        self._session = None

    def _get_session(self):
        """Get or create requests session."""
        if not self._session:
            import requests
            self._session = requests.Session()
            if self.api_key:
                self._session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        return self._session

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> dict:
        """Make API request to Context7."""
        session = self._get_session()
        response = session.request(
            method,
            f"{self.base_url}{endpoint}",
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    # === INGESTION ===

    def ingest_document(
        self,
        content: str,
        metadata: DocumentMetadata,
        namespace: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> dict:
        """
        Ingest a single document into Context7.

        Args:
            content: Document content (markdown, HTML, or text)
            metadata: Document metadata with tags and access control
            namespace: Optional namespace (defaults to default_namespace)
            document_id: Optional document ID for idempotent updates

        Returns:
            Ingestion result with document ID
        """
        payload = {
            "content": content,
            "metadata": metadata.model_dump(),
            "document_id": document_id,
            "namespace": namespace or self.default_namespace,
        }

        return self._request("POST", "/v1/documents", json=payload)

    def ingest_batch(
        self,
        documents: list[tuple[str, DocumentMetadata]],
        namespace: Optional[str] = None,
        batch_size: int = 10,
    ) -> dict:
        """
        Ingest multiple documents in batches.

        Args:
            documents: List of (content, metadata) tuples
            namespace: Optional namespace
            batch_size: Number of documents per batch

        Returns:
            Batch ingestion result with success/failure counts
        """
        results = {"successful": 0, "failed": 0, "documents": []}
        namespace = namespace or self.default_namespace

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_payload = [
                {
                    "content": content,
                    "metadata": metadata.model_dump(),
                    "namespace": namespace,
                }
                for content, metadata in batch
            ]

            try:
                response = self._request(
                    "POST",
                    "/v1/documents/batch",
                    json={"documents": batch_payload}
                )
                results["successful"] += len(batch)
                results["documents"].extend(response.get("documents", []))
            except Exception as e:
                results["failed"] += len(batch)
                # Log failed batch for retry

        return results

    def ingest_from_file(
        self,
        file_path: str,
        metadata: DocumentMetadata,
        namespace: Optional[str] = None,
    ) -> dict:
        """
        Ingest a document from a file.

        Args:
            file_path: Path to file (markdown, PDF, or HTML)
            metadata: Document metadata
            namespace: Optional namespace

        Returns:
            Ingestion result
        """
        # Determine document type from extension
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".md":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            doc_type = DocumentType.MARKDOWN
        elif ext == ".pdf":
            content = self._extract_pdf_text(file_path)
            doc_type = DocumentType.PDF
        elif ext in [".html", ".htm"]:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = self._strip_html(content)
            doc_type = DocumentType.HTML
        else:
            # Default to text
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            doc_type = DocumentType.TEXT

        # Update metadata with source file
        metadata.source_file = file_path

        return self.ingest_document(content, metadata, namespace)

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join(page.extract_text() for page in reader.pages)
            return text
        except ImportError:
            raise ImportError("PyPDF2 required for PDF ingestion: pip install PyPDF2")

    def _strip_html(self, html: str) -> str:
        """Strip HTML tags from content."""
        import re
        clean = re.compile("<.*?>")
        return re.sub(clean, "", html)

    # === RETRIEVAL ===

    def search(
        self,
        query: str,
        namespace: Optional[str] = None,
        filters: Optional[dict] = None,
        max_chunks: int = 5,
        min_similarity: float = 0.7,
        user_role: Optional[str] = None,
        school_id: Optional[str] = None,
    ) -> list[ContextDocument]:
        """
        Search for relevant context documents.

        Args:
            query: Search query (semantic search)
            namespace: Namespace to search in
            filters: Additional metadata filters
            max_chunks: Maximum number of chunks to return
            min_similarity: Minimum similarity score threshold
            user_role: User's role for access control
            school_id: User's school ID for multi-tenancy

        Returns:
            List of relevant document chunks
        """
        # Build search payload with access control
        payload = {
            "query": query,
            "namespace": namespace or self.default_namespace,
            "max_chunks": max_chunks,
            "min_similarity": min_similarity,
            "filters": filters or {},
        }

        # Add role-based filtering
        if user_role:
            payload["filters"]["allowed_roles"] = [user_role, "all"]

        # Add tenant filtering
        if school_id:
            payload["filters"]["school_id"] = school_id

        response = self._request("POST", "/v1/search", json=payload)

        return [
            ContextDocument(
                id=doc.get("id"),
                content=doc.get("content", ""),
                metadata=DocumentMetadata(**doc.get("metadata", {})),
                chunk_id=doc.get("chunk_id"),
                similarity_score=doc.get("similarity_score"),
            )
            for doc in response.get("documents", [])
        ]

    def get_document(
        self,
        document_id: str,
        namespace: Optional[str] = None,
    ) -> Optional[ContextDocument]:
        """
        Get a specific document by ID.

        Args:
            document_id: Document ID
            namespace: Namespace

        Returns:
            Document or None if not found
        """
        try:
            response = self._request(
                "GET",
                f"/v1/documents/{document_id}",
                params={"namespace": namespace or self.default_namespace}
            )
            return ContextDocument(
                id=response.get("id"),
                content=response.get("content", ""),
                metadata=DocumentMetadata(**response.get("metadata", {})),
            )
        except Exception:
            return None

    def delete_document(
        self,
        document_id: str,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Delete a document from Context7.

        Args:
            document_id: Document ID
            namespace: Namespace

        Returns:
            True if deleted successfully
        """
        try:
            self._request(
                "DELETE",
                f"/v1/documents/{document_id}",
                params={"namespace": namespace or self.default_namespace}
            )
            return True
        except Exception:
            return False

    # === MANAGEMENT ===

    def list_documents(
        self,
        namespace: Optional[str] = None,
        module: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        List documents in a namespace.

        Args:
            namespace: Namespace to list
            module: Filter by module
            limit: Maximum number of results

        Returns:
            List of document summaries
        """
        params = {
            "namespace": namespace or self.default_namespace,
            "limit": limit,
        }
        if module:
            params["module"] = module

        response = self._request("GET", "/v1/documents", params=params)
        return response.get("documents", [])

    def get_stats(self, namespace: Optional[str] = None) -> dict:
        """Get statistics for a namespace."""
        response = self._request(
            "GET",
            "/v1/stats",
            params={"namespace": namespace or self.default_namespace}
        )
        return response


# Singleton instance
_context7_client: Optional[Context7Client] = None


def get_context7_client() -> Context7Client:
    """Get or create Context7 client singleton."""
    global _context7_client
    if _context7_client is None:
        _context7_client = Context7Client()
    return _context7_client
```

## Context Shaping Utilities

```python
# backend/app/services/context_shaper.py
from typing import list
from backend.app.services.context7_client import ContextDocument


class ContextShaper:
    """Shape and format retrieved context for AI prompts."""

    MAX_TOKENS = 4000  # Reserve space for prompt
    CHUNK_HEADER = "### Source: {title}"
    FOOTER = "\n\n---\n*Source: {source}*"

    def shape_for_prompt(
        self,
        documents: list[ContextDocument],
        query: str,
        max_chunks: int = 5,
        include_sources: bool = True,
    ) -> str:
        """
        Shape retrieved documents into prompt-safe format.

        Args:
            documents: Retrieved document chunks
            query: Original search query
            max_chunks: Maximum chunks to include
            include_sources: Include source citations

        Returns:
            Formatted context string
        """
        chunks = documents[:max_chunks]

        sections = []
        for i, doc in enumerate(chunks):
            header = f"## Chunk {i + 1}"
            if doc.metadata.title:
                header += f": {doc.metadata.title}"

            section = header
            section += f"\n\n{self._format_content(doc.content)}"

            if include_sources and doc.metadata.source_file:
                section += self.FOOTER.format(source=doc.metadata.source_file)

            sections.append(section)

        context = "\n\n".join(sections)

        # Ensure context fits in token limit
        context = self._truncate_to_token_limit(context, self.MAX_TOKENS)

        return context

    def _format_content(self, content: str) -> str:
        """Format content for readability."""
        # Normalize whitespace
        lines = content.split("\n")
        lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(lines)

    def _truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        # Rough estimate: 4 characters per token
        max_chars = max_tokens * 4

        if len(text) <= max_chars:
            return text

        # Truncate and add note
        truncated = text[:max_chars - 50]
        truncated = truncated.rsplit("\n", 1)[0]  # Don't cut mid-line
        truncated += "\n\n*... (context truncated for length)*"

        return truncated

    def format_for_chat(
        self,
        documents: list[ContextDocument],
        user_role: str,
    ) -> str:
        """
        Format context for chat widget display.

        Args:
            documents: Retrieved documents
            user_role: User's role for messaging

        Returns:
            User-friendly formatted context
        """
        if not documents:
            return "No relevant information found."

        formatted = []
        for doc in documents:
            if doc.metadata.title:
                formatted.append(f"**{doc.metadata.title}**")
            formatted.append(doc.content[:500])  # Limit per chunk
            formatted.append("")

        return "\n".join(formatted)


# Singleton
context_shaper = ContextShaper()
```

## API Routes

```python
# backend/app/api/knowledge/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from pydantic import BaseModel

from app.services.context7_client import (
    get_context7_client,
    DocumentMetadata,
    Context7Client,
)
from app.services.context_shaper import get_context_shaper, ContextShaper
from app.auth.jwt import get_current_user


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class IngestRequest(BaseModel):
    """Request to ingest a document."""
    content: str
    title: str
    description: Optional[str] = None
    module: str
    category: Optional[str] = None
    allowed_roles: list[str] = []
    school_id: Optional[str] = None


class SearchRequest(BaseModel):
    """Request to search knowledge base."""
    query: str
    module: Optional[str] = None
    max_chunks: int = 5
    min_similarity: float = 0.7


class SearchResponse(BaseModel):
    """Search response with shaped context."""
    documents: list[dict]
    context: str  # Shaped for prompt


@router.post("/ingest")
async def ingest_document(
    request: IngestRequest,
    current_user = Depends(get_current_user),
    client: Context7Client = Depends(get_context7_client),
) -> dict:
    """
    Ingest a document into the knowledge base.

    Requires admin or content-manager role.
    """
    # Check permissions
    if "admin" not in current_user.roles and "content-manager" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to ingest documents",
        )

    # Build metadata
    metadata = DocumentMetadata(
        title=request.title,
        description=request.description,
        allowed_roles=request.allowed_roles or ["all"],
        school_id=request.school_id or current_user.school_id,
        module=request.module,
        category=request.category,
    )

    # Ingest
    result = client.ingest_document(
        content=request.content,
        metadata=metadata,
    )

    return {"status": "ingested", "document_id": result.get("id")}


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    current_user = Depends(get_current_user),
    client: Context7Client = Depends(get_context7_client),
    shaper: ContextShaper = Depends(get_context_shaper),
) -> SearchResponse:
    """
    Search the knowledge base.

    Returns shaped context suitable for AI prompts.
    """
    # Search with role and tenant filtering
    documents = client.search(
        query=request.query,
        filters={"module": request.module} if request.module else {},
        max_chunks=request.max_chunks,
        min_similarity=request.min_similarity,
        user_role=current_user.role,
        school_id=current_user.school_id,
    )

    # Shape for prompt
    context = shaper.shape_for_prompt(
        documents=documents,
        query=request.query,
        max_chunks=request.max_chunks,
    )

    return SearchResponse(
        documents=[
            {
                "id": doc.id,
                "title": doc.metadata.title,
                "content": doc.content[:200],
                "similarity": doc.similarity_score,
            }
            for doc in documents
        ],
        context=context,
    )


@router.get("/modules")
async def list_modules(
    current_user = Depends(get_current_user),
    client: Context7Client = Depends(get_context7_client),
) -> dict:
    """List available knowledge modules."""
    documents = client.list_documents(
        limit=1000,
    )

    modules = set()
    for doc in documents:
        if doc.get("metadata", {}).get("school_id") in [None, current_user.school_id]:
            modules.add(doc.get("metadata", {}).get("module"))

    return {"modules": sorted(modules)}
```

## Frontend Hook

```typescript
// frontend/hooks/useContext7Search.ts
import { useState, useCallback } from "react";

interface SearchResult {
  id: string;
  title: string;
  content: string;
  similarity: number;
}

interface SearchOptions {
  module?: string;
  maxChunks?: number;
}

export function useContext7Search() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [context, setContext] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (
    query: string,
    options: SearchOptions = {}
  ) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/v1/knowledge/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          module: options.module,
          max_chunks: options.maxChunks || 5,
        }),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();

      setResults(data.documents);
      setContext(data.context);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setResults([]);
      setContext("");
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setResults([]);
    setContext("");
    setError(null);
  }, []);

  return {
    search,
    clear,
    results,
    context,
    loading,
    error,
  };
}
```

## Document Organization

```
docs/
├── policies/
│   ├── attendance-policy.md
│   ├── fee-refund-policy.md
│   └── grading-policy.md
├── procedures/
│   ├── student-registration.md
│   ├── fee-payment.md
│   └── transcript-request.md
├── faq/
│   ├── fees-faq.md
│   ├── attendance-faq.md
│   └── grades-faq.md
└── handbooks/
    ├── student-handbook.md
    └── parent-handbook.md
```

### Metadata Examples

```python
# Fee policy document
DocumentMetadata(
    title="Fee Refund Policy",
    description="Guidelines for fee refunds and cancellations",
    module="fees",
    category="policy",
    allowed_roles=["admin", "accountant", "parent", "student"],
    school_id="school_001",
    language="en",
    source_file="docs/policies/fee-refund-policy.md",
)

# Student FAQ
DocumentMetadata(
    title="Fee Payment FAQ",
    description="Common questions about fee payment",
    module="fees",
    category="faq",
    allowed_roles=["student", "parent"],
    school_id="school_001",
    language="en",
    source_file="docs/faq/fees-faq.md",
)

# Staff procedure
DocumentMetadata(
    title="Student Registration Procedure",
    description="Step-by-step guide for registering new students",
    module="registration",
    category="procedure",
    allowed_roles=["admin", "registrar"],
    school_id="school_001",
    language="en",
    source_file="docs/procedures/student-registration.md",
)
```

## Quality Checklist

- [ ] **No PII ingestion**: Sensitive documents reviewed before upload
- [ ] **Query bounds**: max_chunks, min_similarity prevent excessive results
- [ ] **Error handling**: Graceful fallback when context unavailable
- [ ] **Source attribution**: Clear indication when answers are document-based
- [ ] **Multi-tenancy**: school_id filtering prevents cross-tenant access
- [ ] **Role filtering**: allowed_roles field controls access
- [ ] **Token limits**: Context truncation prevents prompt overflow

## Integration Points

| Skill | Integration |
|-------|-------------|
| `@jwt-auth` | Extract role and school_id from JWT for access control |
| `@api-client` | API calls for ingest/search endpoints |
| `@chatkit-widget` | Provide context for AI-powered chat |
| `@fastapi-app` | Register knowledge API routes |
| `@error-handling` | Handle context retrieval errors gracefully |

## Multi-Tenancy

```python
# Per-school namespace isolation
class Context7Client:
    # ...

    def search(self, query: str, school_id: str, **kwargs) -> list[ContextDocument]:
        # Always filter by school_id
        return super().search(
            query,
            school_id=school_id,
            filters={"school_id": school_id},
            **kwargs
        )

    def ingest_document(
        self,
        content: str,
        metadata: DocumentMetadata,
        school_id: str,
        **kwargs
    ) -> dict:
        # Always set school_id on metadata
        metadata.school_id = school_id
        return super().ingest_document(content, metadata, **kwargs)
```

## Batch Ingestion Script

```python
# scripts/ingest_docs.py
#!/usr/bin/env python3
"""Batch ingest documentation into Context7."""
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.context7_client import Context7Client, DocumentMetadata


def ingest_directory(
    dir_path: str,
    module: str,
    category: str,
    school_id: str,
    allowed_roles: list[str],
):
    """Ingest all documents in a directory."""
    client = Context7Client()
    dir_path = Path(dir_path)

    for file_path in dir_path.rglob("*.md"):
        print(f"Ingesting: {file_path}")

        metadata = DocumentMetadata(
            title=file_path.stem.replace("-", " ").title(),
            module=module,
            category=category,
            school_id=school_id,
            allowed_roles=allowed_roles,
            source_file=str(file_path),
        )

        try:
            client.ingest_from_file(str(file_path), metadata)
            print(f"  ✓ Ingested")
        except Exception as e:
            print(f"  ✗ Failed: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch ingest documents")
    parser.add_argument("--dir", required=True, help="Directory to ingest")
    parser.add_argument("--module", required=True, help="Document module")
    parser.add_argument("--category", required=True, help="Document category")
    parser.add_argument("--school-id", required=True, help="School ID")
    parser.add_argument("--roles", default="all", help="Comma-separated allowed roles")

    args = parser.parse_args()

    ingest_directory(
        args.dir,
        args.module,
        args.category,
        args.school_id,
        args.roles.split(","),
    )
```

## Error Handling

```python
# backend/app/services/context7_client.py

class Context7Error(Exception):
    """Base exception for Context7 errors."""
    pass


class Context7SearchError(Context7Error):
    """Error during context search."""
    pass


class Context7IngestError(Context7Error):
    """Error during document ingestion."""
    pass


# Usage in search
def search(self, *args, **kwargs) -> list[ContextDocument]:
    try:
        return self._search_impl(*args, **kwargs)
    except Exception as e:
        raise Context7SearchError(f"Search failed: {e}") from e


# Frontend fallback
function useContext7Search() {
  const { search, results, loading, error } = useContext7Search();

  // Fallback to general response if context fails
  const handleSearch = async (query: string) => {
    try {
      await search(query);
    } catch {
      // Use generic response
      setResults([]);
      setContext("");
    }
  };

  return { search: handleSearch, results, loading, error };
}
```
