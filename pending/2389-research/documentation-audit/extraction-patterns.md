# Claim Extraction Patterns

Reference for identifying verifiable claims in documentation.

## Pattern Recognition

### File References (`file_ref`)

**Signals:**
- Backticked paths: `` `scripts/foo.py` ``
- Code block paths: `python scripts/foo.py`
- Directory structures in prose
- "located at", "found in", "see file"

**Extraction regex:**
```
`[a-zA-Z0-9_/.-]+\.(py|sh|md|sql|liq|json|yaml|yml|toml|service|timer)`
```

**Verification:**
```python
import os
os.path.exists(claim.artifact)  # or Glob search for partial matches
```

### Configuration Defaults (`config_default`)

**Signals:**
- "defaults to X"
- "Default: X"
- "default value is X"
- Tables with "Default" column
- .env examples with `VAR=value`

**Extraction regex:**
```
(?:defaults? to|Default:?|default value is)\s*[`'"]?([^`'".\n]+)
```

**Verification sources (priority order):**
1. `.env.example` - documented defaults
2. `src/**/config/*.py` - config modules
3. Code: `os.getenv("VAR", "default")`
4. Schema files (JSON Schema, Pydantic models)

### Environment Variables (`env_var`)

**Signals:**
- UPPERCASE_WITH_UNDERSCORES
- `$VAR` or `${VAR}` syntax
- "set X=" in bash blocks
- Environment tables

**Extraction regex:**
```
\b[A-Z][A-Z0-9_]{2,}\b
```

**Filter out false positives:**
- Common acronyms: HTTP, API, JSON, SQL, URL
- Standard vars: PATH, HOME, USER

**Verification:**
```bash
grep -r "os.getenv.*VAR\|environ.*VAR" src/
grep "^VAR=" .env.example
```

### CLI Commands (`cli_command`)

**Signals:**
- `--flag` or `-f` patterns
- `script.py [args]` in code blocks
- Command tables
- "Usage:" sections

**Extraction patterns:**
```
--[a-z][a-z0-9-]+    # Long flags
-[a-zA-Z]            # Short flags
script\.py\s+\S+     # Script with args
```

**Verification:**
```bash
python scripts/foo.py --help 2>&1 | grep -q "\-\-flag"
grep -E "add_argument.*--flag|argparse" scripts/foo.py
```

### Behavioral Claims (`behavior`)

**Signals:**
- "every N seconds/minutes"
- "runs at :00"
- "retries N times"
- "waits for", "timeout"
- "automatically X when Y"

**Extraction patterns:**
```
every \d+ (?:second|minute|hour)s?
runs? (?:at|every) [:\d]+
retries? \d+ times?
(?:wait|timeout|delay).*\d+
automatically \w+
```

**Verification approach:**
1. Search code for related logic
2. Check systemd timers: `OnCalendar=`, `OnUnitActiveSec=`
3. Extract evidence, flag for human review

## Claim Confidence Scoring

| Type | Auto-Verifiable | Confidence |
|------|-----------------|------------|
| `file_ref` | Yes | High |
| `config_default` | Yes | High |
| `env_var` | Yes | High |
| `cli_command` | Yes | High |
| `symbol_ref` | Partial | Medium |
| `version_req` | Partial | Medium |
| `behavior` | No | Low (human) |
| `constraint` | No | Low (human) |

## Pattern Expansion Templates

When you find a false claim, search for similar patterns:

### Dead Script Pattern
```
Found: scripts/diagnose_track_selection.py (doesn't exist)
Search: grep -rn "scripts/[a-z_]*\.py" docs/
Verify: Each match against actual scripts/ directory
```

### Wrong Interval Pattern
```
Found: "every 10 seconds" (actually 2 minutes)
Search: grep -rn "every [0-9]* \(second\|minute\)" docs/
Verify: Each against actual timer configuration
```

### Renamed Service Pattern
```
Found: ai-radio-break-gen.service (renamed to generate-break.service)
Search: grep -rn "ai-radio-[a-z-]*\.\(service\|timer\)" docs/
Verify: Each against systemd/ directory
```

### Deprecated Config Pattern
```
Found: RADIO_OLD_VAR (removed)
Search: grep -rn "RADIO_[A-Z_]*" docs/
Verify: Each against .env.example and code
```

## False Positive Filters

Skip these during extraction:

1. **Example blocks** - `<!-- example -->`, "For example:"
2. **Hypothetical** - "would be", "could use", "might"
3. **Historical** - "previously", "used to", "was"
4. **External refs** - URLs, package names, external tools
5. **Prose descriptions** - General explanations without specific values
