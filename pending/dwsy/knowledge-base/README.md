# Knowledge Base Skill

专业的知识库管理系统，旨在解决"知识诅咒"（Curse of Knowledge）和认知偏差问题。通过显式化隐性知识、扫描代码提取领域概念、整合行业最佳实践，构建结构化的 Markdown 知识库。

## 特性

- 🧠 **打破知识诅咒**: 强制显式化隐性知识，记录常见误区
- 📂 **多级分类**: 支持任意层级的目录结构，灵活组织知识
- 🔍 **代码扫描**: 自动识别代码中的领域概念，建议文档化
- 📖 **结构化模板**: Concept、Guide、Decision 三种文档类型
- 🔗 **智能索引**: 自动生成层级化的知识索引
- 🔎 **全文搜索**: 支持关键词搜索所有知识文档
- 💡 **认知对齐**: 决策记录包含"认知对齐"章节
- 📚 **行业共识**: 整合标准规范，避免重复定义
- 🤖 **AI 驱动**: 可配合 Knowledge Builder Extension 实现自动化文档生成

## 相关项目

- **[Knowledge Builder Extension](https://github.com/Dwsy/knowledge-builder-extension)**: 使用自然语言和 AI 自动构建知识库的扩展工具

## 快速开始

### 1. 初始化项目知识库

```bash
cd /path/to/project
bun ~/.pi/agent/skills/knowledge-base/lib.ts init
```

这将创建以下结构：

```
docs/knowledge/
├── concepts/    # 领域概念与术语
├── guides/      # 操作指南与最佳实践
├── decisions/   # 架构决策记录
├── external/    # 行业共识与外部参考
└── index.md     # 自动生成的索引
```

### 2. 创建文档

```bash
# 创建一级文档（无分类）
bun ~/.pi/agent/skills/knowledge-base/lib.ts create concept "UserAuthentication"

# 创建二级分类文档
bun ~/.pi/agent/skills/knowledge-base/lib.ts create concept "User" auth
bun ~/.pi/agent/skills/knowledge-base/lib.ts create guide "API" backend

# 创建三级分类文档
bun ~/.pi/agent/skills/knowledge-base/lib.ts create concept "AceTool" core/tools
bun ~/.pi/agent/skills/knowledge-base/lib.ts create guide "ErrorHandling" backend/api
bun ~/.pi/agent/skills/knowledge-base/lib.ts create decision "Redis" database/cache

# 创建四级或更深分类文档（支持无限层级）
bun ~/.pi/agent/skills/knowledge-base/lib.ts create concept "MobileFirst" frontend/responsive/design
bun ~/.pi/agent/skills/knowledge-base/lib.ts create concept "ProgressiveWebApp" frontend/pwa/advanced/optimization
bun ~/.pi/agent/skills/knowledge-base/lib.ts create guide "ResponsiveLayout" frontend/css/flexbox
bun ~/.pi/agent/skills/knowledge-base/lib.ts create decision "WhyUseCSSGrid" frontend/layout/modern/strategies
```

### 3. 扫描代码

```bash
bun ~/.pi/agent/skills/knowledge-base/lib.ts scan
```

自动分析代码库，识别需要文档化的概念。

### 4. 发现项目结构并生成文档清单

```bash
bun ~/.pi/agent/skills/knowledge-base/lib.ts discover
```

分析项目目录结构，识别技术目录，并生成知识库文档清单和建议。

**功能特点**:
- 自动识别常见技术目录（auth, api, components, database 等）
- 为每个目录推荐相关的概念和指南
- 提供创建文档的完整命令
- 显示文档完成进度
- 支持去重（已存在的文档不会重复建议）

### 5. 生成索引

```bash
bun ~/.pi/agent/skills/knowledge-base/lib.ts index
```

### 6. 搜索知识

```bash
bun ~/.pi/agent/skills/knowledge-base/lib.ts search "keyword"
```

## 文档类型

### Concept（概念）
定义领域术语和核心概念，包含：
- Definition（定义）
- Context（上下文）
- Implementation（实现位置）
- Common Misconceptions（常见误区）
- Relationships（关联）
- References（参考）

### Guide（指南）
操作指南和最佳实践，包含：
- Goal（目标）
- Prerequisites（前置知识）
- Steps（步骤）
- Best Practices（最佳实践）
- Examples（示例）

### Decision（决策）
架构决策记录，包含：
- Context（背景）
- Options Considered（考虑过的选项）
- The Decision（最终决策）
- Cognitive Alignment（认知对齐）
- Consequences（后果）

## 目录结构示例

```
docs/knowledge/
├── concepts/
│   ├── KnowledgeBase.md                    # 一级文档
│   ├── CurseOfKnowledge.md                 # 一级文档
│   ├── core/                               # 二级分类
│   │   ├── tools/
│   │   │   └── AceTool.md                  # 三级文档
│   │   ├── workflow/
│   │   │   └── Workhub.md                  # 三级文档
│   │   └── architecture/
│   │       └── SkillSystem.md              # 三级文档
│   └── frontend/                           # 二级分类
│       ├── responsive/                     # 三级分类
│       │   └── design/                     # 四级分类
│       │       └── MobileFirst.md          # 四级文档
│       └── pwa/                            # 三级分类
│           └── advanced/                   # 四级分类
│               └── optimization/           # 五级分类
│                   └── ProgressiveWebApp.md # 五级文档
├── guides/
│   ├── HowToUseKnowledgeBase.md            # 一级文档
│   ├── core/                               # 二级分类
│   │   ├── development/
│   │   │   └── HowToCreateSkill.md         # 三级文档
│   │   └── management/
│   │       └── HowToOrganizeKnowledge.md   # 三级文档
│   └── frontend/                           # 二级分类
│       └── css/                            # 三级分类
│           └── flexbox/                    # 四级分类
│               └── ResponsiveLayout.md     # 四级文档
├── decisions/
│   ├── 20260107-WhyWeBuiltKnowledgeBase.md # 一级文档
│   ├── core/                               # 二级分类
│   │   └── language/
│   │       └── 20260107-WhyUseTypeScript.md # 三级文档
│   └── frontend/                           # 二级分类
│       └── layout/                         # 三级分类
│           └── modern/                     # 四级分类
│               └── strategies/             # 五级分类
│                   └── 20260107-WhyUseCSSGrid.md # 五级文档
└── external/
    └── RESTfulAPIConsensus.md
```

## 最佳实践

### 分类策略

**按模块分类**（推荐用于功能模块清晰的项目）
```
concepts/
├── auth/              # 认证模块
├── payment/           # 支付模块
└── common/            # 通用概念
```

**按层级分类**（推荐用于复杂系统）
```
concepts/
├── core/              # 核心概念
├── domain/            # 领域概念
└── infrastructure/    # 基础设施
```

### 使用建议

- ✅ 遇到不懂的术语时，立即创建概念文档
- ✅ 代码 Review 时，如果需要解释超过 3 句，创建指南
- ✅ 记录"为什么"而不仅仅是"怎么做"
- ✅ 分类层级不超过 5 层
- ✅ 定期运行 `discover` 查看文档完成进度
- ✅ 使用 `discover` 生成的清单系统化构建知识库
- ❌ 不要使用递归定义
- ❌ 不要忽略常见误区记录

### Discover 功能详解

**运行命令**:
```bash
bun ~/.pi/agent/skills/knowledge-base/lib.ts discover
```

**输出内容**:
- `discovery_report.md`: 详细的发现报告

**报告包含**:
1. **项目概览**: 发现的技术目录数量、置信度统计
2. **目录详情**: 每个技术目录的建议文档（概念和指南）
3. **快速开始指南**: 系统化构建知识库的步骤
4. **进度追踪**: 文档完成度百分比

**支持的技术目录类型**:
- `auth`: 认证和授权
- `api`: API 设计和开发
- `components`: 前端组件
- `config`: 配置管理
- `database`: 数据库相关
- `utils`: 工具函数
- `services`: 服务层
- `models`: 数据模型
- `hooks`: React Hooks
- `store`: 状态管理
- `middleware`: 中间件
- `routes`: 路由
- `tests`: 测试
- `docker`: Docker 容器化
- `deploy`: 部署

**使用流程**:
```bash
# 1. 运行发现
bun ~/.pi/agent/skills/knowledge-base/lib.ts discover

# 2. 查看报告
cat docs/knowledge/discovery_report.md

# 3. 根据建议创建文档（复制报告中的命令）
bun ~/.pi/agent/skills/knowledge-base/lib.ts create concept "Authentication" auth

# 4. 重新运行发现查看进度
bun ~/.pi/agent/skills/knowledge-base/lib.ts discover
```

## 核心原则

### 1. 显式化（Explicitness）
强制将默会知识（Tacit Knowledge）转化为显性知识（Explicit Knowledge）。

### 2. 上下文对齐（Context Alignment）
通过代码扫描提取领域术语，建立统一词汇表。

### 3. 认知共识（Cognitive Consensus）
记录"为什么这样做"而不仅仅是"怎么做"。

### 4. SSOT（Single Source of Truth）
每个知识领域只有一个权威文档。

## 依赖

- Node.js / Bun
- 无外部依赖（纯 TypeScript 实现）

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关资源

- [Curse of Knowledge - Wikipedia](https://en.wikipedia.org/wiki/Curse_of_knowledge)
- [ADR (Architecture Decision Records)](https://adr.github.io/)
- [Pi Agent Skills](https://github.com/dengwenyu/pi-agent-skills)

## 作者

Created for Pi Agent System

---

**状态**: ✅ 生产就绪