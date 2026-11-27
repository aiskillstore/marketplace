#!/usr/bin/env python3
"""skill-onboarding 状态与配置管理。

记录哪些 skill 已给过"用法卡"，并让行为可通过配置调整。
只用标准库，无第三方依赖。

用法:
    python onboarding_state.py check <skill-name>     # NEW / SEEN / SKIP
    python onboarding_state.py mark  <skill-name>     # 标记为已引导
    python onboarding_state.py list                   # 列出已引导的 skill
    python onboarding_state.py reset <skill-name>     # 撤销单个
    python onboarding_state.py reset --all            # 清空
    python onboarding_state.py new                    # 列出未引导的已安装 skill

    python onboarding_state.py config                 # 查看当前配置（含默认值）
    python onboarding_state.py config set <k> <v>     # 修改一项
    python onboarding_state.py config reset           # 恢复默认

所有命令支持 --json，输出机器可读结果。
"""

import json
import os
import sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

HOME = os.path.expanduser("~")
BASE = os.path.join(HOME, ".workbuddy", "skill-onboarding")
STATE_FILE = os.path.join(BASE, "state.json")
CONFIG_FILE = os.path.join(BASE, "config.json")
CARDS_DIR = os.path.join(BASE, "cards")

# 本 skill 自身与元 skill 不参与引导
EXCLUDE_ALWAYS = {"skill-onboarding", "skill-creator", "skill-tester"}

DEFAULT_CONFIG = {
    # 卡片语言：zh | en | auto（跟随用户说话的语言）
    "language": "zh",
    # 用户首次用完某 skill 后，是否自动补一张卡
    "auto_trigger": True,
    # 普通卡片行数上限
    "max_lines": 40,
    # 族卡行数上限
    "family_max_lines": 60,
    # 明确不引导的 skill 名单
    "exclude": [],
    # 与 skill-creator 协同：建/改完 skill 后自动补一次首跑验证
    "pair_with_skill_creator": True,
}


# ---------- 配置 ----------

def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user = json.load(f)
            if isinstance(user, dict):
                cfg.update(user)
        except Exception:
            pass
    return cfg


def save_config(cfg):
    os.makedirs(BASE, exist_ok=True)
    tmp = CONFIG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CONFIG_FILE)


def coerce(raw):
    """把字符串解析成合适的类型（布尔 / 数字 / 数组 / 字符串）。"""
    try:
        return json.loads(raw)
    except Exception:
        return raw


# ---------- 状态 ----------

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"version": 1, "onboarded": {}}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "onboarded" not in data:
            return {"version": 1, "onboarded": {}}
        return data
    except Exception:
        return {"version": 1, "onboarded": {}}


def save_state(state):
    os.makedirs(BASE, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)


def installed_skills():
    """扫描常见 skills 目录，返回 skill 名集合。"""
    roots = [
        os.path.join(HOME, ".workbuddy", "skills"),
        os.path.join(HOME, ".claude", "skills"),
    ]
    names = set()
    for root in roots:
        if not os.path.isdir(root):
            continue
        try:
            for entry in os.listdir(root):
                if entry.startswith("."):
                    continue
                if os.path.exists(os.path.join(root, entry, "SKILL.md")):
                    names.add(entry)
        except Exception:
            pass
    return names - EXCLUDE_ALWAYS


def find_card(skill):
    path = os.path.join(CARDS_DIR, skill + ".md")
    return path if os.path.exists(path) else None


def out(payload, as_json, plain):
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(plain)


# ---------- 命令 ----------

def cmd_check(args, as_json):
    if not args:
        print("error: check 需要 <skill-name>", file=sys.stderr)
        return 2
    skill = args[0]
    cfg = load_config()
    if skill in cfg.get("exclude", []):
        out({"skill": skill, "status": "SKIP", "reason": "在 exclude 名单中"},
            as_json, "SKIP")
        return 0
    state = load_state()
    rec = state["onboarded"].get(skill)
    seen = rec is not None
    payload = {
        "skill": skill,
        "status": "SEEN" if seen else "NEW",
        "onboarded_at": rec.get("at") if seen else None,
        "card": find_card(skill) if seen else None,
        "language": cfg.get("language"),
        "max_lines": cfg.get("max_lines"),
        "family_max_lines": cfg.get("family_max_lines"),
    }
    out(payload, as_json, payload["status"])
    return 0


