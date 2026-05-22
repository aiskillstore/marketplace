# time 模块

> 完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

时间处理库（内置，直接使用）。

## 属性

| 属性       | 类型  | 说明                          |
| ---------- | ----- | ----------------------------- |
| `timezone` | int   | 当地时区相对于 UTC 的偏移秒数 |
| `altzone`  | int   | 启用夏令时时的偏移秒数        |
| `tzname`   | tuple | (标准时区名, 夏令时区名)      |

## 函数

| 函数                            | 参数           | 返回值 | 说明                                                 |
| ------------------------------- | -------------- | ------ | ---------------------------------------------------- |
| `time()`                        | -              | float  | 当前时间戳 (秒，自 1970-01-01 UTC)                   |
| `localtime(timestamp)`          | float/None     | Time   | 时间戳转本地时间结构，默认当前时间                   |
| `gmtime(timestamp)`             | float/None     | Time   | 时间戳转 UTC 时间结构，默认当前时间                  |
| `mktime(time_struct)`           | Time           | float  | 时间结构转时间戳                                     |
| `strftime(format, time_struct)` | str, Time/None | str    | 格式化时间，第二个参数可选，默认当前时间             |
| `strptime(string, format)`      | str, str       | Time   | 解析时间字符串，format 默认 `"%a %b %d %H:%M:%S %Y"` |
| `asctime(time_struct)`          | Time/None      | str    | 将时间结构转为标准字符串，默认当前时间               |
| `ctime(timestamp)`              | float/None     | str    | 时间戳转标准字符串，默认当前时间                     |

## Time 结构属性

| 属性       | 说明                   |
| ---------- | ---------------------- |
| `tm_year`  | 年                     |
| `tm_mon`   | 月 (1-12)              |
| `tm_mday`  | 日 (1-31)              |
| `tm_hour`  | 小时 (0-23)            |
| `tm_min`   | 分钟 (0-59)            |
| `tm_sec`   | 秒 (0-61)              |
| `tm_wday`  | 星期几 (0-6, 周一为 0) |
| `tm_yday`  | 一年中的第几天 (1-366) |
| `tm_isdst` | 夏令时标志             |

## 示例

```python
# 获取当前时间戳
current = time.time()      # 例如: 1716122400.123

# 转为本地时间
local = time.localtime(current)
print(local.tm_year)       # 2024
print(local.tm_mon)        # 5
print(local.tm_mday)       # 20

# 格式化时间
formatted = time.strftime("%Y-%m-%d %H:%M:%S", local)
# 例如: "2024-05-20 10:30:45"

# 解析时间字符串
parsed = time.strptime("2024-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
timestamp = time.mktime(parsed)

# 获取友好字符串
readable = time.ctime(current)
# 例如: "Mon May 20 10:30:45 2024"
```

## Timestamp 类

`Timestamp` 用于创建时间戳对象，常用于时间序列的滚动窗口和重采样操作。

```python
ts = Timestamp("2024-05-07T15:06:24+08:00")   # 从字符串构造
ts = Timestamp(1716122400000)                   # 从毫秒级 Unix 时间戳构造
```

**参数：**

- `value` (str/int): 支持常见时间/日期格式的字符串，或毫秒级 Unix 时间戳

```python
# 结合 rolling / resample 使用
df = query("SELECT price, created_at FROM trades")
ts = df['created_at'].map(lambda x: Timestamp(x))

result = df['price'].rolling('5s', timeline=ts).mean()
```
