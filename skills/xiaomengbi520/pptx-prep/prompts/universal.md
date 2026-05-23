# PPTX Material Pre-Check

Paste this at the start of your conversation before asking AI to create any PowerPoint presentation.

## Instructions for the AI

Before generating any PPTX or slides, you MUST run this material pre-check protocol.

### Phase 1: 确认幻灯片结构
If the user hasn't given a clear outline, ask 3-5 questions to lock down: how many slides, topic, key sections. Present a numbered skeleton. Wait for confirmation before proceeding.

### Phase 2: 扫描人类依赖材料
Check each slide against 5 categories. For each item, use these labels:

| 图标 | 状态 | 含义 |
|------|------|------|
| ✅ | 可用 | Material ready, no user action needed |
| ❌ | 需补充 | Must be provided by user (photo, data, logo) |
| 🤖 | 待核实 | AI can draft, but user should verify accuracy |

Output format:
```
## 材料扫描

| Slide | 材料 | 状态 |
|-------|------|------|
| 1 封面 | 标题文案 | ✅ 可用 |
| 1 封面 | 封面照片 | ❌ 需补充 |
| 2 简介 | 基本信息 | 🤖 待核实 |
...
```

5 Categories:
- **Category 1: Personal/Identity** — names, roles, dates, contact info (关键词: 团队、成员、姓名、职位、日期)
- **Category 2: Visual Assets** — photos, logos, screenshots (关键词: 照片、Logo、截图、头像)
- **Category 3: Data/Statistics** — revenue, metrics, survey results (关键词: 收入、数据、指标、统计)
- **Category 4: Custom Content/Branding** — slogans, brand colors, quotes (关键词: 口号、品牌色、愿景、引用)
- **Category 5: External References** — URLs, PDFs, templates (关键词: 内网、参考文档、模板)

### Phase 3: 缺失阈值判断
If ❌ 需补充 > 50% of total materials → warn user, offer to proceed anyway. If ≤ 50%, continue.

### Phase 4: 内容生成分层
- General knowledge → ✅ 可生成 (AI-generated, verified)
- Accuracy matters → 🤖 待核实 (AI draft, user reviews)
- Must be user-provided → Phase 5

### Phase 5: 收集材料
When user wants to provide materials, create a `materials/` folder and tell them the path. After they put files in, scan and auto-match by content analysis, filename, and description. Present a full matching table for confirmation. **If user corrects any match, re-display the complete corrected table.**

### Phase 6: 宽高比检查 + 即时选项
If photo aspect ratio differs from slot by >10%, immediately present A/B/C:
- A) contain — show whole photo, empty space on sides
- B) cover — fill slot, crop edges
- C) swap for different photo

**Never flag a risk without presenting the choice.**

### Phase 7: 质量门禁
Reject photos <200px any dimension (with override option). Flag wrong content types.

### Phase 8: 内容溢出检查
If text > slot capacity × 1.5 → warn. If > 3× → mention splitting but mark as not recommended.

### Phase 9: 缺失项处理
For missing items: A) AI search (prep searches real photos NOW, downloads, marks ready), B) AI generate (prep creates illustration NOW, downloads, marks ready), C) placeholder, D) user uploads. A/B must complete before handoff. No ai-fill left in manifest. Always keep D.

### Phase 10: 输出 manifest
Write `manifest.yml` to the project directory.

### Phase 11: 输出汇总
Use icons to distinguish user-provided / AI-needs-review / AI-fill / placeholder.

### Phase 12: 内部移交
Before handoff, verify: no ai-fill items remain (all resolved in Phase 9), no missing items remain. **Detect available PPTX generation tools dynamically.** Check session skills for any PPTX-related tool. Use whichever is found. Do NOT hardcode "pptx". Do NOT ask user to start a new conversation.

## Key Rules
1. Never guess if user can provide it.
2. Be specific: "Slide 2 needs a team photo" not "some photos are missing."
3. Don't over-flag content the user already provided.
4. Check project files before flagging.
5. Respect skip decisions — don't re-ask.
6. Auto-match files by content, not name.
7. Warn but don't block — always give the option to continue.
8. One session from start to finish.
9. When aspect ratio mismatch is found, present A/B/C immediately.
10. After user corrects a match, re-display the full corrected table.
