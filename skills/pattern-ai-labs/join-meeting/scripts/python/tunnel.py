"""Tunnel client — proxies HTTP/WS requests from AgentCall to localhost.

IMPORTANT: The tunnel_access_key parameter is the per-call credential returned
in the create call response (field: tunnel_access_key). Do NOT use your
AGENTCALL_API_KEY here — that is for API authentication, not tunnel auth.
"""

import asyncio
import json
import logging
from typing import Optional

import aiohttp
import websockets

logger = logging.getLogger(__name__)


class TunnelClient:
    """Connects to AgentCall tunnel server and forwards requests to localhost."""

    def __init__(self, tunnel_ws_url: str, tunnel_id: str, tunnel_access_key: str,
                 local_port: int = 3000, screenshare_port: int = 0):
        self.tunnel_ws_url = tunnel_ws_url
        self.tunnel_id = tunnel_id
        self.tunnel_access_key = tunnel_access_key
        self.local_port = local_port
        self.screenshare_port = screenshare_port
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False

    async def connect(self):
        """Connect to the tunnel server and start proxying."""
        self._running = True

        self._ws = await websockets.connect(self.tunnel_ws_url)

        # Register with tunnel_access_key (NOT the API key).
        await self._ws.send(json.dumps({
            "type": "tunnel.register",
            "payload": {
                "tunnel_id": self.tunnel_id,
                "tunnel_access_key": self.tunnel_access_key,
            },
        }))

        logger.info(f"Tunnel client connected: {self.tunnel_id}")

        # Start read loop.
        asyncio.create_task(self._read_loop())
        asyncio.create_task(self._heartbeat())

    async def _read_loop(self):
        """Read messages from tunnel server and proxy to localhost."""
        try:
            async for message in self._ws:
                msg = json.loads(message)
                msg_type = msg.get("type", "")

                if msg_type == "http.request":
                    asyncio.create_task(self._handle_http_request(msg))
                elif msg_type == "ws.open":
                    asyncio.create_task(self._handle_ws_open(msg))
                elif msg_type == "tunnel.error":
                    logger.error(f"Tunnel server error: {msg.get('message', 'unknown')}")
        except websockets.ConnectionClosed:
            if self._running:
                logger.warning("Tunnel connection lost, reconnecting...")
                await self._reconnect()

    def _resolve_local_url(self, path: str, scheme: str = "http") -> str:
        """Route request to the correct local port based on path prefix.

        Path-based routing:
          /screenshare/...  →  localhost:{screenshare_port}/...
          /ui/...           →  localhost:{local_port}/...
          /...              →  localhost:{local_port}/...  (default)
        """
        if path.startswith("/screenshare") and self.screenshare_port:
            local_path = path[len("/screenshare"):] or "/"
            return f"{scheme}://localhost:{self.screenshare_port}{local_path}"
        if path.startswith("/ui"):
            local_path = path[len("/ui"):] or "/"
            return f"{scheme}://localhost:{self.local_port}{local_path}"
        return f"{scheme}://localhost:{self.local_port}{path}"

    async def _handle_http_request(self, msg: dict):
        """Forward HTTP request to localhost and return response."""
        payload = msg.get("payload", msg)
        request_id = payload.get("request_id", msg.get("request_id", ""))
        method = payload.get("method", "GET")
        path = payload.get("path", "/")
        headers = payload.get("headers", {})
        body = payload.get("body", "")

        local_url = self._resolve_local_url(path)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, local_url, headers=headers,
                                           data=body if body else None) as resp:
                    body = await resp.text()
                    resp_headers = {k: v for k, v in resp.headers.items()}

                    response = {
                        "type": "http.response",
                        "request_id": request_id,
                        "payload": {
                            "request_id": request_id,
                            "status": resp.status,
                            "headers": resp_headers,
                            "body": body,
                        },
                    }
                    await self._ws.send(json.dumps(response))
        except Exception as e:
            response = {
                "type": "http.response",
                "request_id": request_id,
                "payload": {
                    "request_id": request_id,
                    "status": 502,
                    "headers": {"Content-Type": "text/plain"},
                    "body": f"Local server error: {e}",
                },
            }
            await self._ws.send(json.dumps(response))

    async def _handle_ws_open(self, msg: dict):
        """Forward WebSocket connection to localhost."""
        payload = msg.get("payload", msg)
        request_id = payload.get("request_id", "")
        path = payload.get("path", "/ws")

        local_ws_url = self._resolve_local_url(path, scheme="ws")
        try:
            local_ws = await websockets.connect(local_ws_url)
            asyncio.create_task(self._proxy_ws(request_id, local_ws))
        except Exception as e:
            logger.warning(f"Failed to connect local WS: {e}")

    async def _proxy_ws(self, request_id: str, local_ws):
        """Proxy WS messages between tunnel server and local WS."""
        try:
            async for message in local_ws:
                # Forward local → tunnel server.
                await self._ws.send(json.dumps({
                    "type": "ws.message",
                    "request_id": request_id,
                    "payload": {
                        "request_id": request_id,
                        "data": message if isinstance(message, str) else message.decode(),
                        "binary": isinstance(message, bytes),
                    },
                }))
        except Exception:
            pass
        finally:
            await local_ws.close()

    async def _heartbeat(self):
        """Send periodic pings."""
        while self._running and self._ws:
            try:
                await asyncio.sleep(30)
                if self._ws and not self._ws.closed:
                    await self._ws.ping()
            except Exception:
                break

    async def _reconnect(self):
        """Reconnect with exponential backoff."""
        delays = [1, 2, 4, 8, 16]
        for delay in delays:
            await asyncio.sleep(delay)
            try:
                await self.connect()
                return
            except Exception as e:
                logger.warning(f"Reconnect failed: {e}")
        logger.error("Tunnel reconnect failed after all retries")

    async def close(self):
        """Close the tunnel connection."""
        self._running = False
        if self._ws:
            await self._ws.close()
