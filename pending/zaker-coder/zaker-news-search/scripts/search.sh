#!/bin/bash

# 基础搜索接口 URL
BASE_URL="https://skills.myzaker.com/api/v1/article/search?v=1.0.6"

# 1. 简单的关键词搜索
echo "======================================"
echo "1. 测试简单关键词搜索: 人工智能"
echo "======================================"
curl -s -X GET "${BASE_URL}?keyword=人工智能" | jq '.'

echo -e "\n\n"

# 2. 带起始时间的关键词搜索
# 注意 URL 编码，空格需要编码为 %20
echo "======================================"
echo "2. 测试带时间范围的搜索: iPhone 15"
echo "======================================"
curl -s -X GET "${BASE_URL}?keyword=iPhone%2015&start_time=2024-01-01%2000:00:00" | jq '.'
