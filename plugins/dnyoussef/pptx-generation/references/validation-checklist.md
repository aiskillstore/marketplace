# Validation Checklist

Comprehensive validation procedures for PowerPoint decks. Use this checklist after generation, before delivery.

## Automated Validation

These checks can be performed programmatically or through systematic measurement.

### Contrast Ratio Validation

**Requirement**: All text must have minimum 4.5:1 contrast ratio against its background.

**Process**:
1. Identify all text elements and their backgrounds
2. Calculate contrast ratio using formula:
   ```
   Contrast Ratio = (L1 + 0.05) / (L2 + 0.05)
   where L = relative luminance (0-1 scale)
   ```
3. Verify each ratio ≥ 4.5:1
4. Document any failures with specific slide numbers

**Common failures**:
- Dark blue text on medium blue background
- Gray text on white background  
- Colored text on colored accent sections

**Fixes**:
- Darken text or lighten background
- Use black/dark gray text for maximum contrast
- Test at multiple color combinations before committing

### Font Size Validation

**Requirements**:
- Body text: ≥18pt minimum
- Titles: ≥24pt minimum
- Captions/notes: ≥16pt minimum (if used)

**Process**:
1. Check title slide: Title should be ≥24pt
2. Sample 3-5 content slides: Body text should be ≥18pt
3. Check any captions or notes: Should be ≥16pt
4. Document any violations

**Common failures**:
- Chart labels too small (14pt or less)
- Footnotes/sources below minimum
- Dense slides with reduced font sizes to fit content

**Fixes**:
- Increase font size, reduce content if necessary
- Simplify charts to use fewer labels
- Split dense slides into multiple slides

### Margin Measurements

**Requirement**: ≥0.5" minimum margins on all sides (top, bottom, left, right)

**Process**:
1. Select sample slides (corners, edges, and center sections)
2. Measure distance from text/elements to slide edge
3. Verify all measurements ≥0.5"
4. Check both text and visual elements

**Common failures**:
- Titles too close to top edge
- Bullet points extending to right edge
- Chart elements touching bottom edge

**Fixes**:
- Add explicit margin requirements to design plan
- Reduce content to fit within margins
- Check margins during generation, not after

### Element Overlap Detection

**Requirement**: No overlapping text elements

**Process**:
1. Review each slide systematically
2. Check for text-on-text overlaps
3. Check for text overlapping visual elements
4. Verify all elements have clear visual separation

**Common failures**:
- Title overlapping subtitle
- Bullet points overlapping chart legends
- Text bleeding into adjacent sections

**Fixes**:
- Increase spacing between elements
- Reduce element sizes to create separation
- Reorganize layout to prevent crowding

### Bullet Count Verification

**Requirement**: Maximum 3 bullets per slide

**Process**:
1. Count bullets on each content slide
2. Document any slides exceeding limit
3. Verify sub-bullets (if any) are justified

**Common failures**:
- "Summary" slides with 5-7 bullets
- Slides trying to cover too much content
- Lists of items that should be split across multiple slides

**Fixes**:
- Split content across multiple slides
- Condense points into fewer, stronger bullets
- Use visual elements to replace some bullets

### Design Restriction Compliance

**Requirements**:
- Zero border boxes around text elements
- Zero outline shapes containing text content
- Zero rounded rectangles with text inside
- All text on backgrounds or solid color areas
- No decorative borders or frames

**Process**:
1. Review each slide visually
2. Identify any prohibited elements
3. Check edge cases (charts, diagrams, special slides)
4. Document all violations

**Common failures**:
- Chart legends in border boxes
- Callout text in outline shapes
- Section headers in rounded rectangles
- Automatic PowerPoint text containers

**Fixes**:
- Regenerate slides with explicit prohibition emphasis
- Replace containers with background color blocks
- Use spacing for separation, not borders

## Manual Validation

These checks require human judgment and cannot be fully automated.

### Thumbnail Readability Test

**Requirement**: Content should be readable at thumbnail size (~25% of full size)

**Process**:
1. View slides at 25% zoom or thumbnail view
2. Attempt to read titles and key points
3. Verify visual hierarchy is clear at small size
4. Check that charts/visuals are interpretable

**Pass criteria**:
- Titles clearly readable
- Main points identifiable
- Overall structure apparent
- Visual elements recognizable

**Fail indicators**:
- Text too small to read
- Visual hierarchy unclear
- Charts indistinguishable
- Slides look like gray blocks

**Fixes**:
- Increase font sizes
- Simplify visual hierarchy
- Reduce content density
- Use more visual contrast

### Visual Consistency Check

**Requirement**: Consistent visual styling across all slides

**Process**:
1. Review 3-4 slides from each section
2. Compare color usage across sections
3. Verify typography consistency
4. Check spacing patterns

**Consistency elements**:
- Color palette used uniformly
- Font families consistent
- Title sizing uniform
- Bullet spacing identical
- Accent usage predictable
- Background colors appropriate

**Inconsistency indicators**:
- Different blue shades across sections
- Varying title sizes
- Inconsistent spacing between slides
- Random accent color changes

**Fixes**:
- Reference master design plan
- Regenerate inconsistent sections
- Create style guide for future maintenance

### Narrative Flow Check

**Requirement**: Logical progression from beginning to end

**Process**:
1. Read slide titles in sequence
2. Verify story arc (beginning → middle → end)
3. Check for logical transitions
4. Confirm conclusions follow from evidence

**Flow elements**:
- Clear introduction establishing context
- Logical progression of ideas
- Supporting evidence for claims
- Natural transitions between sections
- Compelling conclusion

