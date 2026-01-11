# 记忆系统使用示例

## 快速开始

### 环境准备
```bash
# 进入项目目录
cd /path/to/ai-runtime

# 进入记忆系统目录
cd .ai-runtime/memory
```

### 第一个查询
```bash
# 查看所有记忆事件
python3 memory_cli.py query

# 查看今天的事件
python3 memory_cli.py query --where "date='$(date +%Y-%m-%d)'"
```

## 情景记忆查询示例

### 时间范围查询
```bash
# 查看本周事件
python3 memory_cli.py query \
    --where "date>='$(date -d 'last monday' +%Y-%m-%d)'" \
    --order-by "timestamp desc"

# 查看最近24小时的事件
python3 memory_cli.py query \
    --where "timestamp >= '$(date -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)'" \
    --order-by "timestamp desc"
```

### 类型过滤
```bash
# 查看所有决策
python3 memory_cli.py query \
    --where "type='decision'" \
    --order-by "timestamp desc"

# 查看错误事件
python3 memory_cli.py query \
    --where "type='error'" \
    --select "timestamp,title,tags" \
    --limit 10
```

### 标签查询
```bash
# 查找架构相关事件
python3 memory_cli.py query \
    --where "tags CONTAINS 'architecture'"

# 查找安全相关决策
python3 memory_cli.py query \
    --where "type='decision' AND tags CONTAINS 'security'"
```

### 复杂组合查询
```bash
# 查找本月的重要架构决策
python3 memory_cli.py query \
    --where "date>='$(date +%Y-%m-01)' AND type='decision' AND tags CONTAINS 'architecture'" \
    --order-by "timestamp desc" \
    --limit 20
```

## 数据导出和分析

### JSON格式导出
```bash
# 导出本周事件为JSON
python3 memory_cli.py query \
    --where "date>='$(date -d '7 days ago' +%Y-%m-%d)'" \
    --format json \
    --order-by "timestamp desc" > weekly-events.json
```

### 统计分析
```bash
# 统计各类型事件数量
python3 memory_cli.py query \
    --select "type" \
    --format json | jq -r '.[].type' | sort | uniq -c | sort -nr

# 统计热门标签
python3 memory_cli.py query \
    --select "tags" \
    --format json | jq -r '.[].tags[]' | sort | uniq -c | sort -nr | head -10
```

### 时间线分析
```bash
# 生成每日事件数量统计
python3 memory_cli.py query \
    --select "date" \
    --format json | jq -r '.[].date' | sort | uniq -c | sort
```

## 编程接口使用

### Python集成示例
```python
#!/usr/bin/env python3
"""记忆系统集成示例"""

import sys
from pathlib import Path
from memory_discovery import MemoryDiscovery

class MemoryAnalytics:
    """记忆分析工具"""

    def __init__(self, memory_root: str):
        self.discovery = MemoryDiscovery(memory_root)

    def get_recent_events(self, days: int = 7):
        """获取最近N天的所有事件"""
        import datetime
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)

        return self.discovery.query(
            where=f"timestamp >= '{cutoff.isoformat()}'",
            order_by="timestamp desc"
        )

    def get_events_by_type(self, event_type: str, limit: int = 50):
        """按类型获取事件"""
        return self.discovery.query(
            where=f"type='{event_type}'",
            order_by="timestamp desc",
            limit=limit
        )

    def search_by_tags(self, tags: list, match_all: bool = True):
        """按标签搜索"""
        if not tags:
            return []

        conditions = []
        for tag in tags:
            conditions.append(f"tags CONTAINS '{tag}'")

        operator = " AND " if match_all else " OR "
        where_clause = operator.join(conditions)

        return self.discovery.query(where=where_clause)

    def get_event_summary(self, days: int = 30):
        """生成事件摘要统计"""
        events = self.get_recent_events(days)

        summary = {
            'total': len(events),
            'by_type': {},
            'by_tag': {},
            'timeline': {}
        }

        for event in events:
            # 按类型统计
            summary['by_type'][event.type] = summary['by_type'].get(event.type, 0) + 1

            # 按标签统计
            for tag in event.tags:
                summary['by_tag'][tag] = summary['by_tag'].get(tag, 0) + 1

            # 按日期统计
            date_str = event.date
            summary['timeline'][date_str] = summary['timeline'].get(date_str, 0) + 1

        return summary

def main():
    analytics = MemoryAnalytics('.ai-runtime/memory')

    # 获取最近7天的事件摘要
    summary = analytics.get_event_summary(7)
    print(f"最近7天共记录 {summary['total']} 个事件")

    # 显示类型分布
    print("\n事件类型分布:")
    for event_type, count in summary['by_type'].items():
        print(f"  {event_type}: {count}")

    # 显示热门标签
    print("\n热门标签:")
    sorted_tags = sorted(summary['by_tag'].items(), key=lambda x: x[1], reverse=True)
    for tag, count in sorted_tags[:10]:
        print(f"  {tag}: {count}")

if __name__ == "__main__":
    main()
```

