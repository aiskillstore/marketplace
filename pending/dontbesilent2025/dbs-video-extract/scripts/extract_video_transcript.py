#!/usr/bin/env python3
"""调用轻抖文案提取 API，并把短视频文字稿按作者和标题保存为 Markdown。"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://www.qingdou.vip"
KEYCHAIN_SERVICE = "dbs-qingdou-api-key"
DEFAULT_API_KEYS_FILE = Path.home() / ".config" / "dbs" / "API_Keys.md"
SUCCESS_CODE = 1001
ITEM_STATUS = {
    0: "任务处理中",
    1000: "文案提取成功",
    1001: "获取视频唯一状态码失败",
    1010: "链接获取失败",
    1011: "QPS 上限",
    1100: "视频链接为空",
    1101: "视频结果获取失败",
    1110: "文案提取错误",
    1111: "其他错误",
    1112: "视频过大或视频不是 MP4",
    1113: "用户资源不足",
    1114: "视频时长获取失败或时长为 0",
    1115: "获取链接信息失败",
    1116: "预扣费异常",
    1117: "获取视频链接异常",
    1118: "超时失败",
}
AUTHOR_KEYS = (
    "authorName",
    "author_name",
    "authorNickname",
    "author_nickname",
    "nickname",
    "userName",
    "user_name",
    "accountName",
    "account_name",
)


class ExtractError(RuntimeError):
    """可向调用方展示的提取失败。"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="把抖音、小红书等短视频链接提取为 Markdown 文字稿。"
    )
    parser.add_argument("inputs", nargs="*", help="视频链接或完整分享文案")
    parser.add_argument(
        "--stdin", action="store_true", help="从标准输入读取一个完整分享文案"
    )
    parser.add_argument(
        "--input-file", type=Path, help="从 UTF-8 文件读取，每个非空行作为一个输入"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd() / "短视频文字稿",
        help="Markdown 输出根目录",
    )
    parser.add_argument(
        "--poll-interval", type=float, default=2.0, help="轮询间隔秒数，默认 2"
    )
    parser.add_argument(
        "--timeout", type=float, default=900.0, help="每条输入最长等待秒数，默认 900"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="覆盖已经存在的同源 Markdown"
    )
    return parser.parse_args()


def find_api_key() -> str:
    value = os.environ.get("QINGDOU_API_KEY", "").strip()
    if value:
        return value
    configured_path = os.environ.get("QINGDOU_API_KEYS_FILE", "").strip()
    api_keys_path = Path(configured_path).expanduser() if configured_path else DEFAULT_API_KEYS_FILE
    if api_keys_path.is_file():
        try:
            text = api_keys_path.read_text(encoding="utf-8")
        except OSError:
            pass
        else:
            section = re.search(
                r"(?ms)^##\s+轻抖 API\s*$\n(.*?)(?=^##\s|\Z)", text
            )
            if section:
                key_line = re.search(
                    r"(?m)^-\s+\*\*Key\*\*:\s*(\S+)\s*$", section.group(1)
                )
                if key_line:
                    return key_line.group(1)
    if (
        sys.platform == "darwin"
        and os.environ.get("DBS_VIDEO_EXTRACT_DISABLE_KEYCHAIN") != "1"
    ):
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        else:
            value = result.stdout.strip()
            if value:
                return value
    return ""


def get_api_key() -> str:
    value = find_api_key()
    if value:
        return value
    raise ExtractError(
        "缺少轻抖 API Key：请在 API_Keys.md 中添加轻抖 API 条目，设置环境变量 "
        "QINGDOU_API_KEY，或在 macOS 钥匙串中创建服务名为 "
        f"{KEYCHAIN_SERVICE} 的通用密码。轻抖只负责语音文字稿；没有这个 Key "
        "时仍可单独使用 TikHub 查询作品或账号数据。"
    )


