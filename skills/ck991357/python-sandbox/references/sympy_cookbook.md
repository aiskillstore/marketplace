# SymPy 符号数学指南 (v2.5)

## 🎯 工具概述
**功能**：符号数学计算，包括方程求解、微积分、代数运算等
**输出原则**：直接打印结果，系统自动处理输出格式

## ✅ 代码解释器适配说明
- **直接打印**：所有计算结果直接使用 `print()` 输出
- **符号表达式**：SymPy 表达式会以美观的数学格式显示
- **自动渲染**：复杂数学公式会自动转换为易读格式
- **数值计算**：需要数值结果时使用 `.evalf()` 或 `sp.N()`

## 🧮 基础符号运算

### 符号定义与基本操作
```python
import sympy as sp

# 定义符号变量
x, y, z = sp.symbols('x y z')
a, b, c = sp.symbols('a b c')

# 基本表达式操作
expr1 = x**2 + 2*x + 1
expr2 = (x + 1)**2

print("=== 基础符号运算 ===")
print(f"表达式1: {expr1}")
print(f"表达式2: {expr2}")
print(f"表达式1展开: {sp.expand(expr1)}")
print(f"表达式2因式分解: {sp.factor(expr2)}")
print(f"两个表达式是否相等: {expr1.equals(expr2)}")

# 表达式简化
complex_expr = (x**2 - 1)/(x - 1)
simplified = sp.simplify(complex_expr)
print(f"复杂表达式: {complex_expr}")
print(f"简化后: {simplified}")
```

## 🎯 方程求解

### 代数方程求解
```python
import sympy as sp

x, y, z = sp.symbols('x y z')

print("=== 代数方程求解 ===")

# 一元二次方程
eq1 = sp.Eq(x**2 - 5*x + 6, 0)
solutions1 = sp.solve(eq1, x)
print(f"方程: {eq1}")
print(f"解: {solutions1}")

# 线性方程组
eq2 = sp.Eq(2*x + 3*y, 7)
eq3 = sp.Eq(4*x - y, 1)
solutions2 = sp.solve([eq2, eq3], (x, y))
print(f"\n方程组:")
print(f"  {eq2}")
print(f"  {eq3}")
print(f"解: {solutions2}")

# 非线性方程数值解
eq4 = sp.Eq(sp.sin(x) - x/2, 0)
solution4 = sp.nsolve(eq4, x, 1)  # 从x=1开始数值求解
print(f"\n非线性方程: {eq4}")
print(f"数值解: {solution4}")
```

## 📐 微积分运算

### 微分计算
```python
import sympy as sp

x = sp.symbols('x')

print("=== 微分计算 ===")

# 定义函数
f = x**3 + 2*x**2 + sp.sin(x)
print(f"函数: f(x) = {f}")

# 一阶导数
f_prime = sp.diff(f, x)
print(f"一阶导数: f'(x) = {f_prime}")

# 二阶导数
f_double_prime = sp.diff(f, x, 2)
print(f"二阶导数: f''(x) = {f_double_prime}")

# 偏导数（多变量）
y = sp.symbols('y')
g = x**2 * y + sp.sin(x*y)
g_x = sp.diff(g, x)
g_y = sp.diff(g, y)
print(f"\n多变量函数: g(x,y) = {g}")
print(f"对x偏导: ∂g/∂x = {g_x}")
print(f"对y偏导: ∂g/∂y = {g_y}")
```

### 积分计算
```python
import sympy as sp

x = sp.symbols('x')

print("=== 积分计算 ===")

# 不定积分
f = x**2 + sp.sin(x)
indefinite = sp.integrate(f, x)
print(f"函数: f(x) = {f}")
print(f"不定积分: ∫f(x)dx = {indefinite} + C")

# 定积分
definite = sp.integrate(f, (x, 0, sp.pi))
print(f"定积分 [0,π]: ∫₀^π f(x)dx = {definite}")
print(f"数值结果: {definite.evalf()}")

# 多重积分
y = sp.symbols('y')
double_int = sp.integrate(x*y, (x, 0, 1), (y, 0, 2))
print(f"\n二重积分: ∫₀¹∫₀² xy dy dx = {double_int}")
```

