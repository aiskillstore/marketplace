#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import json
import mimetypes
import re
import ssl
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib import error, parse, request


_CONFIG_LINE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*(.*)$")


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_config(path: Path) -> dict[str, str]:
    config: dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _CONFIG_LINE_RE.match(line)
        if not match:
            continue
        key = match.group(1).upper()
        value = _strip_quotes(match.group(2))
        config[key] = value
    return config


def _as_int(value: str | None, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _join_prompt(pad_url: str, prompt: str) -> str:
    pad_url = pad_url.strip()
    prompt = prompt.strip()
    if not pad_url:
        return prompt
    return f"{pad_url} {prompt}"


def load_requests(input_path: Path) -> list[dict[str, Any]]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    if input_path.suffix.lower() == ".jsonl":
        requests_list: list[dict[str, Any]] = []
        for line_no, raw_line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"Invalid JSONL at line {line_no}: expected object")
            requests_list.append(obj)
        return requests_list

    obj = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(obj, list) and all(isinstance(item, dict) for item in obj):
        return list(obj)  # type: ignore[return-value]
    raise ValueError("Unsupported input format: use .jsonl (recommended) or a JSON array of objects")


@dataclass(frozen=True)
class Normalized:
    request_id: str
    payload: dict[str, Any]


def normalize_requests(
    raw_requests: Iterable[dict[str, Any]],
    *,
    default_model: str,
    default_size: str,
    default_n: int,
    default_resolution: str,
    default_pad_url: str,
) -> list[Normalized]:
    normalized: list[Normalized] = []
    auto_id = 1
    for raw in raw_requests:
        prompt = str(raw.get("prompt", "")).strip()
        if not prompt:
            continue

        request_id = str(raw.get("id", "")).strip()
        if not request_id:
            request_id = f"{auto_id:02d}"
        auto_id += 1

        model = str(raw.get("model", "")).strip() or default_model
        size = str(raw.get("size", "")).strip() or default_size
        resolution = str(raw.get("resolution", "")).strip() or default_resolution
        n = raw.get("n", None)
        if isinstance(n, int):
            n_value = n
        else:
            n_value = default_n

        pad_url = str(raw.get("pad_url", "")).strip() or default_pad_url
        joined_prompt = _join_prompt(pad_url, prompt)

        payload = {
            "model": model,
            "prompt": joined_prompt,
            "size": size,
            "n": n_value,
            "resolution": resolution,
        }
        normalized.append(Normalized(request_id=request_id, payload=payload))

    return normalized


