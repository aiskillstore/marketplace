#!/bin/bash

# 获取热榜文章接口
API_URL="https://skills.myzaker.com/api/v1/article/hot?v=1.0.3"

echo "======================================"
echo "获取 ZAKER 平台最新热榜文章"
echo "======================================"

# 发送 GET 请求并使用 jq 格式化 JSON 输出
# 如果没有安装 jq，请移除 | jq '.'
curl -s -X GET "${API_URL}" | jq '.'
