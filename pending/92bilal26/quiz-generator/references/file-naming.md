# File Naming Convention - Quiz Files

This document details the proper file naming pattern for quiz files to ensure consistency with lesson naming conventions.

---

## Naming Pattern

```
##_chapter_##_quiz.md
```

Where:
- **First `##`** = sidebar_position (quiz position number, after all lessons)
- **Second `##`** = chapter number (zero-padded: 01, 02, 05, 14, 32, etc.)

---

## Why This Naming?

### Consistency with Lesson Naming
Lessons follow similar patterns:
- `01_lesson_01.md` or `01_chapter_02_lesson_01.md`
- `02_lesson_02.md` or `02_chapter_02_lesson_02.md`

Quizzes should match this convention:
- `05_chapter_02_quiz.md` (quiz for Chapter 2, after 4 lessons)

### Clear Chapter Identification
The second `##` clearly identifies which chapter the quiz belongs to:
- `05_chapter_02_quiz.md` → Chapter 2 quiz
- `07_chapter_05_quiz.md` → Chapter 5 quiz
- `06_chapter_14_quiz.md` → Chapter 14 quiz

### Natural Sorting
Files sort alphabetically, placing quiz at chapter end:
```
01_lesson_01.md
02_lesson_02.md
03_lesson_03.md
04_lesson_04.md
05_chapter_02_quiz.md ← Quiz appears last
```

---

## How to Determine the First `##` (sidebar_position)

### Step 1: Count Lessons in Chapter

List all lesson files in the chapter directory:
```
apps/learn-app/docs/part-1-foundations/chapter-02-ai-turning-point/
  01_lesson_01.md
  02_lesson_02.md
  03_lesson_03.md
  04_lesson_04.md
```

**Lesson count:** 4 lessons (01 through 04)

### Step 2: Quiz Position = Lesson Count + 1

Since quiz should appear AFTER all lessons:
```
Quiz sidebar_position = 4 + 1 = 5
```

### Step 3: Apply Pattern

```
05_chapter_02_quiz.md
```

Where:
- `05` = sidebar_position (after 4 lessons)
- `chapter_02` = Chapter 2
- `quiz` = file type identifier

---

## Examples by Chapter

### Chapter 2 (4 Lessons)

**Lessons:**
```
01_lesson_01.md
02_lesson_02.md
03_lesson_03.md
04_lesson_04.md
```

**Quiz filename:**
```
05_chapter_02_quiz.md
```

**Explanation:**
- 4 lessons → quiz is position 5
- Chapter 2 → `chapter_02`
- Result: `05_chapter_02_quiz.md`

---

### Chapter 5 (6 Lessons)

**Lessons:**
```
01_lesson_01.md
02_lesson_02.md
03_lesson_03.md
04_lesson_04.md
05_lesson_05.md
06_lesson_06.md
```

**Quiz filename:**
```
07_chapter_05_quiz.md
```

**Explanation:**
- 6 lessons → quiz is position 7
- Chapter 5 → `chapter_05`
- Result: `07_chapter_05_quiz.md`

---

### Chapter 14 (5 Lessons)

**Lessons:**
```
01_lesson_01.md
02_lesson_02.md
03_lesson_03.md
04_lesson_04.md
05_lesson_05.md
```

**Quiz filename:**
```
06_chapter_14_quiz.md
```

**Explanation:**
- 5 lessons → quiz is position 6
- Chapter 14 → `chapter_14`
- Result: `06_chapter_14_quiz.md`

---

### Chapter 32 (7 Lessons)

**Lessons:**
```
01_lesson_01.md
02_lesson_02.md
03_lesson_03.md
04_lesson_04.md
05_lesson_05.md
06_lesson_06.md
07_lesson_07.md
```

**Quiz filename:**
```
08_chapter_32_quiz.md
```

**Explanation:**
- 7 lessons → quiz is position 8
- Chapter 32 → `chapter_32`
- Result: `08_chapter_32_quiz.md`

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Missing Chapter Number
```
05_quiz.md
```
**Problem:** Doesn't identify which chapter; breaks naming convention

**Fix:**
```
05_chapter_02_quiz.md
```

---

### ❌ Mistake 2: Using Only Chapter Number
```
02_quiz.md
```
**Problem:** First `##` should be sidebar_position, not chapter number

**Fix:**
```
05_chapter_02_quiz.md (if 4 lessons)
```

---

### ❌ Mistake 3: Wrong Sidebar Position
```
04_chapter_02_quiz.md (but chapter has 4 lessons 01-04)
```
**Problem:** Quiz would appear at same position as last lesson; sorting conflict

