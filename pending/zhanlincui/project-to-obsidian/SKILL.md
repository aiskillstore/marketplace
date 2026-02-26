---
name: project-to-obsidian
description: |
  将代码项目转换为 Obsidian 知识库。当用户提到 obsidian、项目文档、知识库、分析项目、转换项目 时激活。

  【激活后必须执行】：
  1. 先完整阅读本 SKILL.md 文件
  2. 理解 AI 写入规则（默认到 00_Inbox/AI/、追加式、统一 Schema）
  3. 执行 STEP 0: 使用 AskUserQuestion 询问用户确认
  4. 用户确认后才开始 STEP 1 项目扫描
  5. 严格按 STEP 0 → 1 → 2 → 3 → 4 顺序执行

  【禁止行为】：
  - 禁止不读 SKILL.md 就开始分析项目
  - 禁止跳过 STEP 0 用户确认
  - 禁止直接在 30_Resources 创建（先到 00_Inbox/AI/）
  - 禁止自作主张决定输出位置
version: 1.4.0
author: Claude Code
---

# Project to Obsidian - 项目知识库生成器

将任意代码项目转换为结构化的 Obsidian 知识库，让项目知识可搜索、可链接、可扩展。

---

## 🎯 核心功能

| 命令 | 功能 | 说明 |
|------|------|------|
| `/p2o <项目路径>` | 完整转换 | 分析项目并生成完整 Obsidian 库 |
| `/p2o <路径> --quick` | 快速概览 | 只生成项目概览和结构 |
| `/p2o <路径> --api` | API 文档 | 专注生成 API/函数文档 |
| `/p2o <路径> --arch` | 架构文档 | 生成架构和设计文档 |

---

## ⚡ 执行流程

```
用户意图: "把这个项目转成知识库" / /p2o
              ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 0: 用户确认（必须）                                │
│                                                         │
│  Claude 使用 AskUserQuestion 工具询问：                   │
│                                                         │
│  "检测到你想将项目转换为 Obsidian 知识库，请确认："        │
│                                                         │
│  📁 项目路径: /path/to/project                           │
│                                                         │
│  选择输出方式：                                           │
│  [1] 写入 Obsidian vault（需要 MCP）                     │
│  [2] 创建本地文件夹                                       │
│  [3] 输出到项目 /docs 目录                                │
│  [4] 取消                                                │
│                                                         │
│  用户选择后才继续执行。                                    │
└─────────────────────────────────────────────────────────┘
              ↓
        用户确认后
              ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: 项目扫描                                       │
│  ├─ 读取项目结构 (Glob + Bash ls/find)                   │
│  ├─ 识别项目类型 (package.json/Cargo.toml/go.mod 等)     │
│  ├─ 检测主要语言和框架                                    │
│  └─ 生成文件清单                                         │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: 代码分析                                       │
│  ├─ 读取关键文件 (入口、配置、核心模块)                    │
│  ├─ 提取：                                               │
│  │   ├─ 函数/类/接口定义                                 │
│  │   ├─ API 端点                                        │
│  │   ├─ 依赖关系                                        │
│  │   ├─ 配置项                                          │
│  │   └─ 注释和文档字符串                                 │
│  └─ 构建代码知识图谱                                     │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: 文档生成                                       │
│  ├─ 生成 Obsidian 目录结构                               │
│  ├─ 创建各类文档：                                       │
│  │   ├─ 00-项目概览.md (MOC)                            │
│  │   ├─ 01-快速开始.md                                  │
│  │   ├─ 02-架构设计.md                                  │
│  │   ├─ 03-API文档/                                     │
│  │   ├─ 04-模块说明/                                    │
│  │   ├─ 05-配置参考.md                                  │
│  │   └─ 06-开发指南.md                                  │
│  └─ 添加双向链接 [[]] 和标签 #tag                        │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 4: 输出到 Obsidian                                │
│  ├─ 方式A: 写入 00_Inbox/AI/{{项目名}}/ (推荐，先落地)    │
│  ├─ 方式B: 写入 30_Resources/Projects/{{项目名}}/        │
│  └─ 方式C: 创建本地文件夹                                 │
└─────────────────────────────────────────────────────────┘
              ↓
         完成报告
```

