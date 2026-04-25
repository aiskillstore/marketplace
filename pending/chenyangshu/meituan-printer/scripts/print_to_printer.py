#!/usr/bin/env python3
"""
美团热敏打印机打印脚本 v2.0
- 通过 config.json 读取打印机配置
- 支持别名 / IP 直接打印
- 独立运行，无外部依赖

用法:
    python3 print_to_printer.py --name <别名> --title "标题" --content "内容"
    python3 print_to_printer.py --ip <IP> --port <端口> --title "标题" --content "内容"
    python3 print_to_printer.py --setup           进入引导配置模式
    python3 print_to_printer.py --list            列出所有已配置打印机
    python3 print_to_printer.py --guide            功能引导（新手指南）
"""

import os
import sys
import json
import socket
import argparse
from datetime import datetime
from pathlib import Path

# ============== 路径配置 ==============
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
DEFAULT_PORT = 9100


def get_config():
    """加载 config.json，不存在则返回空"""
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_config(config):
    """保存配置到 config.json"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def find_printer_by_alias(alias, config):
    """按别名查找打印机"""
    for p in config.get("printers", []):
        if p["alias"] == alias:
            return p
    return None


def build_print_commands(title, message, center_content=False):
    """构建 ESC/POS 打印命令序列
    center_content: 正文是否居中（标题始终居中）
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cmds = []

    # 初始化打印机
    cmds.append(b"\x1B\x40")

    # 大标题（居中 + 双倍高宽）
    cmds.append(b"\x1B\x61\x01")      # 居中对齐
    cmds.append(b"\x1B\x21\x30")      # 双倍高宽
    cmds.append(title.encode("gb18030"))
    cmds.append(b"\n\n")

    # 时间（居中 + 倍高）
    cmds.append(b"\x1B\x61\x01")
    cmds.append(b"\x1B\x21\x10")
    cmds.append(f"打印时间: {current_time}".encode("gb18030"))
    cmds.append(b"\n\n")

    # 恢复对齐 + 正常大小
    cmds.append(b"\x1B\x61\x01" if center_content else b"\x1B\x61\x00")
    cmds.append(b"\x1B\x21\x00")

    # 分隔线
    cmds.append(("=" * 32 + "\n").encode("gb18030"))

    # 正文内容
    cmds.append(b"\x1B\x21\x10")
    lines = message.strip().split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        if clean_line.startswith("-------") or clean_line.startswith("---"):
            cmds.append(b"\n\x1B\x21\x28")
            cmds.append(clean_line.encode("gb18030"))
            cmds.append(b"\n\x1B\x21\x10")
        else:
            prefix = "" if center_content else "  "
            cmds.append(f"{prefix}{clean_line}\n".encode("gb18030"))

    # 结尾
    cmds.append(b"\n" + ("=" * 32 + "\n").encode("gb18030"))
    cmds.append(b"\x1B\x61\x01\x1B\x21\x10")
    cmds.append("请按时完成各项工作\n".encode("gb18030"))
    cmds.append(b"\n" * 5)

    # 切纸
    cmds.append(b"\x1d\x56\x00")

    return cmds


def send_print(ip, port, title, message, center_content=False):
    """连接打印机并发送任务"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((ip, port))

        cmds = build_print_commands(title, message, center_content=center_content)
        for cmd in cmds:
            s.send(cmd)
        s.close()
        return True, f"✅ 打印成功 → {ip}:{port}"
    except socket.timeout:
        return False, f"❌ 连接超时 → {ip}:{port}（请检查打印机是否在线）"
    except ConnectionRefusedError:
        return False, f"❌ 连接被拒绝 → {ip}:{port}（打印机未监听此端口）"
    except socket.gaierror:
        return False, f"❌ IP 地址无效 → {ip}"
    except Exception as e:
        return False, f"❌ 打印失败 ({type(e).__name__}): {e}"


def list_printers(config):
    """列出所有已配置打印机"""
    printers = config.get("printers", [])
    if not printers:
        print("\n⚠️  尚未配置任何打印机，请先运行 --setup 进行配置\n")
        return

    print("\n🖨️  已配置的打印机:")
    print("-" * 55)
    print(f"  {'别名':<8} {'IP':<16} {'端口':<6} {'类型':<10} {'备注'}")
    print("-" * 55)
    for p in printers:
        remark = p.get("remark", "")[:20]
        print(f"  {p['alias']:<8} {p['ip']:<16} {p['port']:<6} {p.get('type',''):<10} {remark}")
    print()
    print("  使用示例: python3 print_to_printer.py --name 后厨 --title \"任务单\" --content \"内容\"")


def guide():
    """新手指南 / 功能介绍"""
    print("""
