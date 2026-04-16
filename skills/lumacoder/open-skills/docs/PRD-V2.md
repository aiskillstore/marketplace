# open-skills 项目计划书 (PRD V2)

> 一个面向多 IDE/AI 编辑器的 Skill 分发与同步引擎
> 本身即是一个可安装的 skill，提供分类浏览、空格多选、批量安装的全流程 CLI 引导
> **V2 核心升级：引入 IDE Engine 设计思想，从"安装工具"进化为"跨编辑器 Skill 同步引擎"**

---

## 1. 项目定位

**仓库名称:** `open-skills`  
**发布路径:** `lumacoder/open-skills` (GitHub，通过 skills.sh / npx skills 分发)

**核心定位:**
- `open-skills` **本身就是一个 skill**
- 开发者通过 `npx skills add lumacoder/open-skills` 安装后，获得一个 CLI 工具
- 运行该工具，通过交互式引导，按分类浏览、空格键多选、一键批量安装/同步其他 skills 到本地
- 本仓库**不托管第三方 skill 源码**，只维护分类目录、元数据清单和安装引导逻辑
- **V2 新增**：同一份 skill 源，根据目标 IDE/AI 编辑器自动进行内容转换与格式适配

**一句话描述:**
> "AI Agent 时代的跨编辑器 Skill 分发引擎 —— 装一个 skill，获得整个工具箱，无论用 Claude、Cursor 还是 Windsurf。"

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

### Step 2: 选择目标编辑器（V2 新增）

```
? 选择目标编辑器/Agent（↑/↓ 移动，Space 多选，Enter 确认）:
  ○ Claude Code      → ~/.claude/skills/
  ○ Hermes           → ~/.hermes/skills/
  ○ Cursor           → .cursorrules
  ○ Windsurf         → .windsurfrules
  ○ Cline            → .clinerules
  ○ GitHub Copilot   → .github/skills/
```

> 用户可同时选择多个目标编辑器，引擎会为每个编辑器生成适配后的内容。

### Step 3: 选择安装范围

```
? 选择安装范围:
  > 全局安装 (Global)  → ~/.claude/skills/ 等
    本地安装 (Local)   → 当前项目 .claude/skills/ 等
```

> 仅对目录输出模式的编辑器（Claude、Hermes 等）生效。单文件模式编辑器自动输出到工作区根目录。

### Step 4: 选择分类（一级菜单）

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

### Step 5: 选择具体 Skills（二级菜单，空格多选）

```
? 前端开发 — 选择要安装的 skills（Space 多选，Enter 确认）:
  ○ react-best-practices          — React & Next.js 最佳实践 (Vercel)
  ○ typescript-patterns           — TypeScript 设计模式与类型技巧
  ○ tailwind-mastery              — Tailwind CSS 高级用法
  ○ frontend-performance          — 前端性能优化指南
  ○ accessibility-a11y            — 无障碍开发规范
  ○ css-architecture              — 大规模 CSS 架构设计
```

### Step 6: 确认并安装/同步

```
? 即将安装/同步以下 3 个 skills:
  目标编辑器: Claude Code, Cursor
  安装范围: Global
  ✓ react-best-practices
  ✓ typescript-patterns
  ✓ frontend-performance
  > 确认执行
    返回重选
    取消
```

### Step 7: 自动下载、转换与输出

CLI 自动执行：
1. 解析选中 skill 的元数据
2. 根据目标编辑器类型，实例化对应适配器
3. 根据安装范围（全局/本地）确定目标目录/文件路径
4. 按优先级下载：
   - 优先 `source`（git clone / curl）
   - fallback `bundle`（本地副本复制）
5. **V2 新增**：通过 `Skill Transformer` 对内容进行编辑器适配转换
6. **V2 新增**：单文件模式下执行部分更新（保留用户手动添加的内容）
7. **V2 新增**：目录模式下执行旧文件清理与镜像同步
8. 校验输出结果（`SKILL.md` 存在性 / 单文件标记完整性）
9. 输出安装结果报告

---

## 3. 核心概念

### 3.1 open-skills 的双重身份

