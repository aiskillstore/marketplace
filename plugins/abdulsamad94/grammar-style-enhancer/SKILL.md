---
name: grammar-style-enhancer
description: Analyzes prose for grammar errors, style inconsistencies, clarity issues, and readability problems. Provides specific suggestions for improvement while preserving the author's unique voice. Use when the user needs help polishing their writing, improving clarity, or maintaining consistent style.
---

# Grammar and Style Enhancer

## Purpose

This skill helps authors refine their prose by identifying grammar errors, style inconsistencies, weak constructions, and clarity issues. It provides actionable suggestions that improve readability while respecting and preserving the author's unique voice.

## When to Use

- User wants to polish a completed draft
- User needs help with grammar and punctuation
- User wants to improve sentence variety and rhythm
- User is concerned about passive voice or weak verbs
- User needs consistency checking (tense, POV, spelling)
- User wants to enhance clarity and conciseness
- User requests style analysis or readability assessment

## Instructions

### Step 1: Establish Parameters

Ask the user:

- **Text to Analyze**: Specific passage, chapter, or full manuscript
- **Genre**: Literary fiction, genre fiction, non-fiction, academic, etc.
- **Target Audience**: Adult, YA, middle grade, academic readers
- **Style Preferences**: Formal/casual, verbose/concise, complex/simple
- **Specific Concerns**: Any particular issues they've noticed or want addressed
- **Voice Preservation**: How important is maintaining their exact style vs. optimization?

### Step 2: Multi-Level Analysis Framework

Analyze the text across these dimensions:

#### A. Grammar and Mechanics

- Subject-verb agreement
- Pronoun agreement and clarity
- Verb tense consistency
- Comma splices and run-ons
- Sentence fragments (distinguish stylistic from errors)
- Apostrophe and quotation mark usage
- Capitalization
- Spelling and homophones

#### B. Clarity and Concision

- Redundancy and wordiness
- Vague or ambiguous phrasing
- Unclear antecedents
- Dangling or misplaced modifiers
- Overly complex sentences
- Jargon or unexplained terms

#### C. Style and Voice

- Passive vs. active voice
- Weak verbs (is, was, has, etc.)
- Telling vs. showing
- Sentence variety (length and structure)
- Rhythm and pacing
- Repetitive sentence starts
- Clichés and overused phrases
- Word choice (precision and impact)

#### D. Consistency

- Tense shifts (unless intentional)
- POV consistency
- Spelling variants (theater/theatre, grey/gray)
- Formatting (em dashes, ellipses, etc.)
- Character name/description consistency

#### E. Readability

- Average sentence length
- Paragraph length
- Reading level (Flesch-Kincaid)
- Flow and transitions between ideas

### Step 3: Generate Enhancement Report

Present findings in this structured format:

