# Word Precision Audit: Deep Research Skill

**Date:** 2025-11-04
**Purpose:** Systematic review of every word in SKILL.md for precision, intention, and clarity

---

## Audit Methodology

**Criteria for precision:**
1. **No hedge words** ("reasonably", "generally", "basically", "essentially")
2. **No weak verbs** ("can", "may", "might", "should" → use "must", "will", "do")
3. **No vague adjectives** ("good", "nice", "reasonable" → use specific criteria)
4. **No passive voice** where active is stronger
5. **No colloquialisms** in formal directives
6. **No double negatives** ("no need to" → "proceed without")
7. **No redundancy** (say once, clearly)
8. **No ambiguous pronouns** without clear referents

---

## Issues Found (14 total)

### HIGH PRIORITY (8 issues)

#### Issue #1: "reasonable assumptions" (Lines 54, 58)
**Current:**
```markdown
Proceed with reasonable assumptions.
Make reasonable assumptions based on query context.
```

**Problem:** "reasonable" is subjective, vague, creates uncertainty about what's acceptable

**Fix:**
```markdown
Infer assumptions from query context.
Derive assumptions from query signals.
```

**Intention carried:** "reasonable" → permission-seeking, cautious | "infer/derive" → direct action, confident

---

#### Issue #2: "genuinely incomprehensible" (Line 61)
**Current:**
```markdown
Query is genuinely incomprehensible
```

**Problem:** "genuinely" is hedge word, weakens the criterion

**Fix:**
```markdown
Query is incomprehensible
```

**Intention carried:** "genuinely" → doubting, qualifying | removed → clear, definitive

---

#### Issue #3: "User can redirect if needed" (Line 64)
**Current:**
```markdown
PROCEED with standard mode. User can redirect if needed.
```

**Problem:** "can" is weak permission, "if needed" is uncertain, both undermine autonomy

**Fix:**
```markdown
PROCEED with standard mode. User will redirect if incorrect.
```

**Intention carried:** "can...if needed" → uncertain, permission-seeking | "will...if incorrect" → confident, definitive

---

#### Issue #4: "NO need to wait" - double negative (Line 85)
**Current:**
```markdown
NO need to wait for approval - proceed directly to execution
```

**Problem:** Double negative ("NO need") is weaker than direct command, "proceed directly to execution" is wordy

**Fix:**
```markdown
Proceed without waiting for approval
```

**Intention carried:** "NO need to" → permissive, passive | "Proceed without" → imperative, active

---

#### Issue #5: Contraction "Don't" (Line 113)
**Current:**
```markdown
Don't inline everything - use references
```

**Problem:** Contraction in formal directive, less authoritative

**Fix:**
```markdown
Do not inline everything - reference external files
```

**Intention carried:** "Don't" → casual | "Do not" → formal, authoritative

---

#### Issue #6: "ask to proceed" - weak request (Line 229)
**Current:**
```markdown
<5 sources after exhaustive search → Report limitation, ask to proceed
```

**Problem:** "ask to proceed" is weak, implies uncertainty about whether to continue

**Fix:**
```markdown
<5 sources after exhaustive search → Report limitation, request direction
```

**Intention carried:** "ask to proceed" → tentative | "request direction" → professional, clear need

---

#### Issue #7: "When uncertain" contradicts autonomy (Line 262)
**Current:**
```markdown
**When uncertain:** Be thorough, not fast. Quality > speed.
```

**Problem:** "When uncertain" directly contradicts autonomy principle (line 54 says operate independently), creates confusion about when to be uncertain

**Fix:**
```markdown
**Priority:** Thoroughness over speed. Quality > speed.
```

**Intention carried:** "When uncertain" → hesitation, doubt | "Priority" → clear directive, no uncertainty

---

#### Issue #8: "acceptable" is passive (Line 280)
**Current:**
```markdown
Extended reasoning acceptable (5-45 min)
```

**Problem:** "acceptable" is passive, permission-seeking, weak

**Fix:**
```markdown
Time investment: 5-45 minutes
```

**Intention carried:** "acceptable" → asking permission | "investment" → stating fact

---

### MEDIUM PRIORITY (6 issues)

#### Issue #9: "Good autonomous assumptions" - vague judgment (Line 66)
**Current:**
```markdown
**Good autonomous assumptions:**
```

**Problem:** "Good" is vague value judgment without criteria

**Fix:**
```markdown
**Default assumptions:**
```

