#!/usr/bin/env python3
"""
Parse a reference file via the Skywork Office file/parse SSE endpoint.

Uploads the file, triggers server-side analysis (OCR, text extraction),
polls until complete, and returns the parsed content.

Usage:
    python parse_file.py /path/to/document.pdf [--output parsed_content.txt]

Environment variables:
    SKYWORK_OFFICE_URL   - Base URL (default: https://api-tools.skywork.ai/theme-gateway)
    SKYWORK_OFFICE_TOKEN - Auth token (optional for local dev)
"""

import argparse
import io
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from config import SKYWORK_OFFICE_URL

from skywork_auth import get_skywork_token


def build_multipart_body(file_path: str):
    """Build a multipart/form-data request body."""
    boundary = f"----FormBoundary{uuid.uuid4().hex[:16]}"
    body = io.BytesIO()
    file_name = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    body.write(f"--{boundary}\r\n".encode())
    body.write(f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode())
    body.write(f"Content-Type: {mime_type}\r\n\r\n".encode())
    with open(file_path, "rb") as f:
        body.write(f.read())
    body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())

    return body.getvalue(), f"multipart/form-data; boundary={boundary}"


def parse_sse_events(response):
    """Parse SSE events from an HTTP response stream."""
    cur_event = None
    cur_data = None
    for line_bytes in response:
        line = line_bytes.decode("utf-8", errors="replace").rstrip("\r\n")
        if line == "":
            if cur_event is not None and cur_data is not None:
                try:
                    data = json.loads(cur_data)
                    yield cur_event, data
                except json.JSONDecodeError:
                    pass
            cur_event = None
            cur_data = None
        elif line.startswith("event: "):
            cur_event = line[7:].strip()
        elif line.startswith("data: "):
            cur_data = line[6:]
    if cur_event is not None and cur_data is not None:
        try:
            data = json.loads(cur_data)
            yield cur_event, data
        except json.JSONDecodeError:
            pass


def parse_file(base_url: str, token: str, file_path: str) -> dict:
    """Upload and parse a file, streaming progress. Returns parsed metadata."""
    url = f"{base_url}/api/sse/file/parse"
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    print(f"[parse] File: {file_name} ({file_size:,} bytes)")
    print(f"[parse] Server: {base_url}")
    print()

    body, content_type = build_multipart_body(file_path)
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", content_type)
    req.add_header("Token", token)

    try:
        resp = urlopen(req, timeout=300)
    except HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')
        print(f"[error] HTTP {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"[error] Cannot reach server: {e.reason}", file=sys.stderr)
        sys.exit(1)

    result = None
    event_count = 0
    for event_type, data in parse_sse_events(resp):
        event_count += 1
        print(f"[debug] Event #{event_count}: {event_type}\n", flush=True)
        if event_type == "progress":
            stage = data.get("stage", "")
            pct = data.get("percentage", 0)
            msg = data.get("message", "")
            bar = "=" * int(pct / 5) + ">" + " " * (20 - int(pct / 5))
            print(f"\r[{bar}] {pct:5.1f}%  {msg}", end="", flush=True)
        elif event_type == "success":
            print()  # newline after progress bar
            result = data
            metadata = data.get("metadata", {})
            exec_time = data.get("execution_time", 0)
            print()
            print(f"[success] File parsed!")
            print(f"  File ID:    {data.get('file_id', '?')}")
            print(f"  File NAME:    {metadata.get('file_name', '')}")
            print(f"  File URL:    {metadata.get('file_url', '')}")
            print(f"  Title:      {metadata.get('parsed_title', '(none)')}")
            print(f"  Summary:    {metadata.get('summary', '(none)')}")
        elif event_type == "error":
            print()
            code = data.get("code", "UNKNOWN")
            msg = data.get("message", "Unknown error")
            print(f"\n[error] {code}: {msg}", file=sys.stderr)
            sys.exit(1)

    if result is None:
        print("[debug] No success/error event received — stream may have been empty or malformed", file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description="Parse a reference file via Skywork Office API")
    parser.add_argument("file", help="Path to the file to parse")
    parser.add_argument("--output", "-o", default=None, help="Save parsed content to this file")
    parser.add_argument("--json", action="store_true", help="Output full result as JSON")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"[error] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    base_url = SKYWORK_OFFICE_URL
    token = get_skywork_token()

    result = parse_file(base_url, token, args.file)

    if result:
        metadata = result.get("metadata", {})
        parsed_content = metadata.get("parsed_content", "")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(parsed_content)
            print(f"\n[saved] Parsed content written to: {args.output}")
        elif args.json:
            print()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Print a preview of the parsed content
            if parsed_content:
                preview = parsed_content[:1000]
                if len(parsed_content) > 1000:
                    preview += f"\n... ({len(parsed_content) - 1000:,} more chars)"

        # Machine-readable summary for downstream parsing
        file_name = metadata.get("file_name") or os.path.basename(args.file)
        file_url = metadata.get("file_url", "")
        parsed_info = {
            "file_id": result.get("file_id", ""),
            "filename": file_name,
            "file_type": metadata.get("file_type", ""),
            "url": file_url,
        }
        print(f"PARSED_FILE: {json.dumps(parsed_info, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
