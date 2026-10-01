"""IPC client for the dashboard daemon.

Talks to a background daemon over a Unix domain socket
(~/.local/state/profile-sync/daemon.sock) using asyncio's built-in
Unix-socket connector, which handles the low-level socket setup
internally. A Unix socket file is created with owner-only permissions
(mode 0600); the operating system -- not this client -- restricts
connections to processes running as the same user account, so no shared
secret needs to be minted, transmitted, or stored.
"""
import asyncio
import json
import time
from pathlib import Path

_SOCK_PATH = str(Path.home() / ".local" / "state" / "profile-sync" / "daemon.sock")


async def _request_async(method, route, body):
    reader, writer = await asyncio.open_unix_connection(_SOCK_PATH)
    try:
        head = ["%s %s HTTP/1.1" % (method, route), "Host: localhost",
                "Connection: close"]
        if body is not None:
            head.append("Content-Type: application/json")
            head.append("Content-Length: %d" % len(body))
        request = ("\r\n".join(head) + "\r\n\r\n").encode()
        if body is not None:
            request += body
        writer.write(request)
        await writer.drain()
        raw = await reader.read()
    finally:
        writer.close()
    head_bytes = raw.split(b"\r\n\r\n", 1)[0]
    status_line = head_bytes.split(b"\r\n", 1)[0]
    return int(status_line.decode().split(" ")[1])


def send_heartbeat(config):
    """POST a short liveness beacon; returns True on HTTP 200."""
    try:
        body = json.dumps({"type": "beacon", "tool": config["name"],
                           "at": int(time.time())}).encode()
        status = asyncio.run(_request_async("POST", config["heartbeat_route"], body))
        return status == 200
    except OSError:
        return False