---

## ⚠️ AI 写入规则（必须遵守）

### 规则 1: 默认落地到 AI 专区
```
首选位置: 00_Inbox/AI/{{项目名}}-知识库/
用户确认后可移动到: 30_Resources/Projects/
```

### 规则 2: 使用追加式写入
```
✅ obsidian_append_content - 创建新文件
✅ obsidian_patch_content - 追加到指定位置
❌ 不要覆盖已存在的笔记
```

### 规则 3: 统一 Properties Schema
```yaml
# 项目文档统一使用以下字段
---
type: project-doc          # project-doc | api | module | architecture
project: "{{项目名}}"
source: "{{项目路径}}"
language: ""               # typescript | python | go | rust | java
framework: ""              # react | express | fastapi | gin
tags: []
created: {{date}}
---
```

### 规则 4: 生成 Dataview 索引
```
在项目概览中自动添加 Dataview 查询：
- 模块列表
- API 端点列表
- 最近修改
```

---

## 📋 详细执行步骤

### STEP 0: 用户确认（必须先执行）

**当 skill 被触发时，Claude 必须首先使用 AskUserQuestion 工具询问用户：**

```
AskUserQuestion:
  question: "检测到你想将项目转换为 Obsidian 知识库"
  header: "确认"
  options:
    - label: "写入 Obsidian vault"
      description: "使用 MCP 直接写入你的 Obsidian 库（推荐）"
    - label: "创建本地文件夹"
      description: "在指定位置创建新的知识库文件夹"
    - label: "输出到 /docs"
      description: "在当前项目目录下创建 docs/obsidian/"
    - label: "取消"
      description: "不执行转换"
```

**用户选择「取消」时，立即停止，不执行后续步骤。**

**用户确认后，继续显示项目信息并询问生成模式：**

```
AskUserQuestion:
  question: "选择生成模式"
  header: "模式"
  options:
    - label: "完整模式"
      description: "生成全部文档：概览、架构、API、模块说明"
    - label: "快速模式"
      description: "只生成项目概览和目录结构"
    - label: "API 文档"
      description: "专注生成 API/接口文档"
```

### STEP 1: 项目扫描

```python
# Claude 执行的分析逻辑

# 1. 获取项目结构
使用 Glob 工具扫描：
- **/*.{js,ts,py,go,rs,java,rb,php,swift,kt}  # 代码文件
- **/package.json, **/Cargo.toml, **/go.mod   # 项目配置
- **/*.{md,txt}                                # 文档
- **/.env*, **/config.*                        # 配置文件

# 2. 识别项目类型
检测标志文件：
- package.json → Node.js/前端项目
- Cargo.toml → Rust 项目
- go.mod → Go 项目
- pyproject.toml/setup.py → Python 项目
- pom.xml/build.gradle → Java 项目
- Gemfile → Ruby 项目

# 3. 识别框架
检测特征：
- next.config.* → Next.js
- vite.config.* → Vite
- tsconfig.json → TypeScript
- Dockerfile → Docker 化项目
- .github/workflows → CI/CD
```

### STEP 3: 代码分析

```
对每个关键文件，Claude 需要提取：

├─ 入口文件 (main.*, index.*, app.*)
│   ├─ 应用初始化流程
│   ├─ 路由配置
│   └─ 中间件设置
│
├─ API/路由文件
│   ├─ 端点路径
│   ├─ HTTP 方法
│   ├─ 请求参数
│   └─ 响应格式
│
├─ 模型/类型定义
│   ├─ 数据结构
│   ├─ 接口定义
│   └─ 类型别名
│
├─ 服务/业务逻辑
│   ├─ 核心函数
│   ├─ 业务流程
│   └─ 外部调用
│
└─ 配置文件
    ├─ 环境变量
    ├─ 功能开关
    └─ 第三方配置
```

