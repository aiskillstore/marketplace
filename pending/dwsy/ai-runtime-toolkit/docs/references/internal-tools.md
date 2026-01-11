---
name: internal-tools-reference
description: AI Runtime内部工具完整参考 - 包含所有内部创建的工具详细信息
category: reference
version: 1.0.0
---

# 内部工具完整参考

**最后更新**: 2025-11-14

---

## 工具概览

AI Runtime工具装备系统包含以下**内部创建的工具**（按语言分类）：

### Python工具 (python/)

| 工具名称 | ID | 用途 | 复杂度 | 文件位置 |
|---------|-----|-----|--------|----------|
| **依赖关系分析器** | PY-DEPENDENCY-ANALYZER-001 | CODE,DATA | level-3 | python/analysis/dependency-analyzer.py |
| **代码统计器** | PY-CODE-STATS-004 | CODE,DATA | level-2 | python/analysis/code-stats.py |
| **图形生成器** | PY-GRAPH-GENERATOR-002 | DATA,VISUAL | level-3 | python/graph/generate-graph.py |
| **报告生成器** | PY-REPORT-GENERATOR-005 | DOC,REPORT | level-3 | python/report/generate-report.py |

#### PY-DEPENDENCY-ANALYZER-001 依赖关系分析器

**元文件**: `python/analysis/dependency-analyzer.meta.yml`

**用途**: 分析Python/JavaScript项目的依赖关系，生成可视化报告

**功能特性**:
- 解析Python requirements.txt
- 解析JavaScript package.json
- 识别安全风险
- 生成Markdown报告
- 导出JSON格式

**使用方法**:
```bash
# 分析当前目录
python3 python/analysis/dependency-analyzer.py

# 分析指定项目
python3 python/analysis/dependency-analyzer.py /path/to/project

# 保存JSON报告
python3 python/analysis/dependency-analyzer.py . -o report.json

# 详细输出
python3 python/analysis/dependency-analyzer.py -v
```

**依赖要求**:
- Python >= 3.8
- 无第三方依赖（仅标准库）

**输入输出**:
- 输入: requirements.txt, package.json
- 输出: Markdown报告到stdout, JSON到文件（如果指定-o）

**上次使用**:
- 时间: 2025-11-14 10:30:00
- 用途: 分析ai-runtime项目依赖
- 满意度: 0.92

#### PY-CODE-STATS-004 代码统计器

**元文件**: `python/analysis/code-stats.meta.yml`

**用途**: 分析代码库统计信息，包括行数、函数、类、注释率和代码健康指标

**功能特性**:
- 统计代码行数（LOC）
- 统计函数和类数量
- 计算注释率
- 识别代码质量问题（长函数、复杂文件）

**使用方法**:
```bash
# 统计当前目录
python3 python/analysis/code-stats.py

# 统计指定目录
python3 python/analysis/code-stats.py src/

# 详细输出
python3 python/analysis/code-stats.py -v
```

**上次使用**:
- 时间: 2025-11-14 11:15:00
- 用途: 统计项目代码规模
- 满意度: 0.88

---

### Bash工具 (bash/)

| 工具名称 | ID | 用途 | 复杂度 | 文件位置 |
|---------|-----|-----|--------|----------|
| **服务健康检查器** | SERVICE-CHECK-001 | MONITOR | level-1 | bash/system/check-service.sh |
| **日志分析器** | BASH-ANALYZE-LOGS-002 | DATA,MONITOR | level-2 | bash/analysis/analyze-logs.sh |
| **磁盘健康检查器** | BASH-CHECK-DISK-003 | MONITOR | level-2 | bash/system/check-disk.sh |

#### SERVICE-CHECK-001 服务健康检查器

**元文件**: `bash/system/check-service.meta.yml`

**用途**: 检查HTTP服务、数据库、Redis的健康状态

**功能特性**:
- HTTP服务健康检查（/health端点）
- PostgreSQL数据库连接检查
- Redis连接和ping测试
- 可配置超时

**使用方法**:
```bash
# 检查HTTP服务
bash bash/system/check-service.sh auth-service http

# 检查数据库
bash bash/system/check-service.sh db-service db

# 检查Redis
bash bash/system/check-service.sh cache redis

# 自定义超时（10秒）
bash bash/system/check-service.sh myapp http 10
```

**依赖要求**:
- curl（HTTP检查）
- pg_isready（PostgreSQL检查）
- redis-cli（Redis检查）

**环境变量**:
- DB_HOST (默认: localhost)
- DB_PORT (默认: 5432)
- DB_NAME
- DB_USER
- REDIS_HOST (默认: localhost)
- REDIS_PORT (默认: 6379)

