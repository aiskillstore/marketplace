# 记忆系统工具详解

## memory_cli.py - 命令行查询工具

### 核心功能
提供SQL风格的命令行接口，支持复杂条件查询情景记忆事件。

### 命令语法
```bash
python3 memory_cli.py query [选项...]
```

### 查询选项详解

#### --select 字段选择
```bash
# 选择特定字段
--select "id,timestamp,title"

# 默认选择（不指定时）
--select "id,timestamp,title"
```

#### --where 条件过滤
支持SQL风格WHERE条件，字段包括：
- `id`, `type`, `level`, `title`, `date`, `timestamp`
- `tags` (支持 CONTAINS 操作)

```bash
# 基础条件
--where "type='decision'"
--where "date>='2025-11-14'"
--where "tags CONTAINS 'architecture'"

# 组合条件
--where "date>='2025-11-14' AND tags CONTAINS 'decision'"
--where "type='meeting' OR type='decision'"
```

#### --order-by 排序
```bash
# 单个字段排序
--order-by "timestamp desc"
--order-by "date asc"

# 多个字段排序（暂不支持）
```

#### --limit / --offset 分页
```bash
--limit 20 --offset 0    # 第一页，20条
--limit 20 --offset 20   # 第二页，20条
```

#### --format 输出格式
```bash
--format table   # 表格格式（默认）
--format json    # JSON格式
```

### 使用示例

#### 基础查询
```bash
# 查看所有事件
python3 memory_cli.py query

# 查看今天的事件
python3 memory_cli.py query --where "date='2025-11-14'"
```

#### 高级查询
```bash
# 查找架构决策
python3 memory_cli.py query \
    --where "type='decision' AND tags CONTAINS 'architecture'" \
    --order-by "timestamp desc" \
    --limit 10

# 搜索错误事件
python3 memory_cli.py query \
    --where "type='error'" \
    --select "timestamp,title,tags" \
    --format table
```

#### 时间范围查询
```bash
# 本周事件
python3 memory_cli.py query \
    --where "date>='2025-11-10' AND date<='2025-11-16'"

# 最近7天
python3 memory_cli.py query \
    --where "timestamp >= '2025-11-07T00:00:00'" \
    --order-by "timestamp desc"
```

## memory_discovery.py - 编程接口

### 类概述

#### MemoryDiscovery 类
核心记忆发现和查询引擎。

#### MemoryEvent 类
单个记忆事件的索引信息数据类。

### 编程接口

#### 初始化
```python
from memory_discovery import MemoryDiscovery

# 初始化发现器
discovery = MemoryDiscovery("path/to/memory/root")
```

#### 刷新索引
```python
# 重新扫描episodic目录
discovery.refresh()
```

#### SQL风格查询
```python
# 基础查询
events = discovery.query()

# 条件查询
events = discovery.query(
    where="date>='2025-11-14' AND tags CONTAINS 'architecture'",
    order_by="timestamp desc",
    limit=20,
    offset=0
)
```

#### 格式化输出
```python
# 表格格式
output = discovery.format_events(events, format_type="table")

# JSON格式
output = discovery.format_events(events, format_type="json")

# 自定义字段选择
output = discovery.format_events(
    events,
    select=["id", "title", "date"],
    format_type="table"
)
```

### 事件解析协议

#### 时间推断顺序
1. YAML front matter `timestamp`/`time` 字段
2. 正文 `## 时间` 段落第一行
3. 文件名模式 `YYYYMMDD-HHMM.md`
4. 文件名模式 `YYYYMMDD.md`
5. 文件修改时间 (mtime)

#### 标签解析顺序
1. YAML front matter `tags` 数组
2. 正文 `## 标签` 段落（逗号分隔）
3. 空数组（无标签）

#### 标题解析顺序
1. YAML front matter `title`
2. 正文第一个 `# ` 标题
3. 文件名（去除扩展名）

### 高级用法

#### 自定义查询条件
```python
# 复杂的标签组合查询
events = discovery.query(
    where="tags CONTAINS 'architecture' AND (tags CONTAINS 'decision' OR tags CONTAINS 'design')"
)
```

#### 批量处理
```python
# 分页处理大量事件
page_size = 50
all_events = []

for offset in range(0, 1000, page_size):  # 最多1000条
    batch = discovery.query(limit=page_size, offset=offset)
    if not batch:
        break
    all_events.extend(batch)
```

#### 事件对象操作
```python
# 访问事件属性
for event in events:
    print(f"ID: {event.id}")
    print(f"标题: {event.title}")
    print(f"时间: {event.timestamp}")
    print(f"标签: {event.tags}")
    print(f"类型: {event.type}")

    # 转换为字典
    event_dict = event.to_dict()
```

## 工具集成

### Shell脚本集成
```bash
# 创建查询别名
alias memory-query="python3 .ai-runtime/memory/memory_cli.py query"

# 快速查看今天事件
memory-query --where "date='$(date +%Y-%m-%d)'"
```

### Python脚本集成
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '.ai-runtime/memory')

from memory_discovery import MemoryDiscovery

def get_recent_decisions(days=7):
    import datetime
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)

    discovery = MemoryDiscovery('.ai-runtime/memory')
    return discovery.query(
        where=f"type='decision' AND timestamp >= '{cutoff.isoformat()}'",
        order_by="timestamp desc"
    )
```

## 故障排除

### 常见问题

**查询无结果**
- 检查WHERE条件语法
- 验证字段名称拼写
- 确认时间格式（YYYY-MM-DD）

**事件不显示**
- 检查文件路径结构（episodic/YYYY/MM/DD/）
- 验证YAML front matter格式
- 确认时间戳有效性

**性能问题**
- 使用LIMIT限制结果数量
- 优化WHERE条件（先过滤时间范围）
- 考虑分页查询大量数据

### 调试技巧
```python
# 查看所有已解析事件
discovery = MemoryDiscovery('.ai-runtime/memory')
for event in discovery.events:
    print(f"{event.id}: {event.title} ({event.date}) - {event.tags}")
```
