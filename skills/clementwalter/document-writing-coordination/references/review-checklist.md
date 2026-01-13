# Document Review Checklist

## Section Review (Per Task)

### Content Accuracy

- [ ] Technical details match source code
- [ ] File paths and line references are correct
- [ ] Code snippets are syntactically valid
- [ ] Configuration examples are accurate
- [ ] Version numbers and dependencies are current

### Completeness

- [ ] All scope items from task description addressed
- [ ] Required diagrams included
- [ ] Examples provided where specified
- [ ] No "TODO" placeholders remaining
- [ ] Edge cases mentioned where relevant

### Quality

- [ ] Clear and concise writing
- [ ] Appropriate technical depth for audience
- [ ] No redundant content
- [ ] Proper markdown formatting
- [ ] Consistent terminology

### Integration

- [ ] Section numbering matches TOC
- [ ] Cross-references to other sections are valid
- [ ] Terminology consistent with rest of document
- [ ] Style matches other sections

## Consistency Review (After Merge)

### Terminology Consistency

Check these terms are used consistently throughout:

| Correct Term          | Avoid                   |
| --------------------- | ----------------------- |
| [Define for your doc] | [Alternatives to avoid] |

### Cross-Reference Validation

- [ ] All "see Section X" references point to correct sections
- [ ] All file path references are accurate
- [ ] All external links are valid

### Structural Consistency

- [ ] Heading levels are consistent
- [ ] Code block language tags are consistent
- [ ] List formatting is consistent
- [ ] Diagram style is consistent

### Content Overlap

- [ ] No duplicate explanations across sections
- [ ] No contradictory information
- [ ] Appropriate referencing between related sections

## Review Decision Matrix

| Issue Type                  | Action                      |
| --------------------------- | --------------------------- |
| Minor typo/formatting       | Fix directly, approve       |
| Incorrect technical detail  | Reject, create fix task     |
| Missing required content    | Reject, update scope        |
| Style inconsistency         | Note for consistency review |
| Scope creep (extra content) | Discuss, may split          |

## Rejection Feedback Template

```markdown
## Revision Required

**Section**: [Section Number and Title]
**Task ID**: [VK Task UUID]

### Issues Found

#### Critical (Must Fix)

- [ ] Issue 1: [Description and location]
- [ ] Issue 2: [Description and location]

#### Recommended (Should Fix)

- [ ] Issue 3: [Description]

### Specific Corrections

- Line X: Change "incorrect" to "correct"
- Add missing diagram showing [concept]
- Update code snippet to match current API

### Action

Fix issues above and return task to "inreview" status.
```

## Final Document Checklist

Before marking documentation complete:

### Structure

- [ ] Table of contents matches actual sections
- [ ] All sections have content (no TODOs)
- [ ] Appendices are complete
- [ ] Changelog/version info updated

### Technical Accuracy

- [ ] All code samples tested/verified
- [ ] All commands verified to work
- [ ] Architecture diagrams accurate
- [ ] Dependencies correctly listed

### Readability

- [ ] Executive summary provides quick orientation
- [ ] Sections can be read independently
- [ ] Technical jargon explained or linked
- [ ] Examples clarify concepts

### Maintenance

- [ ] Document location noted in README
- [ ] Update process documented
- [ ] Owner/maintainer identified
- [ ] Last updated date set
