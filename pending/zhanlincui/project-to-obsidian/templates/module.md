---
tags: [module, {{category}}]
path: {{file_path}}
language: {{language}}
---

# {{module_name}}

> {{description}}

## 📍 位置

```
{{file_path}}
```

## 🎯 职责

{{responsibilities}}

## 📥 导入/依赖

```{{language}}
{{imports}}
```

## 🔧 核心函数/方法

{{#each functions}}
### `{{name}}`

{{description}}

**签名：**
```{{language}}
{{signature}}
```

**参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
{{params}}

**返回：**
- 类型: `{{return_type}}`
- 说明: {{return_description}}

**示例：**
```{{language}}
{{example}}
```

---
{{/each}}

## 📊 类/结构体

{{#each classes}}
### `{{name}}`

{{description}}

**属性：**
| 属性 | 类型 | 说明 |
|------|------|------|
{{properties}}

**方法：**
{{methods}}

---
{{/each}}

## 🔗 依赖关系

```mermaid
graph TD
    {{module_name}} --> {{dep1}}
    {{module_name}} --> {{dep2}}
    {{dep1}} --> {{subdep1}}
```

## 📎 被依赖

以下模块依赖本模块：
{{dependents}}

## 💡 设计说明

{{design_notes}}

## 相关模块

- [[{{related_1}}]]
- [[{{related_2}}]]

---
*返回 [[_模块索引|模块索引]]*
