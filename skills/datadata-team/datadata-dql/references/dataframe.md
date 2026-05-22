# DataFrame API 完整参考

> **注意**：`DataFrame` 是内置全局类型，**无需 `import`**。完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

本文档详细列出 DataFrame 支持的所有方法和属性。

## 构造 DataFrame

`DataFrame()` 可以从多种方式构造：

```python
# 从字典构造（列为键，值为列表）
df = DataFrame({"name": ["js", "go"], "count": [1, 2]})

# 从字典列表构造（每行一个 dict）
df = DataFrame([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
])

# 从列表构造，指定列名
df = DataFrame([["js", 1], ["go", 2]], columns=["name", "count"])

# 从 query 结果构造（通常不需要，query 直接返回 DataFrame）
df = query("SELECT * FROM users")
```

## 属性 (Properties)

| 属性       | 类型                | 说明                                    |
| ---------- | ------------------- | --------------------------------------- |
| `columns`  | list                | 列名列表                                |
| `dtypes`   | dict                | 每列的数据类型                          |
| `shape`    | tuple               | (行数, 列数)                            |
| `size`     | int                 | 总元素数                                |
| `empty`    | bool                | 是否为空                                |
| `has_more` | bool                | 是否有更多行（query 最多返回 10000 行） |
| `loc`      | LocIndexerDataFrame | 基于位置的索引器                        |

## 数据访问

### 按列名访问

```python
series = df['column_name']  # 返回 Series
```

### 按行索引访问

```python
row_dict = df[0]    # 第一行，返回字典
row_dict = df[-1]   # 最后一行
```

### 多行选择

```python
# 使用布尔 Series 过滤
mask = df['price'] > 100
filtered = df[mask]  # 返回 DataFrame
```

## 方法列表

### 查看数据

| 方法        | 返回值    | 说明        |
| ----------- | --------- | ----------- |
| `head(n=5)` | DataFrame | 返回前 n 行 |
| `tail(n=5)` | DataFrame | 返回后 n 行 |

### 数据清洗

| 方法                                     | 参数                                       | 说明       |
| ---------------------------------------- | ------------------------------------------ | ---------- |
| `fillna(value, inplace)`                 | value: 填充值, inplace: 原地修改           | 填充缺失值 |
| `ffill(inplace)`                         | inplace: 原地修改                          | 向前填充   |
| `bfill(inplace)`                         | inplace: 原地修改                          | 向后填充   |
| `drop_duplicates(subset, keep, inplace)` | subset: 列列表, keep: 'first'/'last'/False | 删除重复行 |

### 数据转换

| 方法                        | 参数                 | 说明           |
| --------------------------- | -------------------- | -------------- |
| `rename(mapper)`            | mapper: 列名映射字典 | 重命名列       |
| `apply(fn)`                 | fn: 函数             | 对每列应用函数 |
| `round(decimals)`           | decimals: 小数位     | 四舍五入       |
| `abs(skipna, numeric_only)` | 见统计聚合参数       | 绝对值         |

### 排序和分组

| 方法                                      | 参数                                                        | 说明   |
| ----------------------------------------- | ----------------------------------------------------------- | ------ |
| `sort_values(by, ascending, na_position)` | by: 列名/列表, ascending: 升序, na_position: 'first'/'last' | 排序   |
| `groupby(by)`                             | by: 列名/列表                                               | 分组   |
| `pivot(index, columns, values)`           | index: 行索引列, columns: 列索引列, values: 值列            | 透视表 |

### 统计聚合

统计方法均支持以下参数：

- `skipna` (默认 True): 是否忽略缺失值
- `numeric_only` (默认 False): 是否只计算数值列

`std` 和 `var` 额外支持 `ddof` 参数（默认 1，设为 0 为总体标准差/方差）。

| 方法                              | 返回值 | 说明           |
| --------------------------------- | ------ | -------------- |
| `sum(skipna, numeric_only)`       | Series | 每列求和       |
| `mean(skipna, numeric_only)`      | Series | 每列平均值     |
| `median(skipna, numeric_only)`    | Series | 每列中位数     |
| `mode(dropna)`                    | Series | 每列众数       |
| `std(skipna, ddof, numeric_only)` | Series | 每列标准差     |
| `var(skipna, ddof, numeric_only)` | Series | 每列方差       |
| `min(skipna, numeric_only)`       | Series | 每列最小值     |
| `max(skipna, numeric_only)`       | Series | 每列最大值     |
| `count()`                         | Series | 每列非空值计数 |
| `nunique(dropna)`                 | Series | 每列唯一值数量 |
| `abs(skipna, numeric_only)`       | Series | 每列绝对值     |
| `round(decimals)`                 | Series | 每列四舍五入   |

