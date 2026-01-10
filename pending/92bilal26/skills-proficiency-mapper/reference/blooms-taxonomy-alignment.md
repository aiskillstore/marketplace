---
title: "Bloom's Taxonomy: Cognitive Complexity & Assessment Design"
date: 2025-11-01
source: "Anderson & Krathwohl (2001) - Revision of Bloom's Taxonomy"
timeline: "1956 original → 2001 revision (current standard)"
---

# Bloom's Taxonomy: 70+ Years of Cognitive Framework

## Quick Alignment to CEFR Proficiency Levels

| CEFR Level | Bloom's Levels | What Students Do | Assessment Type |
|-----------|----------------|------------------|-----------------|
| **A1** | Remember | Recognize concepts, define terms | Multiple choice, matching |
| **A2** | Understand, Apply | Explain meaning, apply to simple contexts | Short answer, guided tasks |
| **B1** | Apply, Analyze | Apply independently, compare, analyze | Case studies, real problems |
| **B2** | Analyze, Evaluate | Evaluate alternatives, critique, defend | Essays, design critique |
| **C1+** | Evaluate, Create | Innovate, design, teach, research | Projects, teaching, research |

---

## The Six Cognitive Levels (2001 Revision)

### Level 1: REMEMBER

**Definition**: Retrieving relevant knowledge from long-term memory

**Action Verbs**:
- define, duplicate, list, memorize, recall, repeat, reproduce
- describe (basic), identify (basic)

**What This Looks Like**:
- Student can recall the definition of "specification"
- Student can list the 5 components of a spec
- Student can identify which example is a specification

**How to Assess**:
- Multiple choice: "Which is a specification?"
- Matching: Match term to definition
- Fill-in-the-blank: "A specification describes ___ in ___ way"
- Short-answer recall: "List 5 components of a spec"

**Time to teach**: 15-30 minutes
**Cognitive demand**: Minimal
**Prerequisite**: None (starting point)

**Example Test Item**:
```
Q: What are the 5 core components of a specification?
A: Intent, Inputs/Outputs, Requirements, NFRs, Acceptance Criteria
```

---

### Level 2: UNDERSTAND

**Definition**: Determining the meaning of instructional messages

**Action Verbs**:
- classify, describe, discuss, explain, identify, interpret, locate,
- recognize, report, select, sort, translate

**What This Looks Like**:
- Student can explain what makes a specification "clear"
- Student can describe why specs matter in teams
- Student can classify which spec component addresses which concern
- Student can translate a vague requirement into precise one

**How to Assess**:
- Short answer: "Why do acceptance criteria matter?"
- Concept map: How spec components relate to each other
- Essay: "Explain why vague specs fail with AI"
- Analogy: "A specification is like ___ because ___"

**Time to teach**: 30-60 minutes
**Cognitive demand**: Low-Moderate
**Prerequisite**: Remember-level knowledge

**Example Test Item**:
```
Q: A manager says "The system should be fast." Why is this a poor acceptance criterion?

A: Because "fast" is undefined.
   - Fast for who? (users? administrators?)
   - In what context? (normally responsive? during peak load?)
   - Measurable? (no way to test if achieved)
   - The spec lacks clarity.
```

---

### Level 3: APPLY

**Definition**: Using information in a new situation

**Action Verbs**:
- apply, change, choose, demonstrate, dramatize, interpret, practice,
- schedule, sketch, solve, use, write

**What This Looks Like**:
- Student can apply specification framework to a new problem
- Student can demonstrate how to write acceptance criteria
- Student can solve a requirement clarification problem
- Student can choose appropriate spec depth for context

**How to Assess**:
- Problem-solving task: "Write specification for this problem"
- Case study: "Here's a requirement; write acceptance criteria"
- Simulation: "Create spec for your capstone project"
- Practical exercise: Actual specification writing

**Time to teach**: 60-120 minutes
**Cognitive demand**: Moderate
**Prerequisite**: Remember + Understand

**Example Test Item**:
```
Q: A client says "Users should be able to reset their password"
   Write 3 acceptance criteria for this requirement.

A: - User receives password reset link by email within 30 seconds
   - User can create new password meeting complexity requirements
   - User can log in with new password immediately after reset
```

---

### Level 4: ANALYZE

**Definition**: Breaking material into parts and determining relationships

