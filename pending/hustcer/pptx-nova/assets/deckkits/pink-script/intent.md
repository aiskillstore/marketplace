# Pink Script：夜间编辑叙事

1.0.0 是创建型 DeckKit，当前为 production，可参与自动交付选择；readiness 以 [catalog](../catalog.json) 为准。默认 16:9，以暖黑光照、单一玫红、奶油粉正体衬线、开放细线与巨大数字建立身份。用户已明确要求取消全部外框；收尾只保留透明二维码，不生成白色底板、CONTACT 或网址标题。数值事实源为同目录 `design.json`。

| 页型             | 注册构图             | 职责与边界                                         |
| ---------------- | -------------------- | -------------------------------------------------- |
| pinkCoverSlide   | hanging / offset     | 双行错位封面，2–4 项元数据；短标题优先             |
| pinkIndexSlide   | rail / band          | 大题侧栏或横向刊头，3–5 项开放索引                 |
| pinkStatsSlide   | rail / band          | 3–5 项原始数值、单位、标签和解释；侧栏或下方指标带 |
| pinkSectionSlide | left / right         | 巨大章节代码与对侧说明；水平侧注改善可读性         |
| pinkTrendSlide   | rail / band          | 两条完整原生折线、3–12 个类别、焦点标记与独立旁注  |
| pinkProcessSlide | columns / rows       | 3–5 步，列式箭头或开放行式，独立时间说明           |
| pinkMatrixSlide  | full / inset         | 3–4 列、3–5 行原生表格，最多 6 个唯一状态单元格    |
| pinkQuoteSlide   | rail / broad         | 大引号、正体引文、作者与来源身份                   |
| pinkClosingSlide | invitation / sidecar | 2–3 项行动；可选透明 QR 图片槽，无默认联系人文案   |

通过标准 `slots → validate-content → create/build → create/run → 逐页审查 → finalize` 使用。`auto` 根据真实输入容量与近期构图确定性选择，显式 `layoutId` 也必须适配。无可用构图时应重组或拆页；不会删字段、改数值或无限缩字。完整 deck 使用封面与收尾；片段可指定 `meta.designScope: "excerpt"`。大小写与明确换行原样保留。

英文展示使用 DM Serif Display 常规体；中文展示使用宋体粗体替代参考建议的 Noto Serif SC 900。英文正文 Inter 常规体替代 Light，中文正文宋体常规体，元数据为 JetBrains Mono / Noto Sans SC。字体不嵌入，须在生成/播放环境安装并验证；常规/粗体和实际混排需分别看图。仅 Latin 元数据加字距，CJK 不强加大写或等宽。

所有标题、观点、业务实体、来源、日期、单位、阈值和政策来自 content。主示例为明确标注的合成参考重建；社区维修示例用于不同领域验证。图表两系列、类别与原始数值保持原生；独立图例和旁注不自动跟随 PowerPoint 手工改数，需从 content 重建。极小数在共同线性轴上可能小于一个像素，数据回读不等于像素可见性。

矩阵逐格写入原生表格，状态通过原生单元格填充/文字表达，避免独立胶囊与表格编辑不同步。`solid`、`outline`、`dim` 只是视觉状态，业务含义来自内容；不固定肯定/否定或金融规则。列权重必须正数，每行宽度一致，状态索引必须唯一且在范围内。

`pinkClosingSlide.imageSlots["contact.qr"]` 可绑定 `assets_manifest.json` 中的图片；声明 `ratio: "1:1"` 与 `fitPolicy: "no-crop"` 或 `contain`，保留二维码自身 quiet zone。未绑定时该区域为空，不绘制假二维码。请提供透明背景、浅色码点且可独立解码的资产；套件不负责从 URL 编码二维码，也不验证任意输入图片的扫码语义。示例 QR 已独立验证指向用户指定的 `https://structurify.io/en`，网址只在示例资产清单中。二维码作为可替换图片保留位置/尺寸编辑，不承诺码点或 URL 在 PowerPoint 中直接编辑。

原 HTML 的动画、导航和伪 QR 不迁移。稀疏原生颗粒与轻量光晕近似网页气氛，不承诺 SVG 噪声逐像素一致；原生焦点标记替代 SVG 圆环/垂线组合。未声明原生换肤、任意旧稿保真、动画或其他比例。具体证据与未验证宿主见 [验收记录](../../../benchmarks/visual/cases/pink-script/golden-editorial/review.md)。
