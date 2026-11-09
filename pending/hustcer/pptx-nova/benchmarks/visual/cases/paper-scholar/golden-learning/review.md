# Paper Scholar golden review

2026-10-26：1.0.0，candidate；xdoc 0.20.0 (91827673)。

同日先晋级 production，再晋级 default。golden benchmark 重跑通过，vision 高／中／低均为 0，并建立空的已接受 vision 基线。八页 canonical PNG 与 contact sheet 均和此前已审查的 benchmark 逐字节相同。本轮 benchmark 证据：`.tmp/deckkit-production-20261026-fBFdCq/paper-scholar/golden-learning/`。

最终完整主样为 `.tmp/deckkit-paper-scholar/create/golden-03/candidate.pptx`，
SHA-256 `f536d7f17842203f3ae66e1a0ec634b4548425edb59dc1bb304c5972e25189a8`。
该文件与 `benchmark/03/paper-scholar/golden-learning/deck.pptx` 及分发的
`assets/examples/deckkits/paper-scholar/deck.pptx` 字节相同。

## 机器验证

标准 Create：validate、check-lock、dry-run、apply、inspect/model、design-readback、vision、
canonical 均通过。完成实际逐页审查后以视觉哈希绑定 finalize，状态为 delivered。
benchmark/03 三次构建通过：错误／阻塞 fit 为 0，dry-run 高／中为 0，vision 高／中／低为 0。
从 benchmark 实际 PPTX 新生成 canonical 并再次查看八页；未以 contact sheet 代替逐页。
required-live candidate readiness 通过。字体／颜色／placeholder 结构检查及 Office 365 compat 通过。

## 实际逐页与局部审查

| 页  | 检查重点                                                       | 结果                           |
| --- | -------------------------------------------------------------- | ------------------------------ |
| 1   | 17 条等高线、cubic S 路径、五刻线、badge、横线与元信息         | pass；保持封面细节与留白       |
| 2   | 四个圆内数字居中、细箭头、三来源区、失访注记                   | pass；无压线或越界             |
| 3   | 110pt 主百分比、比较组与派生差异、6.5 个实心圆的精确扇区       | pass；不使用四舍五入的圆点数量 |
| 4   | 原生柱图 59%／43%／52%、底部分类与单位、双段解释               | pass；全部标签实际可见         |
| 5   | 两条半衰期曲线、图内标签、公式／图例同源、复核刻度、轴箭头     | pass；无曲线穿字               |
| 6   | 原生五列表、深绿首列与图标白圆、隔行 tint、重点值、末行及附注  | pass；首列图标留白进入容量     |
| 7   | 粉色标题带、叠压的 shape 图片外壳、三段案例和深绿前后对比      | pass；照片按授权使用占位 shape |
| 8   | 行动圆号与图标、功能性浅绿圆角条、依据／执行关系和底部复核字段 | pass；附注与来源边界清楚       |

局部裁图保存在 run 的 `final-crops/`；逐页 PNG、候选、manifest 与 hash 记录见
`visual-review-ledger.json`。同内容变体、纯中文、混排水务、两套最大密度和边界输入共 52 页均已实际查看。
压力／边界探针只验结构、容量和原值，不作为研究叙事交付。

## 原生与限制

macOS PowerPoint 16.114.1 打开最终主样、另存、关闭、重开，无 Repair 或丢页；保存后的
222 个对象、一个图表和一个表格回读通过。最终水务样例同样保存重开，通过 216 个对象回读。
主样图表、表格和文字另做实际编辑并保存回读，详见
`native/native-edit-verification.json`；该编辑探针来自标签调整前的主样，最终候选另有保存重开证据。

逐点标签继承差异已改用完整 series 作用域关闭：短柱触发整组柱外标签。科学计数的
canonical 显示可能简化，原生 PowerPoint 保留完整格式与单位；数据及图下注明单位不变。
CLI clean-open 因 UI scripting 权限 skipped，未记为 pass；实际原生验证使用 CUA。
Windows、旧版 Office、字体嵌入与像素一致未验证。图标为 SVG 图片；独立派生形状／注记手改后须重建。