**上次使用**:
- 时间: 2025-11-14 16:45:00
- 用途: 验证auth-service修复后状态
- 满意度: 0.9

#### BASH-ANALYZE-LOGS-002 日志分析器

**元文件**: `bash/analysis/analyze-logs.meta.yml`

**用途**: 分析日志文件，按级别过滤、时间范围筛选、模式匹配和错误统计

**功能特性**:
- 按日志级别过滤（ERROR, WARN, INFO, DEBUG）
- 时间范围筛选
- 模式匹配
- 错误统计
- 生成摘要报告

**使用方法**:
```bash
# 分析日志并统计ERROR
bash bash/analysis/analyze-logs.sh /var/log/app.log --level ERROR

# 分析最近1小时的日志
bash bash/analysis/analyze-logs.sh /var/log/app.log --since "1 hour ago"

# 搜索特定模式
bash bash/analysis/analyze-logs.sh /var/log/app.log --pattern "connection failed"
```

**上次使用**:
- 时间: 2025-11-14 14:20:00
- 用途: 分析生产环境错误日志
- 满意度: 0.85

#### BASH-CHECK-DISK-003 磁盘健康检查器

**元文件**: `bash/system/check-disk.meta.yml`

**用途**: 检查磁盘空间、inode使用和健康状态，提供详细的分析和建议

**功能特性**:
- 磁盘空间使用检查（总容量、已使用、可用）
- Inode使用检查
- 使用阈值警报（可配置，默认80%）
- 文件系统类型检测
- 挂载点和权限检查
- 性能指标分析
- 智能建议生成

**使用方法**:
```bash
# 检查根目录（阈值80%）
bash bash/system/check-disk.sh /

# 检查日志目录自定义阈值（90%）
bash bash/system/check-disk.sh /var/log 90

# 检查所有挂载点
bash bash/system/check-disk.sh --all
```

**上次使用**:
- 时间: 2025-11-14 13:30:00
- 用途: 预防性检查服务器磁盘空间
- 满意度: 0.87

---

### Node.js工具 (node/)

| 工具名称 | ID | 用途 | 复杂度 | 文件位置 |
|---------|-----|-----|--------|----------|
| **API测试工具** | NODE-API-TESTER-001 | TEST,API | level-2 | node/api/test-api.js |

#### NODE-API-TESTER-001 API测试工具

**元文件**: `node/api/test-api.meta.yml`

**用途**: 测试RESTful API端点

**功能特性**:
- HTTP GET/POST/PUT/DELETE请求
- JSON请求体支持
- 响应验证
- 批量测试

**使用方法**:
```bash
# 测试API健康检查
node node/api/test-api.js http://localhost:3000

# 测试指定端点
node node/api/test-api.js http://localhost:3000/api/users

# POST测试（需要修改脚本）
node node/api/test-api.js post http://localhost:3000/api/users '{"name":"test"}'
```

**依赖要求**:
- Node.js 14+
- npm包: axios, chalk, commander（根据实际实现）

---

## 工具分类说明

### 按语言分类

| 语言 | 工具数量 | 主要用途 |
|-----|---------|---------|
| **python** | 4 | 代码分析、数据处理、报告生成 |
| **bash** | 3 | 系统监控、日志分析、服务检查 |
| **node** | 1 | API测试、网络操作 |

### 按复杂度分类

| 复杂度 | 数量 | 说明 |
|--------|-----|------|
| **level-1** | 1-5行 | 简单命令别名 |
| **level-2** | 6-20行 | 简单脚本（4个工具） |
| **level-3** | 21-50行 | 中等复杂度（3个工具） |
| **level-4** | 50+行 | 系统级工具（1个工具） |

### 按用途分类

| 用途 | 工具数量 | 代表工具 |
|-----|---------|---------|
| **CODE** | 3 | 依赖分析器、代码统计器 |
| **DATA** | 3 | 依赖分析器、日志分析器 |
| **MONITOR** | 3 | 服务检查、磁盘检查、日志分析 |
| **TEST** | 1 | API测试工具 |
| **API** | 1 | API测试工具 |
| **VISUAL** | 1 | 图形生成器 |
| **REPORT** | 1 | 报告生成器 |
| **DOC** | 2 | 报告生成器 |

---

## 维护信息

**最后审查**: 2025-11-14
**下次审查**: 2025-12-14
**维护者**: CodeConscious
**状态**: Active

## 相关文档

- **快速开始指南**: `@docs/guides/quickstart.md`
- **创建工具指南**: `@docs/guides/creating-tools.md`
- **外部工具整合**: `@docs/guides/external-integration.md`
- **工具分类说明**: `@docs/references/tool-categories.md`
