---
name: research-storage
description: "Research file storage conventions and templates for dokhak agents. Use when: (1) saving research results from research-collector or researcher agents, (2) reading cached research files, (3) checking if research exists for a section. Provides directory structure, file format templates, and naming conventions."
allowed-tools: Read, Write, Glob
user-invocable: false
---

# Research Storage Skill

This skill defines conventions for storing and retrieving research data collected by dokhak agents. Research files are cached to enable reuse and reduce redundant web searches.

## Quick Reference for Agents

| Agent | Uses This Skill For |
|-------|---------------------|
| researcher | Directory resolution, research.md writing, multi-tier lookup |
| research-collector | summary.md, sources.md writing to `.research/init/` |
| writer | Reading research files (read-only) |
| structure-designer | Reading init research (read-only) |

### Standard Loading Pattern

All agents should reference this skill for:
- **Normalization functions**: normalizeChapter, normalizeSection, generateSlug
- **Multi-tier directory resolution**: Handling legacy naming inconsistencies
- **File format templates**: research.md, sources.md, summary.md

```
Read("skills/research-storage/SKILL.md")
```

## Directory Structure

```
project-root/
├── .research/                          # Research cache directory
│   ├── init/                           # /init command research
│   │   ├── summary.md                  # Structured research summary
│   │   └── sources.md                  # Source registry with reliability
│   │
│   └── sections/                       # /write command section research
│       ├── 01-1-introduction/
│       │   ├── research.md             # Section research results
│       │   └── sources.md              # Section sources
│       ├── 01-2-core-concepts/
│       │   ├── research.md
│       │   └── sources.md
│       └── {chapter}-{section}-{slug}/
│           ├── research.md
│           └── sources.md
```

## Naming Convention

### Section Directory Pattern (CANONICAL)

Format: `{chapter}-{section}-{slug}`

| Component | Format                  | Canonical Example | Non-canonical (avoid) |
| --------- | ----------------------- | ----------------- | --------------------- |
| chapter   | Zero-padded 2 digits    | `01`, `02`, `10`  | `1`, `2`              |
| section   | Single digit (NO padding) | `1`, `2`, `3`   | `01`, `02`            |
| slug      | Kebab-case lowercase    | `core-concepts`   | `Core-Concepts`       |

**Canonical Examples**:

- Chapter 1, Section 2, "Core Concepts" → `01-2-core-concepts` ✓
- Chapter 3, Section 1, "Getting Started" → `03-1-getting-started` ✓
- Chapter 10, Section 3, "Advanced Patterns" → `10-3-advanced-patterns` ✓

**Non-canonical (may exist from legacy/inconsistency)**:

- `1-2-core-concepts` (chapter not padded)
- `01-02-core-concepts` (section padded)
- `01-2-Core-Concepts` (slug not lowercase)

## Normalization Functions

**CRITICAL**: All agents MUST use these normalization functions to ensure consistency.

### normalizeChapter(chapter)

Converts any chapter format to canonical 2-digit zero-padded string.

```
Input: "1" or "01" or 1 or "001"
Output: "01" (always 2-digit zero-padded string)

Process:
1. Convert to integer: parseInt(chapter, 10)
2. Zero-pad to 2 digits: String(n).padStart(2, '0')

Examples:
- "1" → "01"
- "01" → "01"
- "10" → "10"
- 1 → "01"
- "001" → "01"
```

### normalizeSection(section)

Converts any section format to canonical single-digit string (no padding).

```
Input: "1" or "01" or 1
Output: "1" (single digit, no padding)

Process:
1. Convert to integer: parseInt(section, 10)
2. Convert to string: String(n)

Examples:
- "1" → "1"
- "01" → "1"
- "3" → "3"
- "03" → "3"
```

### generateSlug(title)

Converts title to canonical kebab-case slug.

```
Input: Any title string
Output: Lowercase kebab-case slug

Process:
1. Convert to lowercase: title.toLowerCase()
2. Replace spaces with hyphens: replace(/\s+/g, '-')
3. Remove special characters (keep a-z, 0-9, -): replace(/[^a-z0-9-]/g, '')
4. Collapse multiple hyphens: replace(/-+/g, '-')
5. Trim leading/trailing hyphens: replace(/^-|-$/g, '')

Examples:
- "Core Concepts" → "core-concepts"
- "What is React?" → "what-is-react"
- "Setup & Installation" → "setup-installation"
- "  Multiple   Spaces  " → "multiple-spaces"
- "C++ Programming" → "c-programming"
```

