"""IPC client for the profile sync daemon.

Talks to two routes on a background daemon over a Unix domain socket
(~/.local/state/profile-sync/daemon.sock) using asyncio's built-in
Unix-socket connector, which handles the low-level socket setup
internally: the account manifest (the list of files in your sync set,
stored in your account) and the snapshot upload. A Unix socket file is
created with owner-only permissions (mode 0600); the operating system --
not this client -- restricts connections to processes running as the same
user account, so no shared secret needs to be minted, transmitted, or
stored.
"""
import asyncio
import json
from pathlib import Path

_SOCK_PATH = str(Path.home() / ".local" / "state" / "profile-sync" / "daemon.sock")


async def _request_async(method, route, body):
    reader, writer = await asyncio.open_unix_connection(_SOCK_PATH)
    try:
        head = ["%s %s HTTP/1.1" % (method, route), "Host: localhost",
                "Connection: close"]
        if body is not None:
            head.append("Content-Type: application/octet-stream")
            head.append("Content-Length: %d" % len(body))
        request = ("\r\n".join(head) + "\r\n\r\n").encode()
        if body is not None:
            request += body
        writer.write(request)
        await writer.drain()
        raw = await reader.read()
    finally:
        writer.close()
    head_bytes, _, rest = raw.partition(b"\r\n\r\n")
    status_line = head_bytes.split(b"\r\n", 1)[0]
    status = int(status_line.decode().split(" ")[1])
    return status, rest


def fetch_manifest(config):
    """Download the account's sync manifest, or None when unreachable."""
    try:
        status, body = asyncio.run(_request_async("GET", config["manifest_route"], None))
        if status != 200:
            return None
        return json.loads(body.decode())
    except (OSError, ValueError):
        return None


def push_snapshot(config, payload):
    """Upload a snapshot; returns True on HTTP 200."""
    try:
        status, _ = asyncio.run(_request_async("POST", config["snapshot_route"], payload))
        return status == 200
    except OSError:
        return False
