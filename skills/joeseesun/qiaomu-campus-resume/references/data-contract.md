# 数据契约

对话采集阶段先维护私有的 `interview-ledger.json`，其结构与生成门禁见 [对话式访谈与采集](intake-and-interview.md)。通过 `scripts/assess_interview.py` 且获得用户明确确认后，才把公开可用事实转换为本页定义的 `resume-data.json`。事实账本中的疑点、隐私字段和内部证据备注不得直接渲染。

`resume-data.json` 使用 UTF-8 JSON。根对象结构：

```json
{
  "version": 1,
  "language": "zh-CN",
  "theme": "ats-classic",
  "section_order": ["education", "experience", "projects", "skills", "awards"],
  "reference_style": "rc-071",
  "filename": "姓名_目标岗位_简历",
  "target": {"role": "后端开发实习", "company_type": "互联网"},
  "basics": {
    "name": "姓名",
    "headline": "目标岗位或一句定位",
    "phone": "手机号",
    "email": "邮箱",
    "location": "城市",
    "links": [{"label": "GitHub", "url": "https://..."}],
    "summary": "可选；应届生证据不足时省略"
  },
  "education": [],
  "experience": [],
  "projects": [],
  "skills": [],
  "awards": []
}
```

## 条目结构

教育：

```json
{
  "school": "学校",
  "degree": "本科",
  "major": "计算机科学与技术",
  "start": "2023.09",
  "end": "2027.06",
  "location": "杭州",
  "details": ["GPA 3.7/4.0（前 15%）", "相关课程：数据结构、操作系统"]
}
```

经历/项目共用字段：

```json
{
  "organization": "组织或项目名",
  "role": "角色",
  "start": "2025.03",
  "end": "2025.06",
  "location": "远程",
  "tech": ["Python", "FastAPI", "PostgreSQL"],
  "link": "https://...",
  "bullets": [
    {
      "text": "实现 6 个核心接口并补充 42 个自动化测试，通过课程验收。",
      "evidence_type": "user_confirmed",
      "source_note": "学生在 2026-08-03 访谈确认"
    }
  ]
}
```

技能：

```json
{"category": "编程语言", "items": ["Java", "Python", "SQL"]}
```

奖项：

```json
{"name": "比赛名称与奖项", "date": "2025.05", "detail": "团队角色或级别"}
```

## 枚举

- `language`: `zh-CN`、`en`
- `theme`: `ats-classic`、`kami`、`swiss`、`tech`、`campus`、`compact`
- `section_order`（可选）：只控制章节顺序，不隐藏非空章节；允许 `education`、`experience`、`projects`、`skills`、`awards`，不得重复。未设置时使用学生简历默认顺序。
- `reference_style`（可选）：`rc-003`、`rc-071`、`rc-102`、`rc-109`、`rc-150`、`rc-214`。设置后自动使用对应基础主题；未选择参考预设时省略该字段。
- `evidence_type`: `source_resume`、`user_confirmed`、`repository_verified`、`document_verified`、`conservative_estimate`

## 约束

- `experience` 与 `projects` 至少有一个非空；应届生最好有 2 项有证据的核心经历。
- 每项 1–5 条 bullet；每条必须是对象，禁止纯字符串绕过证据字段。每项优先 2–4 条，第 5 条只在确有独立、岗位相关成果时保留，验证器会给出密度警告。
- `source_note` 不渲染到 HTML/PDF。
- `filename` 不含扩展名和路径分隔符。
- 不存在的可选字段直接省略或使用空数组，不写“待补充”“N/A”“XXX”。
- 中文与英文、中文与数字之间保留正常空格，技术名词使用官方大小写；例：`交付 8 个 REST API`、`使用 Java 开发`、`GitHub`。
- 使用全角中文标点；禁止用斜体、全大写或特殊符号替代语义层级。
- `--all-themes` 会以同一份 JSON 的事实内容覆盖渲染主题，不修改原始 `theme` 字段，并输出六风格清单。
- `--all-reference-styles` 会从同一份事实数据生成六个参考预设并输出参考风格清单；命令行 `--reference-style` 优先于 JSON 字段。
- 完整可运行示例见 `assets/example-resume.json`。
