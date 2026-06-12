# Skill 写作指南（SKILL.md 怎么写才好）

这份指南是官方 skill-creator 的写作规则翻译+改写，针对卖家场景加了示例。

---

## 1. Skill 的解剖

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter（name、description 必填）
│   └── Markdown 指令
└── 可选资源
    ├── scripts/    - 固定/重复任务的可执行代码
    ├── references/ - 按需加载的文档（大型参考）
    └── assets/     - 输出要用的素材（模板、图标、字体）
```

---

## 2. 三层加载机制（理解这个能让你写得更聪明）

Skill 采用**渐进式加载**：

| 层级 | 什么时候加载 | 大小建议 |
|------|--------------|----------|
| **1. 元数据**（name + description） | 永远在 Claude 上下文里 | ~100 词 |
| **2. SKILL.md 正文** | skill 触发时才加载 | < 500 行理想 |
| **3. Bundled resources** | 按需加载；脚本可不加载直接执行 | 无限制 |

**关键推论**：
- **常用的指令放 SKILL.md**，罕用的细节放 `references/xxx.md`
- SKILL.md 超过 500 行时，拆一层——在 SKILL.md 留"何时读哪个 reference"的指针
- `references/` 里 >300 行的文件，文件头加个目录

---

## 3. name

Skill 的英文标识符。小写 + 连字符。例：

- `keyword-rank-report`
- `review-crisis-response`
- `listing-ab-test`

不要用中文、下划线、驼峰命名。

---

## 4. description（决定触发的核心）

这是 Claude 决定要不要调用这个 skill 的**唯一依据**。

### 反例（太保守，触发不到）

> 一个关键词自然排名分析的 skill

问题：没说什么时候用、用在什么场景、用户会说什么话触发。Claude 读完一脸懵。

### 正例（有推力，会主动触发）

> 生成 BCG 品牌的关键词自然排名周报。每周一、用户说"查排名""跑排名周报""BCG 关键词"时调用，即使没明说"skill"也要触发。输入 ASIN 清单和核心词清单，产出 Markdown 报告 + 飞书消息通知异常。

为什么好：
- **做什么**：生成排名周报
- **什么时候用**：每周一、说这些话时
- **给了触发词**：查排名、跑排名周报、BCG 关键词
- **暗示了 input/output**：ASIN 清单、核心词清单、Markdown 报告、飞书消息
- **最后补了一句"即使没明说 skill 也要触发"**——对抗 Claude 的保守倾向

### 写 description 的三条原则

1. **包含做什么 + 什么时候用**（两者缺一不可）
2. **列出触发词**（用户最可能说的 3-5 句话）
3. **稍微推一下**——加一句"即使没明说 xxx 也要调用"或"即使用户说成 yyy 也触发"

---

## 5. SKILL.md 正文：核心写作模式

### 5.1 用祈使句，少用情态

| 软 | 硬（推荐） |
|----|-----------|
| "可以用 `scripts/xxx.py` 处理" | "用 `scripts/xxx.py` 处理" |
| "建议把结果存到 ..." | "把结果存到 ..." |
| "也许需要读一下 references/ 里的文件" | "读 references/xxx.md 了解 Y" |

### 5.2 解释 why，少用 ALWAYS / NEVER 大写强制

**反例**：

> ALWAYS use the template. NEVER skip the snapshot step.

Claude 会照做但不理解为什么。碰到 edge case 就僵住。

**正例**：

> 每次都用模板——模板里的字段是运营团队和财务对齐过的，不用模板他们读不懂。
> 
> 改 skill 之前先 snapshot——因为 baseline 对比需要旧版本；漏 snapshot 会导致迭代数据全作废。

Claude 懂了**为什么**，碰到 edge case 能合理判断。

### 5.3 输出格式用模板展示

与其抽象描述，不如直接给模板：

```markdown
## 报告结构

**总是**按这个模板输出：

# [品牌名] 关键词自然排名周报 (YYYY-MM-DD)

## 总体评估
- 检查 ASIN 数量：
- 异常（变化 > 10 位）：
- 严重（掉出前 20）：

## 严重情况（需立即介入）
[列表，每项含 ASIN、关键词、排名变化、建议动作]

## 异常观察
[同上]

## 数据附录
[完整数据表]
```

### 5.4 Examples Pattern

给正反例：

```markdown
## 触发的句子

**例 1：**
用户说：BCG 那个排名看下
判断：触发。这是简短口语，"看下"意味着要生成报告。

**例 2：**
用户说：昨天那份 BCG 排名怎么样
判断：不触发。这是问已生成报告的后续追问，不需要重新跑。
```

---

## 6. 多变体 skill 的组织

当 skill 支持多种变体（比如广告类型 SP/SB/SD，或不同品牌的不同模板），按变体拆 references：

```
ads-budget-optimizer/
├── SKILL.md              # 主干流程 + 选择逻辑
└── references/
    ├── sp.md             # SP 广告专属规则
    ├── sb.md
    └── sd.md
```

SKILL.md 里写"用户问的是 SP 就读 `references/sp.md`"。Claude 只加载需要的那份，上下文不会撑满。

---

## 7. SKILL.md 长度控制

| 行数 | 评估 |
|------|------|
| < 200 行 | 精简，ok |
| 200-500 行 | 理想区间 |
| 500-800 行 | 需要拆一层 |
| > 800 行 | 肯定要拆 |

拆的方法：把**细节性说明、长清单、大段示例**抽出到 `references/xxx.md`，SKILL.md 里只留指令 + 指针：

> 完整的错误分类规则见 `references/error-codes.md`，出错时读它做判断。

---

## 8. 写作风格

尝试用 theory of mind 解释事情的重要性，别用过多死板的 MUST。模型很聪明——只要你告诉它**为什么**，它能比死板规则处理得更好。

**建议流程**：
1. 写一份 draft
2. 放一会儿，然后用新视角重读
3. 删掉所有"不拉车"的部分
4. 给每个 ALWAYS / NEVER 都配一句 why；没 why 就改成解释性表达

---

## 9. 不要做的事

- **不要在 SKILL.md 里放 how-to 和 background 一起塞**——SKILL.md 是执行手册，不是教程
- **不要过度拟合具体例子**——skill 要能服务成千上万次调用
- **不要写"如果 X，可能要考虑 Y"这种软绵绵的指令**——模型需要能执行的判断
- **不要在 SKILL.md 里解释"这个 skill 的原理"**——用户不关心
- **不要把 description 写成推销词**——写成"判断触发条件"

---

## 10. 最后：验证 SKILL.md 格式

```bash
python ~/.claude/skills/zach-seller-skill-creator/scripts/quick_validate.py <你的 skill 路径>/SKILL.md
```

PASS 才继续。