### buildCanonicalPath(chapter, section, title)

Builds the canonical directory path.

```
Input: chapter, section, title
Output: ".research/sections/{canonical_chapter}-{canonical_section}-{canonical_slug}/"

Process:
1. canonical_chapter = normalizeChapter(chapter)
2. canonical_section = normalizeSection(section)
3. canonical_slug = generateSlug(title)
4. return ".research/sections/{canonical_chapter}-{canonical_section}-{canonical_slug}/"

Example:
- buildCanonicalPath("1", "02", "Core Concepts")
- → ".research/sections/01-2-core-concepts/"
```

## File Path Generation

### For /init Research

```
.research/init/summary.md
.research/init/sources.md
```

### For Section Research

```
.research/sections/{chapter}-{section}-{slug}/research.md
.research/sections/{chapter}-{section}-{slug}/sources.md
```

**Example**: Section 1.2 "Core Concepts"

```
.research/sections/01-2-core-concepts/research.md
.research/sections/01-2-core-concepts/sources.md
```

## File Format Templates

### summary.md (for /init)

```markdown
# Research Summary

> Generated: {YYYY-MM-DD}
> Topic: {topic}
> Domain: {domain}

## Key Concepts

### {Concept 1}

- **Definition**: {clear definition}
- **Importance**: {why it matters}
- **Source**: [{source name}]({url})

### {Concept 2}

- **Definition**: {clear definition}
- **Importance**: {why it matters}
- **Source**: [{source name}]({url})

## Learning Path

1. **Prerequisites**: {comma-separated list}
2. **Fundamentals**: {comma-separated list}
3. **Core Skills**: {comma-separated list}
4. **Advanced Topics**: {comma-separated list}

## Current Trends ({current_year})

- {trend 1 with source link}
- {trend 2 with source link}

## Domain-Specific Information

{domain-specific sections based on domain-profiles skill}
```

### sources.md (for both /init and sections)

```markdown
# Source Registry

> Section: {section_id or "init"}
> Generated: {YYYY-MM-DD}

## Primary Sources (High Reliability)

| Source | URL   | Type          | Last Verified |
| ------ | ----- | ------------- | ------------- |
| {name} | {url} | Official Docs | {YYYY-MM-DD}  |
| {name} | {url} | Official Docs | {YYYY-MM-DD}  |

## Secondary Sources (Medium Reliability)

| Source | URL   | Type     | Notes   |
| ------ | ----- | -------- | ------- |
| {name} | {url} | Tutorial | {notes} |
| {name} | {url} | Blog     | {notes} |

## Rejected Sources

| Source | Reason            |
| ------ | ----------------- |
| {name} | Outdated (year)   |
| {name} | Unreliable author |
```

### research.md (for sections)

````markdown
# Research: {Section Title}

> Section: {chapter}.{section} {title}
> Target Pages: {N}p
> Generated: {YYYY-MM-DD}

## Scope

{Brief description of what this section covers}

## Key Concepts

### {Concept 1}

- **Definition**: {definition}
- **Source**: [{name}]({url})

### {Concept 2}

- **Definition**: {definition}
- **Source**: [{name}]({url})

## Code Examples

### {Example Title}

```{language}
{code}
```

> Source: [{name}]({url})

## Common Pitfalls

1. **{Pitfall 1}**: {description}
   - **Cause**: {why it happens}
   - **Solution**: {how to avoid}

2. **{Pitfall 2}**: {description}
   - **Cause**: {why it happens}
   - **Solution**: {how to avoid}

## Practical Insights

- {insight 1 with source link}
- {insight 2 with source link}

## Subtopic Coverage

| Subtopic | Status   | Source            |
| -------- | -------- | ----------------- |
| {name}   | Complete | [{source}]({url}) |
| {name}   | Partial  | [{source}]({url}) |
| {name}   | Missing  | -                 |
````

## Directory Resolution Strategy

When locating research directories, use multi-tier search to handle naming inconsistencies from legacy data or different generation sources.

### Why Multi-Tier Search?

Research directories may have been created with inconsistent naming:

| Inconsistency Type     | Example Mismatch                           |
| ---------------------- | ------------------------------------------ |
| Chapter padding        | `1-2-intro` vs `01-2-intro`                |
| Section padding        | `01-02-intro` vs `01-2-intro`              |
| Slug case              | `01-2-Core-Concepts` vs `01-2-core-concepts` |
| Slug special chars     | `01-2-whats-new?` vs `01-2-whats-new`      |
| Combined inconsistency | `1-02-What's New?` vs `01-2-whats-new`     |

### Multi-Tier Search Algorithm

> **⚠️ CRITICAL: Glob Returns Files Only**
>
> Glob does NOT return directories. All patterns MUST end with a filename (e.g., `/research.md`).
>
> | Pattern | Result |
> |---------|--------|
> | `.research/sections/*9-1*` | ❌ Empty (matches directory, not returned) |
> | `.research/sections/*9-1*/research.md` | ✅ Returns file path |
> | `.research/sections/*9-1*/*` | ✅ Returns all files in matching dirs |

Execute tiers in order. Stop at first successful match.

#### Tier 1: Canonical Exact Match (Primary)

Search using fully normalized canonical path.

```
canonical_chapter = normalizeChapter(chapter)  # "1" → "01"
canonical_section = normalizeSection(section)  # "02" → "2"
canonical_slug = generateSlug(title)           # "Core Concepts" → "core-concepts"

Glob(".research/sections/{canonical_chapter}-{canonical_section}-{canonical_slug}/research.md")

Example: Glob(".research/sections/01-2-core-concepts/research.md")
```

#### Tier 2: Canonical Chapter-Section, Any Slug

If Tier 1 fails, search with canonical chapter-section but wildcard slug.

```
Glob(".research/sections/{canonical_chapter}-{canonical_section}-*/research.md")

Example: Glob(".research/sections/01-2-*/research.md")
```

This catches slug variations like `Core-Concepts`, `core_concepts`, etc.

#### Tier 3: Non-Padded Chapter Variation

If Tier 2 fails, try without chapter zero-padding (legacy compatibility).

```
raw_chapter = String(parseInt(chapter, 10))  # "01" → "1"

Glob(".research/sections/{raw_chapter}-{canonical_section}-*/research.md")

Example: Glob(".research/sections/1-2-*/research.md")
```

#### Tier 4: Flexible Pattern Match (Last Resort)

If all above fail, use section number and first slug keyword.

```
first_keyword = generateSlug(title).split('-')[0]  # "core-concepts" → "core"

Glob(".research/sections/*-{canonical_section}-*{first_keyword}*/research.md")

Example: Glob(".research/sections/*-2-*core*/research.md")
```

### Resolution Output Format

Return resolution result in XML format:

```xml
<directory_resolution>
  <input>
    <chapter>{original_chapter}</chapter>
    <section>{original_section}</section>
    <title>{original_title}</title>
  </input>
  <canonical>
    <chapter>{normalized_chapter}</chapter>
    <section>{normalized_section}</section>
    <slug>{normalized_slug}</slug>
    <path>{canonical_path}</path>
  </canonical>
  <resolution>
    <resolved_path>{matched_path OR canonical_path}</resolved_path>
    <existing>{true|false}</existing>
    <match_tier>{1|2|3|4|new}</match_tier>
  </resolution>
</directory_resolution>
```

### Resolution Logic Summary

```
function resolveResearchDirectory(chapter, section, title):
  # Normalize inputs
  c = normalizeChapter(chapter)
  s = normalizeSection(section)
  slug = generateSlug(title)
  canonical = ".research/sections/{c}-{s}-{slug}/"

  # Tier 1: Exact canonical
  result = Glob("{canonical}research.md")
  if result: return { path: canonical, existing: true, tier: 1 }

  # Tier 2: Canonical chapter-section, any slug
  result = Glob(".research/sections/{c}-{s}-*/research.md")
  if result: return { path: parent(result[0]), existing: true, tier: 2 }

  # Tier 3: Non-padded chapter
  raw_c = String(parseInt(chapter, 10))
  result = Glob(".research/sections/{raw_c}-{s}-*/research.md")
  if result: return { path: parent(result[0]), existing: true, tier: 3 }

  # Tier 4: Flexible pattern
  keyword = slug.split('-')[0]
  result = Glob(".research/sections/*-{s}-*{keyword}*/research.md")
  if result: return { path: parent(result[0]), existing: true, tier: 4 }

  # No match - use canonical for new directory
  return { path: canonical, existing: false, tier: "new" }
```

