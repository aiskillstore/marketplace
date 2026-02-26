---
name: obsidian-helper
description: |
  Obsidian 智能笔记助手。当用户提到 obsidian、日记、笔记、知识库、capture、review 时激活。

  【激活后必须执行】：
  1. 先完整阅读本 SKILL.md 文件
  2. 理解 AI 写入三条硬规矩（00_Inbox/AI/、追加式、白名单字段）
  3. 按 STEP 0 → STEP 1 → ... 顺序执行
  4. 不要跳过任何步骤，不要自作主张

  【禁止行为】：
  - 禁止不读 SKILL.md 就开始工作
  - 禁止跳过用户确认步骤
  - 禁止在非 00_Inbox/AI/ 位置创建新笔记（除非用户明确指定）
version: 1.4.0
author: Claude Code
---

# Obsidian Helper - 智能笔记助手

这是一个与 Obsidian MCP 深度整合的智能助手，提供三大核心功能来提升你的笔记效率。

---

## ⚡ 首次使用必读：自动检测与配置引导

### 执行任何功能前，Claude 必须先执行 STEP 0

```
STEP 0: MCP 连接检测（每次会话首次使用时执行）
├─ 尝试调用 obsidian_list_files_in_vault()
├─ 如果成功 → 继续执行用户请求的功能
└─ 如果失败 → 进入【配置引导流程】
```

### 配置引导流程（全中文提示）

当 MCP 连接失败时，Claude 必须向用户显示以下引导信息：

---

**检测到 Obsidian MCP 未连接，我来帮你配置！**

#### 📋 配置步骤

**第一步：安装 Obsidian 插件**

1. 打开 Obsidian → 设置 → 第三方插件
2. 关闭「安全模式」
3. 点击「浏览」，搜索 **Local REST API**
4. 安装并启用该插件

**第二步：获取 API Key**

1. 在 Obsidian 设置中找到 **Local REST API** 插件设置
2. 点击「Copy API Key」复制你的 API Key
3. 记下端口号（默认是 `27124`）

**第三步：配置 Claude Code MCP**

在终端运行以下命令，将 `你的API_KEY` 替换为刚才复制的 Key：

```bash
# 创建 MCP 配置目录（如果不存在）
mkdir -p ~/.claude

# 添加 Obsidian MCP 配置
cat >> ~/.claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "你的API_KEY",
        "OBSIDIAN_HOST": "https://127.0.0.1:27124"
      }
    }
  }
}
EOF
```

**或者手动编辑** `~/.claude/mcp.json`：

```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "你的API_KEY",
        "OBSIDIAN_HOST": "https://127.0.0.1:27124"
      }
    }
  }
}
```

**第四步：重启 Claude Code**

```bash
# 完全退出 Claude Code，然后重新启动
claude
```

**第五步：验证连接**

重启后，再次输入你想要的命令（如 `/daily`），我会自动验证连接是否成功。

---

#### ❓ 常见问题

| 问题 | 解决方案 |
|------|----------|
| 插件找不到 | 确保 Obsidian 版本 ≥ 1.0.0 |
| 连接被拒绝 | 检查 Obsidian 是否正在运行 |
| API Key 无效 | 重新在插件设置中复制 Key |
| 端口冲突 | 在插件设置中修改端口，并更新 mcp.json |

**需要帮助？** 告诉我你遇到的具体错误信息，我来帮你解决。

---

### 连接成功后的提示

当 MCP 连接成功时，Claude 应该简短确认：

```
✅ Obsidian 已连接！检测到你的知识库，现在开始执行 [功能名称]...
```

---

## 🎯 核心功能概览

| 命令 | 功能 | 使用场景 |
|------|------|----------|
| `/daily` | 智能日记助手 | 每日开始时，快速启动一天 |
| `/capture <主题>` | 知识捕获 | 随时记录想法、笔记 |
| `/review [period]` | 周期回顾 | 定期总结复盘 |

---

## 🏗️ 推荐 Vault 结构（PARA + Zettelkasten）

```
Vault/
├── 00_Inbox/                 # 随手记
│   └── AI/                   # 【重要】AI 专用落地区
├── 10_Projects/              # 有截止时间的项目
├── 20_Areas/                 # 长期领域（学习/健康/职业）
├── 30_Resources/             # 资料库
│   └── Products/             # 产品卡片
├── 40_Zettels/               # 永久笔记（结论/洞见）
├── 90_Archive/               # 归档
├── 99_System/Templates/      # 模板
└── Daily Notes/              # 日记
```

## ⚠️ AI 写入三条硬规矩

**Claude 必须遵守以下规则：**

### 规则 1: AI 专用落地区
```
新建笔记默认位置: 00_Inbox/AI/
用户确认后才移动到其他位置
```

### 规则 2: 追加式写入
```
✅ 用 obsidian_append_content 追加
✅ 用 obsidian_patch_content 在指定标题下追加
❌ 不要重写整篇笔记
```

