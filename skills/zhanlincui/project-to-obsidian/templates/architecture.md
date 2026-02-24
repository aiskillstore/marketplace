---
tags: [architecture, design]
parent: "[[00-项目概览]]"
---

# 整体架构

## 📐 架构概览

{{architecture_summary}}

## 🏗️ 系统架构图

```mermaid
graph TB
    subgraph 客户端
        {{client_components}}
    end

    subgraph 服务端
        {{server_components}}
    end

    subgraph 数据层
        {{data_components}}
    end

    {{connections}}
```

## 📂 目录结构

```
{{directory_structure}}
```

### 目录说明

| 目录 | 用途 |
|------|------|
{{directory_descriptions}}

## 🔄 数据流

```mermaid
sequenceDiagram
    {{data_flow_diagram}}
```

## 🧩 核心组件

{{#each components}}
### {{name}}

- **职责**: {{responsibility}}
- **位置**: `{{path}}`
- **详情**: [[{{link}}]]

{{/each}}

## 🔌 外部依赖

| 服务/库 | 用途 | 版本 |
|---------|------|------|
{{external_dependencies}}

## 🔐 安全设计

{{security_design}}

## ⚡ 性能考虑

{{performance_notes}}

## 🚀 扩展性

{{scalability_notes}}

## 相关文档

- [[目录结构]]
- [[技术栈]]
- [[06-开发指南/部署流程|部署流程]]

---
*返回 [[00-项目概览|项目概览]]*
