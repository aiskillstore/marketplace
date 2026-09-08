from __future__ import annotations

import argparse
from typing import Any, Literal

from . import __version__
from .capabilities import get_capabilities
from .health import get_adapter_health
from .http import FetchError, UnsafeURL
from .router import ExtractionFailure, extract

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - exercised by optional-dependency boundary
    raise RuntimeError(
        'HTTP API dependencies are not installed. Install with: pip install -e ".[service]"'
    ) from exc


class ExtractRequest(BaseModel):
    url: str = Field(description="Public HTTP(S) URL to extract.")
    strategy: Literal["auto", "native", "media", "web"] = "auto"
    timeout: float = Field(default=20.0, gt=0, le=120)
    max_bytes: int = Field(default=8 * 1024 * 1024, ge=1024, le=64 * 1024 * 1024)


class MessageResponse(BaseModel):
    role: str
    text: str
    author: str | None = None
    created_at: str | float | int | None = None
    attachments: list[dict[str, Any]] = Field(default_factory=list)


class ExtractResponse(BaseModel):
    source_url: str
    canonical_url: str
    platform: str
    kind: str
    extraction_method: str
    confidence: float
    title: str = ""
    author: str = ""
    text: str = ""
    markdown: str = ""
    html: str = ""
    messages: list[MessageResponse] = Field(default_factory=list)
    media: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    retrieved_at: str


def create_app() -> FastAPI:
    app = FastAPI(
        title="ShareXtract API",
        version=__version__,
        description=(
            "Protocol-first extraction of content that is already publicly accessible. "
            "The API does not bypass authentication, CAPTCHAs, paywalls, WAFs, or private sharing controls."
        ),
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/v1/capabilities")
    def capabilities() -> dict[str, Any]:
        return {"version": __version__, **get_capabilities()}

    @app.get("/v1/health/adapters")
    def adapter_health(
        live: bool = False,
        adapter: str | None = None,
        timeout: float = 12.0,
    ) -> dict[str, Any]:
        names = [
            token.strip()
            for token in (adapter or "").split(",")
            if token.strip()
        ]
        try:
            return {
                "version": __version__,
                **get_adapter_health(
                    live=live,
                    adapter_names=names,
                    timeout=timeout,
                ),
            }
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/v1/extract", response_model=ExtractResponse)
    def extract_url(request: ExtractRequest) -> dict[str, Any]:
        try:
            result = extract(
                request.url,
                strategy=request.strategy,
                timeout=request.timeout,
                max_bytes=request.max_bytes,
            )
            return result.to_dict()
        except UnsafeURL as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ExtractionFailure as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except FetchError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return app


app = create_app()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the ShareXtract HTTP/OpenAPI service.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--log-level", default="info")
    args = parser.parse_args(argv)

    import uvicorn

    uvicorn.run(
        "sharextract.http_api:app",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
