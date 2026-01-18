---
name: share-skill
description: 自动分享skill、将本地skill迁移到代码仓库、skill开源、skill版本管理、配置git远端
---

# Share Skill

将用户本地临时创建的 skill 通过符号链接的方式迁移到项目仓库，并初始化 Git 进行版本跟踪。

## 使用方法

| 命令 | 说明 |
|------|------|
| `/share-skill <skill-name>` | 迁移指定 skill 到代码仓库并初始化 git |
| `/share-skill config` | 配置 code_root 和其他设置 |
| `/share-skill <skill-name> --remote <url>` | 迁移并配置远端地址 |
| `/share-skill list` | 列出所有可迁移的本地 skill |
| `/share-skill remote <alias> <endpoint>` | 配置 Git 远端别名 |
| `/share-skill remote list` | 列出已配置的远端别名 |
| `/share-skill docs` | 为仓库生成文档网站 |
| `/share-skill docs --style <name>` | 使用指定设计风格生成文档 |
| `/share-skill docs --skill <ui-skill>` | 调用指定 UI 技能设计文档 |
| `/share-skill docs config` | 配置默认设计风格或 UI 技能 |
| `/share-skill allow` | 一次性授权本 skill 所需的权限 |
| 自然语言 | 例如："帮我把 port-allocator 开源并 push 到 github" |

## 配置文件

所有设置存储在 `~/.claude/share-skill-config.json`：

```json
{
  "code_root": "~/Codes",
  "skills_repo": "skills",
  "github_username": "guo-yu",
  "remotes": {
    "github": "git@github.com:guo-yu/skills",
    "gitlab": "git@gitlab.com:guo-yu/skills"
  },
  "default_remote": "github",
  "auto_detected": true,
  "docs": {
    "style": "botanical",
    "custom_skill": null,
    "custom_domain": null
  }
}
```

**配置字段说明：**

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `code_root` | 代码仓库根目录 | `~/Codes` |
| `skills_repo` | 技能仓库文件夹名 | `skills` |
| `github_username` | GitHub 用户名 | 自动检测 |
| `remotes` | Git 远端别名 | 自动配置 |
| `docs.custom_domain` | 文档网站自定义域名 | `null`（使用 GitHub Pages） |

**路径变量：**

本文档中使用以下变量：
- `{code_root}` → `code_root` 配置值（如 `~/Codes`）
- `{skills_repo}` → `skills_repo` 配置值（如 `skills`）
- `{skills_path}` → `{code_root}/{skills_repo}`（如 `~/Codes/skills`）
- `{username}` → `github_username` 配置值

### 首次运行自动检测

首次调用 share-skill 时，会自动检测设置：

**自动检测逻辑：**

1. **检查配置文件是否存在**
   ```bash
   if [ ! -f ~/.claude/share-skill-config.json ]; then
     # 首次运行，执行自动检测
   fi
   ```

2. **检测 code_root 目录**
   ```bash
   # 按顺序检查常见的代码目录位置
   for dir in ~/Codes ~/Code ~/Projects ~/Dev ~/Development ~/repos; do
     if [ -d "$dir" ]; then
       CODE_ROOT="$dir"
       break
     fi
   done

   # 如果都不存在，默认使用 ~/Codes
   CODE_ROOT="${CODE_ROOT:-~/Codes}"
   ```

3. **读取 Git 全局配置获取用户名**
   ```bash
   # 尝试获取用户名
   USERNAME=$(git config --global user.name)

   # 如果用户名包含空格，尝试从 GitHub 邮箱提取
   if [[ "$USERNAME" == *" "* ]]; then
     EMAIL=$(git config --global user.email)
     # 从 xxx@users.noreply.github.com 提取
     USERNAME=$(echo "$EMAIL" | grep -oP '^\d+-?\K[^@]+(?=@users\.noreply\.github\.com)')
   fi

   # 如果还是无法确定，尝试从 remote URL 提取
   if [ -z "$USERNAME" ]; then
     USERNAME=$(git config --global --get-regexp "url.*github.com" | grep -oP 'github\.com[:/]\K[^/]+' | head -1)
   fi
   ```

4. **生成默认配置**
   ```json
   {
     "code_root": "<检测到的代码目录>",
     "skills_repo": "skills",
     "github_username": "<检测到的用户名>",
     "remotes": {
       "github": "git@github.com:<检测到的用户名>/skills"
     },
     "default_remote": "github",
     "auto_detected": true,
     "docs": {
       "style": "botanical",
       "custom_skill": null,
       "custom_domain": null
     }
   }
   ```

5. **输出检测结果**
   ```
   首次运行，自动检测设置...

   检测到的设置:
     代码目录: ~/Codes
     GitHub 用户名: guo-yu

   已自动配置:
     技能路径: ~/Codes/skills
     远端: git@github.com:guo-yu/skills

   配置文件: ~/.claude/share-skill-config.json

   如需修改，请使用:
     /share-skill config
   ```

### 命令: `/share-skill config`

交互式配置 share-skill 设置：

**TUI 界面 (AskUserQuestion):**
```
配置 share-skill 设置:

代码根目录:
  当前: ~/Codes
  [ ] ~/Codes
  [ ] ~/Code
  [ ] ~/Projects
  [ ] 其他...（输入自定义路径）

文档网站自定义域名:
  当前: (无 - 使用 GitHub Pages)
  [ ] 不使用自定义域名（使用 {username}.github.io/{repo}）
  [ ] 输入自定义域名...
```

**实现:**
```bash
# 读取当前配置
CONFIG=$(cat ~/.claude/share-skill-config.json 2>/dev/null || echo '{}')

# 用户选择后更新配置
# 示例: 更新 code_root
jq --arg root "$NEW_CODE_ROOT" '.code_root = $root' <<< "$CONFIG" > ~/.claude/share-skill-config.json
```

### 无法检测时的处理

如果无法自动检测设置，提示用户手动配置：

```
无法自动检测设置

请手动配置:
  /share-skill config

或在迁移时指定:
  /share-skill <skill-name> --remote git@github.com:你的用户名/skills.git
```

