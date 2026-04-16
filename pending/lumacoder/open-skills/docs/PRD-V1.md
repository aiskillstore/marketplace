# open-skills 项目计划书 (PRD V1)

> 一个面向开发者的 AI Agent Skill 聚合与一键安装工具
> 本身即是一个可安装的 skill，提供分类浏览、空格多选、批量安装的全流程 CLI 引导

---

## 1. 项目定位

**仓库名称:** `open-skills`
**发布路径:** `lumacoder/open-skills` (GitHub，通过 skills.sh / npx skills 分发)

**核心定位:**
- `open-skills` **本身就是一个 skill**
- 开发者通过 `npx skills add lumacoder/open-skills` 安装后，获得一个 CLI 工具
- 运行该工具，通过交互式引导，按分类浏览、空格键多选、一键批量安装其他 skills 到本地
- 本仓库**不托管第三方 skill 源码**，只维护分类目录、元数据清单和安装引导逻辑

**一句话描述:**
> "AI Agent 时代的 skill 应用商店 CLI —— 装一个 skill，获得整个工具箱。"

---

## 2. 用户使用流程（核心体验）

### Step 0: 安装 open-skills

```bash
npx skills add lumacoder/open-skills -g -y
```

### Step 1: 启动 CLI 引导

```bash
open-skills
# 或
npx open-skills
```

### Step 2: 选择安装范围

```
? 选择安装范围:
  > 全局安装 (Global)  → ~/.claude/skills/ 等
    本地安装 (Local)   → 当前项目 .claude/skills/ 等
```

### Step 3: 选择分类（一级菜单）

```
? 选择分类（↑/↓ 移动，Enter 确认）:
  > 前端开发
    后端开发
    运维/DevOps
    产品设计
    UI/UX
    测试
    数据科学
    全栈通用
```

### Step 4: 选择具体 Skills（二级菜单，空格多选）

```
? 前端开发 — 选择要安装的 skills（Space 多选，Enter 确认）:
  ○ react-best-practices          — React & Next.js 最佳实践 (Vercel)
  ○ typescript-patterns           — TypeScript 设计模式与类型技巧
  ○ tailwind-mastery              — Tailwind CSS 高级用法
  ○ frontend-performance          — 前端性能优化指南
  ○ accessibility-a11y            — 无障碍开发规范
  ○ css-architecture              — 大规模 CSS 架构设计
```

### Step 5: 确认并安装

```
? 即将安装以下 3 个 skills 到 ~/.claude/skills/:
  ✓ react-best-practices
  ✓ typescript-patterns
  ✓ frontend-performance
  > 确认安装
    返回重选
    取消
```

### Step 6: 自动下载与安装

CLI 自动执行：
1. 解析选中 skill 的元数据
2. 根据安装范围（全局/本地）确定目标目录
3. 按优先级下载：
   - 优先 `source`（git clone / curl）
   - fallback `bundle`（本地副本复制）
4. 校验 `SKILL.md` 存在性及 `name` 字段匹配
5. 输出安装结果报告

---

## 3. 核心概念

### 3.1 open-skills 的双重身份

| 身份 | 说明 |
|------|------|
| **作为 Skill** | 符合 skill 规范，可被 `npx skills add` 安装，包含 `SKILL.md` |
| **作为 CLI 工具** | 安装后暴露 `open-skills` 命令，提供交互式 skill 分发能力 |

### 3.2 Skill 来源的两种形式

| 形式 | 说明 | 下载行为 |
|------|------|----------|
| **source** | 远程仓库引用（git url、分支、子路径） | 运行时 `git clone` 或稀疏检出 |
| **bundle** | 打包在 `open-skills` 仓库内的 `bundles/` 目录 | 运行时直接 `cp` 到目标目录 |

### 3.3 安装范围

| 范围 | 目标目录示例 |
|------|-------------|
| **Global** | `~/.claude/skills/`、`~/.hermes/skills/openclaw-imports/` |
| **Local** | `./.claude/skills/`、`./.hermes/skills/` |

> 注：先选择安装范围，再选择分类和 skills。范围决定后续所有选中 skills 的安装目录。

---

## 4. 项目目录结构

