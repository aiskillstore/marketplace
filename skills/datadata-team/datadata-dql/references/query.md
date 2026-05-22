# query 函数

> 完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

执行 SQL 查询并返回 DataFrame。支持参数化查询防止 SQL 注入。

```python
df = query(sql, *args)
```

**参数：**

- `sql` (str): SQL SELECT 查询
- `*args`: 查询参数，按顺序替换 SQL 中的 `?` 占位符

**返回值：** DataFrame 对象

**示例：**

```python
# 简单查询
df = query("SELECT * FROM users LIMIT 100")

# 参数化查询
df = query(
    "SELECT * FROM orders WHERE user_id = ? AND status = ?",
    12345,
    "completed"
)

# 复杂查询
df = query("""
    SELECT
        u.id, u.name, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.created_at > ?
    GROUP BY u.id, u.name
    ORDER BY order_count DESC
""", "2024-01-01")
```

## 实用示例

### 月度对比分析

```python
# 场景：对比当前月份与上个月的营收

now = time.localtime()
current_month = now.tm_mon
current_year = now.tm_year

# 获取上个月
if current_month == 1:
    prev_month = 12
    prev_year = current_year - 1
else:
    prev_month = current_month - 1
    prev_year = current_year

# 当月数据
current_data = query("""
    SELECT SUM(amount) as revenue, COUNT(*) as orders
    FROM orders
    WHERE MONTH(created_at) = ? AND YEAR(created_at) = ?
""", current_month, current_year)

# 上月数据
previous_data = query("""
    SELECT SUM(amount) as revenue, COUNT(*) as orders
    FROM orders
    WHERE MONTH(created_at) = ? AND YEAR(created_at) = ?
""", prev_month, prev_year)

# 计算增长率
current_revenue = current_data['revenue'].max()
prev_revenue = previous_data['revenue'].max()
growth = (current_revenue - prev_revenue) / prev_revenue * 100 if prev_revenue > 0 else 0

return {
    'current_month': current_revenue,
    'previous_month': prev_revenue,
    'growth_percent': round(growth, 2)
}
```

### 每日活跃用户统计

```python
# 场景：统计每日活跃用户数，判断趋势
df = query("""
    SELECT
        DATE(created_at) as day,
        COUNT(DISTINCT user_id) as active_users,
        COUNT(*) as total_events
    FROM events
    WHERE created_at > '2024-01-01'
    GROUP BY DATE(created_at)
    ORDER BY day DESC
""")

df['user_trend'] = df['active_users'].map(lambda x: 'up' if x > 100 else 'down')
return df.head(30)
```