### 时间序列

| 方法                                     | 参数                                                                   | 说明       |
| ---------------------------------------- | ---------------------------------------------------------------------- | ---------- |
| `diff(periods)`                          | periods: 差分级数，默认 1                                              | 差分       |
| `pct_change(periods)`                    | periods: 偏移周期，默认 1                                              | 百分比变化 |
| `cumprod(skipna)`                        | skipna: 忽略缺失值，默认 True                                          | 累积乘积   |
| `rolling(window, min_periods, timeline)` | window: 窗口大小/时间周期, min_periods: 最小观测数, timeline: 时间索引 | 滚动窗口   |
| `resample(rule, timeline)`               | rule: 采样频率, timeline: 时间索引                                     | 重采样     |

### 合并 & 连接

| 方法                                   | 参数                                                           | 说明     |
| -------------------------------------- | -------------------------------------------------------------- | -------- |
| `merge(other, left_on, right_on, how)` | other: 另一 DataFrame, left_on/right_on: 连接键, how: 连接类型 | 合并     |
| `append(data)`                         | data: dict 或 Series                                           | 添加一行 |

`concat()` 是全局函数，详见 [builtins.md](./builtins.md)：

```python
# 按行合并（axis=0）
result = concat([df1, df2], join="outer")

# 按列合并（axis=1）
result = concat([df1, df2], axis=1, join="outer")
```

### 分组聚合 (GroupBy)

`groupby()` 返回 `DataFrameGroupBy` 对象，支持以下聚合方法：

| 方法                                       | 说明           |
| ------------------------------------------ | -------------- |
| `.sum()` / `.mean()` / `.median()`         | 求和/平均/中位数 |
| `.min()` / `.max()`                        | 最小值/最大值   |
| `.std()` / `.var()`                        | 标准差/方差     |
| `.skew()` / `.kurt()`                      | 偏度/峰度       |
| `.diff()` / `.cumprod()` / `.pct_change()` | 差分/累积/变化率 |
| `.apply(fn)`                               | 自定义函数     |
| `.transform(fn)`                           | 转换函数       |
| `.aggregation(fn)`                         | 聚合函数       |

```python
df.groupby('category').sum()       # 按分类求和
df.groupby('date').mean()          # 按日期平均
df.groupby(['a', 'b']).apply(fn)   # 多级分组 + 自定义函数
```

### 滚动窗口 (Rolling)

`rolling()` 返回 `Rolling` 对象，支持以下方法：

| 方法                                 | 说明     |
| ------------------------------------ | -------- |
| `.sum()` / `.mean()` / `.median()`   | 求和/平均/中位数 |
| `.min()` / `.max()`                  | 最小值/最大值 |
| `.std()` / `.var()`                  | 标准差/方差 |
| `.skew()` / `.kurt()`                | 偏度/峰度 |
| `.apply(fn)`                         | 自定义函数 |

```python
df['value'].rolling(window=3).mean()         # 3 期移动平均
df['value'].rolling('5s', timeline=ts).sum() # 按时间滚动
```

### 重采样 (Resample)

`resample()` 返回 `Resampler` 对象，支持方法同 Rolling。

```python
df['price'].resample('1min', timeline=ts).mean()
```

### 指数加权 (EWM)

`ewm()` 返回 `ExponentialMovingWindow` 对象：

```python
df['value'].ewm(span=10).mean()    # 指数加权移动平均
df['value'].ewm(alpha=0.3).sum()   # 指数加权求和
df['value'].ewm(span=10).var()     # 指数加权方差
```

### 迭代

| 方法         | 返回值 | 说明                  |
| ------------ | ------ | --------------------- |
| `items()`    | 迭代器 | 迭代列 (列名, Series) |
| `iterrows()` | 迭代器 | 迭代行 (索引, 行字典) |
| `to_list()`  | list   | 转换为列表            |

## 使用示例

### 基本操作

```python
# 查看数据
df.head()
df.shape  # (1000, 5)

# 访问列
prices = df['price']
names = df['name']

# 条件过滤
expensive = df[df['price'] > 1000]
```

### 数据清洗

```python
# 删除重复
df = df.drop_duplicates(subset=['id'])

# 填充缺失值
df = df.fillna(0, inplace=True)
df = df.ffill(inplace=True)  # 向前填充

# 按列排序
df = df.sort_values('date', ascending=False)
```

### 分组聚合

```python
# 按分类分组统计
by_category = df.groupby('category')
sales_by_cat = by_category['amount'].sum()

# 多级分组
by_date_cat = df.groupby(['date', 'category']).sum()
```

### 数据转换