```markdown
# Grammar and Style Enhancement Report

## Text Analyzed

**Word Count**: [X,XXX]
**Paragraph Count**: [XX]
**Average Sentence Length**: [XX words]
**Estimated Reading Level**: [Grade level]
**Genre**: [Genre]

---

## Executive Summary

- **Grammar Errors**: [X] (Critical: [Y])
- **Style Opportunities**: [X] (High-impact: [Y])
- **Consistency Issues**: [X]
- **Overall Prose Quality**: [X/10]
- **Primary Strength**: [What's working well]
- **Primary Opportunity**: [Biggest area for improvement]

---

## Critical Grammar Errors

### 1. [Error Type]

**Original**: "[Quote from text with error]"
**Issue**: [Explanation of what's wrong]
**Corrected**: "[Suggested fix]"
**Rule**: [Brief grammar rule explanation]

---

## Style Enhancement Opportunities

### High-Impact Changes

#### 1. Passive Voice → Active Voice

**Original**: "The door was opened by Sarah."
**Suggested**: "Sarah opened the door."
**Why**: Active voice is more direct and engaging; strengthens Sarah's agency
**Impact**: Medium - Improves clarity and pacing

#### 2. Weak Verb Strengthening

**Original**: "He was walking very quickly down the street."
**Suggested**: "He hurried down the street." OR "He strode down the street."
**Why**: Stronger verb incorporates the adverb, more concise and vivid
**Impact**: High - More precise and engaging

#### 3. Show, Don't Tell

**Original**: "She was very angry."
**Suggested**: "Her hands clenched into fists, nails biting into her palms."
**Why**: Showing emotion through physical detail is more immersive
**Impact**: High - Engages reader more deeply

---

### Sentence Variety Opportunities

**Issue**: Multiple consecutive sentences start with "The" or subject-verb pattern

**Original**:

> "The sun set over the horizon. I watched it disappear. I felt a sense of peace wash over me. I decided to head home."

**Enhanced**:

> "The sun set over the horizon. As I watched it disappear, peace washed over me. Time to head home."

**Why**: Varying sentence structure improves rhythm and readability

---

## Clarity Issues

### 1. Unclear Antecedent

**Original**: "Mark told Jason he needed to leave."
**Issue**: Who needs to leave? Mark or Jason? "He" is ambiguous.
**Suggested Options**:

- "Mark told Jason, 'You need to leave.'" (Jason leaves)
- "Mark told Jason, 'I need to leave.'" (Mark leaves)
- "Mark needed to leave, so he told Jason." (Mark leaves)
  **Impact**: Critical - Changes meaning of the scene

### 2. Dangling Modifier

**Original**: "Walking down the street, the trees looked beautiful."
**Issue**: Trees aren't walking; the subject is missing/misplaced.
**Corrected**: "Walking down the street, I noticed the beautiful trees."
**Impact**: Moderate - Sounds awkward but meaning usually clear from context

---

## Consistency Issues

### 1. Tense Shift

**Location**: Paragraph 3, sentences 2-4
**Issue**: Shifts from past tense to present tense mid-paragraph
**Original**:

> "She walked to the door. She opens it and sees a stranger standing there."
> **Corrected**:
> "She walked to the door. She opened it and saw a stranger standing there."
> **Note**: Unless using historical present tense intentionally, maintain past tense

### 2. Spelling Variants

**Issue**: Inconsistent spelling throughout text
**Found**: "gray" (4 times) and "grey" (2 times)
**Recommendation**: Choose one and apply consistently (American English = gray, British = grey)

---

## Word Choice Enhancements

### Imprecise → Precise

| Original       | Enhanced                                    | Why                               |
| -------------- | ------------------------------------------- | --------------------------------- |
| "very big"     | "enormous" / "massive" / "towering"         | More specific and vivid           |
| "said loudly"  | "shouted" / "yelled" / "bellowed"           | Stronger verb incorporates adverb |
| "kind of sad"  | "melancholy" / "wistful" / "dejected"       | More precise emotion              |
| "walked sadly" | "trudged" / "shuffled" / "dragged her feet" | Conveys emotion through action    |

---

## Repetition Analysis

### Overused Words

| Word       | Frequency | Recommendation                                                   |
| ---------- | --------- | ---------------------------------------------------------------- |
| "very"     | 23 times  | Reduce by 80%; replace with stronger words                       |
| "just"     | 18 times  | Often unnecessary filler; remove in most cases                   |
| "really"   | 15 times  | Adds little meaning; remove or use stronger word                 |
| "suddenly" | 12 times  | Overused in this passage; vary or show suddenness through action |

### Repetitive Sentence Starts

- "She [verb]" - 15 sentences
- "The [noun]" - 12 sentences
- "I [verb]" - 10 sentences

**Recommendation**: Vary sentence structure by starting with:

- Dependent clauses: "As the door opened, she..."
- Prepositional phrases: "With trembling hands, she..."
- Adverbs: "Slowly, she..."
- Participial phrases: "Gripping the railing, she..."

---

## Readability Metrics

**Current Statistics**:

- Average sentence length: 18 words
- Average paragraph length: 4 sentences
- Flesch Reading Ease: 72 (target: 60-70 for adult fiction)
- Flesch-Kincaid Grade Level: 8.2

**Assessment**:
Readability is good for general adult fiction. If targeting literary fiction, could increase complexity. If targeting middle grade, should simplify further.

---

## Paragraph-Level Analysis

### Sample Paragraph Review

**Original**:

> "The house was old. It was really falling apart. Paint was peeling off the walls. The roof was sagging. Windows were broken. I didn't want to go in, but I had to. The door creaked when I opened it. Inside was dark and smelled musty."

**Issues**:

- Choppy: 8 sentences, all simple subject-verb structure
- Repetitive: All sentences start similarly
- Weak verbs: "was" appears 4 times
- Telling: States facts without creating atmosphere
- No variety in sentence length

**Enhanced Version**:

> "The house was falling apart. Paint peeled from the walls in long, papery strips, and the roof sagged like an old spine. Broken windows gaped like missing teeth. I didn't want to go in—every instinct screamed against it—but I had no choice. The door creaked open, releasing a wave of musty air that spoke of decades of abandonment."

**Improvements**:

- Varied sentence structure (simple, compound, complex)
- Stronger verbs (peeled, gaped, screamed)
- Showing through vivid comparisons (similes)
- Combines related ideas for better flow
- Creates atmosphere, not just description
- Maintained 3 sentences instead of 8 without losing information

---

## Voice Preservation Notes

**Author's Strengths** (preserve these):

- Strong dialogue tags and character voice
- Effective use of sensory details
- Good pacing in action scenes
- Unique metaphors and comparisons

**Author's Style Markers** (maintain):

- Tendency toward shorter paragraphs (works for pacing)
- Conversational tone in narration
- Occasional sentence fragments for emphasis (stylistic choice)

**Recommendation**:
The suggested edits focus on technical errors and clarity while preserving your conversational, fast-paced style. The fragments and occasional informal language are features, not bugs, for this genre.

---

## Priority Action Items

### Must Fix (Affects Clarity/Correctness)

1. Fix unclear antecedents (3 instances marked)
2. Correct tense shifts (paragraph 3, 7, 12)
3. Resolve subject-verb disagreement (2 instances)

### High Impact (Significantly Improves Prose)

4. Replace passive voice in action scenes (15 instances)
5. Strengthen weak verbs in key emotional moments (22 instances)
6. Remove/replace filler words "very," "really," "just" (56 total)

### Polish (Fine-tuning)

7. Vary sentence structure in descriptive passages
8. Replace repeated words with synonyms
9. Enhance word precision in character descriptions

---

## Comparison Example: Before and After

**Original Passage** (200 words):

> [Full original text]

**Issues Summary**:

- Grammar errors: 3
- Passive voice: 5 instances
- Weak verbs: 12 instances
- Repetitive structure: 8 sentences start with "The" or "I"
- Wordiness: ~20 unnecessary words

**Enhanced Passage** (180 words):

> [Revised text with changes highlighted]

**Changes Made**:

- ~~"was walking"~~ → **"walked"** (tense consistency)
- ~~"very scared"~~ → **"terrified"** (stronger word choice)
- ~~"The door was opened by her"~~ → **"She opened the door"** (active voice)
- Combined short choppy sentences for better flow
- Removed filler words ("really," "just," "very")

**Result**:

- 10% reduction in word count without losing content
- Improved clarity and pacing
- Maintained author's voice
- Eliminated technical errors

---

## Global Style Recommendations

Based on this sample, consider these manuscript-wide improvements:

1. **Active Voice in Action**: Use passive voice sparingly; prefer active voice especially in action scenes
2. **Verb Strength**: Audit "to be" verbs (is, was, were) and replace 50% with stronger alternatives
3. **Sentence Variety**: Aim for mix of simple, compound, and complex sentences
4. **Adverb Audit**: Replace adverb+weak verb with strong verb ("walked quickly" → "hurried")
5. **Filler Words**: Search and destroy most instances of "very," "really," "just"
6. **Showing Emotions**: Replace telling ("she was angry") with physical manifestations 60% of the time
7. **Repetition**: Use Find to identify overused words; vary vocabulary
8. **Paragraph Rhythm**: Mix short punchy paragraphs with longer descriptive ones

---

## Genre-Specific Style Notes

**[Based on user's specified genre]**

For **[Genre]**, readers expect:

- [Style element 1]
- [Style element 2]
- [Style element 3]

**Your text aligns with genre expectations in**:

- [Alignment 1]
- [Alignment 2]

**Consider adjusting**:

- [Adjustment 1]
- [Adjustment 2]
```

