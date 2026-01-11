---
name: file-header-guardian
description: 文件头三行契约注释。触发：create file、新建文件、编写代码。
---

# 文件头注释守护者

触发：创建代码文件，修改文件后检查头注释准确性。

## 模板

**TS/JS:**
```typescript
/**
 * @input  依赖什么
 * @output 提供什么
 * @pos    系统地位
 * ⚠️ 修改后同步：文件头 + 目录 CLAUDE.md
 */
```

**Python:**
```python
"""
@input  依赖什么
@output 提供什么
@pos    系统地位
⚠️ 修改后同步：文件头 + 目录 CLAUDE.md
"""
```

**Shell:**
```bash
# @input  依赖什么
# @output 提供什么
# @pos    系统地位
# ⚠️ 修改后同步：文件头 + 目录 CLAUDE.md
```

## 示例

```typescript
/**
 * @input  prisma.service 数据库连接
 * @output UserService: create/update/delete
 * @pos    用户模块核心
 * ⚠️ 修改后同步：文件头 + 目录 CLAUDE.md
 */
export class UserService { }
```

## 豁免

配置文件（json/yaml）、样式（css）、生成文件（*.d.ts）、node_modules。

协作：本 skill 管文件，fractal-docs-generator 管目录。
