# Obsidian Helper

Obsidian 智能助手 - 让 Claude Code 与你的 Obsidian 知识库深度整合。

## 功能特性

| 命令 | 功能 | 说明 |
|------|------|------|
| `/daily` | 智能日记 | 自动创建今日日记，继承昨日未完成任务 |
| `/capture <主题> [内容]` | 知识捕获 | 快速记录想法，智能匹配现有笔记 |
| `/review [weekly\|monthly]` | 周期回顾 | 分析笔记数据，生成回顾报告 |

## 安装

### 方式一：直接复制

```bash
# 克隆到 Claude Code skills 目录
git clone https://github.com/YOUR_USERNAME/obsidian-helper.git ~/.claude/skills/obsidian-helper
```

### 方式二：手动下载

1. 下载本仓库
2. 将 `obsidian-helper` 文件夹复制到 `~/.claude/skills/`

## 首次使用

**无需手动配置！** 首次使用任何命令时，skill 会自动检测 MCP 连接状态：

- ✅ 已配置：直接执行功能
- ❌ 未配置：自动显示中文配置引导

### 配置引导预览

当检测到未配置时，会显示：

```
检测到 Obsidian MCP 未连接，我来帮你配置！

第一步：安装 Obsidian 插件
1. 打开 Obsidian → 设置 → 第三方插件
2. 搜索并安装 Local REST API
3. 启用插件

第二步：获取 API Key
...

第三步：配置 Claude Code MCP
...
```

## 使用示例

```bash
# 开始今日日记
/daily

# 或者用中文
开始今日日记

# 快速捕获知识
/capture API设计 RESTful API 应该使用名词而非动词

# 生成周回顾
/review weekly

# 查看帮助
obsidian 帮助
```

## 文件结构

```
obsidian-helper/
├── .claude-plugin/
│   └── marketplace.json    # 插件配置
├── templates/
│   ├── daily-template.md   # 日记模板
│   ├── weekly-review-template.md
│   └── monthly-review-template.md
├── references/
│   └── mcp-tools-reference.md
├── SKILL.md                # 核心技能定义
└── README.md
```

## 自定义配置

在 Obsidian 库中创建 `_config/obsidian-helper.md` 可自定义设置：

```markdown
# Obsidian Helper 配置

## 日记设置
- 日记文件夹: Daily Notes/
- 日记格式: YYYY-MM-DD

## 捕获设置
- 默认捕获文件夹: Resources/
- 自动添加时间戳: true

## 回顾设置
- 默认回顾周期: weekly
- 回顾保存位置: Daily Notes/
```

## 依赖

- Obsidian 1.0.0+
- Obsidian 插件：[Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api)
- MCP：[mcp-obsidian](https://www.npmjs.com/package/mcp-obsidian)

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| MCP 连接失败 | 确保 Obsidian 正在运行且 Local REST API 已启用 |
| API Key 无效 | 在插件设置中重新复制 Key |
| 日记位置不对 | 在 `_config/obsidian-helper.md` 中配置路径 |

## License

MIT

---

*Obsidian Helper v1.1.0*
