---
name: plot-consistency-checker
description: Analyzes narrative plot points, timelines, and story events to identify inconsistencies, plot holes, continuity errors, and pacing issues. Use when the user needs help ensuring their story remains logically consistent and well-paced.
---

# Plot Consistency Checker

## Purpose

This skill helps authors maintain narrative consistency by tracking plot points, character actions, timelines, and world-building details. It identifies contradictions, plot holes, and pacing problems that could confuse readers or break story immersion.

## When to Use

- User has written multiple chapters and wants to check for continuity errors
- User is concerned about timeline inconsistencies
- User wants to verify character motivations remain consistent
- User needs help identifying plot holes
- User requests a pacing analysis
- User is revising their manuscript and wants to catch errors

## Instructions

### Step 1: Gather Story Information

Ask the user to provide:

- **Story Synopsis**: Brief overview of the main plot
- **Chapters/Scenes**: The content to analyze (can be full manuscript or specific sections)
- **Character List**: Main and supporting characters
- **World Rules**: Any magical systems, technology, or world-specific rules
- **Timeline**: Story duration and key event dates/times
- **Point of View (POV)**: Who tells the story and how (first person, third limited, omniscient)

### Step 2: Create a Story Tracking System

Build comprehensive trackers for:

#### A. Timeline Tracker

```markdown
| Event               | Chapter | Time/Date         | Duration   | Notes         |
| ------------------- | ------- | ----------------- | ---------- | ------------- |
| [Event description] | Ch. X   | [When it happens] | [How long] | [Key details] |
```

#### B. Character Action Tracker

```markdown
| Character | Location | Action          | Chapter | Consequences    |
| --------- | -------- | --------------- | ------- | --------------- |
| [Name]    | [Where]  | [What they did] | Ch. X   | [What resulted] |
```

#### C. Plot Thread Tracker

```markdown
| Plot Thread   | Introduced | Developments | Resolution | Status        |
| ------------- | ---------- | ------------ | ---------- | ------------- |
| [Thread name] | Ch. X      | Ch. Y, Z     | Ch. XX     | Open/Resolved |
```

#### D. World Rules Tracker

```markdown
| Rule/Law           | Established | Used     | Broken? | Chapter References |
| ------------------ | ----------- | -------- | ------- | ------------------ |
| [Rule description] | Ch. X       | Ch. Y, Z | Yes/No  | [List chapters]    |
```

### Step 3: Analyze for Inconsistencies

Check the following categories:

#### A. Timeline Inconsistencies

- Events happening out of order
- Impossible timeframes (character travels 100 miles in 1 hour without explanation)
- Age/birthday contradictions
- Seasonal discrepancies
- Day/night continuity errors

#### B. Character Inconsistencies

- Motivations changing without explanation
- Skills appearing/disappearing randomly
- Physical descriptions contradicting earlier mentions
- Knowledge they shouldn't have (or forgetting what they should know)
- Personality shifts that aren't part of character arc
- Characters being in two places at once

#### C. Plot Holes

