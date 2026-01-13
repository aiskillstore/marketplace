# {PROJECT_TITLE} - Task List

> **Detailed Plan**: [plan.md](plan.md)
> **Last Updated**: {DATE}

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Sections | {TOTAL_SECTIONS} |
| Completed | {COMPLETED_COUNT} |
| Remaining | {REMAINING_COUNT} |
| Progress | {PROGRESS_PERCENT}% |
| Estimated Pages | {TOTAL_PAGES} |

---

## Part 1: {PART_1_TITLE} ({PART_1_PAGES}p)

<!-- Session 1: {SESSION_1_DESCRIPTION} -->

### Chapter 1: {CHAPTER_1_TITLE}

- [ ] 1.1 {SECTION_1_1_TITLE} ({SECTION_1_1_PAGES}p) → [plan.md#section-11](plan.md#11-{SECTION_1_1_SLUG})
- [ ] 1.2 {SECTION_1_2_TITLE} ({SECTION_1_2_PAGES}p) → [plan.md#section-12](plan.md#12-{SECTION_1_2_SLUG})
- [ ] 1.3 {SECTION_1_3_TITLE} ({SECTION_1_3_PAGES}p) → [plan.md#section-13](plan.md#13-{SECTION_1_3_SLUG})

### Chapter 2: {CHAPTER_2_TITLE}

- [ ] 2.1 {SECTION_2_1_TITLE} ({SECTION_2_1_PAGES}p) → [plan.md#section-21](plan.md#21-{SECTION_2_1_SLUG})
- [ ] 2.2 {SECTION_2_2_TITLE} ({SECTION_2_2_PAGES}p) → [plan.md#section-22](plan.md#22-{SECTION_2_2_SLUG})

<!-- Session 2: {SESSION_2_DESCRIPTION} -->

### Chapter 3: {CHAPTER_3_TITLE}

- [ ] 3.1 {SECTION_3_1_TITLE} ({SECTION_3_1_PAGES}p) → [plan.md#section-31](plan.md#31-{SECTION_3_1_SLUG})
- [ ] 3.2 {SECTION_3_2_TITLE} ({SECTION_3_2_PAGES}p) → [plan.md#section-32](plan.md#32-{SECTION_3_2_SLUG})
- [ ] 3.3 {SECTION_3_3_TITLE} ({SECTION_3_3_PAGES}p) → [plan.md#section-33](plan.md#33-{SECTION_3_3_SLUG})

---

## Part 2: {PART_2_TITLE} ({PART_2_PAGES}p)

<!-- Session 3: {SESSION_3_DESCRIPTION} -->

### Chapter 4: {CHAPTER_4_TITLE}

- [ ] 4.1 {SECTION_4_1_TITLE} ({SECTION_4_1_PAGES}p) → [plan.md#section-41](plan.md#41-{SECTION_4_1_SLUG})
- [ ] 4.2 {SECTION_4_2_TITLE} ({SECTION_4_2_PAGES}p) → [plan.md#section-42](plan.md#42-{SECTION_4_2_SLUG})

### Chapter 5: {CHAPTER_5_TITLE}

- [ ] 5.1 {SECTION_5_1_TITLE} ({SECTION_5_1_PAGES}p) → [plan.md#section-51](plan.md#51-{SECTION_5_1_SLUG})
- [ ] 5.2 {SECTION_5_2_TITLE} ({SECTION_5_2_PAGES}p) → [plan.md#section-52](plan.md#52-{SECTION_5_2_SLUG})

<!-- Session 4: {SESSION_4_DESCRIPTION} -->

### Chapter 6: {CHAPTER_6_TITLE}

- [ ] 6.1 {SECTION_6_1_TITLE} ({SECTION_6_1_PAGES}p) → [plan.md#section-61](plan.md#61-{SECTION_6_1_SLUG})
- [ ] 6.2 {SECTION_6_2_TITLE} ({SECTION_6_2_PAGES}p) → [plan.md#section-62](plan.md#62-{SECTION_6_2_SLUG})
- [ ] 6.3 {SECTION_6_3_TITLE} ({SECTION_6_3_PAGES}p) → [plan.md#section-63](plan.md#63-{SECTION_6_3_SLUG})

---

## Part 3: {PART_3_TITLE} ({PART_3_PAGES}p)

<!-- Session 5: {SESSION_5_DESCRIPTION} -->

### Chapter 7: {CHAPTER_7_TITLE}

- [ ] 7.1 {SECTION_7_1_TITLE} ({SECTION_7_1_PAGES}p) → [plan.md#section-71](plan.md#71-{SECTION_7_1_SLUG})
- [ ] 7.2 {SECTION_7_2_TITLE} ({SECTION_7_2_PAGES}p) → [plan.md#section-72](plan.md#72-{SECTION_7_2_SLUG})

---

## Progress Summary

| Part | Complete | Total | Progress |
|------|----------|-------|----------|
| Part 1 | 0 | {PART_1_SECTIONS} | 0% |
| Part 2 | 0 | {PART_2_SECTIONS} | 0% |
| Part 3 | 0 | {PART_3_SECTIONS} | 0% |
| **Total** | **0** | **{TOTAL_SECTIONS}** | **0%** |

---

## Session Guide

| Session | Sections | Pages | Focus |
|---------|----------|-------|-------|
| Session 1 | {SESSION_1_SECTIONS} | {SESSION_1_PAGES}p | {SESSION_1_DESCRIPTION} |
| Session 2 | {SESSION_2_SECTIONS} | {SESSION_2_PAGES}p | {SESSION_2_DESCRIPTION} |
| Session 3 | {SESSION_3_SECTIONS} | {SESSION_3_PAGES}p | {SESSION_3_DESCRIPTION} |
| Session 4 | {SESSION_4_SECTIONS} | {SESSION_4_PAGES}p | {SESSION_4_DESCRIPTION} |
| Session 5 | {SESSION_5_SECTIONS} | {SESSION_5_PAGES}p | {SESSION_5_DESCRIPTION} |

---

## Notes

### Completion Criteria

Mark a section as complete `[x]` when:
1. Document file exists in `docs/` directory
2. Frontmatter is valid and complete
3. Page count is within 20% of target

### Session Boundaries

Session boundaries are marked with HTML comments:
```markdown
<!-- Session N: Description -->
```

Each session should:
- Cover 3-5 sections
- Target 20-40 pages
- Complete within one Claude Code context window
- Group related sections from the same Part/Chapter