```python
# 透视表
pivot_table = df.pivot(
    index='date',
    columns='category',
    values='amount'
)

# 重命名列
df = df.rename({"name": "language"})

# 添加计算列
df['discounted_price'] = df['price'].map(lambda x: x * 0.9)
```

## 实用示例

### 用户行为分析

```python
# 场景：统计用户登录活跃度分类
df = query("""
    SELECT
        user_id,
        COUNT(*) as login_count,
        MAX(created_at) as last_login
    FROM user_logins
    GROUP BY user_id
    ORDER BY login_count DESC
""")

# 分类活跃度
def categorize_activity(count):
    if count >= 100:
        return 'Very Active'
    elif count >= 50:
        return 'Active'
    elif count >= 10:
        return 'Regular'
    else:
        return 'Inactive'

df['activity_level'] = df['login_count'].map(categorize_activity)

# 统计用户分类
by_level = df.groupby('activity_level')['user_id'].count()

return {
    'breakdown': by_level,
    'top_users': df.head(10),
    'summary': {
        'total_users': len(df),
        'avg_logins': df['login_count'].mean(),
        'max_logins': df['login_count'].max()
    }
}
```

### 月度销售报表

```python
# 场景：生成当月销售报表
now = time.localtime()
month = now.tm_mon
year = now.tm_year

df = query("""
    SELECT
        DATE(created_at) as date,
        COUNT(*) as orders,
        SUM(amount) as revenue
    FROM sales
    WHERE MONTH(created_at) = ? AND YEAR(created_at) = ?
    GROUP BY DATE(created_at)
    ORDER BY date
""", month, year)

total_orders = df['orders'].sum()
total_revenue = df['revenue'].sum()
avg_daily_revenue = total_revenue / len(df) if len(df) > 0 else 0
max_revenue_day = df.sort_values('revenue', ascending=False).head(1)

return {
    'period': f"{year}-{month:02d}",
    'total_orders': total_orders,
    'total_revenue': round(total_revenue, 2),
    'avg_daily_revenue': round(avg_daily_revenue, 2),
    'best_day': {
        'date': max_revenue_day['date'].max() if len(max_revenue_day) > 0 else None,
        'revenue': max_revenue_day['revenue'].max() if len(max_revenue_day) > 0 else 0
    },
    'daily_breakdown': df
}
```

### 多表连接

```python
# 场景：关联订单、用户和产品信息
orders = query("SELECT id, user_id, product_id, quantity FROM orders")
users = query("SELECT id, name FROM users")
products = query("SELECT id, name, price FROM products")

# 第一次合并
result = orders.merge(users, left_on='user_id', right_on='id', how='left')

# 第二次合并
result = result.merge(products, left_on='product_id', right_on='id', how='left')

# 计算订单总价
result['total_price'] = result['quantity'].map(
    lambda q: q * result['price'].max() if result['price'].max() else 0
)

return result
```

### 异常检测

```python
# 场景：基于 3σ 原则识别异常订单
df = query("SELECT id, amount FROM orders WHERE created_at > DATE_SUB(CURDATE(), INTERVAL 30 DAY)")

mean_amount = df['amount'].mean()
std_amount = df['amount'].std()
threshold = mean_amount + 3 * std_amount

def is_outlier(amount):
    return amount > threshold

df['is_outlier'] = df['amount'].map(is_outlier)
outliers = df[df['is_outlier']]

return {
    'statistics': {
        'mean': mean_amount,
        'std': std_amount,
        'threshold': threshold
    },
    'outliers': outliers,
    'outlier_count': len(outliers)
}
```

### RFM 分析

```python
# 场景：客户价值分析（最近一次消费、频率、金额）
df = query("""
    SELECT
        customer_id,
        MAX(order_date) as last_order_date,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM orders
    WHERE order_date > DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    GROUP BY customer_id
""")

now = time.time()

def calculate_recency(last_order_date):
    days_ago = (now - last_order_date) / (24 * 3600)
    return int(days_ago)

df['recency'] = df['last_order_date'].map(calculate_recency)

def calculate_rfm_score(recency, frequency, monetary):
    r_score = 5 if recency < 30 else (4 if recency < 60 else (3 if recency < 90 else 1))
    f_score = 5 if frequency >= 20 else (4 if frequency >= 10 else (3 if frequency >= 5 else 1))
    m_score = 5 if monetary >= 5000 else (4 if monetary >= 1000 else (3 if monetary >= 100 else 1))
    return r_score * 100 + f_score * 10 + m_score

df['rfm_score'] = df.apply(
    lambda row: calculate_rfm_score(row['recency'], row['frequency'], row['monetary'])
)

return df.sort_values('rfm_score', ascending=False).head(100)
```
