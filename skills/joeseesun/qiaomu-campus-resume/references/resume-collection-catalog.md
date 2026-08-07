# ResumeCollection 简洁参考目录

## 来源与边界

- 上游：[`mmmlllnnn/ResumeCollection`](https://github.com/mmmlllnnn/ResumeCollection)
- 核对提交：`56a18c26dd8d6ecd60df80b7dd8261b78dd70998`
- 核对日期：2026-08-04
- 仓库许可证：MIT；版权声明 `Copyright (c) 2024 mln`
- 上游 README 表示模板收集自互联网。仓库许可证不等于每个模板、图片或字体的原始权利链都已逐项澄清，因此本技能不打包上游 DOCX、预览图、图标、照片或字体。

本目录仅把上游模板当作视觉先例。所有可生成样式均以本技能自己的单栏 HTML/CSS 重构，继续服从 ATS、隐私、事实真实性和无框约束。

## 筛选方法

从中文模板目录抽样检查 28 份预览，优先寻找单栏、少色、明确层级、正文密度合理的候选。随后解包 6 个候选 DOCX，检查 `word/document.xml`：

| 参考编号 | drawings | textboxes | 结论 |
|---|---:|---:|---|
| 003 | 36 | 44 | 只吸收高密度蓝线节奏 |
| 071 | 28 | 24 | 只吸收姓名/岗位/日期对齐 |
| 102 | 21 | 30 | 只吸收扁平章条层级 |
| 109 | 9 | 26 | 只吸收双语章节与细线 |
| 150 | 41 | 30 | 只吸收灰白机构感 |
| 214 | 24 | 30 | 只吸收时间顺序强调 |

这些原文件均大量使用 Word 形状或文本框，不作为 ATS 安全模板直接复用。

## 六个可选参考预设

| 预设 ID | 用户可见名称 | 适用场景 | 吸收内容 | 明确移除 |
|---|---|---|---|---|
| `rc-003` | RC003 高密蓝线 | 软件、算法、数据；经历较多 | 紧凑节奏、深蓝细线、短段落 | 照片、上下色条、装饰图形 |
| `rc-071` | RC071 深蓝极简 | 通用校招、产品、运营 | 强对齐、深蓝标题、充足留白 | 头像、图标、目标卡片 |
| `rc-102` | RC102 章条商务 | 国企、制造、金融、咨询 | 扁平深蓝章条、正式层级 | 头像、图标、宽装饰色块 |
| `rc-109` | RC109 双语经典 | 外企、国际项目、英文环境 | 中英文章节标题、细线分节 | 头像、图标、顶部装饰条 |
| `rc-150` | RC150 灰白机构 | 研究助理、公共部门、教育 | 中性灰阶、机构化秩序 | 侧栏、头像、技能图示 |
| `rc-214` | RC214 天蓝时间序 | 实习连续、强调成长顺序 | 蓝色日期、清楚的时间顺序 | 竖向时间轴、头像、图标 |

## 用户选择规则

- 用户说“参考 ResumeCollection 071”或“深蓝极简”，使用 `--reference-style rc-071`。
- 用户只说“从 ResumeCollection 里选简洁模板”，先按岗位推荐 1 个，并说明另 2 个备选；只有风格选择会影响内容密度时才追问。
- 用户要比较时，运行 `--all-reference-styles`，一次生成六套参考预设。
- 用户未提及 ResumeCollection 时，仍按核心六主题流程，不把参考预设悄悄混入默认输出。
- 无论用户选择哪个预设，都不恢复原模板中的照片、二维码、图标、侧栏、竖线、技能进度条、闭合边框或圆角框。

## 命令

生成单个参考预设：

```bash
python3 scripts/render_resume.py resume-data.json \
  --reference-style rc-071 \
  --output-dir output
```

生成六个参考预设：

```bash
python3 scripts/render_resume.py resume-data.json \
  --all-reference-styles \
  --output-dir output
```

批量验收：

```bash
python3 scripts/validate_style_set.py \
  resume-data.json \
  output/resume_参考风格清单.json \
  --output output/validation-reference-styles.json
```

## 归属说明

“RC003”等名称仅用于指明视觉研究来源编号，不表示上游对本技能背书。重构预设与上游原模板不是像素级复刻，也不提供上游文件的再分发。
