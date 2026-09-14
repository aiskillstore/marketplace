---
name: ai-visibility-audit
description: >
  Audit and optimize a website's AI search visibility using BotSee analysis data.
  Use when the user wants to: (1) check how visible their brand is across AI search
  engines (ChatGPT, Claude, Perplexity, Gemini), (2) find keyword and terminology
  gaps between what AI engines search for and what their site says, (3) make
  landing page copy changes to improve AI visibility, or (4) run a full AI
  visibility audit on any domain. Triggered by requests like "audit my AI visibility",
  "check how AI sees my site", "optimize my landing page for AI search", or
  "run an AI visibility audit on <site>".
---

# AI Visibility Audit & Landing Page Optimization

Audit a site's AI search visibility with BotSee, identify terminology gaps, and make surgical copy changes.

**Requires:** BotSee plugin installed (`/botsee` skill available)

## Workflow

### 1. Set Up BotSee Site

```
/botsee create-site <site>
```

Creates site with 2 customer types, 4 personas, 20 auto-generated questions. Note the persona UUIDs from the output.

### 2. Review & Replace Questions

Auto-generated questions are often too generic. Review and replace them:

1. List questions per persona: `/botsee list-questions <persona_uuid>`
2. Delete questions that don't match how real customers search AI engines
3. Create new questions matching actual search intent for the site's audience

Use `--text` flag: `/botsee create-question <persona_uuid> --text "question text"`

Questions should match how target customers actually ask AI search engines. Think about what someone would type into ChatGPT or Perplexity when looking for a product like this one.

Present draft questions to the user for approval before creating them.

### 3. Run Analysis

```
/botsee analyze
```

~660 credits. Capture the analysis UUID from the output. Returns competitors, keywords, and sources by customer type.

### 4. Pull Opportunities

```
/botsee results-keyword-opportunities <analysis_uuid>
/botsee results-source-opportunities <analysis_uuid>
```

- **Keyword opportunities** = queries where the brand is missing or ranks poorly
- **Source opportunities** = sites AI cites when it doesn't mention the brand (link-building/PR targets)

### 5. Compare Against Current Homepage

Fetch the live homepage with WebFetch and compare its language against what AI engines searched for. Look for:

- **Terms AI uses that the page doesn't** (industry acronyms, category names)
- **Phrases competitors rank for that the site doesn't use** (e.g., "share of voice" vs generic "monitoring")
- **Audience segments not addressed** (e.g., enterprise vs startup, developer vs marketer)
- **Missing integration or feature keywords** (e.g., "REST API", "CI/CD", "webhook")

Present a gap table to the user:

| Missing Term | Evidence (where AI searched for it) |
|---|---|
| Term A | N+ search queries mentioning it |
| Term B | Competitor X ranks for this |

### 6. Make Surgical Copy Changes

Edit only text strings in the landing page template. No layout or structural changes. Target:

- Page title and meta description
- Hero headline and subtitle
- Feature descriptions and bullet points
- Section headers
- Integration lists or badges

Insert missing keywords into existing copy rather than rewriting sections. Keep changes minimal. Present the proposed changes to the user before editing.

### 7. Verify & Ship

Compile to verify no syntax errors. Commit and push when the user approves.