- Unresolved plot threads (Chekhov's gun fired but never established)
- Questions raised but never answered
- Easy solutions the characters should have tried but didn't
- Coincidences that are too convenient
- Missing cause-and-effect connections

#### D. World-Building Contradictions

- Magic/technology working differently in different scenes
- Geography changes (forest becomes desert with no explanation)
- Rules established then broken without acknowledgment
- Historical events contradicting each other

#### E. POV Violations

- First person narrator knowing things they couldn't know
- Third limited showing thoughts of non-POV characters
- Omniscient narrator suddenly not knowing something
- Head-hopping mid-scene

#### F. Pacing Issues

- Too much time on minor events, rushing major ones
- Long stretches with no conflict or tension
- Too many events crammed into short timeframes
- Uneven chapter lengths without stylistic purpose

### Step 4: Generate Consistency Report

Present findings in this format:

```markdown
# Plot Consistency Analysis Report

## Executive Summary

- **Total Issues Found**: [Number]
  - Critical: [X] (breaks story logic)
  - Moderate: [Y] (confusing but fixable)
  - Minor: [Z] (easily overlooked)
- **Overall Consistency Score**: [X/10]
- **Most Common Issue Type**: [Category]

---

## Critical Issues

### 1. [Issue Title]

**Type**: Timeline Inconsistency / Character Error / Plot Hole / etc.

**Location**: Chapter [X], pages/paragraphs [reference]

**Problem**:
[Clear description of the inconsistency]

**Evidence**:

- Chapter X, para Y: "[Quote or description]"
- Chapter Z, para W: "[Contradicting quote or description]"

**Impact**: [Why this matters to the reader/story]

**Suggested Fix**:
[Specific recommendation on how to resolve]

---

### 2. [Next Issue]

...

## Moderate Issues

[Same format as Critical]

## Minor Issues

[Same format, can be more brief]

---

## Timeline Visualization
```

Week 1:
Day 1: [Events] - Ch. 1-2
Day 2: [Events] - Ch. 3
[ISSUE: Character teleports from City A to City B instantaneously]
Day 3: [Events] - Ch. 4-5

Week 2:
[etc.]

```

---

## Character Tracking Summary

### [Character Name]
**Chapters Present**: [List]
**Key Actions**: [Brief list]
**Inconsistencies Found**: [X]
  - Chapter Y vs. Chapter Z: [Description]

---

## Unresolved Plot Threads

1. **[Thread Name]** (Introduced: Ch. X)
   - Status: Dangling
   - Last Mention: Ch. Y
   - Reader Expectation: [What readers will expect resolution of]
   - Recommendation: [Resolve in Ch. Z or remove setup in Ch. X]

---

## Pacing Analysis

### Chapter-by-Chapter Breakdown
| Chapter | Word Count | Events | Tension Level | Pacing |
|---------|------------|--------|---------------|--------|
| 1 | 3,500 | Setup, inciting incident | Medium | Good |
| 2 | 5,000 | Travel, conversation | Low | Too slow |
| 3 | 2,000 | Major revelation, action | High | Too rushed |

**Pacing Recommendations**:
- Chapter 2: Consider cutting 1,000 words of exposition; add minor conflict
- Chapter 3: Expand action scene by 1,000 words to give proper weight

---

## World-Building Consistency

### Magic System: [Name]
**Established Rules**:
1. [Rule 1] - Ch. [X]
2. [Rule 2] - Ch. [Y]

**Violations**:
- Ch. [Z]: Character does [action] which violates rule #1
  - FIX: Either establish exception or revise action

---

## POV Consistency Check

**Declared POV**: Third Person Limited (Character A's perspective)

**Violations**:
- Ch. [X], para [Y]: Narrator reveals Character B's thoughts
  - Quote: "[Example]"
  - FIX: Show Character B's feelings through actions/dialogue only

---

## Positive Observations

[List things that are working well]
- Timeline for Chapters 1-5 is perfectly consistent
- Character X's arc is well-maintained
- World rules are clearly established in Ch. 2

---

## Priority Fixes (Top 5)

1. **[Most critical issue]** - Breaks story logic
2. **[Second most critical]** - Major reader confusion
3. [etc.]

---

## Questions for Author

[List ambiguities or decisions the author needs to make]
1. In Chapter X, is [event] supposed to be a dream sequence? Current text is unclear.
2. Character Y seems to change motivation in Chapter Z—is this intentional character development or an error?
```

## Examples

### Example 1: Fantasy Novel Timeline Issue

**User**: "Can you check my first 5 chapters for consistency? My beta readers said something felt off with the timeline."

**Analysis Output**:

```markdown
# Plot Consistency Analysis Report

## Executive Summary

- **Total Issues Found**: 8
  - Critical: 2 (breaks story logic)
  - Moderate: 4 (confusing but fixable)
  - Minor: 2 (easily overlooked)
- **Overall Consistency Score**: 6/10
- **Most Common Issue Type**: Timeline Inconsistencies

---

## Critical Issues

### 1. Impossible Travel Time

**Type**: Timeline Inconsistency

**Location**: Chapter 2 (para 15) to Chapter 3 (para 1)

**Problem**:
Kael travels from Riverhold to the Capital (established as 5 days' journey in Ch. 1) in what appears to be overnight.

**Evidence**:

- Chapter 2, para 15: "As the sun set over Riverhold, Kael mounted his horse and began the long journey to the Capital."
- Chapter 2, para 23: "He made camp that first night under a canopy of stars."
- Chapter 3, para 1: "The next morning, Kael rode through the Capital gates."

**Impact**: Readers who remember the 5-day distance will be confused. Breaks geographical consistency.

**Suggested Fix**:
Option 1: Add a time skip - "After five days of hard riding, Kael finally..."
Option 2: Add magical transport that was established earlier (teleportation, portal, etc.)
Option 3: Revise Ch. 1 to make it 1-2 days' journey instead

---

### 2. Character Knowledge Violation

**Type**: Character Inconsistency / Plot Hole

**Location**: Chapter 4, para 18

**Problem**:
Princess Elara knows about the assassination plot, but there's no scene where she learns this information.

**Evidence**:

- Chapter 4, para 18: "'I know you're planning to kill the king,' Elara said coldly."
- No prior scene shows: someone telling her, her overhearing, or her discovering evidence

**Impact**: Readers will re-read looking for the reveal they missed. Feels like a plot hole.

**Suggested Fix**:
Option 1: Add a scene in Ch. 3 where Elara overhears the plotting
Option 2: Add internal monologue in Ch. 4: "After weeks of piecing together whispers and stolen glances, she finally had confirmation..."
Option 3: Make her accusation a bluff/guess and show her reaction to their guilty faces confirming it

---

## Moderate Issues

### 3. Eye Color Inconsistency

**Type**: Character Physical Description

**Location**: Chapter 1 vs. Chapter 5

**Problem**:
Kael's eye color changes from blue to green.

**Evidence**:

- Chapter 1, para 7: "His blue eyes reflected the ocean."
- Chapter 5, para 12: "She looked into his startling green eyes."

**Impact**: Character description inconsistency breaks immersion.

**Suggested Fix**:
Choose one color and useFind & Replace. Consider unique eye color as character identifier.

---

[etc.]

---

## Timeline Visualization
```

Day 1 (Chapter 1):

- Morning: Kael in Riverhold, receives mission
- Afternoon: Meets with informant, learns Capital is "5 days north"
- Evening: Departs Riverhold

Day 2 (Chapter 2-3):

- Night: Makes camp [CORRECT]
- Morning: ARRIVES AT CAPITAL [ISSUE: Should be Day 6]

Day 3 (Chapter 3-4):

- Palace infiltration
- Meets Princess Elara

Day 4 (Chapter 5):

- Assassination attempt

```

**Recommendation**: Insert time skip or explain rapid travel.

---

## Unresolved Plot Threads

1. **The Mysterious Informant** (Introduced: Ch. 1, para 15)
   - Status: Dangling
   - Last Mention: Ch. 1, para 20
   - Reader Expectation: This shady character will return or be revealed as important
   - Recommendation: Either bring them back in Ch. 6-7 or establish in Ch. 1 they're just a one-time contact

2. **Kael's Sister's Illness** (Introduced: Ch. 2, mentioned in flashback)
   - Status: Unresolved
   - Last Mention: Ch. 2
   - Reader Expectation: This is his motivation, should stay relevant
   - Recommendation: Have Kael reference it periodically; maybe he's doing this mission for money to cure her

---

## Priority Fixes (Top 5)

1. **Impossible Travel Time (Critical)** - Major timeline break
2. **Princess's Unexplained Knowledge (Critical)** - Plot hole
3. **Eye Color Change (Moderate)** - Easy fix but noticeable
4. **Unresolved Informant Thread (Moderate)** - Decide if relevant
5. **Missing Motivation (Moderate)** - Why does Kael care about this mission?
```

### Example 2: Contemporary Romance POV Issue

**User**: "I'm writing in first person from Ava's perspective. Can you check if I accidentally head-hopped?"

**Analysis Output**:

```markdown
# Plot Consistency Analysis Report - POV Check

## Executive Summary

- **Declared POV**: First Person (Ava's perspective)
- **POV Violations Found**: 3
- **Overall POV Consistency Score**: 7/10

---

## POV Violations

### 1. Character Thought Access Violation

**Type**: POV Violation

**Location**: Chapter 3, paragraph 8

**Problem**:
Narrator reveals Jake's internal thoughts/feelings that Ava couldn't know.

**Evidence**:

> "I watched Jake from across the coffee shop. He seemed nervous, his fingers drumming the table. He was worried I'd say no to his invitation, remembering how his ex had always refused his suggestions."

**Why It's a Problem**:
Ava can't know:

- That Jake is nervous (she can observe behavior but can't confirm internal state)
- What specifically he's worried about
- His memories of his ex

**What Ava CAN Know**:

- Observable behaviors (drumming fingers)
- What Jake tells her verbally
- Her own interpretations and guesses

**Suggested Fix**:

> "I watched Jake from across the coffee shop. His fingers drummed the table—a nervous habit I'd noticed before. Was he worried I'd say no? Maybe he'd dealt with too many rejections before. I decided to put him out of his misery."

(Shows Ava _observing_ and _inferring_, not magically knowing)

---

### 2. Omniscient Narrator Slip

**Type**: POV Violation

**Location**: Chapter 5, paragraph 14

**Problem**:
Narrator provides information about a character not present that Ava couldn't know yet.

**Evidence**:

> "While I was meeting with my editor, Jake was at home finding the letter I'd hidden in my desk drawer."

**Why It's a Problem**:
Ava isn't present for this scene and doesn't learn about it until later (Ch. 7). In first person POV, you can't show scenes the narrator didn't witness unless it's framed as them learning about it later.

**Suggested Fix**:
Option 1: Remove this line entirely; reveal Jake found the letter when Ava discovers it
Option 2: Frame as flashback/retrospective: "I didn't know it then, but while I was meeting with my editor, Jake was at home finding the letter..."
Option 3: Switch to alternating POV (requires full revision to add Jake's first-person chapters)

---

### 3. Impossible Knowledge

**Type**: POV Violation / Plot Hole

**Location**: Chapter 6, paragraph 22

**Problem**:
Ava knows specific dialogue from a conversation she wasn't part of.

**Evidence**:

> "'We need to tell her,' Sarah said to Marcus.
> 'Not yet,' he replied. 'She's not ready.'
> I had no idea they were talking about me, but I'd find out soon enough."

**Why It's a Problem**:
If Ava wasn't there and hasn't been told about this conversation yet, she can't quote it verbatim. The last sentence tries to justify it but doesn't fix the logical impossibility.

**Suggested Fix**:
Option 1: Remove this scene entirely; show Ava discovering later that they'd been discussing her
Option 2: Frame as Sarah telling Ava later: "Sarah later confided in me: 'We had a whole conversation about whether to tell you...'"
Option 3: Make Ava present but hidden: "I froze outside the door when I heard Sarah's voice..."

---

## What's Working Well

✓ Chapters 1, 2, 4, and 7-10 maintain perfect first-person POV
✓ Ava's voice is consistent and distinct
✓ You do a great job showing Jake's feelings through his actions and Ava's interpretations
✓ The internal monologue feels natural and adds personality

---

## POV Best Practices Reminder

When writing first person (Ava's POV), she can share:

- ✓ Everything she directly experiences (sees, hears, smells, touches, tastes)
- ✓ Her own thoughts and feelings
- ✓ Her interpretations and guesses about others ("He seemed angry" not "He was angry")
- ✓ Information told to her by other characters
- ✓ Things she learns about later (if framed as "I later found out...")

She CANNOT share:

- ✗ Other characters' internal thoughts/feelings as fact
- ✗ Scenes she's not present for (unless doing retrospective framing)
- ✗ Dialogue/events she didn't witness and hasn't been told about
- ✗ Information she has no way of knowing

---

## Recommended Reading Order for Fixes

1. Fix Ch. 5, para 14 first (biggest logic problem)
2. Fix Ch. 6, para 22 second (affects later plot)
3. Fix Ch. 3, para 8 last (minor, easy fix)
```

## Validation Process

After generating the report, Claude should ask:

"I've completed the consistency analysis. Would you like me to:

1. Elaborate on any specific issue?
2. Help you fix the critical issues with revised text?
3. Check additional chapters?
4. Create a continuity bible for future reference?"

## Tips for Authors

**Before Submitting for Analysis**:

- Compile all relevant chapters/scenes
- List any intentional contradictions (unreliable narratort, time loops, etc.)
- Note any world rules that might seem inconsistent but aren't (magic that works differently based on X)

**Using the Analysis**:

- Fix Critical issues before Moderate
- Some "inconsistencies" might be intentional mysteries—decide case by case
- Create a story bible to track details for future writing

## Validation Checklist

Before finalizing the consistency report:

- [ ] All issues include specific chapter/paragraph references
- [ ] Evidence is quoted or specifically described
- [ ] Each issue includes suggested fix options
- [ ] Timeline is visualized if relevant
- [ ] Character tracking is complete
- [ ] Unresolved threads are identified
- [ ] Positive observations are included (not just problems)
- [ ] Report is actionable (author knows what to do next)