def request_json(
    method: str, url: str, api_key: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "dbs-video-extract/1.0",
            "x-api-key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        detail = detail.replace(api_key, "[REDACTED]")
        raise ExtractError(f"HTTP {error.code}：{detail}") from error
    except urllib.error.URLError as error:
        raise ExtractError(f"网络请求失败：{error.reason}") from error
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ExtractError("接口没有返回合法 JSON。") from error
    if not isinstance(data, dict):
        raise ExtractError("接口返回的 JSON 顶层不是对象。")
    return data


def business_status(data: dict[str, Any]) -> tuple[int | None, str]:
    status = data.get("status")
    if not isinstance(status, dict):
        return None, "接口缺少 status"
    code = status.get("code")
    try:
        normalized_code = int(code)
    except (TypeError, ValueError):
        normalized_code = None
    return normalized_code, str(status.get("msg") or "未知错误")


def extract_batch_id(data: dict[str, Any]) -> str:
    result = data.get("result")
    batch_id = result.get("batchId") if isinstance(result, dict) else result
    if batch_id is None or str(batch_id).strip() == "":
        raise ExtractError("创建任务成功，但返回结果中没有 batchId。")
    return str(batch_id)


def commit_task(base_url: str, api_key: str, user_input: str) -> str:
    url = f"{base_url.rstrip('/')}/web/api/commitGetTextTask"
    payloads = (
        {"userInputList": user_input},
        {"userInputList": [{"numberIndex": 0, "url": user_input}]},
    )
    for index, payload in enumerate(payloads):
        data = request_json("POST", url, api_key, payload)
        code, message = business_status(data)
        if code == SUCCESS_CODE:
            return extract_batch_id(data)
        if code != 4001 or index == len(payloads) - 1:
            raise ExtractError(f"创建任务失败：业务状态 {code}，{message}")
    raise ExtractError("创建任务失败。")


def poll_task(
    base_url: str,
    api_key: str,
    batch_id: str,
    poll_interval: float,
    timeout: float,
) -> dict[str, Any]:
    query = urllib.parse.urlencode({"batchId": batch_id})
    url = f"{base_url.rstrip('/')}/web/api/getTaskResult?{query}"
    deadline = time.monotonic() + timeout
    while True:
        data = request_json("GET", url, api_key)
        code, message = business_status(data)
        if code != SUCCESS_CODE:
            raise ExtractError(f"获取任务失败：业务状态 {code}，{message}")
        result = data.get("result")
        if not isinstance(result, dict):
            raise ExtractError("任务结果缺少 result 对象。")
        try:
            batch_status = int(result.get("batchStatus"))
        except (TypeError, ValueError):
            batch_status = None
        if batch_status == 2:
            return result
        if batch_status not in (0, 1):
            raise ExtractError(f"未知 batchStatus：{batch_status}")
        if time.monotonic() >= deadline:
            raise ExtractError("轮询超时。")
        remain = result.get("remainInterval")
        try:
            server_interval = float(remain)
        except (TypeError, ValueError):
            server_interval = 0.0
        wait_seconds = max(poll_interval, min(server_interval, 30.0))
        time.sleep(min(wait_seconds, max(0.0, deadline - time.monotonic())))


def first_text(mapping: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def find_author(item: dict[str, Any]) -> str:
    direct = first_text(item, AUTHOR_KEYS)
    if direct:
        return direct
    for parent_key in ("author", "user", "owner", "account"):
        nested = item.get(parent_key)
        if isinstance(nested, dict):
            value = first_text(nested, AUTHOR_KEYS + ("name",))
            if value:
                return value
    return ""


def safe_name(value: str, fallback: str, max_length: int = 100) -> str:
    cleaned = re.sub(r"[\x00-\x1f/\\:*?\"<>|]", " ", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    if not cleaned or cleaned in {".", ".."}:
        cleaned = fallback
    return cleaned[:max_length].rstrip(" .") or fallback


def yaml_string(value: Any) -> str:
    return json.dumps("" if value is None else str(value), ensure_ascii=False)


def normalize_transcript(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"\s+", " ", value).strip()


def render_markdown(item: dict[str, Any], title: str, author: str) -> str:
    transcript = normalize_transcript(item.get("videoContent"))
    fields = {
        "title": title,
        "author": author or "未识别作者",
        "platform": item.get("platformName"),
        "source_url": item.get("originLink"),
        "video_id": item.get("awemeId") or item.get("videoId"),
        "duration_seconds": item.get("videoTime"),
        "cover_url": item.get("videoCover"),
        "extracted_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    }
    frontmatter = "\n".join(f"{key}: {yaml_string(value)}" for key, value in fields.items())
    return f"---\n{frontmatter}\n---\n\n# {title}\n\n{transcript}\n"


def source_url_in_file(path: Path, source_url: str) -> bool:
    try:
        head = path.read_text(encoding="utf-8")[:5000]
    except OSError:
        return False
    return f"source_url: {yaml_string(source_url)}" in head


def choose_output_path(
    output_dir: Path,
    author: str,
    title: str,
    video_id: str,
    source_url: str,
    overwrite: bool,
) -> tuple[Path, str]:
    folder_name = safe_name(author, "_未识别作者") if author else "_未识别作者"
    title_name = safe_name(title, f"未命名视频-{video_id or '未知ID'}")
    folder = output_dir.expanduser().resolve() / folder_name
    candidate = folder / f"{title_name}.md"
    if not candidate.exists():
        return candidate, "created"
    if source_url_in_file(candidate, source_url):
        return candidate, "overwritten" if overwrite else "skipped_existing"
    suffix = safe_name(video_id, "", 40)
    if suffix:
        candidate = folder / f"{title_name}-{suffix}.md"
        if not candidate.exists() or source_url_in_file(candidate, source_url):
            action = "overwritten" if candidate.exists() and overwrite else (
                "skipped_existing" if candidate.exists() else "created"
            )
            return candidate, action
    number = 2
    while True:
        candidate = folder / f"{title_name}-{number}.md"
        if not candidate.exists():
            return candidate, "created"
        if source_url_in_file(candidate, source_url):
            return candidate, "overwritten" if overwrite else "skipped_existing"
        number += 1


def save_item(item: dict[str, Any], output_dir: Path, overwrite: bool) -> dict[str, Any]:
    try:
        status = int(item.get("status"))
    except (TypeError, ValueError):
        status = None
    if status != 1000:
        return {
            "ok": False,
            "status": status,
            "error": ITEM_STATUS.get(status, "未知条目状态"),
            "source_url": str(item.get("originLink") or ""),
        }
    video_id = str(item.get("awemeId") or item.get("videoId") or "").strip()
    raw_title = str(item.get("videoTitle") or "").strip()
    title = raw_title or f"未命名视频-{video_id or '未知ID'}"
    author = find_author(item)
    source_url = str(item.get("originLink") or "").strip()
    transcript = normalize_transcript(item.get("videoContent"))
    if not transcript:
        return {
            "ok": False,
            "status": status,
            "error": "接口返回成功，但文字稿为空",
            "source_url": source_url,
        }
    path, action = choose_output_path(
        output_dir, author, title, video_id, source_url, overwrite
    )
    if action != "skipped_existing":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_markdown(item, title, author), encoding="utf-8")
    return {
        "ok": True,
        "action": action,
        "path": str(path),
        "title": title,
        "author": author or None,
        "author_identified": bool(author),
        "source_url": source_url,
    }


def collect_inputs(args: argparse.Namespace) -> list[str]:
    inputs = [value.strip() for value in args.inputs if value.strip()]
    if args.stdin:
        value = sys.stdin.read().strip()
        if value:
            inputs.append(value)
    if args.input_file:
        content = args.input_file.expanduser().read_text(encoding="utf-8")
        inputs.extend(line.strip() for line in content.splitlines() if line.strip())
    if not inputs:
        raise ExtractError("没有收到视频链接或分享文案。")
    return inputs


def main() -> int:
    args = parse_args()
    try:
        inputs = collect_inputs(args)
        api_key = get_api_key()
    except (ExtractError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2

    base_url = os.environ.get("QINGDOU_BASE_URL", DEFAULT_BASE_URL).strip()
    results: list[dict[str, Any]] = []
    for user_input in inputs:
        try:
            batch_id = commit_task(base_url, api_key, user_input)
            result = poll_task(
                base_url,
                api_key,
                batch_id,
                max(0.2, args.poll_interval),
                max(1.0, args.timeout),
            )
            items = result.get("list")
            if not isinstance(items, list) or not items:
                raise ExtractError("批任务没有返回条目。")
            item_results = [
                save_item(item, args.output_dir, args.overwrite)
                for item in items
                if isinstance(item, dict)
            ]
            results.append(
                {
                    "input": user_input,
                    "items": item_results,
                }
            )
        except (ExtractError, OSError) as error:
            results.append({"input": user_input, "ok": False, "error": str(error)})

    success_count = sum(
        1
        for result in results
        for item in result.get("items", [])
        if item.get("ok")
    )
    failure_count = sum(
        1
        for result in results
        if result.get("ok") is False
    ) + sum(
        1
        for result in results
        for item in result.get("items", [])
        if not item.get("ok")
    )
    summary = {
        "ok": failure_count == 0,
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