## 自然语言调用

当用户通过自然语言调用时，需要智能分析：

### 1. 识别用户指代的 skill

用户可能说：
- "帮我把 xxx skill 开源" → 提取 skill 名称 `xxx`
- "分享刚才创建的 skill" → 查找最近修改的 skill
- "把这个技能迁移到仓库" → 根据当前上下文判断
- "开源 port-allocator" → 直接使用名称

### 2. 识别远端地址

**默认行为：** 使用自动检测的用户名 + 默认仓库名 `skills`

用户可能说：
- "帮我把 xxx 开源" → 使用默认: `git@github.com:<用户名>/skills/<skill-name>.git`
- "push 到 github" → 使用默认 github 配置
- "推送到 git@github.com:other-user/repo.git" → **必须明确指定完整地址**
- "开源到我的 my-tools 仓库" → **必须明确指定仓库名**

**⚠️ 重要规则：修改远端路径必须显式指定**

如果用户想使用非默认的远端路径，必须通过以下方式**明确指定**：

1. **命令行显式指定**
   ```bash
   /share-skill <skill-name> --remote git@github.com:other-user/other-repo.git
   ```

2. **自然语言中明确路径**
   ```
   ✅ "帮我把 port-allocator 推送到 git@github.com:my-org/tools.git"
   ✅ "开源到 gitlab，地址是 git@gitlab.com:team/shared-skills.git"

   ❌ "帮我推送到其他地方" (不明确，会询问具体地址)
   ❌ "换个仓库" (不明确，会询问具体地址)
   ```

**地址解析规则：**
```
"帮我把 xxx 开源"
  → 使用默认配置: git@github.com:<auto-detected-user>/skills
  → 最终地址: git@github.com:<user>/skills/<skill-name>.git

"推送到 git@github.com:other-user/repo.git"
  → 检测到完整地址，直接使用

"开源到 gitlab" (未配置 gitlab)
  → 提示: 请指定完整的 GitLab 地址
```

### 3. 自动搜索 skill 位置

skill 可能存在于以下位置，按优先级搜索：

```bash
# 1. 标准 skills 目录
~/.claude/skills/<skill-name>/SKILL.md

# 2. 用户自定义 skills 目录
~/.claude/skills/*/<skill-name>/SKILL.md

# 3. 独立 skill 文件
~/.claude/skills/<skill-name>.md

# 4. 项目级 skills（当前工作目录）
.claude/skills/<skill-name>/SKILL.md
```

**搜索命令：**
```bash
# 在 ~/.claude 下搜索包含 SKILL.md 的目录
find ~/.claude -name "SKILL.md" -type f 2>/dev/null | while read f; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  echo "$name: $dir"
done

# 或搜索特定名称
find ~/.claude -type d -name "<skill-name>" 2>/dev/null
```

### 4. 确认后操作

找到 skill 后：
1. 显示找到的位置，请用户确认
2. 如果找到多个匹配，列出选项让用户选择
3. 确认后执行迁移
4. **如果用户未指定远端，迁移完成后询问是否配置**

## 执行步骤

### 命令: `/share-skill remote <alias> <endpoint>`

配置 Git 远端别名：

1. **读取现有配置**
   ```bash
   cat ~/.claude/share-skill-config.json 2>/dev/null || echo '{"remotes":{}}'
   ```

2. **更新配置**
   ```json
   {
     "remotes": {
       "<alias>": "<endpoint>"
     }
   }
   ```

3. **写入配置文件**（保留现有配置）

4. **输出确认**
   ```
   ✅ 已配置远端别名

   别名: github
   地址: git@github.com:guo-yu/skills

   使用方式:
     /share-skill <skill-name> --remote github
     或: "帮我把 xxx 开源到 github"
   ```

### 命令: `/share-skill remote list`

列出已配置的远端别名：

```bash
cat ~/.claude/share-skill-config.json | jq '.remotes'
```

**输出格式：**
```
📡 已配置的远端别名:

  github  → git@github.com:guo-yu/skills
  gitlab  → git@gitlab.com:guo-yu/skills
  gitee   → git@gitee.com:guo-yu/skills

默认: github
```

### 命令: `/share-skill <skill-name> [--remote <url|alias>]`

将指定的 skill 从 `~/.claude/` 目录迁移到 `{skills_path}/`：

1. **搜索 skill 位置**
   ```bash
   # 优先在标准位置查找
   if [ -d ~/.claude/skills/<skill-name> ]; then
     SKILL_PATH=~/.claude/skills/<skill-name>
   else
     # 递归搜索
     SKILL_PATH=$(find ~/.claude -type d -name "<skill-name>" 2>/dev/null | head -1)
   fi
   ```
   - 如果找不到，报错退出
   - 如果已经是符号链接，提示已迁移并显示链接目标
   - 如果找到多个，列出让用户选择

2. **检查目标目录**
   ```bash
   ls {skills_path}/<skill-name> 2>/dev/null
   ```
   - 如果目标已存在，报错退出（避免覆盖）

3. **执行迁移**
   ```bash
   # 创建目标目录（如果不存在）
   mkdir -p {skills_path}

   # 移动 skill 到代码目录
   mv ~/.claude/skills/<skill-name> {skills_path}/

   # 创建符号链接
   ln -s {skills_path}/<skill-name> ~/.claude/skills/<skill-name>
   ```

4. **创建 .gitignore**
   ```bash
   cat > {skills_path}/<skill-name>/.gitignore << 'EOF'
   # OS
   .DS_Store
   Thumbs.db

   # Editor
   .vscode/
   .idea/
   *.swp
   *.swo

   # Logs
   *.log

   # Temp
   tmp/
   temp/
   EOF
   ```

5. **初始化 Git**
   ```bash
   cd {skills_path}/<skill-name>
   git init
   git add .
   git commit -m "Initial commit: <skill-name> skill"
   ```

