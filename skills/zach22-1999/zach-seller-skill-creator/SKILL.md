---
name: zach-seller-skill-creator
description: 亚马逊卖家专用的 skill 创建器（中文）。当用户想把一个亚马逊运营/自媒体/日常工作流程变成可复用的 skill 时使用。触发场景包括但不限于：用户说"我想做一个 skill""把这个流程变成 skill""帮我写个自动化""优化我已有的 skill""给这个工作流做个自动化"，即使用户没用"skill"这个词，只要在描述"以后每次都这样做"的重复性工作时也应触发。本 skill 的核心差异：强制用户先回答 6 个业务问题（业务目标/过去做法/具体步骤/方法论/调用方式/期望输出）再进入创建流程，防止产出空洞 skill。Create new skills, improve existing skills, run evals and benchmarks — tailored for Amazon sellers with a Chinese-first workflow.
---

# 卖家 Skill 创建器

这是一个**中文版**的 skill 创建器，基于 Anthropic 官方 `skill-creator` 重构，针对亚马逊卖家（AI 基础较弱但有丰富业务经验的用户）优化。

## 核心差异：6 问硬门禁

官方 `skill-creator` 上来就问"这个 skill 要做什么"。卖家用户经常给出空洞的答案（比如"帮我做关键词分析"），导致产出的 skill 只是一份说明书、没有业务深度。

**本 skill 在官方流程前插入 6 个强制问题**。这 6 个问题是**硬门禁**——任何一个为空或答得敷衍，不得进入写 SKILL.md 的阶段。

---

## 工作流总览

```
【阶段 0】6 问硬门禁  ← 卖家版新增
    ↓
【阶段 1】意图澄清（基于阶段 0 已收集结果）
    ↓
【阶段 2】调研补齐
    ↓
【阶段 3】写 SKILL.md 初稿
    ↓
【阶段 4】写测试用例（2-3 个）
    ↓
【阶段 5】并行跑 with-skill + 基线
    ↓
【阶段 6】评分 + HTML 可视化
    ↓
【阶段 7】根据反馈迭代改进
    ↓
（可选）描述优化 + 打包
```

你的工作是根据用户当前所处的阶段，引导他们推进。如果用户直接说"我不想搞这么多测试，随便写个 skill 就行"，可以跳过阶段 4-7，但**阶段 0 的 6 问门禁不能跳过**。

---

## 与用户沟通的风格

用户群体：亚马逊卖家。可能对代码、JSON、断言（assertion）、基准（benchmark）等术语不熟悉。

沟通规则：
- 默认用中文对话
- 术语第一次出现时配一句通俗解释（例："assertion——就是用来判断 skill 输出合不合格的具体标准"）
- 不要动辄写"必须 MUST、绝对 NEVER"这样的强硬指令，而是解释"为什么这样做"
- 读到用户有明显的技术背景信号（会聊脚本、Git、JSON），可以切换到更专业的表达

禁用词（继承工作区规则）：赋能、抓手、综上所述、一言以蔽之、多维度赋能。

---

## 【阶段 0】6 问硬门禁

阶段 0 的正式执行脚本在 `references/6问引导式流程.md`。先读它，再开始问。**不要**把 `references/6问模板.md` 当成用户填写入口发出去。

### 阶段 0 的主协议

- 必须顺序走 `Q1 → Q6`，一个主题走完再进入下一个
- 每个主题优先用选项题，再用 1 段短简答补具体信息
- 选项里要主动使用亚马逊卖家预设，帮助用户点选：
  - 业务类型：自动化、风险监控、决策支持、团队交付
  - 工具/数据源：Sorftime、领星、SIF、本地 Excel/CSV/TXT、飞书表格、人工粘贴
  - 判断框架：BCG 健康阈值、异常阈值、趋势对比、优先级分层
- 不提供“整份 6 问模板发给用户填写”的入口
- 如果用户一上来贴长文，先拆回当前主题，继续逐层补问，不要直接视为阶段 0 完成

### 6 维答案到 SKILL.md 的映射

阶段 0 收集完后，把结果对应到 SKILL.md 的这些段落：

