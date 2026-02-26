---
type: project-doc
project: "{{project_name}}"
source: "{{project_path}}"
language: {{language}}
framework: {{framework}}
tags: [project, {{project_type}}]
created: {{date}}
---

# {{project_name}} 知识库

> {{description}}

## 🚀 快速导航

- [[01-快速开始|快速开始]] - 安装与运行
- [[02-架构设计/整体架构|架构设计]] - 系统设计
- [[03-API文档/_API索引|API 文档]] - 接口参考
- [[04-模块说明/_模块索引|模块说明]] - 核心代码

## 📊 项目信息

| 属性 | 值 |
|------|-----|
| 语言 | {{language}} |
| 框架 | {{framework}} |
| 版本 | {{version}} |
| 仓库 | {{repository}} |

## 🗂️ 目录结构

```
{{directory_tree}}
```

## 📦 主要依赖

{{dependencies}}

## 📑 模块索引

```dataview
TABLE WITHOUT ID
  file.link as "模块",
  type as "类型"
FROM "{{vault_path}}"
WHERE project = "{{project_name}}" AND type = "module"
SORT file.name ASC
```

## 🔌 API 端点

```dataview
TABLE WITHOUT ID
  file.link as "API",
  endpoint as "端点",
  method as "方法"
FROM "{{vault_path}}"
WHERE project = "{{project_name}}" AND type = "api"
SORT endpoint ASC
```

## 📅 最近修改

```dataview
LIST
FROM "{{vault_path}}"
WHERE project = "{{project_name}}"
SORT file.mtime DESC
LIMIT 10
```

## 🔗 相关链接

{{related_links}}

---
*由 project-to-obsidian 自动生成 | {{generated_at}}*
*人工审核后可移动到 30_Resources/Projects/*
