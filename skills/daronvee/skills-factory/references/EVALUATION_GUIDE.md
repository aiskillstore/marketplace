# Evaluation-Driven Development for Skills

## Why Start with Evaluations?

**Traditional approach (problematic):**
1. Write extensive skill documentation
2. Test manually
3. Discover it doesn't work as expected
4. Rewrite significant portions
5. Repeat

**Evaluation-driven approach (recommended):**
1. Define what success looks like (evaluation)
2. Write minimal skill version
3. Run evaluation to measure performance
4. Iterate based on objective metrics
5. Expand skill only where evaluations show gaps

**Key Benefit:** You know if your skill works BEFORE investing hours in comprehensive documentation.

## The Evaluation-First Methodology

### Phase 1: Define Success (Before Building)

**Create your evaluation FIRST** with 3-5 test scenarios:

1. **Baseline scenario** - What happens WITHOUT the skill?
2. **Happy path** - Ideal use case WITH the skill
3. **Edge cases** - Challenging but valid scenarios
4. **Failure cases** - Where skill should gracefully decline
5. **Ambiguous cases** - Unclear triggers or contexts

### Phase 2: Build Minimal Viable Skill

Create the simplest version that could work:
- SKILL.md with essential YAML + core instructions only
- No references yet (unless absolutely critical)
- No scripts yet (unless core to functionality)
- Focus on triggering correctly and basic guidance

### Phase 3: Run Baseline Evaluation

Test your minimal skill against all evaluation scenarios:
- Document actual behavior for each test
- Compare against expected outcomes
- Measure: Did Claude invoke the skill when appropriate?
- Measure: Did the skill provide sufficient guidance?
- Identify gaps objectively

### Phase 4: Iterate Based on Data

**Only add complexity where evaluations show it's needed:**
- Skill not triggering? → Improve description with better trigger terms
- Triggering but vague guidance? → Add concrete examples to SKILL.md
- Users need deep context? → Create reference file for that context
- Repetitive errors? → Add validation script
- Complex decision-making? → Add workflow with checkpoints

### Phase 5: Expand and Re-evaluate

After each improvement:
1. Re-run evaluations
2. Measure improvement (quantify if possible)
3. Identify remaining gaps
4. Add next highest-value enhancement
5. Repeat until evaluation success rate is acceptable

## Evaluation Structure Template

```markdown
# [Skill Name] Evaluation

## Test Scenarios

### Scenario 1: Baseline (No Skill)
**Setup:** Claude without skill loaded
**Task:** [Describe realistic task]
**Expected Behavior:** [What happens without skill]
**Actual Behavior:** [Document what occurred]
**Success Criteria:** [How to measure if this is "good enough"]

### Scenario 2: Happy Path
**Setup:** Claude with skill loaded
**Task:** [Ideal use case for the skill]
**Expected Behavior:**
- Skill triggers automatically
- Provides clear guidance
- User completes task successfully
**Actual Behavior:** [Document what occurred]
**Success Criteria:**
- [ ] Skill invoked within first 2 messages
- [ ] User completes task without confusion
- [ ] Output meets quality standards

### Scenario 3: Edge Case - [Specific Challenge]
**Setup:** Claude with skill loaded
**Task:** [Challenging but valid scenario]
**Expected Behavior:** [How skill should handle this]
**Actual Behavior:** [Document what occurred]
**Success Criteria:** [Specific measures of success]

### Scenario 4: Failure Case - [Invalid Use]
**Setup:** Claude with skill loaded
**Task:** [Something skill should NOT try to handle]
**Expected Behavior:** Skill should NOT trigger, or should gracefully decline
**Actual Behavior:** [Document what occurred]
**Success Criteria:**
- [ ] Skill doesn't trigger inappropriately
- [ ] Claude handles task normally without skill interference

### Scenario 5: Ambiguous Case
**Setup:** Claude with skill loaded
**Task:** [Unclear whether skill should activate]
**Expected Behavior:** [Desired outcome]
**Actual Behavior:** [Document what occurred]
**Success Criteria:** [How to judge success]

## Evaluation Results Summary

| Scenario | Baseline Score | With Skill Score | Improvement | Notes |
|----------|----------------|------------------|-------------|-------|
| Scenario 1 | [rating] | N/A | N/A | Baseline reference |
| Scenario 2 | N/A | [rating] | - | Happy path test |
| Scenario 3 | [rating] | [rating] | [delta] | Edge case |
| Scenario 4 | [rating] | [rating] | [delta] | Failure handling |
| Scenario 5 | [rating] | [rating] | [delta] | Ambiguity test |

**Overall Assessment:** [Summary of skill effectiveness]
**Next Improvements:** [Prioritized list based on gaps]
```