| 身份 | 说明 |
|------|------|
| **作为 Skill** | 符合 skill 规范，可被 `npx skills add` 安装，包含 `SKILL.md` |
| **作为 CLI 工具** | 安装后暴露 `open-skills` 命令，提供交互式 skill 分发能力 |
| **作为同步引擎** | V2 新增：支持增量同步、多编辑器输出、内容转换 |

### 3.2 Skill 来源的两种形式

| 形式 | 说明 | 下载行为 |
|------|------|----------|
| **source** | 远程仓库引用（git url、分支、子路径） | 运行时 `git clone` 或稀疏检出 |
| **bundle** | 打包在 `open-skills` 仓库内的 `bundles/` 目录 | 运行时直接 `cp` 到目标目录 |

### 3.3 编辑器适配器预设（V2 新增）

通过一张**预设配置表**定义所有支持的 IDE/AI 编辑器：

| 字段 | 说明 |
|------|------|
| `id` | 适配器唯一标识（如 `claude-code`, `cursor`, `hermes`） |
| `name` | 显示名称 |
| `filePath` | 目标输出路径（相对于工作区根目录或用户主目录） |
| `type` | 单文件（`file`）或目录（`directory`） |
| `defaultEnabled` | 是否默认在菜单中显示 |
| `isSkillType` | 输出的是 skill 目录还是规则文件 |

运行时根据用户选择，从配置表中动态实例化适配器。新增一个 IDE 支持，只需要在配置表中加一行。

### 3.4 双模态输出（V2 新增）

#### 单文件模式
适用于 `.cursorrules`、`.clinerules`、`.windsurfrules` 等单文件配置。所有选中的 skills 合并到一个 Markdown 文件中，通过标记系统实现部分更新。

#### 目录模式
适用于 `.claude/skills/`、`.hermes/skills/` 等需要保持目录结构的场景。支持：
- **保持目录结构**：按 skill 源内部的相对路径完整输出
- **平铺结构**：所有文件直接放在输出目录下

目录模式还会自动生成 `index.md` 索引文件（可选）。

### 3.5 安装范围

| 范围 | 目标目录示例 |
|------|-------------|
| **Global** | `~/.claude/skills/`、`~/.hermes/skills/openclaw-imports/` |
| **Local** | `./.claude/skills/`、`./.hermes/skills/` |

> 注：先选择目标编辑器，再选择安装范围，最后选择分类和 skills。范围仅影响目录输出模式的编辑器。

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
│   │   ├── install.ts          # 核心：分类引导 + 空格多选 + 安装
│   │   ├── list.ts             # 列出所有可用 skills
│   │   ├── search.ts           # 搜索 skills
│   │   ├── sync.ts             # 将远程 source 同步到本地 bundle
│   │   ├── validate.ts         # 校验 registry 完整性
│   │   └── update.ts           # V2 新增：检测已安装 skills 并提示更新
│   ├── ui/
│   │   ├── editor-select.ts    # V2 新增：目标编辑器多选
│   │   ├── scope-select.ts     # 安装范围选择（全局/本地）
│   │   ├── category-select.ts  # 一级菜单：分类选择
│   │   ├── skill-select.ts     # 二级菜单：空格多选 skill
│   │   └── confirm-panel.ts    # 安装确认面板
│   ├── core/
│   │   ├── registry.ts         # 加载解析 registry/
│   │   ├── downloader.ts       # git clone / bundle copy
│   │   ├── resolver.ts         # 根据 scope + editor 解析目标路径
│   │   ├── validator.ts        # 校验 skill 结构
│   │   ├── engine.ts           # V2 新增：IDE Engine 核心调度器
│   │   ├── adapters/           # V2 新增：编辑器适配器集合
│   │   │   ├── base-adapter.ts
│   │   │   ├── claude-adapter.ts
│   │   │   ├── cursor-adapter.ts
│   │   │   ├── hermes-adapter.ts
│   │   │   └── windsurf-adapter.ts
│   │   ├── presets/            # V2 新增：编辑器预设配置表
│   │   │   └── editors.json
│   │   ├── transformer.ts      # V2 新增：Skill 内容转换引擎
│   │   ├── marker-system.ts    # V2 新增：单文件标记系统解析与写入
│   │   └── cleaner.ts          # V2 新增：目录模式旧文件清理
│   └── types/
│       └── index.ts
├── registry/                   # skill 元数据清单（按分类组织）
│   ├── frontend/
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
# V2 新增：内容转换提示
transform:
  cursor:
    remove_frontmatter: [allowed-tools]
    map_tools:
      terminal: execute_command
  windsurf:
    inject_header: "# Windsurf Rules\n\n"
