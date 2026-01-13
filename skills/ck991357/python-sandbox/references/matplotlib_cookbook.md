# 可视化图表生成指南 (v3.0 - 完整工作流版)

## 🚀 核心使用方法

**重要提示**：您只需要专注于绘图逻辑，系统会自动处理图像输出。

### 必须遵循的原则：
1. **正常导入**：`import matplotlib.pyplot as plt`
2. **正常绘图**：使用标准的matplotlib函数
3. **无需编码**：禁止使用`io.BytesIO`、`base64`等手动编码
4. **推荐使用**：在代码末尾调用`plt.show()`

---

## 📊 可直接使用的代码模板（从数据文件开始）

### 模板1：读取上传文件并生成条形图
```python
import matplotlib.pyplot as plt
import pandas as pd
import os

# 检查可用的数据文件
data_dir = '/data'
files = os.listdir(data_dir) if os.path.exists(data_dir) else []
print(f"可用文件: {files}")

if files:
    # 选择第一个CSV文件
    csv_files = [f for f in files if f.endswith('.csv')]
    if csv_files:
        file_path = f'/data/{csv_files[0]}'
        df = pd.read_csv(file_path)
        print(f"读取文件: {csv_files[0]}, 形状: {df.shape}")
        print(df.head())
        
        # 假设数据有category和value列
        if 'category' in df.columns and 'value' in df.columns:
            plt.figure(figsize=(12, 7))
            plt.bar(df['category'], df['value'], 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFE66D'])
            plt.title(f'{csv_files[0]} - 数据分布')
            plt.xlabel('类别')
            plt.ylabel('数值')
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.3)
            plt.tight_layout()
            plt.show()
        else:
            print("数据格式不匹配，生成示例图表")
            generate_sample_chart()
    else:
        print("没有找到CSV文件，生成示例图表")
        generate_sample_chart()
else:
    print("没有上传文件，生成示例图表")
    generate_sample_chart()

def generate_sample_chart():
    """生成示例图表"""
    import numpy as np
    
    # 示例数据
    categories = ['A', 'B', 'C', 'D', 'E']
    values = np.random.randint(50, 200, 5)
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories, values, 
                  color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFE66D'])
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{int(height)}', ha='center', va='bottom')
    
    plt.title('示例条形图 - 数据分布')
    plt.xlabel('产品类别')
    plt.ylabel('销售额 (万元)')
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
```

### 模板2：时间序列折线图（适合月度报告）
```python
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# 生成示例时间序列数据
def create_time_series_data():
    dates = [datetime(2024, 1, 1) + timedelta(days=i*7) for i in range(12)]
    values = [100, 120, 90, 150, 180, 200, 170, 220, 240, 210, 250, 280]
    
    df = pd.DataFrame({
        'date': dates,
        'value': values,
        'target': [130] * 12
    })
    return df

df = create_time_series_data()

plt.figure(figsize=(14, 8))

# 实际值折线
plt.plot(df['date'], df['value'], 
         marker='o', 
         linestyle='-', 
         linewidth=3, 
         markersize=8,
         color='#2E86AB',
         label='实际销售额')

# 目标线
plt.plot(df['date'], df['target'], 
         linestyle='--', 
         linewidth=2,
         color='#A23B72',
         label='目标线')

# 填充区域
plt.fill_between(df['date'], df['value'], df['target'], 
                 where=(df['value'] >= df['target']),
                 alpha=0.3, color='#4ECDC4', label='超额完成')
plt.fill_between(df['date'], df['value'], df['target'],
                 where=(df['value'] < df['target']),
                 alpha=0.3, color='#FF6B6B', label='未达目标')

plt.title('2024年销售额趋势分析', fontsize=18, pad=20)
plt.xlabel('日期', fontsize=14)
plt.ylabel('销售额 (万元)', fontsize=14)
plt.legend(fontsize=12, loc='upper left')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
```

