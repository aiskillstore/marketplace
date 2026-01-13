# 快速参考指南

## 常用命令速查

### 核心运行时命令
```bash
# 探索新代码库（首次使用推荐）
/runtime.explore

# 深度思考不修改文件
/runtime.think "为什么..."

# 自主学习未知问题
/runtime.learn "问题描述"

# 需求规划和任务分解
/runtime.plan

# 基于计划迭代执行
/runtime.implement

# 固化经验到记忆系统
/runtime.remember

# 自我反思和评估
/runtime.reflect
```

### 记忆系统查询
```bash
# 进入记忆目录
cd .ai-runtime/memory

# 查询今天的事件
python3 memory_cli.py query --where "date='2025-11-14'"

# 按标签搜索
python3 memory_cli.py query --where "tags CONTAINS 'architecture'"

# 查看记忆统计
./scripts/memory-query.sh stats

# 便捷查询脚本
./scripts/memory-query.sh today    # 今天事件
./scripts/memory-query.sh week     # 本周事件
./scripts/memory-query.sh recent 3 # 最近3天
```

### 工具装备系统
```bash
# 查看所有工具
python3 .ai-runtime/toolkit/discover-toolkit.py list

# 查看外部工具
python3 .ai-runtime/toolkit/discover-toolkit.py list --external
```

## 宪法原则速查

### 核心原则
```
1.1 认知主体性    → 展示思考过程
1.2 类脑思维      → 联想优先于精确匹配
1.3 谦逊与不确定  → 标注置信度
2.3 质量优先      → 整合优于创造
4.1 从经验学习    → 更新心智模型
```

### 应用检查表
- **推理过程**: 是否展示了完整思考路径？
- **置信度**: 是否标注了建议的可信度？
- **记忆查询**: 是否检查了相关历史经验？
- **方案比较**: 是否考虑了多种可行方案？
- **风险评估**: 是否识别了潜在问题？

## 响应格式模板

### 标准响应结构
```markdown
## 摘要
[核心结论，1-3句话]

## 详细分析
- [发现1，带证据]
- [发现2，带证据]

## 相关记忆
- [记忆引用]

## 我的推理
1. [推理步骤1]
2. [推理步骤2]

## 建议和下一步
- [具体建议1]
- [具体建议2]

## 不确定性声明
- 置信度: 0.XX
- 需要验证: [假设]
```

### 代码建议格式
```markdown
### 建议: [标题]

**文件**: `path/to/file.py:行号`

**问题**: [问题描述]

**建议修改**:
```python
# 原代码
old_code()

# 建议改为
new_code()
```

**验证方法**: [如何验证]
**风险**: [潜在风险]
**置信度**: 0.XX
```

## 置信度标准

### 等级定义
- **>0.90**: 高度确信（充分证据，成功经验）
- **0.70-0.90**: 中等确信（合理推断，部分证据）
- **<0.70**: 低确信（有限信息，重大不确定）

### 使用指南
```markdown
## 置信度: 0.85
基于3个类似项目的成功经验，但需要验证当前环境兼容性
```

## 文件系统结构

### 项目根目录
```
.ai-runtime/
├── cognition/          # 认知记录和分析
├── commands/           # 命令系统和文档
├── constitution.md     # 宪法治理文档
├── memory/            # 分层记忆系统
└── toolkit/           # 工具装备系统
```

### 记忆系统结构
```
memory/
├── episodic/          # 情景记忆（事件时间线）
├── long-term/         # 长期记忆（技术知识）
├── short-term/        # 短期记忆（当前会话）
├── scripts/           # 查询脚本
├── references/        # 详细文档
└── SKILL.md          # 技能定义
```

## 故障排除

### 常见问题
- **命令不响应**: 检查语法，确认在正确上下文中使用
- **记忆查询无结果**: 验证WHERE条件语法和字段名称
- **置信度过低**: 需要更多信息或调查，主动提出澄清问题

### 紧急联系
- **宪法文档**: `.ai-runtime/constitution.md`
- **完整文档**: 各模块的references/目录
- **记忆查询**: `python3 .ai-runtime/memory/memory_cli.py --help`

## 版本信息

### 当前版本
- **CodeConscious**: 2.0.0
- **宪法版本**: 2.0.0
- **身份版本**: 2.0.0
- **最后更新**: 2025-11-14

### 兼容性
- **Python**: 3.8+
- **操作系统**: macOS, Linux
- **依赖**: PyYAML (核心)

## 更新日志

### v2.0.0 (2025-11-14)
- ✨ 完整宪法治理体系
- 🧠 分层记忆系统重构
- 🤖 自主学习能力增强
- 📚 渐进式披露文档架构
- 🛠️ 工具装备系统优化