| 阶段 0 维度 | 映射到 SKILL.md 的哪里 |
|------------|------------------------|
| Q1 业务目标 | `## 业务背景` 段（解释 why） |
| Q2 现有做法 | `## 当前工作流（人工版）` 段（基线对照） |
| Q3 具体步骤 | `## Skill 工作流（自动版）` 段（主干指令，转成编号步骤） |
| Q4 方法论 | `## 核心原则 / 踩坑规避` 段（对应官方的 principles 概念） |
| Q5 调用方式 | YAML `description` 字段 + `## 触发场景` 段 |
| Q6 期望输出 | `## 输出规范` 段 |

### 硬门禁规则

采用“逐题门禁 + 阶段末总门禁”：

- 每一题结束时，先检查这一题是否已经具体到能落文档
- 任意一题出现以下情况，不得进入下一题，必须当场补问：
  - **为空**：用户跳过没回答
  - **敷衍**：答案只有一句话且不具体（例如 Q3 只回答“做数据分析”）
  - **矛盾**：Q2 说“没做过”，Q3 却列了成熟流程，需要澄清真实状态
  - **只谈动作不谈判断**：Q3 只有步骤顺序，没有任何“如果……则……”逻辑
  - **只谈经验不谈规则**：Q4 只有“看经验”“综合判断”，没有具体阈值、优先级或例外条件
  - **只谈结果不谈落点**：Q6 只说“给我报告”，没说保存到哪里或如何算完成

追问方式：引用用户的原话，指出哪里还不够具体，再给一个你想看到的粒度示例。

**例外**：用户明确说“我就想快速试试，先不管那么多”时，可以降级为只走 `Q1 + Q3 + Q6` 三个核心主题，但要明确告诉他：这样产出的 skill 更容易空、后面如果结果不满意需要回来补齐。

### 阶段 0 完成标志

当 6 个维度（或快速试试路径中的 3 个核心维度）都有可执行答案时，向用户复述一次（用 bullet list），让他确认。确认后才进入阶段 1。



---

## 【阶段 1】意图澄清

进入这一阶段的前提：阶段 0 的 6 维答案已经按引导式流程采集到位。

### 基于阶段 0 结果再补 4 个技术细节

官方 skill-creator 的标准 4 问，在这里作为补充：

1. **输出是否需要测试？** 有客观可验证输出的 skill（文件转换、数据提取、代码生成）适合做测试；主观输出的 skill（写作风格、设计）通常不用。根据 skill 类型给出建议，让用户决定。
2. **有没有现成的工具/脚本/MCP？** 如果用户提到过 Sorftime、领星、SIF 等 MCP，或者手头有 Python 脚本，让他说清楚 skill 里是否要直接复用。
3. **调用频率**是每周、每天、还是一事一议？这影响是否需要做 description 优化。
4. **谁来用？** 只有自己用、团队共用、还是要发布出去？团队共用的话要考虑不同人表达触发语的差异。

### 如果对话历史里已经有答案

经常发生的情况：用户进入本 skill 之前，已经在聊天里演示过一遍手动流程（比如"上周你帮我分析了 BCG 的关键词，就按那个流程做"）。这时优先从对话历史抽答案：用过的工具、步骤顺序、用户的修正、观察到的输入输出格式。抽完后复述给用户确认，别让他从头再讲一遍。



---

## 【阶段 2】调研补齐

在阶段 0-1 的基础上，主动问这些事情：

- **边界情况**：输入为空、数据缺失、API 失败时怎么办？
- **输入格式的具体例子**：用户提供一个真实文件或示例粘贴过来
- **成功标准**：什么样的输出算"对"？什么样的算"错"？
- **依赖项**：用到哪些 MCP、哪些文件路径、哪些外部脚本？

如果环境里有可用的 MCP（比如 Sorftime、领星、SIF），并且对本 skill 的调研有帮助（找类似 skill、查文档、看最佳实践），可以派子 agent 并行调研。目的是带着信息回到用户，降低他的负担。

这一步的目标：**把"写 SKILL.md 所需的事实"都收齐**。等到真正动笔写 SKILL.md 时不用再反复问。



---

## 【阶段 3】写 SKILL.md 初稿