**Flow problems**:
- Jumping between topics randomly
- Missing logical connections
- Conclusions not supported by slides
- Repetitive or circular content

**Fixes**:
- Reorder slides for better flow
- Add transition slides if needed
- Remove redundant content
- Strengthen logical connections

### Data Accuracy Verification

**Requirement**: All data accurate to source materials

**Process**:
1. Select sample of quantitative claims
2. Trace back to source data
3. Verify calculations are correct
4. Check that context is preserved

**Verification points**:
- Numbers match source data
- Calculations are correct
- Percentages accurately computed
- Trends correctly characterized
- Context not misleading

**Common errors**:
- Transcription errors
- Calculation mistakes
- Missing context
- Misleading comparisons
- Outdated data

**Fixes**:
- Regenerate slides with data errors
- Add source citations for verification
- Include data validation in generation prompt

### Accessibility Beyond Contrast

**Requirements**:
- Color not sole means of conveying information
- Alt text for visual elements
- Logical reading order
- No flashing/animated elements

**Process**:
1. Identify information conveyed by color only
2. Check for alt text on charts/images
3. Verify reading order makes sense
4. Ensure no problematic animations

**Accessibility issues**:
- "Red means bad, green means good" without labels
- Charts without axis labels
- Visual-only information
- Illogical reading order
- Distracting animations

**Fixes**:
- Add labels or text alongside color coding
- Include descriptive chart labels
- Structure content for logical reading order
- Remove or simplify animations

## Validation Workflow

### For Simple Decks

1. Run automated validation immediately after generation
2. Fix any automated validation failures
3. Perform manual validation checks
4. Address manual validation issues
5. Final review against design plan
6. Approve for delivery

### For Complex Decks

**After each Generator chat**:
1. Run automated validation on section
2. Fix section-specific issues
3. Quick manual review of section
4. Approve section before proceeding

**After Assembly chat**:
1. Run automated validation on complete deck
2. Perform comprehensive manual validation
3. Check cross-section consistency
4. Verify narrative flow across sections
5. Final data accuracy spot-checks
6. Approve for delivery

## Failure Response Protocol

### When Validation Fails

**DO NOT**:
- Apply band-aid fixes without understanding root cause
- Regenerate entire deck for isolated issues
- Skip validation steps to save time
- Ignore "minor" violations

**DO**:
1. Identify specific failure mode
2. Determine root cause (refer to design principles)
3. Choose appropriate fix:
   - Simple error → Quick manual fix
   - Systematic problem → Regenerate with updated prompt
   - Design plan issue → Revise plan and regenerate affected sections
4. Re-validate after fix
5. Update skill if new failure mode discovered

### Severity Classification

**Critical** (Must fix before delivery):
- Contrast ratio violations
- Data accuracy errors
- Major narrative flow problems
- Overlapping/unreadable text

**High** (Should fix before delivery):
- Font size violations
- Margin measurement failures
- Visual inconsistencies
- Missing elements

**Medium** (Fix if time permits):
- Minor spacing irregularities
- Suboptimal color choices
- Aesthetic improvements
- Nice-to-have additions

**Low** (Document for future):
- Personal preference items
- Minor wording changes
- Alternative approaches
- Future enhancements

## Validation Report Template

Document validation results for record-keeping and continuous improvement.

```
VALIDATION REPORT
Deck: [Name]
Date: [Date]
Validator: [Name]
Total Slides: [Count]

AUTOMATED VALIDATION:
□ Contrast ratios: PASS / FAIL
  - Failures: [List slide numbers and specific issues]
□ Font sizes: PASS / FAIL
  - Violations: [Details]
□ Margins: PASS / FAIL
  - Violations: [Details]
□ Element overlaps: PASS / FAIL
  - Issues: [Details]
□ Bullet counts: PASS / FAIL
  - Violations: [Details]
□ Design restrictions: PASS / FAIL
  - Violations: [Details]

MANUAL VALIDATION:
□ Thumbnail readability: PASS / FAIL
  - Issues: [Details]
□ Visual consistency: PASS / FAIL
  - Inconsistencies: [Details]
□ Narrative flow: PASS / FAIL
  - Flow issues: [Details]
□ Data accuracy: PASS / FAIL
  - Errors: [Details]
□ Accessibility: PASS / FAIL
  - Issues: [Details]

OVERALL STATUS: APPROVED / REQUIRES FIXES

FIXES APPLIED:
[List fixes and results]

LESSONS LEARNED:
[Notes for future improvements]

APPROVED BY: [Name]
APPROVAL DATE: [Date]
```

## Continuous Improvement

Use validation results to improve future generations:

### Pattern Recognition

Track common validation failures:
- Which requirements most frequently violated?
- Which slides most error-prone?
- Which data sources cause issues?
- Which visual elements problematic?

### Skill Updates

When patterns emerge:
1. Identify root cause
2. Formulate additional constraint
3. Update design restrictions
4. Test on historical failures
5. Incorporate into skill

### Process Refinement

Optimize validation process:
- Automate more checks where possible
- Create slide-specific checklists
- Develop quick-check procedures
- Build validation into generation workflow

## Conclusion

Validation is not optional quality check—it's integral to PowerPoint generation workflow. The goal is zero-defect delivery, achieved through:

- Comprehensive automated checks
- Systematic manual validation
- Structured failure response
- Continuous improvement

**Remember**: Time spent on validation prevents rework, ensures accessibility, maintains quality standards, and builds confidence in AI-generated outputs.