**Action Verbs**:
- appraise, compare, contrast, criticize, describe (complex), differentiate,
- discriminate, distinguish, examine, explain (complex), infer,
- relate, separate, subdivide

**What This Looks Like**:
- Student can analyze why one spec is better than another
- Student can compare spec-first vs. spec-anchored approaches
- Student can identify what makes a spec testable vs. vague
- Student can examine specification gaps in real example

**How to Assess**:
- Analysis essay: "Compare these two specs; identify strengths/weaknesses"
- Diagnostic task: "What's wrong with this spec? Why?"
- Decision matrix: "Evaluate spec approaches against criteria"
- Code review analogy: "Critique this specification"

**Time to teach**: 120-180 minutes
**Cognitive demand**: High
**Prerequisite**: Remember + Understand + Apply

**Example Test Item**:
```
Q: Compare these two specifications for a password reset feature.
   What are the strengths and weaknesses of each?

Spec A: "User can reset password"
Spec B: "User receives password reset email within 60 seconds of
         requesting reset. Link valid for 1 hour. User creates new
         password meeting requirements. New password works immediately."

Answer:
- Spec A is simple but unmeasurable (what's "can reset"?)
- Spec B is measurable, complete, but may be overly detailed
- For AI generation, Spec B is much more useful
```

---

### Level 5: EVALUATE

**Definition**: Making judgments based on criteria and standards

**Action Verbs**:
- appraise, argue, defend, judge, select, support, value, evaluate,
- critique, weigh

**What This Looks Like**:
- Student can defend why specification-first approach is better
- Student can evaluate whether a spec is ready for implementation
- Student can judge which SDD framework is best for situation
- Student can weigh tradeoffs between competing concerns

**How to Assess**:
- Debate/argue: "Defend your choice of spec framework"
- Critique essay: "Evaluate this spec for production readiness"
- Design review: "Should this spec be approved for development?"
- Justification: "Why is this the best approach? What are the alternatives?"

**Time to teach**: 180-300 minutes
**Cognitive demand**: Very High
**Prerequisite**: All previous levels

**Example Test Item**:
```
Q: Your team is deciding between "spec-first" and "spec-anchored"
   approaches for a 6-month project.

   Evaluate both approaches.
   Which would you recommend? Defend your choice.

Criteria to consider:
- Team experience with SDD
- Project complexity
- Stakeholder stability
- Risk tolerance
- Timeline
- Budget

Answer (varies, must be justified with reasoning):
"I recommend spec-first because... However, spec-anchored might be
better if... The key factor is..."
```

---

### Level 6: CREATE

**Definition**: Putting elements together to form something new

**Action Verbs**:
- assemble, construct, create, design, develop, formulate, write,
- generate, organize, plan, produce

**What This Looks Like**:
- Student can design a specification process for an organization
- Student can create a novel SDD framework for special context
- Student can develop a specification template for domain
- Student can generate new ideas for improving specification practice

**How to Assess**:
- Design project: "Create a specification process for your team"
- Innovation task: "Design a spec framework for [special context]"
- Teaching: "Create a training program on specifications"
- Research: "Investigate specification effectiveness in [domain]"

**Time to teach**: 300+ minutes
**Cognitive demand**: Expert/Mastery
**Prerequisite**: All previous levels + experience

**Example Test Item**:
```
Q: Design a specification process for a startup with:
   - No prior SDD experience
   - 5 developers, 1 product manager
   - 3-month timeline for MVP
   - Needs to iterate based on user feedback

Your design should address:
- How much time on specs vs. coding?
- What spec components are essential vs. optional?
- How to review/approve specs?
- How to handle changing requirements?
- How to train team on process?

Answer (varies, must be well-reasoned design):
[Detailed specification process design with justifications]
```

---

## Bloom's vs. Traditional Multiple-Choice Testing

### The Problem with "Teach to Remember"

**Traditional approach**: Focus on Remember level
```
80% of test items = "What is...", "Define...", "List..."
Result: Students memorize but can't apply
```

**Better approach**: Cognitive balance
```
10% Remember   - Basic definitions, recall
30% Understand - Explanation, interpretation
40% Apply      - Real-world problems, new situations
15% Analyze    - Comparison, breakdown of complex examples
5%  Evaluate   - Judgment and defense
```

**For SDD Course**:
- ✗ Don't ask: "What is a specification?" (Remember)
- ✓ Do ask: "Is this a good specification? Why/why not?" (Evaluate)
- ✗ Don't ask: "List 5 components" (Remember)
- ✓ Do ask: "Write a specification for your project" (Apply)

