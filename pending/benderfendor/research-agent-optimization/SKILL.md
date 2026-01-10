---
name: research-agent-optimization
description: Optimize the research agent for rate limit handling, API call efficiency, web search integration fixes, and improved streaming UX with granular progress updates and source attribution.
---

# Research Agent Optimization

## Scope
- Project root: `/home/bender/classwork/Thesis`
- Backend: `backend/news_research_agent.py`, `backend/app/api/routes/research.py`, `backend/app/services/news_research.py`
- Frontend: `frontend/app/search/page.tsx`, `frontend/lib/api.ts`
- Configuration: `backend/app/core/config.py`

## Problem Statement
1. **Rate Limiting**: Gemini API hits 429 quota exceeded errors during research and article analysis
2. **Web Search**: DuckDuckGo tool integration has naming issues (not properly initialized)
3. **Unclear Progress**: Research streaming shows generic "Still working..." instead of specific tool calls
4. **JSON in Response**: Results show raw JSON blocks instead of formatted source cards
5. **Redundant API Calls**: Multiple internal search calls without caching/deduplication

## Required Outcomes
- Graceful rate limit handling with exponential backoff and quota monitoring
- Working web search tool with proper DuckDuckGo initialization
- Verbose streaming events showing real tool execution (web_search, news_search, internal_news_search)
- Research results rendered with inline source cards (not JSON blocks)
- Optimized API calls: batch searches, cache semantic results, reuse internal knowledge base
- Clear error messages when quota is exceeded

## Workflow

### 1. API Call Optimization
- Implement request batching in `search_internal_news` tool
- Add caching layer for semantic search results (avoid duplicate queries within 5min window)
- Combine web_search + news_search into single result set
- Track API call counts per session and warn before quota exhaustion
- Add exponential backoff retry logic (1s, 2s, 4s, 8s max)

**Files:**
- `backend/news_research_agent.py` - tools and caching
- `backend/app/services/news_research.py` - request batching helpers

### 2. Rate Limit & Quota Handling
- Add try/catch wrapper around Gemini calls
- Detect 429 errors and return user-friendly message ("API Rate Limit: ...please wait a moment...")
- Add optional `--skip-gemini-analysis` mode for article analysis when quota is low
- Log quota usage and remaining tokens
- Set model to `gemini-2.0-flash` (faster, lower token cost) instead of `gemini-2.0-flash-exp`

**Files:**
- `backend/app/core/config.py` - error handling wrapper, model selection
- `backend/app/api/routes/research.py` - HTTP error responses
- `backend/news_research_agent.py` - LLM call error handling

### 3. Web Search Tool Fix
- Verify DuckDuckGo import: `from duckduckgo_search import DDGS` (not `ddgs` or `DuckDuckGo`)
- Ensure `web_search` and `news_search` tools are properly bound to LLM
- Add fallback to internal search if web search fails
- Log tool execution with query and result count

**Files:**
- `backend/news_research_agent.py` - tool definitions and error handling
- Use `exa-code` to verify current DuckDuckGo API patterns

### 4. Streaming Progress Clarity
- Expand SSE event types: `tool_start` includes tool name + query parameters
- Map tool events to user-friendly messages:
  - `web_search("climate change")` → "Searching web for: climate change..."
  - `news_search(keywords="COP30")` → "Searching news for: COP30..."
  - `search_internal_news(query)` → "Searching internal knowledge base..."
  - `fetch_article_content(url)` → "Reading article: [title/domain]..."
- Add timestamps and tool execution duration
- Emit status updates every 3-5 seconds if no tool activity

**Files:**
- `backend/news_research_agent.py` - streaming generator
- `backend/app/api/routes/research.py` - SSE formatting

### 5. Frontend Result Rendering
- Remove JSON blocks from response text
- Render referenced articles in a "Sources" section below the answer
- Use article cards: title, source, date, image thumbnail
- Make cards clickable to open article detail modal
- Group sources by retrieval method (semantic, web search, internal)

**Files:**
- `frontend/app/search/page.tsx` - message rendering and sources grid
- `frontend/lib/api.ts` - response parsing

### 6. Error Handling & User Feedback
- Detect and handle:
  - 429 quota exceeded → "API Rate Limit: The AI service has reached its rate limit. Please wait a moment and try again."
  - Connection timeout → "Request Timeout: The research took too long. Try a simpler query."
  - Tool execution failure → "Tool [name] failed: [reason]. Continuing with alternative search..."
- Add retry prompt on error (not automatic, user chooses)
- Log all errors with request ID for debugging

**Files:**
- `backend/app/api/routes/research.py` - error formatting
- `frontend/app/search/page.tsx` - error UI and retry logic

## Checks

### API Optimization
- Verify semantic search results are cached (no duplicate calls)
- Check web_search and news_search return results (not empty)
- Confirm tool execution logs show cache hits for repeated queries

### Rate Limit Handling
- Trigger 429 error and verify graceful fallback message displays
- Confirm no stack traces shown to user
- Check logs show quota status and retry timing

### Web Search
- Query "climate change" and verify web_search returns 5+ results
- Confirm DuckDuckGo DDGS class is properly instantiated
- Check news_search returns recent news articles

### Streaming Clarity
- Monitor SSE events for tool_start with query details
- Verify timestamps increment correctly
- Confirm "Still working..." message only shows after 30s inactivity

### Frontend Rendering
- Verify research answer is plain text (no JSON)
- Check "Sources" section appears with article cards
- Confirm card click opens article detail modal
- Verify no duplicate sources (de-duplication working)

### Error Scenarios
- Submit invalid query and verify doesn't crash
- Test with network disconnect and check timeout message
- Simulate quota exceeded (403) and verify user sees rate limit message

## Implementation Checklist

- [ ] Add retry decorator with exponential backoff to Gemini client
- [ ] Implement request cache in `search_internal_news` with 5min TTL
- [ ] Fix DuckDuckGo tool initialization (verify DDGS import)
- [ ] Update `research_stream()` to emit granular tool start/result events
- [ ] Map tool events to human-readable status messages in API endpoint
- [ ] Remove JSON block from final answer text
- [ ] Add "Sources" section with article cards to frontend
- [ ] Update error handling for 429 quota exceeded
- [ ] Add streaming status animation to UI
- [ ] Write tests for quota handling and web search integration