6. **配置远端（如果指定）**

   如果用户指定了 `--remote`：
   ```bash
   # 如果是别名，解析为完整地址
   if [ "<remote>" 是别名 ]; then
     ENDPOINT=$(从配置读取别名对应的 endpoint)
     REMOTE_URL="${ENDPOINT}/<skill-name>.git"
   else
     REMOTE_URL="<remote>"
   fi

   cd {skills_path}/<skill-name>
   git remote add origin "$REMOTE_URL"
   git push -u origin master
   ```

7. **未指定远端时询问**

   如果用户未指定远端，迁移完成后使用 AskUserQuestion 询问：
   ```
   是否需要配置 Git 远端地址？

   选项:
   - 使用 github (git@github.com:guo-yu/skills/<skill-name>.git)
   - 使用 gitlab (git@gitlab.com:guo-yu/skills/<skill-name>.git)
   - 输入自定义地址
   - 暂不配置
   ```

### 命令: `/share-skill list`

列出所有可迁移的本地 skill（排除已是符号链接的）：

```bash
# 搜索 ~/.claude 下所有包含 SKILL.md 的目录
echo "📋 发现的 skill:"
find ~/.claude -name "SKILL.md" -type f 2>/dev/null | while read f; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  if [ -L "$dir" ]; then
    target=$(readlink "$dir")
    echo "  🔗 $name -> $target (已迁移)"
  else
    echo "  📦 $name: $dir (可迁移)"
  fi
done
```

## 输出格式

### 迁移成功（带远端）
```
✅ Skill 迁移成功

📦 skill: <skill-name>
📁 新位置: {skills_path}/<skill-name>
🔗 符号链接: ~/.claude/skills/<skill-name> -> {skills_path}/<skill-name>
📝 Git: 已初始化并提交
📡 远端: git@github.com:guo-yu/skills/<skill-name>.git
🚀 已推送到远端

仓库地址: https://github.com/guo-yu/skills
```

### 迁移成功（无远端）
```
✅ Skill 迁移成功

📦 skill: <skill-name>
📁 新位置: {skills_path}/<skill-name>
🔗 符号链接: ~/.claude/skills/<skill-name> -> {skills_path}/<skill-name>
📝 Git: 已初始化并提交

是否需要配置远端地址？
```

### 已迁移
```
ℹ️ Skill 已迁移

<skill-name> 已经是符号链接：
  ~/.claude/skills/<skill-name> -> {skills_path}/<skill-name>
```

### 列表
```
📋 可迁移的本地 skill (N个):
  - art-master
  - design-master
  - prompt-generator

🔗 已迁移的 skill (M个):
  - port-allocator -> {skills_path}/port-allocator
  - share-skill -> {skills_path}/share-skill
```

## 目录结构

### 混合 Git 管理模式

share-skill 支持两种 Git 管理模式：

| 模式 | 触发条件 | Git 结构 | 远端 |
|------|---------|---------|------|
| **Monorepo** | 使用默认端点 | 父仓库管理 | `guo-yu/skills` |
| **独立仓库** | 指定自定义端点 | 独立 .git | 用户指定 |

### Monorepo 模式（默认）

当使用默认端点时，所有 skill 由父仓库 `{skills_path}/.git` 统一管理：

```
{skills_path}/
├── .git/                      # 父仓库 → guo-yu/skills
├── .gitignore
├── README.md
├── port-allocator/            # 无独立 .git，由父仓库管理
│   ├── .gitignore
│   └── SKILL.md
├── share-skill/
│   ├── .gitignore
│   └── SKILL.md
└── skill-permissions/
    ├── .gitignore
    └── SKILL.md
```

**操作方式：**
```bash
# 新增 skill 后
cd {skills_path}
git add <new-skill>/
git commit -m "Add <new-skill>"
git push
```

### 独立仓库模式（自定义端点）

当用户指定自定义端点时，该 skill 拥有独立的 .git：

```
{skills_path}/
├── .git/                      # 父仓库
├── .gitignore                 # 包含: /custom-skill/
├── custom-skill/              # 独立仓库 → 用户指定的地址
│   ├── .git/
│   └── SKILL.md
└── port-allocator/            # 由父仓库管理
```

**父仓库 .gitignore 自动更新：**
```gitignore
# Skills with custom endpoints
/custom-skill/
```

### 符号链接

无论哪种模式，`~/.claude/skills/` 中都使用符号链接：

```
~/.claude/skills/
├── port-allocator -> {skills_path}/port-allocator
├── share-skill -> {skills_path}/share-skill
└── skill-permissions -> {skills_path}/skill-permissions
```

## 首次使用

如果遇到权限提示，请先运行：
```
/share-skill allow
```

### 命令: `/share-skill allow`

执行一次性授权，将本 skill 所需的权限添加到 Claude Code 配置中：

1. 读取 `~/.claude/settings.json`
2. 合并以下权限到 `permissions.allow`：

```json
{
  "permissions": {
    "allow": [
      "Bash(cat ~/.claude/*)",
      "Bash(find ~/.claude *)",
      "Bash(ls {skills_path}/*)",
      "Bash(mkdir -p {skills_path}*)",
      "Bash(mv ~/.claude/skills/* *)",
      "Bash(ln -s {skills_path}/* *)",
      "Bash(git *)",
      "Bash(dirname *)",
      "Bash(basename *)",
      "Bash(readlink *)"
    ]
  }
}
```

3. 写入配置文件（保留现有权限）
4. 输出授权结果

**输出格式：**
```
✅ 已配置 Claude Code 权限

新增允许的命令模式：
  - Bash(cat ~/.claude/*)
  - Bash(find ~/.claude *)
  - Bash(ls {skills_path}/*)
  - Bash(mkdir -p {skills_path}*)
  - Bash(mv ~/.claude/skills/* *)
  - Bash(ln -s {skills_path}/* *)
  - Bash(git *)
  - Bash(dirname *)
  - Bash(basename *)
  - Bash(readlink *)

配置文件: ~/.claude/settings.json
```

## 注意事项

