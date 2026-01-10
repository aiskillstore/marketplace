# Bias Detection Checklist - Answer Distribution Verification (v4.0)

**PURPOSE:** Catch answer bias BEFORE submission. This checklist detects when correct answers are not evenly distributed across indices 0-3, which allows students to exploit patterns.

**WHEN TO USE:** After generating all 50 questions, BEFORE creating the Quiz component file. Use this to verify the distribution is acceptable.

---

## The Problem: Why Bias Detection Matters

### Real-World Example (The Bias You're Fixing)

**Observed Problem:**
- Quiz shows 18 questions to user
- 15 questions have correct answer as option B (index 1)
- 3 questions have correct answers as A, C, or D

**Result:**
```
Student Strategy: "Always pick B"
Student Score: 15/18 = 83%

But student only understood ~20% of material!
The quiz failed to assess understanding.
```

### Why This Happens

When the person generating the quiz doesn't randomize answer positions:
- They naturally tend to place correct answers in the same position
- Over 50 questions, this becomes statistically obvious
- Even if someone tries to randomize mentally, bias creeps in

**SOLUTION:** Systematic verification before submission catches this 100% of the time.

---

## Quick Verification (2 minutes)

**Step 1: List All 50 Correct Indices**

Write out or list the `correctOption` value for each of the 50 questions:

```
Q1: 2
Q2: 0
Q3: 3
Q4: 1
Q5: 0
Q6: 2
...
Q50: 1
```

**Step 2: Count Each Index**

Tally how many times each appears:

```
Index 0 (Option A): ||||||||||||| = 13 times
Index 1 (Option B): |||||||||||| = 12 times
Index 2 (Option C): ||||||||||||| = 13 times
Index 3 (Option D): ||||||||| = 12 times
Total: 50 ✓
```

**Step 3: Check Against Acceptance Criteria**

```
Index 0: 13 times → Within 12-13 range ✓
Index 1: 12 times → Within 12-13 range ✓
Index 2: 13 times → Within 12-13 range ✓
Index 3: 12 times → Within 12-13 range ✓

All within acceptable range? → YES ✓
```

**If ALL indices are 12-13:** PASS → Proceed to full checklist
**If ANY index is outside 12-13:** FAIL → Fix before submission

---

## Full Verification Checklist

### Section 1: Distribution Check (MANDATORY GATE)

Use this checklist to verify correct answers are evenly distributed:

**1.1 Count All Indices**

- [ ] **Manually count** how many times each index (0, 1, 2, 3) appears as correctOption
- [ ] **Record counts:**
  ```
  Index 0: ___ times
  Index 1: ___ times
  Index 2: ___ times
  Index 3: ___ times
  Total: ___ (must equal 50)
  ```

**1.2 Verify Equal Distribution**

- [ ] **All counts are 11-14?** (ideal: 12-13)
  - ✅ PASS: All between 12-13
  - ⚠️ BORDERLINE: One or more between 11-14 (acceptable if no index < 11 or > 14)
  - ❌ FAIL: Any index < 11 or > 14
- [ ] **No index dominates** (not one index appearing 20+ times)
- [ ] **No index is missing** (all 4 indices appear at least once)

**1.3 Calculate Percentages (Optional, for documentation)**

```
Index 0: ___ ÷ 50 = ___% (target: 25% = 12.5)
Index 1: ___ ÷ 50 = ___% (target: 25% = 12.5)
Index 2: ___ ÷ 50 = ___% (target: 25% = 12.5)
Index 3: ___ ÷ 50 = ___% (target: 25% = 12.5)
```

**GATE DECISION:**
- [ ] **ALL indices between 12-13?** → ✅ PASS (proceed to Section 2)
- [ ] **ALL indices between 11-14 with no extreme outliers?** → ✅ BORDERLINE PASS (document and proceed)
- [ ] **ANY index outside 11-14?** → ❌ FAIL (fix distribution before submitting)

---

### Section 2: Pattern Detection

If Section 1 passes, verify there are no obvious patterns that could be exploited:

**2.1 Consecutive Same Indices Check**

Write out the sequence of all 50 correctOption indices:
```
2, 0, 3, 1, 0, 2, 1, 3, 2, 0, 1, 3, 2, 1, 0, 3, 2, 0, 1, 3, ...
```

