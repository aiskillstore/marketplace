# DQL 最佳实践与调试

> 当脚本运行出错、性能不佳或遇到边界情况时查阅本文档。**日常编写脚本通常不需要阅读本文。**
>
> 完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

## 最佳实践

### 1. 使用参数化查询防止 SQL 注入

```python
# ❌ 不安全
user_id = user_input
df = query("SELECT * FROM users WHERE id = " + str(user_id))

# ✅ 安全
df = query("SELECT * FROM users WHERE id = ?", user_id)
```

### 2. 在 SQL 层过滤数据，而非 Python 层

```python
# ❌ 低效：获取所有数据再过滤
df = query("SELECT * FROM large_table")
df = df[df['amount'] > 100]

# ✅ 高效：在 SQL 中过滤
df = query("SELECT * FROM large_table WHERE amount > 100")
```

### 3. 使用 LIMIT 防止查询过大数据集

```python
# ✅ 规范做法
df = query("SELECT * FROM logs LIMIT 10000")

# ❌ 避免：可能查询太多数据
df = query("SELECT * FROM logs")
```

### 4. 检查数据存在性

```python
# ❌ 容易出错
df = query("SELECT * FROM users")
count = len(df['id'])  # 假设存在 id 列

# ✅ 更稳健
df = query("SELECT COUNT(*) as cnt FROM users")
if df and 'cnt' in df.columns:
    count = df['cnt'].max()
```

### 5. 为复杂计算添加注释

```python
# 计算客户生命周期价值 (CLV)
# 公式: CLV = 平均订单金额 × 年购买频率 × 客户生命期年数
# 用于评估客户价值和营销预算分配

avg_order = total_revenue / total_orders
annual_frequency = total_orders / days * 365
clv = avg_order * annual_frequency * customer_life_years
```

### 6. 验证外部数据

```python

response = fetch("https://api.example.com/data")

# 检查响应状态
if not response.ok:
    throw(f"API 返回错误: {response.status}")

# 验证响应格式
data = response.body
if data == None:
    throw("API returned empty response")

if "results" not in data:
    throw("Missing 'results' field in API response")
```

### 7. 使用描述性变量名

```python
# ❌ 不清晰
df1 = query("SELECT * FROM t1")
r = df1['c'].sum()
d = r / len(df1['c'])

# ✅ 清晰
sales_data = query("SELECT revenue FROM monthly_sales")
total_revenue = sales_data['revenue'].sum()
avg_revenue = total_revenue / sales_data['revenue'].count()
```

### 8. 处理边界情况

```python
df = query("SELECT revenue FROM sales WHERE date > ?", "2024-01-01")

# 处理空结果集
if df.empty:
    return {"status": "no_data", "count": 0}

# 处理除数为零
total = df['revenue'].sum()
count = df['revenue'].count()
avg = total / count if count > 0 else 0

return {"total": total, "count": count, "average": avg}
```

### 9. 优化 DataFrame 操作

```python
# ❌ 低效：多次迭代
df = query("SELECT id, amount FROM orders")
prices = df['amount']
doubled = prices.map(lambda x: x * 2)
rounded = doubled.map(lambda x: round(x, 2))

# ✅ 高效：合并操作
df = query("SELECT id, amount FROM orders")
prices = df['amount']
processed = prices.map(lambda x: round(x * 2, 2))
```

### 10. 使用时间函数处理日期

```python

# 获取当前时间
now = time.time()
local_time = time.localtime(now)

# 格式化输出
formatted = time.strftime("%Y-%m-%d %H:%M:%S", local_time)

# 解析输入
from_str = time.strptime("2024-01-01", "%Y-%m-%d")
timestamp = time.mktime(from_str)
```

## 性能优化建议

### 1. 适当使用 SQL 聚合

```python
# ❌ 低效：获取所有数据再聚合
df = query("SELECT amount FROM orders")
total = df['amount'].sum()

# ✅ 高效：在 SQL 中聚合
df = query("SELECT SUM(amount) as total FROM orders")
```

