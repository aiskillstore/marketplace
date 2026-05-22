# Series API 完整参考

> **注意**：`Series` 是内置全局类型，**无需 `import`**。完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

本文档详细列出 Series 支持的所有方法和属性。

## 创建 Series

从 DataFrame 中选择一列即获得 Series：

```python
df = query("SELECT name, age, salary FROM users")
s = df['age']          # 返回 Series
```

也可通过 `Series()` 构造：

```python
s = Series([1, 2, 3], dtype="int", name="count")
```

## 属性 (Properties)

| 属性    | 类型             | 说明                |
| ------- | ---------------- | ------------------- |
| `name`  | str              | Series 名称（列名） |
| `size`  | int              | 元素个数            |
| `dtype` | str              | 数据类型            |
| `loc`   | LocIndexerSeries | 基于位置的索引器    |

## 方法列表

### 数据变换

| 方法                                           | 参数                                         | 返回值 | 说明               |
| ---------------------------------------------- | -------------------------------------------- | ------ | ------------------ |
| `map(fn, ignore_none)`                         | fn: 函数, ignore_none: 忽略 None             | Series | 对每个元素应用函数 |
| `apply(fn)`                                    | fn: 函数                                     | Series | 应用函数 (同 map)  |
| `filter(fn)`                                   | fn: 函数                                     | Series | 过滤元素           |
| `reduce(fn, acc)`                              | fn: 函数, acc: 初始值                        | 标量值 | 累积计算           |
| `rename(name)`                                 | name: 新名称                                 | Series | 重命名             |
| `replace(to_replace, value, inplace)`          | to_replace: 被替换值, value: 新值            | Series | 替换指定值         |
| `sort_values(ascending, inplace, na_position)` | ascending: 升序, na_position: 'first'/'last' | Series | 排序               |

### 数据清洗

| 方法                                                     | 参数                                          | 说明             |
| -------------------------------------------------------- | --------------------------------------------- | ---------------- |
| `fillna(value, inplace)`                                 | value: 填充值, inplace: 原地修改              | 填充缺失值       |
| `ffill(inplace)`                                         | inplace: 原地修改                             | 向前填充         |
| `bfill(inplace)`                                         | inplace: 原地修改                             | 向后填充         |
| `drop_duplicates(keep, inplace)`                         | keep: 'first'/'last'/False, inplace: 原地修改 | 删除重复值       |
| `unique()`                                               | -                                             | 返回唯一值列表   |
| `value_counts(normalize, sort, ascending, bins, dropna)` | 见下方说明                                    | 返回各值出现次数 |
| `isin(values)`                                           | values: 值列表                                | 返回布尔 Series  |

### 统计聚合

| 方法                              | 返回值 | 说明                                     |
| --------------------------------- | ------ | ---------------------------------------- |
| `sum(skipna, numeric_only)`       | 数字   | 求和                                     |
| `mean(skipna, numeric_only)`      | float  | 平均值                                   |
| `median(skipna, numeric_only)`    | float  | 中位数                                   |
| `mode(dropna)`                    | Series | 众数                                     |
| `std(skipna, ddof, numeric_only)` | float  | 标准差（ddof=1 样本标准差，ddof=0 总体） |
| `var(skipna, ddof, numeric_only)` | float  | 方差                                     |
| `min(skipna, numeric_only)`       | 值     | 最小值                                   |
| `max(skipna, numeric_only)`       | 值     | 最大值                                   |
| `count()`                         | int    | 非空值计数                               |
| `nunique(dropna)`                 | int    | 唯一值数量                               |
| `nlargest(n, keep)`               | Series | 前 n 个最大值                            |
| `nsmallest(n, keep)`              | Series | 前 n 个最小值                            |
| `skew(dropna, numeric_only)`      | float  | 偏度                                     |
| `kurt(dropna, numeric_only)`      | float  | 峰度（Fisher 定义，正态分布为 0）        |
| `abs()`                           | Series | 绝对值                                   |

> 统计聚合方法中 `skipna` 默认 `True`（忽略缺失值），`numeric_only` 默认 `False`。
> `std` 和 `var` 的 `ddof` 默认 `1`（样本标准差/方差），设为 `0` 计算总体标准差/方差。

### 时间序列

| 方法                                         | 参数                                                                   | 说明             |
| -------------------------------------------- | ---------------------------------------------------------------------- | ---------------- |
| `diff(periods)`                              | periods: 差分级数，默认 1                                              | 差分             |
| `pct_change(periods)`                        | periods: 偏移周期，默认 1                                              | 百分比变化       |
| `cumprod(skipna)`                            | skipna: 忽略缺失值，默认 True                                          | 累积乘积         |
| `rolling(window, min_periods, timeline)`     | window: 窗口大小/时间周期, min_periods: 最小观测数, timeline: 时间索引 | 滚动窗口         |
| `ewm(com, span, alpha, min_periods, adjust)` | 见下方说明                                                             | 指数加权移动窗口 |
| `resample(rule, timeline)`                   | rule: 采样频率, timeline: 时间索引                                     | 重采样           |

