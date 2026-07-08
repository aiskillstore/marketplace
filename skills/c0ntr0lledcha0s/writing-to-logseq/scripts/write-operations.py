#!/usr/bin/env python3
"""
Logseq Write Operations Library

Provides CRUD operations for writing data to Logseq graphs via HTTP API.

Usage:
    from write_operations import LogseqWriter

    writer = LogseqWriter()
    page = writer.create_page("My Page")
    block = writer.create_block(page["uuid"], "Content")
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union


class WriteError(Exception):
    """Base exception for write operations."""
    pass


class ConnectionError(WriteError):
    """Cannot connect to Logseq."""
    pass


class AuthError(WriteError):
    """Authentication failed."""
    pass


class DuplicateError(WriteError):
    """Resource already exists."""
    pass


class NotFoundError(WriteError):
    """Resource not found."""
    pass


class ValidationError(WriteError):
    """Invalid data provided."""
    pass


class LogseqWriter:
    """
    Write operations for Logseq graphs.

    Requires HTTP API to be enabled in Logseq.
    """

    # Exception classes as attributes
    Error = WriteError
    ConnectionError = ConnectionError
    AuthError = AuthError
    DuplicateError = DuplicateError
    NotFoundError = NotFoundError
    ValidationError = ValidationError

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Initialize the writer.

        Args:
            url: HTTP API URL (default: from env or http://127.0.0.1:12315)
            token: API token (default: from env LOGSEQ_API_TOKEN)
        """
        self.url = url or os.environ.get("LOGSEQ_API_URL", "http://127.0.0.1:12315")
        self.token = token or os.environ.get("LOGSEQ_API_TOKEN", "")

        # Load from config if available
        self._load_config()

        if not self.token:
            raise AuthError("No API token configured. Set LOGSEQ_API_TOKEN or pass token parameter.")

    def _load_config(self):
        """Load configuration from env.json if available."""
        config_path = Path.cwd() / ".claude" / "logseq-expert" / "env.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)

                http_config = config.get("http", {})
                if not self.url or self.url == "http://127.0.0.1:12315":
                    self.url = http_config.get("url", self.url)
                if not self.token:
                    token = http_config.get("token", "")
                    if token.startswith("${") and token.endswith("}"):
                        var_name = token[2:-1]
                        self.token = os.environ.get(var_name, "")
                    else:
                        self.token = token
            except Exception:
                pass

    def _call(self, method: str, args: list = None) -> Any:
        """Make HTTP API call."""
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
                    raise WriteError(data["error"])

                return data.get("result")

        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise AuthError("Invalid token")
            raise ConnectionError(f"HTTP error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Connection failed: {e.reason}")

    # ============== Page Operations ==============

    def create_page(
        self,
        title: str,
        content: Optional[str] = None,
        properties: Optional[dict] = None,
        create_first_block: bool = True
    ) -> dict:
        """
        Create a new page.

        Args:
            title: Page title
            content: Optional initial content for first block
            properties: Optional page properties
            create_first_block: Whether to create an empty first block

        Returns:
            Created page data

        Raises:
            DuplicateError: If page already exists
        """
        # Check if page exists
        existing = self._call("logseq.Editor.getPage", [title])
        if existing:
            raise DuplicateError(f"Page '{title}' already exists")

        # Create page
        options = {"createFirstBlock": create_first_block}
        page = self._call("logseq.Editor.createPage", [title, properties or {}, options])

        # Add initial content if provided
        if content and page:
            blocks = self._call("logseq.Editor.getPageBlocksTree", [title])
            if blocks and len(blocks) > 0:
                self._call("logseq.Editor.updateBlock", [blocks[0]["uuid"], content])

        return page

    def get_or_create_page(self, title: str, properties: Optional[dict] = None) -> dict:
        """
        Get existing page or create if it doesn't exist.

        Args:
            title: Page title
            properties: Properties for new page

        Returns:
            Page data
        """
        page = self._call("logseq.Editor.getPage", [title])
        if page:
            return page
        return self.create_page(title, properties=properties)

    def delete_page(self, title: str) -> bool:
        """
        Delete a page.

        Args:
            title: Page title

        Returns:
            True if deleted
        """
        page = self._call("logseq.Editor.getPage", [title])
        if not page:
            raise NotFoundError(f"Page '{title}' not found")

        self._call("logseq.Editor.deletePage", [title])
        return True

    # ============== Block Operations ==============

    def create_block(
        self,
        parent: str,
        content: str,
        properties: Optional[dict] = None,
        sibling: bool = False
    ) -> dict:
        """
        Create a new block.

        Args:
            parent: Parent block UUID or page title
            content: Block content
            properties: Optional block properties
            sibling: If True, create as sibling; if False, as child

        Returns:
            Created block data
        """
        # Resolve parent
        parent_uuid = self._resolve_parent(parent)

        # Insert block
        options = {"sibling": sibling}
        if properties:
            options["properties"] = properties

        return self._call("logseq.Editor.insertBlock", [parent_uuid, content, options])

    def update_block(self, uuid: str, content: str) -> dict:
        """
        Update block content.

        Args:
            uuid: Block UUID
            content: New content

        Returns:
            Updated block data
        """
        self._call("logseq.Editor.updateBlock", [uuid, content])
        return self._call("logseq.Editor.getBlock", [uuid])

    def delete_block(self, uuid: str) -> bool:
        """
        Delete a block.

        Args:
            uuid: Block UUID

        Returns:
            True if deleted
        """
        block = self._call("logseq.Editor.getBlock", [uuid])
        if not block:
            raise NotFoundError(f"Block '{uuid}' not found")

        self._call("logseq.Editor.removeBlock", [uuid])
        return True

    def append_to_page(self, title: str, content: str) -> dict:
        """
        Append content to the end of a page.

        Args:
            title: Page title
            content: Content to append

        Returns:
            Created block data
        """
        page = self._call("logseq.Editor.getPage", [title])
        if not page:
            # Create page if it doesn't exist
            page = self.create_page(title)

        # Get last block of page
        blocks = self._call("logseq.Editor.getPageBlocksTree", [title])

        if blocks and len(blocks) > 0:
            # Insert after last block
            last_block = blocks[-1]
            return self._call("logseq.Editor.insertBlock", [
                last_block["uuid"],
                content,
                {"sibling": True}
            ])
        else:
            # Page is empty, create first block
            return self._call("logseq.Editor.insertBlock", [
                page["uuid"],
                content,
                {"sibling": False}
            ])

    def _resolve_parent(self, parent: str) -> str:
        """Resolve parent to UUID."""
        # If it looks like a UUID, use it directly
        if len(parent) == 36 and parent.count("-") == 4:
            return parent

        # Try as page title
        page = self._call("logseq.Editor.getPage", [parent])
        if page:
            # Get first block of page
            blocks = self._call("logseq.Editor.getPageBlocksTree", [parent])
            if blocks and len(blocks) > 0:
                return blocks[0]["uuid"]
            return page["uuid"]

        raise NotFoundError(f"Cannot resolve parent: {parent}")

    # ============== Property Operations ==============

    def set_property(
        self,
        uuid: str,
        key: str,
        value: Any,
        property_type: Optional[str] = None
    ) -> bool:
        """
        Set a property on a block.

        Args:
            uuid: Block UUID
            key: Property name
            value: Property value
            property_type: Optional type hint (number, date, checkbox, etc.)

        Returns:
            True if set
        """
        # Convert value based on type if specified
        if property_type == "number":
            value = float(value) if "." in str(value) else int(value)
        elif property_type == "checkbox":
            value = bool(value)
        elif property_type == "date" and isinstance(value, str):
            # Keep as string for date linking
            pass

        self._call("logseq.Editor.upsertBlockProperty", [uuid, key, value])
        return True

    def set_properties(self, uuid: str, properties: dict) -> bool:
        """
        Set multiple properties on a block.

        Args:
            uuid: Block UUID
            properties: Dictionary of property key-value pairs

        Returns:
            True if all set
        """
        for key, value in properties.items():
            self.set_property(uuid, key, value)
        return True

    def remove_property(self, uuid: str, key: str) -> bool:
        """
        Remove a property from a block.

        Args:
            uuid: Block UUID
            key: Property name

        Returns:
            True if removed
        """
        self._call("logseq.Editor.removeBlockProperty", [uuid, key])
        return True

    # ============== Tag Operations ==============

    def add_tag(self, uuid: str, tag: str) -> bool:
        """
        Add a tag to a block.

        Args:
            uuid: Block UUID
            tag: Tag name (without #)

        Returns:
            True if added
        """
        # Get current block
        block = self._call("logseq.Editor.getBlock", [uuid])
        if not block:
            raise NotFoundError(f"Block '{uuid}' not found")

        # Get current content and add tag if not present
        content = block.get("content", "")
        tag_text = f"#{tag}"

        if tag_text not in content:
            new_content = f"{content} {tag_text}".strip()
            self._call("logseq.Editor.updateBlock", [uuid, new_content])

        return True

    def add_tags(self, uuid: str, tags: list) -> bool:
        """
        Add multiple tags to a block.

        Args:
            uuid: Block UUID
            tags: List of tag names

        Returns:
            True if added
        """
        for tag in tags:
            self.add_tag(uuid, tag)
        return True

    def remove_tag(self, uuid: str, tag: str) -> bool:
        """
        Remove a tag from a block.

        Args:
            uuid: Block UUID
            tag: Tag name

        Returns:
            True if removed
        """
        block = self._call("logseq.Editor.getBlock", [uuid])
        if not block:
            raise NotFoundError(f"Block '{uuid}' not found")

        content = block.get("content", "")
        tag_text = f"#{tag}"

        if tag_text in content:
            new_content = content.replace(tag_text, "").strip()
            new_content = " ".join(new_content.split())  # Clean up whitespace
            self._call("logseq.Editor.updateBlock", [uuid, new_content])

        return True

    # ============== Utility Operations ==============

    def sync_notes(self, title: str, notes: str, page_prefix: str = "Claude Notes") -> dict:
        """
        Sync notes to a Logseq page with timestamp.

        Args:
            title: Note title
            notes: Note content
            page_prefix: Prefix for page name

        Returns:
            Block data
        """
        page_title = f"{page_prefix}/{title}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        content = f"""## {timestamp}

{notes}

---"""

        return self.append_to_page(page_title, content)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python write-operations.py <command> [args...]")
        print("Commands:")
        print("  create-page <title>")
        print("  create-block <parent> <content>")
        print("  append <page-title> <content>")
        sys.exit(1)

    writer = LogseqWriter()
    command = sys.argv[1]

    try:
        if command == "create-page" and len(sys.argv) >= 3:
            result = writer.create_page(sys.argv[2])
            print(json.dumps(result, indent=2))

        elif command == "create-block" and len(sys.argv) >= 4:
            result = writer.create_block(sys.argv[2], sys.argv[3])
            print(json.dumps(result, indent=2))

        elif command == "append" and len(sys.argv) >= 4:
            result = writer.append_to_page(sys.argv[2], sys.argv[3])
            print(json.dumps(result, indent=2))

        else:
            print(f"Unknown command or missing arguments: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