**Fix:**
```
05_chapter_02_quiz.md (after lesson 04)
```

---

### ❌ Mistake 4: Not Zero-Padded
```
5_chapter_2_quiz.md
```
**Problem:** Inconsistent with lesson naming; sorting issues

**Fix:**
```
05_chapter_02_quiz.md (zero-padded)
```

---

### ❌ Mistake 5: Using Different Separator
```
05-chapter-02-quiz.md (hyphens instead of underscores)
```
**Problem:** Inconsistent with lesson naming convention

**Fix:**
```
05_chapter_02_quiz.md (underscores)
```

---

## File Location (Where to Save)

### Directory Structure

```
apps/learn-app/docs/
└── [part-folder]/
    └── [chapter-folder]/
        ├── 01_lesson_01.md
        ├── 02_lesson_02.md
        ├── 03_lesson_03.md
        ├── 04_lesson_04.md
        └── 05_chapter_02_quiz.md ← Quiz file here
```

### Example Paths

**Chapter 2:**
```
apps/learn-app/docs/part-1-foundations/chapter-02-ai-turning-point/05_chapter_02_quiz.md
```

**Chapter 5:**
```
apps/learn-app/docs/part-2-workflows/chapter-05-claude-features/07_chapter_05_quiz.md
```

**Chapter 14:**
```
apps/learn-app/docs/part-3-advanced/chapter-14-debugging/06_chapter_14_quiz.md
```

---

## Sidebar Position in YAML Frontmatter

The quiz file should also set `sidebar_position` in YAML frontmatter to match filename:

```yaml
---
title: "Chapter 2: AI Turning Point Quiz"
description: "College-level assessment covering all material from Chapter 2"
sidebar_position: 5
---
```

**Rule:** `sidebar_position` in frontmatter must match first `##` in filename.

### Examples

**File:** `05_chapter_02_quiz.md`
**Frontmatter:** `sidebar_position: 5` ✅

**File:** `07_chapter_05_quiz.md`
**Frontmatter:** `sidebar_position: 7` ✅

**File:** `05_chapter_02_quiz.md`
**Frontmatter:** `sidebar_position: 2` ❌ (mismatch)

---

## Quick Reference Table

| Chapter | Lesson Count | Quiz Position | Quiz Filename |
|---------|--------------|---------------|---------------|
| 02      | 4 lessons    | 5             | `05_chapter_02_quiz.md` |
| 05      | 6 lessons    | 7             | `07_chapter_05_quiz.md` |
| 08      | 5 lessons    | 6             | `06_chapter_08_quiz.md` |
| 14      | 5 lessons    | 6             | `06_chapter_14_quiz.md` |
| 21      | 8 lessons    | 9             | `09_chapter_21_quiz.md` |
| 32      | 7 lessons    | 8             | `08_chapter_32_quiz.md` |

---

## Validation Checklist

Before finalizing quiz file:

**Naming Checks:**
- [ ] File follows pattern: `##_chapter_##_quiz.md`
- [ ] First `##` = sidebar_position (lesson count + 1)
- [ ] Second `##` = chapter number (zero-padded)
- [ ] Uses underscores (not hyphens or spaces)
- [ ] Numbers are zero-padded (01, 02, 05, not 1, 2, 5)

**Location Checks:**
- [ ] File saved in correct chapter directory
- [ ] File appears AFTER all lesson files alphabetically
- [ ] Path is: `apps/learn-app/docs/[part]/[chapter]/##_chapter_##_quiz.md`

**Frontmatter Checks:**
- [ ] YAML frontmatter includes `sidebar_position`
- [ ] `sidebar_position` value matches first `##` in filename
- [ ] Title clearly identifies chapter and quiz
- [ ] Description mentions chapter and assessment type

---

## Migration from Old Naming (v1.0)

If you have existing quizzes with old naming pattern:

### Old Pattern (v1.0)
```
02_quiz.md
```

### New Pattern (v2.0)
```
05_chapter_02_quiz.md (assuming 4 lessons)
```

### Migration Steps

1. **Identify chapter number:** 02
2. **Count lessons:** 4 lessons (01-04)
3. **Calculate sidebar_position:** 4 + 1 = 5
4. **Construct new filename:** `05_chapter_02_quiz.md`
5. **Rename file:** `02_quiz.md` → `05_chapter_02_quiz.md`
6. **Update frontmatter:** Set `sidebar_position: 5`
7. **Verify sorting:** Quiz should appear after all lessons in directory

---

**Keywords for grep:** file-naming, naming-convention, sidebar-position, quiz-filename, chapter-number, pattern, examples, validation, migration, ##_chapter_##_quiz