### Web界面集成
```python
#!/usr/bin/env python3
"""简单的记忆查询Web服务"""

from flask import Flask, request, jsonify
from memory_discovery import MemoryDiscovery

app = Flask(__name__)
discovery = MemoryDiscovery('.ai-runtime/memory')

@app.route('/api/events', methods=['GET'])
def get_events():
    """查询事件API"""
    where = request.args.get('where', '')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    format_type = request.args.get('format', 'json')

    events = discovery.query(where=where, limit=limit, offset=offset)
    return discovery.format_events(events, format_type=format_type)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    days = int(request.args.get('days', 30))

    import datetime
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    events = discovery.query(where=f"timestamp >= '{cutoff.isoformat()}'")

    stats = {
        'total': len(events),
        'by_type': {},
        'by_tag': {},
        'date_range': {
            'start': cutoff.date().isoformat(),
            'end': datetime.date.today().isoformat()
        }
    }

    for event in events:
        stats['by_type'][event.type] = stats['by_type'].get(event.type, 0) + 1
        for tag in event.tags:
            stats['by_tag'][tag] = stats['by_tag'].get(tag, 0) + 1

    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
```

## 自动化脚本

### 每日摘要生成
```bash
#!/bin/bash
# 生成每日记忆摘要

DATE=$(date +%Y-%m-%d)
OUTPUT_DIR=".ai-runtime/reports"
mkdir -p $OUTPUT_DIR

echo "# ${DATE} 记忆摘要" > $OUTPUT_DIR/daily-summary-${DATE}.md
echo "" >> $OUTPUT_DIR/daily-summary-${DATE}.md

echo "## 今日事件统计" >> $OUTPUT_DIR/daily-summary-${DATE}.md
python3 memory_cli.py query --where "date='${DATE}'" --format json | jq '. | length' >> $OUTPUT_DIR/daily-summary-${DATE}.md

echo "" >> $OUTPUT_DIR/daily-summary-${DATE}.md
echo "## 今日事件列表" >> $OUTPUT_DIR/daily-summary-${DATE}.md
python3 memory_cli.py query --where "date='${DATE}'" --select "timestamp,title,type" >> $OUTPUT_DIR/daily-summary-${DATE}.md

echo "" >> $OUTPUT_DIR/daily-summary-${DATE}.md
echo "## 热门标签" >> $OUTPUT_DIR/daily-summary-${DATE}.md
python3 memory_cli.py query --where "date='${DATE}'" --select "tags" --format json | jq -r '.[].tags[]' | sort | uniq -c | sort -nr | head -5 >> $OUTPUT_DIR/daily-summary-${DATE}.md
```

### 定期维护脚本
```bash
#!/bin/bash
# 记忆系统定期维护

MEMORY_ROOT=".ai-runtime/memory"

# 清理过期短期记忆（30天）
find ${MEMORY_ROOT}/short-term/ -mtime +30 -delete

# 检查episodic文件一致性
python3 -c "
from memory_discovery import MemoryDiscovery
d = MemoryDiscovery('${MEMORY_ROOT}')
invalid = [e for e in d.events if not e.timestamp or not e.title]
if invalid:
    print('发现无效事件:')
    for e in invalid:
        print(f'  {e.path}: 缺少必要字段')
else:
    print('所有事件文件有效')
"

# 生成维护报告
REPORT_FILE=".ai-runtime/reports/maintenance-$(date +%Y%m%d).md"
echo "# 记忆系统维护报告 - $(date)" > $REPORT_FILE
echo "" >> $REPORT_FILE
echo "## 统计信息" >> $REPORT_FILE
echo "- Episodic事件数量: $(find ${MEMORY_ROOT}/episodic/ -name '*.md' | wc -l)" >> $REPORT_FILE
echo "- Long-term文档数量: $(find ${MEMORY_ROOT}/long-term/ -name '*.md' | wc -l)" >> $REPORT_FILE
echo "- Short-term文件数量: $(find ${MEMORY_ROOT}/short-term/ -name '*.md' | wc -l)" >> $REPORT_FILE
```

## 高级查询技巧

### 正则表达式搜索
```python
# 使用Python进行高级搜索
import re
from memory_discovery import MemoryDiscovery

discovery = MemoryDiscovery('.ai-runtime/memory')

# 搜索包含特定关键词的事件
keyword_events = []
for event in discovery.events:
    if re.search(r'OAuth|认证', event.title, re.IGNORECASE):
        keyword_events.append(event)

print(f"找到 {len(keyword_events)} 个相关事件")
```

### 时间序列分析
```python
# 分析事件的时间分布
from collections import defaultdict
from memory_discovery import MemoryDiscovery

discovery = MemoryDiscovery('.ai-runtime/memory')
events = discovery.query(order_by="timestamp asc")

# 按小时统计
hourly_stats = defaultdict(int)
for event in events:
    hour = event.timestamp.hour
    hourly_stats[hour] += 1

print("事件按小时分布:")
for hour in sorted(hourly_stats.keys()):
    print(f"  {hour:02d}:00: {hourly_stats[hour]} 个事件")
```

### 相关性分析
```python
# 分析标签共现关系
from collections import defaultdict
from memory_discovery import MemoryDiscovery

discovery = MemoryDiscovery('.ai-runtime/memory')

# 构建标签共现矩阵
cooccurrence = defaultdict(lambda: defaultdict(int))
for event in discovery.events:
    tags = event.tags
    for i, tag1 in enumerate(tags):
        for tag2 in tags[i+1:]:
            cooccurrence[tag1][tag2] += 1
            cooccurrence[tag2][tag1] += 1

# 显示最相关的标签对
print("标签共现分析:")
for tag1 in sorted(cooccurrence.keys()):
    for tag2, count in sorted(cooccurrence[tag1].items(), key=lambda x: x[1], reverse=True):
        if count > 1:  # 至少出现2次
            print(f"  {tag1} + {tag2}: {count} 次")
```
