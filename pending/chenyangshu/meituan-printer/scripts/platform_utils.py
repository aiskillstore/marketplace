#!/usr/bin/env python3
"""
跨平台工具函数 — macOS / Windows 兼容层
"""

import subprocess
import platform
import sys
import os
import shutil
from pathlib import Path


def get_os():
    """识别当前操作系统: 'macos' | 'windows' | 'linux'"""
    s = platform.system().lower()
    if s == "darwin":
        return "macos"
    elif s == "windows":
        return "windows"
    elif s == "linux":
        return "linux"
    return s


def get_python_cmd():
    """检测系统可用的 python 命令"""
    for cmd in ["python3", "python"]:
        path = shutil.which(cmd)
        if path:
            return cmd
    # 最后尝试 sys.executable
    return sys.executable


def get_scripts_dir():
    """获取 scripts 目录的绝对路径"""
    return Path(__file__).resolve().parent


def get_config_path():
    """获取 config.json 路径"""
    return get_scripts_dir() / "config.json"


def get_tasks_path():
    """获取 tasks.json 路径"""
    return get_scripts_dir() / "tasks.json"


def get_templates_path():
    """获取 task_templates.json 路径"""
    return get_scripts_dir() / "templates" / "task_templates.json"


def get_print_script_path():
    """获取 print_to_printer.py 路径"""
    return get_scripts_dir() / "print_to_printer.py"


def generate_task_id():
    """生成短任务 ID（如 task-001）"""
    tasks_file = get_tasks_path()
    if tasks_file.exists():
        try:
            import json
            with open(tasks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            existing_ids = [t["id"] for t in data.get("tasks", [])]
            n = len(existing_ids) + 1
        except Exception:
            n = 1
    else:
        n = 1
    return f"task-{n:03d}"


# ============== 系统定时任务导出 ==============

def export_system_task(task_config):
    """
    将定时任务导出为系统级定时任务。
    导出后即使 Web 服务关闭也会按时执行。

    Args:
        task_config: 任务配置字典，需包含 id, title, printer_alias, content, schedule

    Returns:
        (success, message)
    """
    os_type = get_os()

    if os_type == "macos":
        return _export_macos_launchd(task_config)
    elif os_type == "windows":
        return _export_windows_schtasks(task_config)
    else:
        return False, f"暂不支持 {os_type} 系统的定时任务导出"


def remove_system_task(task_id, task_title=""):
    """
    移除已导出的系统定时任务

    Returns:
        (success, message)
    """
    os_type = get_os()

    if os_type == "macos":
        return _remove_macos_launchd(task_id)
    elif os_type == "windows":
        return _remove_windows_schtasks(task_id, task_title)
    else:
        return False, f"暂不支持 {os_type} 系统"


# ============== macOS launchd ==============

def _build_launchd_plist(task_config):
    """生成 macOS launchd plist 内容"""
    python_cmd = get_python_cmd()
    print_script = str(get_print_script_path())
    schedule = task_config["schedule"]

    program_args = [
        python_cmd,
        print_script,
        "--name", task_config["printer_alias"],
        "--title", task_config["title"],
        "--content", task_config["content"]
    ]

    label = f"com.meituan-printer.{task_config['id']}"

    # 构建 StartCalendarInterval
    calendar_interval = {}
    if schedule["type"] == "daily":
        hour, minute = map(int, schedule["time"].split(":"))
        calendar_interval = {"Hour": hour, "Minute": minute}
    elif schedule["type"] == "weekly":
        hour, minute = map(int, schedule["time"].split(":"))
        calendar_interval = {
            "Weekday": schedule["day_of_week"],
            "Hour": hour,
            "Minute": minute
        }
    elif schedule["type"] == "monthly":
        hour, minute = map(int, schedule["time"].split(":"))
        calendar_interval = {
            "Day": schedule["day_of_month"],
            "Hour": hour,
            "Minute": minute
        }

    plist_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
        '<plist version="1.0">',
        '<dict>',
        f'    <key>Label</key><string>{label}</string>',
        '    <key>ProgramArguments</key><array>',
    ]
    for arg in program_args:
        plist_lines.append(f'        <string>{arg}</string>')
    plist_lines.append('    </array>')
    plist_lines.append('    <key>StartCalendarInterval</key><dict>')
    for k, v in calendar_interval.items():
        plist_lines.append(f'        <key>{k}</key><integer>{v}</integer>')
    plist_lines.append('    </dict>')
    plist_lines.append('    <key>StandardOutPath</key><string>/tmp/meituan-printer-{task_id}.log</string>'.format(task_id=task_config["id"]))
    plist_lines.append('    <key>StandardErrorPath</key><string>/tmp/meituan-printer-{task_id}.err</string>'.format(task_id=task_config["id"]))
    plist_lines.append('</dict>')
    plist_lines.append('</plist>')

    return "\n".join(plist_lines)


