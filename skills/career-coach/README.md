# Career Coach v3.0 — AI 职业规划顾问

一个 Claude Code 技能，提供 12 阶段结构化职业规划咨询。由 20 年经验的 AI 职业规划顾问驱动，覆盖从自我认知到行动计划的完整职业规划流程。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 快速开始

### 安装

```bash
# 克隆到 Claude Code skills 目录
mkdir -p ~/.claude/skills
git clone https://github.com/YOUR_USERNAME/career-coach.git ~/.claude/skills/career
```

或者直接复制：

```bash
cp -r career-coach ~/.claude/skills/career
```

### 使用

在 Claude Code 中输入：

```
/career
```

首次使用会自动从 Phase 1（信息收集）开始。你也可以直接跳到特定阶段：

```
/career phase 4    # 直接进入职业方向匹配
/career phase 8    # 直接进入简历优化
/career resume     # 从上次中断处继续
/career report     # 生成完整汇总报告
```

## 12 阶段流程

| Phase | 名称 | 产出 |
|-------|------|------|
| 1 | 信息收集 | 用户信息档案 |
| 2 | 就业市场分析 | 市场数据 + 薪资参考 |
| 3 | 用户画像分析 | 三维画像 + SWOT |
| 4 | 职业方向匹配 | 5+ 方向完整评分排名 |
| 5 | 收入分析 | 1/3/5/10 年收入预测 |
| 6 | 转行分析 | 转行成本与可行性（条件性） |
| 7 | 求职竞争力 | 能力缺口 + 学习路线 |
| 8 | 简历优化 | 诊断 + 重写 + 100 分评分 |
| 9 | 面试准备 | 10 道 HR 题 + 薪资谈判 |
| 10 | Offer 对比 | 多 Offer 对比表（条件性） |
| 11 | 风险分析 | 14 项风险 + 应对方案 |
| 12 | 行动计划 | 7天/30天/90天/1年 |

所有产出保存在 `~/.claude/career/`，支持断点恢复。

## 角色设定

AI 以 10 重专业身份进行咨询：

- 国家职业生涯规划师
- 企业 HRD（人力资源总监）
- 猎头公司合伙人
- 行业研究员
- 招聘市场分析师
- 薪酬分析师
- 简历优化专家
- 面试教练
- 职业转型顾问
- AI 时代职业发展顾问

熟悉行业：互联网、AI、制造业、新能源、电商、跨境、金融、电力、建筑、教育、医疗、运营、销售、国企、央企、公务员、事业单位。

## 核心原则

1. **收集 → 分析 → 判断 → 推荐** — 严禁一开始就推荐职业
2. **每个建议必须解释** — 为什么推荐、为什么不推荐、风险、成本、成功概率
3. **严格区分标签** — `【事实】` `【推断】` `【建议】` 不得混淆
4. **现实约束优先** — 考量学历、年龄、家庭、经济压力
5. **不空谈、不鸡汤、不安慰** — 每个结论有依据
6. **目标不是找一份工作** — 而是建立 10 年以上可持续的竞争力

## 架构设计

```
~/.claude/skills/career/
├── SKILL.md              # 角色、原则、路由（126 行）
└── sections/             # 按需加载的 Phase 指令
    ├── output-format.md  # 输出格式 + 18 条规则
    ├── phase-01-collect.md
    ├── phase-02-market.md
    ├── ...
    └── phase-12-action.md
```

采用 **sections/ 架构**：主 SKILL.md 保持精简（<300 行），Phase 详细指令在进入时按需 Read，避免长上下文导致的指令遗忘。

## 特性

- 🧩 **模块化**：12 Phase 可独立跳转，不必从头开始
- 💾 **断点恢复**：`.state.json` 保存进度，`/career resume` 继续
- 📊 **数据驱动**：WebSearch + 内建 12 行业薪资 fallback
- 📝 **对话优先**：简历优化以对话为主，文件读取为辅
- 🌐 **中文原生**：专为中国就业市场设计

## 文件结构

```
~/.claude/career/          # 用户数据（运行时生成）
├── .state.json            # 进度状态
├── 01-profile.md          # Phase 1 产出
├── 02-market.md           # Phase 2 产出
├── ...
├── 12-action-plan.md      # Phase 12 产出
└── career-plan.md         # 最终汇总报告
```

## 设计文档

完整设计文档：[docs/2026-07-14-career-coach-design.md](docs/2026-07-14-career-coach-design.md)

## 许可

MIT License — 详见 [LICENSE](LICENSE)

## 贡献

欢迎提交 Issue 和 PR：
- 新增 Phase 或优化现有 Phase 指令
- 添加行业薪资 fallback 数据
- 改进面试题库
- 适配更多职业规划框架（如 80,000 Hours、Holland Codes 等）