```

### 关键字段

- `category`: 决定该 skill 出现在哪个分类菜单下
- `source.type`: `git` | `curl` | `local`
- `source.path`: 仓库内子目录（支持大仓库中的单 skill 提取）
- `bundle.path`: 本地副本路径，作为 fallback 或直接复制
- `transform`: V2 新增：针对特定编辑器的转换规则

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

# 快捷：直接指定目标编辑器
open-skills --editor claude-code,cursor

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

# V2 新增：更新已安装的 skills
open-skills update

# V2 新增：导出当前 stack
open-skills export my-stack.yaml

# V2 新增：导入 stack 一键安装
open-skills import my-stack.yaml
```

### 6.3 核心交互状态机

```
[启动]
  → [选择 Editors: Claude/Cursor/Hermes/...]
    → [选择 Scope: Global / Local]
      → [选择 Category: 前端/后端/运维/...]
        → [选择 Skills: 空格多选]
          → [确认面板]
            → [下载 → 转换 → 输出]
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

## 8. IDE Engine 核心设计（V2 新增）

### 8.1 统一适配器抽象

将所有目标 IDE/AI 工具抽象为统一的 `BaseAdapter` 接口：

```typescript
abstract class BaseAdapter {
  abstract getOutputType(): 'file' | 'directory';
  abstract getTargetPath(scope: 'global' | 'local'): string;
  abstract generateHeaderContent(skills: SkillMeta[]): string;
  abstract transformSkillContent(content: string, skill: SkillMeta): string;
  abstract shouldGenerateIndex(): boolean;
  abstract shouldCopySkillDirectory(): boolean;
}
```

引擎通过统一的适配器接口调度所有 IDE，新增 IDE 支持时不需要改动核心生成逻辑。

### 8.2 模板方法流水线

基类定义固定的生成流水线：

```
加载选中 skills → 下载/读取内容 → 内容转换 → 合并去重 → 排序 → 生成输出
```

子类通过重写钩子方法定制行为，核心逻辑保持稳定。

### 8.3 单文件标记系统

单文件模式（`.cursorrules`、`.windsurfrules` 等）使用 HTML 注释标记实现结构化：

```markdown
<!-- OPEN-SKILLS:BEGIN-FILE editor="cursor" version="1.0.0" -->

<!-- OPEN-SKILLS:BEGIN-SOURCE source="react-best-practices" count="1" -->
<!-- OPEN-SKILLS:BEGIN-RULE source="react-best-practices" id="component-naming" priority="high" -->
...规则内容...
<!-- OPEN-SKILLS:END-RULE -->
<!-- OPEN-SKILLS:END-SOURCE source="react-best-practices" -->

