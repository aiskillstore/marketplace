"""Thin FMP price adapter for MAE/MFE calculation.

Single-purpose: fetch daily close prices.  Does not reuse existing
fmp_client modules (which vary in return shape across skills).
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

_FMP_HIST_ENDPOINTS = [
    ("https://financialmodelingprep.com/stable/historical-price-eod/full", True),
    ("https://financialmodelingprep.com/api/v3/historical-price-full", False),
]


class FMPPriceAdapter:
    """Fetch daily adjusted close prices from FMP API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("FMP_API_KEY")
        if not self.api_key:
            raise ValueError("FMP API key required. Set FMP_API_KEY env var or pass api_key.")

    def get_daily_closes(self, ticker: str, from_date: str, to_date: str) -> list[dict]:
        """Return daily close prices, oldest first.

        Args:
            ticker: Stock symbol (e.g., "AAPL").
            from_date: Start date "YYYY-MM-DD".
            to_date: End date "YYYY-MM-DD".

        Returns:
            List of {"date": "YYYY-MM-DD", "close": float}, oldest first.

        Raises:
            urllib.error.URLError: On network/API errors (only if all endpoints fail).
            ValueError: On invalid response.
        """
        last_error = None
        for base_url, is_stable in _FMP_HIST_ENDPOINTS:
            if is_stable:
                url = f"{base_url}?symbol={ticker}&from={from_date}&to={to_date}"
            else:
                url = f"{base_url}/{ticker}?from={from_date}&to={to_date}"
            req = urllib.request.Request(url, headers={"apikey": self.api_key})

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                last_error = e
                logger.debug("FMP endpoint %s failed for %s: %s", base_url, ticker, e)
                continue

            historical = self._extract_historical(data, ticker)
            if not historical:
                continue

            # FMP returns newest first; reverse to oldest first.
            # Stable EOD endpoint no longer exposes `adjClose`; fall back to `close`.
            # Patched 2026-05-22 (stable shape).
            result = [
                {"date": item["date"], "close": item.get("adjClose") or item["close"]}
                for item in reversed(historical)
                if "date" in item and ("adjClose" in item or "close" in item)
            ]
            return result

        if last_error:
            logger.error("FMP API error for %s: %s", ticker, last_error)
            raise last_error

        logger.warning("No price data returned for %s (%s to %s)", ticker, from_date, to_date)
        return []

    @staticmethod
    def _extract_historical(data, ticker: str) -> list[dict]:
        """Extract historical array from FMP response (stable list / v3 dict)."""
        # New stable EOD endpoint returns a flat list of dicts directly.
        # Patched 2026-05-22 (stable shape).
        if isinstance(data, list):
            norm = ticker.replace("-", ".")
            return [
                row
                for row in data
                if isinstance(row, dict) and row.get("symbol", ticker).replace("-", ".") == norm
            ]
        if not isinstance(data, dict):
            return []
        if "historical" in data:
            return data["historical"]
        if "historicalStockList" in data:
            norm = ticker.replace("-", ".")
            for entry in data["historicalStockList"]:
                if entry.get("symbol", "").replace("-", ".") == norm:
                    return entry.get("historical", [])
        return []
