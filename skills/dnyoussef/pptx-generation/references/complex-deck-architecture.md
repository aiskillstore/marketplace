# Complex Deck Architecture

Use this multi-chat approach for presentations with 30+ slides where visual elements will exhaust the context window in a single conversation.

## Why Multi-Chat Architecture?

**Problem**: Visual/spatial tasks consume tokens faster than pure text or data processing. Beyond ~15 slides, single-context generation becomes unreliable due to:
- Context window exhaustion mid-generation
- Loss of consistency in later slides
- Inability to maintain design plan throughout
- Tool degradation more likely as context fills

**Solution**: Separate concerns across multiple AI conversations, each focused on specific phase with manageable scope.

## Architecture Overview

```
CHAT 1: Architect
↓ (outputs: narrative structure, slide outline, master design plan)
CHAT 2-N: Generators  
↓ (outputs: slide sections of 10-15 slides each)
CHAT N+1: Assembly
↓ (outputs: final compiled deck with consistency validation)
```

## Chat 1: Architect Phase

**Purpose**: Establish narrative structure and master design plan without generating actual slides.

**Inputs**: All data sources, presentation objectives, audience requirements, constraints

**Process**:

1. **Analyze all data sources comprehensively**
   - Extract key insights
   - Identify patterns and themes
   - Note data quality issues or gaps
   
2. **Define narrative structure**
   - Establish story arc (problem → analysis → solution)
   - Identify major sections
   - Determine logical flow between sections
   
3. **Create detailed slide outline**
   - Specify content for each slide
   - Note data sources per slide
   - Identify visual emphasis points
   - Flag complex slides needing special attention
   
4. **Generate master design plan**
   - Layout philosophy
   - Complete color palette with hex codes
   - Typography system (families, sizes, line spacing)
   - Visual emphasis strategy
   - Explicit statement of design restrictions compliance

**Outputs** (saved for subsequent chats):
- `narrative_structure.md`: Story arc and section breakdown
- `slide_outline.md`: Slide-by-slide content specifications
- `master_design_plan.md`: Complete visual system specification

**Validation before proceeding**:
- Design plan explicitly addresses all design restrictions
- Slide outline totals to expected deck length
- Narrative structure has clear beginning/middle/end
- Each slide has clear purpose in overall story

### Architect Prompt Template

```
You are designing the architecture for a [LENGTH]-slide executive presentation. 
Your task is to analyze data, structure narrative, and create a master design plan 
WITHOUT generating actual slides.

[DATA SOURCES]
[List all files with descriptions]

[PRESENTATION OBJECTIVES]
[Specific goals and audience]

[CONSTRAINTS]
[Any specific requirements or limitations]

TASK 1: DATA ANALYSIS
Analyze all data sources. Extract key insights, patterns, and themes. Note any 
data quality issues. Create a structured summary of findings.

TASK 2: NARRATIVE STRUCTURE  
Design the story arc. How should this presentation flow? What major sections 
are needed? What logical progression will be most compelling?

TASK 3: DETAILED SLIDE OUTLINE
Create a slide-by-slide outline specifying:
- Slide number and title
- Key content points
- Data sources to use
- Visual emphasis strategy
- Complexity notes

TASK 4: MASTER DESIGN PLAN
Create a comprehensive visual system including:
- Layout philosophy (spacing, positioning, hierarchy)
- Color palette (exact hex codes, contrast ratios, usage rules)
- Typography system (families, sizes for titles/headers/body/captions)
- Visual emphasis strategy (how priority translates to visual weight)
- Explicit confirmation of design restrictions compliance:
  * NO BORDER BOXES around text
  * NO OUTLINE SHAPES containing text
  * NO ROUNDED RECTANGLES with text
  * Text directly on backgrounds
  * Spacing for separation (not containers)

OUTPUT FORMAT:
Save three separate documents:
1. narrative_structure.md
2. slide_outline.md  
3. master_design_plan.md

Do NOT generate actual slides in this phase.
```

## Chat 2-N: Generator Phase(s)

**Purpose**: Generate actual slide sections of 10-15 slides, maintaining consistency with master design plan.