### 模板3：多子图仪表板
```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 创建示例数据
np.random.seed(42)
n_points = 100
data = {
    'x': np.random.randn(n_points),
    'y': np.random.randn(n_points),
    'category': np.random.choice(['A', 'B', 'C'], n_points),
    'value': np.random.randint(1, 100, n_points)
}
df = pd.DataFrame(data)

# 创建2x2的子图布局
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('综合数据分析仪表板', fontsize=20, fontweight='bold')

# 1. 散点图
scatter = axes[0, 0].scatter(df['x'], df['y'], 
                             c=df['value'], 
                             s=df['value']*2,
                             alpha=0.6,
                             cmap='viridis')
axes[0, 0].set_title('分布散点图（颜色=数值，大小=数值）')
axes[0, 0].set_xlabel('X轴')
axes[0, 0].set_ylabel('Y轴')
axes[0, 0].grid(True, alpha=0.3)
plt.colorbar(scatter, ax=axes[0, 0])

# 2. 箱线图
box_data = [df[df['category'] == cat]['value'].values for cat in ['A', 'B', 'C']]
bp = axes[0, 1].boxplot(box_data, labels=['A类', 'B类', 'C类'],
                        patch_artist=True,
                        boxprops=dict(facecolor='lightblue', color='darkblue'),
                        medianprops=dict(color='red', linewidth=2))
axes[0, 1].set_title('各类别数据分布')
axes[0, 1].set_ylabel('数值')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# 3. 饼图（类别占比）
category_counts = df['category'].value_counts()
axes[1, 0].pie(category_counts.values, 
               labels=category_counts.index,
               autopct='%1.1f%%',
               colors=['#FF6B6B', '#4ECDC4', '#45B7D1'],
               startangle=90,
               explode=(0.05, 0, 0))
axes[1, 0].set_title('类别占比分布')
axes[1, 0].axis('equal')  # 确保饼图是圆形

# 4. 直方图
axes[1, 1].hist(df['value'], bins=20, 
                color='#96CEB4', 
                edgecolor='black',
                alpha=0.7)
axes[1, 1].axvline(df['value'].mean(), color='red', linestyle='--', linewidth=2)
axes[1, 1].text(df['value'].mean()*1.05, axes[1, 1].get_ylim()[1]*0.9,
               f'均值: {df["value"].mean():.1f}', 
               color='red', fontsize=10)
axes[1, 1].set_title('数值分布直方图')
axes[1, 1].set_xlabel('数值')
axes[1, 1].set_ylabel('频数')
axes[1, 1].grid(True, alpha=0.3, axis='y')

plt.tight_layout(rect=[0, 0, 1, 0.96])  # 为标题留出空间
plt.show()
```

---

## 🎨 图表类型选择指南

### 根据分析目的选择图表：

| 分析目的 | 推荐图表 | 示例场景 |
|---------|----------|----------|
| **数据比较** | 条形图、柱状图 | 产品销售额对比、地区业绩排名 |
| **趋势分析** | 折线图、面积图 | 月度销售趋势、用户增长趋势 |
| **分布分析** | 直方图、箱线图、密度图 | 用户年龄分布、收入分布 |
| **比例分析** | 饼图、环形图、旭日图 | 市场份额、预算分配 |
| **关系分析** | 散点图、气泡图、热力图 | 广告投入与销售关系、相关性分析 |
| **组成分析** | 堆叠条形图、瀑布图 | 收入构成分析、成本结构 |
| **地理分析** | 地图、等值线图 | 地区分布、人口密度 |

---

## 🏗️ 流程图与架构图生成指南

### Graphviz 专业流程图（修正版）

#### 基础流程图模板 - 必须赋值给变量并调用
```python
from graphviz import Digraph

# 🎯 关键：1. 创建图表对象 2. 赋值给变量 3. 确保在全局作用域
def create_basic_flowchart():
    dot = Digraph('BusinessProcess', comment='业务流程')
    dot.attr(rankdir='LR', size='10,8')
    
    # 设置节点样式
    dot.node('start', '开始', shape='ellipse', color='green', style='filled', fillcolor='lightgreen')
    dot.node('input', '输入数据', shape='box', style='filled', fillcolor='lightblue')
    dot.node('process', '数据处理', shape='box', style='filled', fillcolor='lightblue')
    dot.node('analyze', '分析结果', shape='box', style='filled', fillcolor='lightblue')
    dot.node('decision', '是否通过？', shape='diamond', color='blue', style='filled', fillcolor='lightyellow')
    dot.node('approve', '审批通过', shape='box', style='filled', fillcolor='lightgreen')
    dot.node('reject', '返回修改', shape='box', style='filled', fillcolor='lightcoral')
    dot.node('end', '结束', shape='ellipse', color='red', style='filled', fillcolor='lightcoral')
    
    # 添加边
    dot.edge('start', 'input', label='启动')
    dot.edge('input', 'process', label='数据验证')
    dot.edge('process', 'analyze', label='执行分析')
    dot.edge('analyze', 'decision', label='生成报告')
    dot.edge('decision', 'approve', label='是', color='green')
    dot.edge('decision', 'reject', label='否', color='red')
    dot.edge('approve', 'end', label='完成')
    dot.edge('reject', 'process', label='重新处理', color='orange', style='dashed')
    
    return dot

# 🎯 关键：将图表对象赋值给全局变量
flowchart = create_basic_flowchart()

# 🎯 关键：图表对象必须在全局作用域中存在
# 系统会自动检测并捕获名为 'flowchart' 的Digraph对象
```