## Examples

### Example 1: Fiction Passage Enhancement

**User**: "Can you help me improve this paragraph? It feels weak but I can't figure out why."

**User's Text**:

> "Sarah was walking down the hallway. The hallway was very dark. She was scared. She heard a noise behind her. She turned around quickly. There was nothing there. She kept walking. Her heart was beating very fast."

**Output**:

```markdown
# Grammar and Style Enhancement Report

## Analysis Summary

**Word Count**: 43
**Sentence Count**: 8
**Average Sentence Length**: 5.4 words (very short)
**Issues Found**: 12

---

## Why It Feels Weak

### Primary Issues:

1. **Monotonous Structure**: All 8 sentences follow identical subject-verb pattern
2. **Weak Verbs**: "was" appears 5 times
3. **Choppy Rhythm**: Every sentence is very short (3-8 words)
4. **Telling Instead of Showing**: States facts ("she was scared") instead of creating fear
5. **Overuse of "very"**: Adds little meaning (2 instances in 43 words)
6. **Passive Construction**: "was walking" instead of "walked"

---

## Enhanced Version

**Option 1: Moderate Enhancement** (maintains simplicity, fixes issues)

> "Sarah walked down the dark hallway, her breath coming in short gasps. A noise echoed behind her. She spun around—nothing. Her heart hammered against her ribs as she forced herself forward."

**Changes Made**:

- Combined related ideas (hallway + description)
- Active voice ("walked" not "was walking")
- Removed "very"
- Showed fear through physical details (breath, spinning, heart hammering)
- Varied sentence length (14, 5, 3, 16 words)
- Stronger verbs (echoed, spun, hammered)
- **Word count**: 32 (25% more concise)

---

**Option 2: Atmospheric Enhancement** (more literary, builds tension)

> "Darkness swallowed the hallway. Sarah's footsteps echoed too loud in the silence, each breath catching in her throat. The noise behind her—sudden, sharp—froze her mid-step. She whirled around. Nothing but shadows. She walked faster, her heart a frantic drum against her ribs."

**Changes Made**:

- More immersive and atmospheric
- Varied sentence structure (fragment, complex, simple)
- Strong sensory details (sound, sight, physical sensation)
- Creates more tension through pacing and word choice
- Shows fear through action and physiological response
- **Word count**: 48 (slightly longer but much more engaging)

---

**Option 3: Urgent/Thriller Enhancement** (fast-paced, genre fiction)

> "The dark hallway stretched endlessly ahead. Sarah ran. A crash behind her—she spun, fists raised. Nothing. Just darkness and the thundering of her own heart. Move. Move. She ran faster."

**Changes Made**:

- Very short sentences for pacing and urgency
- Fragments for effect ("Move. Move.")
- Active, urgent verbs (ran, spun, raised, thundering)
- Eliminates unnecessary details
- Creates immediate tension
- **Word count**: 35

---

## Technical Breakdown

### Original Sentence Structure Analysis:

1. "Sarah was walking..." - Subject + was + gerund
2. "The hallway was..." - Subject + was + adjective
3. "She was scared." - Subject + was + adjective
4. "She heard..." - Subject + verb
5. "She turned..." - Subject + verb + adverb
6. "There was..." - There + was
7. "She kept..." - Subject + verb
8. "Her heart was..." - Subject + was + gerund

**Problem**: 8/8 sentences have identical structure. Brain recognizes pattern and disengages.

### Enhanced Structure Variety:

- Opening with noun/description
- Short action sentence
- Fragment for impact
- Compound sentence
- Sensory detail woven in
- Varying length (3 to 16 words)

**Result**: Unpredictability keeps reader engaged.

---

## Specific Edits Explained

### "was walking" → "walked"

**Why**: Progressive tense (was walking) creates distance. Simple past (walked) is more immediate and active.

### "very dark" → "dark" OR "darkness swallowed"

**Why**: "Very" is a weak intensifier. Either trust "dark" alone or use stronger description.

### "She was scared" → "her breath coming in short gasps"

**Why**: Showing physical symptoms is more immersive than naming the emotion.

### "very fast" → "hammered" / "frantic drum"

**Why**: Strong verb or vivid metaphor beats adjective + adverb.

### "quickly" → "spun"

**Why**: "Spun" inherently suggests speed; adverb becomes redundant.

---

## Recommendations for Rest of Manuscript

1. **Sentence Length Variety**: Aim for 10-20 word average, but vary significantly (3-30 words)
2. **Paragraph Rhythm**: Mix 1-sentence paragraphs (impact) with 3-5 sentence (description/explanation)
3. **"Was" Audit**: Search your manuscript for "was" + verb-ing; replace 70% with simple past
4. **"Very" Elimination**: Remove 90% of instances; use stronger base words
5. **Emotion Showing**: For every "she was [emotion]", add/replace with physical manifestation
6. **Power Verbs**: Replace weak verbs in key moments (climax, emotional beats)

**Genre-Specific Note**:
If this is thriller/suspense, the short, punchy style of Option 3 might work throughout action scenes. If literary fiction, Option 2's atmospheric approach. If middle grade, Option 1's balance of clarity and engagement.
```

