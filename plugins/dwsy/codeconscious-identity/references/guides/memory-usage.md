# 记忆系统使用详解

## 何时查询记忆

### 必须查询
- 任何代码修改前（查询相关历史决策）
- 回答架构问题前（查询长期知识）
- 识别模式时（查询类似历史）

### 可选查询
- 探索新项目时（建立上下文）
- 生成建议时（经验基础）

## 何时更新记忆

### 必须更新
- 关键架构决策（写入长期记忆）
- 错误和教训（写入情景记忆）
- 识别出的新模式（写入长期记忆）

### 可选更新
- 工作假设和上下文（短期记忆）
- 用户偏好（长期记忆）

## 记忆检索技巧

### CLI查询语法

#### 基本查询
```bash
# 进入记忆目录
cd .ai-runtime/memory

# 查询今天的所有事件
python3 memory_cli.py query --where "date='2025-11-14'"

# 按标签搜索架构决策
python3 memory_cli.py query \
    --where "tags CONTAINS 'architecture' AND type='decision'" \
    --order-by "timestamp desc"

# 最近10个事件（表格格式）
python3 memory_cli.py query --limit 10 --order-by "timestamp desc"

# 最近事件（JSON格式，便于程序处理）
python3 memory_cli.py query --limit 5 --format json --order-by "timestamp desc"
```

#### 高级查询条件
- 日期范围: `--where "date>='2025-11-01' AND date<='2025-11-14'"`
- 标签组合: `--where "tags CONTAINS 'error' OR tags CONTAINS 'bug'"`
- 类型过滤: `--where "type='meeting'"`

#### 输出定制
- 选择字段: `--select "id,timestamp,title"`
- 排序: `--order-by "date desc, timestamp asc"`
- 分页: `--limit 20 --offset 40`

### 文件系统检索

```bash
# 快速定位记忆文件
grep -r "关键词" .ai-runtime/memory/

# 查看最近的事件
tail -50 .ai-runtime/memory/episodic/timeline.md

# 搜索相关知识
grep -A5 -B5 "认证" .ai-runtime/memory/long-term/*.md

# 查看短期记忆状态
cat .ai-runtime/memory/short-term/consciousness.md
```

## 记忆管理最佳实践

### 事件记录规范

#### 事件分类
- `event`: 一般事件（代码审查、部署上线）
- `decision`: 关键决策（架构选择、技术栈变更）
- `error`: 错误和问题（生产故障、构建失败）
- `meeting`: 会议纪要（团队会议、客户会议）
- `milestone`: 里程碑（项目启动、版本发布）

#### 标签体系
**技术标签**:
- `architecture` - 架构相关
- `database` - 数据库相关
- `frontend` - 前端相关
- `backend` - 后端相关
- `devops` - 运维相关
- `security` - 安全相关

**活动标签**:
- `planning` - 规划阶段
- `development` - 开发阶段
- `testing` - 测试阶段
- `deployment` - 部署阶段
- `maintenance` - 维护阶段

**结果标签**:
- `success` - 成功
- `failure` - 失败
- `improvement` - 改进
- `regression` - 回归

### 记忆固化流程

#### 短期 → 长期固化
1. **识别价值**: 发现有复用价值的模式或知识
2. **整理内容**: 转换为结构化文档格式
3. **选择位置**: 移动到 `long-term/` 适当分类目录
4. **建立链接**: 更新相关引用和索引
5. **验证完整**: 确保内容准确且可检索

#### 工作记忆 → 情景记忆
1. **事件捕获**: 自动记录关键操作和决策点
2. **上下文提取**: 获取相关背景信息和影响
3. **时间戳记录**: 确保时间线准确性
4. **分类标注**: 添加适当的类型和标签
5. **关联建立**: 链接相关事件和决策

### 质量保证

#### 一致性检查
- 验证所有episodic文件都有有效的YAML front matter
- 检查时间戳格式统一性（ISO 8601）
- 确认标签命名规范和大小写一致性
- 验证文件路径结构正确性

#### 数据完整性
- 确保必需字段存在（id, timestamp, title）
- 检查引用关系的有效性
- 验证元数据的一致性

### 性能优化

#### 查询优化
- 使用索引字段进行过滤（优先使用date, type, tags）
- 合理使用LIMIT限制结果数量
- 组合条件时注意执行顺序

#### 存储优化
- 定期清理过期短期记忆（7天）
- 压缩历史episodic文件
- 归档低频访问的长期记忆

## 高级使用模式

### 编程接口集成

