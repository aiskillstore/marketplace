# SciPy 科学计算指南 (v2.5)

## 🎯 工具概述
**环境特性**：基于 SciPy 的科学计算环境，支持优化、积分、信号处理等
**输出原则**：系统自动处理结果输出，直接打印结果，图表使用 `plt.show()`

## 🔧 核心模块概览

### 主要功能模块：
- **优化算法** (`scipy.optimize`) - 函数最小化、方程求解
- **积分计算** (`scipy.integrate`) - 数值积分、微分方程
- **信号处理** (`scipy.signal`) - 滤波器、频谱分析
- **线性代数** (`scipy.linalg`) - 矩阵运算、线性系统
- **统计函数** (`scipy.stats`) - 概率分布、统计检验
- **空间算法** (`scipy.spatial`) - 空间数据、距离计算

## ✅ 代码解释器适配说明
- **直接打印**：所有计算结果直接使用 `print()` 输出
- **自动图表**：使用 `plt.show()` 即可自动捕获图表
- **完整集成**：SciPy 已预装，无需额外安装
- **内存优化**：大计算时注意内存使用，可分批处理

## 🎯 优化与方程求解

### 函数最小化
```python
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

print("=== 单变量函数优化 ===")

# 1. 单变量函数优化
def single_variable_func(x):
    return (x - 3)**2 * np.sin(x) + x**2

result = optimize.minimize_scalar(single_variable_func, bounds=(0, 10), method='bounded')
print(f"最优解: x = {result.x:.4f}, 函数值: {result.fun:.4f}")

# 可视化
x_plot = np.linspace(0, 10, 100)
y_plot = single_variable_func(x_plot)
plt.figure(figsize=(10, 6))
plt.plot(x_plot, y_plot, label='f(x)')
plt.axvline(result.x, color='red', linestyle='--', label=f'最优解 x={result.x:.3f}')
plt.title('单变量函数优化')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### 多变量优化
```python
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

print("=== 多变量函数优化 ===")

# Rosenbrock 函数优化
def rosenbrock(x):
    return sum(100.0 * (x[1:] - x[:-1]**2)**2 + (1 - x[:-1])**2)

x0 = np.array([-1.2, 1.0])
result = optimize.minimize(rosenbrock, x0, method='BFGS')

print(f"初始点: {x0}")
print(f"最优点: {result.x}")
print(f"最优值: {result.fun:.6f}")
print(f"迭代次数: {result.nit}")
print(f"求解成功: {result.success}")

# 可视化
x = np.linspace(-2, 2, 100)
y = np.linspace(-1, 3, 100)
X, Y = np.meshgrid(x, y)
Z = np.zeros_like(X)

for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        Z[i,j] = rosenbrock([X[i,j], Y[i,j]])

plt.figure(figsize=(10, 8))
contour = plt.contour(X, Y, Z, levels=50)
plt.clabel(contour, inline=True, fontsize=8)
plt.plot(result.x[0], result.x[1], 'ro', markersize=10, label='最优解')
plt.title('Rosenbrock 函数优化')
plt.legend()
plt.tight_layout()
plt.show()
```

### 约束优化
```python
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

print("=== 约束优化 ===")

# 带约束的优化问题
def objective(x):
    return x[0]**2 + x[1]**2

def constraint1(x):
    return x[0] + x[1] - 1  # x + y >= 1

constraints = [{'type': 'ineq', 'fun': constraint1}]
bounds = [(0, None), (0, None)]

result = optimize.minimize(objective, [0.5, 0.5], 
                         method='SLSQP', bounds=bounds, 
                         constraints=constraints)

print(f"约束优化结果:")
print(f"最优点: {result.x}")
print(f"最优值: {result.fun:.4f}")
print(f"约束满足: {result.success}")
print(f"迭代次数: {result.nit}")

# 可视化约束区域
x_const = np.linspace(0, 2, 100)
y_const = np.linspace(0, 2, 100)
X, Y = np.meshgrid(x_const, y_const)
Z = objective([X, Y])

plt.figure(figsize=(10, 8))
plt.contourf(X, Y, Z, levels=20, alpha=0.6)
plt.contour(X, Y, Z, levels=10, colors='black', alpha=0.4)

# 绘制约束条件
y_constraint = 1 - x_const
plt.plot(x_const, y_constraint, 'r-', linewidth=2, label='x + y = 1')
plt.fill_between(x_const, y_constraint, 2, alpha=0.3, color='gray', label='可行域')

