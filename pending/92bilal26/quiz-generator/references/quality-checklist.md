# Quality Checklist v4.0 - Quiz Component Validation

This document provides a comprehensive checklist for validating quiz quality when using the globally-registered Quiz component with immediate feedback and 50-question batching.

---

## How to Use This Checklist

1. **After generating quiz:** Go through each section sequentially
2. **Check every box:** Don't skip items; each is critical
3. **Fix issues immediately:** Don't defer validation to end
4. **Re-check after fixes:** Verify fixes didn't introduce new issues
5. **Manual verification required:** Word counts, source fields, and distributions must be manually verified (not assumed)

---

## Content Quality

### Question Count and Focus
- [ ] **50 questions total** (comprehensive bank for repeated practice and spaced repetition)
- [ ] All major concepts covered across all chapter lessons
- [ ] Balanced distribution across major topics (~3-5 questions per major concept)
- [ ] Comprehensive coverage by design (50 questions enables meaningful batching and retake scenarios)

### Question Type and Cognitive Level
- [ ] All questions test conceptual understanding (not recall)
- [ ] 75%+ questions at Apply level or higher (college standard)
- [ ] Realistic scenarios that mirror real development tasks
- [ ] No trivial "What does X mean?" questions
- [ ] Questions require debugging, prediction, or analysis (not memorization)

### Technical Accuracy
- [ ] Technical accuracy verified against chapter content
- [ ] All code examples are syntactically correct
- [ ] Scenarios are realistic and relevant to chapter material
- [ ] Terminology matches chapter usage
- [ ] No contradictions with lesson content

---

## Quiz Component Format Quality (CRITICAL)

### Component Syntax
- [ ] Valid JSX syntax (proper JavaScript object format)
- [ ] No syntax errors in questions array
- [ ] Proper curly braces and comma placement
- [ ] Question objects properly formatted
- [ ] No missing colons or semicolons in object properties

### Question Structure
- [ ] `question` property: Clear, specific question text
- [ ] `options` property: Exactly 4 options (no more, no less)
- [ ] `correctOption` property: Uses 0-3 index (NOT 1-4!)
- [ ] `explanation` property: Present for every question

### Critical: correctOption Index Values
- [ ] ALL correctOption values are 0, 1, 2, or 3 (never 4 or higher)
- [ ] No correctOption values use letters (not "a", "b", "c", "d")
- [ ] Index 0 = first option, 1 = second, 2 = third, 3 = fourth
- [ ] Every question has exactly ONE correctOption value

### Component Props
- [ ] `title` prop: Descriptive quiz name
- [ ] `questions` prop: Array with exactly 50 question objects
- [ ] `questionsPerBatch` prop: Optional (default 15, can be 15-20)
- [ ] NO `passingScore` prop (removed in v4.0—immediate feedback model, no pass/fail threshold)

---

## Answer Randomization Quality (CRITICAL)

