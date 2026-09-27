"""Tests for fmp_price_adapter.py — mock HTTP responses."""

import json
from unittest.mock import MagicMock, patch

import fmp_price_adapter
import pytest


def test_get_daily_closes_parses_response():
    """Mock FMP response → parsed correctly, oldest first."""
    mock_response_data = {
        "symbol": "AAPL",
        "historical": [
            {"date": "2026-03-03", "adjClose": 152.0, "close": 152.0},
            {"date": "2026-03-02", "adjClose": 150.5, "close": 150.5},
            {"date": "2026-03-01", "adjClose": 149.0, "close": 149.0},
        ],
    }

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(mock_response_data).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        adapter = fmp_price_adapter.FMPPriceAdapter(api_key="test_key")
        result = adapter.get_daily_closes("AAPL", "2026-03-01", "2026-03-03")

    assert len(result) == 3
    # Oldest first
    assert result[0]["date"] == "2026-03-01"
    assert result[0]["close"] == 149.0
    assert result[2]["date"] == "2026-03-03"
    assert result[2]["close"] == 152.0


def test_get_daily_closes_empty_response():
    """Empty historical data → empty list."""
    mock_response_data = {"symbol": "XYZ", "historical": []}

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(mock_response_data).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        adapter = fmp_price_adapter.FMPPriceAdapter(api_key="test_key")
        result = adapter.get_daily_closes("XYZ", "2026-03-01", "2026-03-03")

    assert result == []


def test_uses_apikey_header():
    """FMP adapter should use 'apikey' header (not 'Authorization')."""
    mock_response_data = {"symbol": "AAPL", "historical": []}
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(mock_response_data).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        adapter = fmp_price_adapter.FMPPriceAdapter(api_key="my_test_key")
        adapter.get_daily_closes("AAPL", "2026-03-01", "2026-03-03")

    req = mock_urlopen.call_args[0][0]
    assert req.get_header("Apikey") == "my_test_key"
    assert req.get_header("Authorization") is None


def test_no_api_key_raises():
    """Missing API key should raise ValueError."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="FMP API key required"):
            fmp_price_adapter.FMPPriceAdapter(api_key=None)