plt.plot(result.x[0], result.x[1], 'go', markersize=10, label='最优解')
plt.xlim(0, 2)
plt.ylim(0, 2)
plt.title('约束优化问题')
plt.legend()
plt.tight_layout()
plt.show()
```

### 方程求解
```python
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

print("=== 非线性方程求解 ===")

# 定义非线性方程组
def equations(vars):
    x, y = vars
    eq1 = x**2 + y**2 - 25
    eq2 = x**2 - y - 5
    return [eq1, eq2]

# 初始猜测
initial_guess = [4, 2]

# 求解方程组
result = optimize.root(equations, initial_guess, method='hybr')

print(f"求解结果:")
print(f"解: x = {result.x[0]:.4f}, y = {result.x[1]:.4f}")
print(f"函数值: {result.fun}")
print(f"求解成功: {result.success}")

# 可视化
fig, ax = plt.subplots(figsize=(8, 8))
circle = plt.Circle((0, 0), 5, color='blue', fill=False, linewidth=2, label='x² + y² = 25')
ax.add_patch(circle)

x_parabola = np.linspace(-5, 5, 100)
y_parabola = x_parabola**2 - 5
ax.plot(x_parabola, y_parabola, 'r-', linewidth=2, label='x² - y = 5')

# 绘制交点
ax.plot(result.x[0], result.x[1], 'go', markersize=10, label='解')
ax.text(result.x[0]+0.2, result.x[1]+0.2, f'({result.x[0]:.2f}, {result.x[1]:.2f})')

ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.legend()
plt.title('非线性方程组求解')
plt.tight_layout()
plt.show()
```

## 📐 数值积分

### 定积分计算
```python
from scipy import integrate
import numpy as np
import matplotlib.pyplot as plt

print("=== 数值积分计算 ===")

# 1. 单变量积分
def func1(x):
    return np.exp(-x**2) * np.sin(x)

integral1, error1 = integrate.quad(func1, 0, np.inf)

print(f"积分结果: {integral1:.6f}")
print(f"估计误差: {error1:.2e}")
print(f"有效位数: {-np.log10(error1/abs(integral1)):.1f}")

# 可视化被积函数
x_plot = np.linspace(0, 3, 100)
y_plot = func1(x_plot)

plt.figure(figsize=(10, 6))
plt.plot(x_plot, y_plot, 'b-', linewidth=2, label='被积函数')
plt.fill_between(x_plot, y_plot, alpha=0.3, label=f'积分面积 ≈ {integral1:.4f}')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.title(f'定积分: ∫₀^∞ e^(-x²)sin(x)dx = {integral1:.6f}')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### 多重积分
```python
from scipy import integrate
import numpy as np

print("=== 多重积分计算 ===")

# 二重积分
def integrand(y, x):
    return np.sin(x) * np.cos(y)

# 积分区域: x从0到π, y从0到π/2
result, error = integrate.dblquad(integrand, 0, np.pi, 
                                 lambda x: 0, 
                                 lambda x: np.pi/2)

print(f"二重积分结果: {result:.6f}")
print(f"估计误差: {error:.2e}")

# 三重积分
def integrand3(z, y, x):
    return x * y * z

result3, error3 = integrate.tplquad(integrand3, 
                                   0, 1,                    # x bounds
                                   lambda x: 0, 
                                   lambda x: 1 - x,        # y bounds
                                   lambda x, y: 0, 
                                   lambda x, y: 1 - x - y) # z bounds

print(f"\n三重积分结果: {result3:.6f}")
print(f"估计误差: {error3:.2e}")
print(f"理论值: 1/120 = {1/120:.6f}")
```

