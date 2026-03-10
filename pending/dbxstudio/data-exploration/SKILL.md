---
name: data-exploration
description: Systematic database and table profiling for DBX Studio. Use when a user wants to understand their data, explore schema structure, or profile a dataset.
---

# Data Exploration — DBX Studio

## Exploration Workflow

### Phase 1: Schema Discovery
Start with `read_schema` to list all tables, then `describe_table` for each table of interest.

```
1. read_schema(schema_name: "public")
2. describe_table(table_name: "<each table>")
3. get_table_stats(table_name: "<table>")
```

### Phase 2: Table Profiling
For each table, gather:
- Row count
- Column names and types
- Sample data via `get_table_data`
- Null counts and distributions

### Phase 3: Relationship Discovery
Look for foreign key patterns:
- Columns named `*_id` linking to other tables
- Common join patterns: `users.id → orders.user_id`

## Quality Scoring

| Score | Completeness |
|-------|-------------|
| Green | > 95% populated |
| Yellow | 80–95% populated |
| Orange | 50–80% populated |
| Red | < 50% populated |

## Common Exploration Queries

### Row count
```sql
SELECT COUNT(*) AS row_count FROM "public"."table_name";
```

### Column null rates
```sql
SELECT
  COUNT(*) AS total,
  COUNT(column_name) AS non_null,
  ROUND(100.0 * COUNT(column_name) / COUNT(*), 2) AS pct_filled
FROM "public"."table_name";
```

### Distinct values
```sql
SELECT column_name, COUNT(*) AS frequency
FROM "public"."table_name"
GROUP BY 1
ORDER BY 2 DESC
LIMIT 20;
```

### Date range
```sql
SELECT MIN(created_at), MAX(created_at) FROM "public"."table_name";
```

## Output Format
After exploration, present a structured summary:
- **Tables**: list with row counts
- **Key relationships**: how tables connect
- **Data quality flags**: any columns with high null rates
- **Suggested next queries**: what the user might want to know next
