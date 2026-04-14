#!/bin/bash

# 基础分类文章接口 URL
BASE_URL="https://skills.myzaker.com/api/v1/article/category?v=1.0.6"

# 测试获取科技类文章 (app_id=13)
APP_ID=13

echo "======================================"
echo "获取指定分类(app_id=${APP_ID})最新文章"
echo "======================================"

# 发送 GET 请求并使用 jq 格式化 JSON 输出
# 如果没有安装 jq，请移除 | jq '.'
curl -s -X GET "${BASE_URL}?app_id=${APP_ID}" | jq '.'