### 规则 3: Properties 白名单
```yaml
# 只允许写这些字段，不能发明新字段
---
type: note | product | project | zettel
title: ""
tags: []
status: active | done | archived
created: {{date}}
---
```

---

## 📋 功能一：/daily - 智能日记助手

### 触发条件
- 用户输入 `/daily`
- 用户说「开始今天的日记」「今日日记」「daily note」

### 执行流程

```
STEP 0: MCP 连接检测（见上方）

STEP 1: 获取日记信息
├─ 尝试 obsidian_get_periodic_note(period: "daily")
├─ 如果失败，使用 obsidian_list_files_in_dir("Daily Notes") 查找今日文件
├─ 使用 obsidian_get_recent_periodic_notes 或手动获取昨日日记
└─ 检查日记是否已存在

STEP 2: 分析昨日内容
├─ 读取昨日日记内容
├─ 提取未完成的 TODO（正则匹配 `- \[ \]`）
├─ 识别重要事项
└─ 生成简要总结

STEP 3: 生成今日日记
├─ 如果今日日记不存在，创建新日记
├─ 使用标准模板结构
├─ 自动填入：
│   ├─ 昨日未完成事项 → 今日待办
│   ├─ 日期和星期（中文格式）
│   └─ 基础模板结构
└─ 使用 obsidian_append_content 写入

STEP 4: 向用户报告
├─ 显示日记创建/更新状态
├─ 列出继承的未完成任务数量
└─ 询问是否需要补充内容
```

### 日记模板结构

```markdown
---
date: {{YYYY-MM-DD}}
tags: [daily]
---

# {{星期}}, {{月}} {{日}}, {{年}}

## 今日重点

> [!tip] Focus
>

## 任务

### 从昨日继承
{{yesterday_incomplete_todos}}

### 必须完成
- [ ]

### 应该完成
- [ ]

### 可以完成
- [ ]

## 今日笔记

### 上午


### 下午


### 晚间


## 想法与灵感


## 今日创建的链接


## 晚间反思

### 顺利的地方


### 可以改进的地方


### 感恩

```

### 使用示例

**用户输入**: `/daily` 或 `开始今日日记`

**Claude 执行**:
1. 检测 MCP 连接 ✓
2. 获取今日日记（如 2026-01-19）
3. 获取昨日日记，提取未完成事项
4. 创建/更新今日日记
5. 回复：「✅ 今日日记已创建！从昨日继承了 X 项未完成任务。」

---

## 📋 功能二：/capture - 快速知识捕获

### 触发条件
- 用户输入 `/capture <主题>` 或 `/capture <主题> <内容>`
- 用户说「记录一下」「捕获」「添加笔记」「capture」

### 执行流程

```
STEP 0: MCP 连接检测

STEP 1: 解析用户输入
├─ 提取主题关键词（第一个词或引号内容）
├─ 提取要记录的内容（主题之后的所有文本）
└─ 如果只有主题没有内容，询问用户要记录什么

STEP 2: 搜索现有笔记
├─ 使用 obsidian_simple_search(query: 主题) 搜索
├─ 分析搜索结果的相关性
└─ 按相关度排序

STEP 3: 决策与执行
├─ 情况A：找到高度相关笔记（标题包含主题）
│   ├─ 告诉用户：「找到相关笔记《XXX》，是否追加到此笔记？」
│   ├─ 用户确认后，使用 obsidian_patch_content 追加
│   └─ 追加格式：## {{时间戳}} 捕获\n{{内容}}
│
├─ 情况B：找到部分相关笔记
│   ├─ 列出最相关的 3 个笔记
│   ├─ 询问：「选择追加到哪个笔记，或创建新笔记？」
│   └─ 根据用户选择执行
│
└─ 情况C：未找到相关笔记
    ├─ 告诉用户：「未找到相关笔记，将创建新笔记」
    ├─ 询问存放位置（列出现有文件夹）
    └─ 使用 obsidian_append_content 创建

STEP 4: 确认完成
└─ 显示：「✅ 已保存到《XXX》」
```

### 捕获内容格式

```markdown
## 2026-01-19 14:30 捕获

{{用户输入的内容}}

---
```

### 使用示例

**示例 1**:
```
用户: /capture API设计 RESTful API 应该使用名词而非动词
```
Claude: 搜索 → 找到「API设计最佳实践.md」→ 询问确认 → 追加内容

**示例 2**:
```
用户: /capture 新想法
```
Claude: 「你想记录什么内容？」→ 用户输入 → 搜索 → 处理

---

## 📋 功能三：/review - 周期回顾生成器

### 触发条件
- 用户输入 `/review` 或 `/review weekly` 或 `/review monthly`
- 用户说「周回顾」「月度总结」「复盘」「review」

### 执行流程