#### 系统架构图模板
```python
from graphviz import Digraph

def create_system_architecture():
    dot = Digraph('SystemArchitecture', format='png')
    dot.attr(rankdir='TB', size='14,10', compound='true')
    
    # 前端层集群
    with dot.subgraph(name='cluster_frontend') as c:
        c.attr(label='前端层', style='filled', color='lightgrey', fontsize='16')
        c.node('web_app', 'Web应用', shape='box3d', style='filled', fillcolor='lightblue')
        c.node('mobile_app', '移动端', shape='box3d', style='filled', fillcolor='lightblue')
        c.node('api_gateway', 'API网关', shape='pentagon', style='filled', fillcolor='lightyellow')
        
    # 后端服务集群
    with dot.subgraph(name='cluster_backend') as c:
        c.attr(label='后端服务层', style='filled', color='lightblue', fontsize='16')
        c.node('auth_service', '认证服务', shape='component', style='filled', fillcolor='lightgreen')
        c.node('user_service', '用户服务', shape='component', style='filled', fillcolor='lightgreen')
        c.node('product_service', '产品服务', shape='component', style='filled', fillcolor='lightgreen')
        c.node('order_service', '订单服务', shape='component', style='filled', fillcolor='lightgreen')
        
    # 数据层集群
    with dot.subgraph(name='cluster_data') as c:
        c.attr(label='数据存储层', style='filled', color='lightgreen', fontsize='16')
        c.node('main_db', '主数据库\n(PostgreSQL)', shape='cylinder', style='filled', fillcolor='lightyellow')
        c.node('cache', '缓存\n(Redis)', shape='cylinder', style='filled', fillcolor='lightcoral')
        c.node('search_engine', '搜索引擎\n(Elasticsearch)', shape='cylinder', style='filled', fillcolor='lightskyblue')
        
    # 连接关系
    dot.edge('web_app', 'api_gateway', label='HTTPS')
    dot.edge('mobile_app', 'api_gateway', label='REST API')
    dot.edge('api_gateway', 'auth_service', label='验证请求')
    dot.edge('api_gateway', 'user_service', label='用户数据')
    dot.edge('api_gateway', 'product_service', label='产品数据')
    dot.edge('api_gateway', 'order_service', label='订单处理')
    
    dot.edge('user_service', 'main_db', label='CRUD')
    dot.edge('product_service', 'main_db', label='查询')
    dot.edge('order_service', 'main_db', label='事务')
    dot.edge('user_service', 'cache', label='会话缓存')
    dot.edge('product_service', 'search_engine', label='全文搜索')
    
    return dot

# 创建并赋值给全局变量
system_arch = create_system_architecture()
```

### NetworkX 网络关系图（通过Matplotlib显示）

#### 完整的数据流水线网络图
```python
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

def create_data_pipeline_diagram():
    # 创建有向图
    G = nx.DiGraph()
    
    # 添加节点（数据流水线各阶段）
    nodes = {
        '数据源': {'type': 'source', 'color': 'lightgreen'},
        '数据采集': {'type': 'process', 'color': 'lightblue'},
        '数据清洗': {'type': 'process', 'color': 'lightblue'},
        '数据转换': {'type': 'process', 'color': 'lightblue'},
        '数据存储': {'type': 'storage', 'color': 'lightyellow'},
        '数据分析': {'type': 'analysis', 'color': 'lightcoral'},
        '数据可视化': {'type': 'visualization', 'color': 'lightskyblue'},
        '业务决策': {'type': 'decision', 'color': 'lightpink'}
    }
    
    for node, attrs in nodes.items():
        G.add_node(node, **attrs)
    
    # 添加边（数据流向）
    edges = [
        ('数据源', '数据采集', '原始数据'),
        ('数据采集', '数据清洗', '预处理'),
        ('数据清洗', '数据转换', '格式化'),
        ('数据转换', '数据存储', '持久化'),
        ('数据存储', '数据分析', '查询'),
        ('数据分析', '数据可视化', '结果'),
        ('数据可视化', '业务决策', '洞察')
    ]
    
    for src, dst, label in edges:
        G.add_edge(src, dst, label=label)
    
    # 布局算法
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # 绘图
    plt.figure(figsize=(16, 10))
    
    # 按类型着色节点
    node_colors = [nodes[node]['color'] for node in G.nodes()]
    node_sizes = [3000 if nodes[node]['type'] in ['source', 'decision'] else 2000 for node in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, 
                          node_color=node_colors,
                          node_size=node_sizes,
                          edgecolors='black',
                          linewidths=2,
                          alpha=0.9)
    
    # 绘制边
    nx.draw_networkx_edges(G, pos, 
                          edge_color='gray',
                          arrows=True,
                          arrowsize=20,
                          width=2,
                          alpha=0.7,
                          connectionstyle="arc3,rad=0.1")
    
    # 绘制节点标签
    nx.draw_networkx_labels(G, pos, 
                           font_size=12,
                           font_weight='bold',
                           font_family='WenQuanYi Micro Hei')
    
    # 绘制边标签
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, 
                                edge_labels=edge_labels,
                                font_size=10,
                                label_pos=0.5,
                                font_family='WenQuanYi Micro Hei')
    
    # 设置标题和网格
    plt.title('数据流水线架构图', fontsize=20, pad=30, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    # 🎯 关键：触发Matplotlib自动捕获
    plt.show()

# 调用函数生成图表
create_data_pipeline_diagram()
```

