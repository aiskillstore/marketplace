"""存储调试会话状态与日志的工具。"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

STATE_DIR = Path(os.path.expanduser("~/.cache/pwdebug"))
STATE_FILE = STATE_DIR / "server.json"
LOG_FILE = STATE_DIR / "console.log.jsonl"


def ensure_state_dir() -> None:
    """确保状态目录存在。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def write_state(cdp_endpoint: str, pid: int, browser_type: str) -> None:
    """写入浏览器服务的连接信息。"""
    ensure_state_dir()
    payload = {
        "cdp_endpoint": cdp_endpoint,
        "pid": pid,
        "browser_type": browser_type,
        "updated_at": int(time.time()),
    }
    STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_state() -> Dict[str, Any]:
    """读取浏览器服务连接信息。"""
    if not STATE_FILE.exists():
        raise FileNotFoundError("未找到浏览器服务状态，请先启动服务。")
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def get_cdp_endpoint() -> str:
    """从状态文件中取出 CDP 地址。"""
    state = read_state()
    cdp_endpoint = state.get("cdp_endpoint")
    if not cdp_endpoint:
        raise RuntimeError("状态文件缺少 cdp_endpoint 字段。")
    return cdp_endpoint


def get_profile_dir() -> Path:
    """返回浏览器用户数据目录路径。"""
    ensure_state_dir()
    return STATE_DIR / "profile"


def get_browser_type_name() -> str:
    """从状态文件中取出浏览器类型名称。"""
    state = read_state()
    return state.get("browser_type", "chromium")


def clear_log() -> None:
    """清空控制台日志文件。"""
    ensure_state_dir()
    LOG_FILE.write_text("", encoding="utf-8")


def append_log_entry(entry: Dict[str, Any]) -> None:
    """追加一条控制台日志记录。"""
    ensure_state_dir()
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def iter_log_entries() -> Iterable[Dict[str, Any]]:
    """按行读取控制台日志记录。"""
    if not LOG_FILE.exists():
        return []
    with LOG_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def tail_log_entries(limit: int) -> List[Dict[str, Any]]:
    """读取最近的控制台日志记录。"""
    entries = list(iter_log_entries())
    if limit <= 0:
        return []
    return entries[-limit:]
