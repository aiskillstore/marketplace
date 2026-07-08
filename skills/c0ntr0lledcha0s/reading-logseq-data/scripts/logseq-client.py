#!/usr/bin/env python3
"""
Logseq Client Library

Unified client for reading data from Logseq graphs via HTTP API or CLI.
Supports auto-detection of available backends.

Usage:
    from logseq_client import LogseqClient

    client = LogseqClient()
    page = client.get_page("My Page")
    results = client.datalog_query("[:find ?title :where [?p :block/title ?title]]")
"""

import json
import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional, Union


class LogseqError(Exception):
    """Base exception for Logseq operations."""
    pass


class ConnectionError(LogseqError):
    """Cannot connect to Logseq."""
    pass


class AuthError(LogseqError):
    """Authentication failed."""
    pass


class NotFoundError(LogseqError):
    """Resource not found."""
    pass


class QueryError(LogseqError):
    """Query execution failed."""
    pass


class LogseqClient:
    """
    Unified client for Logseq operations.

    Supports HTTP API and CLI backends with automatic fallback.
    """

    # Exception classes as attributes for easy access
    Error = LogseqError
    ConnectionError = ConnectionError
    AuthError = AuthError
    NotFoundError = NotFoundError
    QueryError = QueryError

    def __init__(
        self,
        backend: Optional[str] = None,
        url: Optional[str] = None,
        token: Optional[str] = None,
        graph_path: Optional[str] = None
    ):
        """
        Initialize the Logseq client.

        Args:
            backend: Force specific backend ("http", "cli", or None for auto)
            url: HTTP API URL (default: from env or http://127.0.0.1:12315)
            token: API token (default: from env LOGSEQ_API_TOKEN)
            graph_path: Path to graph for CLI backend
        """
        self.url = url or os.environ.get("LOGSEQ_API_URL", "http://127.0.0.1:12315")
        self.token = token or os.environ.get("LOGSEQ_API_TOKEN", "")
        self.graph_path = graph_path or os.environ.get("LOGSEQ_GRAPH_PATH", "")

        # Load config if available
        self._load_config()

        # Detect backend
        if backend:
            self.backend = backend
        else:
            self.backend = self._detect_backend()

    def _load_config(self):
        """Load configuration from env.json if available."""
        config_path = Path.cwd() / ".claude" / "logseq-expert" / "env.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)

                # HTTP settings
                http_config = config.get("http", {})
                if not self.url or self.url == "http://127.0.0.1:12315":
                    self.url = http_config.get("url", self.url)
                if not self.token:
                    token = http_config.get("token", "")
                    if token.startswith("${") and token.endswith("}"):
                        # Environment variable reference
                        var_name = token[2:-1]
                        self.token = os.environ.get(var_name, "")
                    else:
                        self.token = token

                # CLI settings
                cli_config = config.get("cli", {})
                if not self.graph_path:
                    self.graph_path = cli_config.get("graphPath", "")

            except Exception:
                pass  # Config loading is optional

    def _detect_backend(self) -> str:
        """Auto-detect the best available backend."""
        # Try HTTP first
        if self._test_http():
            return "http"

        # Fall back to CLI
        if self._test_cli():
            return "cli"

        raise ConnectionError("No Logseq backend available. Start Logseq or install CLI.")

    def _test_http(self) -> bool:
        """Test if HTTP API is available."""
        try:
            import socket
            host = self.url.replace("http://", "").replace("https://", "").split("/")[0]
            host, port = host.split(":") if ":" in host else (host, "12315")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _test_cli(self) -> bool:
        """Test if CLI is available."""
        try:
            result = subprocess.run(
                ["logseq", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def _http_call(self, method: str, args: list = None) -> Any:
        """Make HTTP API call."""
        if not self.token:
            raise AuthError("No API token configured")

        try:
            req = urllib.request.Request(
                f"{self.url}/api",
                data=json.dumps({"method": method, "args": args or []}).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.token}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

                if "error" in data:
                    raise QueryError(data["error"])

                return data.get("result")

        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise AuthError("Invalid token")
            raise ConnectionError(f"HTTP error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Connection failed: {e.reason}")

    def _cli_query(self, query: str, params: list = None) -> Any:
        """Execute query via CLI."""
        cmd = ["logseq", "query", query]

        if self.graph_path:
            cmd.extend(["--graph", self.graph_path])
        elif self.token:
            cmd.extend(["--in-app", "-a", self.token])

        cmd.extend(["--format", "json"])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise QueryError(f"CLI error: {result.stderr}")

            return json.loads(result.stdout)

        except subprocess.TimeoutExpired:
            raise QueryError("Query timed out")
        except json.JSONDecodeError:
            raise QueryError("Invalid response from CLI")
        except FileNotFoundError:
            raise ConnectionError("Logseq CLI not found")

    # ============== Read Operations ==============

    def get_graph_info(self) -> dict:
        """Get information about the current graph."""
        if self.backend == "http":
            return self._http_call("logseq.App.getCurrentGraph")
        else:
            # CLI doesn't have direct equivalent
            return {"path": self.graph_path, "backend": "cli"}

    def get_page(self, title: str, include_children: bool = True) -> Optional[dict]:
        """
        Get a page by title.

        Args:
            title: Page title
            include_children: Include child blocks

        Returns:
            Page data or None if not found
        """
        if self.backend == "http":
            page = self._http_call("logseq.Editor.getPage", [title])
            if page and include_children:
                page["blocks"] = self._http_call(
                    "logseq.Editor.getPageBlocksTree",
                    [title]
                )
            return page
        else:
            # Use query for CLI
            result = self._cli_query(f'''
                [:find (pull ?p [*])
                 :in $ ?title
                 :where [?p :block/title ?title]]
            ''')
            if result and len(result) > 0:
                return result[0][0] if isinstance(result[0], list) else result[0]
            return None

    def get_block(self, uuid: str, include_children: bool = True) -> Optional[dict]:
        """
        Get a block by UUID.

        Args:
            uuid: Block UUID
            include_children: Include child blocks

        Returns:
            Block data or None if not found
        """
        if self.backend == "http":
            return self._http_call(
                "logseq.Editor.getBlock",
                [uuid, {"includeChildren": include_children}]
            )
        else:
            result = self._cli_query(f'''
                [:find (pull ?b [*])
                 :in $ ?uuid
                 :where [?b :block/uuid ?uuid]]
            ''')
            if result and len(result) > 0:
                return result[0][0] if isinstance(result[0], list) else result[0]
            return None

    def list_pages(self, limit: int = None) -> list:
        """
        List all pages in the graph.

        Args:
            limit: Maximum number of pages to return

        Returns:
            List of page summaries
        """
        query = '''
            [:find (pull ?p [:block/title :block/uuid])
             :where
             [?p :block/tags ?t]
             [?t :db/ident :logseq.class/Page]]
        '''

        results = self.datalog_query(query)

        # Flatten results
        pages = [r[0] if isinstance(r, list) else r for r in results]

        if limit:
            pages = pages[:limit]

        return pages

    def search(self, query_text: str, limit: int = 50) -> list:
        """
        Search for blocks containing text.

        Args:
            query_text: Text to search for
            limit: Maximum results

        Returns:
            List of matching blocks
        """
        if self.backend == "http":
            # Use search API if available
            try:
                return self._http_call("logseq.App.search", [query_text])[:limit]
            except Exception:
                pass

        # Fallback to query (less efficient but works)
        # Note: This is a simple substring match, not full-text search
        query = f'''
            [:find (pull ?b [:block/title :block/uuid {{:block/page [:block/title]}}])
             :where
             [?b :block/title ?title]
             [(clojure.string/includes? ?title "{query_text}")]]
        '''
        results = self.datalog_query(query)
        return [r[0] if isinstance(r, list) else r for r in results][:limit]

    def datalog_query(self, query: str, params: list = None) -> list:
        """
        Execute a Datalog query.

        Args:
            query: Datalog query string
            params: Optional query parameters

        Returns:
            Query results
        """
        if self.backend == "http":
            args = [query]
            if params:
                args.append(params)
            return self._http_call("logseq.DB.datascriptQuery", args) or []
        else:
            return self._cli_query(query, params) or []

    def get_backlinks(self, title: str) -> list:
        """
        Get all blocks that reference a page.

        Args:
            title: Page title

        Returns:
            List of referencing blocks
        """
        query = '''
            [:find (pull ?b [:block/title :block/uuid {:block/page [:block/title]}])
             :in $ ?page-title
             :where
             [?p :block/title ?page-title]
             [?b :block/refs ?p]]
        '''
        results = self.datalog_query(query, [title])
        return [r[0] if isinstance(r, list) else r for r in results]

    def get_page_properties(self, title: str) -> dict:
        """
        Get properties of a page.

        Args:
            title: Page title

        Returns:
            Dictionary of properties
        """
        if self.backend == "http":
            page = self._http_call("logseq.Editor.getPage", [title])
            return page.get("properties", {}) if page else {}
        else:
            page = self.get_page(title, include_children=False)
            # Extract properties from page data
            if page:
                props = {}
                for key, value in page.items():
                    if key.startswith("user.property/") or key.startswith(":user.property/"):
                        prop_name = key.split("/")[-1]
                        props[prop_name] = value
                return props
            return {}

    def get_block_properties(self, uuid: str) -> dict:
        """
        Get properties of a block.

        Args:
            uuid: Block UUID

        Returns:
            Dictionary of properties
        """
        if self.backend == "http":
            return self._http_call("logseq.Editor.getBlockProperties", [uuid]) or {}
        else:
            block = self.get_block(uuid, include_children=False)
            if block:
                props = {}
                for key, value in block.items():
                    if "property" in key.lower():
                        prop_name = key.split("/")[-1]
                        props[prop_name] = value
                return props
            return {}


# Convenience function for quick queries
def query(datalog_query: str, params: list = None) -> list:
    """
    Execute a quick Datalog query.

    Args:
        datalog_query: The Datalog query string
        params: Optional parameters

    Returns:
        Query results
    """
    client = LogseqClient()
    return client.datalog_query(datalog_query, params)


if __name__ == "__main__":
    # Quick test
    import sys

    client = LogseqClient()
    print(f"Backend: {client.backend}")

    if len(sys.argv) > 1:
        # Run query from command line
        result = client.datalog_query(sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        # Show graph info
        try:
            info = client.get_graph_info()
            print(f"Graph: {info}")
        except Exception as e:
            print(f"Error: {e}")
