# 代码解释器使用指南 v2.5 (最终融合版)

## 🎯 核心原则：后端自动化，代码要简洁

### ✅ **后端已自动处理的功能：**
1. **图表捕获**：`plt.show()` 自动生成图片，无需手动编码
2. **文件管理**：`/data` 目录已配置好，支持会话持久化
3. **输出处理**：系统自动处理所有 `print()` 输出
4. **错误捕获**：后端有完整的错误处理系统

### ⚠️ **资源限制：**
1. **内存限制**：可用内存上限为6GB
2. **时间限制**：代码执行有90秒超时限制

### ❌ **模型不需要做的：**
1. 不要手动编码图表为 base64
2. 不要编写复杂的错误处理包装器
3. 不要管理文件格式转换（后端自动处理）
4. 不要处理图表标题和格式（系统自动优化）

---

## 📂 文件操作（会话工作区：`/data`）

### 从工作区读取文件
```python
import pandas as pd

# 最简单的文件读取（支持 CSV、Excel、Parquet 等）
df = pd.read_csv('/data/your_file.csv')

# 快速查看数据
print(f"数据形状: {df.shape}")
print(df.head())
```

### 保存文件到工作区
```python
# 保存处理结果
df_processed.to_csv('/data/processed_data.csv', index=False)

# 保存为高效格式（供后续使用）
import pyarrow.feather as feather
feather.write_feather(df_processed, '/data/processed_data.feather')
```

### 📝 重要说明
- **文件位置**：所有文件都在 `/data` 目录下
- **会话持久**：文件在同一会话的多次执行中保持可用
- **自动清理**：24小时后会话文件自动清理

---

## 📊 数据可视化（自动捕获）

### 基础图表
```python
import matplotlib.pyplot as plt

# 设置中文字体（后端已配置，这里只是确保）
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']

# 1. 折线图
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['value'], marker='o', linewidth=2)
plt.title('销售趋势图')  # 标题会被自动捕获
plt.xlabel('日期')
plt.ylabel('销售额')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()  # 🎯 关键：直接 show()，系统自动捕获！

# 2. 柱状图
plt.figure(figsize=(10, 6))
df.groupby('category')['sales'].sum().plot(kind='bar')
plt.title('各品类销售额')
plt.tight_layout()
plt.show()  # 🎯 关键：系统自动处理！

# 3. 散点图
plt.figure(figsize=(10, 6))
plt.scatter(df['x'], df['y'], alpha=0.6, c=df['value'], cmap='viridis')
plt.title('散点分布图')
plt.colorbar(label='值大小')
plt.tight_layout()
plt.show()  # 🎯 关键：系统自动捕获！
```

### 高级图表
```python
# 4. 子图（多图表）
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].plot(df['date'], df['value1'])
axes[0, 0].set_title('图表1')

axes[0, 1].hist(df['value2'], bins=30)
axes[0, 1].set_title('图表2')

axes[1, 0].scatter(df['x'], df['y'])
axes[1, 0].set_title('图表3')

axes[1, 1].boxplot([df['group1'], df['group2']])
axes[1, 1].set_title('图表4')

plt.tight_layout()
plt.show()  # 🎯 系统自动捕获整个图形！

# 5. 热力图（相关性矩阵）
import seaborn as sns

corr_matrix = df.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('特征相关性热力图')
plt.tight_layout()
plt.show()  # 🎯 系统自动捕获！
```

### 📝 图表说明
- **后端自动处理**：所有图表类型（Matplotlib、Seaborn、Graphviz、NetworkX）
- **标题捕获**：系统会自动提取图表标题显示给用户
- **中文字体**：后端已配置中文支持，无需担心乱码

---

## 🧹 数据处理（简洁实用版）

### 基础清洗
```python
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('/data/raw_data.csv')

# 打印基本信息
print(f"原始数据: {df.shape[0]}行 × {df.shape[1]}列")
print(f"缺失值总数: {df.isnull().sum().sum()}")

# 处理缺失值（数值列用中位数）
numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    if df[col].isnull().any():
        df[col].fillna(df[col].median(), inplace=True)

# 处理缺失值（文本列用众数）
text_cols = df.select_dtypes(include=['object']).columns
for col in text_cols:
    if df[col].isnull().any():
        if not df[col].mode().empty:
            df[col].fillna(df[col].mode()[0], inplace=True)

# 删除重复行
df = df.drop_duplicates()
print(f"清洗后数据: {df.shape[0]}行 × {df.shape[1]}列")
```

### 统计分析
```python
# 基础统计
print("数值列统计:")
print(df.describe())

# 分组统计
print("\n分组统计:")
group_stats = df.groupby('category').agg({
    'value': ['mean', 'sum', 'count', 'std']
}).round(2)
print(group_stats)

# 透视表
print("\n透视表:")
pivot = pd.pivot_table(df, 
                      values='sales', 
                      index='region', 
                      columns='month',
                      aggfunc='sum')
print(pivot)
```

---

## 🚀 性能优化（针对大文件）

### 方法1：DuckDB（SQL查询，比Pandas快3-10倍）
```python
import duckdb

# 直接查询CSV/Parquet文件（不加载到内存）
result = duckdb.sql("""
    SELECT department, 
           AVG(salary) as avg_salary,
           COUNT(*) as employee_count
    FROM read_csv_auto('/data/employees.csv')
    WHERE department IS NOT NULL
    GROUP BY department
    ORDER BY avg_salary DESC
""").df()

print("部门薪资统计:")
print(result)
```