### STEP 4: 生成 Obsidian 结构

```
生成的 Obsidian 目录结构：

{{项目名}}-知识库/
├─ 00-项目概览.md          # MOC - 主入口
├─ 01-快速开始.md          # 安装、运行、基本使用
├─ 02-架构设计/
│   ├─ 整体架构.md
│   ├─ 目录结构.md
│   └─ 技术栈.md
├─ 03-API文档/
│   ├─ _API索引.md         # API MOC
│   ├─ 用户相关.md
│   ├─ 订单相关.md
│   └─ ...
├─ 04-模块说明/
│   ├─ _模块索引.md        # 模块 MOC
│   ├─ 核心模块.md
│   ├─ 工具函数.md
│   └─ ...
├─ 05-配置参考.md          # 环境变量、配置项
├─ 06-开发指南/
│   ├─ 本地开发.md
│   ├─ 测试指南.md
│   └─ 部署流程.md
└─ _templates/             # Obsidian 模板
    ├─ 新功能模板.md
    └─ Bug记录模板.md
```

---

## 📝 文档模板

### 项目概览模板 (MOC)

```markdown
---
tags: [project, moc, {{项目类型}}]
created: {{日期}}
---

# {{项目名}} 知识库

> {{一句话描述}}

## 🚀 快速导航

- [[01-快速开始|快速开始]] - 5 分钟上手
- [[02-架构设计/整体架构|架构设计]] - 了解系统设计
- [[03-API文档/_API索引|API 文档]] - 接口参考

## 📊 项目信息

| 属性 | 值 |
|------|-----|
| 语言 | {{主语言}} |
| 框架 | {{框架}} |
| 版本 | {{版本}} |
| 仓库 | {{仓库地址}} |

## 🗂️ 目录结构

```
{{项目结构树}}
```

## 🔗 核心模块

{{模块链接列表}}

## 📅 最近更新

- {{更新记录}}

---
*由 project-to-obsidian 自动生成*
```

### API 文档模板

```markdown
---
tags: [api, {{模块}}]
endpoint: {{路径}}
method: {{方法}}
---

# {{API名称}}

> {{描述}}

## 请求

```http
{{方法}} {{路径}}
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
{{参数表}}

### 请求示例

```json
{{请求示例}}
```

## 响应

### 成功响应

```json
{{响应示例}}
```

## 相关

- [[{{相关API}}]]
- [[{{相关模块}}]]
```

### 模块说明模板

```markdown
---
tags: [module, {{标签}}]
path: {{文件路径}}
---

# {{模块名}}

> {{模块描述}}

## 职责

{{职责说明}}

## 核心函数

### `{{函数名}}`

```{{语言}}
{{函数签名}}
```

**参数：**
{{参数说明}}

**返回：**
{{返回说明}}

**示例：**
```{{语言}}
{{使用示例}}
```

## 依赖关系

```mermaid
graph LR
    {{模块}} --> {{依赖1}}
    {{模块}} --> {{依赖2}}
```

## 相关模块

- [[{{相关模块1}}]]
- [[{{相关模块2}}]]
```

---

## 🔧 输出选项

### 选项 1: 输出到 Obsidian Vault (推荐)

```
如果检测到 Obsidian MCP 可用：
├─ 询问用户选择目标 vault
├─ 在 vault 中创建项目文件夹
├─ 使用 obsidian_append_content 写入文件
└─ 完成后可直接使用 obsidian-helper 功能
```

### 选项 2: 创建本地文件夹

```
├─ 询问输出路径
├─ 创建 {{项目名}}-knowledge-base/ 文件夹
├─ 使用 Write 工具写入所有文件
└─ 提示用户在 Obsidian 中打开该文件夹
```

### 选项 3: 输出到项目 /docs

```
├─ 在项目目录创建 /docs/obsidian/ 文件夹
├─ 写入所有文档
├─ 添加 .gitignore 排除（可选）
└─ 文档与代码同步版本控制
```

---

## 🎯 使用示例

### 示例 1: 完整转换

```
用户: /p2o /Users/jun/Projects/my-api

