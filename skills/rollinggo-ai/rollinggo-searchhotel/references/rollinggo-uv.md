# RollingGo UV 参考文件

> 本文件适用于 uv / uvx / Python 执行环境。
> 酒店搜索逻辑与筛选规则 → 请查阅 `SKILL.md`。

## 目录

1. [运行方式](#运行方式)
2. [版本新鲜度](#版本新鲜度)
3. [API Key 配置](#api-key-配置)
4. [命令说明](#命令说明)
5. [端到端工作流](#端到端工作流)
6. [问题排查](#问题排查)
7. [本地开发](#本地开发)

---

## 运行方式

### 临时执行（uvx — 无需安装）

> 注意：包名和命令名都叫 `rollinggo`，所以需要 `--from` 语法。
> 显式使用 `rollinggo@latest`，让 uv 解析当前最新发布版本。

```bash
uvx --refresh --from rollinggo@latest rollinggo --help
uvx --refresh --from rollinggo@latest rollinggo search-hotels \
  --origin-query "查找东京迪士尼附近的酒店" \
  --place "东京迪士尼" --place-type "<查看 --help 获取合法值>"
```

### 安装为工具（适合长期高频使用）

```bash
uv tool install rollinggo@latest
uv tool upgrade rollinggo@latest
rollinggo --help

# 如果安装后终端找不到命令：
uv tool update-shell
```

### 本地源码模式（仓库内开发）

```bash
uv run --directory rollinggo-uv rollinggo --help
uv run --directory rollinggo-uv rollinggo search-hotels --help
```

---

## 版本新鲜度

本参考默认规则：每次执行都使用 PyPI 最新发布版本。命令模式如下：

```bash
uvx --refresh --from rollinggo@latest rollinggo <子命令> ...
```

如果使用已安装工具，先升级再运行：

```bash
uv tool upgrade rollinggo@latest
```

---

## API Key 配置

解析顺序：`--api-key` 参数 → `RollingGo_API_KEY` 环境变量。

```bash
# Bash / zsh
export RollingGo_API_KEY="YOUR_API_KEY"

# PowerShell
$env:RollingGo_API_KEY="YOUR_API_KEY"

# 单条命令临时指定
rollinggo hotel-tags --api-key YOUR_API_KEY
```

宿主经常丢失 `RollingGo_API_KEY` 时，见 [claw-host-env.md](claw-host-env.md)。

申请 Key：https://mcp.agentichotel.cn/apply

---

## 命令说明

为了便于阅读，下面示例默认使用已安装的 `rollinggo` 命令。本参考的“最新版默认前缀”为 `uvx --refresh --from rollinggo@latest rollinggo`。

### `search-hotels`

必填：`--origin-query`、`--place`、`--place-type`

```bash
# 最简命令
rollinggo search-hotels \
  --origin-query "查找东京迪士尼附近的酒店" \
  --place "东京迪士尼" \
  --place-type "<查看 --help 获取合法值>"

# 带筛选条件
rollinggo search-hotels \
  --origin-query "上海迪士尼附近的亲子友好酒店" \
  --place "上海迪士尼" \
  --place-type "<查看 --help 获取合法值>" \
  --check-in-date 2026-04-01 --stay-nights 2 \
  --adult-count 2 --size 5 \
  --star-ratings 4.0,5.0 --max-price-per-night 800

# 表格可读模式（仅 search-hotels 支持）
rollinggo search-hotels --origin-query "东京的酒店" --place "东京" \
  --place-type "<查看 --help 获取合法值>" --format table
```

可选参数：`--country-code`、`--size`、`--check-in-date`、`--stay-nights`、`--adult-count`、`--distance-in-meter`、`--star-ratings min,max`、`--preferred-tag`、`--required-tag`、`--excluded-tag`、`--preferred-brand`、`--max-price-per-night`、`--min-room-size`、`--format json|table`

### `hotel-detail`

传入 `--hotel-id`（首选）或 `--name` 之一，不允许 `--format table`。

```bash
# 按 ID 查询，带日期和入住人数
rollinggo hotel-detail \
  --hotel-id 123456 \
  --check-in-date 2026-04-01 --check-out-date 2026-04-03 \
  --adult-count 2 --room-count 1

# 带儿童入住
rollinggo hotel-detail \
  --hotel-id 123456 \
  --check-in-date 2026-04-01 --check-out-date 2026-04-03 \
  --adult-count 2 --child-count 2 --child-age 4 --child-age 7 --room-count 1

# 按名称查询（模糊匹配）
rollinggo hotel-detail --name "东京丽思卡尔顿" \
  --check-in-date 2026-04-01 --check-out-date 2026-04-03
```

### `hotel-tags`

```bash
rollinggo hotel-tags
rollinggo hotel-tags --api-key YOUR_API_KEY

# 免安装临时执行
uvx --refresh --from rollinggo@latest rollinggo hotel-tags
```

返回的标签字符串需**原样**使用于 `--preferred-tag` / `--required-tag` / `--excluded-tag` 参数中。

---

## 端到端工作流

### 工作流 1：搜索 → 详情

```bash
# 第一步：搜索候选酒店
rollinggo search-hotels \
  --origin-query "上海迪士尼附近的酒店" \
  --place "上海迪士尼" --place-type "<查看 --help 获取合法值>" \
  --check-in-date 2026-04-01 --stay-nights 2 --size 3

# 第二步：从 JSON 提取 hotelId，然后查详情
rollinggo hotel-detail \
  --hotel-id <hotelId> \
  --check-in-date 2026-04-01 --check-out-date 2026-04-03 \
  --adult-count 2 --room-count 1
```

### 工作流 2：标签筛选搜索

```bash
# 第一步：获取标签库
rollinggo hotel-tags

# 第二步：用标签筛选搜索
rollinggo search-hotels \
  --origin-query "东京迪士尼附近含早餐的亲子酒店" \
  --place "东京迪士尼" --place-type "<查看 --help 获取合法值>" \
  --required-tag "早餐包含" --preferred-tag "亲子友好"
```

---

## 问题排查

- **`rollinggo: command not found`：** 使用 `uvx --refresh --from rollinggo@latest rollinggo ...` 或 `uv tool install rollinggo@latest && uv tool update-shell`
- **缺少 API Key 报错：** 传入 `--api-key`、设置 `RollingGo_API_KEY`，或者如果你跑在任何 claw 风格宿主里，就按 [claw-host-env.md](claw-host-env.md) 把同一个 key 注入到那个宿主的配置层
- **退出码 `2`（参数校验失败）：** 加 `--help` 重新运行，检查必填参数、日期格式、`--child-count` 与 `--child-age` 数量是否一致
- **没有返回任何酒店：** 移除 `--star-ratings` → 增大 `--size` 或 `--distance-in-meter` → 移除标签筛选
- **`hotel-detail` 无房型返回：** 这是正常业务结果，不是错误；尝试换其他酒店、换日期或调整入住人数

---

## 本地开发

```bash
# 从源码运行
uv run --directory rollinggo-uv rollinggo --help

# 运行测试
uv run --directory rollinggo-uv --extra dev python -m pytest

# 强制刷新本地源码的临时执行缓存
uvx --refresh --from . rollinggo --help
```

与 Node 版本的一致性验证：顶层帮助页、`search-hotels --help`、缺少必填参数时退出码为 `2`、`hotel-detail` / `hotel-tags` 仅输出 JSON、真实线上 API 调用成功。
