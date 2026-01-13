# Full Context Pattern

Use when you need comprehensive understanding of an entire library.

## When to Use

- Major migrations between frameworks
- Writing comprehensive tutorials or documentation
- Architectural decisions requiring deep knowledge
- First-time deep learning of a complex library

## Steps

```
@ai-docs/libraries/{library}/full-context.md
```

That's it - this file contains everything for the library.

## Warning

**Use sparingly** - full-context.md files are large:
- Typical size: 5,000-15,000 tokens
- May consume significant context window
- Targeted loading is almost always better

## When Full Context IS Appropriate

| Scenario | Why Full Context |
|----------|------------------|
| Migration from Library X to Y | Need to understand ALL patterns |
| Writing a tutorial | Must cover all major features |
| Architecture review | Need complete picture |
| Onboarding to new library | Initial deep dive |

## When NOT to Use

| Scenario | Better Approach |
|----------|-----------------|
| "What's the retry syntax?" | Direct navigation to specific page |
| Quick bug fix | Load error-handling page only |
| Single feature implementation | Load 2-3 relevant pages |
| Answering user questions | Targeted search |

## Token Budget

- **Full context: 5,000-15,000 tokens**

Compare to targeted loading:
- Single page: ~400 tokens
- 3 pages: ~1,200 tokens
- 5 pages: ~2,000 tokens

## Recovery

If you loaded full-context.md and realize you didn't need it:
- The context is already consumed
- For future similar queries, use targeted loading
- Note the specific sections that were useful for next time
