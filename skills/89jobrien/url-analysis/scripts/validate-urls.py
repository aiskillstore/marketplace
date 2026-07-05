#!/usr/bin/env python3
"""URL validator for url-analysis skill.
Validates URLs and checks HTTP status codes.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests  # type: ignore[import-untyped]
from requests.exceptions import (  # type: ignore[import-untyped]
    RequestException,
    Timeout,
)


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    # URL pattern
    url_pattern = re.compile(
        r"https?://"  # http:// or https://
        r"(?:[-\w.])+"  # domain
        r"(?::[0-9]+)?"  # optional port
        r"(?:/(?:[\w/_.])*)?"  # path
        r"(?:\?(?:[\w&=%.])*)?"  # query string
        r"(?:#(?:[\w.])*)?",  # fragment
        re.IGNORECASE,
    )

    return url_pattern.findall(text)


def validate_url(url: str, timeout: int = 5) -> dict:
    """Validate a single URL."""
    result = {
        "url": url,
        "valid_syntax": False,
        "accessible": False,
        "status_code": None,
        "error": None,
        "redirects_to": None,
    }

    # Check URL syntax
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            result["valid_syntax"] = True
        else:
            result["error"] = "Invalid URL syntax"
            return result
    except Exception as e:
        result["error"] = f"URL parsing error: {e}"
        return result

    # Check if URL is accessible
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        result["accessible"] = True
        result["status_code"] = response.status_code

        # Check for redirects
        if response.history:
            result["redirects_to"] = response.url
            result["redirect_chain_length"] = len(response.history)

    except Timeout:
        result["error"] = "Request timeout"
    except RequestException as e:
        result["error"] = str(e)

    return result


def validate_urls_from_file(file_path: Path) -> dict:
    """Extract and validate URLs from a file."""
    content = file_path.read_text()
    urls = extract_urls(content)

    results = []
    for url in urls:
        validation = validate_url(url)
        results.append(validation)

    return {
        "file": str(file_path),
        "urls_found": len(urls),
        "validations": results,
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate_urls.py <file> [--url <url>]")
        sys.exit(1)

    if "--url" in sys.argv:
        # Validate single URL
        url_index = sys.argv.index("--url")
        if url_index + 1 >= len(sys.argv):
            print("Error: --url requires a URL argument")
            sys.exit(1)
        url = sys.argv[url_index + 1]
        result = validate_url(url)
        print(json.dumps(result, indent=2))
    else:
        # Validate URLs from file
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)

        result = validate_urls_from_file(file_path)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