**Inputs per Chat**: 
- Master design plan (from Architect)
- Slide outline for THIS section only
- Original data sources
- Previous section's final slide (for continuity)

**Process**:

1. **Load master design plan**
   - Review all visual specifications
   - Confirm understanding of restrictions
   
2. **Select section scope**
   - Typically 10-15 slides
   - Complete logical section (don't split mid-section)
   
3. **Enforce html2pptx workflow**
   - Explicitly state workflow requirement
   - Prevent tool degradation
   
4. **Generate section slides**
   - Follow master design plan strictly
   - Implement slide outline specifications
   - Maintain consistency with previous sections
   
5. **Validate section**
   - Visual consistency with design plan
   - No design restriction violations
   - Data accuracy
   - Narrative continuity

**Outputs**: Section file (slides X through Y)

**Before starting next generator chat**:
- Validate section passes all checks
- Note any design plan refinements needed
- Confirm section connects logically to next section

### Generator Prompt Template

```
You are generating slides [START] through [END] of a [TOTAL]-slide presentation. 
You must strictly follow the master design plan and slide outline provided.

[MASTER DESIGN PLAN]
[Paste complete master_design_plan.md content]

[SLIDE OUTLINE FOR THIS SECTION]  
[Paste relevant section from slide_outline.md]

[DATA SOURCES]
[List files, same as Architect chat]

[PREVIOUS SECTION CONTEXT]
[If not first section: summary of previous section's conclusion for continuity]

WORKFLOW ENFORCEMENT:
Use html2pptx workflow only. Debug any installation issues; do not switch to 
alternative approaches. Confirm you will use html2pptx before proceeding.

DESIGN RESTRICTIONS (CRITICAL):
• NO BORDER BOXES around text elements
• NO OUTLINE SHAPES containing text content
• NO ROUNDED RECTANGLES with text inside
• Text sits directly on slide background or solid color areas
• Visual separation through spacing and typography only

GENERATION REQUIREMENTS:
1. Review master design plan completely
2. Confirm html2pptx workflow
3. Generate slides [START] through [END] following specifications exactly
4. Validate section against design plan
5. Verify no design restrictions violated

After generation, validate:
• Contrast ratios ≥4.5:1
• Font sizes meet minimums (18pt/24pt)
• Margins ≥0.5"
• Zero border boxes/outline shapes
• Maximum 3 bullets per slide
• Visual consistency with design plan

OUTPUT: PowerPoint file with slides [START]-[END]
```

## Chat N+1: Assembly Phase

**Purpose**: Compile all sections, ensure consistency across complete deck, final validation.

**Inputs**: 
- All section files from generator chats
- Master design plan
- Complete slide outline

**Process**:

1. **Compile sections**
   - Merge all section files in order
   - Verify no slides missing or duplicated
   
2. **Cross-section consistency check**
   - Visual consistency across section boundaries
   - Color palette used consistently
   - Typography system applied uniformly
   - Narrative flow maintains coherence
   
3. **Comprehensive validation**
   - Run complete validation checklist
   - Verify against master design plan
   - Check data accuracy across all slides
   - Confirm narrative arc completeness
   
4. **Identify issues**
   - Note specific slides with problems
   - Categorize issues (visual, content, data)
   - Determine whether regeneration needed
   
5. **Targeted regeneration (if needed)**
   - Regenerate ONLY problematic slides
   - Maintain surrounding context
   - Revalidate after changes

**Output**: Final compiled deck ready for delivery

### Assembly Prompt Template

```
You are assembling and validating a [TOTAL]-slide presentation from multiple 
section files. Your task is to ensure consistency and quality across the complete deck.

[MASTER DESIGN PLAN]
[Paste complete master_design_plan.md content]

[SECTION FILES]  
• Section 1: slides 1-15 (filename)
• Section 2: slides 16-30 (filename)
• Section 3: slides 31-45 (filename)
[List all sections]

TASK 1: COMPILATION
Merge all section files in order. Verify:
• All slides present (1 through [TOTAL])
• No duplicates or gaps
• Section transitions maintain continuity

TASK 2: CONSISTENCY VALIDATION
Check across complete deck:
• Visual consistency (colors, fonts, spacing)
• Color palette used uniformly
• Typography system applied consistently
• Narrative flow coherent from start to finish
• Design restrictions honored throughout

TASK 3: COMPREHENSIVE VALIDATION CHECKLIST
□ All text contrast ratios ≥4.5:1 (spot check multiple slides)
□ All font sizes ≥18pt body / ≥24pt titles
□ All margins ≥0.5" (measure multiple slides)
□ Zero border boxes anywhere in deck
□ Zero outline shapes anywhere in deck
□ Maximum 3 bullets per slide (check all)
□ No overlapping text elements
□ Thumbnail readability (test sample slides)
□ Data accuracy (verify against sources)
□ Narrative completeness (beginning/middle/end)

TASK 4: ISSUE IDENTIFICATION
If validation fails, identify:
• Specific slide numbers with issues
• Issue categories (visual/content/data)
• Root causes (not symptoms)
• Whether regeneration needed

TASK 5: TARGETED FIXES (if needed)
• Regenerate ONLY problematic slides
• Maintain consistency with surrounding slides
• Revalidate after changes
• Do NOT regenerate entire deck for isolated issues

OUTPUT: Final compiled PowerPoint file
```

## State Management Between Chats

**Critical**: Each generator chat must have access to:
- Complete master design plan
- Relevant section of slide outline
- Summary of previous section (for continuity)

**Best Practice**: Maintain a state document tracking:
```
PROJECT: [Deck name]
TOTAL SLIDES: [Number]
STATUS: [Phase - Architect/Generate/Assembly]

COMPLETED:
✓ Architect chat (narrative_structure.md, slide_outline.md, master_design_plan.md)
✓ Generator chat 1: Slides 1-15 (section1.pptx)
✓ Generator chat 2: Slides 16-30 (section2.pptx)
⧗ Generator chat 3: Slides 31-45 (in progress)
☐ Assembly chat: Final compilation (pending)

NOTES:
- Section 1-2 transition validated successfully
- Design plan note: Accent blue works well, maintaining for section 3
- Data issue in slide 23: Resolved with updated source file

NEXT STEP: Complete generator chat 3, then move to assembly
```

## Decision Tree: When to Use Multi-Chat

```
Is deck >15 slides? 
  ├─ NO → Use simple deck workflow (single chat)
  └─ YES → Is deck >30 slides?
       ├─ NO → Consider single chat with careful token management
       └─ YES → Use multi-chat architecture (mandatory)
```

**Additional considerations for multi-chat**:
- Complex data integration from 5+ sources → Multi-chat
- Brand guidelines requiring extensive visual documentation → Multi-chat  
- Multiple distinct narrative sections → Multi-chat
- Board presentation where quality is critical → Multi-chat (even if <30 slides)

## Benefits of Multi-Chat Architecture

1. **Context window management**: Each chat operates within comfortable token limits
2. **Section-level iteration**: Fix sections without regenerating entire deck
3. **Focused expertise**: Each phase optimizes for its specific task
4. **Reduced failure risk**: Smaller generation units = fewer points of failure
5. **Better consistency**: Master design plan referenced throughout, not buried in context
6. **Scalability**: Architecture scales to 50, 75, 100+ slide decks

## Common Pitfalls

❌ **Skipping architect phase**: Jumping directly to generation without narrative structure
❌ **Inconsistent design plans**: Not referencing master design plan in generator chats
❌ **Over-sized sections**: Generating 20+ slides in single generator chat
❌ **No validation between sections**: Discovering issues only at assembly phase
❌ **Complete regeneration for small issues**: Regenerating entire deck instead of targeted fixes

## Validation Gates Summary

**After Architect Chat**:
- [ ] Design plan addresses all restrictions explicitly
- [ ] Slide outline totals to expected length
- [ ] Narrative structure has clear arc

**After Each Generator Chat**:
- [ ] Section visually consistent with design plan
- [ ] No design restrictions violated
- [ ] Section connects to previous section

**After Assembly Chat**:
- [ ] All slides present and in order
- [ ] Visual consistency across complete deck
- [ ] Comprehensive validation checklist passed
- [ ] Narrative arc complete and coherent
