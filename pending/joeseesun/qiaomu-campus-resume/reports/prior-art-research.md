# Prior-Art Research

- Researched at: 2026-08-04
- Queries: `ATS resume PDF generator`; `student resume builder`; `resume template design`
- Catalogs: skills.sh, SkillsMP, direct GitHub and official career-service sources
- Catalog run: `reports/prior-art-candidates-v2.json`（41 个去重候选，三组查询均成功）
- Rating evidence: unavailable；安装量与 GitHub stars 仅分别表示目录采用度和仓库关注度，不是质量评分

## Dialogue interview redesign v1.5

- Researched at: 2026-08-04
- Queries: `grill me interview agent skill`; `resume interview student skill`; `career story evidence interview`
- Catalog run: `reports/prior-art-interview-v15.json`（40 个去重候选；skills.sh 与 SkillsMP 三组查询均成功）
- Source review: canonical GitHub `SKILL.md` and repository license/metadata; no third-party scripts were executed
- Rating evidence: unavailable

| Candidate | Role | Mutable signal observed 2026-08-04 | Mechanism learned | Adopt / reject | License |
|---|---|---|---|---|---|
| [alirezarezvani/claude-skills: grill-me](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/grill-me/skills/grill-me) | skills.sh popularity anchor | 1K skills.sh installs; repository 23,749 GitHub stars | one question per turn, recommendation attached, depth-first branches, dependency order | adopted conversational cadence and depth-first evidence branches; rejected codebase-specific extractor/session wrappers | MIT |
| [mattpocock/skills: grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) | upstream concept anchor | SkillsMP indexed the skill; repository 201,786 GitHub stars | relentless narrowing and one-at-a-time questioning | adapted “relentless” into supportive student coaching; rejected hostile tone and the wrapper-only entrypoint | MIT |
| [addyosmani/agent-skills: interview-me](https://github.com/addyosmani/agent-skills/tree/main/skills/interview-me) | complementary intent specialist | SkillsMP indexed the skill; repository 81,485 GitHub stars | attach a hypothesis, restate understanding, require explicit confirmation | adopted correctable current judgments and explicit confirmation; rejected pseudo-precise 95% confidence as unsuitable for factual resume readiness | MIT |

Repository stars describe repository attention, not the quality of a specific skill. skills.sh installs describe ecosystem adoption, not user satisfaction or output correctness.

### v1.5 contribution ledger

- **Keep**: one question per turn; attach a concrete recommendation or hypothesis; resolve one branch before opening the next; restate before execution.
- **Adapt**: decision-tree branches become resume evidence loops—context, personal ownership, action, result, proof and interview explainability; the tone is supportive and students may skip or stop.
- **Reject**: hostile grilling, multiple questions per message, fixed question counts, unverifiable confidence percentages, codebase-only exploration tools and automatic generation after an ambiguous “sounds good.”
- **Invent**: a private `interview-ledger.json`; deterministic `assess_interview.py`; two evidence-loop minimum; skill-to-evidence linking; blocking-uncertainty gate; sensitive-field rejection; one-final-PDF default.

### v1.5 advantages and limits

- **Design advantage**: the interview is domain-specific rather than a generic requirements interview; every follow-up exists to improve a resume fact or remove an uncertainty.
- **Validated advantage**: unit tests cover ready state, missing explicit confirmation, insufficient evidence loops and sensitive fields; trigger evaluation includes Grill Me, one-question interview and mock-interview exclusions.
- **Hypothesis**: one-question cadence and periodic restatement may reduce student fatigue and surface stronger evidence than a giant intake form, but live student completion rate, comfort and recruiter outcomes remain `missing evidence`.

## Typography polish v1.4 note

This in-place typography pass reused the already verified corpus below rather than reopening broad template discovery: MIT CAPD for ATS-safe structure, RenderCV for content/design separation, Kami for editorial typography, and ResumeCollection for Chinese layout priors. The change generalized defects observed across all 12 local styles—mixed Latin/CJK glyph fallback, synthesized italics, flat weight hierarchy and mixed print units—rather than introducing a new visual family. Kimi K3 independently audited the before/after code and rendered pages; its provider evidence is recorded in `reports/k3-typography-*-v1.4-*.md`.

## Skill shortlist

| Candidate | Relevance | skills.sh installs* | Repository signal* | Concrete lesson | Adopt / reject | License |
|---|---|---:|---:|---|---|---|
| [RenderCV Skill](https://github.com/rendercv/rendercv-skill) | 结构化数据、多主题、确定性校验 | direct source | skill repo 10 stars；main repo 16.8k stars | 内容与设计分离；主题注册表；schema/runtime eval | 采用多主题与显式主题 ID；不引入 Typst/Pydantic 全依赖 | MIT |
| [cv-creator](https://skills.sh/erichowens/some_claude_skills/cv-creator) | ATS、岗位匹配、变体生成 | 606 | source repo page reported 158 stars | 同一事实生成岗位变体；把岗位分析与版式分开 | 采用变体思路；拒绝不可复核的 95/100 ATS 分数与 MCP 强依赖 | MIT repo |
| [Reactive Resume / resume-builder](https://github.com/amruthpillai/reactive-resume) | 多模板、本地数据、PDF 导出 | 384 | project repo 38k stars | 多模板来自同一数据；本地优先；预览与导出同源 | 采用单一 JSON → 六套输出与清单；拒绝账号、服务端和数据库依赖 | MIT |
| [resume-design-generation](https://skills.sh/eachlabs/skills/resume-design-generation) | 按行业区分现代、极简、技术等视觉族 | 291 | source repo 28 stars | 风格必须对应职业场景而不是随机换色 | 采用场景矩阵；拒绝图片生成、信息图、双栏、照片和作品集式简历 | source repo terms |

\* 可变指标观测于 2026-08-04；不得合并或称为用户评分。

## Professional and visual references

- [MIT CAPD undergraduate resume guide](https://capd.mit.edu/blog/2023/09/01/enhance-your-resume-a-guide-for-first-year-undergraduates/): 相关性、清晰字体、一致性、留白、反向时间顺序；避免文本框、表格、图像等 ATS 风险。
- [MIT sample resumes](https://capd.mit.edu/resources/sample-resumes/): 不同年级和职业方向需要不同内容重心。
- [Europass CV guidance](https://europass.europa.eu/en/create-europass-cv): 按岗位取舍、强动词、清晰表达与反向时间顺序。
- [OpenResume](https://github.com/xitanggg/open-resume): PDF 解析可读性应独立验证。
- [RenderCV design docs](https://docs.rendercv.com/user_guide/yaml_input_structure/design/): 主题是受约束的默认值集合，内容与视觉可以分离。
- [Jake's Resume](https://github.com/jakegut/resume): 单页、单栏、技术岗位、细分割线；仓库已于 2024-08-15 归档，只借鉴原则。
- [Awesome-CV](https://github.com/posquit0/Awesome-CV) 与 [AltaCV](https://github.com/liantze/AltaCV): 字体和主题可定制，但图标、照片、双栏与信息图不适合作为本技能默认 ATS 路径。
- [tw93/kami](https://github.com/tw93/kami): 暖纸色、今楷与油墨蓝继续作为六套中的编辑式主题。
- [mmmlllnnn/ResumeCollection](https://github.com/mmmlllnnn/ResumeCollection): 仓库在 2026-08-04 显示 862 stars、141 forks、MIT 许可；数字仅表示关注度。抽样检查 28 份预览，并解包 003/071/102/109/150/214 六份 DOCX；全部大量依赖 Word drawing/textbox，因此只吸收排版骨架，不复制资产或直接作为 ATS 模板。

## Contribution ledger

### Keep

- 一份结构化事实数据驱动所有输出。
- 单栏、标准章节、反向时间顺序与文本型 PDF。
- 本地优先、可编辑 HTML、PDF 文本提取与页数检查。
- 主题可选，但每套必须有明确默认值与适用场景。

### Adapt

- 把通用多主题机制收紧为六套面向中国大学生校招的视觉系统。
- 把“可无限自定义”改成主题注册表，避免随意拼色与版式漂移。
- 把 ATS 兼容从分数改为可复核证据：单栏、无表格/文本框、文本提取、A4、字体嵌入。
- 保留 Kami 字体与版权边界，同时让其他主题使用本机 Songti SC、PingFang SC、Menlo。

### Reject

- 两栏、侧边栏、照片、图标字体、二维码、技能条、信息图和图片化简历：文本顺序与解析风险不符合默认投递路径。
- 圆角卡片、闭合框、顶边和侧边线：不符合用户明确视觉约束。
- “ATS 95/100”“保证面试”等不可复核结果声明。
- 为使用主题而引入账号、数据库、云服务、MCP 或完整 LaTeX/Typst 工具链。

### Invent

- 六套主题共享一个 HTML 语义结构，只改变受控设计令牌与排版节奏。
- `--all-themes` 一次生成六套 HTML/PDF 和机器可读清单。
- `--reference-style` / `--all-reference-styles` 提供六个 ResumeCollection 安全重构预设，并在清单中保留来源编号和链接。
- 验证器按主题核对 `data-theme`、核心色、目标字体嵌入及禁止边框声明。
- 六套逐页截图比较，要求“差异不只换色”，同时保持 ATS 结构不变。
- 参考预设显式 opt-in；默认核心六主题不被 200 多个上游模板选项污染。

## Created skill advantages

- **Design advantage**: 六种风格直接映射六种投递情境，且共同保持无圆角框、无侧边栏、单栏语义结构。证据：`references/style-system.md`、`scripts/render_resume.py`。
- **Validated advantage**: 六套样例均通过 A4、1 页、文本提取、主题色、目标字体、零圆角与零禁止边框检查。证据：本地六套 `validation-*.json` 与单元测试。
- **Hypothesis**: 给候选人六套受控选项预计能减少盲目套模板并改善人与岗位的视觉匹配，但招聘方盲评、真实 ATS 跨平台解析和面试转化仍是 `missing evidence`。

## Missing evidence

- 没有六主题的招聘方盲评或真实面试转化实验。
- 没有对 Greenhouse、Lever、Workday、北森等真实平台逐一上传解析的证据。
- SkillsMP/skills.sh 不提供可复核的用户评分，目录采用度不能替代质量评价。
