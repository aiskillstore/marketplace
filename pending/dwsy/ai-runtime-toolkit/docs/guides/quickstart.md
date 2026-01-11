---
name: quickstart
description: 工具装备系统快速入门指南
category: guide
version: 1.0.0
---

# 工具装备系统 - 快速开始

## 发现和使用工具

```bash
# 进入工具装备目录
cd .ai-runtime/toolkit

# 查看所有可用工具
python3 discover-toolkit.py list

# 查看所有可用工具（包含外部工具）
python3 discover-toolkit.py list --include-external

# 仅查看外部工具
python3 discover-toolkit.py list --external

# 查看特定工具详情
python3 discover-toolkit.py show SERVICE-CHECK-001

# 搜索相关工具（模糊匹配）
python3 discover-toolkit.py search health

# 推荐适合任务的工具
python3 discover-toolkit.py recommend "检查数据库连接"

# 直接运行工具
python3 discover-toolkit.py run dependency-analyzer . -o report.json

# 查看工具使用历史（如果有）
python3 discover-toolkit.py history
```

## 可用的工具

### 内部工具（AI-Runtime创建）

| 工具名称 | ID | 语言 | 用途 | 描述 |
|---------|-----|------|-----|------|
| **服务健康检查器** | SERVICE-CHECK-001 | bash | MONITOR | 检查HTTP服务、数据库、Redis的健康状态 |
| **依赖分析器** | PY-DEPENDENCY-ANALYZER-001 | python | CODE,DATA | 分析Python/JavaScript项目的依赖关系 |
| **代码统计器** | PY-CODE-STATS-004 | python | CODE,DATA | 分析代码库统计信息 |
| **日志分析器** | BASH-ANALYZE-LOGS-002 | bash | DATA,MONITOR | 分析日志文件 |
| **磁盘健康检查器** | BASH-CHECK-DISK-003 | bash | MONITOR | 检查磁盘空间和使用情况 |

#### 服务健康检查器
- **文件**: `bash/system/check-service.sh`
- **用途**: 检查HTTP服务、数据库、Redis的健康状态
- **使用**: `bash check-service.sh <服务名> <类型> [超时]`
- **类型**: http, db/database, redis
- **示例**:
  ```bash
  bash check-service.sh auth-service http
  bash check-service.sh db-service db
  ```

#### 依赖分析器
- **文件**: `python/analysis/dependency-analyzer.py`
- **用途**: 分析Python/JavaScript项目的依赖关系，生成可视化报告
- **使用**: `python3 dependency-analyzer.py [项目目录] -o report.json`
- **支持**: requirements.txt, package.json
- **功能**: 依赖解析、安全风险检测、报告生成
- **示例**:
  ```bash
  python3 dependency-analyzer.py
  python3 dependency-analyzer.py /path/to/project
  python3 dependency-analyzer.py . -o report.json
  ```

#### API测试工具
- **文件**: `node/api/test-api.js`
- **用途**: 测试RESTful API端点
- **使用**: `node test-api.js [base-url]`
- **示例**:
  ```bash
  node test-api.js http://localhost:3000
  ```

## 工具使用流程

### 场景1：探索新项目
```bash
# 1. 查看项目结构
python3 discover-toolkit.py list

# 2. 分析项目依赖
python3 discover-toolkit.py run dependency-analyzer . -o deps.json

# 3. 检查服务健康（如果适用）
bash bash/system/check-service.sh myapp http
```

### 场景2：排查问题
```bash
# 1. 搜索相关工具
python3 discover-toolkit.py search log

# 2. 分析日志
bash bash/analysis/analyze-logs.sh /path/to/logs --level ERROR

# 3. 检查磁盘空间
bash bash/system/check-disk.sh /
```

### 场景3：常规监控
```bash
# 1. 检查所有服务
for service in auth db cache; do
  bash bash/system/check-service.sh $service http
done

# 2. 生成健康报告
python3 discover-toolkit.py recommend "health check"
```

## 下一步学习

- **查看完整参考**: `@docs/references/internal-tools.md`
- **了解外部工具**: `@docs/external-integration.md`
- **学习如何创建工具**: `@docs/guides/creating-tools.md`
