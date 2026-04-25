#!/usr/bin/env python3
"""
美团热敏打印机 - Web 管理界面后端
Flask + APScheduler，支持打印机配置管理和定时打印任务
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# 确保能导入同目录的模块
sys.path.insert(0, str(Path(__file__).resolve().parent))
from platform_utils import (
    get_scripts_dir, get_config_path, get_tasks_path,
    get_templates_path, get_print_script_path,
    generate_task_id, get_python_cmd, get_os,
    export_system_task, remove_system_task
)

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# ============== 数据读写 ==============

def load_json(filepath, default=None):
    """安全加载 JSON 文件"""
    if default is None:
        default = {"version": "1.0"}
    path = Path(filepath)
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def save_json(filepath, data):
    """保存 JSON 文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_config():
    return load_json(get_config_path(), {"version": "1.0", "printers": []})


def get_printer_types_path():
    return get_scripts_dir() / "printer_types.json"


def get_printer_types():
    return load_json(get_printer_types_path(), {"version": "1.0", "types": ["其他"]})


def save_printer_types(types_data):
    save_json(get_printer_types_path(), types_data)


def save_config(config):
    config["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_json(get_config_path(), config)


def get_tasks():
    return load_json(get_tasks_path(), {"version": "1.0", "tasks": []})


def save_tasks(tasks_data):
    save_json(get_tasks_path(), tasks_data)


def get_templates():
    return load_json(get_templates_path(), {"version": "1.0", "templates": []})


# ============== 打印执行 ==============

def execute_print(printer_alias, title, content, center_content=False):
    """执行打印任务（通过命令行调用 print_to_printer.py）"""
    py = get_python_cmd()
    script = str(get_print_script_path())
    cmd = [
        py, script,
        "--name", printer_alias,
        "--title", title,
        "--content", content
    ]
    if center_content:
        cmd.append("--center")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return True, result.stdout.strip() or "打印成功"
        else:
            return False, result.stderr.strip() or result.stdout.strip() or "打印失败"
    except subprocess.TimeoutExpired:
        return False, "打印超时（15秒）"
    except Exception as e:
        return False, f"执行异常: {e}"


def check_printer_connection(ip, port):
    """测试打印机连通性"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip, int(port)))
        s.close()
        return True, "连接成功"
    except socket.timeout:
        return False, "连接超时"
    except ConnectionRefusedError:
        return False, "连接被拒绝"
    except socket.gaierror:
        return False, "IP 地址无效"
    except Exception as e:
        return False, f"连接失败: {e}"


# ============== APScheduler 任务管理 ==============

def add_scheduler_job(task):
    """将任务添加到 APScheduler"""
    if not task.get("enabled"):
        return

    job_id = task["id"]
    schedule = task["schedule"]

    if schedule["type"] == "daily":
        hour, minute = map(int, schedule["time"].split(":"))
        trigger = CronTrigger(hour=hour, minute=minute)
    elif schedule["type"] == "weekly":
        hour, minute = map(int, schedule["time"].split(":"))
        trigger = CronTrigger(day_of_week=schedule["day_of_week"] - 1, hour=hour, minute=minute)
    elif schedule["type"] == "monthly":
        hour, minute = map(int, schedule["time"].split(":"))
        trigger = CronTrigger(day=schedule["day_of_month"], hour=hour, minute=minute)
    else:
        return

    scheduler.add_job(
        _scheduled_print,
        trigger=trigger,
        id=job_id,
        replace_existing=True,
        args=[task["printer_alias"], task["title"], task["content"], task.get("content_centered", False)]
    )


def remove_scheduler_job(task_id):
    """从 APScheduler 移除任务"""
    try:
        scheduler.remove_job(task_id)
    except Exception:
        pass


def _scheduled_print(printer_alias, title, content, center_content=False):
    """APScheduler 回调函数"""
    success, msg = execute_print(printer_alias, title, content, center_content=center_content)
    print(f"[定时打印 {datetime.now().strftime('%H:%M:%S')}] {title} -> {msg}")
    return success, msg


def load_all_scheduler_jobs():
    """启动时加载所有已启用的任务到调度器"""
    tasks_data = get_tasks()
    for task in tasks_data.get("tasks", []):
        if task.get("enabled"):
            add_scheduler_job(task)


# ============== 页面路由 ==============

@app.route("/")
def index():
    return render_template("index.html")


# ============== 打印机 API ==============

@app.route("/api/printers", methods=["GET"])
def list_printers():
    config = get_config()
    return jsonify({"success": True, "printers": config.get("printers", [])})


@app.route("/api/printers", methods=["POST"])
def add_printer():
    config = get_config()
    data = request.json

    alias = data.get("alias", "").strip()
    ip = data.get("ip", "").strip()
    port = int(data.get("port", 9100))
    ptype = data.get("type", "").strip()
    remark = data.get("remark", "").strip()

    if not alias or not ip:
        return jsonify({"success": False, "message": "别名和 IP 为必填项"}), 400

    # 检查别名重复
    for p in config.get("printers", []):
        if p["alias"] == alias:
            return jsonify({"success": False, "message": f"别名 '{alias}' 已存在"}), 400

    printer = {
        "alias": alias,
        "ip": ip,
        "port": port,
        "type": ptype,
        "remark": remark
    }

    if "printers" not in config:
        config["printers"] = []
    config["printers"].append(printer)
    save_config(config)

    return jsonify({"success": True, "message": f"打印机 '{alias}' 添加成功", "printer": printer})


@app.route("/api/printers/<alias>", methods=["PUT"])
def update_printer(alias):
    config = get_config()
    data = request.json

    for i, p in enumerate(config.get("printers", [])):
        if p["alias"] == alias:
            new_alias = data.get("alias", alias).strip()
            # 检查新别名是否与其他打印机冲突
            if new_alias != alias:
                for other in config["printers"]:
                    if other["alias"] == new_alias:
                        return jsonify({"success": False, "message": f"别名 '{new_alias}' 已存在"}), 400

            config["printers"][i] = {
                "alias": new_alias,
                "ip": data.get("ip", p["ip"]).strip(),
                "port": int(data.get("port", p["port"])),
                "type": data.get("type", p.get("type", "")).strip(),
                "remark": data.get("remark", p.get("remark", "")).strip()
            }
            save_config(config)
            return jsonify({"success": True, "message": "打印机更新成功", "printer": config["printers"][i]})

    return jsonify({"success": False, "message": f"未找到打印机 '{alias}'"}), 404


@app.route("/api/printers/<alias>", methods=["DELETE"])
def delete_printer(alias):
    config = get_config()
    printers = config.get("printers", [])
    new_printers = [p for p in printers if p["alias"] != alias]

    if len(new_printers) == len(printers):
        return jsonify({"success": False, "message": f"未找到打印机 '{alias}'"}), 404

    config["printers"] = new_printers
    save_config(config)
    return jsonify({"success": True, "message": f"打印机 '{alias}' 已删除"})


@app.route("/api/printers/<alias>/test", methods=["POST"])
def test_printer(alias):
    config = get_config()
    for p in config.get("printers", []):
        if p["alias"] == alias:
            success, msg = check_printer_connection(p["ip"], p["port"])
            return jsonify({"success": success, "message": msg})

    return jsonify({"success": False, "message": f"未找到打印机 '{alias}'"}), 404


# ============== 定时任务 API ==============

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    tasks_data = get_tasks()
    # 补充下次执行时间信息
    for task in tasks_data.get("tasks", []):
        task["next_run"] = _get_next_run_time(task)
    return jsonify({"success": True, "tasks": tasks_data.get("tasks", [])})


@app.route("/api/tasks", methods=["POST"])
def add_task():
    tasks_data = get_tasks()
    data = request.json

    title = data.get("title", "").strip()
    printer_alias = data.get("printer_alias", "").strip()
    content = data.get("content", "").strip()
    schedule = data.get("schedule", {})

    if not title or not printer_alias or not content:
        return jsonify({"success": False, "message": "标题、目标打印机和内容为必填项"}), 400

    # 验证打印机存在
    config = get_config()
    found = any(p["alias"] == printer_alias for p in config.get("printers", []))
    if not found:
        return jsonify({"success": False, "message": f"打印机 '{printer_alias}' 不存在"}), 400

    # 验证调度参数
    sched_type = schedule.get("type", "")
    if sched_type not in ("daily", "weekly", "monthly"):
        return jsonify({"success": False, "message": "频率类型必须为 daily/weekly/monthly"}), 400

    if not schedule.get("time"):
        return jsonify({"success": False, "message": "请设置执行时间"}), 400

    if sched_type == "weekly" and not schedule.get("day_of_week"):
        return jsonify({"success": False, "message": "请选择星期几"}), 400

    if sched_type == "monthly" and not schedule.get("day_of_month"):
        return jsonify({"success": False, "message": "请选择几号"}), 400

    task_id = generate_task_id()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    task = {
        "id": task_id,
        "title": title,
        "printer_alias": printer_alias,
        "content": content,
        "content_centered": data.get("content_centered", False),
        "schedule": {
            "type": sched_type,
            "time": schedule["time"],
            "day_of_week": schedule.get("day_of_week"),
            "day_of_month": schedule.get("day_of_month")
        },
        "enabled": data.get("enabled", True),
        "exported_to_system": False,
        "created_at": now,
        "updated_at": now
    }

    if "tasks" not in tasks_data:
        tasks_data["tasks"] = []
    tasks_data["tasks"].append(task)
    save_tasks(tasks_data)

    # 如果启用，添加到调度器
    if task["enabled"]:
        add_scheduler_job(task)

    return jsonify({"success": True, "message": "任务创建成功", "task": task})


@app.route("/api/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    tasks_data = get_tasks()
    data = request.json

    for i, task in enumerate(tasks_data.get("tasks", [])):
        if task["id"] == task_id:
            # 如果修改了打印机，验证新打印机存在
            new_alias = data.get("printer_alias", task["printer_alias"])
            config = get_config()
            found = any(p["alias"] == new_alias for p in config.get("printers", []))
            if not found:
                return jsonify({"success": False, "message": f"打印机 '{new_alias}' 不存在"}), 400

            tasks_data["tasks"][i]["title"] = data.get("title", task["title"])
            tasks_data["tasks"][i]["printer_alias"] = new_alias
            tasks_data["tasks"][i]["content"] = data.get("content", task["content"])
            tasks_data["tasks"][i]["content_centered"] = data.get("content_centered", task.get("content_centered", False))
            tasks_data["tasks"][i]["enabled"] = data.get("enabled", task["enabled"])
            tasks_data["tasks"][i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

            if "schedule" in data:
                tasks_data["tasks"][i]["schedule"] = {
                    "type": data["schedule"].get("type", task["schedule"]["type"]),
                    "time": data["schedule"].get("time", task["schedule"]["time"]),
                    "day_of_week": data["schedule"].get("day_of_week", task["schedule"].get("day_of_week")),
                    "day_of_month": data["schedule"].get("day_of_month", task["schedule"].get("day_of_month"))
                }

            save_tasks(tasks_data)

            # 重建调度
            remove_scheduler_job(task_id)
            if tasks_data["tasks"][i]["enabled"]:
                add_scheduler_job(tasks_data["tasks"][i])

            return jsonify({"success": True, "message": "任务更新成功", "task": tasks_data["tasks"][i]})

    return jsonify({"success": False, "message": f"未找到任务 '{task_id}'"}), 404


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks_data = get_tasks()
    old_len = len(tasks_data.get("tasks", []))
    tasks_data["tasks"] = [t for t in tasks_data.get("tasks", []) if t["id"] != task_id]

    if len(tasks_data["tasks"]) == old_len:
        return jsonify({"success": False, "message": f"未找到任务 '{task_id}'"}), 404

    save_tasks(tasks_data)
    remove_scheduler_job(task_id)

    # 如果已导出到系统，也一并移除
    task = next((t for t in tasks_data.get("tasks", []) if t["id"] == task_id), None)
    # （已从列表中删除，直接尝试移除系统任务）
    remove_system_task(task_id)

    return jsonify({"success": True, "message": "任务已删除"})


@app.route("/api/tasks/<task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    tasks_data = get_tasks()
    for task in tasks_data.get("tasks", []):
        if task["id"] == task_id:
            task["enabled"] = not task["enabled"]
            task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_tasks(tasks_data)

            if task["enabled"]:
                add_scheduler_job(task)
                return jsonify({"success": True, "message": "任务已启用", "enabled": True})
            else:
                remove_scheduler_job(task_id)
                return jsonify({"success": True, "message": "任务已暂停", "enabled": False})

    return jsonify({"success": False, "message": f"未找到任务 '{task_id}'"}), 404


@app.route("/api/tasks/<task_id>/run", methods=["POST"])
def run_task_now(task_id):
    """立即执行一次打印任务"""
    tasks_data = get_tasks()
    for task in tasks_data.get("tasks", []):
        if task["id"] == task_id:
            success, msg = execute_print(task["printer_alias"], task["title"], task["content"],
                                       center_content=task.get("content_centered", False))
            return jsonify({"success": success, "message": msg})

    return jsonify({"success": False, "message": f"未找到任务 '{task_id}'"}), 404


@app.route("/api/tasks/<task_id>/export", methods=["POST"])
def export_task(task_id):
    """导出为系统定时任务"""
    tasks_data = get_tasks()
    for task in tasks_data.get("tasks", []):
        if task["id"] == task_id:
            success, msg = export_system_task(task)
            if success:
                task["exported_to_system"] = True
                task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_tasks(tasks_data)
            return jsonify({"success": success, "message": msg})

    return jsonify({"success": False, "message": f"未找到任务 '{task_id}'"}), 404


@app.route("/api/tasks/<task_id>/unexport", methods=["POST"])
def unexport_task(task_id):
    """移除系统定时任务"""
    tasks_data = get_tasks()
    for task in tasks_data.get("tasks", []):
        if task["id"] == task_id:
            success, msg = remove_system_task(task_id, task.get("title", ""))
            if success:
                task["exported_to_system"] = False
                task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_tasks(tasks_data)
            return jsonify({"success": success, "message": msg})

    return jsonify({"success": False, "message": f"未找到任务 '{task_id}'"}), 404


# ============== 打印机类型 API ==============

@app.route("/api/printer-types", methods=["GET"])
def list_printer_types():
    types_data = get_printer_types()
    return jsonify({"success": True, "types": types_data.get("types", [])})


@app.route("/api/printer-types", methods=["POST"])
def add_printer_type():
    types_data = get_printer_types()
    data = request.json
    new_type = data.get("type", "").strip()

    if not new_type:
        return jsonify({"success": False, "message": "类型名称不能为空"}), 400

    types = types_data.get("types", [])
    if new_type in types:
        return jsonify({"success": False, "message": f"类型 '{new_type}' 已存在"}), 400

    types.append(new_type)
    types_data["types"] = types
    save_printer_types(types_data)

    return jsonify({"success": True, "message": f"类型 '{new_type}' 添加成功", "type": new_type})


@app.route("/api/printer-types/<type_name>", methods=["DELETE"])
def delete_printer_type(type_name):
    types_data = get_printer_types()
    types = types_data.get("types", [])

    if type_name not in types:
        return jsonify({"success": False, "message": f"类型 '{type_name}' 不存在"}), 404

    # 检查是否有打印机正在使用此类型
    config = get_config()
    in_use = [p["alias"] for p in config.get("printers", []) if p.get("type") == type_name]
    if in_use:
        return jsonify({
            "success": False,
            "message": f"类型 '{type_name}' 正在被打印机 {', '.join(in_use)} 使用，请先修改打印机类型"
        }), 400

    types.remove(type_name)
    types_data["types"] = types
    save_printer_types(types_data)

    return jsonify({"success": True, "message": f"类型 '{type_name}' 已删除"})


# ============== 模板 API ==============

@app.route("/api/templates", methods=["GET"])
def list_templates():
    templates_data = get_templates()
    return jsonify({"success": True, "templates": templates_data.get("templates", [])})


@app.route("/api/templates", methods=["POST"])
def add_template():
    templates_data = get_templates()
    data = request.json

    name = data.get("name", "").strip()
    category = data.get("category", "通用").strip()
    content = data.get("content", "").strip()

    if not name or not content:
        return jsonify({"success": False, "message": "模板名称和内容为必填项"}), 400

    tpl_id = f"tpl-{len(templates_data.get('templates', [])) + 1:03d}"

    template = {
        "id": tpl_id,
        "name": name,
        "category": category,
        "content": content,
        "content_centered": data.get("content_centered", False),
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }

    if "templates" not in templates_data:
        templates_data["templates"] = []
    templates_data["templates"].append(template)
    save_json(get_templates_path(), templates_data)

    return jsonify({"success": True, "message": "模板创建成功", "template": template})


@app.route("/api/templates/<tpl_id>", methods=["PUT"])
def update_template(tpl_id):
    templates_data = get_templates()
    data = request.json

    for i, tpl in enumerate(templates_data.get("templates", [])):
        if tpl["id"] == tpl_id:
            templates_data["templates"][i]["name"] = data.get("name", tpl["name"])
            templates_data["templates"][i]["category"] = data.get("category", tpl.get("category", "通用"))
            templates_data["templates"][i]["content"] = data.get("content", tpl["content"])
            templates_data["templates"][i]["content_centered"] = data.get("content_centered", tpl.get("content_centered", False))
            save_json(get_templates_path(), templates_data)
            return jsonify({"success": True, "message": "模板更新成功", "template": templates_data["templates"][i]})

    return jsonify({"success": False, "message": f"未找到模板 '{tpl_id}'"}), 404


@app.route("/api/templates/<tpl_id>", methods=["DELETE"])
def delete_template(tpl_id):
    templates_data = get_templates()
    old_len = len(templates_data.get("templates", []))
    templates_data["templates"] = [t for t in templates_data.get("templates", []) if t["id"] != tpl_id]

    if len(templates_data["templates"]) == old_len:
        return jsonify({"success": False, "message": f"未找到模板 '{tpl_id}'"}), 404

    save_json(get_templates_path(), templates_data)
    return jsonify({"success": True, "message": "模板已删除"})


# ============== 系统信息 API ==============

@app.route("/api/info", methods=["GET"])
def system_info():
    return jsonify({
        "success": True,
        "os": get_os(),
        "python": get_python_cmd(),
        "scheduler_running": scheduler.running
    })


# ============== 辅助函数 ==============

def _get_next_run_time(task):
    """获取任务下次执行时间（用于前端显示）"""
    if not task.get("enabled"):
        return None
    try:
        job = scheduler.get_job(task["id"])
        if job and job.next_run_time:
            return job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    return None


# ============== 启动 ==============

if __name__ == "__main__":
    # 启动时加载所有已启用的定时任务
    load_all_scheduler_jobs()
    port = 5000
    # macOS AirPlay Receiver 默认占用 5000，自动切换到 5001
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", port))
        sock.close()
    except OSError:
        port = 5001
        sock.close()

    print(f"\n🖨️  美团打印机 Web 管理界面")
    print(f"   系统平台: {get_os()}")
    print(f"   Python: {get_python_cmd()}")
    print(f"   访问地址: http://localhost:{port}")
    print(f"   按 Ctrl+C 停止服务\n")

    app.run(host="0.0.0.0", port=port, debug=False)