1. **不覆盖** - 如果目标目录已存在，会报错而非覆盖
2. **保持兼容** - 符号链接确保 Claude Code 仍能正常读取 skill
3. **Git 跟踪** - 自动初始化 git 并创建首次提交
4. **别名优先** - 使用别名时自动拼接 skill 名称作为仓库名
5. **询问远端** - 未指定远端时，迁移后主动询问用户
6. **首次授权** - 建议先运行 `/share-skill allow` 配置权限

---

## 文档网站生成

share-skill 支持自动生成优雅的文档网站，用于展示 skill 的使用说明。

### 命令: `/share-skill docs`

为 skills 仓库生成 GitHub Pages 文档网站。

**参数：**
- `--style <name>`: 使用预设的设计风格（默认: `botanical`）
- `--skill <ui-skill>`: 调用指定的 UI 技能进行设计
- `--domain <domain>`: 配置自定义域名
- `--i18n`: 启用 SKILL.md 和 README 文件的多语言选择

### i18n 语言选择

由于生成多语言文档比较耗时且消耗 token，用户可以通过交互式 TUI 勾选框选择要生成的语言。

**触发条件：** 运行 `/share-skill docs` 时使用 `--i18n` 参数，或命令检测到需要翻译 SKILL.md 文件时。

**TUI 界面：**
```
选择文档语言（空格切换，回车确认）：

  [x] English (en)        - 始终生成
  [ ] 简体中文 (zh-CN)    - 简体中文
  [ ] 日本語 (ja)         - 日语
  [ ] 其他...             - 输入自定义语言代码

已选择: English
```

**默认选择：**
- English: **已勾选**（必需，始终生成）
- 简体中文 (zh-CN): **未勾选**
- 日本語 (ja): **未勾选**
- 其他: **未勾选**（允许输入自定义语言代码）

**自定义语言输入：**
当用户选择"其他..."时，提示输入语言代码：
```
请输入语言代码（例如：'ko' 表示韩语，'de' 表示德语）：
> ko

已添加语言: 한국어 (ko)
```

**AskUserQuestion 实现：**
```json
{
  "questions": [
    {
      "question": "选择要生成的文档语言",
      "header": "语言",
      "multiSelect": true,
      "options": [
        { "label": "English (en)", "description": "必需，始终生成" },
        { "label": "简体中文 (zh-CN)", "description": "简体中文翻译" },
        { "label": "日本語 (ja)", "description": "日语翻译" },
        { "label": "其他...", "description": "输入自定义语言代码" }
      ]
    }
  ]
}
```

**根据选择生成的文件：**
| 选择 | SKILL 文件 | README 文件 |
|------|-----------|------------|
| 仅英文 | `SKILL.md` | `README.md` |
| +中文 | `SKILL.md`, `SKILL.zh-CN.md` | `README.md`, `README.zh-CN.md` |
| +日语 | `SKILL.md`, `SKILL.ja.md` | `README.md`, `README.ja.md` |
| +韩语 | `SKILL.md`, `SKILL.ko.md` | `README.md`, `README.ko.md` |

**执行步骤：**

1. **检查仓库结构**
   ```bash
   # 确认在 skills 仓库目录
   if [ ! -d {skills_path}/.git ]; then
     echo "请先在 skills 仓库中运行此命令"
     exit 1
   fi
   ```

2. **读取配置**
   ```bash
   # 从配置读取设计偏好
   cat ~/.claude/share-skill-config.json | jq '.docs'
   ```

3. **选择设计方式**
   - 如果指定 `--skill`：调用对应的 UI skill（如 `ui-ux-pro-max`）
   - 否则使用 `--style` 指定的预设风格（默认 `botanical`）

4. **生成文档网站**
   ```bash
   mkdir -p {skills_path}/docs
   mkdir -p {skills_path}/docs/css
   mkdir -p {skills_path}/docs/js
   ```

5. **配置本地开发服务器**

   根据端点配置和现有 package.json 情况处理：

   **场景 A：Monorepo 模式（默认端点）**

   检查 `{skills_path}/package.json` 是否存在：

   ```bash
   if [ -f {skills_path}/package.json ]; then
     # 已存在，只添加 docs 相关脚本（不覆盖现有内容）
     # 使用 jq 或手动合并 scripts
   else
     # 不存在，创建新的 package.json
   fi
   ```

   - **已存在 package.json**：追加 `dev:docs` 脚本
     ```bash
     # 读取现有 package.json，添加新脚本
     jq '.scripts["dev:docs"] = "npx serve . -l <端口>"' package.json > tmp.json
     mv tmp.json package.json
     ```

   - **不存在 package.json**：创建新文件
     ```json
     {
       "name": "claude-code-skills",
       "version": "1.0.0",
       "private": true,
       "scripts": {
         "dev": "npx serve . -l <端口>"
       }
     }
     ```

   **场景 B：独立仓库模式（自定义端点）**

   每个 skill 有独立的 Git 仓库，检查各自的 package.json：

   ```bash
   SKILL_DIR={skills_path}/<skill-name>

   if [ -f "$SKILL_DIR/package.json" ]; then
     # ⚠️ 重要：不覆盖用户现有的 package.json
     # 只追加 docs 脚本（如果不存在）
     echo "检测到现有 package.json，追加 dev:docs 脚本"
   else
     # 创建最小化的 package.json
     echo "创建 package.json..."
   fi
   ```

   **端口分配流程：**
   - 读取 `~/.claude/port-registry.json` 获取下一个可用端口
   - 更新 port-registry 注册该项目
   - 追加或创建 package.json 中的开发脚本

   **⚠️ 安全规则：**
   - **绝不覆盖**现有的 package.json
   - 只在 `scripts` 字段中**追加**新命令
   - 如果 `dev` 脚本已存在，使用 `dev:docs` 作为替代命令名

6. **配置自定义域名**（可选）
   ```bash
   echo "skill.guoyu.me" > {skills_path}/docs/CNAME
   ```