╔══════════════════════════════════════════════════════╗
║         🖨️  美团热敏打印机技能 - 功能介绍            ║
╚══════════════════════════════════════════════════════╝

【功能一览】
  ① 打印任务单  - 向指定美团打印机发送格式化任务单
  ② 定时打印   - 设置定时任务，自动在指定时间打印
  ③ 多打印机   - 支持配置多台打印机，按名称/用途区分

【使用流程】
  第1步 → 运行 --setup 配置打印机（只需配置一次）
  第2步 → 使用 --name <别名> 发起打印

【快速命令】
  --setup    配置/管理打印机
  --list     查看已配置的打印机
  --guide    显示本指南

【示例】
  python3 print_to_printer.py --name 后厨 --title "早班任务" --content "打卡\\n解冻"
  python3 print_to_printer.py --ip 192.168.3.172 --port 9100 --title "测试" --content "内容"

【打印机类型参考】
  出菜档 / 分菜档 / 前台收银 / 后厨主打印 / 备菜档 / 小吃档

  首次使用？运行: python3 print_to_printer.py --setup
""")


def main():
    parser = argparse.ArgumentParser(
        description="美团热敏打印机 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--name", help="使用已配置打印机的别名")
    parser.add_argument("--ip", help="打印机 IP 地址（直接指定）")
    parser.add_argument("--port", type=int, default=9100, help="端口（默认 9100）")
    parser.add_argument("--title", help="打印标题")
    parser.add_argument("--content", help="打印内容（支持 \\n 换行）")
    parser.add_argument("--center", action="store_true", help="正文内容居中打印")
    parser.add_argument("--setup", action="store_true", help="进入引导配置模式")
    parser.add_argument("--list", action="store_true", help="列出所有已配置打印机")
    parser.add_argument("--guide", action="store_true", help="显示新手指南")

    args = parser.parse_args()

    # 加载配置
    config = get_config()

    # 引导配置
    if args.setup:
        from platform_utils import get_python_cmd
        py = get_python_cmd()
        os.system(f"{py} \"{SCRIPT_DIR}/init_printer.py\"")
        return

    # 列出打印机
    if args.list:
        list_printers(config)
        return

    # 功能指南
    if args.guide:
        guide()
        return

    # 打印任务
    if not args.title or not args.content:
        print("❌ 缺少必填参数 --title 和 --content")
        print("   使用 --guide 查看帮助，或 --setup 配置打印机\n")
        sys.exit(1)

    # 确定目标打印机
    if args.name:
        if not config:
            print("❌ 尚未配置打印机，请先运行: python3 print_to_printer.py --setup\n")
            sys.exit(1)
        printer = find_printer_by_alias(args.name, config)
        if not printer:
            aliases = [p["alias"] for p in config.get("printers", [])]
            print(f"❌ 未找到别名: '{args.name}'")
            print(f"   已配置: {', '.join(aliases)}")
            print("   使用 --list 查看全部\n")
            sys.exit(1)
        ip, port = printer["ip"], printer["port"]
        target = f"{args.name} ({ip}:{port})"
    elif args.ip:
        ip, port = args.ip, args.port
        target = f"{ip}:{port}"
    else:
        print("❌ 必须指定 --name 或 --ip\n")
        parser.print_help()
        sys.exit(1)

    # 执行打印
    success, msg = send_print(ip, port, args.title, args.content, center_content=args.center)
    print(msg)

    if success and args.name and config:
        printer = find_printer_by_alias(args.name, config)
        if printer:
            print(f"   📋 标题: {args.title}")
            print(f"   🖥️  设备: {printer['alias']} ({printer.get('type', '')})")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
