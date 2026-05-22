# math 模块

> 完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

数学函数库（内置，直接使用）。所有函数都是静态方法，无需实例化。

```python
math.ceil(3.2)          # 4
math.floor(3.8)         # 3
math.sqrt(16)           # 4.0
math.pow(2, 10)         # 1024.0
```

## 基础函数

| 函数             | 参数         | 返回值 | 说明                     |
| ---------------- | ------------ | ------ | ------------------------ |
| `ceil(x)`        | float        | int    | 天花板函数，向上取整     |
| `floor(x)`       | float        | int    | 地板函数，向下取整       |
| `round(x)`       | float        | int    | 四舍五入                 |
| `fabs(x)`        | float        | float  | 绝对值 (浮点)            |
| `copysign(x, y)` | float, float | float  | 返回 x 的大小和 y 的符号 |

## 幂和对数

| 函数           | 参数         | 返回值 | 说明                 |
| -------------- | ------------ | ------ | -------------------- |
| `pow(x, y)`    | float, float | float  | x 的 y 次方          |
| `sqrt(x)`      | float        | float  | 平方根               |
| `exp(x)`       | float        | float  | e 的 x 次方          |
| `log(x, base)` | float, float | float  | x 以 base 为底的对数 |

## 三角函数

所有三角函数参数单位为弧度。

| 函数          | 参数         | 返回值 | 说明         |
| ------------- | ------------ | ------ | ------------ |
| `sin(x)`      | float        | float  | 正弦         |
| `cos(x)`      | float        | float  | 余弦         |
| `tan(x)`      | float        | float  | 正切         |
| `asin(x)`     | float        | float  | 反正弦       |
| `acos(x)`     | float        | float  | 反余弦       |
| `atan(x)`     | float        | float  | 反正切       |
| `atan2(y, x)` | float, float | float  | 两参数反正切 |
| `degrees(x)`  | float        | float  | 弧度转度     |
| `radians(x)`  | float        | float  | 度转弧度     |

## 双曲函数

| 函数       | 参数  | 返回值 | 说明       |
| ---------- | ----- | ------ | ---------- |
| `sinh(x)`  | float | float  | 双曲正弦   |
| `cosh(x)`  | float | float  | 双曲余弦   |
| `tanh(x)`  | float | float  | 双曲正切   |
| `asinh(x)` | float | float  | 反双曲正弦 |
| `acosh(x)` | float | float  | 反双曲余弦 |
| `atanh(x)` | float | float  | 反双曲正切 |

## 其他函数

| 函数              | 参数         | 返回值 | 说明                        |
| ----------------- | ------------ | ------ | --------------------------- |
| `hypot(x, y)`     | float, float | float  | 欧几里得范数，sqrt(x² + y²) |
| `mod(x, y)`       | float, float | float  | x 除以 y 的浮点余数         |
| `remainder(x, y)` | float, float | float  | IEEE 754 余数               |
| `gamma(x)`        | float        | float  | Gamma 函数                  |

## 示例

```python
# 基础计算
math.ceil(3.2)          # 4
math.floor(3.8)         # 3
math.sqrt(16)           # 4.0
math.pow(2, 10)         # 1024.0

# 三角运算
angle_degrees = 45
angle_radians = math.radians(angle_degrees)
sin_value = math.sin(angle_radians)  # 约 0.707

# 对数运算
math.log(100, 10)       # 2.0
math.log(8, 2)          # 3.0
```
