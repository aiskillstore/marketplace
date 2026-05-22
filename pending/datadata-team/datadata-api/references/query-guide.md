# 查询指南

通过 `execute-adhoc` 执行只读查询时，必须遵循以下 SQL 编写约定。

## 查询引擎

- 默认 `duckdb`；仅当针对 ClickHouse 数据源时切换为 `clickhouse`
- `duckdb` 查询使用 DuckDB SQL；`clickhouse` 查询使用 ClickHouse SQL
- ClickHouse 数据源不支持跨数据源关联

## 数据源绑定

- 格式：`--datasource "DATASOURCE_ID:ATTACH_ALIAS"`，可重复使用
- SQL 中通过别名而非 datasource ID 引用表
- **例外**：`ducklake` 类型数据源忽略别名 — 始终使用 datasource 自身的 `name` 作为 schema。通过 `get-datasource-info` 获取。

## 表命名

在 SQL 中引用表的方式取决于数据源的**类型**。在编写 SQL 前，务必通过 `get-datasource-info` 检查数据源类型，以使用正确的命名模式。

### Ducklake 数据源（类型 `ducklake`）

Datadata 管理的基于 DuckDB 的 data-spaces。catalog 名固定为 `ducklake`。datasource 自身的 `name`（来自 `get-datasource-info`）用作 schema — **不支持自定义别名**。schema 层级不超过 datasource 名：

```txt
ducklake.{datasourceName}.{tableName}
```

通过 `get-datasource-info` 获得 datasource 名，在 SQL 和 `--datasource "ID:NAME"` 绑定中使用。表管理操作详见 [data-spaces.md](./data-spaces.md)。

### 数据库数据源（MySQL、PostgreSQL、DuckDB、SQLite、ClickHouse 等）

别名变成数据库名。表存放在该数据库中的 schema：

```txt
attachAlias.schemaName.tableName
```

### 文件数据源（CSV、JSON、Parquet 等）

每个附加文件在 DuckDB 内置 `memory` 数据库的 `main` schema 中变成一个表。别名是表名：

```txt
memory.main.attachAlias
```

### 简化名称（仅文件数据源）

文件数据源挂载后表名即为别名，可使用简化名：

- `memory.main.sales` → 仅 `sales`（当所有数据源中没有其他同名表时）
- 用 `*` 从简化名引用所有列：`SELECT * FROM sales`

> 数据库数据源（MySQL、PostgreSQL 等）不支持简化名称，必须使用全限定名 `attachAlias.schemaName.tableName`。

## 标识符引用

始终引用可能与 SQL 关键字冲突的标识符（表名、列名、别名）。标准 SQL 标识符使用双引号，MySQL 兼容语法使用反引号。不确定时，引用所有标识符 — 这是无害的，防止列名恰好为保留字时的微妙崩溃（如 `"from"`、`"order"`、`"group"`、`"select"`、`"user"`、`"status"`、`"key"`）。

```sql
-- 好：引用的标识符
SELECT "id", "name", "status" FROM "sales" WHERE "order" = 'abc'

-- 不好：未引用的 "status" 和 "order" 可能与保留字冲突
SELECT id, name, status FROM sales WHERE order = 'abc'
```

## 安全性

- `execute-adhoc` 是**只读的**。不要用它执行 INSERT、UPDATE、DELETE、DROP、ALTER 或任何修改数据的 SQL
- 仅 `insert-rows` API / 子命令可以插入数据 — 支持**批量插入**
- 未明确要求时不要运行破坏性 SQL
- 不要默默改写业务逻辑 SQL

## 结果处理

`execute-adhoc` 执行后通过 `get-execution-result` 获取结果：

- 不要将完整的大数据集发送到 model context — 保存到文件，本地搜索，总结摘要
- 报告文件路径、格式和 execution ID 以便重用
