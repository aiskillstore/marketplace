---
name: skill-from-masters
description: Help users create high-quality skills by discovering and incorporating proven methodologies from domain experts. Use this skill BEFORE skill-creator when users want to create a new skill - it enhances skill-creator by first identifying expert frameworks and best practices to incorporate. Triggers on requests like "help me create a skill for X" or "I want to make a skill that does Y". This skill guides methodology selection, then hands off to skill-creator for the actual skill generation.
---

# Skill From Masters

Create skills that embody the wisdom of domain masters. This skill helps users discover and incorporate proven methodologies from recognized experts before generating a skill.

## Core Philosophy

Most professional domains have outstanding practitioners who have codified their methods through books, talks, interviews, and frameworks. A skill built on these proven methodologies is far more valuable than one created from scratch.

The goal is not just "good enough" — it's reaching the highest level of human expertise in that domain.

## Workflow

### Step 1: Understand the Skill Intent

Ask the user:
- What skill do they want to create?
- What specific tasks should it handle?
- What quality bar are they aiming for?

### Step 2: Identify Relevant Domains

Map the skill to one or more methodology domains. A single skill may span multiple domains.

Example mappings:
- "Sales email skill" → Sales, Writing, Persuasion
- "User interview skill" → User Research, Interviewing, Product Discovery
- "Presentation skill" → Storytelling, Visual Design, Persuasion
- "Code review skill" → Software Engineering, Feedback, Communication

### Step 3: Surface Expert Methodologies

**Layer 1: Local Database**
Consult `references/methodology-database.md` for known frameworks.

**Layer 2: Web Search for Experts**
Search the web to discover additional experts and methodologies:
- Search: "[domain] best practices expert"
- Search: "[domain] framework methodology"
- Search: "[domain] master practitioner"

**Layer 3: Deep Dive on Selected Experts**
For promising experts, search for their original content:
- Search: "[expert name] methodology interview"
- Search: "[expert name] [domain] transcript"
- Search: "[expert name] framework explained"

Fetch and read primary sources when available (articles, talk transcripts, blog posts).

For each relevant domain, present:
- Key experts and their core contributions
- Specific frameworks, principles, or processes
- Source materials (books, talks, interviews)

### Step 4: Find Golden Examples

Before finalizing methodology selection, search for exemplary outputs:
- Search: "best [output type] examples"
- Search: "[output type] template [top company]"
- Search: "award winning [output type]"

Understanding what excellence looks like helps define the quality bar.

### Step 5: Collaborative Selection

Present the methodologies to the user and discuss:
- Which frameworks resonate with their goals?
- Are there conflicts between methodologies to resolve?
- Should they combine multiple approaches?
- Any specific principles they want to emphasize or exclude?

Guide the user to select 1-3 primary methodologies that will form the skill's foundation.

### Step 6: Extract Actionable Principles

For each selected methodology, search for and distill:

**The Why (Core Principles)**
- Search: "[methodology] core principles"
- Search: "why [methodology] works"

**The How (Concrete Process)**
- Search: "[methodology] step by step"
- Search: "[methodology] implementation guide"

**The What (Quality Criteria)**
- Search: "[methodology] checklist"
- Search: "[methodology] evaluation criteria"

**The Pitfalls (Common Mistakes)**
- Search: "[domain] common mistakes"
- Search: "[methodology] pitfalls avoid"

Fetch primary sources to get exact wording and nuance, not just summaries.

### Step 7: Cross-Validate

Compare insights across multiple sources:
- What principles appear consistently? (high confidence)
- Where do experts disagree? (flag for user)
- What's unique to each approach? (differentiation)

Synthesize a coherent framework that takes the best from each source.

### Step 8: Generate the Skill

With methodologies confirmed, use the **skill-creator** skill to generate the final skill. The generated skill should:

1. Credit the methodology sources in a comment (documenting provenance)
2. Translate expert wisdom into actionable instructions
3. Include concrete examples derived from golden examples found
4. Capture quality criteria as explicit checkpoints
5. Include "don't do this" anti-patterns from pitfall research
6. Match the quality bar of the best human practitioners

## Quality Checklist

Before finalizing, verify:
- [ ] Did we search beyond the local database?
- [ ] Did we find primary sources, not just summaries?
- [ ] Did we find golden examples of the output?
- [ ] Did we identify common mistakes to avoid?
- [ ] Did we cross-validate across multiple experts?
- [ ] Does the skill encode specific, actionable steps (not vague principles)?

## Example Interaction

**User**: I want to create a skill for writing product requirement documents.

**Assistant**: Great choice. Let me search for the best methodologies on PRD writing.

[Searches: "PRD best practices expert", "product requirements document methodology", "best PRD examples"]

I found several strong frameworks:

**Product Management**:
- Marty Cagan (SVPG): Emphasizes problem-first PRDs, separating problem space from solution space
- Teresa Torres: Continuous discovery, outcome-focused requirements

**Business Writing**:
- Barbara Minto: Pyramid Principle - lead with conclusion, MECE structure
- Amazon: Working backwards from press release, 6-pager narrative format

**Golden Examples Found**:
- Intercom's public PRD template
- Linear's product spec format

**Common Mistakes** (from my search):
- Jumping to solutions before defining the problem
- Writing for engineers instead of for alignment
- Missing success metrics

Which of these approaches resonates? Or should I search deeper into any of them?

**User**: I like Amazon's approach combined with Cagan's problem-first thinking. Can you find more details on Amazon's method?

**Assistant**: [Searches: "Amazon 6-pager template", "Amazon working backwards methodology", "Amazon PR FAQ process"]

[Fetches relevant articles and synthesizes key principles]

Here's what I found from primary sources...
[Continues to Step 6, 7, and 8]
