---
name: creating-tools-guide
description: 在AI Runtime工具装备系统中创建新工具的完整指南
category: guide
version: 1.0.0
---

# 如何创造新工具 - 完整指南

## 创造新工具的流程

### 步骤1: 识别需求

在创造新工具之前，先问自己：

```markdown
✅ 这个需求是否真实存在？
   - 是否已经重复执行某个任务超过3次？
   - 是否花费了超过1小时的手动操作？

✅ 是否有现有工具可以解决？
   - 检查: python3 discover-toolkit.py search "关键词"
   - 检查: 外部工具是否可用？

✅ 这个工具是否对其他人也有价值？
   - 不只是解决一次性问题
   - 可能是可复用的模式

✅ 复杂度是否适合工具化？
   - level-1 (1-5行): 简单命令别名
   - level-2 (6-20行): 简单脚本
   - level-3 (21-50行): 中等复杂度
   - level-4 (50+行): 系统级工具
```

### 步骤2: 选择工具类型

根据需求选择合适的工具类型：

#### 选项A: Shell脚本工具 (bash/)

**适用场景**：
- 系统管理任务
- 文件操作
- 命令编排
- 快速原型

**优点**：
- 无需额外依赖
- 启动速度快
- 与系统紧密集成

**示例**：
```bash
#!/bin/bash
# bash/monitor/check-disk.sh
echo "检查磁盘空间..."
df -h | grep -E '^/dev/' | awk '$5 > 80 {print "警告: " $0}'
```

#### 选项B: Python工具 (python/)

**适用场景**：
- 复杂逻辑
- 数据处理
- 结构化输出
- 需要库支持

**优点**：
- 强大的标准库
- 跨平台
- 易于测试
- 类型安全（可选）

**示例**：
```python
#!/usr/bin/env python3
# python/analysis/dependency-analyzer.py
"""
分析项目依赖关系
"""
import json
import sys

def analyze_dependencies(project_path):
    """分析依赖"""
    # 实现逻辑
    pass

if __name__ == '__main__':
    analyze_dependencies(sys.argv[1])
```

#### 选项C: Node.js工具 (node/)

**适用场景**：
- API测试
- Web相关工具
- JavaScript生态

**优点**：
- 丰富的npm包
- 异步I/O
- 适合网络操作

**示例**：
```javascript
// node/api/test-api.js
const http = require('http');

function testApi(baseUrl) {
    http.get(`${baseUrl}/health`, (res) => {
        console.log('API响应:', res.statusCode);
    });
}
```

### 步骤3: 创建工具和元数据

#### 示例：创建一个日志分析工具

**1. 创建工具脚本**

```bash
# bash/analysis/analyze-logs-v2.sh
#!/bin/bash
# 分析日志文件，提取错误和警告

LOG_FILE="$1"
echo "=== 日志分析开始 ==="
echo "分析文件: $LOG_FILE"

# 统计ERROR数量
echo "ERROR数量:"
grep -c "ERROR" "$LOG_FILE" || echo "0"

# 统计WARN数量
echo "WARN数量:"
grep -c "WARN" "$LOG_FILE" || echo "0"

echo "=== 日志分析完成 ==="
```

**2. 创建元数据文件**

在相同目录创建 `.meta.yml`：

```yaml
# bash/analysis/analyze-logs-v2.meta.yml
tool_id: BASH-ANALYZE-LOGS-V2-001
tool_name: "日志分析器V2"

基本信息:
  语言: bash
  文件: analyze-logs-v2.sh
  复杂度: level-2
  创建日期: 2025-11-14
  作者: YourName

用途分类:
  - DATA  # 数据分析
  - MONITOR  # 监控诊断

功能描述:
  简介: "分析日志文件，提取错误和警告统计"
  详细: |
    支持功能:
    - 统计ERROR数量
    - 统计WARN数量
    - 显示分析摘要

使用场景:
  - "分析应用日志，识别错误模式"
  - "监控日志文件，统计错误频率"
  - "生成日志分析报告"

使用方法:
  命令: "bash analyze-logs-v2.sh <日志文件>"
  参数:
    日志文件: "要分析的日志文件路径"
  示例:
    - "分析单个日志: bash analyze-logs-v2.sh app.log"

依赖要求:
  系统命令:
    - grep: "用于搜索日志内容"
    - wc: "用于统计行数"
  环境变量: 无

输入输出:
  输入:
    - 日志文件（纯文本格式）
  输出:
    - stdout: 分析结果
    - 退出码: 0（成功），非0（错误）

维护记录:
  2025-11-14:
    - 初始创建
    - 实现ERROR和WARN统计
```

### 步骤4: 测试工具

