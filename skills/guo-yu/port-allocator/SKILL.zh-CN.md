---
name: port-allocator
description: 自动分配端口、自动分配和管理开发服务器端口，避免多个 Claude Code 实例之间的端口冲突
---

# Port Allocator

智能端口分配器，只为包含 `package.json` 的真实项目分配端口。

## 使用方法

| 命令 | 说明 |
|------|------|
| `/port-allocator` | 为当前项目分配/查询端口 |
| `/port-allocator list` | 列出所有已分配的端口 |
| `/port-allocator scan` | 扫描代码目录，发现新项目并分配端口 |
| `/port-allocator config <path>` | 设置代码主目录路径 |
| `/port-allocator add <目录路径>` | 手动添加项目的端口分配 |
| `/port-allocator allow` | 配置 Claude Code 权限，允许本 skill 的常用命令 |

## ⚠️ 重要规则

### 1. 服务重启时只操作本项目端口

当需要重启开发服务器时，**只能杀掉当前项目端口范围内的进程**，绝不能影响其他端口：

```bash
# ✅ 正确：只杀当前项目端口 (例如 3000-3009)
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# ❌ 错误：杀掉所有 node 进程或其他端口
pkill -f node  # 会影响其他项目！
lsof -ti:3010 | xargs kill  # 这是其他项目的端口！
```

### 2. 更新 CLAUDE.md 时追加而非覆盖

更新 `~/.claude/CLAUDE.md` 时，**必须保留用户原有内容**：

```bash
# ✅ 正确：检查并追加或更新特定章节
# ❌ 错误：直接覆盖整个文件
```

## 执行步骤

### 命令: `/port-allocator allow`

配置 Claude Code 允许本 skill 执行的命令，避免每次都要手动确认：

1. 读取 `~/.claude/settings.json`（如果存在）
2. 合并以下命令到 `permissions.allow` 数组（保留现有配置）：

```json
{
  "permissions": {
    "allow": [
      "Bash(ls -d *)",
      "Bash(find * -maxdepth * -name package.json *)",
      "Bash(cat ~/.claude/*)",
      "Bash(dirname *)",
      "Bash(lsof -i:3*)",
      "Bash(lsof -ti:3*)"
    ]
  }
}
```

3. 写入更新后的 settings.json
4. 输出已添加的权限列表

**输出格式：**
```
✅ 已配置 Claude Code 权限

新增允许的命令模式：
  - Bash(ls -d *)
  - Bash(find * -maxdepth * -name package.json *)
  - Bash(cat ~/.claude/*)
  - Bash(lsof -i:3*)
  - Bash(lsof -ti:3*)

配置文件: ~/.claude/settings.json
```

### 命令: `/port-allocator config <path>`

设置用户的代码主目录：

1. **验证路径是否存在**（必须！不存在则报错并退出）
2. 更新 `~/.claude/port-registry.json` 中的 `code_root` 字段
3. 输出确认信息

### 首次运行：自动检测

首次运行时（`~/.claude/port-registry.json` 不存在或没有 `code_root`），自动检测代码目录：

```bash
# 检查常见的代码目录
for dir in ~/Codes ~/Code ~/Projects ~/Dev ~/Development ~/repos; do
  if [ -d "$dir" ]; then
    CODE_ROOT="$dir"
    break
  fi
done

# 如果都不存在，默认使用 ~/Codes
CODE_ROOT="${CODE_ROOT:-~/Codes}"
```

**自动检测输出：**
```
首次运行，检测代码目录中...

检测到代码目录: ~/Codes

端口注册表已初始化: ~/.claude/port-registry.json

如需更改，请使用:
   /port-allocator config ~/your/code/path
```

**未找到目录时：**
```
无法自动检测代码目录

请手动配置:
   /port-allocator config ~/your/code/path

常见位置:
   ~/Codes, ~/Code, ~/Projects, ~/Dev
```

### 命令: `/port-allocator scan`

扫描代码目录，自动发现并注册项目：

1. 读取 `~/.claude/port-registry.json` 获取 `code_root`
   - 如果配置不存在，先执行自动检测
   - 如果 `code_root` 目录不存在，提示用户配置
2. 查找所有包含 `package.json` 的目录（精确到 package.json 所在位置）：

```bash
# 查找所有 package.json，排除构建产物目录
find <code_root> -maxdepth 3 -name "package.json" -type f \
  -not -path "*/.next/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" | while read pkg; do
  dirname "$pkg"
done
```

3. **重要**：路径必须精确到 `package.json` 所在目录
   - ✅ 正确：`~/Codes/chekusu/landing`
   - ❌ 错误：`~/Codes/chekusu`（如果 package.json 在子目录）

4. 对于每个发现的项目目录：
   - 检查是否已在注册表中
   - 如果不存在，分配下一个可用端口段
5. 更新配置文件（**追加模式**，不覆盖用户内容）
6. 输出扫描结果摘要

### 命令: `/port-allocator` (默认)

为当前项目分配/查询端口：

1. 获取当前工作目录
2. 读取配置获取 `code_root` 和已分配端口
3. 匹配当前目录对应的项目
4. 如果没有 `package.json`，提示这不是需要端口的项目
5. 如果有，检查是否已分配端口，未分配则自动分配
6. 输出端口信息

### 命令: `/port-allocator list`

列出所有已分配的端口（只读操作）。

## 输出格式

### 端口信息
```
📦 项目目录: ~/Codes/chekusu/landing
📄 package.json: ✓ 已检测到
🔌 端口范围: 3000-3009
   - 主应用: 3000
   - API: 3001
   - 其他服务: 3002-3009

⚠️ 重启服务时只能操作 3000-3009 端口！
```

### 扫描结果
```
🔍 扫描完成: ~/Codes

✅ 已注册项目 (N个):
   - chekusu/landing: 3000-3009
   - saifuri: 3010-3019

🆕 新发现项目 (M个):
   - new-project: 3090-3099 (新分配)

⏭️ 跳过 (K个):
   - .next, node_modules (构建产物)
   - research-folder (无 package.json)
```

## 端口分配规则

- 每个项目分配 **10 个连续端口**
- 起始端口：3000
- 间隔：10
- `x0`: 主应用（如 3000, 3010, 3020）
- `x1`: API 服务（如 3001, 3011, 3021）
- `x2-x9`: 其他服务（数据库、缓存等）

## 配置文件

- **端口注册表**: `~/.claude/port-registry.json`
- **全局说明**: `~/.claude/CLAUDE.md`（追加模式更新）
- **Claude Code 设置**: `~/.claude/settings.json`（存放 allowedCommands）
- **跳过模式**: `.next`, `node_modules`, `dist`, `build`

## 注意事项

1. **只操作本项目端口** - 重启服务时绝不影响其他项目
2. **追加而非覆盖** - 更新配置文件时保留用户原有内容
3. **路径精确** - 指向 package.json 实际所在目录
4. **跳过构建产物** - .next、node_modules 等不分配端口
5. **首次使用** - 建议先运行 `/port-allocator allow` 配置权限
