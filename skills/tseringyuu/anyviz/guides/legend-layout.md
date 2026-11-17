# 图例布局

## 边界

图例必须完全位于 viewBox 内，右侧保留 10px：

`itemWidth = marker 22px + gap 8px + 字数 × 字号 × 0.6 + itemGap 20px`

`legendWidth = Σ itemWidth`；居中时 `x = (viewBoxWidth - legendWidth) / 2`。验证 `x + legendWidth ≤ viewBoxWidth - 10`。

## 安全带

- 顶部图例独占 legend band，不悬浮于绘图区。
- 标题底到图例顶 ≥16px。
- 图例底到绘图区 ≥20px；论文/出版 ≥24px。
- 图例与轴/数据标签 ≥16px；图例与脚注 ≥15px。
- 用增大上边距或缩小绘图区预留空间；不用负 margin。

常见冲突：雷达底部维度标签、柱状负值标签、横条类别标签、折线终点标签。优先换位、换行、分侧或减少直接标注。

## 多项布局

`N ≥ 4` 时用 2×`ceil(N/2)` 网格，行距 22px；先换行，不压缩进绘图区。整体默认按完整画布水平居中。

## Academic

灰度系列必须同时编码线型；图例标记与数据线完全一致：

| 系列 | 颜色 | dash |
|---|---|---|
| 1 | `#333333` | 实线 |
| 2 | `#666666` | `5,3` |
| 3 | `#999999` | `3,2` |
| 4 | `#BBBBBB` | `1,2` |

5+ 系列循环线型并降低 opacity；更推荐小倍数。

## 居中计算

```javascript
const legendWidth = items.reduce((sum, item, i) => {
  return sum + item.markerWidth + item.textWidth + (i < items.length - 1 ? itemGap : 0);
}, 0);

const legendX = (viewBoxWidth - legendWidth) / 2;
```
