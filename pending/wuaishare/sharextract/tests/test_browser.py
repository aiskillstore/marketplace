import unittest
from unittest.mock import patch

from sharextract.browser import _proxy_config


class BrowserProxyTests(unittest.TestCase):
    def test_builds_playwright_proxy_from_standard_https_proxy(self):
        with patch(
            "sharextract.browser.urllib.request.getproxies",
            return_value={"https": "http://127.0.0.1:6152"},
        ):
            self.assertEqual(
                _proxy_config("https://x.com/i/grok/share/example"),
                {"server": "http://127.0.0.1:6152"},
            )

    def test_preserves_proxy_credentials_separately(self):
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
        with patch(
            "sharextract.browser.urllib.request.getproxies",
            return_value={"https": "ftp://proxy.example:21"},
        ):
            self.assertIsNone(_proxy_config("https://x.com/"))


if __name__ == "__main__":
    unittest.main()
