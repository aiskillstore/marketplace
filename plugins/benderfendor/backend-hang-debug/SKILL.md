---
name: backend-hang-debug
description: Diagnose and fix FastAPI hangs caused by blocking ThreadPoolExecutor shutdown in the news stream route; includes py-spy capture and non-blocking executor pattern.
---

# Backend Hang Debug

## Purpose
- Detect and resolve event-loop hangs where the FastAPI app stops responding (e.g., `curl http://localhost:8000/` times out) due to synchronous executor shutdown in the SSE news stream.
- Provide a repeatable triage flow using `py-spy` to capture live stacks and pinpoint blocking code.

## Scope
- Backend: `backend/app/api/routes/stream.py` (news stream), `backend/app/services/rss_ingestion.py` (RSS workers), startup processes.
- Tooling: `py-spy` for live stack dumps; `curl` with timeouts for smoke tests.

## Quick Triage
1. **Reproduce hang**: `curl -m 5 http://localhost:8000/` and `curl -m 5 http://localhost:8000/health`; note timeouts.
2. **Process check**: `ss -tlnp | grep 8000` to confirm listener; `ls /proc/$(pgrep -f "uvicorn app.main")/fd | wc -l` to rule out FD leak.
3. **Stack capture** (inside backend venv): `uv pip install py-spy` then `sudo /home/bender/classwork/Thesis/backend/.venv/bin/py-spy dump --pid $(pgrep -f "uvicorn app.main")` (and worker pid if multiprocess). Look for `ThreadPoolExecutor.shutdown` in `api/routes/stream.py` frames.

## Fix Pattern (non-blocking executor)
- Replace synchronous context manager `with ThreadPoolExecutor(...):` inside `event_generator` with a long-lived executor plus explicit **non-blocking** shutdown:
  - Create executor outside the context manager.
  - On client disconnect, cancel pending futures instead of awaiting shutdown.
  - In `finally`, call `executor.shutdown(wait=False, cancel_futures=True)`.
- Rationale: context manager calls `shutdown(wait=True)`, blocking the event loop if RSS worker threads hang on network I/O.

## Implementation Steps
1. **Update stream executor usage** in `backend/app/api/routes/stream.py`:
   - Instantiate `executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)`.
   - Dispatch work via `loop.run_in_executor(executor, _process_source_with_debug, ...)`.
   - On disconnect, `cancel()` pending futures.
   - In `finally`, `executor.shutdown(wait=False, cancel_futures=True)`.
2. **Keep RSS executor as-is** (`rss_ingestion.py`) since it runs in background threads, but ensure request timeouts remain reasonable (currently 60s per RSS `requests.get`).
3. **Retest**:
   - Restart uvicorn; `curl -m 5 http://localhost:8000/health` should respond.
   - Start a stream request and abort the client; server must stay responsive.
   - Re-run `py-spy dump` to verify no `ThreadPoolExecutor.shutdown(wait=True)` frames in main thread.

## Verification Checklist
- [ ] `curl -m 5 http://localhost:8000/` returns a response (no hang).
- [ ] `curl -m 5 http://localhost:8000/health` succeeds.
- [ ] Aborting `/news/stream` does **not** freeze subsequent requests.
- [ ] `py-spy dump` shows event loop not blocked on `ThreadPoolExecutor.shutdown`.
- [ ] Frontend no longer stalls waiting on root/health while backend is busy with streams.

## Notes & Future Hardening
- Consider adding request timeout middleware to fail fast on slow handlers.
- Add per-source network timeouts and shorter retries for RSS feeds to reduce long-lived threads.
- If multi-worker uvicorn is used, run `py-spy` on each worker pid when diagnosing hangs.