- [ ] **Scan the sequence visually** for runs of same number
- [ ] **Count longest consecutive run** of same index:
  - ✅ PASS: Maximum of 2 consecutive same (e.g., "1, 1" is OK)
  - ❌ FAIL: 3+ consecutive same (e.g., "1, 1, 1" = REJECT)

**2.2 Obvious Repeating Pattern Check**

- [ ] **Does sequence repeat in blocks?**
  - ❌ BAD: `0,1,2,3,0,1,2,3,0,1,2,3` (alphabetical cycling)
  - ✅ GOOD: `2,0,3,1,0,2,1,3,2,0,1,3,...` (appears random)

- [ ] **Does it look "chunked" by topic?**
  - ❌ BAD: Questions 1-20 are mostly 0-1, Questions 21-50 are mostly 2-3
  - ✅ GOOD: Mixed throughout (Lesson 1 has 0,2,1,3; Lesson 2 has 2,0,3,1)

**2.3 Visual Randomness**

- [ ] When you look at the sequence, does it appear random (not following a formula)?
- [ ] Could a student predict the next answer by looking at patterns?
  - ✅ PASS: No, appears unpredictable
  - ❌ FAIL: Yes, they could guess the pattern

**GATE DECISION:**
- [ ] **No runs of 3+ same? No obvious repeating pattern?** → ✅ PASS
- [ ] **Found 3+ consecutive? Or found repeating pattern?** → ❌ FAIL (fix before submitting)

---

### Section 3: Topic Clustering (Bonus Check)

Advanced check: Verify correct answers aren't clustered by topic:

**3.1 Check Each Lesson/Topic**

For each lesson in the chapter:
```
Lesson 1 questions (Q1-8): indices = 2,0,3,1,0,2,1,3
  Contains: 0(2), 1(2), 2(2), 3(2) → Balanced ✓

Lesson 2 questions (Q9-16): indices = 2,0,3,1,0,2,1,3
  Contains: 0(2), 1(2), 2(2), 3(2) → Balanced ✓
```

- [ ] **Each lesson has mixed indices?** (not all same)
  - ✅ PASS: Every lesson has all 4 indices represented
  - ⚠️ BORDERLINE: Some lessons have 3 out of 4 indices
  - ❌ FAIL: Any lesson has only 1-2 indices (e.g., all questions in Lesson 3 have correct answer B)

---

## Failure Examples (What to Watch For)

### ❌ FAIL Example 1: Heavy Bias Toward One Index

```
Count by index:
Index 0: 5 times
Index 1: 30 times ← EXTREME BIAS
Index 2: 10 times
Index 3: 5 times

Problem: Student can achieve 60% accuracy by always selecting B
Status: REJECT - Fix required
```

### ❌ FAIL Example 2: Alphabetical Pattern

```
Sequence: 0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,...

Problem: Obvious repeating pattern; students will notice after Q8
Status: REJECT - Randomize before submitting
```

### ❌ FAIL Example 3: Topic Clustering

```
Lesson 1 (Q1-8): All indices 0,1,2,3,0,1,2,3
  Students learn: "Lesson 1 answers are evenly spread"
Lesson 2 (Q9-16): All indices 1,1,1,1,1,1,1,1
  Students learn: "Lesson 2 = always pick B"
Lesson 3 (Q17-25): All indices 2,2,2,2,2,2,2,2,2
  Students learn: "Lesson 3 = always pick C"

Problem: Student can identify lessons and guess by pattern
Status: REJECT - Randomize with zero topic correlation
```

### ✅ PASS Example 1: Even Distribution

```
Count by index:
Index 0: 13 times (26%)
Index 1: 12 times (24%)
Index 2: 13 times (26%)
Index 3: 12 times (24%)
Total: 50

Sequence: 2,0,3,1,0,2,1,3,2,0,1,3,2,1,0,3,2,0,1,3,0,3,1,2,0,1,3,2,0,1,2,3,0,1,2,0,3,1,2,0,1,3,2,0,1,2,3,0,1,3

Status: PASS ✓
```

### ✅ PASS Example 2: Random Appearing

```
Longest consecutive run: 2 (found "1,1" twice, max)
No 3+ consecutive same indices anywhere
Sequence doesn't repeat (no a,b,c,d,a,b,c,d pattern)
All lessons have mixed indices

Status: PASS ✓
```

