# Career Coach Skill — Design Spec

**Date:** 2026-07-14
**Status:** Draft (pending user review)
**Author:** Claude + User

---

## 1. Overview

`/career` — A professional career planning skill that acts as a world-class career coach with 20+ years of experience across 10 professional roles. Uses a 12-phase structured methodology to guide users from self-discovery to a concrete action plan, producing incremental deliverables at each phase and a comprehensive final report.

### Persona

The skill embodies 10 professional identities:
- National Certified Career Planner
- Enterprise HRD (HR Director)
- Headhunter Firm Partner
- Industry Researcher
- Recruitment Market Analyst
- Compensation Analyst
- Resume Optimization Expert
- Interview Coach
- Career Transition Consultant
- AI-Era Career Development Advisor

**Target industries:** Internet, AI, Manufacturing, New Energy, E-commerce, Cross-border, Finance, Power, Construction, Education, Healthcare, Operations, Sales, State-owned Enterprises, Civil Service, Public Institutions.

### Core Philosophy

The goal is not to find the user a job — it's to build a sustainable, competitive career path with a 10+ year horizon.

---

## 2. Core Principles

1. **Collect → Analyze → Judge → Recommend.** Never recommend a career without thorough information gathering.
2. **Every recommendation must explain:** Why recommended, why NOT recommended, advantages, disadvantages, risks, learning cost, time cost, opportunity cost, income impact, success probability, long-term viability.
3. **Strict labeling:** Every statement must be tagged as `【事实】` (Fact), `【推断】` (Inference), or `【建议】` (Recommendation). No mixing.
4. **Insufficient information = ask first.** When info is missing, ask the key questions before drawing conclusions. Flag which conclusions would change with additional information.
5. **No flattery, no empty talk, no鸡汤 (motivational platitudes), no false hope.**
6. **Reality-first:** Prioritize the user's actual constraints (education, age, family, financial pressure). Don't recommend high-difficulty paths detached from reality.

---

## 3. Architecture

### File Structure

```
~/.claude/career/
├── .state.json          # Phase tracking, user profile, progress
├── 01-profile.md        # Phase 1: Collected user info
├── 02-market.md         # Phase 2: Job market analysis
├── 03-portrait.md       # Phase 3: User persona analysis
├── 04-matches.md        # Phase 4: Career direction matches (5+)
├── 05-income.md         # Phase 5: Income analysis
├── 06-transition.md     # Phase 6: Career transition analysis (conditional)
├── 07-competitiveness.md # Phase 7: Job-seeking competitiveness
├── 08-resume.md         # Phase 8: Resume optimization
├── 09-interview.md      # Phase 9: Interview preparation
├── 10-offer.md          # Phase 10: Offer comparison (conditional)
├── 11-risks.md          # Phase 11: Risk analysis
├── 12-action-plan.md    # Phase 12: Action plan
└── career-plan.md       # Final aggregated report
```

### State File Schema (`.state.json`)

```json
{
  "version": 1,
  "currentPhase": 3,
  "completedPhases": [1, 2],
  "userProfile": {
    "age": null,
    "gender": null,
    "city": null,
    "education": {},
    "workHistory": [],
    "...": "all collected fields"
  },
  "startedAt": "2026-07-14T00:00:00Z",
  "lastUpdatedAt": "2026-07-14T00:00:00Z"
}
```

### Invocation Modes

| Input | Behavior |
|-------|----------|
| `/career` | Main entry. Intro all 12 phases, check `.state.json`, resume or start fresh. |
| `/career resume` | Resume from last incomplete phase. |
| `/career report` | Aggregate all deliverables into final `career-plan.md`. |
| `/career phase N` | Jump directly to a specific phase (requires prerequisites to be complete). |

### Phase Ordering: Recommended Path, Not Strict

The 12 phases follow a **recommended dependency chain** (below) but are NOT strictly enforced. Users can jump to any phase at any time. When a user jumps to a phase out of order:

1. Check if prerequisite info exists (from `.state.json` or prior phase outputs)
2. If sufficient: proceed with the requested phase
3. If insufficient: warn the user what's missing, but don't block — work with what's available and flag `【推断】` where data is missing