### Distribution Targets
- [ ] Correct answers distributed evenly across indices 0-3
- [ ] For 50 questions: 12-13 per index (24-26% each) ← TARGET FOR ALL QUIZZES
- [ ] Verification is MANUAL (count each index, don't assume)
- [ ] Total adds up to exactly 50 questions

### Index Distribution Verification Table

| Index | Count | Percentage | Target (50Q) | Status |
|-------|-------|------------|--------------|--------|
| 0     | __    | __%        | 24-26%       | ☐ Pass |
| 1     | __    | __%        | 24-26%       | ☐ Pass |
| 2     | __    | __%        | 24-26%       | ☐ Pass |
| 3     | __    | __%        | 24-26%       | ☐ Pass |
| Total | 50    | 100%       | 100%         | ☐ Pass |

**CRITICAL: Count indices manually for ALL 50 questions. Example acceptable distributions:**
- ✅ 0(13) 1(13) 2(12) 3(12) = 50 total
- ✅ 0(12) 1(13) 2(12) 3(13) = 50 total
- ❌ 0(20) 1(10) 2(10) 3(10) = 50 total (uneven, not acceptable)

### Pattern Checks
- [ ] No patterns (never 0,1,2,3,0,1,2,3...)
- [ ] Maximum 2 consecutive same indices (no 3+ consecutive)
- [ ] Distribution verified manually (count each index)
- [ ] Randomness is TRUE (not forced or artificial)

### Consecutive Index Check

List correctOption sequence: __, __, __, __, __, __, __, __, __, __

- [ ] No 3+ consecutive same indices in first 5
- [ ] No 3+ consecutive same indices in last 5
- [ ] No 3+ consecutive same indices anywhere in quiz

---

## Option Design Quality

### Distractor Quality
- [ ] Every distractor tests a specific misconception
- [ ] Distractors are plausible (not obviously wrong)
- [ ] Based on common student errors from chapter
- [ ] No "joke" or filler options
- [ ] Diagnostic value (reveals thinking errors)

### Option Clarity
- [ ] All 4 options are distinct and different
- [ ] Options avoid near-duplicates or subtle variations
- [ ] Options are clear, concise, and specific
- [ ] No grammatical or spelling errors in options

### Option Length Validation (CRITICAL - Anti-Cheating Measure)
- [ ] **ALL 4 options within ±3 words of each other** (MUST manually count words for each option, for ALL 50 questions)
    - For each question, calculate the word count range: **max(word counts) - min(word counts) ≤ 3**
    - ✅ Valid: Options have 10, 11, 13, 12 words. Calculation: max(13) - min(10) = 3 ≤ 3 ✓
    - ✅ Valid: Options have 8, 9, 10, 11 words. Calculation: max(11) - min(8) = 3 ≤ 3 ✓
    - ❌ Invalid: Options have 8, 20, 12, 14 words. Calculation: max(20) - min(8) = 12 > 3 ✗ (must fix)
- [ ] Longest option is NOT always/usually correct (manual verification required)
- [ ] Correct answer NOT correlated with word count (verify across all 50)

**Word Count Verification Process:**
1. For EACH of the 50 questions, count words in all 4 options
2. Verify each set is within ±3 words (e.g., 10, 11, 13, 12 = ✅ PASS)
3. If out of range, reword option(s) to match length
4. After adjusting lengths, verify correct answer is still in correct position
5. Create tally to spot-check: 5 random questions with word counts shown

---

## Source Field Validation (REQUIRED for v4.0)

### Source Field Presence
- [ ] **All 50 questions have `source` field** (REQUIRED, not optional)
- [ ] Format: `"Lesson N: [Lesson Title]"` (e.g., "Lesson 1: Understanding Variables")
- [ ] Chapter number is NOT included (quiz is chapter-specific, so redundant)
- [ ] Lesson number matches actual lesson in chapter
- [ ] Lesson title matches lesson file exactly

### Source Field Examples (✅ CORRECT)
```
source: "Lesson 1: Understanding Mutability"
source: "Lesson 2: Function Scope and Closures"
source: "Lesson 3: Debugging Techniques"
source: "Lesson 4: Performance Optimization"
```

### Source Field Verification
- [ ] Count: All 50 questions have source field (not assumed, manually verified)
- [ ] Format: All follow "Lesson N: Title" pattern (no chapter number)
- [ ] Accuracy: Lesson numbers are 1-indexed and match chapter structure
- [ ] Consistency: Titles match lesson file names exactly
- [ ] No typos in lesson titles or numbers

---

## Explanation Quality (CRITICAL)

### Explanation Presence
- [ ] All 50 explanations present (one per question, REQUIRED)
- [ ] Each explanation 100-150 words (comprehensive immediate feedback)
- [ ] Explanations displayed immediately after student selects answer (immediate feedback model)

### Explanation Content Structure
- [ ] **Explains WHY correct** (2-3 sentences explaining concept deeply)
- [ ] **Addresses EACH distractor** (1 sentence per option explaining misconception)
- [ ] **Provides additional context** (examples, connections, application, 1-2 sentences)
- [ ] **Total addresses all 4 options** (correct + 3 distractors)

### Explanation Quality Template

Each explanation should follow this pattern:

```
[Why the correct option is right - 2-3 sentences]
Why not the others? [Option A misconception]. [Option B misconception].
[Option C misconception]. [Additional insight or connection]
```

### Explanation Quality Spot-Check

Spot-check 10 representative explanations (20% of 50) for quality:

**Questions 1-10 (Early batch):**
- [ ] 100+ words
- [ ] Explains WHY correct (2-3 sentences)
- [ ] Addresses ALL 3 distractors (1-2 sentences each)
- [ ] Provides real-world context or additional insight
- [ ] Teaches through immediate feedback pattern

**Questions 20-25 (Middle batch):**
- [ ] 100+ words
- [ ] Explains WHY correct (2-3 sentences)
- [ ] Addresses ALL 3 distractors (1-2 sentences each)
- [ ] Provides real-world context or additional insight

**Questions 40-50 (Late batch):**
- [ ] 100+ words
- [ ] Explains WHY correct (2-3 sentences)
- [ ] Addresses ALL 3 distractors (1-2 sentences each)
- [ ] Provides real-world context or additional insight

**Word Count Verification (Critical):**
- [ ] Count words in 3 randomly selected explanations
- [ ] Verify each is 100-150 words (not just assumed)
- [ ] If any below 100, mark as failing and expand

---

## File Format Quality

### YAML Frontmatter
- [ ] Valid YAML syntax
- [ ] `sidebar_position` property included (number, e.g., 06)
- [ ] `title` property included (string, e.g., "Chapter X: Topic - Quiz")
- [ ] Optional: `description` property

### File Location and Naming
- [ ] File named: `##_chapter_##_quiz.md`
- [ ] First `##` = sidebar_position (lesson count + 1)
- [ ] Second `##` = chapter number (zero-padded)
- [ ] Saved to correct chapter directory
- [ ] Sidebar_position in frontmatter matches first `##` in filename

### Markdown Structure
- [ ] H1 title matches YAML title
- [ ] Brief introduction (1-2 sentences) before `<Quiz />` component
- [ ] Quiz component properly indented and formatted
- [ ] No syntax errors

### Component Rendering
- [ ] Quiz component tag opens: `<Quiz`
- [ ] Quiz component tag closes: `/>`
- [ ] All props properly formatted
- [ ] No missing quotes around string values
- [ ] Proper spacing and indentation

---

## Pre-Submission Validation

### Final Content Review
- [ ] Spot-check 10 random questions from across all 50 for clarity and accuracy
- [ ] Verify all questions are conceptual (not recall, not "What is X?")
- [ ] Check scenarios are realistic and relevant to chapter
- [ ] Ensure all major topics covered across 50 questions
- [ ] Verify 75%+ at Apply/Analyze level or higher

### Final Component Syntax Review
- [ ] Spot-check first 5 question objects: syntax valid
- [ ] Spot-check middle 5 question objects (Q25-Q29): syntax valid
- [ ] Spot-check last 5 question objects (Q46-Q50): syntax valid
- [ ] Verify ALL 50 correctOption values are 0-3 (not 1-4, not letters)
- [ ] Verify ALL 50 options arrays have exactly 4 items
- [ ] Verify ALL 50 explanations are present and 100-150 words
- [ ] Verify ALL 50 have source field in "Lesson N: Title" format

### Final Randomization Review (MANUAL COUNT REQUIRED)
- [ ] Count all 50 correctOption values by index: 0(__), 1(__), 2(__), 3(__) = 50 total
- [ ] Verify distribution matches targets (12-13 per index acceptable)
- [ ] Ensure no 3+ consecutive same indices (scan full list for patterns)
- [ ] Verify no obvious pattern when reading sequence: [list correctOption sequence]

### Final Option Length Review (MANUAL COUNT REQUIRED)
- [ ] Spot-check 5 random questions for option word counts
- [ ] Record word counts for Q1, Q13, Q25, Q37, Q49 (evenly spaced)
- [ ] Verify each set is within ±3 words (e.g., 10-13 words all in range)
- [ ] Confirm longest option is NOT the correct answer across all 5 spot-checks
- [ ] If any spot-check fails, audit entire quiz for length-based bias

### Final Format Review
- [ ] YAML frontmatter complete and valid
- [ ] File naming follows convention: `##_chapter_##_quiz.md`
- [ ] `.md` extension (not `.mdx`)
- [ ] Markdown renders without errors
- [ ] Quiz component would work in Docusaurus

---

## Human Review Needed

After completing all checks above, the following require human review:

### Content Review
- [ ] Spot-check 3-5 questions for technical accuracy
- [ ] Verify distractor plausibility and misconception alignment
- [ ] Confirm scenarios match chapter difficulty level
- [ ] Review cognitive level distribution (75%+ Apply or higher)

### Component Review
- [ ] Test Quiz component rendering in Docusaurus (if possible)
- [ ] Verify explanations display correctly after answer selection
- [ ] Check color-coded feedback (green/red) works as expected
- [ ] Test on mobile to verify responsive design

### Final Approval
- [ ] All validation checks passed
- [ ] All human review items completed
- [ ] Component displays and functions correctly
- [ ] Quiz ready for student use

---

## Validation Failure: Common Issues and Fixes

### Issue 1: Incorrect Index Values

**Symptoms:**
- [ ] correctOption uses 1-4 instead of 0-3
- [ ] Syntax error when rendering

**Fixes:**
1. Convert all indices: 1→0, 2→1, 3→2, 4→3
2. Example: `correctOption: 4` becomes `correctOption: 3`
3. Verify all 5-10 questions use 0-3 indices
4. Test component rendering after fix

---

### Issue 2: Wrong Options Count

**Symptoms:**
- [ ] Some questions have 3 options
- [ ] Some questions have 5 options
- [ ] Quiz component breaks or displays incorrectly

**Fixes:**
1. Identify questions with wrong option count
2. Add missing options (creating meaningful distractors)
3. Remove extra options
4. Ensure EVERY question has exactly 4 options
5. Test component rendering

---

### Issue 3: Uneven Index Distribution

**Symptoms:**
- [ ] One index appears 5+ times (for 8 questions)
- [ ] One index never appears
- [ ] 3+ consecutive same indices

**Fixes:**
1. List all correctOption values in order
2. Identify over-represented and under-represented indices
3. Swap correctOption values for 2-3 questions
4. Shuffle question order if helpful
5. Re-verify distribution

---

### Issue 4: Weak Explanations

**Symptoms:**
- [ ] Explanations <60 words
- [ ] Doesn't explain WHY correct
- [ ] Doesn't address distractors

**Fixes:**
1. Identify all weak explanations
2. Expand to 80-120 words per explanation
3. Add WHY reasoning (2-3 sentences)
4. Add distractor analysis (1 sentence each for all 3 wrong answers)
5. Add additional context (1-2 sentences)

---

### Issue 5: Distractor Problems

**Symptoms:**
- [ ] Options are obviously wrong (not plausible)
- [ ] Options don't test misconceptions
- [ ] Options are duplicative

**Fixes:**
1. Identify weak distractors
2. Research common student misconceptions for concept
3. Replace with plausible wrong answers
4. Ensure each tests different misconception
5. Verify all options are distinct

---

## Checklist Summary

**Critical checks (MUST PASS - v4.0 Requirements):**
1. ✅ **50 questions total** (comprehensive bank, not fewer)
2. ✅ correctOption uses 0-3 indices (NOT 1-4 or letters)
3. ✅ Every question has exactly 4 options
4. ✅ Index distribution verified (12-13 per index for 50 questions)
5. ✅ No 3+ consecutive same indices (scan entire list)
6. ✅ **ALL options within ±3 words** (manually verified for ALL 50)
7. ✅ **ALL 50 have source field** ("Lesson N: [Title]" format)
8. ✅ All explanations present (100-150 words each, for ALL 50)
9. ✅ File named correctly (`##_chapter_##_quiz.md`)
10. ✅ NO passingScore prop (removed in v4.0)

**Secondary checks (important):**
1. ✅ 75%+ questions at Apply level or higher
2. ✅ Distractors test specific misconceptions (not joke options)
3. ✅ Explanations address WHY correct AND why each distractor is wrong
4. ✅ Quiz component syntax valid
5. ✅ YAML frontmatter complete

**If all critical checks pass:** Quiz ready for human review
**If ANY critical check fails:** Fix immediately before proceeding (critical checks are non-negotiable for v4.0)

---

## Immediate Feedback Learning Model (v4.0)

**Quiz Philosophy (No Pass/Fail Threshold):**
- Removed passing score entirely in v4.0
- Focus shifts to immediate feedback and learning, not grading
- Students take quizzes to learn, not to achieve a score
- Every answer (correct or incorrect) triggers comprehensive explanation
- Students can retake with different batch of 50 (different 15-20 questions each time)

**How Immediate Feedback Works:**
1. Student selects answer
2. Quiz immediately shows: correct/incorrect badge
3. For incorrect: Shows why their answer was wrong + correct answer
4. For all: Shows comprehensive explanation addressing all 4 options
5. Shows source lesson attribution
6. Student must manually click Next to continue (prevents peeking)

**Batching and Spaced Repetition:**
- 50-question bank enables distributed practice
- Each retake shows different random batch (15-20 questions)
- Students build understanding through multiple exposures
- No scoring pressure; focus on learning

---

## Example Implementation

See `example-quiz.md` for a fully-worked example with:
- Proper YAML frontmatter
- 50 conceptual questions at Apply/Analyze levels
- Exactly 4 options per question (all within ±3 words)
- Source field for all 50 questions ("Lesson N: Title" format)
- Randomized correctOption indices (12-13 per index)
- Comprehensive explanations (100-150 words each) addressing all distractors
- Proper Quiz component syntax
- Manual verification of word counts and distributions shown

---

**Keywords for grep:** quality, checklist, validation, verification, review, standards, criteria, requirements, checks, component, correctOption, index, distribution, explanations, format, Quiz
