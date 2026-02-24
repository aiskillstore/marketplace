# Project to Obsidian

将代码项目转换为结构化的 Obsidian 知识库。

## 功能

- 自动分析项目结构和代码
- 生成完整的 Obsidian 文档体系
- 支持多种语言和框架
- 与 Obsidian MCP 深度集成

## 使用

```bash
# 完整转换
/p2o /path/to/project

# 快速概览
/p2o /path/to/project --quick

# 只生成 API 文档
/p2o /path/to/project --api

# 只生成架构文档
/p2o /path/to/project --arch
```

## 生成内容

```
{{项目名}}-知识库/
├── 00-项目概览.md          # MOC 主入口
├── 01-快速开始.md          # 安装运行指南
├── 02-架构设计/
│   ├── 整体架构.md
│   ├── 目录结构.md
│   └── 技术栈.md
├── 03-API文档/
│   ├── _API索引.md
│   └── [各API端点].md
├── 04-模块说明/
│   ├── _模块索引.md
│   └── [各模块].md
├── 05-配置参考.md
└── 06-开发指南/
    ├── 本地开发.md
    ├── 测试指南.md
    └── 部署流程.md
```

## 支持的项目类型

| 语言 | 框架 |
|------|------|
| JavaScript/TypeScript | React, Vue, Angular, Express, Next.js |
| Python | FastAPI, Django, Flask |
| Go | Gin, Echo |
| Rust | Actix, Axum |
| Java | Spring Boot |

## 与其他 Skill 集成

生成的知识库可以直接使用 `obsidian-helper`：

```bash
/daily
→ 记录项目学习笔记

/capture 新发现
→ 补充项目文档

/review weekly
→ 回顾项目进展
```

## 安装

```bash
# 复制到 skills 目录
cp -r project-to-obsidian ~/.claude/skills/
```

## License

MIT