def _export_macos_launchd(task_config):
    """导出 macOS launchd 定时任务"""
    plist_content = _build_launchd_plist(task_config)
    label = f"com.meituan-printer.{task_config['id']}"
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_file = plist_dir / f"{label}.plist"

    try:
        plist_dir.mkdir(parents=True, exist_ok=True)
        with open(plist_file, "w", encoding="utf-8") as f:
            f.write(plist_content)
        # 加载任务
        subprocess.run(["launchctl", "load", str(plist_file)], capture_output=True, timeout=10)
        return True, f"已导出到 {plist_file}，并已加载到 launchd"
    except Exception as e:
        return False, f"导出失败: {e}"


def _remove_macos_launchd(task_id):
    """移除 macOS launchd 定时任务"""
    label = f"com.meituan-printer.{task_id}"
    plist_file = Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"

    try:
        if plist_file.exists():
            subprocess.run(["launchctl", "unload", str(plist_file)], capture_output=True, timeout=10)
            plist_file.unlink()
            return True, f"已移除系统定时任务 {label}"
        else:
            return False, f"未找到系统定时任务文件 {plist_file}"
    except Exception as e:
        return False, f"移除失败: {e}"


# ============== Windows Task Scheduler ==============

def _build_schtasks_command(task_config):
    """构建 Windows schtasks 命令"""
    python_cmd = get_python_cmd()
    print_script = str(get_print_script_path())
    schedule = task_config["schedule"]
    task_name = f"MeituanPrinter-{task_config['id']}"

    # 构建执行命令
    exec_cmd = f'"{python_cmd}" "{print_script}" --name "{task_config["printer_alias"]}" --title "{task_config["title"]}" --content "{task_config["content"]}"'

    base_cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", exec_cmd,
        "/f"  # 强制覆盖
    ]

    if schedule["type"] == "daily":
        base_cmd.extend(["/sc", "daily", "/st", schedule["time"]])
    elif schedule["type"] == "weekly":
        weekday_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        dow = weekday_names[schedule["day_of_week"] - 1] if schedule["day_of_week"] <= 7 else "mon"
        base_cmd.extend(["/sc", "weekly", "/d", dow, "/st", schedule["time"]])
    elif schedule["type"] == "monthly":
        base_cmd.extend(["/sc", "monthly", "/d", str(schedule["day_of_month"]), "/st", schedule["time"]])

    return base_cmd, task_name


def _export_windows_schtasks(task_config):
    """导出 Windows 定时任务"""
    try:
        cmd, task_name = _build_schtasks_command(task_config)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return True, f"已创建系统定时任务 \"{task_name}\""
        else:
            return False, f"创建失败: {result.stderr.strip() or result.stdout.strip()}"
    except FileNotFoundError:
        return False, "未找到 schtasks 命令，请确认使用 Windows 系统"
    except Exception as e:
        return False, f"导出失败: {e}"


def _remove_windows_schtasks(task_id, task_title=""):
    """移除 Windows 定时任务"""
    task_name = f"MeituanPrinter-{task_id}"
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return True, f"已移除系统定时任务 \"{task_name}\""
        else:
            return False, f"移除失败: {result.stderr.strip() or result.stdout.strip()}"
    except Exception as e:
        return False, f"移除失败: {e}"