### 微分方程求解
```python
from scipy import integrate
import numpy as np
import matplotlib.pyplot as plt

print("=== 微分方程数值求解 ===")

# Lotka-Volterra 捕食者-被捕食者模型
def ode_system(t, y):
    alpha, beta, delta, gamma = 1.0, 0.1, 0.075, 1.5
    prey, predator = y
    dprey_dt = alpha * prey - beta * prey * predator
    dpredator_dt = delta * prey * predator - gamma * predator
    return [dprey_dt, dpredator_dt]

# 求解微分方程
t_span = (0, 50)
y0 = [10, 5]  # 初始种群
t_eval = np.linspace(0, 50, 1000)
solution = integrate.solve_ivp(ode_system, t_span, y0, t_eval=t_eval, method='RK45')

print(f"求解成功: {solution.success}")
print(f"计算步数: {len(solution.t)}")
print(f"最终被捕食者数量: {solution.y[0, -1]:.2f}")
print(f"最终捕食者数量: {solution.y[1, -1]:.2f}")

# 可视化种群动态
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 时域图
axes[0].plot(solution.t, solution.y[0], 'g-', label='被捕食者', linewidth=2)
axes[0].plot(solution.t, solution.y[1], 'r-', label='捕食者', linewidth=2)
axes[0].set_xlabel('时间')
axes[0].set_ylabel('种群数量')
axes[0].set_title('Lotka-Volterra 模型种群动态')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 相图
axes[1].plot(solution.y[0], solution.y[1], 'b-', linewidth=1)
axes[1].scatter(solution.y[0, 0], solution.y[1, 0], color='green', s=100, label='起点', zorder=5)
axes[1].scatter(solution.y[0, -1], solution.y[1, -1], color='red', s=100, label='终点', zorder=5)
axes[1].set_xlabel('被捕食者数量')
axes[1].set_ylabel('捕食者数量')
axes[1].set_title('相图')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## 📡 信号处理

### 信号滤波与频谱分析
```python
from scipy import signal
from scipy.fft import fft, fftfreq
import numpy as np
import matplotlib.pyplot as plt

print("=== 信号处理与频谱分析 ===")

# 生成测试信号
t = np.linspace(0, 1, 1000, endpoint=False)
original_signal = (np.sin(2 * np.pi * 5 * t) + 
                  0.5 * np.sin(2 * np.pi * 20 * t) + 
                  0.2 * np.sin(2 * np.pi * 50 * t))

# 添加噪声
np.random.seed(42)
noisy_signal = original_signal + 0.3 * np.random.normal(size=len(t))

print(f"信号长度: {len(t)}")
print(f"采样频率: {1/(t[1]-t[0]):.0f} Hz")
print(f"奈奎斯特频率: {0.5/(t[1]-t[0]):.0f} Hz")

# 设计低通滤波器
nyquist = 0.5/(t[1]-t[0])  # 奈奎斯特频率
cutoff = 15 / nyquist
b, a = signal.butter(4, cutoff, btype='low')
filtered_signal = signal.filtfilt(b, a, noisy_signal)

print(f"滤波器阶数: 4")
print(f"截止频率: 15 Hz")

# 可视化信号
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 时域信号
axes[0, 0].plot(t[:100], original_signal[:100], 'b-', alpha=0.7, label='原始信号')
axes[0, 0].plot(t[:100], noisy_signal[:100], 'r-', alpha=0.5, label='带噪声信号')
axes[0, 0].plot(t[:100], filtered_signal[:100], 'g-', linewidth=2, label='滤波后信号')
axes[0, 0].set_xlabel('时间 (s)')
axes[0, 0].set_ylabel('幅度')
axes[0, 0].set_title('时域信号（前100点）')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 频域分析
fft_original = fft(original_signal)
fft_noisy = fft(noisy_signal)
fft_filtered = fft(filtered_signal)
freqs = fftfreq(len(t), t[1] - t[0])
positive_freq_idx = np.where((freqs > 0) & (freqs < 100))

axes[0, 1].plot(freqs[positive_freq_idx], np.abs(fft_original[positive_freq_idx]), 'b-', label='原始频谱')
axes[0, 1].plot(freqs[positive_freq_idx], np.abs(fft_noisy[positive_freq_idx]), 'r-', alpha=0.5, label='噪声频谱')
axes[0, 1].plot(freqs[positive_freq_idx], np.abs(fft_filtered[positive_freq_idx]), 'g-', label='滤波频谱')
axes[0, 1].set_xlabel('频率 (Hz)')
axes[0, 1].set_ylabel('幅度')
axes[0, 1].set_title('频域分析')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].axvline(15, color='gray', linestyle='--', label='截止频率')

# 滤波器频率响应
w, h = signal.freqz(b, a, worN=2000)
axes[1, 0].plot(0.5 * w / np.pi * 500, 20 * np.log10(np.abs(h)), 'b-')
axes[1, 0].set_xlabel('频率 (Hz)')
axes[1, 0].set_ylabel('增益 (dB)')
axes[1, 0].set_title('滤波器频率响应')
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].axvline(15, color='gray', linestyle='--', label='截止频率')