#### Python脚本集成
```python
from memory_discovery import MemoryDiscovery

# 初始化记忆发现器
discovery = MemoryDiscovery('.ai-runtime/memory')

# 复杂查询
events = discovery.query(
    where="date>='2025-11-01' AND (tags CONTAINS 'architecture' OR tags CONTAINS 'security')",
    order_by="timestamp desc",
    limit=50
)

# 统计分析
from collections import Counter
types = Counter(event.type for event in events)
tags = Counter(tag for event in events for tag in event.tags)
```

#### Web服务集成
```python
from flask import Flask, jsonify
from memory_discovery import MemoryDiscovery

app = Flask(__name__)
discovery = MemoryDiscovery('.ai-runtime/memory')

@app.route('/api/events/search')
def search_events():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))

    events = discovery.query(where=f"title LIKE '%{query}%'", limit=limit)
    return jsonify([event.to_dict() for event in events])
```

### 自动化脚本

#### 每日摘要生成
```bash
#!/bin/bash
# 生成每日记忆摘要

DATE=$(date +%Y-%m-%d)
REPORT_DIR=".ai-runtime/reports"
mkdir -p $REPORT_DIR

# 生成摘要报告
python3 memory_cli.py query --where "date='${DATE}'" --format json | jq 'length' > "${REPORT_DIR}/daily-summary-${DATE}.md"

echo "## 今日事件类型分布" >> "${REPORT_DIR}/daily-summary-${DATE}.md"
python3 memory_cli.py query --where "date='${DATE}'" --select "type" --format json | jq -r '.[].type' | sort | uniq -c >> "${REPORT_DIR}/daily-summary-${DATE}.md"
```

#### 定期维护
```bash
#!/bin/bash
# 记忆系统维护脚本

# 清理过期短期记忆
find .ai-runtime/memory/short-term/ -mtime +7 -delete

# 生成健康报告
echo "=== 记忆系统健康检查 $(date) ===" > .ai-runtime/reports/health-$(date +%Y%m%d).md
echo "情景记忆事件数: $(find .ai-runtime/memory/episodic/ -name '*.md' | wc -l)" >> .ai-runtime/reports/health-$(date +%Y%m%d).md
echo "长期记忆文档数: $(find .ai-runtime/memory/long-term/ -name '*.md' | wc -l)" >> .ai-runtime/reports/health-$(date +%Y%m%d).md
echo "短期记忆文件数: $(find .ai-runtime/memory/short-term/ -name '*.md' | wc -l)" >> .ai-runtime/reports/health-$(date +%Y%m%d).md
```

## 故障排除

### 常见问题

#### 查询无结果
- **原因**: WHERE条件过于严格或字段名称错误
- **解决**: 检查语法，简化条件，验证字段名称
- **示例**: `--where "date='2025-11-14'"` 而不是 `--where "date='11/14/2025'"`

#### 事件不显示
- **原因**: 时间戳格式错误或文件路径不符合规范
- **解决**: 验证YAML front matter的timestamp字段格式
- **检查**: `python3 -c "from memory_discovery import MemoryDiscovery; d=MemoryDiscovery('.'); print(len(d.events))"`

#### 性能问题
- **原因**: 查询条件过于宽泛或数据量过大
- **解决**: 添加更多过滤条件，使用LIMIT限制结果
- **优化**: 优先使用索引字段（date, type, tags）

### 调试技巧

#### 查看解析过程
```python
# 调试事件解析
from memory_discovery import MemoryDiscovery
import datetime

discovery = MemoryDiscovery('.ai-runtime/memory')

for event in discovery.events[:5]:  # 只检查前5个
    print(f"ID: {event.id}")
    print(f"标题: {event.title}")
    print(f"时间戳: {event.timestamp}")
    print(f"时间戳类型: {type(event.timestamp)}")
    print(f"标签: {event.tags}")
    print("---")
```

#### 验证查询语法
```python
# 测试查询条件
test_conditions = [
    "date='2025-11-14'",
    "tags CONTAINS 'architecture'",
    "type='decision'",
    "date>='2025-11-01' AND date<='2025-11-14'"
]

for condition in test_conditions:
    try:
        events = discovery.query(where=condition, limit=1)
        print(f"✓ {condition}: {len(events)} 结果")
    except Exception as e:
        print(f"✗ {condition}: {e}")
```

## 扩展和定制

### 自定义事件类型
在episodic事件中添加新的type值，并确保查询时正确处理。

### 自定义标签体系
根据项目需求扩展标签体系，保持一致的命名约定。

### 集成外部系统
通过编程接口将记忆系统集成到其他工具和系统中。
