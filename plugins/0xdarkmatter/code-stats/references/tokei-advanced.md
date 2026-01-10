# tokei Advanced Usage

Complete reference for tokei code statistics tool.

## Filtering Options

### By Language

```bash
# Only specific languages
tokei --type=TypeScript,JavaScript,Python
tokei -t TypeScript,Rust

# Exclude languages
tokei --exclude-lang=Markdown,JSON

# List all recognized languages
tokei --languages
```

### By Path

```bash
# Specific directories
tokei src/ lib/ tests/

# Exclude directories
tokei --exclude node_modules --exclude dist --exclude vendor
tokei -e "*.test.*" -e "*.spec.*"

# Include hidden files
tokei --hidden

# Include gitignored files
tokei --no-ignore
```

### By Depth

```bash
# Limit directory depth
tokei --max-depth 2

# Only files in current directory
tokei --max-depth 1
```

## Output Formats

### Default Table

```bash
tokei
# ===============================================================================
#  Language            Files        Lines         Code     Comments       Blanks
# ===============================================================================
#  TypeScript             45        12847         9823         1456         1568
#  JavaScript             12         2341         1876          234          231
# ===============================================================================
```

### Compact

```bash
tokei --compact
# -------------------------------------------------------------------------------
#  TypeScript   45   12847    9823    1456    1568
#  JavaScript   12    2341    1876     234     231
# -------------------------------------------------------------------------------
```

### JSON

```bash
tokei --output json
# {"TypeScript":{"blanks":1568,"code":9823,"comments":1456,"lines":12847},...}

# Pretty print with jq
tokei --output json | jq .

# Extract specific language
tokei --output json | jq '.TypeScript.code'

# Get total lines
tokei --output json | jq '.Total.code'
```

### YAML

```bash
tokei --output yaml
# TypeScript:
#   blanks: 1568
#   code: 9823
#   comments: 1456
#   lines: 12847
```

## Sorting

```bash
# Sort by lines of code (default)
tokei --sort code

# Sort by number of files
tokei --sort files

# Sort by comments
tokei --sort comments

# Sort by blank lines
tokei --sort blanks

# Sort by total lines
tokei --sort lines
```

## Per-File Statistics

```bash
# Show statistics per file
tokei --files

# JSON with file details
tokei --output json --files | jq '.TypeScript.reports[].name'
```

## Common Workflows

### Compare Before/After

```bash
# Before refactoring
tokei --output json > before.json

# Make changes...

# After refactoring
tokei --output json > after.json

# Compare
diff before.json after.json

# Or with jq
echo "Before: $(jq '.Total.code' before.json), After: $(jq '.Total.code' after.json)"
```

### CI Size Limits

```bash
#!/bin/bash
# Check codebase size limits in CI

MAX_LINES=100000
LINES=$(tokei --output json | jq '.Total.code')

if [ "$LINES" -gt "$MAX_LINES" ]; then
    echo "ERROR: Codebase exceeds $MAX_LINES lines (current: $LINES)"
    exit 1
fi

echo "Codebase size OK: $LINES lines"
```

### Language Breakdown Report

```bash
#!/bin/bash
# Generate language breakdown report

echo "# Code Statistics Report"
echo "Generated: $(date)"
echo
tokei --compact --sort code
echo
echo "## Details"
tokei --output json | jq -r '
  to_entries |
  sort_by(-.value.code) |
  .[] |
  select(.key != "Total") |
  "- \(.key): \(.value.code) lines (\(.value.files) files)"
'
```

### Track Growth Over Time

```bash
#!/bin/bash
# Append to stats history

DATE=$(date +%Y-%m-%d)
STATS=$(tokei --output json | jq -c '{date: "'"$DATE"'", stats: .Total}')
echo "$STATS" >> code_stats_history.jsonl

# View history
cat code_stats_history.jsonl | jq -s '.'
```

## Configuration File

Create `.tokeirc` or `tokei.toml` in project root:

```toml
# tokei.toml
columns = 80
files = false
hidden = false
no_ignore = false
sort = "code"
types = ["TypeScript", "JavaScript", "Python"]

[languages.TypeScript]
line_comment = ["//"]
multi_line = ["/*", "*/"]
quotes = [["\"", "\""], ["'", "'"]]
```

## Understanding Output

| Column | Meaning |
|--------|---------|
| Files | Number of files of this language |
| Lines | Total lines (code + comments + blanks) |
| Code | Non-blank, non-comment lines |
| Comments | Lines that are comments |
| Blanks | Empty/whitespace-only lines |

### What Counts as Code?

- Executable statements
- Declarations
- Import/export statements
- NOT: comments, blank lines, documentation strings (in some languages)

## Comparison with Other Tools

| Feature | tokei | cloc | sloccount | wc -l |
|---------|-------|------|-----------|-------|
| Speed | Fastest | Slow | Medium | Fastest |
| Language detection | Yes | Yes | Yes | No |
| Comment detection | Yes | Yes | Yes | No |
| .gitignore respect | Yes | Yes | No | No |
| JSON output | Yes | Yes | No | No |
| Multi-threaded | Yes | No | No | No |
| Memory usage | Low | High | Medium | Lowest |

## Tips

1. **Use `--compact` for quick overview** - easier to scan
2. **Pipe JSON to jq for scripting** - machine-readable output
3. **Exclude generated code** - `--exclude dist --exclude generated`
4. **Compare branches** - checkout each, run tokei, diff results
5. **Regular tracking** - run in CI to catch unexpected growth