```
open-skills/
├── SKILL.md                    # 本 skill 的入口说明（被 agent 识别）
├── README.md
├── package.json                # CLI 入口、bin 字段、依赖
├── tsconfig.json
├── src/
│   ├── cli.ts                  # CLI 入口：open-skills 命令
│   ├── commands/
│   │   └── install.ts          # 核心：分类引导 + 空格多选 + 安装
│   ├── ui/
│   │   ├── category-select.ts  # 一级菜单：分类选择
│   │   ├── skill-select.ts     # 二级菜单：空格多选 skill
│   │   ├── scope-select.ts     # 安装范围选择（全局/本地）
│   │   └── confirm-panel.ts    # 安装确认面板
│   ├── core/
│   │   ├── registry.ts         # 加载解析 registry/
│   │   ├── downloader.ts       # git clone / bundle copy
│   │   ├── resolver.ts         # 根据 scope 解析目标目录
│   │   └── validator.ts        # 校验 skill 结构
│   └── types/
│       └── index.ts
├── registry/                   # skill 元数据清单（按分类组织）
│   ├── frontend/
│   │   ├── react-best-practices.yaml
│   │   ├── typescript-patterns.yaml
│   │   └── tailwind-mastery.yaml
│   ├── backend/
│   ├── devops/
│   ├── product/
│   ├── ui-ux/
│   ├── testing/
│   ├── data-science/
│   └── fullstack/
├── bundles/                    # 本地副本（可选）
│   └── frontend/
│       └── react-best-practices/
│           └── SKILL.md
└── scripts/
    └── validate-registry.ts    # CI 校验脚本
```

---

## 5. Registry 元数据格式

每个 skill 一个 YAML，按分类存放：

```yaml
# registry/frontend/react-best-practices.yaml
name: react-best-practices
display_name: "React Best Practices"
description: "React & Next.js 性能优化与工程实践指南"
category: frontend
tags: [react, nextjs, frontend, performance]
source:
  type: git
  url: https://github.com/vercel-labs/agent-skills.git
  path: skills/react-best-practices
  ref: main
bundle:
  path: bundles/frontend/react-best-practices/
author: Vercel Labs
version: "2.1.0"
license: MIT
```

### 关键字段

- `category`: 决定该 skill 出现在哪个分类菜单下
- `source.type`: `git` | `curl` | `local`
- `source.path`: 仓库内子目录（支持大仓库中的单 skill 提取）
- `bundle.path`: 本地副本路径，作为 fallback 或直接复制

---

## 6. CLI 命令设计

### 6.1 安装 open-skills

```bash
npx skills add lumacoder/open-skills -g -y
```

### 6.2 命令列表

```bash
# 启动完整交互引导（默认命令）
open-skills

# 快捷：直接指定分类
open-skills --category frontend

# 快捷：直接指定安装范围
open-skills --scope global

# 列出所有可用 skills
open-skills list

# 搜索 skills
open-skills search "performance"

# 将远程 source 同步到本地 bundle（维护者用）
open-skills sync --category frontend --name react-best-practices

# 校验 registry 完整性
open-skills validate
```

### 6.3 核心交互状态机

```
[启动]
  → [选择 Scope: Global / Local]
    → [选择 Category: 前端/后端/运维/...]
      → [选择 Skills: 空格多选]
        → [确认面板]
          → [下载安装]
            → [结果报告]
```

---
## 7. 技术栈

| 层级 | 选型 | 理由 |
|------|------|------|
| 语言 | TypeScript / Node.js | 与 skills 生态一致，安装门槛低 |
| TUI | `ink` + `ink-select-input` + `ink-multi-select` | React 式 CLI UI，空格多选体验最佳 |
| 配置 | `yaml` + `zod` | YAML 人工友好，Zod 运行时强校验 |
| 下载 | `simple-git` + `fs-extra` | git 操作可靠，文件复制方便 |
| 构建 | `tsup` | 零配置快速打包 CLI |
| 测试 | `vitest` | 轻量快速 |

---

## 8. 安装目录解析逻辑

### 8.1 Scope 选择后的目标目录推断

用户先选择 `Global` 或 `Local`，然后 CLI 需要为每个 skill 推断目标目录。

**推断策略：**
- 读取 skill 的 `agent` 字段（若元数据中有）
- 若 skill 未指定 agent，则尝试从 tags 或 name 推断
- 最终映射到对应目录：

| Agent/Eco | Global 目录 | Local 目录 |
|-----------|------------|-----------|
| claude-code | `~/.claude/skills/` | `./.claude/skills/` |
| hermes | `~/.hermes/skills/` 或 `~/.hermes/skills/openclaw-imports/` | `./.hermes/skills/` |
| openclaw | `~/.hermes/skills/openclaw-imports/` | `./.hermes/skills/openclaw-imports/` |
| codex | `~/.codex/skills/` (或自定义) | `./.codex/skills/` |
| opencode | `~/.opencode/skills/` | `./.opencode/skills/` |

### 8.2 目录不存在时的处理