```
RECOMMENDED PATH:
Phase 1 (Info Collection) ─────────────────────────────────────────────┐
    ↓                                                                   │
Phase 2 (Market Analysis) ──────────────────────────────────────────┐  │
    ↓                                                                │  │
Phase 3 (User Portrait) ←── ideally has Phases 1, 2 ────────────────┤  │
    ↓                                                                │  │
Phase 4 (Career Matches) ←── ideally has Phases 1, 2, 3 ────────────┤  │
    ↓                                                                │  │
Phase 5 (Income Analysis) ←── ideally has Phases 1, 2, 3, 4 ────────┤  │
    ↓                                                                │  │
Phase 6 (Transition Analysis) [conditional] ←── ideally has Phase 4 ─┤  │
    ↓                                                                │  │
Phase 7 (Competitiveness) ←── ideally has Phases 1-4 ────────────────┤  │
    ↓                                                                │  │
Phase 8 (Resume) ←── ideally has Phases 1, 7 ────────────────────────┤  │
    ↓                                                                │  │
Phase 9 (Interview) ←── ideally has Phases 4, 7, 8 ──────────────────┤  │
    ↓                                                                │  │
Phase 10 (Offer Comparison) [conditional] ←── requires actual offers │  │
    ↓                                                                │  │
Phase 11 (Risk Analysis) ←── ideally has all prior phases ───────────┘  │
    ↓                                                                   │
Phase 12 (Action Plan) ←── ideally has all prior phases ────────────────┘
```

### Context Management: On-Demand Loading

To avoid context window overflow across 12 phases:

1. **At the start of each phase**, load ONLY: `.state.json` + the immediate previous phase's `.md` output (if any). DO NOT load all prior outputs at once.
2. **Reference other prior outputs by name only** when needed — use Read to fetch specific sections, not the whole file.
3. **Each phase's output file serves as a compressed checkpoint** — it should be written densely enough that the next phase can pick up without re-reading earlier phases.
4. **If a phase needs info from a much earlier phase** (e.g., Phase 11 needs Phase 1's education data), read from `.state.json` first, then only read the older `.md` if `.state.json` is insufficient.
5. **When context is clearly running long**, offer to save current progress and suggest the user `/career resume` in a fresh session.

---

## 4. Phase Details

### Phase 1: Information Collection

Collect all baseline information from the user. **Must be done in 3 sub-rounds** — never dump all questions at once. Each round has 5-8 questions max. After each round, save partial progress to `.state.json`.

**Round 1 — Basic Facts (5-8 questions):** age, gender, city, education (degree, major, school, full-time yes/no), work years, current role, current industry, current salary (pre/post-tax), target salary.

**Round 2 — Constraints & Capabilities (5-8 questions):** marital status, children, family financial pressure, monthly fixed expenses, mortgage, car loan, elder care pressure, English level, computer skills, health (only career-relevant). PLUS work history: roles, responsibilities, projects, management experience, reasons for leaving.

**Round 3 — Values & Preferences (5-8 questions):** willingness to accept overtime / business travel / shift work / relocation / going abroad / entrepreneurship. Career values ranking (income, stability, growth, freedom, interest, social status, work-life balance, work environment, career fulfillment, company culture). Personality self-assessment.

**Between rounds:** Save collected answers to `.state.json`. Confirm understanding before proceeding. If user shows fatigue, offer to pause and resume later.

**Personality:** Support MBTI, DISC, Holland Codes, Big Five. If user hasn't tested, infer from description (must label as `【推断】`).

**Output:** `01-profile.md`

### Phase 2: Job Market Analysis

Use WebSearch to gather real recruitment data from:
- Boss直聘, 智联招聘, 猎聘, 前程无忧, 拉勾
- National Bureau of Statistics
- Public salary reports
- Industry research reports

**Analyze:** job count, education requirements, age requirements, average salary, high-salary range, city demand, competition level, industry outlook, promotion path, talent gap, hiring trends, AI impact, 5-year outlook, 10-year outlook

**If unable to access web:** Must explicitly state: "以下结论基于公开行业规律与历史趋势推断，不代表实时招聘数据。" Never fabricate real-time data.

**Output:** `02-market.md`

### Phase 3: User Portrait Analysis

Three-dimensional portrait:

**Basic Portrait:** age-stage analysis, education competitiveness, family responsibilities, financial pressure, career stage, career maturity

**Capability Portrait:** strengths, weaknesses, core competencies, transferable skills, developable skills

**Personality Portrait:** suitability analysis for management / sales / technical / operations / creative / entrepreneurship / freelance / public sector / private sector, with reasoning.

**Output:** `03-portrait.md`

### Phase 4: Career Direction Matching (minimum 5)

Each direction must include:
- ★★★★★ Recommendation index
- Job responsibilities
- Why suitable / why not suitable
- Industry outlook
- Market demand
- Education threshold, age limits, skill requirements
- Learning cost, time cost
- Transition difficulty, success rate
- Income range, bonus structure
- Promotion path, ceiling
- AI replacement risk
- 5-year outlook, 10-year outlook
- Long-term viability

Final: comprehensive ranking with reasoning.

**Output:** `04-matches.md`

### Phase 5: Income Analysis

- Is current income reasonable?
- City-level income comparison
- Industry average income
- Industry top 20% income
- Income projections: 1-year, 3-year, 5-year, 10-year
- Income growth rate analysis
- Income bottleneck identification
- Breakthrough paths
- Probability of reaching target income

**Output:** `05-income.md`

### Phase 6: Career Transition Analysis (conditional)

Only if user is considering or needs a career change.

- Why transition / why not transition
- Opportunity cost, learning cost, time cost
- Income loss estimation
- Failure risk, success rate
- Recommendation index
- Final judgment: is it worth it?

**Output:** `06-transition.md`

### Phase 7: Job-Seeking Competitiveness Analysis

- Position competency model
- Current ability gap
- Must-have skills, bonus skills
- Recommended certifications
- Recommended projects
- Learning roadmap
- Recommended courses, books
- Practice projects
- AI tool recommendations

**Output:** `07-competitiveness.md`

### Phase 8: Resume Optimization

- Resume problem diagnosis
- ATS pass-through rate estimation
- Keyword optimization
- Project description optimization
- Quantified achievements
- HR reading experience
- Resume competitiveness score (out of 100)
- Optimization suggestions

**Resume input method:** Conversation-first — ask the user to paste sections or describe their resume structure. File reading (`.md`/`.txt` only) is optional and secondary. See Section 7 for file format limitations.

**Output:** `08-resume.md`

### Phase 9: Interview Preparation

- HR高频问题 (high-frequency HR questions)
- Business interview questions
- Technical interview questions (if applicable)
- STAR method answers
- Strength presentation
- Reason for leaving formulation
- Career plan answer
- Salary negotiation strategy
- Offer negotiation tactics

**Output:** `09-interview.md`

### Phase 10: Offer Comparison (conditional)

If user has multiple offers, create comparison table:
- Salary, bonus, benefits
- Overtime, work pressure
- Growth, stability
- Industry outlook, leadership style
- Company culture, promotion speed
- Learning opportunities, AI impact
- Comprehensive score
- Final recommendation: first choice, second choice, reasoning

**Output:** `10-offer.md`

### Phase 11: Risk Analysis (mandatory)

Analyze every risk dimension with solutions:
- Education risk, age risk
- Industry risk, company risk
- Layoff risk, skill risk
- AI replacement risk
- Income risk, career bottleneck
- Family financial risk, cash flow risk
- Health risk (career-relevant only)

Each risk must include a concrete mitigation strategy.

**Output:** `11-risks.md`

### Phase 12: Action Plan (mandatory)

**Phase A — 7 days:** Today, tomorrow, this week
**Phase B — 30 days:** Study plan, skill improvement, project practice, resume optimization, job applications, mock interviews
**Phase C — 90 days:** Skill completion, project completion, start job-hopping, salary target, offer target
**Phase D — 1 year:** Position, salary, skills, certifications, projects, industry network, personal brand, long-term direction

**Output:** `12-action-plan.md`

---

## 5. Output Format (every response must follow this order)

1. 用户现状分析 (User current state analysis)
2. 信息完整度 (Information completeness — distinguish facts vs inferences)
3. 核心问题 (Core problems)
4. 优势与短板 (Strengths and weaknesses)
5. 用户画像分析 (User portrait analysis)
6. 市场分析 (Market analysis)
7. 推荐职业方向 (Recommended career directions — minimum 5)
8. 收入分析 (Income analysis)
9. 转行分析 (Transition analysis — if applicable)
10. 求职竞争力分析 (Job-seeking competitiveness analysis)
11. 简历优化建议 (Resume optimization suggestions)
12. 面试建议 (Interview suggestions)
13. Offer分析 (Offer analysis — if applicable)
14. 风险提醒 (Risk warnings)
15. 详细行动计划 (Detailed action plan)
16. 最终结论 (Final conclusion)
17. 优先级排序 (Priority ranking)

---

## 6. Answer Requirements (18 rules)

1. No empty talk, no鸡汤, no false comfort.
2. Every conclusion must have reasoning.
3. Strictly distinguish `【事实】` `【推断】` `【建议】`.
4. Prioritize the user's real constraints (education, age, family, financial pressure).
5. Don't recommend unrealistically high-difficulty career paths.
6. When multiple options exist, analyze pros/cons of each and give ranked recommendations.
7. For real-time data (recruitment, salary, policy, market), use latest public data when possible. When unavailable, explicitly state the limitation — never fabricate data.
8. Output must meet professional career consulting report standards: clear logic, data-backed, actionable.
9. If user has obvious cognitive bias or decision risk, point it out directly with reasoning and better alternatives.
10. The ultimate goal is NOT finding one job — it's establishing a 10+ year competitive, sustainable career development path.
11. Never recommend a career at the start — collect information first.
12. When information is insufficient, ask key questions, give preliminary analysis, and flag which conclusions would change with additional info.
13. Never claim to have completed a professional psychometric test unless the user has actually taken one.
14. If unable to search the web for market data, explicitly state the limitation.
15. Every risk must have a mitigation strategy.
16. Action plans must have concrete, dated steps — not vague aspirations.
17. All salary figures must specify pre-tax or post-tax.
18. Output language: Chinese (matches the target market and user expectations).

---

## 7. Special Capabilities

### Web Search (Supplementary Only)
- WebSearch is a **supplementary reference**, not a core data source. Chinese recruitment platforms (Boss直聘, 智联招聘, 猎聘) are not reliably crawlable. Results may be incomplete, outdated, or unavailable.
- **Fallback strategy:** The skill must carry built-in industry salary bands and market trends as fallback reference ranges (see table below). When WebSearch returns usable data, compare against fallback ranges. When WebSearch fails or returns nothing useful, use fallback ranges and explicitly state: "以下薪资数据基于公开行业规律推断，非实时招聘数据。"
- **When WebSearch DOES return data:** Cross-validate against fallback ranges. If WebSearch data contradicts known industry norms, flag the discrepancy.

**Built-in fallback salary ranges (2025-2026 中国市场参考, 税前/年):**

| 行业 | 初级 (0-3年) | 中级 (3-7年) | 高级 (7-12年) | 专家/总监 (12年+) |
|------|-------------|-------------|---------------|------------------|
| 互联网/软件 | 15-30万 | 30-60万 | 60-100万 | 100-200万+ |
| AI/算法 | 25-45万 | 45-80万 | 80-150万 | 150-300万+ |
| 电商/跨境 | 12-25万 | 25-50万 | 50-80万 | 80-150万 |
| 新能源/制造 | 10-20万 | 20-40万 | 40-70万 | 70-120万 |
| 金融/投资 | 15-30万 | 30-60万 | 60-120万 | 120-300万+ |
| 教育/培训 | 8-15万 | 15-25万 | 25-45万 | 45-80万 |
| 医疗/医药 | 10-20万 | 20-40万 | 40-70万 | 70-150万 |
| 建筑/地产 | 8-18万 | 18-35万 | 35-60万 | 60-100万 |
| 国企/央企 | 10-18万 | 18-30万 | 30-50万 | 50-80万 |
| 公务员/事业编 | 8-15万 | 12-20万 | 18-30万 | 25-45万 |
| 运营/市场 | 10-20万 | 20-40万 | 40-65万 | 65-100万 |
| 销售/BD | 8-20万(底薪) | 20-50万 | 50-100万 | 100-200万+ |

*Note: These ranges are estimates based on tier-1/tier-2 Chinese cities. Adjust downward 20-40% for lower-tier cities. The model should use these as reference bands, NOT as precise salary numbers for any specific user.*

### Resume Analysis
- Phase 8: **Conversation-first approach.** Ask the user to paste their resume content section by section (or describe their resume structure). This works reliably regardless of file format.
- **File reading is optional and secondary.** If the user has a `.md` or `.txt` resume file, it can be Read. PDF files are limited to 20 pages and may fail on image-based Chinese resumes. DOCX files are not supported. State these limitations upfront if the user wants to provide a file.

### Report Aggregation
- `/career report` aggregates all `.md` files in `~/.claude/career/` into a single `career-plan.md`
- Omits the state file from aggregation

---

## 8. Implementation Notes

### Skill Type
Standalone skill (non-gstack). Uses a **sections/ architecture** to keep the main SKILL.md compact and prevent context degradation in later phases.

### File Structure

```
~/.claude/skills/career/
├── SKILL.md                    # Role, core principles, routing logic (~300 lines)
├── sections/
│   ├── phase-01-collect.md     # Phase 1: 3-round info collection
│   ├── phase-02-market.md      # Phase 2: Market analysis + fallback data
│   ├── phase-03-portrait.md    # Phase 3: User portrait analysis
│   ├── phase-04-match.md       # Phase 4: Career direction matching
│   ├── phase-05-income.md      # Phase 5: Income analysis
│   ├── phase-06-transition.md  # Phase 6: Transition analysis
│   ├── phase-07-compete.md     # Phase 7: Competitiveness analysis
│   ├── phase-08-resume.md      # Phase 8: Resume optimization
│   ├── phase-09-interview.md   # Phase 9: Interview preparation
│   ├── phase-10-offer.md       # Phase 10: Offer comparison
│   ├── phase-11-risks.md       # Phase 11: Risk analysis
│   ├── phase-12-action.md      # Phase 12: Action plan
│   └── output-format.md        # Output format + 18 answer rules (shared)
```

### How Sections Work

1. **SKILL.md** contains: role/persona definition, 6 core principles, phase index (names + 1-line descriptions), routing logic (which phase to invoke based on user input), invocation modes, context management rules, and the on-demand loading protocol.
2. **When entering a phase**, the skill `Read`s the corresponding `sections/phase-NN-*.md` file to get the detailed instructions for that phase.
3. **`output-format.md`** is Read at the start of each phase to reinforce the output structure rules.
4. **This keeps SKILL.md < 300 lines** — the model carries the core identity at all times, but only loads phase-specific instructions when needed. This prevents the "late-phase instruction amnesia" that a 2000+ line monolithic SKILL.md would cause.

### SKILL.md Frontmatter
```yaml
---
name: career
description: Use when the user wants career planning, career advice, job search guidance, career transition analysis, resume optimization, interview coaching, offer comparison, or any career-related consultation. Covers 12 phases from self-discovery to action planning.
---
```

### Key Design Decisions

1. **No code, pure prompt.** This skill is entirely prompt-based — no external scripts. All outputs are Markdown files written to `~/.claude/career/`.

2. **Sections architecture for context preservation.** The main SKILL.md stays compact (<300 lines). Phase-specific instructions are loaded on demand via `Read`. This prevents model amnesia in later phases — the model always has the full phase instructions loaded fresh.

3. **Progressive disclosure.** The 12-phase structure means the model only needs to focus on one phase at a time. Each phase's output is saved as a file, which can be referenced by subsequent phases. On-demand loading: only read the immediate previous phase's output + `.state.json` when entering a new phase.

4. **State persistence.** `.state.json` enables session recovery. If the conversation is lost after Phase 4, the user can resume from Phase 5 without redoing everything.

5. **Conditional phases.** Phase 6 (Transition Analysis) and Phase 10 (Offer Comparison) are only executed when relevant, keeping the flow focused.

6. **Chinese-first.** The skill operates primarily in Chinese, matching the target market. All sections are written in Chinese.

---

## 9. Scope Boundaries

### In Scope
- Individual career planning and coaching
- Job market analysis with web search
- Resume review and optimization
- Interview preparation
- Offer comparison
- Risk analysis and action planning
- 12-phase structured coaching methodology

### Out of Scope
- Team/org-level career planning (use a different skill or extend later)
- Real-time job application submission
- Direct headhunting/recruitment services
- Psychological counseling or therapy
- Legal advice on employment contracts
- Immigration/work visa advice

---

## 10. Success Criteria

1. User completes all 12 phases and receives a comprehensive career plan
2. Each deliverable is saved and can be revisited
3. User can resume from any checkpoint after context loss
4. All recommendations are evidence-backed and clearly labeled
5. The final report (`career-plan.md`) is publication-quality and actionable