### 2. 限制返回的列

```python
# ❌ 低效：查询所有列
df = query("SELECT * FROM large_table")

# ✅ 高效：只查询需要的列
df = query("SELECT id, name, email FROM large_table")
```

### 3. 避免在循环中查询

```python
# ❌ 低效：N 次查询
user_ids = [1, 2, 3, 4, 5]
for uid in user_ids:
    df = query("SELECT * FROM orders WHERE user_id = ?", uid)
    # 处理...

# ✅ 高效：一次查询
df = query("SELECT * FROM orders WHERE user_id IN (1, 2, 3, 4, 5)")
```

### 4. 使用批量操作

```python
# ✅ 预先处理整个 DataFrame
df = query("SELECT * FROM data")
df = df.fillna(0)
df = df.drop_duplicates(subset=['id'])
processed = df.sort_values('date')
```

## 错误处理模式

### 基本错误处理

```python
def safe_process():
    df = query("SELECT * FROM data")

    if df.empty:
        throw("No data available")

    result = df['value'].sum() / df['value'].count()
    return result

return safe_process()
```

### API 调用错误处理

```python

def fetch_external_data(url):
    response = fetch(url, timeout=30)

    if response.status == 404:
        throw(f"Resource not found: {url}")
    elif response.status >= 400:
        throw(f"API error: {response.status} - {response.body}")
    elif not response.ok:
        throw(f"Request failed with status: {response.status}")

    return response.body

data = fetch_external_data("https://api.example.com/data")
```

## 调试技巧

### 1. 使用 return 临时查看中间结果

LLM 无法看到 `print()` 的输出，调试时应使用 `return` 临时返回中间结果来检查：

```python
# 第一步：查询数据
# 先临时返回看看数据长什么样
df = query("SELECT * FROM users")
return df  # 查看后再继续写后面的逻辑
```

```python
# 第二步：清洗后验证
df = query("SELECT * FROM users")
df = df.drop_duplicates(subset=['id'])
return df.head(10)  # 临时返回前 10 行确认去重效果
```

```python
# 第三步：检查数据类型
# 可以返回一个包含元信息的字典
s = df['age']
return {
    "dtype": s.dtype,
    "size": s.size,
    "sample": list(s)[:5]
}
```

### 2. 逐步构建脚本

```python
def main():
    # 第一步：查询数据
    df = query("SELECT * FROM users LIMIT 100")
    # return df  # 调试时可取消注释查看

    # 第二步：清洗数据
    df = df.drop_duplicates(subset=['id'])
    df = df.fillna(0)

    # 第三步：过滤数据
    df = df[df['age'] > 18]

    # 最后：返回结果
    return df

return main()
```

## 常见陷阱与经验教训

### 1. 外部 API 数据一定要先验证字段顺序

从外部 API 获取数据时，**不要凭文档或注释假设字段顺序和嵌套结构**，先输出原始数据确认：

```python
# ✅ 先输出数据样本确认结构
resp = fetch("https://api.example.com/data")
return resp.body  # 临时返回，查看数据类型和具体内容

# 确认结构后再编写处理逻辑
# 例如 resp.body 可能是：
#   - 数组：直接用于 DataFrame
#   - 字典：需要先取正确的 key
# 确认字段顺序后再写 columns
```

**常见陷阱**：API 文档说返回 `[时间, 开, 高, 低, 收]`，实际可能是 `[时间, 开, 收, 低, 高]`。不先用 `return` 查看就直接写 mapping，会导致全部字段错位。

### 2. 构建 DataFrame 时所有列长度必须一致

返回的字典中每个键对应的值长度必须相等：

```python
# ❌ 错误：长度不一致
return {
    "total": 100,                    # 标量
    "details": [1, 2, 3, 4, 5]      # 列表
}

# ✅ 正确：统一用 dict 或 list
return {
    "total": 100,
    "count": 5,
    "average": 20.0
}

# 或统一为列表
return df.head(10)
```