- 检测目标目录是否存在
- 不存在时提示用户：
  ```
  目录 ~/.claude/skills/ 不存在，是否创建？
  > 是
    否（跳过此 skill）
  ```

---

## 9. SKILL.md 设计（open-skills 自身）

作为 skill，`SKILL.md` 需要被 agent 识别。内容示例：

```markdown
---
name: open-skills
description: 一个交互式 CLI 工具，帮助开发者按分类浏览、空格多选、一键批量安装 AI Agent skills。
version: 1.0.0
author: lumacoder
license: MIT
---

# open-skills

安装后运行 `open-skills` 启动交互式引导：

1. 选择安装范围（全局 / 本地）
2. 选择分类（前端 / 后端 / 运维 / 产品 / UI / ...）
3. 空格键多选具体 skills
4. 确认后自动下载安装

## 安装

```bash
npx skills add lumacoder/open-skills -g -y
```

## 使用

```bash
open-skills
```

## 支持的分类

- 前端开发
- 后端开发
- 运维 / DevOps
- 产品设计
- UI / UX
- 测试
- 数据科学
- 全栈通用
```

---

## 10. 开发阶段规划

### Phase 1: 骨架与核心交互 (2-3 天)
- [ ] 初始化 TS + tsup + ink 项目骨架
- [ ] 编写 `SKILL.md` 和基础 `README.md`
- [ ] 实现 `scope-select`（全局/本地选择）
- [ ] 实现 `category-select`（一级分类菜单）
- [ ] 实现 `skill-select`（二级空格多选菜单）
- [ ] 实现 `confirm-panel`（安装确认面板）
- [ ] 实现 registry YAML 加载与解析

### Phase 2: 下载与安装逻辑 (2-3 天)
- [ ] 实现 `downloader.ts`：git clone / sparse checkout
- [ ] 实现 `bundle` 复制逻辑
- [ ] 实现 `resolver.ts`：scope → 目标目录映射
- [ ] 安装后校验 `SKILL.md` 和 `name` 匹配
- [ ] 错误处理、重试、友好提示
- [ ] 安装结果报告面板

### Phase 3: 生态填充与发布 (2-3 天)
- [ ] 收集并录入首批 skills 元数据（每分类 3-5 个）
- [ ] 实现 `list` / `search` / `validate` / `sync` 命令
- [ ] GitHub Actions：registry 校验、自动测试
- [ ] 发布到 npm
- [ ] 在 skills.sh 注册并验证 `npx skills add lumacoder/open-skills` 可用

---

## 11. 关键设计决策

### 11.1 为什么先选 Scope，再选 Category？
- 用户通常先有"我要装到全局还是本地"的明确意图
- 选定 scope 后，后续所有操作的目标目录一致，减少认知负担

### 11.2 为什么用 ink 而不是原生 readline？
- "空格多选"是核心卖点，ink 生态有成熟的 `ink-multi-select`
- React 组件化开发，UI 状态管理更清晰

### 11.3 为什么 registry 按分类分目录？
- 与 CLI 的分类菜单结构一一对应
- 方便社区贡献者按分类提交 PR

### 11.4 bundle 是否必须？
- **不必须**，但强烈建议为核心 skills 提供 bundle
- 保证网络不稳定或远程仓库失效时，用户仍能安装

---

## 12. 风险与应对

| 风险 | 应对 |
|------|------|
| `npx skills add` 安装失败 | 提供手动 git clone + 复制到 skills 目录的 fallback 文档 |
| 远程 source 失效 | bundle 兜底；CI 定期检测链接有效性 |
| 用户目标目录结构未知 | 提供 `--target-dir` 强制覆盖；安装前检测并提示创建 |
| skill 名称/路径冲突 | 安装前检测已存在，提示覆盖/跳过/重命名 |
| ink 在部分终端渲染异常 | 提供 `--simple` 模式，降级为 `enquirer` 纯文本交互 |

---

## 13. 后续扩展方向

- [ ] `open-skills update`：检测已安装 skills 并提示更新
- [ ] `open-skills export my-stack.yaml`：导出当前已选 skills 集合
- [ ] `open-skills import my-stack.yaml`：按集合一键安装
- [ ] 支持自定义 registry 源（适合企业内部私有 skills）
- [ ] 与 `skills.sh` API 打通，实时拉取最新 skills 列表
- [ ] 提供 `--simple` 纯文本降级模式

---

## 14. 命名确认

- **仓库名:** `open-skills`
- **npm 包名:** `open-skills` (需提前确认可用性，备选 `@lumacoder/open-skills`)
- **CLI 命令:** `open-skills`
- **skills.sh 标识:** `lumacoder/open-skills`