### 极限计算
```python
import sympy as sp

x = sp.symbols('x')

print("=== 极限计算 ===")

# 基本极限
limit1 = sp.limit(sp.sin(x)/x, x, 0)
print(f"lim(x→0) sin(x)/x = {limit1}")

# 无穷极限
limit2 = sp.limit(1/x, x, 0, '+')  # 从正方向逼近
limit3 = sp.limit(1/x, x, 0, '-')  # 从负方向逼近
print(f"lim(x→0⁺) 1/x = {limit2}")
print(f"lim(x→0⁻) 1/x = {limit3}")

# 复杂极限
limit4 = sp.limit((1 + 1/x)**x, x, sp.oo)
print(f"lim(x→∞) (1 + 1/x)ˣ = {limit4}")
```

## 🔍 数学证明与恒等式

### 代数恒等式验证
```python
import sympy as sp

a, b, x = sp.symbols('a b x')

print("=== 数学恒等式验证 ===")

# 验证 (a+b)² = a² + 2ab + b²
lhs1 = (a + b)**2
rhs1 = a**2 + 2*a*b + b**2
identity1 = sp.simplify(lhs1 - rhs1) == 0
print(f"(a+b)² = a² + 2ab + b²: {identity1}")

# 验证三角恒等式 sin²x + cos²x = 1
lhs2 = sp.sin(x)**2 + sp.cos(x)**2
rhs2 = 1
identity2 = sp.simplify(lhs2 - rhs2) == 0
print(f"sin²x + cos²x = 1: {identity2}")

# 验证欧拉公式
theta = sp.symbols('theta')
euler_lhs = sp.exp(sp.I * theta)
euler_rhs = sp.cos(theta) + sp.I * sp.sin(theta)
euler_identity = sp.simplify(euler_lhs - euler_rhs) == 0
print(f"e^(iθ) = cosθ + i sinθ: {euler_identity}")
```

## 🧩 线性代数

### 矩阵运算
```python
import sympy as sp

print("=== 矩阵运算 ===")

# 定义符号矩阵
A = sp.Matrix([[1, 2], [3, 4]])
B = sp.Matrix([[2, 0], [1, 2]])

print(f"矩阵 A:\n{A}")
print(f"矩阵 B:\n{B}")

# 基本运算
print(f"\n矩阵加法 A+B:\n{A + B}")
print(f"矩阵乘法 A×B:\n{A * B}")
print(f"A的行列式: {A.det()}")
print(f"A的逆矩阵:\n{A.inv()}")

# 特征值和特征向量
eigenvals = A.eigenvals()
eigenvects = A.eigenvects()
print(f"\nA的特征值: {eigenvals}")
print(f"A的特征向量: {eigenvects}")

# 解线性方程组
x1, x2 = sp.symbols('x1 x2')
eq1 = sp.Eq(2*x1 + 3*x2, 7)
eq2 = sp.Eq(4*x1 + 5*x2, 13)
solution = sp.solve([eq1, eq2], (x1, x2))
print(f"\n方程组:")
print(f"  {eq1}")
print(f"  {eq2}")
print(f"解: {solution}")
```

## 📈 级数展开与数值计算

### 泰勒级数展开
```python
import sympy as sp

x = sp.symbols('x')

print("=== 级数展开 ===")

# 常用函数的泰勒展开
sin_series = sp.sin(x).series(x, 0, 6)  # 在0处展开到6阶
cos_series = sp.cos(x).series(x, 0, 6)
exp_series = sp.exp(x).series(x, 0, 5)

print(f"sin(x)的泰勒展开: {sin_series}")
print(f"cos(x)的泰勒展开: {cos_series}")
print(f"e^x的泰勒展开: {exp_series}")

# 数值近似
print(f"\n数值近似:")
print(f"π ≈ {sp.N(sp.pi, 10)}")  # 10位精度
print(f"e ≈ {sp.N(sp.E, 8)}")    # 8位精度
print(f"√2 ≈ {sp.N(sp.sqrt(2), 6)}")

# 符号表达式的数值计算
expr = sp.integrate(sp.sin(x), (x, 0, sp.pi/2))
numerical_result = sp.N(expr)
print(f"\n符号积分: ∫₀^(π/2) sin(x) dx = {expr}")
print(f"数值结果: {numerical_result}")
```