---

## Decision Tree

```
START: Do you have 50 questions with correctOption indices assigned?
│
├─ NO → Go write your questions first, then return here
│
└─ YES → Continue to distribution check
   │
   ├─ STEP 1: Count indices (Section 1.1)
   │  └─ All between 12-13?
   │     ├─ YES → Continue to pattern check
   │     └─ NO → STOP. Bias detected. Fix before submitting.
   │
   ├─ STEP 2: Pattern check (Section 2)
   │  └─ Any 3+ consecutive same? Any repeating pattern?
   │     ├─ NO → Continue to topic check (optional)
   │     └─ YES → STOP. Pattern detected. Randomize before submitting.
   │
   ├─ STEP 3: Topic check (Section 3, optional)
   │  └─ Are indices mixed across lessons?
   │     ├─ YES → ✅ PASS - Ready for submission
   │     └─ NO → Consider randomizing further (nice-to-have)
   │
   └─ ✅ FINAL: Distribution verified, no bias detected → Proceed to Quiz component creation
```

---

## Pre-Submission Checklist Template

Copy and fill this out before submitting your quiz:

```
QUIZ BIAS DETECTION VERIFICATION

Chapter: ___________________
Quiz File: ___________________
Date Verified: ___________________

SECTION 1: DISTRIBUTION
- [ ] Index 0 count: ___ (target: 12-13)
- [ ] Index 1 count: ___ (target: 12-13)
- [ ] Index 2 count: ___ (target: 12-13)
- [ ] Index 3 count: ___ (target: 12-13)
- [ ] Total: ___ (must be 50)
- [ ] All indices within 12-13? YES / NO / BORDERLINE

SECTION 2: PATTERNS
- [ ] Longest consecutive same index: ___ (max allowed: 2)
- [ ] Found obvious repeating pattern? YES / NO
- [ ] Found alphabetical cycling? YES / NO
- [ ] Sequence appears random? YES / NO

SECTION 3: TOPICS (Optional)
- [ ] Each lesson has all 4 indices? YES / NO / MOSTLY
- [ ] Any lesson clustered to one index? YES / NO

RESULT:
[ ] PASS - No bias detected. Ready for submission.
[ ] BORDERLINE - Some variance; document and proceed.
[ ] FAIL - Bias detected. DO NOT SUBMIT. Fix distribution.

Notes:
_____________________________________________________________________
_____________________________________________________________________
```

---

## When to Reject (BLOCKING CRITERIA)

❌ **REJECT quiz if ANY of these are true:**

1. **Index appears >14 times** (too biased toward one option)
2. **Index appears <11 times** (too biased away from one option)
3. **3+ consecutive same indices** (pattern too obvious)
4. **Alphabetical cycling detected** (0,1,2,3,0,1,2,3...)
5. **Single lesson has only 1-2 indices** (topic clustering)
6. **Student could predict next answer by pattern** (obviously not random)

**If ANY of these are true: DO NOT SUBMIT. Fix the distribution first.**

---

## How to Fix Distribution Issues

If your distribution fails, here's how to fix it:

### Issue 1: One Index Has Too Many Occurrences

**Problem:** Index 1 appears 22 times (should be ~12-13)

**Fix:**
1. Find all questions where correctOption: 1
2. Select 9 of them randomly
3. For each selected question, change correctOption to 0, 2, or 3
4. Rearrange the options to match the new correctOption index
5. Re-count all indices to verify new distribution

### Issue 2: Found 4 Consecutive Same Indices

**Problem:** Questions 15-18 all have correctOption: 2 (4 consecutive)

**Fix:**
1. Swap the correctOption value of Q17 with Q25
2. Rearrange options in both questions accordingly
3. Re-verify no 3+ consecutive patterns remain

### Issue 3: Alphabetical Pattern Detected

**Problem:** Sequence is: 0,1,2,3,0,1,2,3,0,1,2,3...

**Fix:**
1. Use a random number generator to shuffle the entire sequence
2. Reassign indices to questions using the shuffled sequence
3. Rearrange all question options to match new assignments
4. Re-verify distribution and patterns

---

**This checklist catches 100% of bias issues if used correctly. Use it EVERY TIME before submitting a quiz.**