<!-- OPEN-SKILLS:END-FILE -->
```

标记层级：
- **全局包裹标记**：识别文件是否被引擎管理
- **规则源标记**：按 skill 源分组
- **单条规则标记**：标记单条规则的边界和元数据

### 8.4 部分更新机制

基于标记系统，引擎支持增量更新：
1. **解析**现有文件，按标记拆分
2. **识别**需要更新的 skill 区块
3. **替换**目标区块为新内容
4. **保留**其他 skill 区块和用户手动添加的内容
5. **重新组装**文件

### 8.5 用户规则保护

自动识别并保护工作区中用户自定义的内容：
- 单文件模式下，用户手动添加在标记外的内容始终保留
- 目录模式下，用户本地已有的同名文件以本地版本为准（可配置覆盖策略）

### 8.6 内容转换引擎（Skill Transformer）

同一份 `SKILL.md` 源文件，不同 IDE 可能有不同的格式要求。转换维度包括：
- **Frontmatter 重映射**：字段名转换
- **Frontmatter 删除**：移除目标 IDE 不支持的字段
- **工具名映射**：将通用工具名转换为目标编辑器的专有工具名
- **Bash Preamble 剥离**：移除某些编辑器不兼容的 bash 脚本前言
- **Header 注入**：为目标 IDE 添加特定的文件头注释
- **Gstack 专有内容清理**：移除只在特定生态生效的扩展标记

转换失败时**静默降级**，返回原始内容。

### 8.7 目录模式清理策略

每次生成后执行递归清理：
- 扫描输出目录
- 对比"期望文件集合"
- 删除不在期望集合中的文件和空目录
- 对 `SKILL` 目录采用**源目录镜像同步**

### 8.8 冲突解决与排序策略

- `priority`：按优先级排序（high > medium > low）
- `id`：按规则标识符字母序排序
- `none`：保持原始顺序
- 去重时按排序后的顺序决定保留项

---

## 9. 安装目录解析逻辑

### 9.1 编辑器 + Scope 联合推断

用户先选择编辑器，再选择 Scope，CLI 根据编辑器预设表中的 `filePath` 字段推断目标路径：

| 编辑器 | 类型 | Global 路径 | Local 路径 |
|--------|------|------------|-----------|
| claude-code | directory | `~/.claude/skills/` | `./.claude/skills/` |
| hermes | directory | `~/.hermes/skills/` | `./.hermes/skills/` |
| cursor | file | `~/.cursorrules` | `./.cursorrules` |
| windsurf | file | `~/.windsurfrules` | `./.windsurfrules` |
| cline | file | `~/.clinerules` | `./.clinerules` |
| github-copilot | directory | `~/.github/skills/` | `./.github/skills/` |

### 9.2 目录不存在时的处理

- 检测目标目录是否存在
- 不存在时提示用户创建
- 单文件模式下，若目标文件已存在但没有引擎标记，拒绝覆盖并提示备份

---

## 10. SKILL.md 设计（open-skills 自身）

```markdown
---
name: open-skills
description: 一个交互式 CLI 工具，帮助开发者按分类浏览、空格多选、一键批量安装/同步 AI Agent skills 到多个编辑器。
version: 2.0.0
author: lumacoder
license: MIT
---

# open-skills

安装后运行 `open-skills` 启动交互式引导：

1. 选择目标编辑器（可多选）
2. 选择安装范围（全局 / 本地）
3. 选择分类（前端 / 后端 / 运维 / 产品 / UI / ...）
4. 空格键多选具体 skills
5. 确认后自动下载、转换、输出

## 安装

```bash
npx skills add lumacoder/open-skills -g -y
```

## 使用

```bash
open-skills
```

## 支持的目标编辑器