### 方法2：分块处理（大CSV文件）
```python
# 分块读取大文件
chunks = []
for chunk in pd.read_csv('/data/large_file.csv', chunksize=50000):
    # 处理每个数据块
    processed = chunk[chunk['value'] > 0]  # 示例筛选
    chunks.append(processed)

# 合并结果
final_df = pd.concat(chunks, ignore_index=True)
print(f"处理完成: {len(final_df)}行")
```

### 方法3：高效格式转换
```python
# 将CSV转换为Feather格式（提速10-100倍）
import pyarrow.feather as feather

df = pd.read_csv('/data/large.csv')
feather.write_feather(df, '/data/large.feather')

# 下次读取时（极速）
df_fast = feather.read_feather('/data/large.feather')
```

---

## 💡 实用代码片段

### 模板1：基础分析
```python
import pandas as pd
import matplotlib.pyplot as plt

# 1. 读取数据
df = pd.read_csv('/data/data.csv')

# 2. 快速分析
print(f"数据形状: {df.shape}")
print(df.describe())

# 3. 简单可视化
df.groupby('category')['value'].mean().plot(kind='bar')
plt.title('各分类平均值')
plt.tight_layout()
plt.show()
```

### 模板2：数据清洗流水线
```python
# 1. 读取
df = pd.read_csv('/data/raw.csv')

# 2. 清洗
df = df.dropna().drop_duplicates()

# 3. 分析
print(f"清洗后: {df.shape}")
print(df.groupby('group')['value'].mean())

# 4. 保存
df.to_csv('/data/cleaned.csv', index=False)
```

### 模板3：完整报告生成
```python
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 添加资源使用提示
print(f"可用内存限制: 6GB")
print(f"建议大文件处理: 使用分块或DuckDB")
print("注意：代码执行有90秒超时限制，复杂计算请优化")

print("=" * 50)
print(f"数据分析报告 - {datetime.now().strftime('%Y-%m-%d')}")
print("=" * 50)

# 1. 数据概览
df = pd.read_csv('/data/sales.csv')
print(f"数据集: {df.shape[0]}行 × {df.shape[1]}列")
print(f"时间范围: {df['date'].min()} 至 {df['date'].max()}")

# 2. 关键指标
total_sales = df['amount'].sum()
avg_sale = df['amount'].mean()
print(f"\n关键指标:")
print(f"  总销售额: ¥{total_sales:,.2f}")
print(f"  平均交易额: ¥{avg_sale:,.2f}")

# 3. 可视化
plt.figure(figsize=(12, 5))

# 销售额趋势
plt.subplot(1, 2, 1)
df.groupby('date')['amount'].sum().plot()
plt.title('每日销售额')
plt.grid(True, alpha=0.3)

# 品类分布
plt.subplot(1, 2, 2)
df['category'].value_counts().head(10).plot(kind='bar')
plt.title('Top 10 品类')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

print("\n✅ 分析完成！")
```

---

## ⚠️ 重要提醒（基于后端特性）

### 后端已配置，无需担心：
1. **中文字体**：已安装 WenQuanYi 字体，图表无乱码
2. **图表捕获**：所有 `plt.show()` 自动转换为图片
3. **内存管理**：容器限制 6GB，自动处理内存溢出
4. **文件权限**：`/data` 目录有读写权限

### 代码执行限制：
1. **内存限制**：可用内存上限为6GB，处理大文件时建议使用分块处理或DuckDB
2. **超时限制**：代码执行有90秒超时限制，复杂计算请优化算法或分步执行

### 代码编写原则：
1. **保持简洁**：写直白的 Python 代码，无需复杂包装
2. **相信后端**：系统会自动处理图表、错误、输出格式
3. **使用标准库**：Pandas、Matplotlib、NumPy 等已预装
4. **关注业务逻辑**：让后端处理技术细节

---

## 🔧 故障排除

### 常见问题：
1. **文件不存在**：检查文件名是否正确，注意大小写
2. **内存不足**：使用分块处理或 DuckDB 查询
3. **图表不显示**：确保调用了 `plt.show()`
4. **中文乱码**：后端已配置字体，无需额外处理
5. **执行超时**：代码执行超过90秒限制，请优化算法或分步执行

### 性能建议：
- **小文件**：直接使用 Pandas
- **大文件**：使用 DuckDB 或分块处理
- **重复计算**：保存中间结果到 `/data` 目录
- **复杂图表**：后端会自动优化渲染
- **内存使用**：可用内存限制为6GB，处理大型数据集时请注意使用分块或DuckDB以降低内存占用
- **执行时间**：代码执行有90秒超时限制，对于复杂计算建议优化算法或分解为多个步骤执行

---

## 📋 快速参考卡

```python
# 读取文件
df = pd.read_csv('/data/file.csv')

# 保存文件
df.to_csv('/data/output.csv', index=False)

# 显示图表
plt.plot(x, y)
plt.show()  # 🎯 关键！

# 打印结果
print(df.describe())

# 高效查询（大文件）
import duckdb
result = duckdb.sql("SELECT * FROM read_csv_auto('/data/big.csv')").df()

# 添加资源使用提示
print(f"可用内存限制: 6GB")
print(f"建议大文件处理: 使用分块或DuckDB")
print("注意：代码执行有90秒超时限制，复杂计算请优化")
```

---

**最终原则**：写你**想写**的代码，后端会处理**该处理**的细节！图表、文件、输出都交给系统，你只需要关注数据分析和业务逻辑。