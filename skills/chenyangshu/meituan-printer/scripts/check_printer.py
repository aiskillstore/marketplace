#!/usr/bin/env python3
"""
美团热敏打印机 - 连通性检测工具（非交互式）
供 AI 在对话式配置流程中后台调用，验证打印机是否可达。

用法：
    python3 check_printer.py --ip 192.168.3.172 --port 9100

返回 JSON：
    {"reachable": true, "ip": "192.168.3.172", "port": 9100, "error": null}
"""

import argparse
import json
import socket
import sys


def check_socket(ip, port, timeout=3):
    """测试打印机是否可达"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
        return True, None
    except socket.timeout:
        return False, "连接超时"
    except ConnectionRefusedError:
        return True, None  # 连接被拒说明 IP/端口可达，服务可能未完全就绪
    except OSError as e:
        return False, f"网络错误: {e}"
    except Exception as e:
        return False, f"未知错误: {e}"


def main():
    parser = argparse.ArgumentParser(description="美团热敏打印机连通性检测")
    parser.add_argument("--ip", required=True, help="打印机 IP 地址")
    parser.add_argument("--port", type=int, default=9100, help="端口号（默认 9100）")
    parser.add_argument("--timeout", type=int, default=3, help="超时秒数（默认 3）")
    args = parser.parse_args()

    reachable, error = check_socket(args.ip, args.port, args.timeout)

    result = {
        "reachable": reachable,
        "ip": args.ip,
        "port": args.port,
        "error": error
    }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
