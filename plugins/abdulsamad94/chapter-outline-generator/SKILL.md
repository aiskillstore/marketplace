---
name: chapter-outline-generator
description: Generates comprehensive chapter outlines for books, including key topics, subtopics, learning objectives, and estimated word counts. Use this when the user needs help structuring a book chapter or creating a table of contents.
---

# Chapter Outline Generator

## Purpose

This skill helps authors create detailed, structured chapter outlines for their books. It ensures logical flow, comprehensive coverage, and balanced chapter lengths.

## When to Use

- User is starting a new book and needs chapter structure
- User wants to expand a single chapter into detailed sections
- User needs to reorganize or rebalance existing chapters
- User requests a table of contents or chapter breakdown

## Instructions

### Step 1: Understand the Context

Ask the user for:

- Book title and genre/subject matter
- Target audience (academic, general readers, children, etc.)
- Overall book theme or main argument
- Approximate desired book length (word count or page count)
- Number of chapters desired (if known)

### Step 2: Generate Chapter Framework

For each chapter, create:

- **Chapter Number and Title**: Clear, engaging chapter titles
- **Chapter Summary**: 2-3 sentence overview of what the chapter covers
- **Learning Objectives**: 3-5 key takeaways readers should gain
- **Main Sections**: 3-7 major sections within the chapter
- **Subsections**: 2-4 subsections under each main section
- **Estimated Word Count**: Based on overall book length and chapter importance

### Step 3: Ensure Logical Flow

- Check that chapters build upon each other logically
- Ensure no major topic gaps
- Verify balanced distribution of content across chapters
- Confirm clear progression from introduction to conclusion

### Step 4: Output Format

Present the outline in a clean, hierarchical format:

```markdown
# Book Title: [Title]

## Chapter 1: [Chapter Title]

**Summary**: [2-3 sentence overview]

**Learning Objectives**:

- Objective 1
- Objective 2
- Objective 3

**Sections**:

1. [Section Title]
   - Subsection A
   - Subsection B
2. [Section Title]
   - Subsection A
   - Subsection B

**Estimated Word Count**: [X,XXX words]

---

## Chapter 2: [Chapter Title]

...
```

## Examples

### Example 1: Fiction Novel

**User**: "I'm writing a mystery novel about a detective solving art thefts. Can you outline the first 3 chapters?"

**Output**:

```markdown
# Book Title: The Vanishing Canvas

## Chapter 1: The Empty Gallery

**Summary**: Detective Sarah Chen receives a mysterious call about a high-profile art theft at the Metropolitan Museum. She arrives to find not just one, but three priceless paintings missing without a trace.

**Learning Objectives**:

- Introduce the protagonist and her detective skills
- Establish the central mystery and stakes
- Set up the museum setting and key supporting characters

**Sections**:

1. The Midnight Call
   - Sarah's routine disrupted
   - Initial crime scene details
2. The Crime Scene Investigation
   - Missing paintings identified
   - Security footage review
   - First clues discovered
3. Meeting the Museum Director
   - Background on the stolen artworks
   - List of potential suspects
   - Political pressure mounting

**Estimated Word Count**: 3,500 words
```

### Example 2: Non-Fiction Business Book

**User**: "Help me outline a book about remote team management."

**Output**:

```markdown
# Book Title: Leading from Anywhere: The Remote Manager's Playbook

## Chapter 1: The Remote Work Revolution

**Summary**: Explores the shift to remote work, examining why traditional management approaches fail in virtual environments and what successful remote leaders do differently.

**Learning Objectives**:

- Understand the fundamental differences between in-office and remote management
- Identify common pitfalls of traditional management in remote contexts
- Learn the core principles of effective remote leadership

**Sections**:

1. The Great Remote Transition
   - Statistics and trends in remote work adoption
   - Case studies of companies that succeeded (and failed)
2. Why Old Management Models Don't Work
   - The visibility bias problem
   - Time zone challenges
   - Communication breakdowns
3. The Remote Leadership Mindset
   - Trust over surveillance
   - Output versus activity
   - Asynchronous-first thinking

**Estimated Word Count**: 4,000 words
```

## Tips for Authors

- Keep chapter lengths relatively consistent (unless intentionally varying for pacing)
- Frontload crucial world-building/context in early chapters
- Each chapter should have its own mini-arc while contributing to the overall narrative/argument
- Consider ending chapters with hooks or cliffhangers (fiction) or actionable takeaways (non-fiction)
- Review the outline as a whole to ensure comprehensive coverage and no redundancy

## Validation Checklist

Before finalizing the outline, verify:

- [ ] All chapters have clear, distinct purposes
- [ ] Logical progression from chapter to chapter
- [ ] No major gaps in coverage
- [ ] Reasonable word count distribution
- [ ] Each chapter has actionable sections and subsections
- [ ] Learning objectives align with content
