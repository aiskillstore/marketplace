#!/usr/bin/env python3
"""Codex Vision Bridge 环境自检脚本（跨平台）.

检测 Node.js / Ollama / GPU / 端口 / 现有配置，输出一键式报告，
帮助 Codex 判断该引导用户走哪条路线（云端 / 本地 VLM / 仅 OCR）。
"""

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path


def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        return r.returncode == 0, r.stdout.strip()
    except Exception:
        return False, ""


def port_open(port, host="127.0.0.1"):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except Exception:
        return False


def gpu_info():
    """返回 GPU 型号与显存（优先 nvidia-smi，回退 wmic）。"""
    if os.name == "nt":
        ok, out = run(["wmic", "path", "win32_VideoController", "get", "name", "/value"])
        if ok and out:
            names = [l.split("=", 1)[1].strip() for l in out.splitlines() if "=" in l and l.split("=", 1)[1].strip()]
            return names[:2]
        return []
    ok, out = run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
    if ok:
        return [l.strip() for l in out.splitlines()[:2]]
    return []


def ollama_models():
    exe = shutil.which("ollama")
    if not exe:
        return None, None
    if not port_open(11434):
        return exe, None  # 已安装但服务未运行
    ok, out = run([exe, "list"])
    models = []
    if ok:
        for line in out.splitlines()[1:]:
            parts = line.split()
            if parts:
                models.append(parts[0])
    return exe, models


def find_codex_config():
    candidates = [
        Path(os.environ.get("CODEX_HOME", "")) / "config.toml",
        Path.home() / ".codex" / "config.toml",
    ]
    for c in candidates:
        if c and c.exists():
            return c
    return None


def main():
    report = {
        "os": platform.system(),
        "arch": platform.machine(),
        "python": sys.version.split()[0],
        "node": None,
        "ollama_installed": False,
        "ollama_running": False,
        "ollama_models": [],
        "gpu": [],
        "proxy_port_open": port_open(int(os.environ.get("OCR_PROXY_PORT", "57323"))),
        "codex_config": None,
        "deepseek_key_configured": False,
        "siliconflow_key_configured": False,
    }

    ok, out = run([shutil.which("node") or "node", "--version"])
    if ok:
        report["node"] = out

    exe, models = ollama_models()
    if exe:
        report["ollama_installed"] = True
        report["ollama_running"] = models is not None
        report["ollama_models"] = models or []

    report["gpu"] = gpu_info()

    cfg = find_codex_config()
    if cfg:
        report["codex_config"] = str(cfg)
        text = cfg.read_text(encoding="utf-8", errors="ignore")
        report["deepseek_key_configured"] = "experimental_bearer_token" in text
        report["siliconflow_key_configured"] = "siliconflow" in text.lower()

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