```
STEP 0: MCP 连接检测

STEP 1: 确定回顾周期
├─ 解析参数：daily / weekly（默认）/ monthly
└─ 计算时间范围

STEP 2: 收集数据
├─ 获取周期内的日记文件
│   ├─ 尝试 obsidian_get_recent_periodic_notes
│   └─ 备选：obsidian_list_files_in_dir + 日期过滤
├─ 使用 obsidian_batch_get_file_contents 批量读取
├─ 使用 obsidian_get_recent_changes 获取活跃文件
└─ 提取所有相关内容

STEP 3: 分析内容
├─ 统计任务完成情况
│   ├─ 已完成：匹配 `- \[x\]`
│   └─ 未完成：匹配 `- \[ \]`
├─ 提取重要事件和成就
├─ 识别高频主题词
├─ 发现知识关联
└─ 生成洞察

STEP 4: 生成报告
├─ 使用对应周期的模板
├─ 填充统计数据
├─ 添加分析内容
├─ 保存到 Daily Notes/ 文件夹
│   ├─ 周报：YYYY-WXX 周回顾.md
│   └─ 月报：YYYY-MM 月度回顾.md
└─ 使用 obsidian_append_content 写入

STEP 5: 展示结果
├─ 显示回顾摘要
├─ 列出关键数据
└─ 询问是否需要修改或补充
```

### 周回顾模板

```markdown
# {{年}}-W{{周}} 周回顾 | {{日期范围}}

## 📊 数据概览
| 指标 | 数值 |
|------|------|
| 📝 笔记数量 | {{count}} |
| ✅ 完成任务 | {{completed}} |
| ⏳ 未完成任务 | {{incomplete}} |
| 📂 活跃文件 | {{active}} |

## 🏆 本周成就
{{achievements}}

## 📋 任务总结

### ✅ 已完成
{{completed_list}}

### ⏳ 待继续
{{incomplete_list}}

## 💡 关键洞察
{{insights}}

## 🔗 知识连接
本周涉及的主要主题：{{themes}}

## 🎯 下周重点
1.
2.
3.

## 📝 反思
### 做得好的地方

### 可以改进的地方

---
*生成时间: {{timestamp}}*
```

---

## 🔧 配置选项

用户可以在 Obsidian 库中创建 `_config/obsidian-helper.md` 自定义配置：

```markdown
# Obsidian Helper 配置

## 日记设置
- 日记文件夹: Daily Notes/
- 日记格式: YYYY-MM-DD
- 周回顾格式: YYYY-[W]ww

## 捕获设置
- 默认捕获文件夹: Resources/
- 自动添加时间戳: true

## 回顾设置
- 默认回顾周期: weekly
- 回顾保存位置: Daily Notes/
```

Claude 在执行功能前，应检查是否存在此配置文件并读取设置。

---

## 🛠️ 技术实现

### 依赖的 MCP 工具

| 工具 | 用途 | 必需 |
|------|------|------|
| `obsidian_list_files_in_vault` | 检测连接、列出库结构 | ✅ |
| `obsidian_list_files_in_dir` | 列出目录文件 | ✅ |
| `obsidian_get_file_contents` | 读取文件内容 | ✅ |
| `obsidian_batch_get_file_contents` | 批量读取 | ✅ |
| `obsidian_simple_search` | 文本搜索 | ✅ |
| `obsidian_append_content` | 创建/追加内容 | ✅ |
| `obsidian_patch_content` | 精确编辑 | ⚪ |
| `obsidian_get_periodic_note` | 获取周期笔记 | ⚪ |
| `obsidian_get_recent_periodic_notes` | 最近周期笔记 | ⚪ |
| `obsidian_get_recent_changes` | 最近修改 | ⚪ |

### 错误处理策略

| 错误类型 | 处理方式 |
|----------|----------|
| MCP 未连接 | 显示完整配置引导（见上方） |
| 文件不存在 | 自动创建 |
| API 不可用 | 使用备选方法（如直接文件操作） |
| 搜索无结果 | 提示创建新笔记 |

---

## 📚 快速参考

```
/daily                    → 启动今日日记，继承昨日未完成
/capture <主题>           → 快速捕获到相关笔记
/capture <主题> <内容>    → 捕获指定内容
/review                   → 生成周回顾（默认）
/review daily             → 生成日回顾
/review weekly            → 生成周回顾
/review monthly           → 生成月回顾
```

---

## 🆘 帮助命令

当用户输入以下内容时，显示帮助信息：

- `obsidian help`
- `obsidian 帮助`
- `/daily help`
- `怎么用 obsidian helper`

显示内容：

```
📖 Obsidian Helper 使用指南

🗓️ /daily - 智能日记
   自动创建今日日记，继承昨日未完成任务

📝 /capture <主题> [内容] - 知识捕获
   快速记录想法到相关笔记
   示例：/capture API设计 REST要用名词

📊 /review [weekly|monthly] - 周期回顾
   自动分析笔记，生成回顾报告

⚙️ 配置问题？
   输入「配置 obsidian」查看 MCP 配置指南
```

---

*Obsidian Helper v1.1.0 - 让笔记更智能*
