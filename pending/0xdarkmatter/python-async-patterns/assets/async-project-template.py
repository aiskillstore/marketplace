#!/usr/bin/env python3
"""
Async Python Project Template

Production-ready async application structure with:
- Proper session management
- Graceful shutdown
- Structured concurrency
- Error handling
- Logging
"""

import asyncio
import logging
import signal
from contextlib import asynccontextmanager
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AsyncApp:
    """Main application class with lifecycle management."""

    def __init__(self):
        self.session: aiohttp.ClientSession | None = None
        self.running = False
        self._tasks: set[asyncio.Task] = set()

    async def start(self):
        """Initialize resources."""
        logger.info("Starting application...")
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100),
        )
        self.running = True
        logger.info("Application started")

    async def stop(self):
        """Cleanup resources."""
        logger.info("Stopping application...")
        self.running = False

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        # Close session
        if self.session:
            await self.session.close()

        logger.info("Application stopped")

    def create_task(self, coro) -> asyncio.Task:
        """Create a tracked background task."""
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def fetch(self, url: str) -> dict[str, Any] | None:
        """Fetch URL with error handling."""
        if not self.session:
            raise RuntimeError("App not started")

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            return None

    async def fetch_many(
        self,
        urls: list[str],
        concurrency: int = 10
    ) -> list[dict[str, Any] | None]:
        """Fetch multiple URLs with bounded concurrency."""
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_fetch(url: str):
            async with semaphore:
                return await self.fetch(url)

        return await asyncio.gather(*[bounded_fetch(url) for url in urls])


@asynccontextmanager
async def create_app():
    """Context manager for app lifecycle."""
    app = AsyncApp()
    try:
        await app.start()
        yield app
    finally:
        await app.stop()


async def main():
    """Main entry point."""
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Received shutdown signal")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    async with create_app() as app:
        # Example: Fetch some URLs
        urls = [
            "https://httpbin.org/json",
            "https://httpbin.org/uuid",
        ]

        results = await app.fetch_many(urls)
        for url, result in zip(urls, results):
            logger.info(f"{url}: {result}")

        # Keep running until shutdown signal
        # await stop_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