def cmd_mark(args, as_json):
    if not args:
        print("error: mark 需要 <skill-name>", file=sys.stderr)
        return 2
    skill = args[0]
    state = load_state()
    state["onboarded"][skill] = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "card": find_card(skill),
    }
    save_state(state)
    payload = {"skill": skill, "status": "MARKED", "total": len(state["onboarded"])}
    out(payload, as_json, "MARKED " + skill)
    return 0


def cmd_list(args, as_json):
    state = load_state()
    items = sorted(state["onboarded"].items(), key=lambda kv: kv[1].get("at") or "")
    if as_json:
        print(json.dumps({"count": len(items), "onboarded": dict(items)},
                         ensure_ascii=False, indent=2))
    else:
        if not items:
            print("(还没有引导过任何 skill)")
        for name, rec in items:
            print("%s  %s" % (rec.get("at", "?"), name))
    return 0


def cmd_reset(args, as_json):
    if not args:
        print("error: reset 需要 <skill-name> 或 --all", file=sys.stderr)
        return 2
    state = load_state()
    if args[0] == "--all":
        n = len(state["onboarded"])
        state["onboarded"] = {}
        save_state(state)
        out({"status": "RESET_ALL", "removed": n}, as_json, "RESET_ALL %d" % n)
        return 0
    skill = args[0]
    existed = skill in state["onboarded"]
    state["onboarded"].pop(skill, None)
    save_state(state)
    out({"skill": skill, "status": "RESET" if existed else "NOT_FOUND"},
        as_json, "RESET" if existed else "NOT_FOUND")
    return 0 if existed else 1


def cmd_new(args, as_json):
    state = load_state()
    cfg = load_config()
    done = set(state["onboarded"].keys())
    pending = sorted(installed_skills() - done - set(cfg.get("exclude", [])))
    if as_json:
        print(json.dumps({"pending": pending, "count": len(pending)},
                         ensure_ascii=False, indent=2))
    else:
        if not pending:
            print("(全部已引导)")
        for name in pending:
            print(name)
    return 0


def cmd_config(args, as_json):
    cfg = load_config()
    if not args:
        out(cfg, as_json, json.dumps(cfg, ensure_ascii=False, indent=2))
        return 0

    action = args[0]
    if action == "set":
        if len(args) < 3:
            print("error: config set 需要 <key> <value>", file=sys.stderr)
            return 2
        key, raw = args[1], " ".join(args[2:])
        if key not in DEFAULT_CONFIG:
            print("error: 未知配置项 %s。可用: %s"
                  % (key, ", ".join(DEFAULT_CONFIG.keys())), file=sys.stderr)
            return 2
        value = coerce(raw)
        # 类型校验，避免写出坏配置
        if key in ("max_lines", "family_max_lines") and not isinstance(value, int):
            print("error: %s 需要整数" % key, file=sys.stderr)
            return 2
        if key in ("auto_trigger", "pair_with_skill_creator") and not isinstance(value, bool):
            print("error: %s 需要 true 或 false" % key, file=sys.stderr)
            return 2
        if key == "exclude" and not isinstance(value, list):
            print("error: exclude 需要 JSON 数组，例如 '[\"a\",\"b\"]'", file=sys.stderr)
            return 2
        if key == "language" and value not in ("zh", "en", "auto"):
            print("error: language 只能是 zh / en / auto", file=sys.stderr)
            return 2
        cfg[key] = value
        save_config(cfg)
        out({"key": key, "value": value, "status": "SET"}, as_json,
            "%s = %s" % (key, json.dumps(value, ensure_ascii=False)))
        return 0

    if action == "reset":
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        out({"status": "RESET", "config": DEFAULT_CONFIG}, as_json,
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2))
        return 0

    if action == "get":
        if len(args) < 2:
            print("error: config get 需要 <key>", file=sys.stderr)
            return 2
        key = args[1]
        out({key: cfg.get(key)}, as_json,
            json.dumps(cfg.get(key), ensure_ascii=False))
        return 0

    print("error: 未知 config 子命令 %s（可用 set / get / reset）" % action,
          file=sys.stderr)
    return 2


COMMANDS = {
    "check": cmd_check,
    "mark": cmd_mark,
    "list": cmd_list,
    "reset": cmd_reset,
    "new": cmd_new,
    "config": cmd_config,
}


def main():
    argv = sys.argv[1:]
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd not in COMMANDS:
        print("error: 未知命令 %s" % cmd, file=sys.stderr)
        print(__doc__)
        return 2
    return COMMANDS[cmd](argv[1:], as_json)


if __name__ == "__main__":
    sys.exit(main())
