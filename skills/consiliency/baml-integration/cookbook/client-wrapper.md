# BAML Client Wrapper Cookbook

How to wrap the generated BAML client for your application's needs.

## Why Wrap the Client?

Wrapping the BAML client provides:
1. **Error handling**: Consistent error handling across all LLM calls
2. **Logging**: Observability for all LLM interactions
3. **Retry logic**: Automatic retries with backoff
4. **Rate limiting**: Prevent exceeding API limits
5. **Caching**: Cache responses for identical inputs
6. **Metrics**: Track usage, latency, and costs

## Basic Wrapper Pattern

### Python Wrapper

```python
# services/llm_gateway.py
import logging
from typing import TypeVar, Callable, Any
from functools import wraps
import asyncio

from baml_client import b
from baml_client.types import *

logger = logging.getLogger(__name__)

T = TypeVar('T')

class LLMGateway:
    """Wrapper around BAML client with error handling and observability."""

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_caching: bool = True
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_caching = enable_caching
        self._cache: dict[str, Any] = {}

    async def _with_retry(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """Execute function with retry logic."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(
                    f"LLM call failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))

        raise last_error

    def _cache_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key from function call."""
        import hashlib
        import json
        content = json.dumps({
            "func": func_name,
            "args": [str(a) for a in args],
            "kwargs": {k: str(v) for k, v in kwargs.items()}
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    async def analyze_book(
        self,
        request: AnalyzeBookRequest
    ) -> AnalyzeBookResponse:
        """Analyze a book with error handling and caching."""

        # Check cache
        if self.enable_caching:
            cache_key = self._cache_key("analyze_book", request)
            if cache_key in self._cache:
                logger.debug("Cache hit for analyze_book")
                return self._cache[cache_key]

        # Call with retry
        logger.info(f"Analyzing book: {request.analysis_type}")
        result = await self._with_retry(b.AnalyzeBook, request)

        # Cache result
        if self.enable_caching:
            self._cache[cache_key] = result

        logger.info(f"Analysis complete, confidence: {result.confidence}")
        return result

    async def classify_text(
        self,
        text: str,
        categories: list[str]
    ) -> ClassificationResult:
        """Classify text into categories."""
        request = ClassifyTextRequest(
            text=text,
            categories=categories
        )
        return await self._with_retry(b.ClassifyText, request)


# Singleton instance
llm = LLMGateway()
```

### TypeScript Wrapper

```typescript
// services/llmGateway.ts
import { b } from '../baml_client';
import type {
  AnalyzeBookRequest,
  AnalyzeBookResponse,
  ClassifyTextRequest,
  ClassificationResult
} from '../baml_client/types';

interface GatewayConfig {
  maxRetries: number;
  retryDelay: number;
  enableCaching: boolean;
}

const defaultConfig: GatewayConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  enableCaching: true
};

class LLMGateway {
  private config: GatewayConfig;
  private cache: Map<string, unknown> = new Map();

  constructor(config: Partial<GatewayConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
  }

  private async withRetry<T>(
    fn: () => Promise<T>,
    context: string
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.config.maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        console.warn(
          `LLM call failed (${context}, attempt ${attempt + 1}): ${lastError.message}`
        );
        if (attempt < this.config.maxRetries - 1) {
          await this.delay(this.config.retryDelay * Math.pow(2, attempt));
        }
      }
    }

    throw lastError;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private cacheKey(name: string, args: unknown): string {
    return `${name}:${JSON.stringify(args)}`;
  }

  async analyzeBook(request: AnalyzeBookRequest): Promise<AnalyzeBookResponse> {
    const key = this.cacheKey('analyzeBook', request);

    if (this.config.enableCaching && this.cache.has(key)) {
      console.debug('Cache hit for analyzeBook');
      return this.cache.get(key) as AnalyzeBookResponse;
    }

    const result = await this.withRetry(
      () => b.AnalyzeBook(request),
      'analyzeBook'
    );

    if (this.config.enableCaching) {
      this.cache.set(key, result);
    }

    return result;
  }

  async classifyText(
    text: string,
    categories: string[]
  ): Promise<ClassificationResult> {
    return this.withRetry(
      () => b.ClassifyText({ text, categories }),
      'classifyText'
    );
  }

  clearCache(): void {
    this.cache.clear();
  }
}

// Singleton export
export const llm = new LLMGateway();
```

