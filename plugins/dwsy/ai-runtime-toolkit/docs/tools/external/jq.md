---
name: jq
description: JSON数据的命令行处理器 - 查询、过滤和转换JSON
category: advanced
tool_id: EXT-JQ-001
---

# jq (JSON Processor) ⭐⭐⭐⭐⭐

## 用途
命令行JSON查询、过滤和转换工具

## 安装

### macOS
```bash
brew install jq
```

### Ubuntu/Debian
```bash
sudo apt-get install jq
```

## 基础使用

```bash
# 美化打印
cat data.json | jq '.'

# 提取字段
cat api.json | jq '.users[0].name'

# 数组长度
cat data.json | jq '.items | length'

# 过滤
cat logs.json | jq '.[] | select(.level == "ERROR")'

# 转换
cat data.json | jq '{new_name: .old_name, count: .items | length}'
```

## 在ai-runtime中的使用

```bash
# 分析JSON格式的认知记录
jq '.entries[] | select(.type == "ERROR")' .ai-runtime/memory/episodic/timeline.json

# 发现工具统计显示
python3 discover-toolkit.py list --json | jq '.[] | {tool: .tool_name, lang: .language}'

# 提取依赖分析结果
python3 dependency-analyzer.py . -o report.json | jq '.vulnerabilities'
```

## 常用操作

### 数组操作
```bash
# 映射
cat data.json | jq 'map(.value * 2)'

# 过滤
cat data.json | jq 'map(select(.active == true))'

# 排序
cat data.json | jq 'sort_by(.date)'
```

### 对象操作
```bash
# 添加字段
cat data.json | jq '. + {new_field: "value"}'

# 删除字段
cat data.json | jq 'del(.old_field)'

# 合并对象
cat data1.json data2.json | jq -s 'add'
```

### 高级技巧

```bash
# 条件判断
cat config.json | jq '.env.WIN_VERBOSE = if .debug then "true" else "false" end'

# 管道操作
cat data.json | jq '.items[] | select(.price > 100) | .name'

# 变量赋值
cat data.json | jq 'first(.items[] | select(.id == "123")) as $item | $item.price'
```