---

## Designing Assessments at Each Level

### Remember Level Assessments

**When to use**: Establishing baseline knowledge, checking definitions

**Question types**:
- Multiple choice
- Matching
- Fill-in-the-blank
- True/False
- "Define the term..."

**Example items**:
```
1. Multiple choice: Which is an acceptance criterion?
   a) The system should be fast
   b) User receives confirmation email within 60 seconds
   c) The system should work well
   d) Performance is important

2. Matching: Match component to definition
   [ ] Intent       A) What system does when successful
   [ ] Inputs       B) What problem does spec solve?
   [ ] Outputs      C) Data coming into system

3. Fill-in-blank: "Acceptance criteria must be ______, not vague"
   Answer: measurable / testable / specific
```

**Difficulty**: Easy
**Time**: 30 seconds - 2 minutes per item
**Cognitive value**: Low but necessary

---

### Understand Level Assessments

**When to use**: Check comprehension before moving to application

**Question types**:
- Short answer
- Explanation
- Concept mapping
- Analogy/metaphor
- Summarization

**Example items**:
```
1. Short answer: "Explain why acceptance criteria must be testable.
   Use an example."

2. Analogy: "A specification is like _____ because _____"
   Example answer: "A map, because it shows the territory
   (problem space) that the code (journey) must navigate"

3. Concept map: Draw how these relate:
   Specification, Intent, Requirements, Acceptance Criteria,
   Testability, Clarity, SDD Loop
```

**Difficulty**: Easy-Moderate
**Time**: 5-15 minutes per item
**Cognitive value**: Moderate (comprehension verified)

---

### Apply Level Assessments

**When to use**: Check students can do the skill in new contexts

**Question types**:
- Case study
- Problem-solving task
- Practical exercise
- Simulation
- Real-world project

**Example items**:
```
1. Case Study: "Here's a requirement from a client.
   Write a proper specification for it.
   Include all 5 components with proper detail level."

2. Problem-Solving: "Your team is blocked because the spec is
   ambiguous. Show how you would clarify it."

3. Real-world: "Write the specification for your capstone project."
```

**Difficulty**: Moderate-Hard
**Time**: 30-180 minutes
**Cognitive value**: High (real competence demonstrated)

---

### Analyze Level Assessments

**When to use**: Develop critical thinking about specification practices

**Question types**:
- Analysis essay
- Comparison/contrast
- Diagnostic task
- Critique
- Breakdown/decomposition

**Example items**:
```
1. Analysis: "Compare spec-first vs. code-first approaches.
   What are tradeoffs? When is each appropriate?"

2. Diagnostic: "This spec failed production. What went wrong?
   What should have been different?"

3. Critique: "Review this specification. Identify 5 issues and
   explain why each is a problem."
```

**Difficulty**: Hard
**Time**: 45-120 minutes
**Cognitive value**: Very High (expert-level thinking)

---

### Evaluate Level Assessments

**When to use**: Develop judgment and decision-making

**Question types**:
- Debate/argument
- Design choice justification
- Trade-off analysis
- Rubric scoring/judgment
- Strategic decision

**Example items**:
```
1. Argument: "Should your team adopt SDD? Defend your position
   with specific evidence from your project context."

2. Design Choice: "Your startup must choose between spec-first and
   spec-anchored approaches. Which? Justify with your context."

3. Judgment: "Is this specification ready for development? What
   would need to change? Why?"
```

**Difficulty**: Very Hard
**Time**: 60-180 minutes
**Cognitive value**: Expert (strategic thinking demonstrated)

---

### Create Level Assessments

**When to use**: Advanced projects, innovation, mastery demonstration

**Question types**:
- Design project
- Innovation task
- Teaching/training development
- Research
- Original framework

**Example items**:
```
1. Design: "Create a specification process for your organization.
   Include templates, review process, training plan, examples."

2. Innovation: "Design a novel SDD framework tailored to
   [special domain: game development, hardware, biotech, etc.]"

3. Teaching: "Develop a training program to teach SDD to a team
   with no prior experience. Include curriculum, exercises, assessment."
```

**Difficulty**: Expert
**Time**: 4+ hours
**Cognitive value**: Mastery (advancing the field)

---

## Bloom's + CEFR Integration Example

### How They Work Together for "Specification Writing" Skill

