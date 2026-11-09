# Morph 编排：先确定对象关系，再安排运动

读取条件：用户要求 Morph、跨页连续运动、聚焦某个对象、放大 KPI 或主体退场。
先按 [动画与转场](animations.md) 发现运行时契约；本文件复用现有操作，不增加新的动画效果。

## 三种对象角色

| 角色         | 名称示例                         | 相邻页约定                                             |
| ------------ | -------------------------------- | ------------------------------------------------------ |
| 场景对象     | `!!scene-surface`                | 两页同名，位置、大小和样式通常保持一致，提供稳定背景   |
| 运动主体     | `!!actor-product`、`!!actor-kpi` | 两页同名，明确改变位置、大小或旋转，让观众看懂变化关系 |
| 普通逐页内容 | `caption`、`page-number`         | 不自动加 `!!`；按该页需要出现、消失或更新              |

这是命名约定；`scene` 和 `actor` 不是引擎关键字。配对依赖完整名称（含大小写），同一页不得有
重复的同名主体。不要给全部 shape 批量加前缀；普通名称的 PowerPoint 隐式匹配不在本流程保证范围内。

## 复制后再改变目标页

1. inspect 源页，确定场景与主体的名称、shape id、几何和实际画幅。
2. 用 `duplicate-slide` 复制源页（也可使用同 deck 的 `slide-copy` CLI）。复制后再次 inspect，
   根据新增的 slide part 确认目标页索引，再解析目标页的 shape id；不要沿用另一页的 id。
3. 对目标页主体执行 `set-shape`，只改变本次运动意图需要的属性。
4. 在**目标页**设置 `set-slide-transition`：`kind: "morph"`、`morphMode: "by-object"`。
   patch 的 `slide` 为 0-based；`morph-check --from-slide/--to-slide` 为 1-based。
5. 每步先 dry-run，再 apply；保存 inspect 与相邻页 morph-check 的回读结果。

优先每次切页只突出一个主要变化。移动、放大通常可从 700–900ms 试起，退场可从 500–700ms 试起，
再按距离、信息密度和演讲节奏调整。这些是设计起点，不是格式约束；没有固定 5cm 位移或对象数量门槛。
静态场景出现 `morph_pair_no_visible_change` 提示是预期的，不要为消除提示让背景也移动。

## 三个可执行的最小示例

示例是两页的功能样本，不替代完整 deck 的 DeckKit/内容设计流程。需要 Node.js 20+ 与当前 `xdoc`，
不需要安装依赖。脚本会先读 schema，输出创建、复制、修改的 patch 与 dry-run/apply/inspect 报告，
最后验证配对、几何变化、目标页转场及非阻断提示。目标 run 目录必须尚不存在。

```bash
node <skill-root>/scripts/cli/animation/examples.mjs \
  --example focus --run-dir .pptx-nova/morph-focus-<unique>
node <skill-root>/scripts/cli/animation/examples.mjs \
  --example kpi --run-dir .pptx-nova/morph-kpi-<unique>
node <skill-root>/scripts/cli/animation/examples.mjs \
  --example exit --run-dir .pptx-nova/morph-exit-<unique>
```

| 示例    | 意图与变化                                                                        | 预期显式配对                         |
| ------- | --------------------------------------------------------------------------------- | ------------------------------------ |
| `focus` | 主体由左侧移向画布中心，稍微放大；静态背景维持空间参照                            | `!!scene-surface`、`!!actor-product` |
| `kpi`   | 同一数值卡片从概览尺寸放大为重点；文字内容保持 `42%`，同步调整字号                | `!!scene-surface`、`!!actor-kpi`     |
| `exit`  | 保留目标页主体及同名配对，把其完整可见边界移到画布右侧；使用 18° 旋转验证边界计算 | `!!scene-surface`、`!!actor-product` |

每个 run 的 `candidate.pptx` 是最终样本，`evidence-summary.json` 保存预期名字、源/目标索引、
检查结果和实际 finding。`morph-check.json` 中主体应有几何变化，scene 应保持不变；其他 warning
必须逐项理解，不通过“忽略全部 warning”或移动背景来获得表面通过。KPI 示例不承诺数字滚动插值。

## 退场与 ghost 边界

只有确实需要连续退场/进场时，才在画外保留配对主体。直接删除目标页主体会失去显式配对，
不能再保证是连续运动退场。该画外副本是运动端点，不是在原位置叠加一个透明对象。

画外坐标必须来自实际 slide size。设主体未旋转框为 `(x, y, w, h)`、绕中心旋转 `θ`：

```text
halfWidth  = (abs(w*cos θ) + abs(h*sin θ)) / 2
halfHeight = (abs(w*sin θ) + abs(h*cos θ)) / 2
centerX    = x + w/2
centerY    = y + h/2
```

向右退场要求 `centerX - halfWidth >= slideWidth + margin`。margin 还需覆盖描边、阴影、光晕等
可见外溢；示例没有这些外溢效果，使用画幅宽度的 2% 作为余量。其他方向使用对应边界，不写死
`x=36cm`。嵌套旋转 group、图片裁剪或未知效果需先取得可信的 slide-space 可见边界，不能直接套用
简单矩形公式。静态越界检查可能报告有意设计的 ghost，应保存依据，不要把其他越界一并豁免。

## 验证边界

示例脚本证明 dry-run/apply 成功、精确名称配对、几何意图和转场元数据；它不证明视觉播放。
按 [Morph 专用流程](animations.md#morph-专用流程) 在可用时运行 clean-open 与 PowerPoint 播放探针，
需要保存往返证据时用播放探针的 `--resave-output`；这要求 PowerPoint 具备编辑权限且可调用 `unzip`。
View Only 环境可能仍可打开、播放及导出端点截图，但不具备回存证据；空文件或无效 ZIP 不算回存成功。
PNG/contact sheet 只检查端点布局，fade fallback
只服务于不支持 Morph 的 consumer，两者都不能作为 Morph 播放证明。

PowerPoint 不可用时明确记录未验证；若用户要求实际播放证据，该项验收仍待完成。不要因为静态
检查通过而把某个平台上的结构验证提升为跨平台视觉一致性结论。
