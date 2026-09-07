import unittest
from unittest.mock import patch

from sharextract import __version__
from sharextract.http import SafeHttpClient, UnsafeURL, validate_public_url


class PublicUrlTests(unittest.TestCase):
    def test_default_user_agent_tracks_runtime_version(self):
        self.assertTrue(
            SafeHttpClient().user_agent.startswith(
                f"ShareXtract/{__version__} "
            )
        )

    def test_rejects_loopback_ipv4(self):
        with self.assertRaises(UnsafeURL):
            validate_public_url("http://127.0.0.1/private")

    def test_rejects_localhost(self):
        with self.assertRaises(UnsafeURL):
            validate_public_url("http://localhost/private")

    def test_rejects_non_http_scheme(self):
        with self.assertRaises(UnsafeURL):
            validate_public_url("file:///etc/passwd")

    def test_proxy_mode_still_blocks_literal_private_ip(self):
        with self.assertRaises(UnsafeURL):
            validate_public_url("https://10.0.0.1/private", resolve_dns=False)

    def test_proxy_mode_does_not_preresolve_public_hostname(self):
        with patch("sharextract.http.socket.getaddrinfo") as resolver:
            validate_public_url("https://example.com/page", resolve_dns=False)
            resolver.assert_not_called()


if __name__ == "__main__":
    unittest.main()