#### Lesson Targeting A2 Level, Understand-Apply Cognitive Levels

**Learning Objective**:
"Student can understand specification components AND apply them
to simple, given problems"

**Assessment Design** (Remember only A2-level, Use Understand+Apply):

```
Remember (5%):
- Q: "What 5 components should a spec have?"
  (Establishes baseline)

Understand (30%):
- Q: "Explain why each component is important"
- Q: "Compare vague requirement vs. clear requirement"

Apply (65%):
- Task: "Write simple specification for given problem using template"
- Rubric: Does it have all 5 components? Are they clear?

(No Analyze/Evaluate/Create - that's B1+ level)
```

#### Lesson Targeting B1 Level, Apply-Analyze Cognitive Levels

**Learning Objective**:
"Student can apply specification writing to real problems AND
analyze specification quality"

**Assessment Design** (Remember is minimal; Emphasize Apply+Analyze):

```
Remember (5%):
- Quick review of components (1 question)

Understand (15%):
- Explain why spec quality matters in real context

Apply (50%):
- Write complete specification for real/capstone project
- Make decisions about depth, detail level, format

Analyze (30%):
- Analyze existing spec: identify gaps, ambiguities, improvements
- Compare two approaches: which is more complete? Why?

(No Evaluate/Create - that's B2+ level)
```

#### Lesson Targeting B2 Level, Analyze-Evaluate Cognitive Levels

**Learning Objective**:
"Student can evaluate specification approaches and defend decisions"

**Assessment Design** (Remember/Understand minimal; Emphasize Analyze+Evaluate):

```
Remember (2%):
- (Assumes knowledge - quick reference only)

Understand (8%):
- (Assumes comprehension - review only)

Apply (20%):
- (Assumes competence - refresher only)

Analyze (35%):
- Compare approaches: spec-first vs. code-first vs. spec-as-source
- Analyze context to determine best approach
- Break down spec quality into components

Evaluate (35%):
- Judge whether spec is ready for production
- Defend choice of approach for specific context
- Weigh tradeoffs and make strategic decisions

(No Create - that's C1+ level)
```

---

## Cognitive Load and Bloom's Levels

### Key Principle: Higher Cognitive Levels Take More Time

**Rough time allocations for skill mastery**:

```
Level 1 (Remember):        5-10 minutes
Level 2 (Understand):      15-30 minutes additional
Level 3 (Apply):           60-120 minutes additional
Level 4 (Analyze):         120-180 minutes additional
Level 5 (Evaluate):        180-300 minutes additional
Level 6 (Create):          300+ minutes + experience

Total for B1 (Apply+Analyze):     200-300 minutes = 3-5 hours
Total for B2 (Evaluate):          500-600 minutes = 8-10 hours
```

**Implication**: Can't teach B1 mastery in 30 minutes; need 3-5 hours

---

## Research Foundation

**Original Taxonomy**:
- Bloom, B.S. (1956). "Taxonomy of Educational Objectives"

**Modern Revision**:
- Anderson, L.W., & Krathwohl, D.R. (Eds.). (2001). "A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom's Taxonomy of Educational Objectives"

**Application to Assessment**:
- Fink, L.D. (2013). "Creating Significant Learning Experiences: An Integrated Approach to Designing College Courses"
- Wiggins, G. & McTighe, J. (2005). "Understanding by Design"

---

## Summary: Bloom's for SDD Teaching

**When designing lessons and assessment**:

1. **Match cognitive level to proficiency level**
   - A1 = Remember
   - A2 = Understand, Apply
   - B1 = Apply, Analyze
   - B2 = Analyze, Evaluate
   - C1 = Evaluate, Create

2. **Allocate assessment time appropriately**
   - Higher levels require more assessment time
   - Don't expect B1 mastery from 30-minute activity

3. **Include multiple levels in assessment**
   - Don't test only Remember-level (too easy)
   - Build to appropriate cognitive level for proficiency target

4. **Use action verbs precisely**
   - Learning objective: "Student can **analyze** spec quality" (specific level)
   - Not: "Student will understand specifications" (vague)

5. **Match assessment to cognitive level**
   - Remember → Multiple choice, matching
   - Apply → Case study, real problems
   - Evaluate → Critique, defense, trade-off analysis

---

**Used with**: CEFR proficiency levels for complete skill mapping
**Result**: Clear, measurable, internationally-recognized skill credentials