**Intention carried:** "Good" → subjective approval-seeking | "Default" → objective, standard procedure

---

#### Issue #10: "Standard+" unclear notation (Lines 96, 101)
**Current:**
```markdown
**Standard+ adds:**
**Deep+ adds:**
```

**Problem:** "+" notation is programming jargon, unclear if it means "and above" or "additional to"

**Fix:**
```markdown
**Standard/Deep/UltraDeep execute:**
**Deep/UltraDeep execute:**
```

**Intention carried:** "+" → ambiguous scope | explicit listing → clear scope

---

#### Issue #11: "(optional)" weakens directive (Line 174)
**Current:**
```markdown
4. Next steps (optional)
```

**Problem:** "(optional)" signals uncertainty, weakens the delivery item

**Fix:**
```markdown
4. Next steps (if relevant)
```
OR remove entirely since it's in "Deliver to user" section

**Intention carried:** "(optional)" → uncertain, dismissible | "(if relevant)" → conditional, purposeful | removed → expected

---

#### Issue #12: "Offer:" implies asking permission (Lines 176-179)
**Current:**
```markdown
**Offer:**
- Deep-dive any section
- Follow-up questions
- Alternative formats
```

**Problem:** "Offer" implies asking permission, waiting for response, breaks autonomous flow

**Fix:**
```markdown
**Available on request:**
- Section deep-dives
- Follow-up analysis
- Alternative formats
```
OR remove entirely (user will ask if interested)

**Intention carried:** "Offer" → salesperson, permission-seeking | "Available on request" → service menu, user-initiated | removed → autonomous

---

#### Issue #13: "hit" colloquial (Line 234)
**Current:**
```markdown
Time constraint hit → Package partial results, document gaps
```

**Problem:** "hit" is colloquial, imprecise for technical directive

**Fix:**
```markdown
Time constraint reached → Package partial results, document gaps
```

**Intention carried:** "hit" → casual, imprecise | "reached" → formal, precise

---

#### Issue #14: "explicitly needed" redundant (Line 324)
**Current:**
```markdown
Load these files only when explicitly needed for current phase.
```

**Problem:** "explicitly needed" is redundant - either needed or not, "explicitly" adds no precision

**Fix:**
```markdown
Load files on-demand for current phase only.
```

**Intention carried:** "explicitly needed" → overthinking, redundant | "on-demand" → clear technical term

---

## Impact Analysis

### Before Fixes (Current State)

**Hedge words count:** 4 ("reasonable" ×2, "genuinely", "acceptable")
**Weak modal verbs:** 2 ("can redirect", "may")
**Passive constructions:** 3 ("can", "acceptable", "optional")
**Vague adjectives:** 2 ("good", "reasonable")
**Colloquialisms:** 1 ("hit")
**Redundancies:** 2 ("explicitly needed", "NO need to")

**Total weakness indicators:** 14

### After Fixes (Proposed State)

**Hedge words count:** 0
**Weak modal verbs:** 0
**Passive constructions:** 0
**Vague adjectives:** 0
**Colloquialisms:** 0
**Redundancies:** 0

**Total weakness indicators:** 0

---

## Word Intention Analysis

### Critical Word Replacements

| Current Word | Unintended Intention | Replacement | Intended Intention |
|--------------|---------------------|-------------|-------------------|
| reasonable | subjective, cautious | infer/derive | objective, confident |
| genuinely | doubting, qualifying | [remove] | certain, definitive |
| can | permission-seeking | will | confident expectation |
| if needed | uncertain | if incorrect | conditional, clear |
| NO need to | passive, permissive | Proceed without | active, imperative |
| Don't | casual, conversational | Do not | formal, authoritative |
| ask to | tentative, weak | request | professional, clear |
| When uncertain | hesitant, contradictory | Priority | directive, unambiguous |
| acceptable | permission-seeking | investment | factual, confident |
| Good | subjective approval | Default | objective standard |
| + | ambiguous, jargon | explicit list | clear, precise |
| optional | dismissible, weak | [remove or "if relevant"] | purposeful or expected |
| Offer | salesperson, passive | [remove] | autonomous |
| hit | casual, imprecise | reached | formal, precise |
| explicitly needed | redundant, overthinking | on-demand | technical, concise |

---

## Linguistic Precision Principles Applied

