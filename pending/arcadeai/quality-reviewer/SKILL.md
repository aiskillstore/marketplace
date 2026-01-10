---
name: quality-reviewer
description: Deep code quality review with web research. Use when user explicitly requests verification against latest docs ('double check against latest', 'verify versions', 'check security'), needs deeper analysis beyond automatic hook, or is working on projects without SAFEWORD.md/CLAUDE.md. Fetches current documentation (WebFetch), checks latest versions (WebSearch), and provides deep analysis (performance, security, alternatives).
allowed-tools: '*'
---

# Quality Reviewer

Deep quality review with web research to verify code against the latest ecosystem state.

**Primary differentiator**: Web research (WebSearch, WebFetch) to verify against current versions, documentation, and best practices.

**Triggers**:

- **Explicit web research request**: "double check against latest docs", "verify we're using latest version", "check for security issues"
- **Deep dive needed**: User wants analysis beyond automatic hook (performance, architecture alternatives, trade-offs)
- **No SAFEWORD.md/CLAUDE.md**: Projects without context files (automatic hook won't run, manual review needed)
- **Pre-change review**: User wants review before making changes (automatic hook only triggers after changes)
- **Model-invoked**: Claude determines web research would be valuable

**Relationship to automatic quality hook**:

- **Automatic hook**: Fast quality check using existing knowledge + project context (guaranteed, runs on every change)
- **This skill**: Deep review with web research when verification against current ecosystem is needed (on-demand, 2-3 min)

## Review Protocol

### 1. Identify What Changed

Understand context:

- What files were just modified?
- What problem is being solved?
- What was the implementation approach?

### 2. Read Project Standards

```bash
ls CLAUDE.md SAFEWORD.md ARCHITECTURE.md .claude/
```

Read relevant standards:

- `CLAUDE.md` or `SAFEWORD.md` - Project-specific guidelines
- `ARCHITECTURE.md` - Architectural principles
- `@./.safeword/guides/code-philosophy.md` - Core coding principles

### 3. Evaluate Correctness

**Will it work?**

- Does the logic make sense?
- Are there obvious bugs?

**Edge cases:**

- Empty inputs, null/undefined, boundary conditions (0, -1, max)?
- Concurrent access, network failures?

**Error handling:**

- Are errors caught appropriately?
- Helpful error messages?
- Cleanup handled (resources, connections)?

**Logic errors:**

- Off-by-one errors, race conditions, wrong assumptions?

### 4. Evaluate Anti-Bloat

- Are all dependencies necessary? Could we use stdlib/built-ins?
- Are abstractions solving real problems or imaginary ones?
- YAGNI: Is this feature actually needed now?

### 5. Evaluate Elegance

- Is the code easy to understand?
- Are names clear and descriptive?
- Is the intent obvious?
- Will this be easy to change later?

### 6. Check Standards Compliance

**Project standards** (from CLAUDE.md/SAFEWORD.md/ARCHITECTURE.md):

- Does it follow established patterns?
- Does it violate any documented principles?

**Library best practices:**

- Are we using libraries correctly?
- Are we following official documentation?

### 7. Verify Latest Versions ⭐ **PRIMARY VALUE**

**CRITICAL**: This is your main differentiator from automatic hook. ALWAYS check versions.

```
WebSearch: "[library name] latest stable version 2025"
WebSearch: "[library name] security vulnerabilities"
```

**Flag if outdated:**

- Major versions behind → WARN (e.g., React 17 when 19 is stable)
- Minor versions behind → NOTE (e.g., React 19.0.0 when 19.1.0 is stable)
- Security vulnerabilities → CRITICAL (must upgrade)
- Using latest → Confirm

**Common libraries**: React, TypeScript, Vite, Next.js, Node.js, Vitest, Playwright, Jest, esbuild

**Check even if dependencies didn't change** - User might be using outdated patterns.

### 8. Verify Latest Documentation ⭐ **PRIMARY VALUE**

**CRITICAL**: This is your main differentiator from automatic hook. ALWAYS verify against current docs.

```
WebFetch: https://react.dev (for React)
WebFetch: https://vitejs.dev (for Vite)
WebFetch: https://www.electronjs.org/docs (for Electron)
```

**Look for:**

- Are we using deprecated APIs?
- Are there newer, better patterns?
- Did the library's recommendations change since training data?

**Cache results**: If you checked docs recently in this session, don't re-fetch.

## Output Format

**Simple question** ("is it correct?"):

```
**Correctness:** ✓ Logic is sound, edge cases handled, no obvious errors.
```

**Full review** ("double check and critique"):

```markdown
## Quality Review

**Correctness:** [✓/⚠️/❌] [Brief assessment]
**Anti-Bloat:** [✓/⚠️/❌] [Brief assessment]
**Elegance:** [✓/⚠️/❌] [Brief assessment]
**Standards:** [✓/⚠️/❌] [Brief assessment]
**Versions:** [✓/⚠️/❌] [Latest version check with WebSearch]
**Documentation:** [✓/⚠️/❌] [Current docs check with WebFetch]

**Verdict:** [APPROVE / REQUEST CHANGES / NEEDS DISCUSSION]

**Critical issues:** [List or "None"]
**Suggested improvements:** [List or "None"]
```

Use structured format for "double check"/"critique". Use brief format for specific questions.

## Example: Full Review

```markdown
## Quality Review

**Correctness:** ✓ Logic sound, edge cases covered, error handling adequate
**Anti-Bloat:** ✓ Minimal dependencies, appropriate abstractions
**Elegance:** ✓ Clear code, good naming, well-structured
**Standards:** ✓ Follows CLAUDE.md patterns
**Versions:** ✓ React 19.0.0 (latest stable), TypeScript 5.7.2 (latest)
**Documentation:** ✓ Using current React patterns per https://react.dev

**Verdict:** APPROVE - Production ready

**Critical issues:** None
**Suggested improvements:** None
```

## Critical Reminders

1. **Primary value: Web research** - Use WebSearch/WebFetch to verify against current ecosystem (versions, docs, security)
2. **Complement automatic hook** - Hook does fast check with existing knowledge, you do deep dive with web research
3. **Explicit triggers matter** - "double check against latest docs", "verify versions", "check security" = invoke web research
4. **Projects without SAFEWORD.md** - Automatic hook won't run, you're the only quality check
5. **Always check latest docs** - Verify patterns are current, not outdated (WebFetch)
6. **Always verify versions** - Flag outdated dependencies (WebSearch)
7. **Be thorough but concise** - Cover all areas but keep explanations brief
8. **Provide actionable feedback** - Specific line numbers, concrete suggestions
9. **Clear verdict** - Always end with APPROVE/REQUEST CHANGES/NEEDS DISCUSSION
10. **Separate critical vs nice-to-have** - User needs to know what's blocking vs optional

## Non-Obvious Edge Cases

**User requests review after automatic hook ran:**

- Acknowledge hook ran: "The automatic quality hook already did a fast check. I'll now do deeper analysis with web research..."
- Focus on what automatic hook doesn't do: fetch latest docs, verify versions, security checks, performance analysis

**WebSearch/WebFetch fails:**

- Continue review without version/docs checks
- Note: "Couldn't verify latest versions/docs, skipping that check"

**Project has no CLAUDE.md/SAFEWORD.md:**

- Use `@./.safeword/guides/code-philosophy.md` as fallback
- Note: "No project-specific standards found, using general best practices"