### Example 2: Academic Writing Polish

**User**: "This is for my dissertation introduction. Too informal?"

**User's Text**:

> "Many researchers think that climate change is a really big problem. There have been a lot of studies done on this topic. Some of these studies show that temperatures are rising. Other studies show that ice caps are melting. It is important to study this because it affects everyone."

**Output**:

```markdown
# Academic Style Enhancement Report

## Analysis Summary

**Discipline**: Environmental Science (assumed)
**Document Type**: Dissertation Introduction
**Current Style**: Conversational/Informal
**Target Style**: Academic/Formal

---

## Critical Issues for Academic Writing

### 1. Vague/Informal Language

**Original**: "Many researchers think that climate change is a really big problem."

**Issues**:

- "think" - too casual for academic assertion
- "really big" - imprecise and informal
- "problem" - vague term without specificity
- No citation

**Academic Revision**:

> "Climate change represents one of the most significant environmental challenges of the 21st century (IPCC, 2023)."

**Why Better**:

- Precise language ("significant environmental challenges")
- Removes qualifier "really"
- Adds authoritative citation
- Formal tone

---

### 2. Lack of Specificity

**Original**: "There have been a lot of studies done on this topic."

**Issues**:

- "a lot" - quantify instead
- Passive voice without purpose
- No information value (what did studies show?)
- No citations

**Academic Revision**:

> "Over 15,000 peer-reviewed studies published between 2010-2023 have examined various aspects of anthropogenic climate change (Smith & Jones, 2023)."

**Why Better**:

- Specific numbers
- Time frame provided
- Technical precision ("anthropogenic")
- Citation included
- Active information

---

### 3. Simplistic Structure

**Original**: "Some of these studies show that temperatures are rising. Other studies show that ice caps are melting."

**Issues**:

- Repetitive structure
- Obvious statements that need no citation
- Listed facts without synthesis
- Elementary "some...other" construction

**Academic Revision**:

> "Empirical evidence demonstrates consistent global temperature increases of approximately 1.1°C since pre-industrial times (Hansen et al., 2020), accompanied by accelerated polar ice mass loss averaging 400 billion tons annually (White, 2022)."

**Why Better**:

- Synthesizes findings into single sentence
- Provides specific data points
- Technical vocabulary
- Multiple citations
- Shows relationship between phenomena

---

### 4. Weak Justification

**Original**: "It is important to study this because it affects everyone."

**Issues**:

- "It is important" - weak assertion
- "affects everyone" - vague and obvious
- No scholarly rationale
- No research gap identified

**Academic Revision**:

> "Understanding the socioeconomic impacts of climate change remains critical for developing effective adaptation strategies, particularly for vulnerable populations disproportionately affected by environmental degradation (Brown et al., 2021). Despite extensive research on climate mechanisms, significant gaps remain in our understanding of regional adaptation responses, which this study aims to address."

**Why Better**:

- Specific research value articulated
- Acknowledges existing work
- Identifies research gap
- Positions current study
- Citation included

---

## Complete Revision: Before and After

**Original (Informal)**:

> "Many researchers think that climate change is a really big problem. There have been a lot of studies done on this topic. Some of these studies show that temperatures are rising. Other studies show that ice caps are melting. It is important to study this because it affects everyone."

**Issues Summary**:

- Word count: 52
- Citations: 0
- Vague terms: 6
- Informal qualifiers: 2
- Research gap: Not identified
- Academic tone: 2/10

**Revised (Academic)**:

> "Climate change represents one of the most significant environmental challenges of the 21st century (IPCC, 2023). Over 15,000 peer-reviewed studies published between 2010-2023 have examined various aspects of anthropogenic climate change (Smith & Jones, 2023), providing robust empirical evidence for global temperature increases of approximately 1.1°C since pre-industrial times (Hansen et al., 2020) and accelerated polar ice mass loss averaging 400 billion tons annually (White, 2022). Understanding the socioeconomic impacts of climate change remains critical for developing effective adaptation strategies, particularly for vulnerable populations disproportionately affected by environmental degradation (Brown et al., 2021). Despite extensive research on climate mechanisms, significant gaps remain in our understanding of regional adaptation responses, which this dissertation addresses through a mixed-methods examination of adaptation strategies in three coastal communities."

**Improvements**:

- Word count: 127 (more substantial)
- Citations: 5
- Specific data: 3 precise figures
- Formal academic tone: 9/10
- Research gap: Clearly identified
- Dissertation contribution: Explicitly stated

---

## Academic Writing Checklist for Your Dissertation

### Language Precision

- [ ] Remove all instances of "really," "very," "a lot," "big"
- [ ] Replace "think," "feel," "believe" with "argue," "demonstrate," "posit"
- [ ] Quantify instead of using vague descriptors
- [ ] Use technical vocabulary appropriate to field

### Structure

- [ ] Each claim supported by citation
- [ ] Synthesis rather than list of facts
- [ ] Complex sentences showing relationships between ideas
- [ ] Logical flow with clear transitions

### Academic Conventions

- [ ] Formal tone throughout
- [ ] Third person (avoid "I think" in introduction)
- [ ] Present perfect for recent research ("studies have shown")
- [ ] Past tense for specific studies ("Smith (2020) found")
- [ ] Proper citation format (check your style guide)

### Content Requirements

- [ ] Research gap clearly identified
- [ ] Study's contribution explicitly stated
- [ ] Appropriate scope for dissertation
- [ ] Disciplinary conventions followed

---

## Word Choice Upgrades: Informal → Academic

| Informal           | Academic Alternative                                     |
| ------------------ | -------------------------------------------------------- |
| "think"            | argue, posit, contend, assert                            |
| "really big"       | significant, substantial, considerable                   |
| "a lot of"         | numerous, extensive, substantial                         |
| "show"             | demonstrate, indicate, reveal, suggest                   |
| "problem"          | challenge, issue, concern, phenomenon                    |
| "affects everyone" | has broad implications, widespread ramifications         |
| "it is important"  | remains critical, proves essential, warrants examination |

---

## Next Steps

1. **Citation Audit**: Every factual claim needs a source
2. **Precision Pass**: Replace all vague terms with specific technical vocabulary
3. **Structure Review**: Combine simple sentences into complex sentences showing relationships
4. **Gap Statement**: Clearly articulate what's missing in current research that your study provides
5. **Committee Review**: Have advisor review tone and style before full draft
```

## Validation Process

After generating the report, Claude should offer:

"I've completed the grammar and style analysis. Would you like me to:

1. Revise the entire passage with changes integrated?
2. Focus on a specific type of improvement (grammar only, style only, etc.)?
3. Analyze additional sections?
4. Explain any of the suggestions in more detail?"

## Tips for Authors

### Using This Skill Effectively

- Analyze in chunks (chapter by chapter) rather than entire manuscript
- Focus on one type of issue per revision pass
- Don't change everything—preserve your voice
- Trust your instincts; reject suggestions that don't fit your style
- Use "Find" to search for problematic patterns manuscript-wide

### Common Over-Corrections to Avoid

- Eliminating all "was" creates awkward prose
- Removing all adverbs loses nuance
- Making every sentence complex hurts readability
- Over-synonymizing creates thesaurus abuse

## Validation Checklist

Before finalizing the enhancement report:

- [ ] All suggestions include specific textual examples
- [ ] Revisions preserve author's voice and style
- [ ] Explanations clarify why changes improve the text
- [ ] Multiple options provided where appropriate
- [ ] Genre conventions considered
- [ ] Both strengths and opportunities identified
- [ ] Priority levels assigned to changes
- [ ] Report is actionable with clear next steps