详细的写作规则见 `references/skill写作指南.md`。这里只讲关键动作。

### YAML frontmatter 必填字段

- **name**：skill 标识符（英文小写 + 连字符，例如 `keyword-rank-report`）
- **description**：触发的主要机制。必须包含"做什么 + 什么时候用"。**推荐写得稍微"推一点"**——Claude 现在有"倾向于不调用 skill"的毛病，描述写保守了触发不到。

反例（太保守）：
> 一个用来做关键词自然排名分析的 skill

正例（有推力）：
> 生成关键词自然排名分析报告。当用户提到"关键词排名""自然位排名""Sorftime 反查""查 ASIN 曝光"时调用，即使没明说"分析"也要主动触发。

### 正文结构（按阶段 0 的 6 维答案填）

```markdown
# [Skill 名称]

## 业务背景           ← 映射问 1：业务目标
## 当前工作流（人工版）  ← 映射问 2：过去怎么做
## Skill 工作流（自动版） ← 映射问 3：具体步骤
## 核心原则 / 踩坑规避   ← 映射问 4：方法论
## 触发场景            ← 映射问 5：调用方式
## 输出规范            ← 映射问 6：期望输出
## 引用文件            ← 如果有 references/、scripts/、assets/
```

### 关键写法

- **用祈使句**：不是"可以用脚本处理"，而是"用 `scripts/xxx.py` 处理"
- **解释 why**：不要简单写"必须做 X"，写"做 X 是因为 Y，否则会 Z"
- **输出格式用模板**：用 `## 报告结构` + 完整模板示范
- **SKILL.md 正文控制在 500 行以内**，超了就把细节拆到 `references/xxx.md`，正文只留"何时读"的指引
- **大型 reference 文件（>300 行）要有目录**

### Skill 结构

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter
│   └── Markdown 正文
└── 可选资源
    ├── scripts/    - 固定/重复任务的可执行代码
    ├── references/ - 按需加载的文档
    └── assets/     - 输出使用的素材（模板、图标、字体）
```

### 三层加载机制（理解这个能帮你写得更好）

1. **元数据**（name + description）—— 永远在上下文里（~100 词）
2. **SKILL.md 正文** —— skill 触发时才进入上下文（<500 行）
3. **Bundled resources** —— 按需加载（无限制，脚本可以不加载直接执行）

所以"常用的指令放 SKILL.md，罕用的细节放 references"。

### 多领域组织

当一个 skill 支持多套方案（比如 SP/SB/SD 广告），按变体拆：
```
ads-report/
├── SKILL.md (主干流程 + 选择逻辑)
└── references/
    ├── sp.md
    ├── sb.md
    └── sd.md
```
Claude 只读需要的那份 reference。



---

## 【阶段 4】写测试用例

写完 SKILL.md 初稿后，想 2-3 个**真实用户会说的**测试提示词——不是抽象的"格式化数据"，而是"我 BCG 的这个 ASIN 最近广告占比掉得厉害，你按我们之前那个报告模板帮我看下"。

把测试保存到 `evals/evals.json`。**这一步先只写 prompt，不写断言**——断言在阶段 6 跑测试的同时补。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "用户的任务 prompt",
      "expected_output": "期望结果的描述",
      "files": []
    }
  ]
}
```

完整 schema 见 `references/schemas.md`。

把测试用例发给用户看：

> 我想用这几个测试 case 跑一下，你看合适吗？要不要加/减？



---

## 【阶段 5】并行跑测试与基线

这一段是**连贯动作**，不要中间停。**不要**用 `/skill-test` 或任何其他的测试 skill，就按下面的流程做。

结果存放位置：`<skill-name>-workspace/` 作为 skill 目录的**同级目录**。里面按迭代组织（`iteration-1/`、`iteration-2/`），每个测试 case 一个子目录（`eval-0/`、`eval-1/`）。不要一次建全，边做边建。

### Step 1：同一轮内同时派出 with-skill + baseline

对每个测试 case 派两个 subagent——一个带 skill，一个不带。**关键：这两个要在同一轮里同时派出**，不要先跑 with-skill，等结果出来再跑 baseline。原因是让它们在差不多的时间完成，减少系统状态差异。

