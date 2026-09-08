import os
import socket
import unittest
from unittest.mock import patch

from sharextract import __version__
from sharextract.http import (
    SafeHttpClient,
    UnsafeURL,
    _resolve_public_endpoints,
    validate_public_url,
)


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

    def test_rejects_hostname_that_resolves_private(self):
        with patch(
            "sharextract.http.socket.getaddrinfo",
            return_value=[
                (
                    socket.AF_INET,
                    socket.SOCK_STREAM,
                    socket.IPPROTO_TCP,
                    "",
                    ("10.0.0.5", 443),
                )
            ],
        ):
            with self.assertRaises(UnsafeURL):
                validate_public_url("https://example.test/private")

    def test_resolves_public_hostname_once_for_endpoint_set(self):
        answers = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                ("93.184.216.34", 443),
            )
        ]
        with patch(
            "sharextract.http.socket.getaddrinfo",
            return_value=answers,
        ) as resolver:
            endpoints = _resolve_public_endpoints("example.test", 443)
        resolver.assert_called_once_with(
            "example.test",
            443,
            type=socket.SOCK_STREAM,
        )
        self.assertEqual(endpoints[0][3][0], "93.184.216.34")

    def test_dns_skip_requires_explicit_trusted_proxy_mode(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(UnsafeURL):
                validate_public_url(
                    "https://example.com/page",
                    resolve_dns=False,
                )

    def test_trusted_proxy_mode_can_skip_local_dns(self):
        with patch.dict(
            os.environ,
            {"SHAREXTRACT_TRUST_PROXY": "1"},
            clear=True,
        ):
            with patch("sharextract.http.socket.getaddrinfo") as resolver:
                validate_public_url(
                    "https://example.com/page",
                    resolve_dns=False,
                )
                resolver.assert_not_called()


if __name__ == "__main__":
    unittest.main()