# 误差分析
axes[1, 1].plot(t[:100], filtered_signal[:100] - original_signal[:100], 'purple')
axes[1, 1].set_xlabel('时间 (s)')
axes[1, 1].set_ylabel('误差')
axes[1, 1].set_title('滤波误差（前100点）')
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].axhline(0, color='black', linestyle='-', alpha=0.3)

plt.tight_layout()
plt.show()
```

## 🧮 线性代数

### 矩阵运算与分解
```python
from scipy import linalg
import numpy as np

print("=== 线性代数运算 ===")

# 矩阵运算示例
A = np.array([[4, 2, 1], 
              [2, 5, 3], 
              [1, 3, 6]], dtype=float)
b = np.array([1, 2, 3], dtype=float)

print("矩阵 A:")
print(A)
print(f"\n向量 b: {b}")

# 矩阵性质
det_A = linalg.det(A)
cond_A = linalg.cond(A)
print(f"\n行列式: {det_A:.4f}")
print(f"条件数: {cond_A:.4f}")
print(f"矩阵是否对称: {np.allclose(A, A.T)}")
print(f"矩阵是否正定: {np.all(linalg.eigvals(A) > 0)}")

# 线性方程组求解
x = linalg.solve(A, b)
print(f"\n方程解: {x}")

# 验证解
print(f"验证 A*x: {A.dot(x)}")
print(f"目标 b: {b}")
print(f"残差范数: {np.linalg.norm(A.dot(x) - b):.2e}")

# 特征值分解
eigenvalues, eigenvectors = linalg.eig(A)
print(f"\n特征值: {eigenvalues}")
print("特征向量矩阵:")
print(eigenvectors)

# 奇异值分解
U, s, Vh = linalg.svd(A)
print(f"\n奇异值: {s}")
print(f"奇异值条件数: {s.max()/s.min():.4f}")
```

### 稀疏矩阵处理
```python
from scipy import sparse
from scipy.sparse import linalg as splinalg
import numpy as np

print("=== 稀疏矩阵处理 ===")

# 创建稀疏矩阵
n = 100
diag = np.ones(n)
offsets = [0, 1, -1]
data = [2*diag, -1*diag, -1*diag]
A_sparse = sparse.diags(data, offsets, format='csr')

print(f"稀疏矩阵形状: {A_sparse.shape}")
print(f"非零元素数量: {A_sparse.nnz}")
print(f"稀疏度: {100 * A_sparse.nnz / (n*n):.2f}%")

# 创建稠密向量进行比较
b_dense = np.random.randn(n)

# 稀疏求解
print("\n使用稀疏求解器:")
x_sparse = splinalg.spsolve(A_sparse, b_dense)
print(f"求解完成，解的形状: {x_sparse.shape}")

# 与稠密求解比较
A_dense = A_sparse.toarray()
print("\n与稠密求解器比较:")
x_dense = linalg.solve(A_dense, b_dense)
residual = np.linalg.norm(A_dense @ x_sparse - b_dense)
print(f"残差范数: {residual:.2e}")
print(f"与稠密解的最大差异: {np.max(np.abs(x_sparse - x_dense)):.2e}")
```

## 📊 统计计算

### 概率分布与统计检验
```python
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

print("=== 统计计算与概率分布 ===")

# 生成正态分布样本
np.random.seed(42)
normal_samples = np.random.normal(loc=0, scale=1, size=1000)

print(f"样本数量: {len(normal_samples)}")
print(f"样本均值: {np.mean(normal_samples):.4f}")
print(f"样本标准差: {np.std(normal_samples):.4f}")

# 正态性检验
k2_statistic, p_value = stats.normaltest(normal_samples)
print(f"\n正态性检验:")
print(f"统计量: {k2_statistic:.4f}")
print(f"p值: {p_value:.4f}")
print(f"是否正态分布 (α=0.05): {p_value > 0.05}")