**With-skill run：**

```
执行以下任务：
- Skill 路径：<skill 路径>
- 任务：<eval prompt>
- 输入文件：<eval 附带的文件；没有就写 none>
- 输出保存到：<workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- 要保存的输出：<用户真正在意的文件，比如 "the .docx file" 或 "the final CSV">
```

**Baseline run**（prompt 相同，但基线根据场景不同）：
- **新建 skill**：完全不给 skill。同 prompt、不给 skill 路径，保存到 `without_skill/outputs/`。
- **改进已有 skill**：用旧版本。改之前先 snapshot 一份 (`cp -r <skill 路径> <workspace>/skill-snapshot/`)，让 baseline subagent 指向快照，保存到 `old_skill/outputs/`。

同时给每个 eval 写 `eval_metadata.json`（assertions 先留空）。给每个 eval 起**有描述性的名字**（基于测试内容，不要叫 "eval-0"），目录名也用这个名字。如果这次迭代用到新的或修改过的 prompt，需要为每个新 eval 目录都重建这些文件——不要以为会自动继承上一次迭代的。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "用户的任务 prompt",
  "assertions": []
}
```

### Step 2：在测试跑着的时候，写 assertions

别干等。利用这段时间给每个测试 case 写**量化断言**并给用户解释。如果 `evals/evals.json` 里已有断言，也要 review 一遍再给用户解释。

好的断言特征：
- **客观可验证**（不能凭主观）
- **名字具描述性**——在 benchmark 查看器里一瞥就知道它在验证什么
- 主观 skill（写作风格、设计质量）用定性评估，不要硬套断言

写完后更新 `eval_metadata.json` 和 `evals/evals.json`。顺便告诉用户查看器里他会看到什么——两种东西：定性输出 + 定量 benchmark。

### Step 3：subagent 完成时，立刻记录计时

每个 subagent 完成时，你会收到一个通知，里面有 `total_tokens` 和 `duration_ms`。**立刻**保存到该 run 目录下的 `timing.json`：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

这是唯一能抓到这个数据的机会——过了通知就没了。一个一个处理，别想着攒一批再处理。



---

## 【阶段 6】评分、聚合、启动 HTML 查看器

所有 run 跑完后做 4 件事：

### 1. 给每个 run 打分

派一个 grader subagent（或者你自己 inline 做）读 `agents/grader.md` 的指令，对每个 assertion 用 outputs 做判断。结果写到每个 run 目录的 `grading.json` 里。**字段名必须是 `text`、`passed`、`evidence`**（不是 `name`/`met`/`details` 等变体），因为 HTML 查看器依赖这三个精确字段名。

能脚本化验证的 assertion，**写脚本跑**而不是肉眼看——脚本更快、更可靠、跨迭代可复用。

### 2. 聚合成 benchmark

在 zach-seller-skill-creator 目录下运行：

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

产出 `benchmark.json` 和 `benchmark.md`，包含每个配置的 pass_rate、用时、token 数（mean ± stddev 和 delta）。如果要手动生成 benchmark.json，schema 见 `references/schemas.md`。

**摆放顺序**：每个 with_skill 版本排在对应 baseline 前面，方便用户比对。

### 3. 做一遍分析师检查

读 benchmark 数据，看有没有被均值掩盖的 pattern。参考 `agents/analyzer.md` 的"Analyzing Benchmark Results"部分，关注：
- 某个 assertion 不管有没有 skill 都 pass——这种 assertion 没有区分度，等于废
- 方差特别大的 eval——可能是不稳定/flaky
- 时间/token 的 tradeoff

### 4. 启动 HTML 查看器

**定性输出 + 定量数据一起看**：

```bash
nohup python ~/.claude/skills/zach-seller-skill-creator/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "my-skill" \
  --benchmark <workspace>/iteration-N/benchmark.json \
  > /dev/null 2>&1 &