## Example Evaluation: commit-helper Skill

### Scenario 1: Baseline (No Skill)
**Setup:** Claude without commit-helper skill
**Task:** "Create a commit with my changes"
**Expected Behavior:** Claude asks what changes to commit, may miss best practices
**Actual Behavior:**
- Asked user what files to include
- Created commit message without checking git log style
- Didn't run git status first
- Commit message lacked context

**Success Criteria:** Task completed but inefficiently (6/10)

### Scenario 2: Happy Path
**Setup:** Claude with commit-helper skill
**Task:** "Create a commit with my changes"
**Expected Behavior:**
- Skill triggers automatically
- Runs git status, git diff, git log in parallel
- Analyzes changes and drafts appropriate message
- Follows repo's commit style
- Adds co-authored-by attribution

**Actual Behavior:**
- ✓ Skill triggered on "commit" keyword
- ✓ Ran all three git commands in parallel
- ✓ Analyzed diff and drafted message matching repo style
- ✓ Added attribution footer
- Task completed in 2 messages vs. 5+ without skill

**Success Criteria:**
- [x] Skill invoked within first message
- [x] User completed task without additional prompts
- [x] Output met quality standards (repo style matched)

**Score:** 10/10 - Significant improvement

### Scenario 3: Edge Case - Pre-commit Hook Modifies Files
**Setup:** Claude with commit-helper skill
**Task:** "Commit my changes" (repo has pre-commit hook that auto-formats)
**Expected Behavior:**
- Initial commit succeeds
- Hook modifies files
- Skill detects modification and checks if safe to amend
- Amends commit if appropriate (not pushed, same author)

**Actual Behavior:**
- ✓ Initial commit succeeded
- ✓ Detected hook modified files
- ✓ Checked authorship and push status
- ✓ Amended commit safely
- Handled edge case without user intervention

**Success Criteria:**
- [x] Hook changes detected
- [x] Safe amend decision made correctly
- [x] User not confused by hook behavior

**Score:** 9/10 - Well handled

### Scenario 4: Failure Case - No Changes to Commit
**Setup:** Claude with commit-helper skill
**Task:** "Create a commit" (but working directory is clean)
**Expected Behavior:**
- Skill should recognize no changes exist
- Should inform user clearly
- Should NOT create empty commit

**Actual Behavior:**
- ✓ Ran git status and detected clean working directory
- ✓ Informed user: "No changes to commit"
- ✓ Did not attempt to create commit
- Graceful failure

**Success Criteria:**
- [x] Detected clean state
- [x] Did not create empty/invalid commit
- [x] Clear communication to user

**Score:** 10/10 - Correct behavior

### Scenario 5: Ambiguous Case - "Save my work"
**Setup:** Claude with commit-helper skill
**Task:** "Save my work" (could mean commit, or could mean file write)
**Expected Behavior:**
- If files have uncommitted changes → Offer to commit
- If files not yet written → Save files first
- Use context to disambiguate

**Actual Behavior:**
- ✓ Checked git status to see if changes exist
- ✓ Detected uncommitted changes
- ✓ Asked: "Would you like me to commit these changes?"
- Good disambiguation

**Success Criteria:**
- [x] Didn't assume intent
- [x] Used context to make intelligent offer
- [x] User wasn't confused

**Score:** 8/10 - Could auto-commit if obvious, but safe approach

## Evaluation Results Summary