---

## ⚙️ 样式配置与字体设置（重要）

### 中文字体自动配置（系统已处理）
```python
import matplotlib.pyplot as plt

# 系统已自动配置中文字体，无需手动设置
# 如果遇到字体问题，可以使用以下配置：

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 可选：设置全局样式
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (12, 8),
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'grid.alpha': 0.3
})

print("字体配置完成，可以开始绘图")
```

---

## 📈 进阶功能：交互式图表与动画

### 简单动画示例
```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

fig, ax = plt.subplots(figsize=(10, 6))
x = np.linspace(0, 2*np.pi, 100)
line, = ax.plot(x, np.sin(x))

def animate(i):
    line.set_ydata(np.sin(x + i/10.0))
    return line,

ani = animation.FuncAnimation(fig, animate, interval=50, blit=True)
plt.title('正弦波动画演示')
plt.xlabel('X轴')
plt.ylabel('Y轴')
plt.grid(True)
plt.show()
```

---

## ⚠️ 重要注意事项

### ✅ 必须包含：
1. `import matplotlib.pyplot as plt`
2. 有意义的图表标题`plt.title()`
3. `plt.show()`（Matplotlib和NetworkX必须调用）

### ❌ 禁止操作：
1. 不要使用`base64.b64encode()`手动编码图片
2. 不要创建`io.BytesIO()`对象
3. 不要手动构建JSON输出（系统自动处理）
4. **Graphviz图表必须赋值给全局变量**

### 🔧 最佳实践：
1. **文件读取优先**：先从`/data`目录读取用户上传的文件
2. **提供备用方案**：如果没有文件，生成示例图表
3. **清晰的标签**：为图表添加清晰的标题和坐标轴标签
4. **合理的尺寸**：`figsize`建议(12, 8)或(10, 6)
5. **布局优化**：使用`plt.tight_layout()`防止标签重叠

---

## 🎯 现在完全匹配后端！

### 统一的自动捕获机制：

| 图表类型 | 正确使用方法 | 示例代码 |
|---------|-------------|----------|
| **Matplotlib** | `plt.show()` | `plt.plot(); plt.show()` |
| **Graphviz** | 创建并赋值给全局变量 | `dot = Digraph(); ...` |
| **NetworkX** | `plt.show()` | `nx.draw(); plt.show()` |

### 终极工作流模板：
```python
# 1. 检查数据文件
import os, pandas as pd
files = os.listdir('/data') if os.path.exists('/data') else []

# 2. 读取数据（如果有文件）
if files and 'data.csv' in files:
    df = pd.read_csv('/data/data.csv')
    # 使用真实数据绘图
else:
    # 生成示例数据绘图
    pass

# 3. 生成图表（选择一种类型）
# Matplotlib: plt.plot(); plt.show()
# Graphviz: dot = Digraph(); (自动捕获)
# NetworkX: nx.draw(); plt.show()

# 4. 图表会被自动捕获并显示给用户
```

### 故障排除：
1. **图表未显示**：
   - 检查是否调用了`plt.show()`
   - 检查Graphviz对象是否赋值给全局变量
   - 查看系统错误输出

2. **中文乱码**：
   - 系统已内置字体修复
   - 可手动设置字体配置

3. **文件读取失败**：
   - 确保文件已通过上传功能上传
   - 检查文件路径是否正确：`/data/文件名`

**记住**：系统会自动捕获所有图表并转换为标准格式，您只需要专注于绘图逻辑和数据分析！
