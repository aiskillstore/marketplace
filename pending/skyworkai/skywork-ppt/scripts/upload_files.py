#!/usr/bin/env python3
"""
Upload local files to OSS by calling the /upload_oss endpoint.

Usage:
  python upload_files.py file1.png file2.jpg
  python upload_files.py file1.png --path skills/images/
"""
import argparse
import io
import json
import mimetypes
import os
import sys
import urllib.request
import urllib.error
import uuid


from config import SKYWORK_GATEWAY_URL

from skywork_auth import get_skywork_token


def build_multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    """Build a multipart/form-data request body, returns (body_bytes, content_type).

    fields: {"field_name": "value", ...}
    files:  {"field_name": (filename, file_bytes, mime_type), ...}
    """
    boundary = uuid.uuid4().hex
    parts = []

    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f'{value}\r\n'
        )

    for name, (filename, data, mime) in files.items():
        parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
            f'Content-Type: {mime}\r\n\r\n'
        )
        if isinstance(data, str):
            data = data.encode()
        parts_bytes = b''.join(
            p.encode() if isinstance(p, str) else p for p in parts
        ) + data + b'\r\n'
        parts = [parts_bytes]

    body = b''.join(p.encode() if isinstance(p, str) else p for p in parts)
    body += f'--{boundary}--\r\n'.encode()
    content_type = f'multipart/form-data; boundary={boundary}'
    return body, content_type


def upload_file(local_path: str, oss_prefix: str | None, base_url: str, token: str = None) -> str:
    """Upload a single local file and return the OSS URL. Raises an exception on failure."""
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")

    filename = os.path.basename(local_path)
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    with open(local_path, "rb") as f:
        file_bytes = f.read()

    fields = {}
    if oss_prefix:
        fields["path"] = oss_prefix

    body, content_type = build_multipart(
        fields=fields,
        files={"file": (filename, file_bytes, mime)},
    )

    url = base_url.rstrip("/") + "/upload_oss"
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers= {
            "Content-Type": content_type, 
            "Token": token
        },
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8", errors="replace")

    result = json.loads(raw)
    code = result.get("code")
    if code != 200:
        raise RuntimeError(f"Upload failed code={code} msg={result.get('msg')}")

    return result["url"]


def upload_files(local_paths: list[str], oss_prefix: str | None = None, base_url: str = SKYWORK_GATEWAY_URL, token: str = None) -> list[dict]:
    """Upload a batch of local files and return a list of results for each file.

    Return format:
        [{"path": "/local/file.png", "url": "https://cdn.../xxx.png", "ok": True}, ...]
        On failure, url is empty, ok is False, and an error field is included.
    """
    results = []
    for path in local_paths:
        try:
            url = upload_file(path, oss_prefix, base_url, token)
            filename = os.path.basename(path)
            print(f"[OK] {path} -> {url}", flush=True)
            results.append({"path": path, "filename": filename, "url": url, "ok": True})
        except Exception as e:
            print(f"[FAIL] {path}: {e}", file=sys.stderr, flush=True)
            results.append({"path": path, "filename": os.path.basename(path), "url": "", "ok": False, "error": str(e)})
    # Print machine-readable summary for downstream parsing
    uploaded = [{"filename": r["filename"], "url": r["url"]} for r in results if r["ok"]]
    if uploaded:
        print(f"UPLOADED_FILES: {json.dumps(uploaded, ensure_ascii=False)}", flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Batch upload local files to OSS")
    parser.add_argument("files", nargs="+", help="List of local file paths")
    args = parser.parse_args()

    token = get_skywork_token()
    if not token:
        print("[error] Failed to get token", file=sys.stderr)
        sys.exit(1)

    results = upload_files(args.files, oss_prefix='', token=token)

    failed = [r for r in results if not r["ok"]]
    if failed:
        print(f"\n{len(failed)}/{len(results)} file(s) failed to upload", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nAll {len(results)} file(s) uploaded successfully")


if __name__ == "__main__":
    main()
