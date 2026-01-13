#!/usr/bin/env python3
"""
Playwright Undetected Server
=============================
Background server that keeps browser session alive.

Usage:
    python server.py start           # Start server (background)
    python server.py stop            # Stop server
    python server.py call <json>     # Call tool
    python server.py status          # Check status
"""

import asyncio
import json
import sys
import os
import socket
import signal
from pathlib import Path

PORT = 9222
SOCKET_FILE = Path(__file__).parent / ".server.sock"
PID_FILE = Path(__file__).parent / ".server.pid"

# Patchright
try:
    from patchright.async_api import async_playwright
except ImportError:
    print("Error: pip install patchright")
    sys.exit(1)


class BrowserServer:
    def __init__(self):
        self.pw = None
        self.browser = None
        self.page = None
        self.server = None
        self.running = False

    async def start_browser(self, headless=False):
        if self.browser:
            return {"status": "already_running"}
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(
            headless=headless,
            channel='chrome',
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = await self.browser.new_page()
        return {"status": "success", "message": "Browser launched"}

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
        if self.pw:
            await self.pw.stop()
            self.pw = None
        return {"status": "success"}

    async def navigate(self, url):
        if not self.page:
            await self.start_browser()
        await self.page.goto(url, wait_until='networkidle', timeout=30000)
        return {"status": "success", "url": self.page.url, "title": await self.page.title()}

    async def screenshot(self, path="screenshot.png", full_page=False):
        if not self.page:
            return {"status": "error", "message": "No page open"}
        path = str(Path(path).absolute())
        await self.page.screenshot(path=path, full_page=full_page)
        return {"status": "success", "path": path}

    async def click(self, selector):
        if not self.page:
            return {"status": "error", "message": "No page open"}
        await self.page.click(selector)
        return {"status": "success"}

    async def type_text(self, selector, text):
        if not self.page:
            return {"status": "error", "message": "No page open"}
        await self.page.fill(selector, text)
        return {"status": "success"}

    async def get_text(self, selector):
        if not self.page:
            return {"status": "error", "message": "No page open"}
        return {"status": "success", "text": await self.page.text_content(selector)}

    async def get_url(self):
        if not self.page:
            return {"status": "error", "message": "No page open"}
        return {"status": "success", "url": self.page.url}

    async def get_title(self):
        if not self.page:
            return {"status": "error", "message": "No page open"}
        return {"status": "success", "title": await self.page.title()}

    async def evaluate(self, script):
        if not self.page:
            return {"status": "error", "message": "No page open"}
        result = await self.page.evaluate(script)
        return {"status": "success", "result": result}

    async def handle_call(self, data):
        tool = data.get("tool")
        args = data.get("args", {})

        handlers = {
            "launch": lambda: self.start_browser(args.get("headless", False)),
            "close": self.close_browser,
            "navigate": lambda: self.navigate(args["url"]),
            "screenshot": lambda: self.screenshot(args.get("path", "screenshot.png"), args.get("full_page", False)),
            "click": lambda: self.click(args["selector"]),
            "type": lambda: self.type_text(args["selector"], args["text"]),
            "get_text": lambda: self.get_text(args["selector"]),
            "get_url": self.get_url,
            "get_title": self.get_title,
            "evaluate": lambda: self.evaluate(args["script"]),
        }

        if tool not in handlers:
            return {"status": "error", "message": f"Unknown tool: {tool}"}

        try:
            return await handlers[tool]()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def handle_client(self, reader, writer):
        try:
            data = await reader.read(65536)
            request = json.loads(data.decode())

            if request.get("cmd") == "stop":
                self.running = False
                response = {"status": "success", "message": "Server stopping"}
            elif request.get("cmd") == "status":
                response = {"status": "success", "browser": self.browser is not None, "page": self.page is not None}
            else:
                response = await self.handle_call(request)

            writer.write(json.dumps(response).encode())
            await writer.drain()
        except Exception as e:
            writer.write(json.dumps({"status": "error", "message": str(e)}).encode())
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async def run_server(self):
        self.running = True
        self.server = await asyncio.start_server(self.handle_client, '127.0.0.1', PORT)
        PID_FILE.write_text(str(os.getpid()))
        print(f"Server running on port {PORT}")

        while self.running:
            await asyncio.sleep(0.1)

        self.server.close()
        await self.server.wait_closed()
        await self.close_browser()
        PID_FILE.unlink(missing_ok=True)
        print("Server stopped")


def send_command(data):
    """Send command to server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', PORT))
        sock.send(json.dumps(data).encode())
        response = sock.recv(65536)
        sock.close()
        return json.loads(response.decode())
    except ConnectionRefusedError:
        return {"status": "error", "message": "Server not running. Start with: python server.py start"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python server.py [start|stop|status|call <json>]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "start":
        # Check if already running
        if PID_FILE.exists():
            pid = int(PID_FILE.read_text())
            try:
                os.kill(pid, 0)
                print(f"Server already running (PID {pid})")
                sys.exit(0)
            except OSError:
                PID_FILE.unlink()

        server = BrowserServer()
        asyncio.run(server.run_server())

    elif cmd == "stop":
        result = send_command({"cmd": "stop"})
        print(json.dumps(result, indent=2))

    elif cmd == "status":
        result = send_command({"cmd": "status"})
        print(json.dumps(result, indent=2))

    elif cmd == "call":
        if len(sys.argv) < 3:
            print("Usage: python server.py call '{\"tool\": \"navigate\", \"args\": {\"url\": \"...\"}}'")
            sys.exit(1)
        data = json.loads(sys.argv[2])
        result = send_command(data)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
