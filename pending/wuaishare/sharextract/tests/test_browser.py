import os
import unittest
from unittest.mock import patch

from sharextract.browser import _proxy_config, _validate_browser_request_url
from sharextract.http import UnsafeURL


class BrowserProxyTests(unittest.TestCase):
    def test_proxy_is_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "sharextract.browser.urllib.request.getproxies",
                return_value={"https": "http://127.0.0.1:6152"},
            ):
                self.assertIsNone(_proxy_config("https://x.com/"))

    def test_builds_playwright_proxy_only_in_explicit_trust_mode(self):
        with patch.dict(
            os.environ,
            {"SHAREXTRACT_TRUST_PROXY": "1"},
            clear=True,
        ):
            with patch(
                "sharextract.browser.urllib.request.getproxies",
                return_value={"https": "http://127.0.0.1:6152"},
            ):
                self.assertEqual(
                    _proxy_config("https://x.com/i/grok/share/example"),
                    {"server": "http://127.0.0.1:6152"},
                )

    def test_preserves_proxy_credentials_separately(self):
        with patch.dict(
            os.environ,
            {"SHAREXTRACT_TRUST_PROXY": "1"},
            clear=True,
        ):
            with patch(
                "sharextract.browser.urllib.request.getproxies",
                return_value={"https": "http://alice:secret@proxy.example:8080"},
            ):
                self.assertEqual(
                    _proxy_config("https://x.com/"),
                    {
                        "server": "http://proxy.example:8080",
                        "username": "alice",
                        "password": "secret",
                    },
                )

    def test_ignores_unsupported_proxy_scheme(self):
        with patch.dict(
            os.environ,
            {"SHAREXTRACT_TRUST_PROXY": "1"},
            clear=True,
        ):
            with patch(
                "sharextract.browser.urllib.request.getproxies",
                return_value={"https": "ftp://proxy.example:21"},
            ):
                self.assertIsNone(_proxy_config("https://x.com/"))

    def test_browser_guard_rejects_private_destination(self):
        with self.assertRaises(UnsafeURL):
            _validate_browser_request_url("http://127.0.0.1/private")

    def test_browser_guard_allows_non_network_internal_urls(self):
        self.assertEqual(
            _validate_browser_request_url("data:text/plain,hello"),
            "data:text/plain,hello",
        )


if __name__ == "__main__":
    unittest.main()
