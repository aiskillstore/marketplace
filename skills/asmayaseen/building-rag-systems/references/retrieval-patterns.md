# RAG Retrieval Patterns

## Filter Architecture

```
Query Filter Strategy (all AND logic via must=[]):

┌─────────────────────────────────────────────────────────────────┐
│                       REQUIRED FILTERS                          │
├─────────────────────────────────────────────────────────────────┤
│  book_id         │ MatchValue   │ Tenant isolation              │
│  hardware_tier   │ Range(lte)   │ User's tier or lower          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       OPTIONAL FILTERS                          │
├─────────────────────────────────────────────────────────────────┤
│  module          │ MatchValue   │ Exact: ros2, gazebo, etc      │
│  chapter_min/max │ Range        │ Chapter range filter          │
│  lesson          │ MatchValue   │ Exact lesson number           │
│  proficiency     │ MatchAny     │ OR within: [A2, B1]           │
│  parent_doc_id   │ MatchValue   │ All chunks from specific doc  │
└─────────────────────────────────────────────────────────────────┘
```

## Search Query Model

```python
from typing import Literal, Optional
from pydantic import BaseModel, Field

ModuleName = Literal["ros2", "gazebo", "isaac", "vla"]
ProficiencyLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]

class SearchQuery(BaseModel):
    """User's search request with comprehensive filters."""

    text: str = Field(..., min_length=3)

    # Required: Book tenant
    book_id: str = Field(default="my-book")

    # Hardware personalization (Range filter: lte = "tier X or lower")
    hardware_tier: int = Field(default=1, ge=1, le=4)

    # Content location filters
    module: Optional[ModuleName] = None
    chapter_min: Optional[int] = Field(None, ge=0, le=20)
    chapter_max: Optional[int] = Field(None, ge=0, le=20)
    lesson: Optional[int] = Field(None, ge=0, le=15)

    # Pedagogical filters (OR logic within)
    proficiency_levels: Optional[list[ProficiencyLevel]] = None

    # Context expansion
    parent_doc_id: Optional[str] = None

    # Pagination
    limit: int = Field(default=5, ge=1, le=20)
```

## Search Response

```python
class SearchResult(BaseModel):
    """Single search result with metadata for context expansion."""

    # Content
    text: str
    score: float = Field(..., ge=0.0, le=1.0)

    # Location
    source_file: str
    section_title: Optional[str]
    module: str
    chapter: int
    lesson: int

    # Personalization context
    hardware_tier: int
    proficiency_level: str

    # Context expansion metadata
    chunk_index: int
    total_chunks: int
    parent_doc_id: Optional[str]
    prev_chunk_id: Optional[str]
    next_chunk_id: Optional[str]


class SearchResponse(BaseModel):
    """Complete search response."""

    query: str
    results: list[SearchResult]
    total_found: int
    hardware_tier_filter: int
    module_filter: Optional[str]
    book_id: str
```

## Comprehensive Filter Builder

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, Range

class RAGSearch:
    def build_filter(self, query: SearchQuery) -> Filter:
        """Build Qdrant filter with all conditions (AND logic)."""
        conditions = []

        # Required: Book filter (tenant isolation)
        conditions.append(FieldCondition(
            key="book_id",
            match=MatchValue(value=query.book_id),
        ))

        # Required: Hardware tier filter (tier X or lower)
        conditions.append(FieldCondition(
            key="hardware_tier",
            range=Range(lte=query.hardware_tier),
        ))

        # Optional: Module filter (exact match)
        if query.module:
            conditions.append(FieldCondition(
                key="module",
                match=MatchValue(value=query.module),
            ))

        # Optional: Chapter range filter
        if query.chapter_min is not None or query.chapter_max is not None:
            chapter_range = Range()
            if query.chapter_min is not None:
                chapter_range.gte = query.chapter_min
            if query.chapter_max is not None:
                chapter_range.lte = query.chapter_max
            conditions.append(FieldCondition(key="chapter", range=chapter_range))

        # Optional: Lesson filter (exact match)
        if query.lesson is not None:
            conditions.append(FieldCondition(
                key="lesson",
                match=MatchValue(value=query.lesson),
            ))

        # Optional: Proficiency levels (OR logic within)
        if query.proficiency_levels:
            conditions.append(FieldCondition(
                key="proficiency_level",
                match=MatchAny(any=query.proficiency_levels),
            ))

        # Optional: Parent document filter (context expansion)
        if query.parent_doc_id:
            conditions.append(FieldCondition(
                key="parent_doc_id",
                match=MatchValue(value=query.parent_doc_id),
            ))

        return Filter(must=conditions)

    def search(self, query: SearchQuery) -> SearchResponse:
        """Execute semantic search with filters."""
        query_vector = self.embedder.embed_single(query.text)
        query_filter = self.build_filter(query)

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=query.limit,
            with_payload=True,
        )

        return self._to_response(results, query)