## Advanced Patterns

### Pattern 1: Observability Decorator

```python
import time
from functools import wraps

def observe_llm_call(func):
    """Decorator for LLM call observability."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        func_name = func.__name__

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start

            # Log metrics
            logger.info(f"LLM call {func_name} completed in {duration:.2f}s")
            metrics.histogram("llm.duration", duration, tags={"function": func_name})
            metrics.increment("llm.calls.success", tags={"function": func_name})

            return result

        except Exception as e:
            duration = time.time() - start
            logger.error(f"LLM call {func_name} failed after {duration:.2f}s: {e}")
            metrics.increment("llm.calls.failure", tags={"function": func_name})
            raise

    return wrapper

# Usage
class LLMGateway:
    @observe_llm_call
    async def analyze_book(self, request: AnalyzeBookRequest):
        return await b.AnalyzeBook(request)
```

### Pattern 2: Rate Limiting

```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_calls: int, period: timedelta):
        self.max_calls = max_calls
        self.period = period
        self.calls: deque[datetime] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = datetime.now()
            # Remove old calls
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()

            if len(self.calls) >= self.max_calls:
                # Wait until oldest call expires
                wait_time = (self.calls[0] + self.period - now).total_seconds()
                await asyncio.sleep(wait_time)

            self.calls.append(now)

# Usage
rate_limiter = RateLimiter(max_calls=60, period=timedelta(minutes=1))

class LLMGateway:
    async def analyze_book(self, request: AnalyzeBookRequest):
        await rate_limiter.acquire()
        return await b.AnalyzeBook(request)
```

### Pattern 3: Fallback Chain

```python
class LLMGateway:
    async def analyze_with_fallback(
        self,
        request: AnalyzeBookRequest
    ) -> AnalyzeBookResponse:
        """Try primary model, fall back to cheaper model on failure."""
        try:
            # Try GPT-4 first
            return await b.AnalyzeBookGPT4(request)
        except Exception as e:
            logger.warning(f"GPT-4 failed, falling back to GPT-3.5: {e}")
            return await b.AnalyzeBookGPT35(request)
```

### Pattern 4: Structured Error Handling

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class LLMResult(Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None
    retry_count: int = 0
    latency_ms: float = 0

class LLMGateway:
    async def safe_analyze(
        self,
        request: AnalyzeBookRequest
    ) -> LLMResult[AnalyzeBookResponse]:
        """Return result wrapper instead of raising exceptions."""
        start = time.time()
        retry_count = 0

        for attempt in range(self.max_retries):
            try:
                result = await b.AnalyzeBook(request)
                return LLMResult(
                    success=True,
                    data=result,
                    retry_count=retry_count,
                    latency_ms=(time.time() - start) * 1000
                )
            except Exception as e:
                retry_count += 1
                if attempt == self.max_retries - 1:
                    return LLMResult(
                        success=False,
                        error=str(e),
                        retry_count=retry_count,
                        latency_ms=(time.time() - start) * 1000
                    )
```

## Integration with FastAPI

```python
from fastapi import FastAPI, Depends, HTTPException
from services.llm_gateway import LLMGateway, llm

app = FastAPI()

def get_llm() -> LLMGateway:
    return llm

@app.post("/analyze")
async def analyze_book(
    request: AnalyzeBookRequest,
    gateway: LLMGateway = Depends(get_llm)
):
    try:
        result = await gateway.analyze_book(request)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Testing the Wrapper

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def gateway():
    return LLMGateway(max_retries=2, enable_caching=False)

@pytest.mark.asyncio
async def test_retry_on_failure(gateway):
    with patch.object(b, 'AnalyzeBook') as mock:
        mock.side_effect = [Exception("Timeout"), mock_response]

        result = await gateway.analyze_book(mock_request)

        assert mock.call_count == 2
        assert result == mock_response

@pytest.mark.asyncio
async def test_caching(gateway):
    gateway.enable_caching = True

    with patch.object(b, 'AnalyzeBook') as mock:
        mock.return_value = mock_response

        # First call
        await gateway.analyze_book(mock_request)
        # Second call - should use cache
        await gateway.analyze_book(mock_request)

        assert mock.call_count == 1  # Only called once
```