7. **更新缓存版本号**

   每次修改 docs 内容时，自动更新资源文件的版本号以避免浏览器缓存问题：

   ```bash
   # 生成版本号（使用时间戳）
   VERSION=$(date +%s)

   # 更新 index.html 中的版本号
   sed -i '' "s/main.js?v=[0-9]*/main.js?v=$VERSION/" docs/index.html
   sed -i '' "s/custom.css?v=[0-9]*/custom.css?v=$VERSION/" docs/index.html
   ```

   **或者使用文件哈希：**
   ```bash
   JS_HASH=$(md5 -q docs/js/main.js | head -c 8)
   CSS_HASH=$(md5 -q docs/css/custom.css | head -c 8)

   sed -i '' "s/main.js?v=[a-z0-9]*/main.js?v=$JS_HASH/" docs/index.html
   sed -i '' "s/custom.css?v=[a-z0-9]*/custom.css?v=$CSS_HASH/" docs/index.html
   ```

   **index.html 模板应包含版本占位符：**
   ```html
   <link rel="stylesheet" href="css/custom.css?v=1">
   <script src="js/main.js?v=1"></script>
   ```

8. **提交并推送**
   ```bash
   git add docs/
   git commit -m "Update documentation site"
   git push
   ```

### 文档网站功能特性

生成的文档网站包含以下功能：

#### 1. 动态导航栏品牌

导航栏品牌（头像 + 标题）链接到仓库 URL，并从 GitHub API 动态获取数据：

```html
<!-- index.html -->
<a class="navbar-brand" id="repoLink" href="https://github.com/{username}/{repo}" target="_blank">
    <img class="brand-avatar" id="userAvatar" src="" alt="Avatar">
    <span class="brand-text" id="brandTitle">Skills</span>
</a>
```

```javascript
// main.js - 动态更新仓库链接
const repoLink = document.getElementById('repoLink');
if (repoLink) {
    repoLink.href = `https://github.com/${REPO_OWNER}/${REPO_NAME}`;
}
```

#### 2. 动态 Favicon

Favicon 使用 GitHub 用户的头像：

```html
<!-- index.html head 部分 -->
<link rel="icon" id="favicon" type="image/png" href="">
```

```javascript
// main.js - 设置 favicon 为用户头像
const favicon = document.getElementById('favicon');
if (favicon) {
    favicon.href = user.avatar_url;
}
```

#### 3. 页脚署名

页脚链接到文档网站（如果有自定义域名）：

```html
<footer class="footer">
    <div class="footer-content">
        <p>Made with <span class="heart">♥</span> by <a href="https://{custom_domain}/">Yu's skills</a></p>
    </div>
</footer>
```

#### 4. i18n SKILL.md 缓存破坏

加载语言特定的 SKILL.md 文件时，添加缓存破坏参数以确保获取最新内容：

```javascript
// main.js
const CACHE_VERSION = Date.now();

function getBasePath(skillName, lang = 'en') {
    const fileName = lang === 'en' ? 'SKILL.md' : `SKILL.${lang}.md`;

    if (isGitHubPages) {
        // 为 GitHub raw 内容添加缓存破坏
        return `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${BRANCH}/${skillName}/${fileName}?v=${CACHE_VERSION}`;
    } else {
        // 为本地开发添加缓存破坏
        return `../${skillName}/${fileName}?v=${CACHE_VERSION}`;
    }
}
```

#### 5. main.js 配置

`main.js` 文件顶部应包含仓库配置：

```javascript
// 仓库配置 - 更新这些值
const REPO_OWNER = '{github-username}';  // 例如 'guo-yu'
const REPO_NAME = '{repo-name}';          // 例如 'skills'
const BRANCH = 'master';                   // 或 'main'

// 缓存破坏版本号
const CACHE_VERSION = Date.now();
```

#### 6. 营销展示区（为什么使用这个技能？）

每个技能在文档内容上方显示一个引人注目的营销展示区，包含：
- **标题**：一句话说明价值主张
- **原因**：解释为什么用户应该使用这个技能
- **痛点**：三张卡片展示该技能解决的问题

**main.js 中的 SKILL_MARKETING 数据结构：**

```javascript
const SKILL_MARKETING = {
    'skill-name': {
        en: {
            headline: '引人注目的一句话价值主张',
            why: '详细解释这个技能存在的原因以及如何帮助用户...',
            painPoints: [
                {
                    icon: '🔥',
                    title: '问题标题',
                    desc: '描述这个技能解决的问题。'
                },
                {
                    icon: '🧠',
                    title: '另一个问题',
                    desc: '另一个痛点的描述。'
                },
                {
                    icon: '💥',
                    title: '第三个问题',
                    desc: '第三个问题的描述。'
                }
            ]
        },
        'zh-CN': {
            headline: '中文标题',
            why: '中文说明...',
            painPoints: [/* ... */]
        },
        ja: {
            headline: '日本語タイトル',
            why: '日本語説明...',
            painPoints: [/* ... */]
        }
    }
};
```

**渲染函数：**

```javascript
function renderMarketingSection(skillName) {
    const marketing = SKILL_MARKETING[skillName];
    if (!marketing) return '';

    const content = marketing[currentLang] || marketing['en'];
    // 返回包含 .marketing-section 结构的 HTML
}
```

**CSS 类：**
- `.marketing-section` - 带渐变背景的容器
- `.marketing-title` - 渐变文字标题
- `.marketing-why` - 价值主张段落
- `.pain-points-grid` - 响应式三栏网格
- `.pain-point-card` - 玻璃卡片，包含图标、标题、描述

**营销内容撰写指南：**
1. 从用户角度撰写（使用"你"而不是"这个技能"）
2. 先展示痛点，再给出解决方案
3. 使用具体、可共鸣的例子（如"端口 3000 已被占用"）
4. 标题控制在 10 个字以内
5. 痛点标题应该是问题本身，而不是解决方案

#### 7. 三栏布局

文档网站使用响应式三栏布局：

```html
<div class="main-container three-column">
    <!-- 左侧边栏：技能导航 + 目录 -->
    <aside class="sidebar glass">
        <div class="sidebar-content">
            <div class="sidebar-section">
                <h4 class="sidebar-heading" data-i18n="skills">技能列表</h4>
                <nav class="sidebar-nav">
                    <a class="sidebar-link" href="?skill=port-allocator">port-allocator</a>
                    <a class="sidebar-link" href="?skill=share-skill">share-skill</a>
                    <!-- ... 更多技能 -->
                </nav>
            </div>
            <div class="sidebar-section">
                <h4 class="sidebar-heading" data-i18n="onThisPage">本页目录</h4>
                <div class="js-toc"></div>  <!-- Tocbot 在此生成目录 -->
            </div>
        </div>
    </aside>

    <!-- 主内容：Markdown 文档 -->
    <main class="main-content">
        <article class="js-toc-content content-card glass" id="content">
            <!-- 渲染的 markdown 内容 -->
        </article>
    </main>

    <!-- 右侧边栏：安装说明 -->
    <aside class="sidebar-right glass">
        <!-- 安装部分 -->
    </aside>
