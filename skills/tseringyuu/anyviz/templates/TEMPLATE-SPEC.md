# 模板规范

`templates/` 文件统一回答：何时用、数据结构、特有参数、执行规则、变体。

## 结构

```markdown
# 中文名（English Name）

## 用途
- 回答的问题、规模/类别建议

## 数据
​```json
{ ...最小可用输入... }
​```

## 参数
​```json
{ ...仅列图表特有参数... }
​```

## 规则
- **名称**：含数值的可执行规则

## 变体
- **名称（English）**：用途与主图差异
```

章节顺序固定。

## 硬约束

1. 参数显式写死，并与 `aesthetics/default.json` 一致；不发明色值。
2. 色板按数据：分类 `categorical`、顺序 `sequential`、发散 `diverging`、焦点 `highlight`。细则见 `aesthetics/color.md`。
3. 数据示例必须最小可用。同类字段统一：系列 `series/name/values`；关系 `nodes/links/source/target/value`；地理 `regions/id/name/value`。
4. 规则必须可执行；写 hex、px、opacity、阈值，不写“颜色协调”等空话。
5. 关键区分不得只靠颜色；写明形状、线型、标签或纹理兜底。见 `guides/accessibility.md`。
6. 变体只做主图参数调整/扩展；独立图另建模板，并登记到 `guides/chart-selection.md`。

## 基线速查

| 元素 | 值 |
|---|---|
| 颜色 | 主 `#4269d0`；增长 `#3ca951`；减少/对比 `#ff725c`；中性 `#9696a0`；高亮 `#a463f2`；描边 `#FFFFFF` |
| 折线 | 2.2px；monotone；圆角端点 |
| 散点 | r 4.5px；白描边 2px；opacity 0.75 |
| 折线点 | r 3.5px；opacity 1 |
| 高亮点 | r 6px；描边 2.5px `#333333` |
| 异常值 | r 4.5px；×；opacity 0.6 |
| 柱 | 圆角 5px；宽度比 0.65 |
| 面积 | 单层 opacity 0.12；堆叠 0.65 |
| 网格 | 0.5px `#E8E8E8` `[2,2]`；只显 Y 轴 |
| 轴 | 0.8px `#CCCCCC` |
| 参考线 | 1px `#EE7B6F` `[4,4]`；opacity 0.7 |
| 趋势线 | 1.5px `#EE7B6F` `[6,3]`；opacity 0.6 |

字号：H1 16/600；H2 13/400；H3 11/400；H4/H5 10/400；H6 9/400。