# 拟合分布参数
params = stats.norm.fit(normal_samples)
print(f"\n拟合正态分布参数:")
print(f"均值: {params[0]:.4f}")
print(f"标准差: {params[1]:.4f}")

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 直方图与理论PDF
axes[0].hist(normal_samples, bins=30, density=True, alpha=0.7, label='样本直方图')
x = np.linspace(-4, 4, 100)
axes[0].plot(x, stats.norm.pdf(x), 'r-', linewidth=2, label='理论PDF')
axes[0].set_xlabel('值')
axes[0].set_ylabel('概率密度')
axes[0].set_title('正态分布样本与理论PDF')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# QQ图
stats.probplot(normal_samples, dist="norm", plot=axes[1])
axes[1].set_title('正态QQ图')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 假设检验
```python
from scipy import stats
import numpy as np

print("=== 假设检验 ===")

# 生成两组样本
np.random.seed(42)
group1 = np.random.normal(loc=10, scale=2, size=50)
group2 = np.random.normal(loc=12, scale=2, size=50)

print(f"第一组: 均值={np.mean(group1):.2f}, 标准差={np.std(group1):.2f}, n={len(group1)}")
print(f"第二组: 均值={np.mean(group2):.2f}, 标准差={np.std(group2):.2f}, n={len(group2)}")

# t检验（独立样本）
t_statistic, p_value = stats.ttest_ind(group1, group2)
print(f"\n独立样本t检验:")
print(f"t统计量: {t_statistic:.4f}")
print(f"p值: {p_value:.4f}")
print(f"是否显著不同 (α=0.05): {p_value < 0.05}")

# 方差齐性检验
f_statistic, p_value_var = stats.levene(group1, group2)
print(f"\n方差齐性检验:")
print(f"F统计量: {f_statistic:.4f}")
print(f"p值: {p_value_var:.4f}")
print(f"方差是否齐 (α=0.05): {p_value_var > 0.05}")

# 相关性检验
correlation, p_value_corr = stats.pearsonr(group1, np.random.permutation(group2))
print(f"\n相关性检验:")
print(f"相关系数: {correlation:.4f}")
print(f"p值: {p_value_corr:.4f}")
print(f"是否显著相关 (α=0.05): {p_value_corr < 0.05}")
```

## 🧭 空间算法

### 空间数据结构
```python
from scipy import spatial
import numpy as np
import matplotlib.pyplot as plt

print("=== 空间算法与数据结构 ===")

# 创建随机点集
np.random.seed(42)
points = np.random.rand(30, 2) * 10

print(f"点集大小: {points.shape}")
print(f"坐标范围: X[{points[:,0].min():.2f}, {points[:,0].max():.2f}], "
      f"Y[{points[:,1].min():.2f}, {points[:,1].max():.2f}]")

# 计算凸包
hull = spatial.ConvexHull(points)
print(f"\n凸包计算:")
print(f"凸包顶点数量: {len(hull.vertices)}")
print(f"凸包面积: {hull.area:.2f}")
print(f"凸包体积: {hull.volume:.2f}")

# 最近邻搜索
tree = spatial.KDTree(points)
distances, indices = tree.query(points, k=3)  # 每个点找3个最近邻
print(f"\n最近邻搜索:")
print(f"平均最近距离: {distances[:,1].mean():.2f}")
print(f"最远最近距离: {distances[:,1].max():.2f}")

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 点集与凸包
axes[0].scatter(points[:,0], points[:,1], c='blue', s=50, label='数据点')
for simplex in hull.simplices:
    axes[0].plot(points[simplex, 0], points[simplex, 1], 'r-', linewidth=2)
axes[0].set_title('空间点集与凸包')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].axis('equal')

# 最近邻连接
axes[1].scatter(points[:,0], points[:,1], c='blue', s=50, label='数据点')
for i in range(len(points)):
    for j in range(1, 3):  # 连接第1和第2近邻
        neighbor_idx = indices[i, j]
        axes[1].plot([points[i,0], points[neighbor_idx,0]], 
                    [points[i,1], points[neighbor_idx,1]], 
                    'gray', alpha=0.3, linewidth=0.5)
axes[1].set_title('最近邻连接图')
axes[1].grid(True, alpha=0.3)
axes[1].axis('equal')

plt.tight_layout()
plt.show()
```

## ⚠️ 使用注意事项

### ✅ 推荐做法：
1. **模块导入**：按需导入子模块 `from scipy import optimize, integrate, stats`
2. **数值稳定性**：注意矩阵条件数，使用条件良好的问题
3. **内存管理**：大数据使用稀疏矩阵或分块处理
4. **结果验证**：检查求解器的 `success` 标志和残差

### ❌ 避免的操作：
1. 不要重复计算可缓存的结果
2. 不要使用默认参数处理病态问题
3. 不要忽略求解器的收敛状态
4. 不要在循环中重复创建大型数组

### ⚠️ 内存限制提醒：
在执行大型计算前，请添加内存使用提醒：
```python
# 在大型计算前添加提醒
print("注意：以下计算可能需要较大内存，如有问题请分块处理")
```

