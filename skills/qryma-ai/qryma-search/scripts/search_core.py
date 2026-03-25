#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qryma Search Core Logic
"""
import os
import re
import json
import urllib.request
from typing import Optional

# Backward compatibility
QRYMA_URL = "https://search.qryma.com/api/web"


def load_key() -> Optional[str]:
    """Load Qryma API key"""
    # Load from environment variable
    key = os.environ.get("QRYMA_API_KEY")
    if key:
        return key.strip()

    # Load from environment variable for endpoint
    endpoint = os.environ.get("QRYMA_ENDPOINT")
    if endpoint:
        pass  # just for loading, we'll handle it in the core

    # Load from config file
    env_path = os.path.expanduser("~/.qryma/.env")
    if not os.path.exists(env_path):
        env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            m = re.search(r"^\s*QRYMA_API_KEY\s*=\s*(.+?)\s*$", txt, re.M)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                if v:
                    return v
        except Exception:
            pass

    return None


def load_endpoint() -> str:
    """Load Qryma API endpoint"""
    # Load from environment variable
    endpoint = os.environ.get("QRYMA_ENDPOINT")
    if endpoint:
        return endpoint.strip()

    # Load from config file
    env_path = os.path.expanduser("~/.qryma/.env")
    if not os.path.exists(env_path):
        env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            m = re.search(r"^\s*QRYMA_ENDPOINT\s*=\s*(.+?)\s*$", txt, re.M)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                if v:
                    return v
        except Exception:
            pass

    # Default to the old endpoint for backward compatibility
    return "https://search.qryma.com/api/web"


class QrymaSearchCore:
    """Qryma search core class"""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or load_key()
        self.endpoint = endpoint or load_endpoint()

    def search(
        self,
        query: str,
        max_results: int = 5,
        lang: str = "en",
        start: int = 0,
        safe: bool = False,
        detail: bool = False,
    ) -> dict:
        """Execute search"""
        if not self.api_key:
            raise ValueError("QRYMA_API_KEY not found")

        # Backend API parameters: query, lang, start, safe, detail
        payload = {
            "query": query,
            "lang": lang,
            "start": start,
            "safe": safe,
            "detail": detail,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "X-Api-Key": self.api_key,
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")

        try:
            obj = json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Response parsing failed: {e}") from e

        # Format response
        out = {
            "query": query,
            "results": [],
        }

        # Process result format returned by backend
        # max_results is applied locally by truncating results array
        for r in (obj.get("organic") or [])[:max_results]:
            out["results"].append(
                {
                    "title": r.get("title"),
                    "url": r.get("link"),  # API returns link field
                    "content": r.get("snippet"),  # API returns snippet field
                }
            )

        return out
