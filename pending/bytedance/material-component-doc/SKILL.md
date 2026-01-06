---
name: material-component-doc
description: 用于 FlowGram 物料库组件文档撰写的专用技能，提供组件文档生成、Story 创建、翻译等功能的指导和自动化支持
metadata:
  version: "1.1.0"
  category: "documentation"
  language: "zh-CN"
  framework: "FlowGram"
---

# FlowGram 文档的组织结构

- **英文文档**: `apps/docs/src/en`
- **中文文档**: `apps/docs/src/zh`
- **Story 组件**: `apps/docs/components/form-materials/components`
- **物料源码**: `packages/materials/form-materials/src/components`
- **文档模板**: `./templates/material.mdx`

# 组件物料文档撰写流程

## 1. 源码定位

在 `packages/materials/form-materials/src/components` 目录下确认物料源代码地址。

**操作**：
- 使用 Glob 工具搜索物料文件
- 确认目录结构（是否有 hooks.ts, context.tsx 等）
- 记录导出名称和文件路径

## 2. 需求收集

向用户询问物料使用实例和具体需求。

**收集信息**：
- 主要使用场景
- 典型代码示例（1-2 个）
- 特殊配置或高级用法
- 是否需要配图

## 3. 功能分析

深入阅读源代码，理解物料功能。

**分析要点**：
- Props 接口（类型、默认值、描述）
- 核心功能和实现方式
- 依赖关系（FlowGram API、其他物料、第三方库）
- Hooks 和 Context
- 特殊逻辑（条件渲染、副作用等）

## 4. Story 创建

在 `apps/docs/components/form-materials/components` 下创建 Story 组件（详见下方 Story 规范）。

## 5. 文档撰写

基于模板 `./templates/material.mdx` 撰写完整文档。

**文档位置**：
- 中文：`apps/docs/src/zh/materials/components/{物料名称}.mdx`
- 英文：`apps/docs/src/en/materials/components/{物料名称}.mdx`（翻译后）

## 6. 质量检查

**检查清单**：
- [ ] Story 组件能正常运行
- [ ] 代码示例准确无误
- [ ] API 表格完整
- [ ] 依赖链接正确可访问
- [ ] 图片路径正确
- [ ] Mermaid 流程图语法正确
- [ ] CLI 命令路径准确

**用户确认中文文档的撰写后，再执行翻译**。
**用户确认中文文档的撰写后，再执行翻译**。
**用户确认中文文档的撰写后，再执行翻译**。
---

# Story 组件规范

> **参考示例**: `apps/docs/components/form-materials/components/variable-selector.tsx`

## 命名规范

**文件命名**: kebab-case，与物料名称一致
- ✅ `variable-selector.tsx`
- ✅ `dynamic-value-input.tsx`
- ❌ `VariableSelector.tsx`

**Story 导出命名**: PascalCase + "Story" 后缀
- `BasicStory` - 基础使用（必需）
- `WithSchemaStory` - 带 Schema 约束
- `DisabledStory` - 禁用状态
- `CustomFilterStory` - 自定义过滤
- 根据物料特性命名，见名知意

## 代码要求

### 1. 懒加载导入

```tsx
// ✅ 正确
const VariableSelector = React.lazy(() =>
  import('@flowgram.ai/form-materials').then((module) => ({
    default: module.VariableSelector,
  }))
);

// ❌ 错误
import { VariableSelector } from '@flowgram.ai/form-materials';
```

### 2. 包装组件

```tsx
// ✅ 正确
export const BasicStory = () => (
  <FreeFormMetaStoryBuilder
    filterEndNode
    formMeta={{
      render: () => (
        <>
          <FormHeader />
          <Field<string[]> name="variable_selector">
            {({ field }) => (
              <VariableSelector
                value={field.value}
                onChange={(value) => field.onChange(value)}
              />
            )}
          </Field>
        </>
      ),
    }}
  />
);

// ❌ 错误：缺少包装
export const BasicStory = () => (
  <VariableSelector value={[]} onChange={() => {}} />
);
```

### 3. 类型标注

```tsx
// ✅ 正确
<Field<string[] | undefined> name="variable_selector">

// ❌ 错误
<Field<any> name="variable_selector">
```

### 4. 语言规范

代码和注释只使用英文，无中文。

## 完整示例