### 📊 性能监控：
添加性能监控代码可以帮助了解计算资源消耗：
```python
import time
import psutil

start_time = time.time()
process = psutil.Process()
initial_memory = process.memory_info().rss / 1024**2

# ... 执行计算 ...

end_time = time.time()
final_memory = process.memory_info().rss / 1024**2

print(f"计算时间: {end_time - start_time:.2f}秒")
print(f"内存使用: {final_memory - initial_memory:.2f} MB")
```

### 🔧 错误处理：
```python
# 在关键计算周围添加try-except
try:
    result = optimize.minimize_scalar(func, bounds=(0, 10))
    if result.success:
        print(f"优化成功: x={result.x:.4f}")
    else:
        print(f"优化失败: {result.message}")
except Exception as e:
    print(f"计算错误: {e}")
    # 提供替代方案
    print("尝试使用不同的初始值或方法...")
```

### 💡 性能优化建议：
```python
# 1. 使用向量化操作替代循环
# 2. 对于大型线性系统，使用稀疏矩阵
# 3. 重复计算时缓存中间结果
# 4. 使用适当精度，避免不必要的高精度计算
# 5. 大型计算前添加内存使用提醒
# 6. 监控计算时间和内存消耗
# 7. 为关键计算添加错误处理机制
```

## 📋 快速参考卡

```python
# 优化
from scipy import optimize
result = optimize.minimize(f, x0, method='BFGS')

# 积分
from scipy import integrate
result, error = integrate.quad(f, a, b)

# 信号处理
from scipy import signal
filtered = signal.filtfilt(b, a, signal)

# 线性代数
from scipy import linalg
x = linalg.solve(A, b)

# 统计
from scipy import stats
t, p = stats.ttest_ind(group1, group2)

# 空间算法
from scipy import spatial
hull = spatial.ConvexHull(points)
```

## 🚀 高级应用示例

### 全局优化
```python
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

print("=== 全局优化问题 ===")

# 多峰函数
def multimodal_func(x):
    return np.sin(5*x) + 0.5*x**2 + 0.1*np.random.randn() if len(x.shape)==0 else 0.1*np.random.randn(x.shape[0])

# 使用 basinhopping 进行全局优化
result = optimize.basinhopping(multimodal_func, x0=0, niter=100, 
                              stepsize=1.0, minimizer_kwargs={"method": "BFGS"})

print(f"全局优化结果:")
print(f"最优解: x = {result.x[0]:.4f}")
print(f"最优值: {result.fun:.4f}")
print(f"发现局部极值数量: {result.nit}")

# 可视化
x_plot = np.linspace(-5, 5, 1000)
y_plot = np.sin(5*x_plot) + 0.5*x_plot**2

plt.figure(figsize=(12, 6))
plt.plot(x_plot, y_plot, 'b-', linewidth=2, label='目标函数')
plt.axvline(result.x, color='red', linestyle='--', linewidth=2, label='全局最优解')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.title('多峰函数全局优化')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### 偏微分方程求解
```python
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt

print("=== 偏微分方程数值求解 ===")

# 热传导方程（简化示例）
# 使用有限差分法
L = 1.0  # 杆长
N = 50   # 空间网格数
T = 0.5  # 总时间
dt = 0.001  # 时间步长

# 空间网格
x = np.linspace(0, L, N+1)
dx = x[1] - x[0]

# 初始条件（中心加热）
u = np.exp(-100*(x - L/2)**2)

# 时间步进
for n in range(int(T/dt)):
    # 使用显式欧拉法
    u[1:-1] = u[1:-1] + dt/dx**2 * (u[:-2] - 2*u[1:-1] + u[2:])

print(f"热传导方程数值求解完成")
print(f"空间网格: {N+1} 点")
print(f"时间步数: {int(T/dt)}")
print(f"最终温度分布范围: [{u.min():.4f}, {u.max():.4f}]")

# 可视化
plt.figure(figsize=(10, 6))
plt.plot(x, np.exp(-100*(x - L/2)**2), 'b--', linewidth=2, label='初始温度分布')
plt.plot(x, u, 'r-', linewidth=2, label=f'最终温度分布 (t={T})')
plt.xlabel('位置 x')
plt.ylabel('温度 u(x,t)')
plt.title('热传导方程数值解')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

---

**记住**：系统会自动处理所有输出格式，您只需要专注于科学计算逻辑！SciPy 函数会以适当格式显示结果，复杂计算也会被正确处理。