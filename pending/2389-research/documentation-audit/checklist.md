# Documentation Audit Execution Checklist

Use TodoWrite to track these as you execute the audit.

## Phase 1: Setup

- [ ] Identify target docs (user-facing markdown in docs/, README.md)
- [ ] Exclude: `docs/plans/`, `docs/audits/`, design docs
- [ ] Note current git commit: `git rev-parse --short HEAD`
- [ ] Create output directory: `mkdir -p docs/audits`

## Phase 2: Pass 1 - Extraction

For each target doc, use parallel Task agents to extract claims:

- [ ] Extract `file_ref` claims (paths in backticks, code blocks)
- [ ] Extract `config_default` claims ("defaults to", "Default:")
- [ ] Extract `env_var` claims (UPPERCASE_VARS)
- [ ] Extract `cli_command` claims (--flags, script invocations)
- [ ] Extract `behavior` claims (timing, intervals, counts)

**Extraction prompt for each doc:**
```
Extract all verifiable claims from [DOC]. For each claim record:
- Line number
- Claim text (verbatim)
- Claim type (file_ref, config_default, env_var, cli_command, behavior)
- Artifact to verify (the specific file/var/flag)
- Expected value (if applicable)

Focus on: paths, defaults, environment variables, CLI flags, timing/intervals.
Skip: prose descriptions, opinions, marketing language.
```

## Phase 3: Pass 1 - Verification

For each extracted claim:

- [ ] **file_ref:** `test -e <path>` or Glob search
- [ ] **config_default:** Check .env.example, config modules, code defaults
- [ ] **env_var:** Grep for usage in code, check .env.example
- [ ] **cli_command:** Check script's argparse/flags
- [ ] **behavior:** Flag for human review, extract supporting evidence

Record for each:
- Verdict: TRUE / FALSE / NEEDS_REVIEW
- Evidence: file:line or "not found"
- Suggested fix (if FALSE)

## Phase 4: Pass 2A - Pattern Expansion

- [ ] Group false claims by pattern type
- [ ] For each pattern, search ALL docs for similar claims
- [ ] Verify newly discovered claims

**Common expansion searches:**
```bash
# Dead scripts pattern
grep -rn "scripts/.*\.py" docs/ | grep -v "batch_ingest\|enqueue\|schedule"

# Wrong intervals pattern
grep -rn "every [0-9]* \(second\|minute\)" docs/

# Service/timer names
grep -rn "ai-radio-.*\.\(service\|timer\)" docs/

# Environment variables
grep -rn "RADIO_[A-Z_]*" docs/
```

## Phase 5: Pass 2B - Gap Detection

- [ ] List actual scripts: `ls scripts/*.py`
- [ ] List documented scripts in SCRIPTS.md
- [ ] Flag undocumented scripts
- [ ] Flag documented-but-missing scripts

Repeat for:
- [ ] systemd services/timers
- [ ] config modules
- [ ] API endpoints

## Phase 6: Report Generation

- [ ] Create `docs/audits/AUDIT_REPORT_YYYY-MM-DD.md`
- [ ] Include executive summary with metrics
- [ ] List false claims with line numbers and fixes
- [ ] Summarize patterns discovered
- [ ] Create human review queue for behavioral claims

## Anti-Patterns

**Don't:**
- Skip Pass 2 (catches 10-20% more issues)
- Trust "looks correct" without verification
- Fix claims without citing evidence (file:line)
- Audit design docs or plans (historical artifacts)
- Batch verification before extraction is complete

**Do:**
- Use parallel agents for extraction (one per doc)
- Record evidence for every verdict
- Re-run after major refactors
- Prioritize user-facing docs over internal