```

## Direct Chunk Retrieval

```python
def get_chunk_by_id(self, chunk_id: str) -> Optional[SearchResult]:
    """Retrieve a specific chunk by its UUID for context expansion."""
    try:
        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[chunk_id],
            with_payload=True,
            with_vectors=False,
        )

        if not points:
            return None

        return self._point_to_result(points[0], score=1.0)
    except Exception:
        return None
```

## Context Expansion

```python
def expand_context(
    self,
    chunk_id: str,
    prev_count: int = 1,
    next_count: int = 1,
) -> list[SearchResult]:
    """
    Get a chunk and its neighboring chunks for context expansion.
    Walks the prev_chunk_id/next_chunk_id chain stored in payloads.

    Returns:
        List of chunks in order [prev..., current, next...]
    """
    current = self.get_chunk_by_id(chunk_id)
    if not current:
        return []

    # Walk backwards
    prev_chunks = []
    prev_id = current.prev_chunk_id
    for _ in range(prev_count):
        if not prev_id:
            break
        prev_chunk = self.get_chunk_by_id(prev_id)
        if not prev_chunk:
            break
        prev_chunks.insert(0, prev_chunk)  # Prepend to maintain order
        prev_id = prev_chunk.prev_chunk_id

    # Walk forwards
    next_chunks = []
    next_id = current.next_chunk_id
    for _ in range(next_count):
        if not next_id:
            break
        next_chunk = self.get_chunk_by_id(next_id)
        if not next_chunk:
            break
        next_chunks.append(next_chunk)
        next_id = next_chunk.next_chunk_id

    return prev_chunks + [current] + next_chunks
```

## Full Document Retrieval

```python
def get_document_chunks(
    self,
    parent_doc_id: str,
    book_id: str,
) -> list[SearchResult]:
    """
    Get all chunks for a document, ordered by chunk_index.
    Useful for showing full document context.
    """
    results, _ = self.client.scroll(
        collection_name=self.collection_name,
        scroll_filter=Filter(must=[
            FieldCondition(key="book_id", match=MatchValue(value=book_id)),
            FieldCondition(key="parent_doc_id", match=MatchValue(value=parent_doc_id)),
        ]),
        limit=100,
        with_payload=True,
        with_vectors=False,
    )

    chunks = [self._point_to_result(p, score=1.0) for p in results]
    chunks.sort(key=lambda c: c.chunk_index)
    return chunks
```

## FastAPI Endpoints

```python
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

search_client: Optional[RAGSearch] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize search client on startup."""
    global search_client
    search_client = RAGSearch()
    yield
    search_client = None

app = FastAPI(lifespan=lifespan)

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Semantic search with comprehensive Qdrant filters."""
    if search_client is None:
        raise HTTPException(status_code=503, detail="Search not initialized")

    query = SearchQuery(
        text=request.query,
        book_id=request.book_id,
        hardware_tier=request.hardware_tier,
        module=request.module,
        chapter_min=request.chapter_min,
        chapter_max=request.chapter_max,
        lesson=request.lesson,
        proficiency_levels=request.proficiency_levels,
        parent_doc_id=request.parent_doc_id,
        limit=request.limit,
    )

    return search_client.search(query)


@app.get("/context/{chunk_id}")
async def get_context(chunk_id: str, prev: int = 1, next: int = 1):
    """Get a chunk with surrounding context via chain walking."""
    chunks = search_client.expand_context(chunk_id, prev_count=prev, next_count=next)
    if not chunks:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"chunks": [c.model_dump() for c in chunks]}


@app.get("/document/{parent_doc_id}")
async def get_document(parent_doc_id: str, book_id: str = "my-book"):
    """Get all chunks for a document, ordered."""
    chunks = search_client.get_document_chunks(parent_doc_id, book_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "parent_doc_id": parent_doc_id,
        "total_chunks": len(chunks),
        "chunks": [c.model_dump() for c in chunks],
    }
```

## Filter Type Reference

| Filter Field | Qdrant Type | Use Case |
|-------------|-------------|----------|
| `book_id` | MatchValue | Tenant isolation (exact) |
| `hardware_tier` | Range(lte) | Personalization (tier X or lower) |
| `module` | MatchValue | Content location (exact) |
| `chapter` | Range(gte/lte) | Content location (range) |
| `lesson` | MatchValue | Content location (exact) |
| `proficiency_level` | MatchAny | Pedagogical (OR within) |
| `parent_doc_id` | MatchValue | Context expansion (exact) |

## Success Metrics

- **Query latency**: < 100ms for filtered search
- **Relevance**: Top-3 results contain answer 80%+ of time
- **Context expansion**: Successfully walk chunk chains
- **Filter accuracy**: 100% compliance with tier constraints