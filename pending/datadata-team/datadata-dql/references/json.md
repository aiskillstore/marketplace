# json 模块

> 完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

JSON 序列化和反序列化（内置，直接使用）。

## 函数

| 函数                          | 参数                                | 返回值 | 说明                                         |
| ----------------------------- | ----------------------------------- | ------ | -------------------------------------------- |
| `dumps(obj, indent)`          | object, int/None                    | str    | 对象序列化为 JSON 字符串                     |
| `loads(s, default)`           | str, object/None                    | object | 解析 JSON 字符串为对象，解析失败返回 default |
| `indent(str, prefix, indent)` | str, prefix: 行前缀, indent: 缩进符 | str    | 格式化 JSON 字符串，添加前缀和缩进           |

**参数：**

- `indent` (int/str/None): 缩进方式，None 为紧凑格式，整数为空格数，字符串为缩进符
- `default` (object/None): 解析失败时返回的默认值
- `prefix` (str): 每行前添加的前缀，默认 `""`
- `indent` (str): 缩进字符，默认 `"\t"`

## 示例

```python
# 序列化
data = {
    "name": "Alice",
    "age": 30,
    "scores": [90, 85, 92]
}
json_str = json.dumps(data)
# '{"name": "Alice", "age": 30, "scores": [90, 85, 92]}'

# 序列化为格式化字符串
pretty_json = json.dumps(data, indent=2)

# 反序列化
parsed = json.loads(json_str)
print(parsed["name"])      # "Alice"

# 解析失败时返回默认值
invalid_json = '{"name": "Alice", "age": 30'  # 缺少关闭大括号
result = json.loads(invalid_json, default={"name": "Unknown", "age": 0})
print(result)              # {'name': 'Unknown', 'age': 0}

# 格式化 JSON 字符串，添加行前缀
input_json = '{"name": "Alice", "age": 30, "languages": ["English", "French"]}'
formatted = json.indent(input_json, prefix=">> ", indent="  ")
print(formatted)
# 输出:
# {
# >>   "name": "Alice",
# >>   "age": 30,
# >>   "languages": [
# >>     "English",
# >>     "French"
# >>   ]
# >> }
```