</div>
```

**响应式行为：**
- 桌面端：三栏全部可见
- 平板端：隐藏右侧边栏
- 移动端：隐藏两侧边栏，显示移动菜单

#### 8. 右侧边栏 - 安装说明

右侧边栏提供快速安装指南：

```html
<aside class="sidebar-right glass">
    <div class="sidebar-content">
        <div class="sidebar-section">
            <h4 class="sidebar-heading" data-i18n="installation">安装方法</h4>
            <p class="install-desc" data-i18n="installDesc">最简单的安装方式：</p>
            <div class="install-code">
                <pre><code><span class="comment"># <span data-i18n="addMarketplace">添加技能市场</span></span>
<span class="cmd">/plugin marketplace add {username}/{repo}</span>

<span class="comment"># <span data-i18n="installSkills">安装技能</span></span>
<span class="cmd">/plugin install {skill-name}@{username}-{repo}</span></code></pre>
            </div>
            <a class="install-link" href="https://github.com/{username}/{repo}#installation" target="_blank" data-i18n="moreOptions">更多安装选项</a>
        </div>
    </div>
</aside>
```

**安装部分的 i18n 支持：**
```javascript
const I18N = {
    en: {
        installation: 'Installation',
        installDesc: 'The easiest way to install:',
        addMarketplace: 'Add marketplace',
        installSkills: 'Install skills',
        moreOptions: 'More installation options'
    },
    'zh-CN': {
        installation: '安装方法',
        installDesc: '最简单的安装方式：',
        addMarketplace: '添加技能市场',
        installSkills: '安装技能',
        moreOptions: '更多安装选项'
    },
    ja: {
        installation: 'インストール',
        installDesc: '最も簡単なインストール方法：',
        addMarketplace: 'マーケットプレイスを追加',
        installSkills: 'スキルをインストール',
        moreOptions: 'その他のインストールオプション'
    }
};
```

#### 9. 目录生成 (Tocbot)

使用 Tocbot 库从标题自动生成目录：

```html
<!-- 在 <head> 中 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tocbot/4.32.2/tocbot.min.css">

<!-- 在 </body> 前 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/tocbot/4.32.2/tocbot.min.js"></script>
```

```javascript
// 内容加载后初始化
tocbot.init({
    tocSelector: '.js-toc',
    contentSelector: '.js-toc-content',
    headingSelector: 'h1, h2, h3',
    scrollSmooth: true,
    scrollSmoothDuration: 300,
    headingsOffset: 100,
    scrollSmoothOffset: -100
});
```

#### 10. 代码语法高亮 (highlight.js)

使用 highlight.js 进行代码块语法高亮：

```html
<!-- 在 <head> 中 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">

<!-- 在 </body> 前 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
```

```javascript
// 渲染 markdown 后
document.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightElement(block);
});
```

### 命令: `/share-skill docs config`

配置文档生成的默认设置。

**交互选项：**
```
📝 配置文档网站设计

设计方式:
  1. 使用预设风格
  2. 使用 UI 技能

预设风格:
  - botanical (默认): 自然植物风格，优雅柔和
  - minimal: 极简黑白风格
  - tech: 现代科技感风格

UI 技能:
  - ui-ux-pro-max: 专业 UI/UX 设计技能
  - (其他用户安装的 UI 技能)

自定义域名: (可选)
```

### 设计风格预设

#### `botanical` - 自然植物风格（默认）

**设计理念：**
数字化的自然致敬——呼吸、流动、扎根于有机之美。柔和、精致、深思熟虑，拒绝现代科技美学的刚硬和超数字化锐利，转而拥抱温暖、触感和自然的不完美。

**核心元素：**
- **有机柔和**: 圆角无处不在，形状如水磨石般流畅
- **字体优雅**: Playfair Display 高对比衬线体 + Source Sans 3 人文无衬线体
- **大地色系**: 森林绿 (#2D3A31)、鼠尾草绿 (#8C9A84)、陶土色 (#C27B66)、米纸白 (#F9F8F4)
- **纸质纹理**: 必须的 SVG 噪点叠加层，将冷冰冰的数字像素转化为温暖触感
- **呼吸空间**: 慷慨的留白，section 间距 py-32，卡片间距 gap-16
- **缓慢动效**: 如微风中摇曳的植物，duration-500 到 duration-700

**色彩系统：**
| 用途 | 颜色 | 色值 |
|------|------|------|
| 背景 | 暖白/米纸 | `#F9F8F4` |
| 前景 | 深森林绿 | `#2D3A31` |
| 主色 | 鼠尾草绿 | `#8C9A84` |
| 次色 | 软陶/蘑菇 | `#DCCFC2` |
| 边框 | 石色 | `#E6E2DA` |
| 交互 | 陶土色 | `#C27B66` |

**字体配对：**
- 标题: **Playfair Display** (Google Font) - 过渡衬线体，高对比笔画
- 正文: **Source Sans 3** (Google Font) - 清晰易读的人文无衬线体

**圆角规则：**
- 卡片: `rounded-3xl` (24px)
- 按钮: `rounded-full` (药丸形)
- 图片: `rounded-t-full` (拱形) 或 `rounded-[40px]`

