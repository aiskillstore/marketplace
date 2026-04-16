# open-skills V3 PRD

## 1. 目标

将 `open-skills` 的 Registry 管理从分散 YAML 升级为单一 JSON 数据源，并为开发者提供本地 Web 管理面板，实现可视化、列表化的 Skill 与分类管理。

## 2. 核心变化

| 维度 | V2 | V3 |
|--------|-----|-----|
| Registry 格式 | 平铺 YAML + `_index.yaml` | 单一 JSON (`registry/skills.json`) |
| 开发者工具 | CLI `--dev` 面板 | 本地 Web 服务 (`--dev` 启动) |
| 远程 Skill 注册 | 手动填写完整元数据 | 只需名称/地址，一键查询填充 |
| 本地 Bundle 识别 | 显式配置 `bundle.path` | 自动识别 `bundles/` 路径 |
| 分类管理 | 编辑 `_index.yaml` | Web 列表增删改，自动持久化到 JSON |

## 3. 数据模型

### 3.1 `registry/skills.json`

唯一数据源，统一管理所有分类与 Skill 元数据。

```json
{
  "version": "3.0.0",
  "updatedAt": "2026-04-15T12:00:00.000Z",
  "categories": [
    {
      "id": "frontend",
      "displayName": "\u524d\u7aef\u5f00\u53d1",
      "order": 1
    }
  ],
  "skills": [
    {
      "name": "react-patterns",
      "displayName": "React Patterns",
      "description": "React \u7ec4\u4ef6\u8bbe\u8ba1\u4e0e\u6027\u80fd\u4f18\u5316\u6307\u5357",
      "category": "frontend",
      "tags": ["react", "patterns"],
      "origin": {
        "type": "clawhub",
        "ref": "lumacoder/react-patterns"
      },
      "author": "lumacoder",
      "version": "2.0.0",
      "license": "MIT"
    },
    {
      "name": "docker-basics",
      "displayName": "Docker Basics",
      "description": "Docker \u5feb\u901f\u5165\u95e8",
      "category": "devops",
      "tags": ["docker"],
      "origin": {
        "type": "bundle",
        "path": "bundles/devops/docker-basics"
      },
      "author": "open-skills",
      "version": "1.0.0",
      "license": "MIT"
    }
  ]
}
```

### 3.2 字段规范

- `origin.type`: 数据来源类型
  - `clawhub` — ClawHub Skill Store
  - `skillstore` — 其他 Skill Store
  - `github` — GitHub 仓库
  - `git` — 普\u901a Git \u4ed3\u5e93
  - `bundle` — 本\u5730 bundles/ \u76ee\u5f55
- `origin.ref`: 远\u7a0b\u5e93\u7684\u7b80\u5199\u5f15\u7528（\u5982 `owner/repo` \u6216 `repo-name`\uff09
- `origin.path`: 仅对 `bundle` / `git` 有\u6548，\u8868\u793a\u672c\u5730\u8def\u5f84\u6216 git \u4ed3\u5e93\u5185\u5b50\u8def\u5f84
- `origin.url`: 对 `git` \u7c7b\u578b\u53ef\u9009\uff0c\u5b8c\u6574 git URL

## 4. 开发者 Web 服务

### 4.1 启动方式

```bash
open-skills --dev
# 输出: Developer server running at http://localhost:3890
```

服务自动打开浏览器（可配置关闭）。

### 4.2 技\u672f\u6808

- **后端**: Node.js 内\u7f6e `http` 模\u5757 + 轻\u91cf\u8def\u7531 (`src/dev-server/`)
- **前端**: 静态 HTML/CSS/JS（Vanilla），打\u5305\u8fdb `dist/dev-web/`
- **数据\u4ea4\u4e92**: RESTful API + JSON

### 4.3 Web 界面结构

#### 左侧：分类管理

- 分类列表（可拖拽\u6392\u5e8f）
- 每\u884c\u663e\u793a：名\u79f0 + Skill \u6570\u91cf
- 操\u4f5c：新\u589e / 编\u8f91 / 删\u9664
- 删\u9664分\u7c7b\u65f6\uff0c\u5173\u8054的 Skill 自动\u8f6c\u5165 "\u672a\u5206\u7c7b" \u6682\u5b58\u533a

#### 右侧：Skill 列表