VIEWER_PID=$!
```

第 2 次及以后的迭代，加 `--previous-workspace <workspace>/iteration-<N-1>` 做对比。

**无显示环境（Cowork / 远程）**：用 `--static <输出路径>` 生成独立 HTML 文件，用户点 "Submit All Reviews" 时会下载 `feedback.json`。下载后把它放回 workspace 目录供下次迭代读取。

**别自己造轮子写 HTML**——用 `generate_review.py` 就好。

告诉用户类似这样的话：

> 我已经在你浏览器里打开了结果。有两个 tab：
> - **Outputs** — 每个 test case 点进去看输出，底下有文本框留反馈
> - **Benchmark** — 看定量对比
>
> 看完后来这边说一声就行。

### 用户在查看器里看到的

**Outputs tab**（每次一个 test case）：
- **Prompt**：当时给的任务
- **Output**：skill 产出的文件，能内嵌渲染的直接渲染
- **Previous Output**（迭代 2+）：折叠的上一轮输出
- **Formal Grades**（如果有 grading）：折叠的 assertion pass/fail
- **Feedback**：自动保存的反馈文本框
- **Previous Feedback**（迭代 2+）：上次的反馈

**Benchmark tab**：pass rate、时间、token 的统计概览，带 per-eval 细分和分析师观察。

导航用 prev/next 按钮或方向键。完成后点 "Submit All Reviews" 保存所有反馈到 `feedback.json`。

### Step 5：读反馈

用户说完事了之后，读 `feedback.json`：

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "图表缺坐标轴标签", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "完美，继续这样", "timestamp": "..."}
  ],
  "status": "complete"
}
```

空反馈 = 用户觉得 OK。把改进精力集中在有具体吐槽的 test case 上。

最后别忘了杀查看器：

```bash
kill $VIEWER_PID 2>/dev/null
```



---

## 【阶段 7】迭代改进

这是整个循环的**心脏**。测试跑了，用户审过了，现在要根据反馈把 skill 改好。

### 改进的 4 条心法

1. **从反馈泛化**。重点：我们是在造一个要被用**成千上万次**的 skill，和用户在这里迭代只是用 2-3 个例子加快节奏。用户对这几个例子太熟了，评估输出很快。但如果 skill 只对这几个例子好、换个 prompt 就崩，那就废了。**别做过度拟合的 fiddly 修改**，也别加"oppressively constrictive MUSTs"。碰到顽固问题，换个角度、换个比喻、换个工作模式——试的成本不高，说不定灵光一现。

2. **保持 prompt 精简**。删掉不拉车的部分。**读 transcripts（不只是最终输出）**——如果看到 skill 让模型花了大段时间做无用功，就干掉那些让它这么做的指令，看会怎样。

3. **解释 why**。让模型理解你为什么这样要求。现在的 LLM 很聪明，有 theory of mind，给它理由胜过给它规矩。如果你发现自己在写 ALWAYS、NEVER 或特别死板的结构，这是**黄色警报**——试着换成解释原因的表达。这是更人性化、更有效的方式。

4. **找跨测试的重复劳动**。读 transcripts，看 subagent 是不是每次都独立写了类似的辅助脚本、或都走了相同的多步流程。如果 3 个 test 都让 subagent 写了 `create_docx.py` 或 `build_chart.py`，那就是强信号：**把这个脚本内置到 skill**（写一次放 `scripts/`，指令里告诉 skill 用它）。省下每次调用的重复造轮子。

这一步挺重要的（我们在这儿创造价值哩），你的思考时间不是瓶颈——**慢一点、想透**。建议写一份 draft，然后换个视角重看、改进。真正站进用户的位置，理解他要什么。

### 迭代循环

改完之后：

1. 把改动应用到 skill
2. 重跑所有 test case 到新的 `iteration-<N+1>/`，**包括基线**。
   - 新 skill：基线永远是 `without_skill`（不加载 skill），跨迭代不变
   - 改进已有 skill：自行判断——baseline 用最开始的版本，还是上一轮迭代，都可以
3. 启动查看器时加 `--previous-workspace <上一迭代目录>`
4. 等用户审完说"好了"
5. 读新反馈，再改，再循环

何时停：
- 用户说满意
- 反馈基本全空（都 OK）
- 不再有有意义的进步



---

## 进阶：盲比对 A/B 测试