**纸质纹理叠加层（关键）：**
```jsx
<div
  className="pointer-events-none fixed inset-0 z-50 opacity-[0.015]"
  style={{
    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
    backgroundRepeat: "repeat",
  }}
/>
```

**阴影系统：**
```css
/* 默认 */
box-shadow: 0 4px 6px -1px rgba(45, 58, 49, 0.05);
/* 中等 */
box-shadow: 0 10px 15px -3px rgba(45, 58, 49, 0.05);
/* 大 */
box-shadow: 0 20px 40px -10px rgba(45, 58, 49, 0.05);
```

**动效规范：**
- 快速交互: `duration-300` (按钮悬停、链接颜色)
- 标准: `duration-500` (卡片提升、变换)
- 慢速戏剧性: `duration-700` 到 `duration-1000` (图片缩放)
- 悬停行为: `-translate-y-1` 配合阴影增强

**响应式策略：**
- 移动端: 隐藏侧边栏，标题从 text-8xl 降至 text-5xl
- 触摸目标: 保持最小 44px 高度
- 网格断点: `grid-cols-1` → `md:grid-cols-3`

### 使用外部 UI 技能

如果用户安装了 `ui-ux-pro-max` 或其他 UI 技能，可以调用它来设计文档：

```bash
/share-skill docs --skill ui-ux-pro-max
```

**执行流程：**

1. **检测技能是否存在**
   ```bash
   if [ -d ~/.claude/skills/ui-ux-pro-max ] || [ -L ~/.claude/skills/ui-ux-pro-max ]; then
     echo "✅ 检测到 ui-ux-pro-max 技能"
   fi
   ```

2. **调用技能生成设计**
   - 将当前 skills 列表和结构信息传递给 UI 技能
   - UI 技能生成完整的 HTML/CSS/JS
   - 输出到 `{skills_path}/docs/` 目录

3. **询问设计偏好**（如果 UI 技能支持）
   ```
   📐 使用 ui-ux-pro-max 设计文档网站

   请选择设计风格:
     1. glassmorphism - 玻璃拟态
     2. claymorphism - 粘土质感
     3. minimalism - 极简主义
     4. brutalism - 粗野主义
     5. neumorphism - 新拟态
     6. bento-grid - 便当盒布局
   ```

### 输出格式

**成功生成：**
```
✅ 文档网站已生成

📁 位置: {skills_path}/docs/
🎨 设计风格: botanical (自然植物风格)
🌐 自定义域名: skill.guoyu.me

文件结构:
  docs/
  ├── index.html
  ├── CNAME
  ├── css/
  │   └── custom.css
  └── js/
      └── main.js

📡 已推送到 GitHub
🔗 访问: https://skill.guoyu.me

💡 GitHub Pages 设置:
   1. 仓库 Settings → Pages
   2. Source: Deploy from a branch
   3. Branch: master, /docs
```

**使用 UI 技能：**
```
✅ 文档网站已生成

📁 位置: {skills_path}/docs/
🎨 设计: ui-ux-pro-max (glassmorphism 风格)
🌐 自定义域名: skill.guoyu.me

🔗 访问: https://skill.guoyu.me
```

---

## README 自动生成

share-skill 在创建或更新仓库时，会自动生成/更新多语言 README 文件。

### 支持的语言

| 语言 | 文件名 | 语言代码 |
|------|--------|---------|
| English (默认) | `README.md` | `en` |
| 简体中文 | `README.zh-CN.md` | `zh-CN` |
| 日本語 | `README.ja.md` | `ja` |

### 文件结构

```
skills/
├── README.md              # English (默认)
├── README.zh-CN.md        # 简体中文
├── README.ja.md           # 日本語
└── ...
```

### 语言切换导航

每个 README 文件顶部都包含语言切换链接：

```markdown
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja.md">日本語</a>
</p>
```

### README 标题规则

| 仓库类型 | English | 简体中文 | 日本語 |
|---------|---------|---------|--------|
| **Skill Set** | `{username}'s Skills` | `{username} 的技能集` | `{username} のスキル` |
| **单个 Skill** | `{username}'s Skill: {name}` | `{username} 的技能: {name}` | `{username} のスキル: {name}` |

### README 模板 - English (README.md)

```markdown
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja.md">日本語</a>
</p>

# {username}'s Skills

My collection of custom Claude Code skills for productivity and automation.

## Skills

| Skill | Description |
|-------|-------------|
| [port-allocator](./port-allocator/) | Automatically allocate development server ports |
| [share-skill](./share-skill/) | Migrate skills to repositories with Git support |

## Documentation

This skill set has an online documentation site generated by [share-skill](https://github.com/guo-yu/skills/tree/master/share-skill).

**With Custom Domain:**
```
https://{custom_domain}/
```

**GitHub Pages:**
```
https://{username}.github.io/{repo-name}/
```

### Setup GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Under "Source", select **Deploy from a branch**
3. Choose branch: `master` (or `main`), folder: `/docs`
4. (Optional) Add custom domain

## License

MIT

---

Made with ♥ by [Yu's skills](https://skill.guoyu.me/)
```

### README 模板 - 简体中文 (README.zh-CN.md)

```markdown
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja.md">日本語</a>
</p>

# {username} 的技能集

我的 Claude Code 自定义技能集合，用于提高生产力和自动化。

## 技能列表

| 技能 | 说明 |
|------|------|
| [port-allocator](./port-allocator/) | 自动分配开发服务器端口 |
| [share-skill](./share-skill/) | 将技能迁移到仓库并支持 Git 版本管理 |

## 在线文档

本技能集有一个由 [share-skill](https://github.com/guo-yu/skills/tree/master/share-skill) 生成的在线文档网站。

**自定义域名访问：**
```
https://{custom_domain}/
```

**GitHub Pages 访问：**
```
https://{username}.github.io/{repo-name}/
```

### 配置 GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. 在 "Source" 下选择 **Deploy from a branch**
3. 选择分支: `master` (或 `main`)，文件夹: `/docs`
4. (可选) 在 "Custom domain" 中添加自定义域名

## 许可证

MIT

---

Made with ♥ by [Yu's skills](https://skill.guoyu.me/)
```