- 按当前选中分类过滤
- 表格展示：名称、显示名、数据源类型、操作
- 操作：新增 / 编辑 / 删除 / 复\u5236

#### 顶部工具栏

- 保存 JSON（`Ctrl+S` 快捷键）
- 校验 Registry
- 扫描未\u6ce8\u518c Bundle
- 一\u952e\u540c\u6b65\u8fdc\u7a0b Skills（将\u6240\u6709 `git` / `github` / `clawhub` 抉\u53d6\u6700\u65b0 SKILL.md）

### 4.4 远程 Skill 一键填充

在新增 Skill 弹窗中：

1. 用户选择来源类型（如 ClawHub）
2. 输入名称或地址（如 `lumacoder/react-patterns`）
3. 点击 **查询填充**
4. 系统通过查询服务获取元数据，自动填写表单

#### 查询服务接口规范

```typescript
// src/core/resolvers/remote-resolver.ts
interface RemoteResolver {
  provider: string;
  resolve(ref: string): Promise<Partial<SkillMeta>>;
}
```

- **GitHub Resolver**
  - 输入: `owner/repo`
  - 请求: `GET https://api.github.com/repos/{owner}/{repo}`
  - 返回: `name`, `description`, `author` (owner), `license`, `version` (latest tag 或 default branch)
  - 后续可扩展从 `raw.githubusercontent.com` 读取 `SKILL.md` 前置 matter 补充字段

- **ClawHub Resolver**
  - 输入: `owner/repo` 或 `repo-name`
  - 请求: `GET https://api.clawhub.dev/v1/skills/{ref}/meta` (假设接口)
  - 返回: 标\u51c6 SkillMeta JSON

- **SkillStore Resolver**
  - 类似 ClawHub，通过各自平台 API 解析

## 5. 安装引擎适\u914d

### 5.1 数据源分\u8fa8

`Engine` 在安装时根据 `origin.type` 自动分\u652f：

| `origin.type` | 处理逻辑 |
|---------------|----------|
| `bundle` | 从 `origin.path` 直接读取 `SKILL.md` |
| `git` | 克隆远程仓库（支持 sparse-checkout 子路径） |
| `github` | 克隆或通过 GitHub Raw 读取 |
| `clawhub` / `skillstore` | 调用平台 API 获取下载链接，然后下载 |

### 5.2 自动识别 Bundle

当 `origin.type === 'bundle'` 时，系统不需额外配置下载逻辑，直接将 `origin.path` 视为本地 skill 目录，复制或直读其中的 `SKILL.md`。

## 6. 迁移路径

1. 保留 V2 的 `registry/` YAML 作为只读备份
2. 新增 `src/core/migrate-v2-to-v3.ts` 脚本
3. 运行命令自动迁移：
   ```bash
   open-skills migrate --to v3
   ```
4. 迁移后生成 `registry/skills.json`，并将 `origin.type=bundle` 的 skill 自动识别本地路径

## 7. 项目结构变\u66f4

```
open-skills/
├── src/
│   ├── cli.ts                    # 增加 --dev 启动 web 服务
│   ├── commands/
│   ├── core/
│   │   ├── registry-v3.ts        # JSON Registry 读写
│   │   ├── engine.ts             # 适配新数据模型
│   │   └── resolvers/
│   │       ├── remote-resolver.ts
│   │       ├── github-resolver.ts
│   │       ├── clawhub-resolver.ts
│   │       └── skillstore-resolver.ts
│   └── dev-server/
│       ├── server.ts             # 后端服务
│       ├── api.ts                # API 路由
│       └── web/
│           ├── index.html
│           ├── app.js
│           └── style.css
├── registry/
│   ├── skills.json               # V3 主数据源
│   └── _v2_backup/               # YAML 备份
└── ...
```

## 8. 任务清单

- [ ] 设计 `registry/skills.json` Schema
- [ ] 实现 `registry-v3.ts` JSON 读写封装
- [ ] 实现远程 Resolver 接口与 GitHub/ClawHub 实现
- [ ] 搭建 `dev-server` 后端 + 静态资源打包
- [ ] 实现 Web 端分类管理页面
- [ ] 实现 Web 端 Skill 列表与编辑页面
- [ ] 实现一键查询填充功能
- [ ] Engine 适配 V3 数据模型
- [ ] 实现 V2→V3 迁移脚本
- [ ] 文档更新