当你需要对两个版本的 skill 做更严谨的对比（例如用户问"新版本真的比旧版好吗？"），有一套盲比对机制。详见 `agents/comparator.md` 和 `agents/analyzer.md`。

核心思想：把两个输出扔给一个独立 agent，**不告诉它谁是谁**，让它判质量；然后解盲再分析赢家为什么赢。

这是可选的、需要 subagent，多数用户用不到。人工审阅循环通常已经够用。



---

## 进阶：描述（description）触发优化

SKILL.md frontmatter 的 `description` 是决定 Claude 是否调用这个 skill 的主要机制。创建或改进 skill 后，可以主动问用户要不要做 description 优化。

### Step 1：生成触发评估用的查询

做 20 个 eval queries——混合 should-trigger 和 should-not-trigger。存成 JSON：

```json
[
  {"query": "用户的 prompt", "should_trigger": true},
  {"query": "另一个 prompt", "should_trigger": false}
]
```

查询必须**真实具体**，是 Claude Code 或 Claude.ai 用户会真的输入的东西。不要抽象请求，要有细节：文件路径、用户的背景、列名和数值、公司名、URL、一点背景故事。有的可以小写、有的可以有缩写或错别字、有的像日常口语。长度混合，关注边缘情况而不是显而易见的。

反例：`"格式化一下这份数据"`、`"从 PDF 提取文字"`、`"做个图表"`

正例：`"我老板刚扔给我一个 xlsx 文件（在我下载目录里，叫 'Q4 sales final FINAL v2.xlsx' 之类的），她想让我加一列显示利润率百分比。我记得收入在 C 列、成本在 D 列"`

- **should-trigger**（8-10 个）：想覆盖度。同一个意图的不同说法——有正式、有口语。**故意不直接提 skill 名或文件类型**但显然需要它的 case。加一些少见场景，以及和别的 skill 竞争但应该赢的 case。
- **should-not-trigger**（8-10 个）：**最有价值的是 near-miss**——和 skill 关键词/概念类似，但真正需要别的东西的 query。想邻近领域、模糊措辞（naive 关键词匹配会触发但不该触发的）、以及碰到 skill 涉及的事情但应该用别的工具的情况。

**要避免**：不要让 should-not-trigger 显而易见地无关。"写个 fibonacci 函数"作为 PDF skill 的反例——太简单了，测不出任何东西。反例要**真的棘手**。

### Step 2：和用户一起审

用 HTML 模板给用户看 eval set：

1. 读模板 `assets/eval_review.html`
2. 替换占位符：
   - `__EVAL_DATA_PLACEHOLDER__` → eval items 的 JSON 数组（不要加引号——它是 JS 变量赋值）
   - `__SKILL_NAME_PLACEHOLDER__` → skill 名
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → skill 当前 description
3. 写到临时文件（比如 `/tmp/eval_review_<skill-name>.html`）并打开：`open /tmp/eval_review_<skill-name>.html`
4. 用户可以改 query、切换 should-trigger、加减条目，然后点 "Export Eval Set"
5. 文件下载到 `~/Downloads/eval_set.json`——如果有重名（`eval_set (1).json`），取最新的

**这一步很关键**——bad eval queries 会导致 bad description。

### Step 3：跑优化循环

告诉用户："这个要跑一会儿——我在后台跑，过一会儿来看进度。"

把 eval set 存到 workspace，然后后台跑：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <当前会话的 model id> \
  --max-iterations 5 \
  --verbose
