---
name: skill-from-masters
description: Help users create high-quality skills by discovering and incorporating proven methodologies from domain experts. Use this skill BEFORE skill-creator when users want to create a new skill - it enhances skill-creator by first identifying expert frameworks and best practices to incorporate. Triggers on requests like "help me create a skill for X" or "I want to make a skill that does Y". This skill guides methodology selection, then hands off to skill-creator for the actual skill generation.
---

# Skill From Masters

Create skills that embody the wisdom of domain masters. This skill helps users discover and incorporate proven methodologies from recognized experts before generating a skill.

## Core Philosophy

Most professional domains have outstanding practitioners who have codified their methods through books, talks, interviews, and frameworks. A skill built on these proven methodologies is far more valuable than one created from scratch.

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

Consult `references/methodology-database.md` for known frameworks. For each relevant domain, present:
- Key experts and their core contributions
- Specific frameworks, principles, or processes
- Source materials (books, talks, interviews)

If the domain isn't covered in the database, search the web to find recognized experts and their methodologies.

### Step 4: Collaborative Selection

Present the methodologies to the user and discuss:
- Which frameworks resonate with their goals?
- Are there conflicts between methodologies to resolve?
- Should they combine multiple approaches?
- Any specific principles they want to emphasize or exclude?

Guide the user to select 1-3 primary methodologies that will form the skill's foundation.

### Step 5: Extract Actionable Principles

For each selected methodology, distill:
- Core principles (the "why")
- Concrete steps or processes (the "how")
- Quality criteria or checklists (the "what good looks like")
- Common pitfalls to avoid (the "watch out for")

If source material is available online (transcripts, articles, documentation), fetch and review primary sources.

### Step 6: Generate the Skill

With methodologies confirmed, use the **skill-creator** skill to generate the final skill. Follow skill-creator's standard process, ensuring the generated skill:

1. Credits the methodology sources in a comment (documenting provenance)
2. Translates expert wisdom into actionable instructions
3. Includes concrete examples derived from the methodologies
4. Captures the quality bar and evaluation criteria from the experts

## Example Interaction

**User**: I want to create a skill for writing product requirement documents.

**Assistant**: Great choice. PRD writing spans several domains where experts have codified best practices:

**Product Management**:
- Marty Cagan (SVPG): Emphasizes problem-first PRDs, separating problem space from solution space
- Teresa Torres: Continuous discovery, outcome-focused requirements
- Gibson Biddle: DHM model for evaluating features

**Business Writing**:
- Barbara Minto: Pyramid Principle - lead with conclusion, MECE structure
- Amazon: Working backwards from press release, 6-pager narrative format

**User Research Integration**:
- Jobs to be Done framework: Focus on what job the user is hiring the product to do

Which of these approaches resonates with how you want PRDs written? Or should we combine elements?

**User**: I like Amazon's approach combined with Cagan's problem-first thinking.

**Assistant**: Perfect combination. Let me extract the key principles from both...
[Continues to Step 5 and 6]
