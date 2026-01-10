---
name: fractal-docs-generator
description: 目录级 CLAUDE.md 生成。触发：mkdir、create directory、目录结构变更。
---

# 分形文档生成器

触发：创建/移动/重命名目录，目录内文件变化。

## 模板

```markdown
<!-- 若此目录变更，立即更新本文件 -->
# {目录名} - {一句话定位}

| 文件 | 地位 | 职责 |
|------|------|------|
| foo.ts | 入口 | 对外唯一接口 |
```

## 地位

| 地位 | 典型文件 |
|------|----------|
| 入口 | index.ts, main.ts |
| 核心 | service.ts, engine.ts |
| 辅助 | utils.ts, helpers.ts |
| 类型 | types.ts |
| 配置 | config.ts |
| 测试 | *.test.ts |

## 示例

```markdown
<!-- 若此目录变更，立即更新本文件 -->
# auth - 认证授权

| 文件 | 地位 | 职责 |
|------|------|------|
| index.ts | 入口 | 导出 AuthService |
| auth.service.ts | 核心 | 登录、令牌刷新 |
| jwt.helper.ts | 辅助 | JWT 签发验证 |
```

协作：本 skill 管目录，file-header-guardian 管文件。
