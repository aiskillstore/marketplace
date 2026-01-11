# Two-Claude Iterative Development Methodology

## The Core Concept

Most skills require iteration to reach production quality. The **Two-Claude Method** uses separate Claude instances with distinct roles to systematically improve skills through observation and refinement.

**Why this works:**
- **Claude A (Builder)** experiences the skill as a real user would
- **Claude B (Tester)** provides objective analysis without bias from having just used the skill
- Separation prevents "creator's bias" where you assume your skill is clearer than it is
- Systematic observation captures data that drives targeted improvements

## The Two Roles

### Claude A: The Builder (Skill User)

**Environment Setup:**
- Has the skill loaded in `~/.claude/skills/` or `.claude/skills/`
- Works on realistic tasks the skill is designed to help with
- Behaves like a normal user (doesn't try to "game" the skill)

**Responsibilities:**
1. Perform realistic tasks that should trigger the skill
2. Follow skill guidance naturally (don't force it to work)
3. Document experience in real-time:
   - When did skill trigger (or fail to trigger)?
   - Was guidance clear or confusing?
   - What worked smoothly?
   - Where did you get stuck?
4. Complete tasks and save session logs

**Key Behavior:**
- **Be authentic** - If confused, be confused (don't "help" the skill)
- **Document friction** - Every moment of uncertainty is data
- **Follow instructions literally** - Reveals ambiguity in wording
- **Don't fix skill mid-session** - Finish task first, then analyze

### Claude B: The Tester/Observer (Skill Analyzer)

**Environment Setup:**
- Reviews Claude A's session logs and outputs
- Has access to skill source files for editing
- Does NOT have skill loaded (prevents bias)

**Responsibilities:**
1. Analyze Claude A's session systematically:
   - Did skill trigger appropriately?
   - What friction points occurred?
   - Which instructions were followed vs. skipped?
   - What caused confusion or errors?
2. Identify root causes (not just symptoms)
3. Propose specific, targeted improvements
4. Edit skill files based on analysis
5. Document changes for next iteration

**Key Behavior:**
- **Look for patterns** - One confusion = possible fluke, three = problem
- **Root cause analysis** - Why did Claude A struggle? (not just "it didn't work")
- **Minimal effective changes** - Fix specific issue, don't rewrite everything
- **Measure impact** - Predict how change will improve next iteration

## The Iteration Cycle

### Iteration 1: Baseline

**Claude A (Builder):**
1. Start with fresh conversation
2. Work on realistic task that should use the skill
3. Document experience:
   ```
   Task: [What you're trying to accomplish]
   Expected: Skill should trigger on [specific keyword/context]
   Actual: [What happened]
   Confusion points: [Where did you get stuck?]
   Completion: [Did you finish the task? Quality of output?]
   ```
4. Save conversation log and outputs
5. **Do not look at skill source files yet**

**Claude B (Tester):**
1. Read Claude A's session log completely
2. Analyze systematically:
   ```
   Triggering Analysis:
   - Did skill load when appropriate? YES/NO
   - False positives (triggered when shouldn't)? YES/NO
   - Trigger clarity score: [1-10]

   Guidance Analysis:
   - Were instructions clear? [1-10]
   - Which steps caused confusion? [List specific steps]
   - What was missing? [Specific gaps]

   Workflow Analysis:
   - Did workflow match actual task? YES/NO
   - Were checkpoints helpful? [1-10]
   - Validation effective? YES/NO

   Output Quality:
   - Task completed successfully? YES/NO
   - Output met standards? [1-10]
   - User confidence level? [1-10]
   ```

3. Identify top 3 improvement opportunities
4. Make targeted edits to skill files
5. Document changes:
   ```
   Change 1: [What you changed]
   Reason: [Why - reference specific Claude A friction]
   Expected improvement: [What should be better next iteration]
   ```

### Iteration 2: First Improvement

**Claude A (Builder):**
1. **New fresh conversation** (don't continue previous session)
2. Work on SAME task as Iteration 1 (for comparison)
3. Document experience using same template
4. Note: "Better than Iteration 1?" [Specific improvements noticed]

**Claude B (Tester):**
1. Compare Iteration 1 vs. Iteration 2 logs side-by-side
2. Measure improvement:
   ```
   Triggering: Iter1 [score] → Iter2 [score] = [delta]
   Clarity: Iter1 [score] → Iter2 [score] = [delta]
   Completion: Iter1 [score] → Iter2 [score] = [delta]
   ```
3. Identify:
   - What improved (validate changes worked)
   - What didn't improve (changes ineffective)
   - New issues that emerged
4. Make next round of targeted improvements
5. Document changes with comparison to previous iteration

### Iteration 3+: Refinement

Repeat the cycle:
- Claude A: Fresh conversation, same or similar task
- Claude B: Analyze, compare to previous iterations, refine

**Stop iterating when:**
- Task completion rate ≥90% across 3 consecutive sessions
- Clarity scores ≥8/10 consistently
- No new friction points in last 2 iterations
- Improvements show diminishing returns

## Example Iteration: commit-helper Skill

### Iteration 1: Baseline Session

**Claude A's Experience:**

*Task:* "Create a commit for my changes to the authentication system"

*Session Log:*
```
User: Create a commit for my changes to the authentication system

Claude A: I'll help create a commit. Let me check your changes.
[Runs: git status]
[Runs: git diff]

I can see you've modified auth.py and added tests. Let me create a commit message.

[Creates commit with message: "Update authentication"]

User: That commit message isn't very descriptive...

Claude A: You're right, let me improve it.
[Amends commit with: "Add JWT token validation to authentication system"]

Task completed in 4 messages.
```

*Claude A's Notes:*
- ✓ Skill triggered on "commit" keyword
- ✗ Didn't check git log for repo style before crafting message
- ✗ Initial commit message too vague
- ✗ Required user correction (shouldn't need this)
- ⚠️ Workflow exists but wasn't fully followed

**Claude B's Analysis:**

```
Triggering Analysis:
- Did skill load? YES ✓
- Triggered appropriately? YES ✓
- Trigger clarity: 9/10 ✓

Guidance Analysis:
- Instructions clear? 7/10 (adequate but not followed completely)
- Confusion points: None explicit
- Missing: Emphasis on checking git log BEFORE drafting message

Workflow Analysis:
- Did workflow match task? YES
- Issue: git log step exists but Claude A skipped it
- Root cause: Not emphasized as REQUIRED step

Output Quality:
- Task completed? YES
- Output quality: 6/10 initially, 8/10 after correction
- Required user intervention: YES ✗
```

**Top 3 Improvements:**
1. **Make git log check explicit and required** before drafting message
2. **Add example** of good vs. bad commit message
3. **Emphasize**: Run git status + git diff + git log **in parallel**

**Changes Made:**
```
Change 1: Modified Step 1 in SKILL.md
BEFORE: "Run git status to see changes"
AFTER: "Run these commands IN PARALLEL:
        - git status (see all untracked files)
        - git diff (see changes being committed)
        - git log (see recent commits to match style)"

Reason: Claude A skipped git log, leading to poor initial message
Expected improvement: Claude will run all three commands together

Change 2: Added example section
BEFORE: [No examples in SKILL.md]
AFTER: "Example good message: 'Add JWT validation to auth system with expiry checks'
        Example bad message: 'Update auth' (too vague)"

Reason: Claude A wrote vague message initially
Expected improvement: Clear example sets standard

Change 3: Added explicit checklist
AFTER: "Before committing:
        - [ ] Reviewed git log for message style
        - [ ] Message explains WHY, not just WHAT
        - [ ] Message is 1-2 sentences, descriptive"

Reason: Make critical steps impossible to skip
Expected improvement: Systematic quality gates
```

### Iteration 2: First Improvement

**Claude A's Experience:**

*Task:* "Create a commit for my changes to the authentication system" (SAME task)

*Session Log:*
```
User: Create a commit for my changes to the authentication system

Claude A: I'll create a commit. Let me gather context first.
[Runs in parallel: git status, git diff, git log]

I can see:
- Modified: auth.py (added JWT validation)
- Added: test_auth.py (validation tests)
- Recent commits follow pattern: "Add [feature] to [system] with [detail]"

I'll create a commit following this style:
"Add JWT token validation to authentication system with expiry checking"

[Creates commit with message]

Task completed in 2 messages. ✓
```

*Claude A's Notes:*
- ✓ Skill triggered immediately
- ✓ Ran all three commands in parallel (improvement!)
- ✓ Checked git log BEFORE crafting message
- ✓ Message matched repo style without correction needed
- ✓ No user intervention required
- ✓ 4 messages → 2 messages (50% faster)

**Claude B's Analysis:**

```
Comparison Iter1 → Iter2:
- Messages to completion: 4 → 2 (50% improvement) ✓
- User corrections needed: 1 → 0 (100% improvement) ✓
- Initial message quality: 6/10 → 9/10 (+3 points) ✓
- Workflow adherence: 7/10 → 10/10 (+3 points) ✓

Changes Validated:
✓ Change 1 (parallel commands): EFFECTIVE - Claude ran all three
✓ Change 2 (examples): EFFECTIVE - Message quality improved
✓ Change 3 (checklist): EFFECTIVE - Systematic approach followed

New Issues: None identified

Recommendation: Test on different task type (edge case)
```

### Iteration 3: Edge Case Testing

**Claude A's Experience:**

*Task:* "Commit my changes" (DIFFERENT: repo has pre-commit hook that auto-formats code)

*Session Log:*
```
User: Commit my changes

Claude A: I'll create a commit.
[Runs: git status, git diff, git log]

Changes detected in format.py (added new formatter)
[Creates commit: "Add markdown formatter with syntax highlighting"]

Pre-commit hook ran and modified format.py (auto-formatting)

Let me check if I should amend the commit...
[Checks: git log -1 --format='%an %ae' → confirms I'm author]
[Checks: git status → confirms not pushed]

Amending commit to include hook's formatting changes.
[Amends commit]

Task completed successfully with hook handling. ✓
```

*Claude A's Notes:*
- ✓ Handled pre-commit hook edge case perfectly
- ✓ Checked authorship before amending (good safety)
- ✓ No user confusion about hook behavior
- ⚠️ Could have explained what hook did (minor improvement)

**Claude B's Analysis:**

```
Edge Case Performance: 9/10
- Handled hook modification correctly ✓
- Safety checks performed ✓
- Could add brief explanation of hook behavior

Minor Enhancement:
Add one line explaining: "Pre-commit hook auto-formatted code - amending commit to include these changes."

Overall Status: Production-ready for commit workflow
- Happy path: 10/10
- Edge cases: 9/10
- No critical issues remaining
```

**Final Change:**
```
Change 4: Add hook explanation
AFTER: "If pre-commit hook modifies files, explain:
        'Pre-commit hook auto-formatted code - amending commit to include these changes.'"

Reason: User confidence - know what's happening
Expected improvement: Minor (already working well, adds clarity)
```

### Iteration Complete

**Decision:** Ship skill after Iteration 3
- 3 consecutive successful sessions
- Happy path: 10/10
- Edge case: 9/10
- No critical issues
- Further iteration shows diminishing returns

## Observation Techniques

### What to Document During Claude A Sessions

**Triggering Observations:**
- Timestamp when skill should have triggered
- Timestamp when skill actually triggered (if different)
- Keywords/context present when trigger occurred
- False positives (triggered when shouldn't have)

**Guidance Observations:**
- Which instructions were followed exactly as written
- Which instructions were interpreted differently
- Steps that were skipped (and why, if inferable)
- Points where Claude A paused or seemed uncertain
- Questions Claude A asked (indicates missing info)

**Workflow Observations:**
- Did workflow steps match actual task sequence?
- Were checkpoints encountered at right times?
- Did validation catch errors effectively?
- Were error messages actionable?

**Output Quality Observations:**
- Did output meet expected standards?
- What quality issues occurred?
- How many corrections were needed?
- User satisfaction with final result

### What to Analyze in Claude B Review

**Pattern Recognition:**
- Same issue in multiple sessions? → Systemic problem
- Issue in one session only? → Possible edge case or fluke
- Issue getting worse? → Recent change made it worse
- Issue getting better? → Recent change working

**Root Cause Analysis:**

Don't just fix symptoms:
```
❌ Symptom: "Claude A wrote bad commit message"
   Bad fix: Add more examples

✓ Root cause: "Claude A didn't check git log for style"
  Good fix: Make git log check explicit and required
```

Ask "Why?" 5 times:
1. Why was commit message bad? → Didn't match repo style
2. Why didn't it match? → Didn't check existing commits
3. Why didn't check? → Step not emphasized as required
4. Why not emphasized? → Listed alongside optional steps
5. Why alongside optional? → Workflow structure unclear

**Fix at root level:** Restructure workflow with required vs. optional steps clearly marked

### Measuring Improvement

**Quantitative Metrics:**
- Messages to completion (fewer is better)
- User corrections needed (fewer is better)
- Time to completion (faster is better)
- Error rate (lower is better)

**Qualitative Metrics:**
- Clarity score 1-10 (higher is better)
- Confidence score 1-10 (higher is better)
- Workflow adherence (percentage of steps followed correctly)

**Track Across Iterations:**
```
| Metric | Iter1 | Iter2 | Iter3 | Target | Status |
|--------|-------|-------|-------|--------|--------|
| Messages | 4 | 2 | 2 | ≤3 | ✓ Met |
| Corrections | 1 | 0 | 0 | 0 | ✓ Met |
| Clarity | 7/10 | 9/10 | 9/10 | ≥8 | ✓ Met |
| Workflow % | 70% | 100% | 100% | ≥90% | ✓ Met |
```

## Common Iteration Patterns

### Pattern 1: Skill Not Triggering

**Symptom:** Claude A doesn't use skill when expected

**Investigation:**
- Check: Is description specific enough?
- Check: Are trigger terms present?
- Check: Is YAML valid?

**Fixes:**
- Add concrete trigger terms to description
- Include use case keywords
- Test with variations of user phrasing

### Pattern 2: Skill Triggers But Ignored

**Symptom:** Skill loads but Claude A doesn't follow guidance

**Investigation:**
- Check: Are instructions clear and concrete?
- Check: Are examples present?
- Check: Is guidance actionable?

**Fixes:**
- Add concrete examples
- Make steps explicit (numbered list vs. paragraph)
- Show expected output format

### Pattern 3: Workflow Skipped Steps

**Symptom:** Claude A skips certain workflow steps

**Investigation:**
- Check: Are steps clearly required vs. optional?
- Check: Is value of step explained?
- Check: Are steps in logical order?

**Fixes:**
- Mark required steps explicitly
- Explain WHY step matters (not just WHAT to do)
- Reorder steps to match natural flow

### Pattern 4: Validation Ineffective

**Symptom:** Errors aren't caught by validation steps

**Investigation:**
- Check: Is validation automated (script) or manual (Claude judgment)?
- Check: Are validation criteria specific?
- Check: Are error messages actionable?

**Fixes:**
- Add validation script (don't rely on Claude to spot errors)
- Define specific pass/fail criteria
- Improve error messages with fix suggestions

## Two-Claude Checklist

**Before Starting Iterations:**
- [ ] Clear task defined (realistic use case)
- [ ] Success criteria established (what "good" looks like)
- [ ] Claude A environment set up (skill loaded)
- [ ] Claude B environment set up (skill source accessible)
- [ ] Documentation template ready (for consistent observation)

**During Each Iteration:**
- [ ] Claude A: Fresh conversation started
- [ ] Claude A: Task attempted authentically
- [ ] Claude A: Experience documented thoroughly
- [ ] Claude B: Session log analyzed systematically
- [ ] Claude B: Root causes identified (not just symptoms)
- [ ] Claude B: Changes made with predicted impact
- [ ] Changes documented for comparison

**After Iteration Cycle:**
- [ ] Improvements measured quantitatively
- [ ] Pattern analysis completed (what works, what doesn't)
- [ ] Diminishing returns check (is further iteration worth it?)
- [ ] Production-ready criteria met (all targets achieved)

---

**Key Principle:** Skills improve through systematic observation and targeted refinement, not through guessing what might be better. Let real usage data drive every change.