```

`--model` 用当前会话的 model id（你的 system prompt 里有），这样触发测试匹配用户真实体验。

跑的同时，周期性 tail 一下输出，告诉用户跑到第几轮、分数如何。

这个脚本会自动做完整优化循环：把 eval set 分成 60% train + 40% held-out test，对当前 description 跑 3 遍（稳定性），用 extended thinking 让 Claude 基于失败案例提改进，每个新 description 在 train 和 test 上重评，最多 5 轮。结束时在浏览器打开 HTML 报告，返回 JSON（含 `best_description`——**用 test 分数选而不是 train 分数**，防过拟合）。

### 触发机制的原理

理解触发机制有助于写好 eval queries。Skills 在 Claude 的 `available_skills` 列表里展示 name + description，Claude 根据 description 决定要不要用。**关键**：Claude 只在自己不容易搞定的任务时才咨询 skill——像 "读这份 PDF" 这种简单一步就能办完的查询，即使 description 完全匹配也可能不触发，因为 Claude 用基础工具自己就能做。复杂、多步、专业的查询才会可靠触发。

所以**你的 eval queries 应该有足够的实质内容**让 Claude 觉得需要咨询 skill。过简的 query（"读文件 X"）是差的 test case——不管 description 多好都不会触发。

### Step 4：应用结果

把 JSON 输出里的 `best_description` 更新到 skill 的 SKILL.md frontmatter。给用户看 before/after 和分数。



---

## 打包分发

**只在有 `present_files` 工具时跑**。没有就跳过。有的话，把 skill 打包并把 .skill 文件交给用户：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包完，告诉用户生成的 `.skill` 文件路径，他可以安装到自己的环境。



---

## 特殊环境适配

### Claude.ai（没有 subagent）

核心流程相同（draft → test → review → improve → 循环），但因为没 subagent，机制要调整：

- **跑测试**：没法并行。每个 test case 自己读 SKILL.md，按其指令完成任务。逐个做。这比独立 subagent 不严谨（你自己写 skill 自己跑，信息对称了），但搭配人工审阅还是有用的 sanity check。跳过 baseline runs，用 skill 做完就行。
- **审阅结果**：如果打不开浏览器，跳过浏览器查看器，直接在对话里呈现。每个 test case 展示 prompt 和 output；如果输出是 .docx 之类用户需要下载的文件，存到文件系统并告诉路径，让用户下载查看。"这样 OK 吗？有要改的吗？"
- **Benchmark**：跳过定量 benchmark——它依赖 baseline 对比，没 subagent 就没意义。聚焦定性反馈。
- **Description 优化**：依赖 `claude -p`（只 Claude Code 有），跳过。
- **盲比对**：需要 subagent，跳过。
- **打包**：`package_skill.py` 只要 Python 和文件系统就能跑，能用。

### Cowork

- 有 subagent，主流程（并行跑、基线、grading）都能用。如果遇到严重 timeout，可以串行跑 test prompts。
- 没浏览器/显示，生成查看器时用 `--static <输出路径>` 写独立 HTML，给用户一个链接点开。
- Cowork 环境下 Claude 经常**不主动**生成 eval viewer，这里大写提醒：**跑完测试后，在你自己评估前，先用 `generate_review.py` 生成 eval viewer 给人看**。你要的是让人尽快看到例子！
- 反馈机制不同：没运行中的 server，viewer 的 "Submit All Reviews" 会下载 `feedback.json`，你读这个文件（可能要先申请访问）。
- 打包能用。
- Description 优化（`run_loop.py` / `run_eval.py`）在 Cowork 里能跑（它用 subprocess 调 `claude -p`，不用浏览器），但**等 skill 稳定了、用户说 OK 了再做**。



---

## 引用文件

`agents/` 目录是给专业子 agent 的英文指令（Claude 派子 agent 时直接读，英文更稳）：

- `agents/grader.md` — 如何用 outputs 评估 assertions
- `agents/comparator.md` — 如何做盲 A/B 对比
- `agents/analyzer.md` — 如何分析一个版本为什么赢

`references/` 目录：
- `references/schemas.md` — evals.json、grading.json 等的 JSON 结构（中文）
- `references/6问引导式流程.md` — 阶段 0 的唯一执行脚本（逐题引导 + 门禁校验）
- `references/6问模板.md` — 阶段 0 结果如何映射到 SKILL.md 的内部参考
- `references/skill写作指南.md` — SKILL.md 写作的完整规则与示例


---

最后再重复一次核心循环：

1. 用户提出想法 → 过 6 问硬门禁
2. 写 SKILL.md 初稿 → 写 2-3 个测试用例
3. 并行跑 with/without 测试 → 启动 HTML 查看器让用户看
4. 读用户反馈 → 改 skill
5. 重复直到满意 → 打包分发

遇到时记得把这些步骤加入 TodoList，避免漏掉。

祝创建顺利！
