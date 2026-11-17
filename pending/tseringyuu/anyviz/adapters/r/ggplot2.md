# ggplot2 适配器

## 用途
- R 统计可视化、论文、knitr/rmarkdown。

## 映射

### 全局主题
```r
library(ggplot2)

# 色板
categorical_10 <- c(
  '#4269d0', '#3ca951', '#ff725c', '#a463f2', '#efb118',
  '#6cc5b0', '#9696a0', '#f5a623', '#ca5bb8', '#ff8ab7'
)

# anyviz 默认主题
theme_anyviz <- function() {
  theme_minimal(base_family = 'Helvetica Neue') +
  theme(
    # 画布
    plot.background = element_rect(fill = '#FFFFFF', color = NA),
    panel.background = element_rect(fill = '#FFFFFF', color = NA),
    panel.grid.major = element_line(color = '#E0E0E0', linewidth = 0.3),
    panel.grid.minor = element_blank(),

    # 排版
    plot.title = element_text(size = 16, face = 'bold', color = '#1A1A1A',
                              hjust = 0.5, margin = margin(b = 16)),
    plot.title.position = 'plot',
    plot.subtitle = element_text(size = 13, color = '#555555',
                                 margin = margin(b = 8)),
    axis.title = element_text(size = 11, color = '#333333'),
    axis.title.x = element_text(margin = margin(t = 6)),
    axis.title.y = element_text(margin = margin(r = 6)),
    axis.text = element_text(size = 10, color = '#666666'),

    # 图例
    legend.position = 'top',
    legend.text = element_text(size = 10, color = '#555555'),
    legend.title = element_text(size = 10, color = '#555555'),
    legend.key = element_rect(fill = 'white', color = NA),
    legend.box = 'horizontal',
    legend.margin = margin(t = 0, r = 0, b = 20, l = 0),

    # 边距
    plot.margin = margin(t = 48, r = 36, b = 56, l = 56),

    # 轴线
    axis.line = element_line(color = '#333333', linewidth = 0.5),
    axis.ticks = element_line(color = '#333333', linewidth = 0.5),

    # 分面
    strip.background = element_rect(fill = '#F5F5F5', color = '#D0D0D0'),
    strip.text = element_text(size = 10, color = '#555555')
  )
}

# 设置默认主题
theme_set(theme_anyviz())

# 设置默认色板
options(ggplot2.discrete.colour = categorical_10)
options(ggplot2.discrete.fill = categorical_10)
```

### 折线图
```r
ggplot(data, aes(x = date, y = value, color = category)) +
  geom_line(linewidth = 1.0) +          # ggplot2 linewidth = stroke width
  geom_point(size = 1.5) +              # point radius ≈ 3px
  scale_color_manual(values = categorical_10) +
  labs(
    title = 'Chart Title',
    x = 'X Axis',
    y = 'Y Axis'
  ) +
  theme_anyviz()
```

### 柱状图
```r
ggplot(data, aes(x = reorder(category, -value), y = value)) +
  geom_col(fill = categorical_10[1], width = 0.7) +
  geom_text(aes(label = sprintf('%.1f', value)),
            vjust = -0.5,                # outside position
            size = 9 / .pt,              # h6 (9px) → ggplot2 mm
            color = '#888888') +
  labs(title = 'Chart Title', x = '', y = 'Value') +
  theme_anyviz()
```

### 散点图
```r
ggplot(data, aes(x = x_var, y = y_var, color = category)) +
  geom_point(size = 2.0, alpha = 0.8, stroke = 0.2) +
  scale_color_manual(values = categorical_10) +
  labs(title = 'Chart Title', x = 'X Variable', y = 'Y Variable')
```

### 箱线图
```r
ggplot(data, aes(x = category, y = value, fill = category)) +
  geom_boxplot(width = 0.6, outlier.size = 1.5, outlier.alpha = 0.6) +
  scale_fill_manual(values = categorical_10) +
  labs(title = 'Chart Title', x = '', y = 'Value') +
  theme(legend.position = 'none')  # 类别已在 X 轴上
```

## 默认

- 基于 `theme_minimal()`；`scale_color_manual`/`scale_fill_manual` 用 `categorical_10`。
- `ggsave(dpi=150, bg='white')`；默认 8×5in，宽高比 1.6。