### README 模板 - 日本語 (README.ja.md)

```markdown
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja.md">日本語</a>
</p>

# {username} のスキル

生産性と自動化のための Claude Code カスタムスキルコレクション。

## スキル一覧

| スキル | 説明 |
|--------|------|
| [port-allocator](./port-allocator/) | 開発サーバーポートの自動割り当て |
| [share-skill](./share-skill/) | Git サポート付きでスキルをリポジトリに移行 |

## ドキュメント

このスキルセットには [share-skill](https://github.com/guo-yu/skills/tree/master/share-skill) で生成されたオンラインドキュメントサイトがあります。

**カスタムドメイン：**
```
https://{custom_domain}/
```

**GitHub Pages：**
```
https://{username}.github.io/{repo-name}/
```

### GitHub Pages の設定

1. リポジトリの **Settings** → **Pages** に移動
2. "Source" で **Deploy from a branch** を選択
3. ブランチ: `master` (または `main`)、フォルダ: `/docs` を選択
4. (オプション) "Custom domain" にカスタムドメインを追加

## ライセンス

MIT

---

Made with ♥ by [Yu's skills](https://skill.guoyu.me/)
```

### 执行步骤

在 `/share-skill docs` 或 `/share-skill <skill-name>` 执行时：

1. **读取配置**
   ```bash
   CONFIG=$(cat ~/.claude/share-skill-config.json)
   GITHUB_URL=$(echo "$CONFIG" | jq -r '.remotes.github')
   GITHUB_USERNAME=$(echo "$GITHUB_URL" | grep -oP 'github\.com[:/]\K[^/]+')
   CUSTOM_DOMAIN=$(echo "$CONFIG" | jq -r '.docs.custom_domain // empty')
   REPO_NAME=$(basename "$(git rev-parse --show-toplevel)")
   ```

2. **生成语言切换导航**
   ```bash
   LANG_NAV='<p align="center">
     <a href="README.md">English</a> |
     <a href="README.zh-CN.md">简体中文</a> |
     <a href="README.ja.md">日本語</a>
   </p>'
   ```

3. **生成所有语言版本的 README**
   ```bash
   # 定义语言配置
   declare -A LANG_CONFIG
   LANG_CONFIG[en]="README.md"
   LANG_CONFIG[zh-CN]="README.zh-CN.md"
   LANG_CONFIG[ja]="README.ja.md"

   # 为每种语言生成 README
   for lang in en zh-CN ja; do
     FILE="${LANG_CONFIG[$lang]}"
     generate_readme "$lang" "$FILE"
   done
   ```

4. **写入 README 文件**
   ```bash
   generate_readme() {
     local lang=$1
     local file=$2

     # 根据语言选择模板
     case $lang in
       en)
         TITLE="${GITHUB_USERNAME}'s Skills"
         # ... 英文内容
         ;;
       zh-CN)
         TITLE="${GITHUB_USERNAME} 的技能集"
         # ... 中文内容
         ;;
       ja)
         TITLE="${GITHUB_USERNAME} のスキル"
         # ... 日文内容
         ;;
     esac

     cat > "$file" << EOF
     $LANG_NAV

     # $TITLE
     ...
     EOF
   }
   ```

### 输出格式

```
📝 README 多语言文件已更新

生成的文件:
  ✓ README.md (English)
  ✓ README.zh-CN.md (简体中文)
  ✓ README.ja.md (日本語)

文档链接: https://skill.guoyu.me/

包含章节:
  ✓ 语言切换导航
  ✓ Skills 列表
  ✓ Documentation (在线文档说明)
  ✓ License
  ✓ Attribution (Made with ♥)
```

---

## 本地测试

share-skill 提供验证脚本，确保生成的文档符合 SKILL.md 规范。

### 验证脚本

位置：`share-skill/test/verify-docs.sh`

**使用方法：**
```bash
# 测试当前目录
./share-skill/test/verify-docs.sh .

# 测试指定仓库
./share-skill/test/verify-docs.sh {skills_path}
```

**检查项目：**

| 类别 | 检查内容 |
|------|----------|
| **目录结构** | docs/index.html, docs/js/main.js, docs/css/custom.css, docs/CNAME |
| **index.html** | Favicon, 导航栏品牌, 三栏布局, 语言切换器, 安装说明, tocbot, highlight.js, 页脚, 版本号 |
| **main.js** | REPO_OWNER, REPO_NAME, BRANCH, CACHE_VERSION, I18N 对象, getBasePath, 动态 favicon/repoLink, tocbot.init, hljs |
| **README 文件** | README.md, README.zh-CN.md, README.ja.md, 语言导航链接, 页脚署名 |
| **技能文件** | 每个技能的 SKILL.md, SKILL.zh-CN.md, SKILL.ja.md |
| **技能配置** | 每个技能在 main.js SKILLS 对象中配置 |

**示例输出：**
```
╔════════════════════════════════════════════════════════════╗
║     share-skill Documentation Verification Script          ║
╚════════════════════════════════════════════════════════════╝

Repository: /Users/username/Codes/skills

── 1. Directory Structure ──
  ✓ docs/index.html exists
  ✓ docs/js/main.js exists
  ✓ docs/css/custom.css exists
  ✓ docs/CNAME exists (custom domain configured)

── 2. index.html Structure ──
  ✓ Favicon element with id='favicon'
  ✓ Navbar brand with id='repoLink'
  ...

════════════════════════════════════════════════════════════
                        Summary
════════════════════════════════════════════════════════════

  Passed:  71
  Failed:  0
  Warnings: 0

✓ All required checks passed!
```

**退出码：**
- `0`：所有检查通过
- `1`：一项或多项检查失败

### 何时运行

建议在以下情况运行验证脚本：
- 使用 `/share-skill docs` 生成文档后
- 提交文档更改前
- 排查文档问题时
- 作为文档的 CI/CD 流程的一部分
