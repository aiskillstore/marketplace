#!/usr/bin/env python3
"""
Generate or edit images via backend image API.

Usage:
    python3 generate_image.py --prompt "description" --filename "out.png"
    python3 generate_image.py --prompt "edit instructions" --filename "out.png" --input-image "ref.png"
    python3 generate_image.py --prompt "combine styles" --filename "out.png" -i "ref1.png" -i "ref2.png"
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

SKYWORK_GATEWAY_URL = os.environ.get("SKYWORK_GATEWAY_URL", "https://api-tools.skywork.ai/theme-gateway").rstrip("/")

VALID_ASPECT_RATIOS = [
    "1:1", "2:3", "3:2", "3:4", "4:3",
    "4:5", "5:4", "9:16", "16:9", "21:9",
]


def load_image_base64(path: str) -> tuple[str, str]:
    """Return (base64_data, mime_type) for a local image file."""
    p = Path(path)
    if not p.exists():
        print(f"Error: Input image not found: {path}", file=sys.stderr)
        sys.exit(1)
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    return base64.b64encode(p.read_bytes()).decode(), mime


# ---------------------------------------------------------------------------
# SSE parsing
# ---------------------------------------------------------------------------

def parse_sse_stream(resp):
    """Yield (event_type, data_dict) from an SSE byte stream."""
    cur_event = None
    cur_data = None
    for line in resp:
        line = line.decode("utf-8", errors="replace").rstrip("\r\n")
        if line == "":
            if cur_event is not None and cur_data is not None:
                try:
                    data = json.loads(cur_data) if cur_data else {}
                except json.JSONDecodeError:
                    data = {}
                if not isinstance(data, dict):
                    data = {}
                yield cur_event, data
            cur_event = None
            cur_data = None
            continue
        if line.startswith("event:"):
            cur_event = line[6:].strip()
        elif line.startswith("data:"):
            cur_data = line[5:].strip()

    if cur_event is not None and cur_data is not None:
        try:
            data = json.loads(cur_data) if cur_data else {}
        except json.JSONDecodeError:
            data = {}
        if not isinstance(data, dict):
            data = {}
        yield cur_event, data


from skywork_auth import get_skywork_token


def call_sse(url: str, body: dict) -> dict | None:
    """POST to an SSE endpoint. Print progress, return success payload or exit on error."""
    token = get_skywork_token()
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, method="POST",
        headers={"Content-Type": "application/json", "Accept": "text/event-stream", "token": token},
    )

    success_data = None
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            for event_type, event_data in parse_sse_stream(resp):
                if event_type == "progress":
                    pct = event_data.get("percentage", 0)
                    msg = event_data.get("message", "")
                    print(f"[{pct:.0f}%] {msg}", flush=True)
                elif event_type == "success":
                    success_data = event_data
                elif event_type == "error":
                    print(f"Error: {event_data.get('message', event_data)}", file=sys.stderr)
                    sys.exit(1)
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"HTTP error {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    return success_data


def download_image(file_url: str, output_path: str) -> None:
    """Download the result image from a URL (OSS CDN)."""
    out_abs = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(out_abs) or ".", exist_ok=True)

    try:
        req = urllib.request.Request(file_url, method="GET")
        with urllib.request.urlopen(req, timeout=120) as r:
            with open(out_abs, "wb") as f:
                f.write(r.read())
        print(f"\nImage saved: {out_abs}")
        print(f"OSS URL: {file_url}")
        print("Please notice that the local path and OSS URL are provided for user reference.")
    except Exception as e:
        print(f"Download failed: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate/edit images via backend API")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt or edit instructions")
    parser.add_argument("--filename", "-f", required=True, help="Output filename")
    parser.add_argument("--input-image", "-i", action="append", help="Input image(s) for editing (repeatable)")
    parser.add_argument("--aspect-ratio", "-a", choices=VALID_ASPECT_RATIOS, default=None, help="Aspect ratio")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="2K",
                        help="Output resolution (default: 2K)")
    args = parser.parse_args()

    base_url = SKYWORK_GATEWAY_URL

    if args.input_image:
        # --- Edit mode: POST /api/sse/image/update ---
        images = []
        for img_path in args.input_image:
            b64, mime = load_image_base64(img_path)
            images.append({"base64": b64, "mime_type": mime})

        operation: dict = {
            "action": "edit",
            "prompt": args.prompt,
            "source_images": images,
            "resolution": args.resolution,
        }
        if args.aspect_ratio:
            operation["aspect_ratio"] = args.aspect_ratio

        body = {
            "file_id": "from-local",
            "operations": [operation],
        }

        mode = "Editing"
        url = f"{base_url}/api/sse/image/update"
    else:
        # --- Generate mode: POST /api/sse/image/create ---
        body: dict = {
            "title": args.prompt[:60],
            "content": args.prompt,
            "style": {},
            "options": {"resolution": args.resolution},
        }
        if args.aspect_ratio:
            body["style"]["aspect_ratio"] = args.aspect_ratio

        mode = "Generating"
        url = f"{base_url}/api/sse/image/create"

    print(f"{mode} image (resolution={args.resolution}, aspect_ratio={args.aspect_ratio or 'auto'})...")
    print("This may take 30-120 seconds. Please wait...")

    body["source_platform"] = "skyclaw" if os.environ.get("POD_TYPE", "") == "skyclaw" else ""
    result = call_sse(url, body)

    if not result:
        print("No success response from server.", file=sys.stderr)
        sys.exit(1)

    file_url = result.get("file_url", "")
    if file_url:
        download_image(file_url, args.filename)
    else:
        print("Warning: No file_url in response.", file=sys.stderr)
        file_path = result.get("file_path", "")
        if file_path:
            print(f"Server file path: {file_path}")


if __name__ == "__main__":
    main()