## 🎓 复杂数学问题

### 函数分析与极值
```python
import sympy as sp

x = sp.symbols('x')

print("=== 函数分析与极值 ===")

# 定义函数
f = x**3 - 6*x**2 + 9*x + 1
print(f"函数: f(x) = {f}")

# 求导找临界点
f_prime = sp.diff(f, x)
critical_points = sp.solve(f_prime, x)
print(f"一阶导数: f'(x) = {f_prime}")
print(f"临界点: {critical_points}")

# 二阶导数测试
f_double_prime = sp.diff(f, x, 2)
for point in critical_points:
    second_deriv_val = f_double_prime.subs(x, point)
    if second_deriv_val > 0:
        extremum_type = "局部极小值"
    elif second_deriv_val < 0:
        extremum_type = "局部极大值"
    else:
        extremum_type = "需要进一步分析"
    print(f"点 x = {point}: {extremum_type}")

# 函数值
for point in critical_points:
    func_val = f.subs(x, point)
    print(f"f({point}) = {func_val}")
```

### 曲线性质分析
```python
import sympy as sp

x = sp.symbols('x')

print("=== 曲线性质分析 ===")

f = x**2 * sp.sin(x)

# 曲线长度（弧长）
curve_length = sp.integrate(sp.sqrt(1 + sp.diff(f, x)**2), (x, 0, sp.pi))
print(f"函数: f(x) = {f}")
print(f"曲线在 [0,π] 上的长度: {sp.N(curve_length)}")

# 旋转体体积
volume = sp.pi * sp.integrate(f**2, (x, 0, sp.pi))
print(f"曲线绕x轴旋转的体积: {sp.N(volume)}")

# 曲率
f_prime = sp.diff(f, x)
f_double_prime = sp.diff(f, x, 2)
curvature = f_double_prime / (1 + f_prime**2)**(3/2)
print(f"曲率公式: κ(x) = {curvature}")
```

## 💡 实用工具函数

### 自动验证等式
```python
import sympy as sp

def verify_identity(expr1, expr2, method="simplify"):
    """
    验证两个表达式是否恒等
    method: "simplify", "expand", "factor", "trigsimp"
    """
    if method == "simplify":
        difference = sp.simplify(expr1 - expr2)
    elif method == "expand":
        difference = sp.expand(expr1 - expr2)
    elif method == "factor":
        difference = sp.factor(expr1 - expr2)
    elif method == "trigsimp":
        difference = sp.trigsimp(expr1 - expr2)
    else:
        difference = expr1 - expr2
    
    is_identity = (difference == 0)
    
    print(f"表达式1: {expr1}")
    print(f"表达式2: {expr2}")
    print(f"验证方法: {method}")
    print(f"是否恒等: {is_identity}")
    
    return is_identity

# 使用示例
x, y = sp.symbols('x y')
verify_identity((x + y)**2, x**2 + 2*x*y + y**2, "expand")
```

## 🔧 代码解释器适配优化

### SymPy 与图表集成
```python
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np

x = sp.symbols('x')

print("=== SymPy 与 Matplotlib 集成 ===")

# 定义符号函数
f_sym = sp.sin(x) * sp.exp(-x/5)

# 转换为数值函数用于绘图
f_num = sp.lambdify(x, f_sym, 'numpy')

# 创建数据点
x_vals = np.linspace(0, 20, 400)
y_vals = f_num(x_vals)

# 绘图
plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals, 'b-', linewidth=2, label='f(x) = sin(x)·e^(-x/5)')
plt.title('SymPy 符号函数可视化')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.grid(True, alpha=0.3)
plt.legend()

# 计算并标记极值点
f_prime_sym = sp.diff(f_sym, x)
critical_points = sp.solve(f_prime_sym, x)

# 筛选实数解
real_critical_points = [cp.evalf() for cp in critical_points if cp.is_real]
for cp in real_critical_points:
    if 0 <= cp <= 20:
        y_cp = f_sym.subs(x, cp).evalf()
        plt.plot(cp, y_cp, 'ro', markersize=8)
        plt.text(cp, y_cp + 0.1, f'({cp:.2f}, {y_cp:.2f})', 
                ha='center', fontsize=9)

plt.tight_layout()
plt.show()
```

