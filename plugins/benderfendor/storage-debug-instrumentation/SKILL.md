---
name: storage-debug-instrumentation
description: Add comprehensive debugging and observability tooling for backend storage layers (PostgreSQL, ChromaDB) and startup metrics. Includes storage drift detection, raw data inspection endpoints, and a Next.js admin dashboard.
---

# Storage Debug Instrumentation

## Purpose
Enable rapid diagnosis of storage state, synchronization health, and backend performance bottlenecks by exposing:
- Raw article inspection from both PostgreSQL and ChromaDB
- Storage drift detection (missing/dangling entries)
- Detailed startup timeline breakdown (DB init, cache preload, vector store, RSS refresh)
- One-page debug dashboard consolidating all diagnostics

## Scope
- Backend: `app/services/startup_metrics.py`, `app/main.py`, `app/vector_store.py`, `app/database.py`, `app/api/routes/debug.py`
- Frontend: `frontend/lib/api.ts`, `frontend/app/debug/page.tsx`
- No schema changes; purely additive instrumentation and debug routes

## Workflow

### 1. Create startup metrics service
**File:** `backend/app/services/startup_metrics.py`
- Implement thread-safe `StartupMetrics` class to record phase timings
- Expose `record_event(name, started_at, detail, metadata)` for phase capture
- Support `add_note(key, value)` for arbitrary annotations
- Export singleton `startup_metrics` for app-wide use

### 2. Instrument vector store initialization
**File:** `backend/app/vector_store.py`
- Import `startup_metrics`
- In `VectorStore.__init__()`, wrap initialization with `time.time()` timer
- Record event with metadata: `host`, `port`, `collection`, `documents`
- Catch connection errors and annotate them

### 3. Instrument FastAPI startup sequence
**File:** `backend/app/main.py`
- Call `startup_metrics.mark_app_started()` at beginning of `on_startup()`
- Wrap each phase (DB init, schedulers, cache preload, RSS refresh, migration) with `record_event()`
- Include metadata: `cache_size`, `article_count`, `oldest_article_hours`
- Call `startup_metrics.mark_app_completed()` at end
- Add app version notes via `add_note()`

### 4. Add database pagination helpers
**File:** `backend/app/database.py`
- Implement `fetch_articles_page()` to support:
  - Limit/offset pagination
  - Optional source filter
  - Missing-embeddings-only flag
  - Published date range filters
  - Sort direction (asc/desc)
  - Return oldest/newest timestamp bounds
- Implement `fetch_article_chroma_mappings()` to return all article→chroma ID mappings for drift analysis

### 5. Add vector store pagination helpers
**File:** `backend/app/vector_store.py`
- Implement `list_articles(limit, offset)` to return paginated Chroma documents with metadata and previews
- Implement `list_all_ids()` to return all stored Chroma IDs for drift detection (used by `/debug/storage/drift`)

### 6. Expose debug API endpoints
**File:** `backend/app/api/routes/debug.py`
- Add `GET /debug/startup` → returns startup metrics timeline (events + notes)
- Add `GET /debug/chromadb/articles` → returns paginated raw Chroma entries with limit/offset
- Add `GET /debug/database/articles` → returns paginated Postgres rows with filters (source, embeddings, date range, sort)
- Add `GET /debug/storage/drift` → compares Chroma IDs vs Postgres mappings, returns missing/dangling counts + samples

### 7. Add frontend API bindings
**File:** `frontend/lib/api.ts`
- Export types: `StartupEventMetric`, `StartupMetricsResponse`, `ChromaDebugResponse`, `DatabaseDebugResponse`, `StorageDriftReport`
- Export fetchers: `fetchStartupMetrics()`, `fetchChromaDebugArticles()`, `fetchDatabaseDebugArticles()`, `fetchStorageDrift()`
- Ensure snake_case→camelCase mapping for response fields

### 8. Build debug dashboard page
**File:** `frontend/app/debug/page.tsx`
- Create `/debug` route with multi-tab inspection UI
- Render startup timeline: phase name, duration, metadata badges (cache size, vectors, migrated records)
- Display Chroma browser: paginated table with ID, title, source, preview
- Display Postgres browser: paginated table with filters (source, date range, missing-embeddings-only flag)
- Display drift report: sample tables for missing-in-chroma and dangling-in-chroma entries
- Include summary cards for quick metrics (boot time, total articles, vector count, drift count)

## Implementation checklist
- [ ] Create `backend/app/services/startup_metrics.py`
- [ ] Instrument `backend/app/vector_store.py::VectorStore.__init__()`
- [ ] Instrument `backend/app/main.py::on_startup()` (all phases)
- [ ] Add `fetch_articles_page()` and `fetch_article_chroma_mappings()` to `backend/app/database.py`
- [ ] Add `list_articles()` and `list_all_ids()` to `backend/app/vector_store.py`
- [ ] Add `/debug/startup`, `/debug/chromadb/articles`, `/debug/database/articles`, `/debug/storage/drift` to `backend/app/api/routes/debug.py`
- [ ] Add types and fetchers to `frontend/lib/api.ts`
- [ ] Create `frontend/app/debug/page.tsx` with dashboard layout
- [ ] Run `uvx ruff check backend` → all checks pass
- [ ] Test endpoints in curl or Postman to verify response structure

## Verification checklist
- [ ] `GET http://localhost:8000/debug/startup` returns valid timeline with events and notes
- [ ] `GET http://localhost:8000/debug/chromadb/articles?limit=50&offset=0` returns paginated Chroma docs
- [ ] `GET http://localhost:8000/debug/database/articles?source=bbc&missing_embeddings_only=false` filters correctly
- [ ] `GET http://localhost:8000/debug/storage/drift` compares counts and returns drift samples
- [ ] `http://localhost:3000/debug` loads without errors and displays all four sections
- [ ] Refresh button triggers all four API calls in parallel
- [ ] Pagination controls update limit/offset correctly
- [ ] Database filters (source, date range) update and refresh data
- [ ] Startup timeline shows non-zero phase durations if backend just started

## Future enhancements
- Streaming startup metrics via SSE (live tail during boot)
- Export startup report as JSON/CSV for performance tracking over time
- Automated drift alerts (post to Slack/email if dangling > threshold)
- Performance graphs (startup time trends, article throughput)
- Sync-on-demand action (button to force vector store refresh for missing articles)
