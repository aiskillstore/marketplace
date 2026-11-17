# Matplotlib 适配器

## 用途
- Python/Jupyter、学术出版、高 DPI、精确样式控制。

## 映射

### 全局样式设置
```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# 色板
CATEGORICAL_10 = [
    '#4269d0', '#3ca951', '#ff725c', '#a463f2', '#efb118',
    '#6cc5b0', '#9696a0', '#f5a623', '#ca5bb8', '#ff8ab7'
]

SEQUENTIAL_BLUES = [
    '#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6',
    '#4292C6', '#2171B5', '#08519C', '#08306B'
]

# 全局 rcParams
mpl.rcParams.update({
    # 排版
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue', 'Helvetica', 'Arial',
                        'PingFang SC', 'Microsoft YaHei', 'sans-serif'],
    'font.size': 10,                    # h4 默认

    # 画布
    'figure.facecolor': '#FFFFFF',
    'axes.facecolor': '#FFFFFF',
    'axes.edgecolor': '#333333',        # axis color
    'axes.linewidth': 1.0,              # axis width
    'axes.grid': True,
    'grid.color': '#E0E0E0',
    'grid.linewidth': 0.5,
    'grid.linestyle': (0, (2, 2)),      # dash [2,2]

    # 刻度
    'xtick.labelsize': 10,              # h4
    'ytick.labelsize': 10,
    'xtick.color': '#666666',
    'ytick.color': '#666666',
    'xtick.major.width': 1.0,
    'ytick.major.width': 1.0,

    # 图例
    'legend.fontsize': 10,             # h5
    'legend.frameon': True,
    'legend.edgecolor': '#D0D0D0',
    'legend.framealpha': 0.9,

    # 线条
    'lines.linewidth': 2.0,
    'lines.solid_capstyle': 'round',
    'lines.solid_joinstyle': 'round',
    'lines.markersize': 4,             # point radius (diameter = 8, Matplotlib uses points)

    # 保存
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.18,

    # LaTeX（可选，学术场景）
    # 'text.usetex': True,
})
```

### 折线图
```python
fig, ax = plt.subplots(figsize=(12.8, 8))  # 800×500 @ 100dpi → 8×5 inch

# 但考虑边距：实际图表宽度 = 12.8 - margin_left - margin_right
# 保持宽高比 1.6:1 的有效绘图区域
fig, ax = plt.subplots(figsize=(10, 6.25))

# 间距
fig.subplots_adjust(
    top=0.86,      # 留标题与图例空间
    right=0.96,
    bottom=0.12,   # 留轴标签空间
    left=0.10
)

for i, series in enumerate(data):
    ax.plot(x, y,
            color=CATEGORICAL_10[i],
            linewidth=2.0,
            marker='o',
            markersize=4,
            markerfacecolor=CATEGORICAL_10[i],
            markeredgewidth=0)

# 标题：以完整画布居中，不以坐标轴绘图区居中
ax.set_title('')
fig.text(0.5, 0.965, 'Chart Title',
         ha='center', va='top',
         fontsize=16, fontweight=600, color='#1A1A1A')

# 轴标签
ax.set_xlabel('X Axis', fontsize=11, color='#333333', labelpad=6)
ax.set_ylabel('Y Axis', fontsize=11, color='#333333', labelpad=6)

# 网格
ax.grid(True, color='#E0E0E0', linewidth=0.5, linestyle=(0, (2, 2)))
ax.set_axisbelow(True)  # 网格在数据下层

# 图例
ax.legend(
    fontsize=10,
    loc='upper center',
    bbox_to_anchor=(0.5, 1.12),
    ncol=3,
    frameon=True,
    edgecolor='#D0D0D0',
    framealpha=0.9,
    borderaxespad=0.0,
    columnspacing=2.0
)

# 去除顶部和右侧边框（Tufte 原则）
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
```

### 静态导出后的视觉居中

`bbox_inches='tight'` 可能造成可见边界不对称。出版、论文、报告导出后补齐留白。

```python
from pathlib import Path
from PIL import Image


def recenter_visual_content(path: str | Path, threshold: int = 245) -> None:
    image = Image.open(path).convert('RGB')
    width, height = image.size
    pixels = image.load()

    xs, ys = [], []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if min(r, g, b) < threshold:
                xs.append(x)
                ys.append(y)

    if not xs:
        image.save(path)
        return

    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    crop = image.crop((left, top, right + 1, bottom + 1))

    margin_x = max(left, width - right - 1)
    margin_y = max(top, height - bottom - 1)
    canvas = Image.new(
        'RGB',
        (right - left + 1 + margin_x * 2, bottom - top + 1 + margin_y * 2),
        'white'
    )
    canvas.paste(crop, (margin_x, margin_y))
    canvas.save(path)


fig.savefig(output_path, dpi=220, bbox_inches='tight', pad_inches=0.18)
recenter_visual_content(output_path)
```

### 时间轴节点防变形

宽扁时间轴不用 `Circle(..., transform=ax.transAxes)`；改用 `scatter` 或等比坐标。

```python
ax.scatter([x], [0.5], s=220, color='#333333',
           transform=ax.transAxes, zorder=3)
```

### 柱状图
```python
bars = ax.bar(categories, values,
              color=CATEGORICAL_10[0],
              width=0.7,
              edgecolor='white',
              linewidth=0.5)

# 数据标签
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2., height + 4,
            f'{height:.1f}',
            ha='center', va='bottom',
            fontsize=9, color='#888888')  # h6
```

### 散点图
```python
ax.scatter(x, y,
           s=50,              # 面积 ≈ π * r² → (4px)² * π ≈ 50 pts²
           c=CATEGORICAL_10[0],
           alpha=0.8,
           edgecolors='white',
           linewidth=0.5)
```

## 默认

- 屏幕 100 DPI；保存 150 DPI，出版按需求提高。
- PNG 光栅；PDF/SVG 矢量。
- 检测中文字体或接受用户指定；色板从 `aesthetics/default.json` 导入。
