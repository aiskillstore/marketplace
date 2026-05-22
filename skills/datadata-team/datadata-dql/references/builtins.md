# 内置函数

> 完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

以下函数均为 DQL 内置全局名称，**无需 `import`**，直接使用。

## concat

连接多个 Series 或 DataFrame 对象。

```python
result = concat(
    objs,
    join="outer"
)
```

**参数：**

- `objs` (list): 要连接的 Series/DataFrame 列表
- `join` (str): 连接方式，"inner" (交集) 或 "outer" (并集)，默认 "outer"

**返回值：** 连接后的 Series 或 DataFrame

**示例：**

```python
# 连接两个 DataFrame
df1 = query("SELECT * FROM table1")
df2 = query("SELECT * FROM table2")
combined = concat([df1, df2], join="outer")  # 竖向拼接
```

## throw

抛出错误，中断脚本执行。

```python
throw(error_message)
```

**参数：**

- `error_message`: 错误消息或任意对象

**示例：**

```python
def validate_data(df):
    if df.empty:
        throw("DataFrame is empty")
    if 'id' not in df.columns:
        throw("Missing 'id' column")
    return True

df = query("SELECT * FROM users")
validate_data(df)
```

## print

输出到调试日志。

```python
print("Debug message")
print(f"User: {name}, Age: {age}")
```

## len

获取序列长度。

```python
lst = [1, 2, 3]
print(len(lst))         # 3

s = "hello"
print(len(s))           # 5
```

## range

生成数字序列。

```python
list(range(5))          # [0, 1, 2, 3, 4]
list(range(2, 8, 2))    # [2, 4, 6]
```

## 实用示例

### 完整的错误处理脚本

```python
def main():
    # 第一步：查询数据
    df = query("SELECT * FROM data WHERE status = ?", 'active')

    if df.empty:
        throw("No active records found")

    # 第二步：数据验证
    if 'id' not in df.columns or 'value' not in df.columns:
        throw("Missing required columns")

    # 第三步：数据处理
    df = df.drop_duplicates(subset=['id'])
    df = df[df['value'].map(lambda x: x is not None)]

    # 第四步：计算结果
    total = df['value'].sum()
    count = df['value'].count()

    if count == 0:
        throw("No valid values to process")

    avg = total / count

    return {
        'status': 'success',
        'total': total,
        'count': count,
        'average': avg
    }

return main()
```
