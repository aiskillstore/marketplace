# Slide Modification Guide

Workflows for modifying individual slides after initial generation.

## Edit Single Slide

Regenerate a specific slide with modified content:

1. Identify slide to edit (e.g., `03-slide-key-findings.svg`)
2. Update prompt in `prompts/03-slide-key-findings.md`
3. If content changes significantly, update slug in filename
4. Regenerate image using same session ID

## Add New Slide

Insert a new slide at specified position:

1. Specify insertion position (e.g., after slide 3)
2. Create new prompt with appropriate slug (e.g., `04-slide-new-section.md`)
3. Generate new slide image
4. **Renumber files**: All subsequent slides increment NN by 1
   - `04-slide-conclusion.svg` → `05-slide-conclusion.svg`
   - Slugs remain unchanged
5. Update `outline.md` with new slide entry

## Delete Slide

Remove a slide and renumber:

1. Identify slide to delete (e.g., `03-slide-key-findings.svg`)
2. Remove image file and prompt file
3. **Renumber files**: All subsequent slides decrement NN by 1
   - `04-slide-conclusion.svg` → `03-slide-conclusion.svg`
   - Slugs remain unchanged
4. Update `outline.md` to remove slide entry

## File Naming Convention

Files use meaningful slugs for better readability:

```
NN-slide-[slug].svg
NN-slide-[slug].md (in prompts/)
```

Examples:
- `01-slide-cover.svg`
- `02-slide-problem-statement.svg`
- `03-slide-key-findings.svg`
- `04-slide-back-cover.svg`

## Slug Rules

| Rule | Description |
|------|-------------|
| Format | Kebab-case (lowercase, hyphens) |
| Source | Derived from slide title/content |
| Uniqueness | Must be unique within the deck |
| Updates | Change slug when content changes significantly |

## Renumbering Rules

| Scenario | Action |
|----------|--------|
| Add slide | Increment NN for all subsequent slides |
| Delete slide | Decrement NN for all subsequent slides |
| Reorder slides | Update NN to match new positions |
| Edit slide | NN unchanged, update slug if needed |

**Important**: Slugs remain unchanged during renumbering. Only the NN prefix changes.

## Post-Modification Checklist

After any modification:

- [ ] Image file renamed/created correctly
- [ ] Prompt file renamed/created correctly
- [ ] Subsequent files renumbered (if add/delete)
- [ ] `outline.md` updated to reflect changes
- [ ] Slide count in outline header updated