# Canvas 绘制参考

> ⚠️ **重要**：`canvas` 模块是 DQL 的补充功能。可视化需求应优先使用 Datadata 平台的可视化功能（`datadata-viz-config` skill）。
> **仅当用户明确要求用 canvas 绘图时才使用此模块**，不要主动建议。
>
> Canvas API 基于 [github.com/fogleman/gg](https://github.com/fogleman/gg) 实现。
>
> 完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

本文档详细列出 Canvas Context 支持的所有绘制方法。

## 创建 Canvas

> 注意：`canvas` 是内置模块，无需 `import`，直接使用。

```python
# 创建一个 800x600 的 canvas
ctx = canvas.Context(800, 600)
```

## 基本图形绘制

### 点

```python
ctx.set_rgb(255, 0, 0)          # 设置颜色为红色
ctx.draw_point(100, 100, 5)     # 在 (100, 100) 绘制半径为 5 的点
```

### 线

```python
ctx.draw_line(10, 10, 100, 100)  # 从 (10, 10) 到 (100, 100) 的直线
```

### 矩形

```python
ctx.set_rgb(0, 255, 0)                    # 绿色
ctx.draw_rectangle(50, 50, 200, 100)      # 左上角 (50, 50)，宽 200，高 100
ctx.fill()                                 # 填充

# 圆角矩形
ctx.draw_rounded_rectangle(50, 50, 200, 100, 10)  # 圆角半径 10
ctx.stroke()                               # 描边
```

### 圆形

```python
ctx.set_rgb(0, 0, 255)          # 蓝色
ctx.draw_circle(200, 200, 50)   # 中心 (200, 200)，半径 50
ctx.fill()
```

### 椭圆

```python
ctx.draw_ellipse(300, 200, 80, 50)  # 中心 (300, 200)，长轴 80，短轴 50
ctx.stroke()
```

### 弧线

```python
# 圆弧
ctx.draw_arc(400, 300, 50, 0, 3.14)  # 中心、半径、起始角、结束角

# 椭圆弧
ctx.draw_elliptical_arc(400, 300, 80, 50, 0, 1.57)
```

### 多边形

```python
# 正多边形：n 边形，中心、半径、旋转角
ctx.draw_regular_polygon(6, 300, 300, 50, 0)  # 正六边形
ctx.fill()
```

## 路径 (Path) 绘制

使用路径 API 绘制复杂图形：

```python
# 开始路径
ctx.move_to(10, 10)             # 移动笔尖到 (10, 10)

# 绘制直线路径
ctx.line_to(50, 10)
ctx.line_to(50, 50)
ctx.line_to(10, 50)

# 绘制二次贝塞尔曲线
ctx.quadratic_to(x1, y1, x2, y2)

# 绘制三次贝塞尔曲线
ctx.cubic_to(x1, y1, x2, y2, x3, y3)

# 闭合路径
ctx.close_path()

# 填充或描边
ctx.fill()          # 填充路径
ctx.stroke()        # 描边
```

### 路径管理

```python
ctx.clear_path()        # 清除当前路径
ctx.new_sub_path()      # 开始新子路径
```

## 像素操作

```python
ctx.set_pixel(100, 100)  # 在 (100, 100) 设置一个像素
```

## 文本绘制

### 基础文本

```python
ctx.set_rgb(0, 0, 0)           # 黑色
ctx.draw_string("Hello", 100, 100)
```

### 文本对齐

```python
# draw_string_anchored: 基于锚点绘制文本
# ax, ay: 对齐点 (0.0 = 左/上, 0.5 = 中, 1.0 = 右/下)
ctx.draw_string_anchored("Centered", 200, 200, 0.5, 0.5)
```

### 多行文本

```python
# 绘制换行文本，自动折行
# ax, ay: 对齐方式
# width: 文本宽度限制
# lineSpacing: 行间距
# align: 0 = 左对齐，1 = 居中，2 = 右对齐
ctx.draw_string_wrapped("Long text here", 50, 50, 0, 0, 300, 20, 0)
```

### 文本测量

```python
# 测量单行文本宽度和高度
width, height = ctx.measure_string("Hello")

# 测量多行文本
width, height = ctx.measure_multiline_string("Line1\nLine2", 20)

# 自动折行
lines = ctx.word_wrap("Long text", 300)  # 返回折行后的列表
```

## 颜色设置

### RGB 颜色

```python
# 0-1 范围 (浮点)
ctx.set_rgb(1.0, 0.0, 0.0)     # 红色
ctx.set_rgb(0.0, 1.0, 0.0)     # 绿色
ctx.set_rgb(0.0, 0.0, 1.0)     # 蓝色

# 0-255 范围 (整数)
ctx.set_rgb255(255, 0, 0)      # 红色
ctx.set_rgb255(0, 255, 0)      # 绿色
```

### RGBA 颜色 (含透明度)

```python
# 0-1 范围
ctx.set_rgba(1.0, 0.0, 0.0, 0.5)   # 半透明红色

# 0-255 范围
ctx.set_rgba255(255, 0, 0, 128)    # 半透明红色
```

### 16 进制颜色

```python
ctx.set_hex_color("#FF0000")    # 红色
ctx.set_hex_color("#00FF00")    # 绿色
ctx.set_hex_color("#0000FF")    # 蓝色
```

## 笔画样式

```python
# 线条宽度
ctx.set_line_width(2.0)

# 线条端点样式: 0 = Butt, 1 = Round, 2 = Square
ctx.set_line_cap(1)

# 线条连接样式: 0 = Miter, 1 = Round
ctx.set_line_join(1)

# 虚线: 依次指定线段长度和间隙
ctx.set_dash(5, 3)              # 5 像素线，3 像素间隙
ctx.set_dash(5, 3, 2, 3)        # 复杂虚线

# 虚线起始偏移
ctx.set_dash_offset(2.0)

# 填充规则: 0 = EvenOdd, 1 = Winding
ctx.set_fill_rule(0)
```

## 渐变

### 线性渐变

```python
ctx.new_linear_gradient(x0, y0, x1, y1)
# 之后的填充使用此渐变
ctx.fill()
```

### 径向渐变

```python
ctx.new_radial_gradient(x0, y0, r0, x1, y1, r1)
ctx.fill()
```

### 角度渐变

```python
ctx.new_conic_gradient(cx, cy, deg)
ctx.fill()
```

## 变换 (Transformation)

### 基本变换

```python
# 平移
ctx.translate(50, 100)

# 缩放
ctx.scale(2.0, 1.5)

# 旋转 (角度为弧度)
ctx.rotate(3.14159 / 4)

# 剪切
ctx.shear(0.5, 0.0)
```

### 相对于点的变换

```python
# 关于点 (x, y) 缩放
ctx.scale_about(2.0, 2.0, 100, 100)

# 关于点 (x, y) 旋转
ctx.rotate_about(3.14159 / 4, 100, 100)

# 关于点 (x, y) 剪切
ctx.shear_about(0.5, 0.0, 100, 100)
```

### 变换管理

```python
# 重置为恒等变换
ctx.identity()

# 转换点坐标
x_new, y_new = ctx.transform_point(100, 100)

# 反转 Y 轴（用于 UI 坐标系）
ctx.invert_y()
```

## 栈操作

用于保存和恢复绘制状态：

```python
# 保存当前状态
ctx.push()

# 修改状态（颜色、变换等）
ctx.set_rgb(255, 0, 0)
ctx.translate(100, 100)
ctx.draw_circle(0, 0, 50)
ctx.fill()

# 恢复之前的状态
ctx.pop()

# 现在颜色和变换都已恢复
```

## 裁剪 (Clipping)

```python
# 定义裁剪路径
ctx.move_to(10, 10)
ctx.line_to(100, 10)
ctx.line_to(100, 100)
ctx.close_path()

# 应用裁剪
ctx.clip()

# 后续绘制只显示在裁剪区域内
ctx.draw_circle(50, 50, 40)
ctx.fill()

# 保留路径的裁剪
ctx.clip_preserve()

# 重置裁剪
ctx.reset_clip()

# 反转蒙版
ctx.invert_mask()
```

## 清除和填充

```python
# 清晰整个 canvas
ctx.clear()

# 填充当前路径
ctx.fill()

# 描边当前路径
ctx.stroke()

# 保留路径进行后续操作
ctx.fill_preserve()
ctx.stroke_preserve()
```

## 输出

```python
# 获取 base64 编码的 PNG 数据 URI
data_uri = ctx.get_data_uri()

# 用于 HTML img 标签
# <img src="data:image/png;base64,iVBORw0KG..." />
```

## 辅助函数

```python
canvas.radians(degrees)  # 角度转弧度
canvas.degrees(radians)  # 弧度转角度
```

## 完整示例

### 基础图形

```python
# 创建 canvas
ctx = canvas.Context(400, 300)

# 背景
ctx.set_rgb(1, 1, 1)  # 白色
ctx.draw_rectangle(0, 0, 400, 300)
ctx.fill()

# 绘制圆形
ctx.set_rgb(0, 0, 1)  # 蓝色
ctx.draw_circle(200, 150, 80)
ctx.fill()

# 绘制标题
ctx.set_rgb(0, 0, 0)  # 黑色
ctx.draw_string_anchored("My Chart", 200, 50, 0.5, 0.5)

# 获取结果
data_uri = ctx.get_data_uri()
```

### 旋转的椭圆

展示 `push`/`pop` 状态保存恢复和 `rotate_about` 的用法：

```python
S = 1024
ctx = canvas.Context(S, S)

ctx.set_rgba(10, 250, 10, 0.1)

for i in range(0, 360, 15):
    ctx.push()                                              # 保存当前状态
    ctx.rotate_about(canvas.radians(i), S / 2, S / 2)      # 绕画布中心旋转
    ctx.draw_ellipse(S / 2, S / 2, S * 7 / 16, S / 8)     # 绘制椭圆
    ctx.fill()                                              # 填充
    ctx.pop()                                               # 恢复之前的状态

return ctx.get_data_uri()
```

## 呈现方式

Canvas 绘制的图像通过 `get_data_uri()` 返回 Data URI，需要在 Datadata 平台的表格中呈现。脚本返回包含 `data_uri` 的对象即可在表格单元格中显示图像。