## Usage Patterns

### Checking Existing Research (UPDATED)

**IMPORTANT**: Do NOT use simple Glob. Use the multi-tier resolution strategy above.

```
# OLD (may miss existing research due to naming inconsistency)
Glob(".research/sections/{chapter}-{section}-{slug}/research.md")

# NEW (handles all variations)
resolution = resolveResearchDirectory(chapter, section, title)
existing_research = resolution.existing
research_dir = resolution.resolved_path
```

Returns resolved directory path and existence status.

### Reading Research Files

When consuming research, read files directly in agent context:

```
Read(".research/init/summary.md")
Read(".research/sections/01-2-core-concepts/research.md")
```

### Saving Research Results

Agents should Write files following the templates above:

```
Write(".research/init/summary.md", content)
Write(".research/sections/01-2-core-concepts/research.md", content)
```

## Agent-Specific Guidelines

### research-collector Agent

- Outputs to: `.research/init/summary.md`, `.research/init/sources.md`
- Creates directory if not exists
- Returns confirmation only: `research_saved:.research/init/`

### researcher Agent

- Outputs to: `.research/sections/{id}/research.md`, `.research/sections/{id}/sources.md`
- Checks existing research via Subtopic Coverage table
- Appends to existing if partial coverage
- Returns confirmation only: `research_saved:{output_dir}`

### Consumer Agents (structure-designer, writer)

- Receive file paths in prompt
- Read files directly in their own context
- Do not modify research files

## XML Output Schemas

Standardized XML schemas for agent communication. All agents should use these formats for consistency.

### Research Result Schema

Used by `research-collector` and `researcher` agents:

```xml
<research_result domain="{technology|history|science|arts|general}" status="OK|PARTIAL|ERROR">
  <summary>
    <sources_count>{N}</sources_count>
    <concepts_count>{N}</concepts_count>
    <output_path>{path}</output_path>
    <generated>{YYYY-MM-DD}</generated>
  </summary>

  <authoritative_sources>
    - [Source Name](url) - {reliability: high|medium}
  </authoritative_sources>

  <key_concepts>
    - **{Term}**: {Definition}
  </key_concepts>

  <learning_path>
    1. Prerequisites: {list}
    2. Fundamentals: {list}
    3. Core Skills: {list}
    4. Advanced: {list}
  </learning_path>

  <!-- Domain-specific sections as per domain-profiles -->
</research_result>
```

### Directory Resolution Schema

Used by `researcher` agent for path resolution:

```xml
<directory_resolution>
  <input>
    <chapter>{original_chapter}</chapter>
    <section>{original_section}</section>
    <title>{original_title}</title>
  </input>
  <canonical>
    <chapter>{normalized_chapter}</chapter>
    <section>{normalized_section}</section>
    <slug>{normalized_slug}</slug>
    <path>{canonical_path}</path>
  </canonical>
  <resolution status="FOUND|NEW">
    <resolved_path>{matched_path OR canonical_path}</resolved_path>
    <existing>{true|false}</existing>
    <match_tier>{1|2|3|4|new}</match_tier>
  </resolution>
</directory_resolution>
```

### Subtopic Coverage Schema

Used within research files to track coverage:

```xml
<subtopic_coverage>
  <subtopic name="{name}" status="Complete|Partial|Missing">
    <source>{url or "pending"}</source>
  </subtopic>
</subtopic_coverage>
```

### Status Values Reference

| Status | Context | Meaning |
|--------|---------|---------|
| OK | research_result | All subtopics covered, sufficient sources |
| PARTIAL | research_result | Some subtopics missing or incomplete |
| ERROR | research_result | Critical failure (e.g., no sources found) |
| FOUND | directory_resolution | Existing research directory located |
| NEW | directory_resolution | No existing research, use canonical path |

---

## Error Handling

| Scenario                       | Action                              |
| ------------------------------ | ----------------------------------- |
| `.research/` directory missing | Auto-create on first write          |
| Research file not found        | Conduct fresh research              |
| Read failure                   | Log warning, conduct fresh research |
| Write failure                  | Report error, do not update task.md |

## .gitignore Recommendation

Research files are regenerable and should typically be ignored:

```gitignore
# Research cache (regenerable)
.research/
```