def _safe_filename_part(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value[:80] if value else "item"


def post_json(*, url: str, token: str, payload: dict[str, Any], timeout_s: float) -> tuple[int, dict[str, str], bytes]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url=url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    with request.urlopen(req, timeout=timeout_s) as resp:
        status = int(getattr(resp, "status", 200))
        headers = {k.lower(): v for k, v in resp.headers.items()}
        body = resp.read()
    return status, headers, body


def _extract_base64_blob(value: str) -> tuple[str | None, str]:
    value = value.strip()
    if value.startswith("data:") and ";base64," in value:
        header, b64 = value.split(";base64,", 1)
        mime = header[5:] if header.startswith("data:") else None
        return mime, b64
    return None, value


def extract_images(response_obj: Any) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key in ("url",):
                value = node.get(key)
                if isinstance(value, str) and value.startswith(("http://", "https://")):
                    item = ("url", value)
                    if item not in seen:
                        seen.add(item)
                        found.append(item)
            for key in ("b64_json", "base64", "image_base64", "image_b64"):
                value = node.get(key)
                if isinstance(value, str) and value.strip():
                    item = ("base64", value.strip())
                    if item not in seen:
                        seen.add(item)
                        found.append(item)

            for value in node.values():
                visit(value)
            return

        if isinstance(node, list):
            for value in node:
                visit(value)

    visit(response_obj)
    return found


def _guess_extension_from_mime(mime: str | None) -> str:
    if not mime:
        return ".png"
    ext = mimetypes.guess_extension(mime.split(";", 1)[0].strip())
    return ext or ".png"


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def download_url(url: str, *, timeout_s: float, ctx: ssl.SSLContext) -> tuple[bytes, str | None]:
    req = request.Request(url=url, method="GET")
    with request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
        body = resp.read()
        mime = resp.headers.get("Content-Type")
    return body, mime


def render_curl_command(api_url: str, payload: dict[str, Any]) -> str:
    body = json.dumps(payload, ensure_ascii=False)
    return (
        "curl --request POST \\\n"
        f"  --url '{api_url}' \\\n"
        "  --header 'Authorization: Bearer [TOKEN]' \\\n"
        "  --header 'Content-Type: application/json' \\\n"
        f"  --data-raw '{body}'"
    )


def _extract_task_ids(obj: Any) -> list[str]:
    task_ids: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key in ("task_id", "taskId", "id"):
                value = node.get(key)
                if isinstance(value, str) and value.startswith("task_"):
                    task_ids.append(value)
            for value in node.values():
                visit(value)
            return
        if isinstance(node, list):
            for value in node:
                visit(value)

    visit(obj)
    seen: set[str] = set()
    unique: list[str] = []
    for tid in task_ids:
        if tid not in seen:
            seen.add(tid)
            unique.append(tid)
    return unique


def _extract_urls(obj: Any) -> list[str]:
    urls: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key in ("url", "urls"):
                value = node.get(key)
                if isinstance(value, str) and value.startswith(("http://", "https://")):
                    urls.append(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and item.startswith(("http://", "https://")):
                            urls.append(item)
            for value in node.values():
                visit(value)
            return
        if isinstance(node, list):
            for value in node:
                visit(value)

    visit(obj)
    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def _task_base_url(api_url: str) -> str:
    parts = parse.urlsplit(api_url)
    if not parts.scheme or not parts.netloc:
        raise ValueError(f"Invalid API_URL: {api_url}")
    return f"{parts.scheme}://{parts.netloc}"


def _get_json(url: str, *, token: str, timeout_s: float, ctx: ssl.SSLContext) -> Any:
    req = request.Request(url=url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    with request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
        body = resp.read()
    return json.loads(body.decode("utf-8", errors="replace"))


def poll_task(
    *,
    api_url: str,
    task_id: str,
    token: str,
    timeout_s: float,
    max_wait_s: float,
    interval_s: float,
    ctx: ssl.SSLContext,
) -> dict[str, Any]:
    base_url = _task_base_url(api_url)
    url = f"{base_url}/v1/tasks/{task_id}"
    deadline = time.time() + max_wait_s
    last_obj: Any = None

    while True:
        try:
            last_obj = _get_json(url, token=token, timeout_s=timeout_s, ctx=ctx)
        except error.HTTPError as exc:
            body = exc.read() if hasattr(exc, "read") else b""
            return {"error": {"type": "HTTPError", "code": exc.code, "body": body.decode("utf-8", errors="replace")}}
        except Exception as exc:
            return {"error": {"type": type(exc).__name__, "message": str(exc)}}

        status = str(((last_obj or {}).get("data") or {}).get("status") or "").strip().lower()
        if status in {"completed", "failed", "canceled", "cancelled"}:
            break
        if time.time() >= deadline:
            break
        time.sleep(max(0.1, interval_s))

    return last_obj if isinstance(last_obj, dict) else {"data": last_obj}


def _write_run_json(path: Path, obj: dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _get_main_output_dir() -> Path:
    """
    检测主工作目录：
    - 如果当前目录在 .claude/skills 下，往上找到主工作目录
    - 否则使用当前目录
    """
    cwd = Path.cwd().resolve()
    # 检查是否在 .claude/skills 路径下
    parts = cwd.parts
    if '.claude' in parts and 'skills' in parts:
        # 找到 .claude 的位置，往上一层就是主工作目录
        try:
            claude_idx = parts.index('.claude')
            main_dir = Path(*parts[:claude_idx])
            return main_dir / "outputs"
        except (ValueError, IndexError):
            pass
    # 默认返回当前目录下的 outputs
    return Path("outputs")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Batch generate images via APIMart.")
    parser.add_argument("--config", type=Path, default=Path("scripts/apimart.env"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--dry-run", action="store_true", help="Do not call API; write a single run.json with requests/curl.")
    parser.add_argument("--no-download", action="store_true", help="Do not download images; still record URLs in run.json.")
    parser.add_argument("--max-wait", type=float, default=300.0, help="Max seconds to wait for async task completion.")
    parser.add_argument("--interval", type=float, default=2.0, help="Polling interval seconds for async tasks.")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    api_url = config.get("API_URL", "https://api.apimart.ai/v1/images/generations").strip()
    model = config.get("MODEL", "gemini-3-pro-image-preview").strip()
    token = config.get("TOKEN", "").strip()
    resolution = config.get("RESOLUTION", "2K").strip()
    size = config.get("SIZE", "16:9").strip()
    n = _as_int(config.get("N"), default=1)
    pad_url = config.get("PAD_URL", "").strip()

    if not api_url:
        raise ValueError("Missing API_URL in config")
    if not model:
        raise ValueError("Missing MODEL in config")
    if not resolution:
        raise ValueError("Missing RESOLUTION in config")
    if not size:
        raise ValueError("Missing SIZE in config")

    if not args.dry_run and not token:
        raise ValueError("Missing TOKEN in config (or use --dry-run)")

    raw_requests = load_requests(args.input)
    normalized = normalize_requests(
        raw_requests,
        default_model=model,
        default_size=size,
        default_n=n,
        default_resolution=resolution,
        default_pad_url=pad_url,
    )
    if not normalized:
        print("No valid requests found (need at least a 'prompt').", file=sys.stderr)
        return 2

    if args.out is None:
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        base_output_dir = _get_main_output_dir()
        out_dir = base_output_dir / f"apimart-{stamp}"
    else:
        out_dir = args.out

    out_dir.mkdir(parents=True, exist_ok=True)
    run_json_path = out_dir / "run.json"
    ctx = _ssl_context()
    started_at = _dt.datetime.now().isoformat(timespec="seconds")

    run: dict[str, Any] = {
        "started_at": started_at,
        "input": str(args.input),
        "output_dir": str(out_dir),
        "config": {
            "api_url": api_url,
            "model": model,
            "resolution": resolution,
            "size": size,
            "n": n,
            "pad_url": pad_url,
        },
        "items": [],
    }
    _write_run_json(run_json_path, run)

    for item in normalized:
        request_id = _safe_filename_part(item.request_id)
        record: dict[str, Any] = {
            "id": request_id,
            "request": item.payload,
        }

        if args.dry_run:
            record["curl"] = render_curl_command(api_url, item.payload)
            run["items"].append(record)
            _write_run_json(run_json_path, run)
            continue

        try:
            status, headers, body = post_json(url=api_url, token=token, payload=item.payload, timeout_s=args.timeout)
        except error.HTTPError as exc:
            body = exc.read() if hasattr(exc, "read") else b""
            record["error"] = {
                "type": "HTTPError",
                "message": str(exc),
                "body": (body or b"").decode("utf-8", errors="replace"),
            }
            run["items"].append(record)
            _write_run_json(run_json_path, run)
            print(f"[{request_id}] HTTPError: {exc}", file=sys.stderr)
            continue
        except Exception as exc:
            record["error"] = {"type": type(exc).__name__, "message": str(exc)}
            run["items"].append(record)
            _write_run_json(run_json_path, run)
            print(f"[{request_id}] Error: {exc}", file=sys.stderr)
            continue

        record["post"] = {"status": status, "headers": headers}

        response_obj: Any | None = None
        body_text = body.decode("utf-8", errors="replace")
        try:
            response_obj = json.loads(body_text)
            record["post_json"] = response_obj
        except Exception:
            record["post_text"] = body_text

        saved_images: list[dict[str, Any]] = []
        image_sources: list[dict[str, Any]] = []
        tasks: list[dict[str, Any]] = []

        if response_obj is not None:
            images = extract_images(response_obj)
            for idx, (kind, value) in enumerate(images, start=1):
                if kind == "base64":
                    mime, b64 = _extract_base64_blob(value)
                    image_sources.append({"kind": "base64", "index": idx, "mime": mime})
                    if args.no_download:
                        continue
                    try:
                        data = base64.b64decode(b64, validate=False)
                    except Exception:
                        continue
                    ext = _guess_extension_from_mime(mime)
                    filename = f"{request_id}-{idx}{ext}"
                    (out_dir / filename).write_bytes(data)
                    saved_images.append({"filename": filename, "source_kind": "base64", "index": idx})
                    continue

                if kind == "url":
                    image_sources.append({"kind": "url", "index": idx, "url": value})
                    if args.no_download:
                        continue
                    try:
                        data, mime = download_url(value, timeout_s=args.timeout, ctx=ctx)
                    except Exception:
                        continue
                    ext = _guess_extension_from_mime(mime)
                    filename = f"{request_id}-{idx}{ext}"
                    (out_dir / filename).write_bytes(data)
                    saved_images.append({"filename": filename, "source_kind": "url", "index": idx, "url": value})

            task_ids = _extract_task_ids(response_obj)
            for task_index, task_id in enumerate(task_ids, start=1):
                task_obj = poll_task(
                    api_url=api_url,
                    task_id=task_id,
                    token=token,
                    timeout_s=args.timeout,
                    max_wait_s=args.max_wait,
                    interval_s=args.interval,
                    ctx=ctx,
                )
                task_entry: dict[str, Any] = {"task_id": task_id, "task": task_obj}
                task_urls = _extract_urls(task_obj)
                if task_urls:
                    task_entry["image_urls"] = task_urls
                tasks.append(task_entry)

                if args.no_download:
                    continue
                for url_index, url in enumerate(task_urls, start=1):
                    try:
                        data, mime = download_url(url, timeout_s=args.timeout, ctx=ctx)
                    except Exception:
                        continue
                    ext = _guess_extension_from_mime(mime)
                    filename = f"{request_id}-task{task_index}-{url_index}{ext}"
                    (out_dir / filename).write_bytes(data)
                    saved_images.append(
                        {
                            "filename": filename,
                            "source_kind": "task_url",
                            "task_id": task_id,
                            "task_index": task_index,
                            "url_index": url_index,
                            "url": url,
                        }
                    )

        if image_sources:
            record["image_sources"] = image_sources
        if tasks:
            record["tasks"] = tasks
        if saved_images:
            record["saved_images"] = saved_images

        run["items"].append(record)
        _write_run_json(run_json_path, run)
        print(f"[{request_id}] OK ({status})")

    run["ended_at"] = _dt.datetime.now().isoformat(timespec="seconds")
    _write_run_json(run_json_path, run)
    print(f"\nDone. Output: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
