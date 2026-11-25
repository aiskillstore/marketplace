#!/usr/bin/env python3
"""cost_guard.py -- tiny local spend ledger + cap guard for Claude Code.

Stdlib only. No network, no account access, no real billing data.

What it does:
  - records ESTIMATED spend (token counts x API list prices) in a local JSON ledger
  - enforces a daily USD cap and a per-task USD cap
  - counts repeated failures per signature and brakes error loops

What it does NOT do (see README.md):
  - it cannot see your real Anthropic bill or plan quota
  - it cannot stop a model API call; Claude Code hooks only gate tool calls
  - every cost here is an ESTIMATE from token counts you record

Usage:
  cost_guard.py estimate --model sonnet --input 1000000 --output 500000 [--cache-read 2000000]
  cost_guard.py record   --model sonnet --input 1000000 --output 500000 [--task NAME] [--session NAME]
  cost_guard.py status   [--task NAME]
  cost_guard.py check    [--task NAME] [--est-cost 2.50]
  cost_guard.py fail     --signature "tests-fail:auth" [--task NAME]
  cost_guard.py config

Exit codes: 0 = OK / under cap, 1 = usage or file error, 2 = BLOCKED (cap hit or loop brake).

Environment:
  COST_GUARD_LEDGER      ledger path (default ~/.cost-guard/ledger.json)
  COST_GUARD_CONFIG      config path (default ~/.cost-guard/config.json)
  COST_GUARD_DAILY_CAP   daily cap in USD (default 10)
  COST_GUARD_TASK_CAP    per-task cap in USD (default 5)
  COST_GUARD_LOOP_LIMIT  same-signature failures before the brake (default 3)
  COST_GUARD_SESSION     session label (default "default")
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime

DEFAULT_PRICING = {
    # API list prices per 1M tokens, Nov 2026. Estimates only -- verify
    # current pricing and override them in config.json if they change.
    "opus": {"in": 5.0, "out": 25.0},
    "sonnet": {"in": 3.0, "out": 15.0},
    "haiku": {"in": 1.0, "out": 5.0},
    "gpt-5": {"in": 1.25, "out": 10.0},
    "gemini-2.5-pro": {"in": 1.25, "out": 10.0},
    "default": {"in": 3.0, "out": 15.0},
}

DEFAULTS = {
    "daily_cap_usd": 10.0,
    "task_cap_usd": 5.0,
    "loop_limit": 3,
    "default_model": "sonnet",
    "cache_read_fraction": 0.1,
}


def _default_ledger_path():
    return os.path.join(os.path.expanduser("~"), ".cost-guard", "ledger.json")


def _default_config_path():
    return os.path.join(os.path.expanduser("~"), ".cost-guard", "config.json")


def _env_float(name):
    try:
        return float(os.environ[name])
    except (KeyError, ValueError):
        return None


def _env_int(name):
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return None


def load_config():
    cfg = dict(DEFAULTS)
    cfg["pricing"] = {model: dict(prices) for model, prices in DEFAULT_PRICING.items()}
    path = os.environ.get("COST_GUARD_CONFIG") or _default_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                user = json.load(f)
        except (OSError, ValueError) as exc:
            print(f"cost-guard: cannot read config {path}: {exc}", file=sys.stderr)
            sys.exit(1)
        if isinstance(user, dict):
            for key in ("daily_cap_usd", "task_cap_usd", "loop_limit",
                        "default_model", "cache_read_fraction"):
                if key in user:
                    cfg[key] = user[key]
            if isinstance(user.get("pricing"), dict):
                for model, prices in user["pricing"].items():
                    if isinstance(prices, dict) and "in" in prices and "out" in prices:
                        cfg["pricing"][model] = prices
    daily = _env_float("COST_GUARD_DAILY_CAP")
    if daily is not None:
        cfg["daily_cap_usd"] = daily
    task = _env_float("COST_GUARD_TASK_CAP")
    if task is not None:
        cfg["task_cap_usd"] = task
    loop = _env_int("COST_GUARD_LOOP_LIMIT")
    if loop is not None:
        cfg["loop_limit"] = loop
    return cfg, path


def ledger_path():
    return os.environ.get("COST_GUARD_LEDGER") or _default_ledger_path()


def load_ledger():
    path = ledger_path()
    if not os.path.exists(path):
        return {"entries": [], "failures": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cost-guard: cannot read ledger {path}: {exc}", file=sys.stderr)
        sys.exit(1)
    if isinstance(data, list):  # very old format: bare list of entries
        return {"entries": data, "failures": []}
    if not isinstance(data, dict):
        print(f"cost-guard: ledger {path} has unexpected shape", file=sys.stderr)
        sys.exit(1)
    data.setdefault("entries", [])
    data.setdefault("failures", [])
    return data


def save_ledger(data):
    path = ledger_path()
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory or ".", prefix=".ledger-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def today_str():
    return datetime.now().date().isoformat()


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def price_for(cfg, model):
    pricing = cfg["pricing"]
    if model in pricing:
        return pricing[model], False
    return pricing["default"], True


def cost_of(cfg, model, input_tokens, output_tokens, cache_read_tokens=0):
    prices, used_default = price_for(cfg, model)
    cache_fraction = float(cfg.get("cache_read_fraction", 0.1))
    cost = (
        input_tokens / 1_000_000 * float(prices["in"])
        + output_tokens / 1_000_000 * float(prices["out"])
        + cache_read_tokens / 1_000_000 * float(prices["in"]) * cache_fraction
    )
    return round(cost, 4), used_default


def _non_negative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be 0 or more")
    return number


def cmd_estimate(cfg, args):
    cost, used_default = cost_of(cfg, args.model, args.input, args.output, args.cache_read)
    print(f"model: {args.model}" + (" (unknown model -- default pricing used)" if used_default else ""))
    print(f"input tokens: {args.input:,}")
    print(f"output tokens: {args.output:,}")
    print(f"cache-read tokens: {args.cache_read:,}")
    print(f"estimated cost: ${cost:.4f}")
    print("note: estimate only -- list prices, Nov 2026. Real billing may differ.")
    return 0


def cmd_record(cfg, args):
    cost, used_default = cost_of(cfg, args.model, args.input, args.output, args.cache_read)
    data = load_ledger()
    session = os.environ.get("COST_GUARD_SESSION", "default")
    data["entries"].append({
        "ts": now_iso(),
        "date": today_str(),
        "session": session,
        "task": args.task,
        "model": args.model,
        "input": args.input,
        "output": args.output,
        "cache_read": args.cache_read,
        "cost_usd": cost,
    })
    save_ledger(data)
    if used_default:
        print(f"note: unknown model '{args.model}' -- default pricing used", file=sys.stderr)
    print(f"recorded: ${cost:.4f} for task '{args.task}' ({args.model})")
    return cmd_status(cfg, args)


def _totals(data, date, task=None):
    total = 0.0
    task_total = 0.0
    count = 0
    for entry in data["entries"]:
        if entry.get("date") != date:
            continue
        count += 1
        total += float(entry.get("cost_usd", 0.0))
        if task is not None and entry.get("task") == task:
            task_total += float(entry.get("cost_usd", 0.0))
    return count, round(total, 4), round(task_total, 4)


def cmd_status(cfg, args):
    data = load_ledger()
    date = today_str()
    task = getattr(args, "task", None)
    count, total, task_total = _totals(data, date, task)
    daily_cap = float(cfg["daily_cap_usd"])
    task_cap = float(cfg["task_cap_usd"])
    print(f"cost-guard status -- {date}")
    print(f"entries today: {count}")
    print(f"spent today: ${total:.2f} / daily cap ${daily_cap:.2f}", end="")
    if total > daily_cap:
        print(f" -- OVER CAP by ${total - daily_cap:.2f}")
    else:
        print(f" -- remaining ${daily_cap - total:.2f}")
    if task is not None:
        print(f"task '{task}': ${task_total:.2f} / task cap ${task_cap:.2f}", end="")
        if task_total > task_cap:
            print(f" -- OVER CAP by ${task_total - task_cap:.2f}")
        else:
            print(f" -- remaining ${task_cap - task_total:.2f}")
    print(f"ledger: {ledger_path()}")
    return 0


def cmd_check(cfg, args):
    data = load_ledger()
    date = today_str()
    task = getattr(args, "task", None)
    est = float(args.est_cost)
    _, total, task_total = _totals(data, date, task)
    daily_cap = float(cfg["daily_cap_usd"])
    task_cap = float(cfg["task_cap_usd"])
    if total + est > daily_cap:
        print(f"cost-guard: BLOCKED -- today ${total:.2f} + est ${est:.2f} "
              f"would exceed daily cap ${daily_cap:.2f}")
        return 2
    if task is not None and task_total + est > task_cap:
        print(f"cost-guard: BLOCKED -- task '{task}' ${task_total:.2f} + est ${est:.2f} "
              f"would exceed task cap ${task_cap:.2f}")
        return 2
    print(f"cost-guard: OK -- today ${total:.2f} / ${daily_cap:.2f}"
          + (f", task '{task}' ${task_total:.2f} / ${task_cap:.2f}" if task is not None else ""))
    return 0


def cmd_fail(cfg, args):
    data = load_ledger()
    date = today_str()
    session = os.environ.get("COST_GUARD_SESSION", "default")
    data["failures"].append({
        "ts": now_iso(),
        "date": date,
        "session": session,
        "task": args.task,
        "signature": args.signature,
    })
    save_ledger(data)
    count = sum(
        1 for f in data["failures"]
        if f.get("date") == date and f.get("signature") == args.signature
    )
    limit = int(cfg["loop_limit"])
    if count >= limit:
        print(f"cost-guard: LOOP BRAKE -- '{args.signature}' failed {count} times "
              f"today (limit {limit}). Stop, report, and ask the user before retrying.")
        return 2
    print(f"cost-guard: failure {count}/{limit} for '{args.signature}' -- "
          f"{limit - count} retries left before the brake.")
    return 0


def cmd_config(cfg, path):
    print(f"config: {path}")
    print(f"daily cap: ${float(cfg['daily_cap_usd']):.2f}")
    print(f"task cap: ${float(cfg['task_cap_usd']):.2f}")
    print(f"loop limit: {int(cfg['loop_limit'])} identical failures")
    print(f"default model: {cfg['default_model']}")
    print(f"cache-read fraction of input price: {float(cfg.get('cache_read_fraction', 0.1))}")
    print("pricing per 1M tokens (in/out USD):")
    for model in sorted(cfg["pricing"]):
        prices = cfg["pricing"][model]
        print(f"  {model}: ${float(prices['in']):.2f} / ${float(prices['out']):.2f}")
    print(f"ledger: {ledger_path()}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="cost_guard.py",
        description="Local spend ledger + cap guard for Claude Code. Estimates only -- see README.md.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("estimate", help="estimate the cost of a run from token counts")
    p.add_argument("--model", default=None, help="model key (default: config default_model)")
    p.add_argument("--input", type=_non_negative, required=True, help="input tokens")
    p.add_argument("--output", type=_non_negative, required=True, help="output tokens")
    p.add_argument("--cache-read", type=_non_negative, default=0, help="cache-read tokens")

    p = sub.add_parser("record", help="record a finished run in the ledger")
    p.add_argument("--model", default=None, help="model key (default: config default_model)")
    p.add_argument("--input", type=_non_negative, required=True, help="input tokens")
    p.add_argument("--output", type=_non_negative, required=True, help="output tokens")
    p.add_argument("--cache-read", type=_non_negative, default=0, help="cache-read tokens")
    p.add_argument("--task", default="default", help="task label")
    p.add_argument("--session", default=None, help="session label (default: $COST_GUARD_SESSION)")

    p = sub.add_parser("status", help="show today's spend vs caps")
    p.add_argument("--task", default=None, help="also show one task's spend")

    p = sub.add_parser("check", help="exit 2 if caps would be exceeded (for hooks)")
    p.add_argument("--task", default=None, help="task label to check")
    p.add_argument("--est-cost", type=float, default=0.0, help="estimated cost of the next run")

    p = sub.add_parser("fail", help="record a failure; brake the loop at the limit")
    p.add_argument("--signature", required=True, help="stable failure signature, e.g. 'tests-fail:auth'")
    p.add_argument("--task", default="default", help="task label")

    sub.add_parser("config", help="show effective caps, pricing and paths")

    args = parser.parse_args(argv)
    cfg, config_path = load_config()
    if getattr(args, "model", None) is None:
        args.model = cfg["default_model"]
    if getattr(args, "session", None):
        os.environ["COST_GUARD_SESSION"] = args.session

    if args.command == "estimate":
        return cmd_estimate(cfg, args)
    if args.command == "record":
        return cmd_record(cfg, args)
    if args.command == "status":
        return cmd_status(cfg, args)
    if args.command == "check":
        return cmd_check(cfg, args)
    if args.command == "fail":
        return cmd_fail(cfg, args)
    if args.command == "config":
        return cmd_config(cfg, config_path)
    parser.error(f"unknown command {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