```bash
# 1. 赋予执行权限
chmod +x bash/analysis/analyze-logs-v2.sh

# 2. 创建测试日志
cat > test.log << 'EOF'
INFO: Starting application
INFO: Processing request #1
WARN: Timeout on request #1
ERROR: Failed to connect to database
INFO: Retrying...
ERROR: Database connection failed
EOF

# 3. 运行工具测试
bash bash/analysis/analyze-logs-v2.sh test.log

# 期望输出:
# === 日志分析开始 ===
# 分析文件: test.log
# ERROR数量: 2
# WARN数量: 1
# === 日志分析完成 ===

# 4. 删除测试文件
rm test.log
```

### 步骤5: 注册和验证

```bash
# 验证工具被检测到
python3 discover-toolkit.py list | grep LOGS-V2

# 查看工具详细信息
python3 discover-toolkit.py show BASH-ANALYZE-LOGS-V2-001

# 搜索相关工具
python3 discover-toolkit.py search log

# 推荐工具（应该推荐我们的新工具）
python3 discover-toolkit.py recommend "分析日志"
```

### 步骤6: 文档和分享

**1. 创建工具文档**

```markdown
# docs/tools/internal/analyze-logs-v2.md
---
name: analyze-logs-v2
description: 分析日志文件，统计错误和警告
---

# 日志分析器V2

## 用途
快速分析日志文件，统计错误和警告数量

## 使用
```bash
bash bash/analysis/analyze-logs-v2.sh <日志文件>
```

## 示例
```bash
bash bash/analysis/analyze-logs-v2.sh app.log
```

## 输出
```
=== 日志分析开始 ===
分析文件: app.log
ERROR数量: 5
WARN数量: 12
=== 日志分析完成 ===
```
```

**2. 更新主文档**

如果这是重要工具，考虑添加到 `@docs/guides/quickstart.md`

## 工具质量检查清单

在发布工具之前，请检查：

### 功能检查
- [ ] 工具完成预期任务
- [ ] 处理边界情况（空输入、错误输入）
- [ ] 错误处理友好
- [ ] 输出清晰可读

### 代码质量
- [ ] 代码有注释
- [ ] 遵循语言规范
- [ ] 变量命名清晰
- [ ] 没有重复代码

### 元数据检查
- [ ] 填写完整的.meta.yml
- [ ] ID格式正确（LANG-CATEGORY-NAME-001）
- [ ] 包含使用示例
- [ ] 标记了依赖项

### 测试验证
- [ ] 本地测试通过
- [ ] discover-toolkit能检测到
- [ ] show命令显示正确
- [ ] 搜索能找到

### 文档检查
- [ ] 创建了工具文档
- [ ] 更新相关索引
- [ ] 添加了使用示例

## 常见错误

### 1. 权限错误
```bash
chmod +x script.sh  # 记得添加执行权限
```

### 2. 缺少shebang
```bash
#!/bin/bash  # Bash脚本
#!/usr/bin/env python3  # Python脚本
#!/usr/bin/env node  # Node.js脚本
```

### 3. 路径错误
使用相对路径（相对于toolkit根目录）：
```yaml
# 正确
文件: python/analysis/my-tool.py

# 错误（绝对路径）
文件: /Users/.../toolkit/python/analysis/my-tool.py
```

### 4. YAML格式错误
```bash
# 验证YAML语法
python3 -c "import yaml; yaml.safe_load(open('meta.yml'))"
```

## 高级：工具模板

可以使用工具模板快速创建新工具：

```bash
# 复制模板
cp templates/tool-template.sh bash/category/my-tool.sh
cp templates/template.meta.yml bash/category/my-tool.meta.yml

# 修改内容
nano bash/category/my-tool.sh
nano bash/category/my-tool.meta.yml

# 测试
bash bash/category/my-tool.sh
python3 discover-toolkit.py show MY-TOOL-001
```

## 获取帮助

如果遇到困难：

1. **查看现有工具**: `python3 discover-toolkit.py list`
2. **查看示例元文件**: `cat bash/*/*.meta.yml`
3. **查看创建指南**: `@docs/guides/creating-tools.md`
4. **检查外部工具**: `@docs/guides/external-integration.md`

## 贡献工具

如果想贡献工具到AI Runtime：

1. **Fork仓库**: 创建自己的分支
2. **创建工具**: 按照本指南
3. **测试验证**: 确保工具正常工作
4. **提交PR**: 包含工具说明和使用场景
5. **审查合并**: 等待review和merge

## 工具版本管理

为工具添加版本信息：

```yaml
# 在.meta.yml中添加
版本信息:
  当前版本: "1.0.0"
  发布日期: "2025-11-14"
  更新日志:
    - "1.0.0: 初始发布"
```

---

**最后更新**: 2025-11-14
**指南版本**: 1.0.0
**维护者**: CodeConscious