- Claude Code
- Hermes
- Cursor
- Windsurf
- Cline
- GitHub Copilot
```

---

## 11. 开发阶段规划

### Phase 1: 骨架与核心交互 (3-4 天)
- [ ] 初始化 TS + tsup + ink 项目骨架
- [ ] 编写 `SKILL.md` 和基础 `README.md`
- [ ] 实现 `editor-select`（目标编辑器多选）
- [ ] 实现 `scope-select`（全局/本地选择）
- [ ] 实现 `category-select`（一级分类菜单）
- [ ] 实现 `skill-select`（二级空格多选菜单）
- [ ] 实现 `confirm-panel`（安装确认面板）
- [ ] 实现 registry YAML 加载与解析

### Phase 2: IDE Engine 核心架构 (4-5 天)
- [ ] 设计并实现 `BaseAdapter` 抽象类
- [ ] 编写 `editors.json` 预设配置表
- [ ] 实现 `ClaudeAdapter` 和 `HermesAdapter`（目录模式）
- [ ] 实现 `CursorAdapter` 和 `WindsurfAdapter`（单文件模式）
- [ ] 实现 `Skill Transformer` 基础转换逻辑
- [ ] 实现单文件标记系统（解析 + 写入）
- [ ] 实现部分更新机制
- [ ] 实现目录模式旧文件清理

### Phase 3: 下载与安装逻辑 (2-3 天)
- [ ] 实现 `downloader.ts`：git clone / sparse checkout
- [ ] 实现 `bundle` 复制逻辑
- [ ] 实现 `resolver.ts`：editor + scope → 目标路径映射
- [ ] 安装后校验 `SKILL.md` 存在性及 `name` 字段匹配
- [ ] 单文件模式下校验标记完整性
- [ ] 错误处理、重试、友好提示
- [ ] 安装结果报告面板

### Phase 4: 生态填充与发布 (3-4 天)
- [ ] 收集并录入首批 skills 元数据（每分类 3-5 个）
- [ ] 实现 `list` / `search` / `validate` / `sync` / `update` / `export` / `import` 命令
- [ ] GitHub Actions：registry 校验、自动测试
- [ ] 发布到 npm
- [ ] 在 skills.sh 注册并验证 `npx skills add lumacoder/open-skills` 可用

---

## 12. 关键设计决策

### 12.1 为什么先选 Editor，再选 Scope？
- 不同编辑器的输出形态（文件/目录）不同，决定了后续是否需要选择 scope
- 用户通常明确知道自己使用哪个编辑器，以此为起点最自然

### 12.2 为什么用 ink 而不是原生 readline？
- "空格多选"是核心卖点，ink 生态有成熟的 `ink-multi-select`
- React 组件化开发，UI 状态管理更清晰
- 需要支持编辑器多选、skill 多选等复杂交互

### 12.3 为什么引入 IDE Engine 的适配器模式？
- 避免为每个 IDE 写独立的安装逻辑
- 新增 IDE 支持时，只需在预设表中加一行、实现一个轻量适配器
- 核心下载、转换、输出流程完全复用

### 12.4 单文件标记系统是否过度设计？
- 对于 `.cursorrules` 等文件，用户往往会手动追加自己的规则
- 没有标记系统，每次同步都会覆盖用户手动添加的内容
- 标记系统让配置文件具备了"数据库表"一样的可寻址、可替换能力

### 12.5 bundle 是否必须？
- **不必须**，但强烈建议为核心 skills 提供 bundle
- 保证网络不稳定或远程仓库失效时，用户仍能安装

---

## 13. 风险与应对

| 风险 | 应对 |
|------|------|
| `npx skills add` 安装失败 | 提供手动 git clone + 复制到 skills 目录的 fallback 文档 |
| 远程 source 失效 | bundle 兜底；CI 定期检测链接有效性 |
| 用户目标目录结构未知 | 提供 `--target-dir` 强制覆盖；安装前检测并提示创建 |
| skill 名称/路径冲突 | 安装前检测已存在，提示覆盖/跳过/重命名 |
| ink 在部分终端渲染异常 | 提供 `--simple` 模式，降级为 `enquirer` 纯文本交互 |
| 单文件标记解析失败 | 降级为全量重写，并提示用户备份 |
| 内容转换导致格式异常 | 静默降级为原始内容，不中断流程 |

---

## 14. 后续扩展方向

- [ ] `open-skills update`：检测已安装 skills 并提示更新
- [ ] `open-skills export my-stack.yaml`：导出当前已选 skills 集合
- [ ] `open-skills import my-stack.yaml`：按集合一键安装
- [ ] 支持自定义 registry 源（适合企业内部私有 skills）
- [ ] 与 `skills.sh` API 打通，实时拉取最新 skills 列表
- [ ] 提供 `--simple` 纯文本降级模式
- [ ] 支持 WebDAV / S3 等私有 bundle 存储后端
- [ ] 提供 VSCode 扩展，图形化浏览和安装 skills

---

## 15. 命名确认

- **仓库名:** `open-skills`
- **npm 包名:** `open-skills` (需提前确认可用性，备选 `@lumacoder/open-skills`)
- **CLI 命令:** `open-skills`
- **skills.sh 标识:** `lumacoder/open-skills`
