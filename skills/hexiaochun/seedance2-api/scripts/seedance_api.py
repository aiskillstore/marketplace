"""
Seedance 分镜 Skill 通用 API 脚本

供 Cursor Agent 在 MCP 不可用时通过 Shell 调用。
API Key 通过环境变量 XSKILL_API_KEY 读取。

用法:
  python seedance_api.py submit  --model MODEL_ID --params '{"prompt":"..."}' 
  python seedance_api.py query   --task-id TASK_ID
  python seedance_api.py poll    --task-id TASK_ID [--interval 5] [--timeout 600]
  python seedance_api.py balance
"""

import argparse
import json
import os
import sys
import time

import requests

BASE_URL = os.environ.get("XSKILL_BASE_URL", "https://api.xskill.ai")
API_KEY = os.environ.get("XSKILL_API_KEY", "")

CREATE_URL = f"{BASE_URL}/api/v3/tasks/create"
QUERY_URL = f"{BASE_URL}/api/v3/tasks/query"
BALANCE_URL = f"{BASE_URL}/api/v3/user/balance"
UPLOAD_URL = f"{BASE_URL}/api/v3/upload/image"


def _headers():
    if not API_KEY:
        print("错误: 环境变量 XSKILL_API_KEY 未设置", file=sys.stderr)
        print("  export XSKILL_API_KEY=sk-your-api-key", file=sys.stderr)
        print("  获取 API Key: https://www.xskill.ai/#/v2/api-keys", file=sys.stderr)
        sys.exit(1)
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }


# ------------------------------------------------------------------
# submit: 创建任务
# ------------------------------------------------------------------
def cmd_submit(args):
    params = json.loads(args.params)
    payload = {"model": args.model, "params": params}
    resp = requests.post(CREATE_URL, json=payload, headers=_headers(), timeout=30)
    result = resp.json()

    if result.get("code") != 200:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    task_id = result["data"]["task_id"]
    price = result["data"].get("price", "?")
    print(json.dumps({
        "task_id": task_id,
        "price": price,
        "status": "submitted",
        "raw": result,
    }, ensure_ascii=False, indent=2))


# ------------------------------------------------------------------
# query: 查询任务状态
# ------------------------------------------------------------------
def cmd_query(args):
    resp = requests.post(QUERY_URL, json={"task_id": args.task_id}, headers=_headers(), timeout=30)
    result = resp.json()
    data = result.get("data", {})
    status = data.get("status", "unknown")

    output_urls = []
    if status == "completed":
        output = data.get("result", {}).get("output", {})
        output_urls = output.get("images", []) or output.get("videos", []) or []

    print(json.dumps({
        "task_id": args.task_id,
        "status": status,
        "output_urls": output_urls,
        "error": data.get("error", ""),
        "raw": result,
    }, ensure_ascii=False, indent=2))


# ------------------------------------------------------------------
# poll: 轮询等待任务完成
# ------------------------------------------------------------------
def cmd_poll(args):
    interval = args.interval
    timeout = args.timeout
    elapsed = 0

    print(f"[轮询] task_id={args.task_id}  间隔={interval}s  超时={timeout}s", file=sys.stderr)

    while elapsed < timeout:
        resp = requests.post(QUERY_URL, json={"task_id": args.task_id}, headers=_headers(), timeout=30)
        result = resp.json()
        data = result.get("data", {})
        status = data.get("status", "unknown")
        print(f"[轮询] {elapsed}s - {status}", file=sys.stderr)

        if status == "completed":
            output = data.get("result", {}).get("output", {})
            output_urls = output.get("images", []) or output.get("videos", []) or []
            print(json.dumps({
                "task_id": args.task_id,
                "status": "completed",
                "output_urls": output_urls,
                "raw": result,
            }, ensure_ascii=False, indent=2))
            return

        if status == "failed":
            print(json.dumps({
                "task_id": args.task_id,
                "status": "failed",
                "error": data.get("error", "未知错误"),
                "raw": result,
            }, ensure_ascii=False, indent=2))
            sys.exit(1)

        time.sleep(interval)
        elapsed += interval

    print(json.dumps({
        "task_id": args.task_id,
        "status": "timeout",
        "error": f"等待 {timeout}s 后仍未完成",
    }, ensure_ascii=False, indent=2))
    sys.exit(1)


# ------------------------------------------------------------------
# balance: 查询余额
# ------------------------------------------------------------------
def cmd_balance(args):
    resp = requests.get(BALANCE_URL, headers=_headers(), timeout=30)
    result = resp.json()
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ------------------------------------------------------------------
# upload: 上传图片
# ------------------------------------------------------------------
def cmd_upload(args):
    payload = {}
    if args.image_url:
        payload["image_url"] = args.image_url
    elif args.image_path:
        import base64
        with open(args.image_path, "rb") as f:
            payload["image_data"] = base64.b64encode(f.read()).decode()
    else:
        print("错误: 需要 --image-url 或 --image-path", file=sys.stderr)
        sys.exit(1)

    resp = requests.post(UPLOAD_URL, json=payload, headers=_headers(), timeout=60)
    result = resp.json()
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ------------------------------------------------------------------
# CLI 入口
# ------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Seedance Storyboard API CLI")
    sub = parser.add_subparsers(dest="command")

    p_submit = sub.add_parser("submit", help="创建任务")
    p_submit.add_argument("--model", required=True, help="模型 ID")
    p_submit.add_argument("--params", required=True, help="参数 JSON 字符串")

    p_query = sub.add_parser("query", help="查询任务")
    p_query.add_argument("--task-id", required=True, help="任务 ID")

    p_poll = sub.add_parser("poll", help="轮询等待任务完成")
    p_poll.add_argument("--task-id", required=True, help="任务 ID")
    p_poll.add_argument("--interval", type=int, default=5, help="轮询间隔（秒）")
    p_poll.add_argument("--timeout", type=int, default=600, help="超时时间（秒）")

    sub.add_parser("balance", help="查询余额")

    p_upload = sub.add_parser("upload", help="上传图片")
    p_upload.add_argument("--image-url", help="网络图片 URL")
    p_upload.add_argument("--image-path", help="本地图片路径")

    args = parser.parse_args()

    commands = {
        "submit": cmd_submit,
        "query": cmd_query,
        "poll": cmd_poll,
        "balance": cmd_balance,
        "upload": cmd_upload,
    }

    if args.command not in commands:
        parser.print_help()
        sys.exit(1)

    commands[args.command](args)


if __name__ == "__main__":
    main()