```tsx
/**
 * Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
 * SPDX-License-Identifier: MIT
 */

import React from 'react';
import { Field } from '@flowgram.ai/free-layout-editor';
import { FreeFormMetaStoryBuilder, FormHeader } from '../../free-form-meta-story-builder';

const VariableSelector = React.lazy(() =>
  import('@flowgram.ai/form-materials').then((module) => ({
    default: module.VariableSelector,
  }))
);

export const BasicStory = () => (
  <FreeFormMetaStoryBuilder
    filterEndNode
    formMeta={{
      render: () => (
        <>
          <FormHeader />
          <Field<string[] | undefined> name="variable_selector">
            {({ field }) => (
              <VariableSelector
                value={field.value}
                onChange={(value) => field.onChange(value)}
              />
            )}
          </Field>
        </>
      ),
    }}
  />
);

export const FilterSchemaStory = () => (
  <FreeFormMetaStoryBuilder
    filterEndNode
    formMeta={{
      render: () => (
        <>
          <FormHeader />
          <Field<string[] | undefined> name="variable_selector">
            {({ field }) => (
              <VariableSelector
                value={field.value}
                onChange={(value) => field.onChange(value)}
                includeSchema={{ type: 'string' }}
              />
            )}
          </Field>
        </>
      ),
    }}
  />
);
```

---

# 物料文档格式

## 使用模板

**模板文件**: `./templates/material.mdx`

文档必须严格按照模板格式编写，包含以下章节：
1. Import 语句
2. 标题和简介（带可选配图）
3. 案例演示（基本使用 + 高级用法）
4. API 参考（Props 表格）
5. 源码导读（目录结构、核心实现、流程图、依赖梳理）

## 参考示例

- [`dynamic-value-input.mdx`](apps/docs/src/zh/materials/components/dynamic-value-input.mdx) - 完整的流程图和依赖说明
- [`variable-selector.mdx`](apps/docs/src/zh/materials/components/variable-selector.mdx) - 多个 API 表格和警告提示

## 关键注意事项

**API 表格要求**：
- 必须包含所有公开的 Props
- 类型使用反引号（如 \`string\`）
- 描述清晰简洁
- 多个相关类型分开列表

**源码导读要求**：
- 目录结构：展示文件列表及说明
- 核心实现：用代码片段说明关键逻辑
- 整体流程：Mermaid 流程图（推荐）
- 依赖梳理：分类列出 FlowGram API、其他物料、第三方库

---

# 图片处理指南

## 截图要求

1. **时机**: Story 组件完成后，运行 docs 站点截图
2. **内容**: 捕获物料的典型使用状态，清晰可见
3. **格式**: PNG，适当压缩

## 命名和存储

- **命名**: `{物料名称}.png`（kebab-case）
- **存储**: `apps/docs/src/public/materials/{物料名称}.png`
- **引用**: `/materials/{物料名称}.png`

## 在文档中使用

```mdx
<br />
<div>
  <img loading="lazy" src="/materials/{物料名称}.png" alt="{物料名称} 组件" style={{ width: '50%' }} />
</div>
```

---

# 翻译流程

## 翻译时机

- ✅ 用户明确要求翻译
- ✅ 中文文档已经用户审核确认
- ❌ 文档还在修改中
- ❌ 用户未确认最终版本

## 翻译原则

**术语一致性**：
- ComponentName → ComponentName（组件名不翻译）
- Props、Hook、Schema 等术语保持原文

**代码不翻译**：
- 所有代码块、命令、路径保持原样

**链接处理**：
- 内部链接：`/zh/` → `/en/`
- 外部链接和 GitHub 链接：保持不变

**格式保持**：
- Markdown 格式、缩进、空行完全一致

## 翻译检查清单

- [ ] 标题和描述已翻译
- [ ] 代码示例未被翻译
- [ ] 命令和路径保持原样
- [ ] 内部文档链接已更新
- [ ] API 表格描述列已翻译
- [ ] Mermaid 图中文节点已翻译
- [ ] 术语使用一致

---

# 最佳实践

## Props 提取技巧

1. 查找 `interface` 或 `type` 定义
2. 检查组件函数参数类型
3. 查找 `defaultProps` 确认默认值
4. 阅读 JSDoc 提取描述

## 依赖分析方法

1. 查看 import 语句（直接依赖）
2. 分析 Hook 调用（FlowGram API）
3. 查找组件引用（其他物料）
4. 检查 package.json（第三方库）

## Mermaid 流程图建议

1. 简洁明了，关注核心流程
2. 使用时序图绘制

## 常见错误避免

❌ 直接导入物料而不使用 `React.lazy`
❌ API 表格遗漏 Props
❌ 依赖链接失效
❌ 中英文混用
❌ 路径格式错误

✅ 参考优秀示例
✅ 仔细阅读源码
✅ 验证所有链接
✅ 保持语言和格式一致
✅ 使用项目约定的路径格式

---

# 相关工具和资源

## 开发命令

```bash
# 启动文档站点
rush dev:docs

# 查看修改
git diff
git diff --cached
```

## 关键目录

| 目录 | 说明 |
|------|------|
| `packages/materials/form-materials/src/components` | 物料源码 |
| `apps/docs/src/zh/materials/components` | 中文文档 |
| `apps/docs/src/en/materials/components` | 英文文档 |
| `apps/docs/components/form-materials/components` | Story 组件 |
| `apps/docs/src/public/materials` | 图片资源 |
| `./templates` | 文档模板 |