| Scenario | Baseline Score | With Skill Score | Improvement | Notes |
|----------|----------------|------------------|-------------|-------|
| Baseline | 6/10 | N/A | N/A | Inefficient, missed best practices |
| Happy path | N/A | 10/10 | - | Excellent automation and quality |
| Edge case (hooks) | 4/10 | 9/10 | +5 | Significant improvement |
| Failure case | 7/10 | 10/10 | +3 | Better detection and messaging |
| Ambiguous case | 6/10 | 8/10 | +2 | Smart disambiguation |

**Overall Assessment:** Skill provides substantial value across all scenarios. Baseline → With Skill shows 3-5 point improvement consistently.

**Next Improvements:**
1. Could auto-commit on unambiguous "save my work" (minor enhancement)
2. Add support for multi-repo workflows (future feature)

## Success Criteria Guidelines

### Quantitative Metrics
- **Task completion rate:** Did user accomplish goal?
- **Message efficiency:** How many messages required? (fewer is better)
- **Error rate:** How many mistakes/retries?
- **Time to completion:** Faster with skill vs. without?

### Qualitative Metrics
- **Clarity:** Was guidance clear and unambiguous?
- **Correctness:** Did output meet quality standards?
- **Appropriate triggering:** Did skill activate when it should (and not when it shouldn't)?
- **User confidence:** Did user feel guided vs. confused?

### Comparison Framework
Always compare **Baseline (without skill)** vs. **With skill**:

| Dimension | Baseline | With Skill | Target Improvement |
|-----------|----------|------------|-------------------|
| Messages to completion | 5-7 | 2-3 | >50% reduction |
| Errors made | 2-3 | 0-1 | >60% reduction |
| Quality score (1-10) | 6 | 9 | +3 points minimum |
| User confusion events | 2 | 0 | 100% elimination |

**A successful skill should show meaningful improvement in at least 3 dimensions.**

## When to Expand Your Skill

**Expand when evaluations show specific gaps:**

❌ **Don't expand if:**
- Evaluation shows skill already works well (>8/10 across scenarios)
- Users aren't actually confused (your assumption, not data)
- You just want to add "nice to have" features without evaluation justification

✅ **Do expand if:**
- Evaluation shows skill fails to trigger when needed (<7/10 triggering rate)
- Users get stuck at specific step repeatedly (>30% confusion rate)
- Edge cases fail frequently (>20% failure rate on valid use cases)
- Specific reference content would improve score by >2 points

**Example:**
- Evaluation shows 40% of users confused by validation errors
- → **Add** validation_patterns.md reference with clear examples
- Re-evaluate: Confusion drops to 10%
- → **Justified expansion**

## Evaluation Iteration Cycle

```
1. Write evaluation (5 scenarios)
         ↓
2. Build minimal skill
         ↓
3. Run evaluation → Document scores
         ↓
    Score <8/10? → 4. Identify specific gap
         ↓              ↓
    Score ≥8/10    5. Add targeted improvement
         ↓              ↓
    6. Ship it!    Back to step 3 (re-evaluate)
```

**Stop iterating when:**
- Evaluation scores ≥8/10 consistently across all scenarios
- Cost of improvement > benefit (diminishing returns)
- Skill meets production-ready criteria

## Production-Ready Evaluation Checklist

Before calling your skill "done," verify:

- [ ] 5+ evaluation scenarios defined (baseline, happy, edge, failure, ambiguous)
- [ ] Baseline comparison documented (shows skill adds value)
- [ ] Happy path scores ≥9/10 consistently
- [ ] Edge cases handled gracefully (≥7/10)
- [ ] Failure cases fail safely (no incorrect behavior)
- [ ] Ambiguous cases disambiguate intelligently
- [ ] Overall improvement ≥3 points vs. baseline across scenarios
- [ ] At least 3 quantitative metrics improved
- [ ] Documentation reflects actual behavior (not aspirational)

---

**Remember:** Evaluations aren't bureaucracy—they're your defense against building the wrong thing. Start with evaluations, build minimally, let data drive expansion.