## ⚠️ 使用注意事项

### ✅ 推荐做法：
1. **标准导入**：`import sympy as sp`
2. **符号定义**：明确使用 `sp.symbols()` 定义变量
3. **数值计算**：需要数值结果时使用 `.evalf()` 或 `sp.N()`
4. **直接打印**：使用 `print()` 输出所有结果

### ❌ 避免的操作：
1. 不要手动构建 JSON 输出
2. 不要使用复杂的自定义输出格式
3. 不要省略符号定义直接使用变量

### 🔧 错误处理：
```python
try:
    import sympy as sp
    x = sp.symbols('x')
    result = sp.solve(x**2 - 1, x)
    print(f"方程解: {result}")
except ImportError:
    print("SymPy 不可用")
except Exception as e:
    print(f"计算错误: {e}")
```

### 💡 实用技巧：
```python
# 快速获取符号表达式的数值近似
expr = sp.integrate(sp.sin(x**2), (x, 0, 1))
print(f"符号结果: {expr}")
print(f"数值近似: {expr.evalf(10)}")  # 10位精度

# 生成LaTeX代码用于文档
latex_code = sp.latex(expr)
print(f"LaTeX代码: {latex_code}")

# 漂亮打印
sp.pprint(expr, use_unicode=True)
```

## 📋 快速参考卡

```python
import sympy as sp

# 定义符号
x, y = sp.symbols('x y')

# 方程求解
sp.solve(x**2 - 4, x)  # [-2, 2]

# 微分
sp.diff(sp.sin(x), x)  # cos(x)

# 积分
sp.integrate(x**2, x)  # x³/3

# 极限
sp.limit(sp.sin(x)/x, x, 0)  # 1

# 级数展开
sp.sin(x).series(x, 0, 4)  # x - x³/6 + O(x⁵)

# 矩阵运算
A = sp.Matrix([[1, 2], [3, 4]])
A.det()  # -2
```

## 🚀 高级应用示例

### 微分方程求解
```python
import sympy as sp

t = sp.symbols('t')
y = sp.Function('y')

print("=== 微分方程求解 ===")

# 定义微分方程：y'' + y = 0
ode = sp.Eq(sp.diff(y(t), t, 2) + y(t), 0)

# 求解
solution = sp.dsolve(ode, y(t))
print(f"微分方程: {ode}")
print(f"通解: {solution}")

# 添加初始条件：y(0)=1, y'(0)=0
ics = {y(0): 1, y(t).diff(t).subs(t, 0): 0}
particular_solution = sp.dsolve(ode, y(t), ics=ics)
print(f"特解: {particular_solution}")
```

### 符号优化问题
```python
import sympy as sp

x, y = sp.symbols('x y', real=True)

print("=== 符号优化问题 ===")

# 目标函数和约束
f = x**2 + y**2  # 最小化 x² + y²
constraint = sp.Eq(x + y, 1)  # 约束 x + y = 1

# 使用拉格朗日乘子法
lam = sp.symbols('λ')
L = f + lam * (x + y - 1)

# 求偏导
eq1 = sp.Eq(sp.diff(L, x), 0)
eq2 = sp.Eq(sp.diff(L, y), 0)
eq3 = sp.Eq(sp.diff(L, sp.symbols('λ')), 0)

# 求解方程组
solution = sp.solve([eq1, eq2, eq3], (x, y, sp.symbols('λ')))
print(f"优化问题: 最小化 {f}, 约束 {constraint}")
print(f"拉格朗日乘子法解: {solution}")

# 验证结果
optimal_point = solution[0]
print(f"最优点: x={optimal_point[0]}, y={optimal_point[1]}")
print(f"最优值: {f.subs({x: optimal_point[0], y: optimal_point[1]})}")
```

---

**记住**：系统会自动处理所有输出格式，您只需要专注于符号数学计算！SymPy 表达式会以美观的数学格式自动渲染，复杂公式也会被正确处理。