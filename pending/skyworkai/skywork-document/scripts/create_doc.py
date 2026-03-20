#!/usr/bin/env python3
"""
Create a document via the Skywork Office Doc SSE API.

Supports passing reference files via --files parameter (JSON format from parse_file.py).
The server will automatically retrieve parsed content using file_id.

Usage:
    # Without reference files
    python create_doc.py --title "My Report" --content "Write a comprehensive report..."

    # With reference files (from parse_file.py output)
    python create_doc.py --title "Analysis Report" \
        --content "Based on the uploaded files, create an analysis..." \
        --files '[{"file_id":"2032146192467681280","filename":"report.pdf","url":""}]'

Environment variables:
    SKYWORK_GATEWAY_URL - Base URL
    SKYBOT_TOKEN       - Auth token (takes priority)
"""

import argparse
import json
import os
import sys
import uuid
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import URLError, HTTPError

from skywork_auth import get_skywork_token


def parse_sse_events(response):
    """Parse SSE events from an HTTP response stream."""
    import io
    # Wrap the binary response in a TextIOWrapper so multi-byte UTF-8
    # characters (e.g. Chinese) are decoded correctly as whole characters.
    reader = io.TextIOWrapper(response, encoding="utf-8", errors="replace")
    buffer = ""
    for char in iter(lambda: reader.read(1), ""):
        buffer += char
        while "\n\n" in buffer:
            event_block, buffer = buffer.split("\n\n", 1)
            event_type = None
            event_data = None
            for line in event_block.strip().split("\n"):
                if line.startswith("event: "):
                    event_type = line[7:].strip()
                elif line.startswith("data: "):
                    event_data = line[6:]
            if event_data:
                try:
                    data = json.loads(event_data)
                    yield event_type or data.get("type", "message"), data
                except json.JSONDecodeError:
                    pass


def create_doc(base_url, token, title, content, input_files=None, language=None, fmt="html"):
    """Call the doc create SSE endpoint and stream progress."""
    url = f"{base_url}/api/sse/doc/create"
    request_id = str(uuid.uuid4())

    payload = {
        "type": "create_doc",
        "request_id": request_id,
        "title": title,
        "content": content,
        "format": fmt,
    }

    if input_files:
        payload["input_files"] = input_files

    if language:
        payload["options"] = {"language": language}
    payload["source_platform"] = "skyclaw" if os.environ.get("POD_TYPE", "") == "skyclaw" else ""

    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "request_id": request_id}
    if token:
        headers["token"] = token

    req = Request(url, data=body, headers=headers, method="POST")

    print(f"[doc] Creating document: \"{title}\"")
    print(f"[doc] Request ID: {request_id}")
    print(f"[doc] Server: {base_url}")
    if input_files:
        print(f"[doc] Reference files: {len(input_files)}")
    print()

    try:
        resp = urlopen(req, timeout=600)
    except HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')
        print(f"[error] HTTP {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"[error] Cannot reach server: {e.reason}", file=sys.stderr)
        sys.exit(1)

    result = None
    for event_type, data in parse_sse_events(resp):
        if event_type == "progress":
            stage = data.get("stage", "")
            pct = data.get("percentage", 0)
            msg = data.get("message", "")
            bar = "=" * int(pct / 5) + ">" + " " * (20 - int(pct / 5))
            print(f"[{bar}] {pct:5.1f}%  {stage}: {msg}",flush=True)
        elif event_type == "content_chunk":
            chunk = data.get("chunk", "")
            print(f"{chunk}", end="", flush=True)
        elif event_type == "deepsearch":
            chunk = data.get("chunk", "")
            print(f"{chunk}", end="", flush=True)
        elif event_type == "success":
            print()  # newline after progress bar
            result = data
            file_id = data.get("file_id", "?")
            file_path = data.get("file_path", "?")
            file_url = data.get("file_url", "")
            exec_time = data.get("execution_time", 0)
            metadata = data.get("metadata", {})
            print()
            print(f"[success] Document created!")
            print(f"  File ID:   {file_id}")
            print(f"  Path:      {file_path}")
            if file_url:
                print(f"  URL:       {file_url}")
            print(f"  Time:      {exec_time:.1f}s")
            if metadata.get("headings"):
                print(f"  Sections:  {len(metadata['headings'])} top-level headings")
        elif event_type == "error":
            print()
            code = data.get("code", "UNKNOWN")
            msg = data.get("message", "Unknown error")
            print(f"\n[error] {code}: {msg}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"[debug] Event #{event_type}: {data}\n", flush=True)

    return result


def download_file(url, dest_dir=None):
    """Download a file from url to dest_dir and return the local file path."""
    if dest_dir is None:
        dest_dir = os.getcwd()

    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) or "document"
    local_path = os.path.join(dest_dir, filename)

    # Avoid overwriting existing files
    if os.path.exists(local_path):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(local_path):
            local_path = os.path.join(dest_dir, f"{base}_{counter}{ext}")
            counter += 1

    # URL-encode non-ASCII characters in the path (e.g. Chinese filenames)
    encoded_path = quote(parsed.path, safe="/")
    encoded_url = parsed._replace(path=encoded_path).geturl()

    print(f"[download] Saving to: {local_path}")
    try:
        urlretrieve(encoded_url, local_path)
        size = os.path.getsize(local_path)
        print(f"[download] Done ({size:,} bytes)")
    except Exception as e:
        print(f"[download] Failed: {e}", file=sys.stderr)
        return ""
    return local_path


def main():
    parser = argparse.ArgumentParser(description="Create a document via Skywork Office Doc API")
    parser.add_argument("--title", required=True, help="Document title")
    parser.add_argument("--content", required=True, help="Content description / creative prompt")
    parser.add_argument("--language", default=None, help="Output language (English, 简体中文, 繁體中文, 日本語, 한국어, Français, Deutsch, Español, etc.)")
    parser.add_argument("--format", default="", dest="fmt", choices=["docx", "pdf", "html", "md", ""], help="default to empty and the server will determine the format")
    parser.add_argument(
        "--files", default=None,
        help='Reference files JSON from parse_file.py, e.g.: \'[{"file_id":"xxx","filename":"a.pdf","url":""}]\'',
    )
    args = parser.parse_args()

    base_url = os.environ.get("SKYWORK_GATEWAY_URL", "https://api-tools.skywork.ai/theme-gateway").rstrip("/")

    # Get token
    token = get_skywork_token()

    # Parse input_files if provided
    input_files = None
    if args.files:
        try:
            input_files = json.loads(args.files)
            if not isinstance(input_files, list):
                print(f"[error] --files must be a JSON array", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[error] --files JSON parse error: {e}", file=sys.stderr)
            sys.exit(1)

    result = create_doc(
        base_url=base_url,
        token=token,
        title=args.title,
        content=args.content,
        input_files=input_files,
        language=args.language,
        fmt=args.fmt,
    )

    if result:
        # Download the generated file locally and populate file_path
        file_url = result.get("file_url", "")
        if file_url:
            local_path = download_file(file_url)
            result["file_path"] = local_path

        # Print the full result as JSON for programmatic consumption
        print()
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
