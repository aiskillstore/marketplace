#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SkillRadar Discover Client

调用 SkillRadar Discover 服务，根据任务目标、约束和关键词搜索匹配的技能。
"""

import argparse
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# SkillRadar Discover 服务地址
DISCOVER_API_BASE = "https://api.skillradar.quest"


def discover(task_goal: str, task_constraints: str, keywords: str, max_results: int) -> dict:
    """
    调用 SkillRadar Discover API
    """
    url = f"{DISCOVER_API_BASE}/discover"
    
    payload = {
        "task_goal": task_goal,
        "task_constraints": task_constraints,
        "keywords": keywords,
        "max_results": max_results,
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "skillradar-discover-client/0.1",
        },
        method="POST",
    )
    
    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return {
            "candidates": [],
            "note": f"服务请求失败 (HTTP {e.code}): {error_body}",
        }
    except URLError as e:
        return {
            "candidates": [],
            "note": f"无法连接到 SkillRadar 服务: {e.reason}",
        }
    except Exception as e:
        return {
            "candidates": [],
            "note": f"请求异常: {str(e)}",
        }


def parse_args():
    p = argparse.ArgumentParser(description="SkillRadar Discover Client")
    p.add_argument("--task_goal", required=True, help="任务目标（必选）")
    p.add_argument("--task_constraints", default="", help="任务约束（可选）")
    p.add_argument("--keywords", default="", help="关键词（可选，逗号分隔）")
    p.add_argument("--max_results", type=int, default=5, help="候选数量（可选，默认 5）")
    return p.parse_args()


def main():
    # Windows 控制台中文编码修复
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    args = parse_args()
    result = discover(
        task_goal=args.task_goal,
        task_constraints=args.task_constraints,
        keywords=args.keywords,
        max_results=max(1, min(args.max_results, 20)),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

