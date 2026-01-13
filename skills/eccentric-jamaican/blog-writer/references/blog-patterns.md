# Blog Patterns for Addis the Advisor

## Canonical data shape
- Source file: `src/lib/blog-data.ts`
- Each post follows the `BlogPost` interface (all fields required).
- Content is a Markdown template string and is dedented at render time.

## Voice and positioning
- Audience: Jamaican households and professionals seeking insurance and financial planning clarity.
- Tone: confident, modern, advisory; professional and trustworthy.
- Perspective: second person ("you") with occasional brand reference ("Addis the Advisor").

## Structure patterns (use as needed)
- Start with H2 that matches the post title.
- Use short paragraphs and H3/H4 subheads for skimmability.
- Common sections that appear across posts:
  - The Real Issue
  - What the Numbers Say (Evidence & Examples)
  - Common Mistakes
  - What To Do Next
  - Final Note
  - Sources (numbered list when citing)
- Action steps often appear as numbered lists or bolded lead-ins.

## SEO patterns
- SEO title: includes topic + Jamaica relevance where possible.
- SEO description: 1 concise sentence summarizing the benefit.
- Keywords: 3–5 phrases; include "Jamaica" or brand terms when relevant.

## Metadata patterns
- `slug`: commonly `YYYY-MM-DD-topic` for newer posts; older posts may be topic-only.
- `date`: ISO `YYYY-MM-DD`.
- `readTime`: derive from word count (roughly 200-250 wpm, round to nearest minute).
- `category`: reuse existing categories unless there is a clear need for a new one.
- `author`: keep name/role/image consistent unless instructed otherwise.
- `image`: store in `public/blog/` and reference as `/blog/<filename>.png`.

## Content template (adaptable)
```
## <Post Title>

<1-2 paragraph lead that frames the problem in Jamaica>

### The Real Issue
<Explain the core risk or misconception>

### What the Numbers Say (Evidence & Examples)
- <Data point or example>
- <Data point or example>

### Common Mistakes
- <Mistake>
- <Mistake>

### What To Do Next
**Key takeaway:** <one sentence>

**Action steps:**
1. <Step one>
2. <Step two>
3. <Step three>

### Final Note
<Closing invite to contact or follow up>

### Sources
1. <Source>
2. <Source>
```
