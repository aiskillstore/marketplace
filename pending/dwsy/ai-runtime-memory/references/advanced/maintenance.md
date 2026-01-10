# 记忆系统维护指南

## 日常维护任务

### 定期清理
```bash
# 清理7天前的短期记忆
find .ai-runtime/memory/short-term/ -mtime +7 -delete

# 检查episodic目录结构
find .ai-runtime/memory/episodic/ -type f -name "*.md" | head -20
```

### 索引更新
```bash
# 手动刷新记忆索引
python3 -c "from memory_discovery import MemoryDiscovery; d=MemoryDiscovery('.ai-runtime/memory'); d.refresh()"
```

### 一致性检查
- 验证所有episodic文件都有有效的YAML front matter
- 检查时间戳格式统一性
- 确认标签命名规范

## 事件添加流程

### 1. 创建事件文件
```bash
# 创建目录结构（如果不存在）
mkdir -p .ai-runtime/memory/episodic/$(date +%Y/%m/%d)

# 创建事件文件
vim .ai-runtime/memory/episodic/$(date +%Y/%m/%d)/event-description.md
```

### 2. YAML Front Matter 模板
```yaml
---
id: unique-event-id
type: event|decision|error|meeting|milestone
level: day
timestamp: "2025-11-14T10:30:00"
tags: [tag1, tag2, tag3]
related: [related-event-id-1, related-event-id-2]
---

# 事件标题

## 时间
2025-11-14 10:30:00

## 标签
tag1, tag2, tag3

## 内容
详细的事件描述，包括：
- 背景信息
- 决策过程
- 结果和影响
- 后续行动项

## 相关事件
- [related-event-id-1](link-to-related)
- [related-event-id-2](link-to-related)
```

### 3. 事件类型规范

| 类型 | 描述 | 示例 |
|------|------|------|
| `event` | 一般事件 | 代码审查、部署上线 |
| `decision` | 关键决策 | 架构选择、技术栈变更 |
| `error` | 错误和问题 | 生产故障、构建失败 |
| `meeting` | 会议纪要 | 团队会议、客户会议 |
| `milestone` | 里程碑 | 项目启动、版本发布 |

### 4. 标签规范

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

## 记忆固化策略

### 短期记忆 → 长期记忆

**触发条件**:
- 识别出可复用的技术模式
- 积累了足够的使用经验
- 形成了最佳实践

**固化流程**:
1. 从短期记忆提取关键信息
2. 整理为结构化文档
3. 移动到 `long-term/` 目录
4. 更新相关引用
5. 添加到知识图谱

**示例**:
```bash
# 提取OAuth2.0集成经验
cp .ai-runtime/memory/short-term/oauth-integration-notes.md .ai-runtime/memory/long-term/oauth-integration-patterns.md

# 更新引用
echo "- oauth-integration-patterns.md" >> .ai-runtime/memory/long-term/index.md
```

### 工作记忆 → 情景记忆

**触发条件**:
- 任务完成
- 关键决策做出
- 错误发生并解决
- 里程碑达成

**固化流程**:
1. 自动生成事件ID
2. 创建时间戳
3. 提取上下文信息
4. 添加到episodic时间线
5. 更新相关链接

**自动固化**:
```bash
# 使用/runtime.remember命令
/runtime.remember "完成了用户认证模块重构，采用JWT替代session"
```

## 质量保证

### 一致性检查脚本
```python
#!/usr/bin/env python3
"""记忆系统质量检查工具"""

import sys
from pathlib import Path
from memory_discovery import MemoryDiscovery

def check_memory_quality(memory_root: Path):
    """检查记忆系统质量"""
    discovery = MemoryDiscovery(str(memory_root))

    issues = []

    # 检查episodic文件
    for event in discovery.events:
        # 检查必需字段
        if not event.id:
            issues.append(f"事件缺少ID: {event.path}")
        if not event.timestamp:
            issues.append(f"事件缺少时间戳: {event.path}")
        if not event.title:
            issues.append(f"事件缺少标题: {event.path}")

        # 检查时间合理性
        if event.timestamp and event.timestamp > datetime.now():
            issues.append(f"事件时间戳为未来: {event.path}")

    return issues

if __name__ == "__main__":
    memory_root = Path(".ai-runtime/memory")
    issues = check_memory_quality(memory_root)

    if issues:
        print("发现以下质量问题:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("记忆系统质量检查通过")
```

### 数据备份策略

**自动备份**:
- 每日备份episodic目录
- 每周备份long-term目录
- 每月备份完整记忆系统

**备份脚本**:
```bash
#!/bin/bash
# 记忆系统备份脚本

BACKUP_DIR=".ai-runtime/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份episodic记忆
tar -czf $BACKUP_DIR/episodic_$TIMESTAMP.tar.gz .ai-runtime/memory/episodic/

# 备份long-term记忆
tar -czf $BACKUP_DIR/long-term_$TIMESTAMP.tar.gz .ai-runtime/memory/long-term/

echo "备份完成: $TIMESTAMP"
```

## 性能优化

### 索引优化
- 定期重建事件索引
- 优化时间范围查询
- 维护标签倒排索引

### 存储优化
- 压缩历史episodic文件
- 清理重复内容
- 归档过期短期记忆

### 查询优化
- 使用分页查询大量数据
- 优先使用索引字段过滤
- 缓存常用查询结果