### 1. Imperative Voice for Commands
**Before:** "NO need to wait for approval"
**After:** "Proceed without waiting for approval"
**Principle:** Direct commands > passive permissions

### 2. Remove Hedge Words
**Before:** "genuinely incomprehensible"
**After:** "incomprehensible"
**Principle:** Qualifiers weaken, removal strengthens

### 3. Eliminate Subjective Judgments
**Before:** "Good autonomous assumptions"
**After:** "Default assumptions"
**Principle:** Objective standards > vague judgments

### 4. Active Voice Over Passive
**Before:** "Extended reasoning acceptable"
**After:** "Time investment: 5-45 minutes"
**Principle:** Active assertions > passive permissions

### 5. Precise Technical Terms
**Before:** "Time constraint hit"
**After:** "Time constraint reached"
**Principle:** Formal precision > colloquial approximation

### 6. Remove Redundancy
**Before:** "explicitly needed"
**After:** "on-demand"
**Principle:** Say once clearly > repeat with qualifiers

### 7. Strong Modals
**Before:** "User can redirect if needed"
**After:** "User will redirect if incorrect"
**Principle:** "will" (expectation) > "can" (possibility)

---

## Autonomy Language Analysis

### Contradiction Resolution

**Problem:** Line 262 "When uncertain" contradicts Line 54 "operates independently"

**Analysis:**
- Line 54 establishes autonomy principle: proceed independently
- Line 262 suggests there are times of uncertainty
- These create cognitive dissonance: am I uncertain or autonomous?

**Resolution:**
- Replace "When uncertain" with "Priority"
- Frame as quality standard, not uncertainty condition
- Maintains autonomy while setting quality expectations

**Result:** No contradiction, clear hierarchy (autonomy + quality priority)

---

## Permission-Seeking Language Removal

### Identified Permission-Seeking Patterns

1. "reasonable assumptions" → seeking approval for assumption quality
2. "can redirect if needed" → seeking permission to proceed
3. "NO need to wait" → asking if it's okay to proceed
4. "acceptable" → asking if time investment is okay
5. "Offer" → asking permission to provide options

### Replacement Strategy

Replace all permission-seeking with:
- **Assertions:** State facts confidently
- **Imperatives:** Give direct commands
- **Expectations:** Describe what will happen
- **Standards:** Define objective criteria

---

## Testing Precision Improvements

### Scenario 1: Ambiguous Query

**Before (with weak language):**
> "Make reasonable assumptions based on query context. User can redirect if needed."

**Interpretation:** Unclear what "reasonable" means, "can" suggests permission, "if needed" is vague

**After (precise language):**
> "Infer assumptions from query context. User will redirect if incorrect."

**Interpretation:** Clear action (infer), confident expectation (will), definite condition (incorrect)

### Scenario 2: Time Investment

**Before (passive):**
> "Extended reasoning acceptable (5-45 min)"

**Interpretation:** Sounds like asking permission for time

**After (assertive):**
> "Time investment: 5-45 minutes"

**Interpretation:** States fact, no permission sought

---

## Implementation Priority

### Phase 1: HIGH PRIORITY (Autonomy-Critical)
Fix Issues #1-8 immediately - these directly impact autonomous operation

### Phase 2: MEDIUM PRIORITY (Clarity Improvements)
Fix Issues #9-14 after Phase 1 - these improve clarity but don't block autonomy

---

## Verification Checklist

After fixes applied:

- [ ] No hedge words ("basically", "essentially", "generally", "reasonably")
- [ ] No weak modals ("can", "may", "might", "could" where "will", "must" fit)
- [ ] No passive voice where active is stronger
- [ ] No subjective judgments ("good", "nice", "reasonable")
- [ ] No colloquialisms in formal directives
- [ ] No double negatives ("NO need to")
- [ ] No redundancies ("explicitly needed")
- [ ] No permission-seeking language
- [ ] All commands use imperative voice
- [ ] All conditions state clear criteria

---

## Conclusion

**Total issues found:** 14
**High priority:** 8 (autonomy-impacting)
**Medium priority:** 6 (clarity improvements)

**Primary problem:** Permission-seeking and hedge language that undermines autonomous operation principle

**Primary fix:** Replace all permission-seeking with assertions, imperatives, and expectations

**Expected impact:**
- Clearer autonomous behavior (no uncertainty about when to proceed)
- Stronger directives (commands not suggestions)
- Precise language (every word carries specific intention)
- Zero ambiguity about autonomy expectations
