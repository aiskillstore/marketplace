# 六主题系统

六套主题不是“从好看到不好看”的排名，而是六种投递情境的视觉起点。内容和文本顺序保持单栏一致；主题改变字体组合、页头构图、色彩与标题节奏，`sparse / balanced / dense` 再根据真实内容量调整字号和垂直节奏。

## 共同底线

- A4，默认一页，最多两页。
- 单栏、标准章节、正文文本型 PDF。
- 禁止照片、侧边栏、表格布局、信息图、技能条、卡片轮廓、闭合边框和圆角框。
- CSS 只允许 `border-bottom` 横向分割线；禁止 `border`、`border-top`、`border-left`、`border-right`、`outline` 与 `border-radius`。
- 姓名、联系方式与章节标题必须保持正常文本顺序，不能依靠定位或图形替代。
- 风格不能改变事实、夸大数字或绕过证据字段。
- 字体、字阶、数字、混排与垂直节奏必须遵循 [字体与印刷排版系统](typography-system.md)。
- “只允许 `border-bottom`”约束的是边框声明；无轮廓、无圆角的浅色页头 wash 或完整横向章节色带可以使用，但不得形成卡片或改变 ATS 顺序。

## 主题矩阵

| ID | 中文名 | 默认场景 | 视觉机制 | 目标字体 |
|---|---|---|---|---|
| `ats-classic` | ATS 经典 | 通用校招、国企、金融、咨询 | 居中页头、宋体层级、酒红细线、白纸 | Songti SC |
| `kami` | Kami 编辑式 | 教育、内容、品牌、产品 | 暖纸色、油墨蓝、今楷、编辑式留白 | TsangerJinKai02 |
| `swiss` | 瑞士现代 | 产品、数据、商业分析、互联网 | 左对齐大标题、无衬线、红色基线、强网格感 | PingFang SC |
| `tech` | 技术工程 | 软件、AI、算法、数据、DevOps | 冷灰纸、工程蓝、等宽标题、项目式信息节奏 | PingFang SC + Menlo |
| `campus` | 校园清新 | 第一份实习、运营、市场、教育 | 暖白纸、青绿、柔和页头色面、宽松节奏 | PingFang SC |
| `compact` | 高密信息 | 项目或实习很多但需一页 | 小页边距、紧凑层级、蓝灰线、信息密度优先 | Songti SC |

## 选择规则

1. 用户明确点名主题：只生成该主题。
2. 用户明确要求“多种风格”或“给我选择”：使用 `--all-themes` 一次生成六套；没有明确偏好时由岗位与内容决定一套默认主题。
3. 技术岗位但没有视觉偏好：内容策略优先推荐 `tech`，同时保留 `ats-classic` 作为稳健备选。
4. 正式机构、银行、咨询、国企：优先 `ats-classic`。
5. 教育、内容、品牌或希望保持人文气质：优先 `kami`。
6. 项目很多导致一页拥挤：先删弱内容，再考虑 `compact`；不能直接把正文压到 9pt 以下。

## ResumeCollection 可选参考预设

参考预设不属于默认六主题，也不是原 Word 模板复刻。只有用户点名 ResumeCollection、具体编号或要求比较其简洁方案时，才按 [ResumeCollection 简洁参考目录](resume-collection-catalog.md) 路由：

| ID | 名称 | 基础主题 |
|---|---|---|
| `rc-003` | 高密蓝线 | `compact` |
| `rc-071` | 深蓝极简 | `swiss` |
| `rc-102` | 章条商务 | `tech` |
| `rc-109` | 双语经典 | `ats-classic` |
| `rc-150` | 灰白机构 | `ats-classic` |
| `rc-214` | 天蓝时间序 | `campus` |

每个参考预设继续遵守单栏、无照片、无图标、无侧栏、无竖线、无圆角框和仅横向 `border-bottom` 的共同底线。

## 研究依据与边界

- MIT CAPD 强调相关性、反向时间顺序、清晰字体、统一格式、留白，以及避免文本框、表格、图像等常见 ATS 风险：<https://capd.mit.edu/blog/2023/09/01/enhance-your-resume-a-guide-for-first-year-undergraduates/>
- Europass 强调按岗位取舍、清晰表达、强动词与反向时间顺序：<https://europass.europa.eu/en/create-europass-cv>
- RenderCV 展示了“同一结构化内容 + 多主题 + 严格校验”的可复用设计模式：<https://github.com/rendercv/rendercv>、<https://docs.rendercv.com/user_guide/yaml_input_structure/design/>
- OpenResume 将 PDF 解析可读性作为独立检查能力：<https://github.com/xitanggg/open-resume>
- Jake's Resume 提供单页、单栏、细分割线的技术岗位范式，但其仓库已于 2024 年归档，因此只吸收版式原则，不依赖其实现：<https://github.com/jakegut/resume>
- Awesome-CV 与 AltaCV 证明了字体和主题定制空间，但照片、图标、双栏和信息图不进入本技能的 ATS 默认路径：<https://github.com/posquit0/Awesome-CV>、<https://github.com/liantze/AltaCV>
- ResumeCollection 提供大量中文 Word 简历视觉样本；本技能只从 003/071/102/109/150/214 吸收排版骨架，并移除其照片、图标、侧栏、竖向时间轴和文本框依赖：<https://github.com/mmmlllnnn/ResumeCollection>

这些资料支持版式原则与场景划分，不证明任何主题能提高面试率。真实 ATS 平台对六套 PDF 的横向解析对比与招聘方盲评仍是 `missing evidence`。
