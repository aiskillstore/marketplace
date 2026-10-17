#!/usr/bin/env python3
"""在本地隐蔽读取并保存 dbs-video-extract 的服务凭证。"""

from __future__ import annotations

import argparse
import getpass
import os
import re
import tempfile
from pathlib import Path


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "dbs" / "API_Keys.md"
PROVIDERS = {
    "tikhub": {
        "display_name": "TikHub",
        "section": "TikHub API",
    },
    "qingdou": {
        "display_name": "轻抖",
        "section": "轻抖 API",
    },
}


class ConfigureError(RuntimeError):
    """可以安全展示给用户的配置错误。"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="安全保存 TikHub 或轻抖的 API 使用凭证。"
    )
    parser.add_argument("provider", choices=tuple(PROVIDERS))
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="本地私密配置文件，默认 ~/.config/dbs/API_Keys.md",
    )
    return parser.parse_args()


def replace_section(text: str, section: str, secret: str) -> str:
    block = f"## {section}\n- **Key**: {secret}\n"
    pattern = re.compile(
        rf"(?ms)^##\s+{re.escape(section)}\s*$\n.*?(?=^##\s|\Z)"
    )
    if pattern.search(text):
        return pattern.sub(lambda _match: block, text, count=1).rstrip() + "\n"
    prefix = text.rstrip()
    return f"{prefix}\n\n{block}" if prefix else block


def write_private_config(path: Path, section: str, secret: str) -> None:
    target = path.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = target.read_text(encoding="utf-8") if target.is_file() else ""
    updated = replace_section(existing, section, secret)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(updated)
        temporary.chmod(0o600)
        os.replace(temporary, target)
        target.chmod(0o600)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    args = parse_args()
    provider = PROVIDERS[args.provider]
    display_name = provider["display_name"]
    print(
        f"请粘贴 {display_name} 提供的 API 使用凭证。输入不会显示在屏幕上，"
        "按回车保存。"
    )
    secret = getpass.getpass("使用凭证：").strip()
    if not secret:
        raise ConfigureError("没有收到使用凭证，未修改任何文件。")
    if any(character.isspace() for character in secret):
        raise ConfigureError("使用凭证中包含空格或换行，未修改任何文件。")
    try:
        write_private_config(args.file, provider["section"], secret)
    except OSError as error:
        raise ConfigureError(f"保存失败：{error}") from error
    print(
        f"{display_name} 使用凭证已保存到本地私密配置。"
        "现在可以运行 extract_video.py --check-keys 检查状态。"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigureError as error:
        print(error)
        raise SystemExit(2) from None
