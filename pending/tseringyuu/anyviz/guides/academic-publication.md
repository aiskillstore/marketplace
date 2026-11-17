# 学术出版图表

目标：稳定、克制、可引用、可打印。

## 标题、题注、来源

- 图内标题按完整画布居中；版面紧张时优先保留文档层题注。
- 文档层统一生成 `图 N-M 标题` 与交叉引用。
- 正文已有资料来源时，图内不重复；独立传播版才内嵌来源。
- 同文档题注与来源字号、颜色、对齐一致；来源默认 H6、muted、居中。

## 图例

- 顶部图例独占安全带；到绘图区 ≥24px。
- 4+ 项用两行。
- Academic 多系列同时使用灰度、线型、点型，不只靠颜色。

## 导出

- 检查标题、图例、轴、外置标签构成的可见边界。
- 使用 `bbox_inches="tight"` 后补齐不对称留白。
- 插入 Word/PDF 后按最终物理尺寸复查视觉中心、字号、灰度与清晰度。
- 优先保留 PNG 高 DPI 与 PDF/SVG 矢量版。

## 时间轴与节点

- Matplotlib 不用 `Circle(..., transform=ax.transAxes)`；宽扁坐标会拉成椭圆。
- 用 `ax.scatter(..., transform=ax.transAxes)` 或等比坐标。
- SVG/Canvas 的圆形 symbol 保持相同 x/y 半径；导出后查圆度。

## 交付检查

- 图内标题按画布中轴居中。
- 图例与标题、绘图区、数据标签间距合格。
- 题注与来源由文档层统一；图内无重复来源。
- 节点未拉伸；CI、事件线、标签无重叠或裁切。
- Word/PDF 中视觉居中；跨图字体、题注、来源、线型一致。

## 参考实现

画布标题：

```python
ax.set_title("")
fig.text(0.5, 0.965, title, ha="center", va="top",
         fontsize=15, fontweight="bold", color="#000000")
```

```javascript
title: {
  text,
  left: "center",
  top: 12,
  textAlign: "center"
}
```

```r
theme(
  plot.title = element_text(hjust = 0.5),
  plot.title.position = "plot"
)
```

来源策略：

```json
{
  "publication": {
    "source_note": {
      "inside_chart": false,
      "outside_chart": true,
      "alignment": "center",
      "font_role": "h6",
      "deduplicate": true
    }
  }
}
```

顶部图例：

```python
fig.subplots_adjust(top=0.80)
ax.legend(
    frameon=False,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.12),
    ncol=3,
    borderaxespad=0.0,
    columnspacing=2.2
)
```

导出与节点：

```python
fig.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.18)
# 保存后读取像素边界，补齐左右/上下留白，使可见内容中心与画布中心一致。
```

```python
ax.scatter([x], [0.5], s=220, color="#333333",
           transform=ax.transAxes, zorder=3)
```