### 运算操作

支持与标量的算术运算和比较运算，返回 Series：

```python
s = df['price']
s + 10          # 每个元素加 10
s * 1.1         # 每个元素乘以 1.1
s > 30          # 返回布尔 Series
s == 'active'   # 相等比较
```

### 迭代与转换

| 方法              | 返回值 | 说明                 |
| ----------------- | ------ | -------------------- |
| `items()`         | 迭代器 | 迭代 (索引, 值) 元组 |
| `values()`        | list   | 返回值列表           |
| `to_list()`       | list   | 转换为列表           |
| `append(value)`   | -      | 添加一个值           |
| `round(decimals)` | Series | 四舍五入             |

### 高级统计

| 方法                             | 参数                            | 说明        |
| -------------------------------- | ------------------------------- | ----------- |
| `cov(other, min_periods, ddof)`  | other: 另一 Series              | 协方差      |
| `corr(other, min_periods, ddof)` | other: 另一 Series              | 相关系数    |
| `lin_reg(other)`                 | other: 另一 Series              | 线性回归    |
| `r2(other, alpha, beta)`         | other: 另一 Series, alpha, beta | 决定系数 R² |

### 滚动窗口 (Rolling)

`rolling()` 返回 `Rolling` 对象，支持以下方法：

| 方法                               | 说明         |
| ---------------------------------- | ------------ |
| `.sum()` / `.mean()` / `.median()` | 求和/平均/中位数 |
| `.min()` / `.max()`                | 最小值/最大值 |
| `.std()` / `.var()`                | 标准差/方差 |
| `.skew()` / `.kurt()`              | 偏度/峰度 |
| `.apply(fn)`                       | 自定义函数 |

```python
s.rolling(window=3).mean()          # 3 期移动平均
s.rolling('5s', timeline=ts).sum()  # 按时间滚动
```

### 重采样 (Resample)

`resample()` 返回 `Resampler` 对象，支持方法同 Rolling。

```python
s.resample('1min', timeline=ts).mean()
```

### 指数加权 (EWM)

`ewm()` 返回 `ExponentialMovingWindow` 对象：

```python
s.ewm(span=10).mean()    # 指数加权移动平均
s.ewm(alpha=0.3).sum()   # 指数加权求和
s.ewm(span=10).var()     # 指数加权方差
```

## 使用示例

### 条件过滤

```python
df = query("SELECT id, age, salary FROM employees")
high_earners = df[df['salary'] > 50000]  # 使用布尔 Series 过滤
```

### 数据映射转换

```python
# 简单变换
prices = df['price']
doubled_prices = prices.map(lambda x: x * 2)

# 条件变换
discounted = prices.map(lambda x: x * 0.8 if x > 100 else x)
```

### 统计分析

```python
scores = df['score']
average_score = scores.mean()           # 平均分
median_score = scores.median()          # 中位数
std_dev = scores.std()                  # 标准差
max_score = scores.max()                # 最高分
total = scores.sum()                    # 总分
unique_scores = scores.nunique()        # 唯一值数量
```

### 缺失值处理

```python
# 向前填充
s = s.ffill(inplace=True)

# 向后填充
s = s.bfill(inplace=True)

# 用指定值填充
s = s.fillna(0, inplace=True)
```

### 值替换与去重

```python
# 替换指定值
s = s.replace(0, -99)                   # 将 0 替换为 -99

# 去重
unique_vals = s.unique()                # 返回唯一值列表
deduped = s.drop_duplicates()           # 返回去重后的 Series

# 值计数
counts = s.value_counts()               # 返回每个值出现的次数

# 检查成员资格
mask = s.isin(['active', 'pending'])    # 返回布尔 Series
```

### 最大/最小值选取

```python
top5 = s.nlargest(5)    # 前 5 个最大值
bottom3 = s.nsmallest(3) # 前 3 个最小值
```

### 时间序列分析

```python
values = df['value']

# 差分
diff_values = values.diff(1)

# 百分比变化
pct_changes = values.pct_change(1)

# 滚动窗口计算
rolling_mean = values.rolling(window=3).mean()

# 按时间滚动
r = values.rolling('5s', timeline=df['timeline']).mean()

# 重采样
r = values.resample('1min', timeline=df['timeline']).sum()
```

### 操作优先级

当对 Series 进行多次操作时，避免低效的链式调用：

```python
# ❌ 低效：多次迭代
result = df['price'].map(lambda x: x * 1.1).map(lambda x: round(x, 2))

# ✅ 高效：合并操作
result = df['price'].map(lambda x: round(x * 1.1, 2))
```
