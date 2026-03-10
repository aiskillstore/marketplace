---
name: sql-queries-tool
description: Expert SQL query generation for DBX Studio. Use when writing, optimizing, or debugging SQL queries against user database connections.
---

# SQL Query Expert — DBX Studio

This project supports multiple database backends via user connections. Always write dialect-appropriate SQL.

## Supported Dialects

| Dialect | Provider |
|---------|----------|
| PostgreSQL | Default / Railway |
| Snowflake | Via MCP connector |
| BigQuery | Via MCP connector |
| Databricks | Via MCP connector |
| MySQL | Via connection string |
| SQLite | Via connection string |

## Query Patterns

### Safe SELECT with limit
Always add LIMIT unless the user explicitly wants all rows:
```sql
SELECT * FROM "schema"."table" LIMIT 100;
```

### CTEs for complex queries
```sql
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY created_at DESC) AS rn
  FROM orders
)
SELECT * FROM ranked WHERE rn = 1;
```

### Aggregations
```sql
SELECT
  DATE_TRUNC('month', created_at) AS month,
  COUNT(*) AS total,
  SUM(amount) AS revenue
FROM orders
GROUP BY 1
ORDER BY 1 DESC;
```

### Window Functions
```sql
SELECT
  user_id,
  amount,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY created_at) AS running_total
FROM transactions;
```

## Tool Usage in DBX Studio AI

The AI has access to these tools — always use them rather than guessing:

| Tool | When to Use |
|------|-------------|
| `read_schema` | First call — understand table structure |
| `get_table_data` | Preview rows before writing complex queries |
| `execute_query` | Run SELECT queries (SELECT/WITH only) |
| `describe_table` | Get column details, FK relationships |
| `get_table_stats` | Row counts, distributions |
| `generate_chart` | Visualize query results |

## Query Safety Rules
- Only SELECT and WITH (CTEs) are permitted via `execute_query`
- Always quote identifiers: `"schema"."table"."column"`
- Add LIMIT automatically unless the user asks for all data
- Validate table/column names exist via `read_schema` or `describe_table` first

## Response Format
1. Execute tool to get data
2. Answer the user's question directly with the result
3. Show SQL in ```sql blocks only if the user asks "how" or "show me the query"
4. Present numbers clearly: "There are **1,247 orders** this month"