Claude:
1. 扫描项目... 检测到 Node.js + Express 项目
2. 分析代码... 找到 15 个 API 端点，8 个核心模块
3. 询问：输出到哪里？
   - [1] 当前 Obsidian vault (Projects/ 文件夹)
   - [2] 新建文件夹
   - [3] 项目内 /docs
4. 用户选择 [1]
5. 生成文档到 Obsidian vault
6. 完成！生成了 23 个笔记文件
```

### 示例 2: 快速概览

```
用户: /p2o ~/code/rust-project --quick

Claude:
1. 快速扫描项目结构
2. 生成：
   - 项目概览.md
   - 目录结构.md
   - 技术栈.md
3. 输出 3 个文件到指定位置
```

### 示例 3: 只生成 API 文档

```
用户: /p2o ./backend --api

Claude:
1. 扫描 API 路由文件
2. 提取所有端点
3. 生成 API 文档集合
4. 输出到 Obsidian
```

---

## 🔗 与其他工具集成

### 与 obsidian-helper 集成

生成的知识库完全兼容 obsidian-helper：

```
/daily
→ 在日记中记录「今天研究了 [[my-api-知识库/03-API文档/用户认证|用户认证 API]]」

/capture API设计 发现了一个新的设计模式
→ 自动链接到相关 API 文档

/review weekly
→ 回顾中包含项目相关笔记的修改
```

### 与 MCP 工具集成

```
生成后可使用 MCP 工具：
├─ obsidian_simple_search - 搜索项目文档
├─ obsidian_patch_content - 更新文档
├─ obsidian_get_file_contents - 读取文档
└─ obsidian_append_content - 添加新文档
```

---

## ⚙️ 配置选项

在目标 vault 创建 `_config/project-to-obsidian.md` 自定义：

```markdown
# Project to Obsidian 配置

## 生成选项
- 生成 Mermaid 图表: true
- 生成代码示例: true
- 提取注释: true
- 最大文件大小: 100KB

## 忽略规则
- 忽略文件夹: node_modules, .git, dist, build, __pycache__
- 忽略文件: *.min.js, *.map, *.lock

## 输出设置
- 默认输出位置: Projects/
- 文档语言: zh-CN
- 链接样式: wiki-link
```

---

## 🚨 错误处理

| 情况 | 处理 |
|------|------|
| 项目路径不存在 | 提示用户检查路径 |
| 项目太大 (>1000 文件) | 建议使用 --quick 模式或指定子目录 |
| 无法识别项目类型 | 询问用户手动指定语言/框架 |
| MCP 未连接 | 自动切换到本地文件输出 |
| 写入失败 | 回滚并提示错误原因 |

---

## 📚 支持的项目类型

| 语言/框架 | 识别标志 | 特殊处理 |
|-----------|----------|----------|
| Node.js | package.json | 提取 scripts, dependencies |
| TypeScript | tsconfig.json | 提取类型定义 |
| Python | pyproject.toml, setup.py | 提取 docstrings |
| Go | go.mod | 提取包结构 |
| Rust | Cargo.toml | 提取 crate 结构 |
| Java | pom.xml, build.gradle | 提取类和接口 |
| React/Vue/Angular | 框架配置 | 提取组件结构 |
| Express/FastAPI/Gin | 路由文件 | 提取 API 端点 |

---

## 📎 快速参考

```
/p2o <路径>              → 完整转换项目到 Obsidian
/p2o <路径> --quick      → 快速生成概览
/p2o <路径> --api        → 只生成 API 文档
/p2o <路径> --arch       → 只生成架构文档
/p2o <路径> -o <输出>    → 指定输出位置
```

---

*Project to Obsidian v1.0.0 - 让代码知识可视化*
