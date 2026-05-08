#!/usr/bin/env python3
"""
小羊云商供应链平台 API 调用脚本
自动获取 Token 并调用商品 API
"""

import json
import os
import sys

# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

import requests

# API 配置
API_URL = "https://openapi.legendshop.cn"
CLIENT_ID = "lflRYWthH1Kh9om9"
CLIENT_SECRET = "K3RU8keFDTGrizHWviePHj3jc4iHSvUE"

# 创建禁用代理的 session
session = requests.Session()
session.trust_env = False  # 不使用环境代理


def get_token():
    """获取访问令牌"""
    url = f"{API_URL}/portal/login/getToken"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "shop"
    }

    try:
        resp = session.post(url, data=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        token = result.get("access_token")
        if not token:
            raise Exception(f"获取Token失败: {result.get('message', 'unknown error')}")
        return token
    except requests.exceptions.RequestException as e:
        raise Exception(f"获取Token失败: {str(e)}")


def get_goods_list(token, page_num=1, page_size=12):
    """获取商品池列表（POST请求）"""
    url = f"{API_URL}/open/v2/product/queryProdPage"
    data = {
        "pageNum": page_num,
        "pageSize": page_size
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        resp = session.post(url, data=data, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"获取商品列表失败: {str(e)}")


def get_goods_detail(token, prod_id):
    """获取商品详情（POST请求）"""
    url = f"{API_URL}/open/v2/product/getDetail"
    data = {"prodId": prod_id}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        resp = session.post(url, data=data, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"获取商品详情失败: {str(e)}")


def get_account_balance(token):
    """查询开发者资金账号余额"""
    url = f"{API_URL}/open/v2/captital/getAccount"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        resp = session.post(url, data={}, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"查询资金余额失败: {str(e)}")


def main():
    if len(sys.argv) < 2:
        print("用法: api_client.py <command> [args]")
        print("命令: token - 获取访问令牌")
        print("      list [page] [size] - 获取商品列表")
        print("      detail <spuId> - 获取商品详情")
        print("      balance - 查询资金账号余额")
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "token":
            token = get_token()
            print(json.dumps({"access_token": token}, ensure_ascii=False, indent=2))

        elif command == "list":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            size = int(sys.argv[3]) if len(sys.argv) > 3 else 12
            token = get_token()
            result = get_goods_list(token, page, size)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "detail":
            if len(sys.argv) < 3:
                print("错误: 需要提供 spuId")
                sys.exit(1)
            token = get_token()
            result = get_goods_detail(token, sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif command == "balance":
            token = get_token()
            result = get_account_balance(token)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        else:
            print(f"未知命令: {command}")
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
