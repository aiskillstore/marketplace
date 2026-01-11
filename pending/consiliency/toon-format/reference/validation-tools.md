# TOON Validation Tools

Tools and scripts for validating and fixing TOON files.

## Official CLI

```bash
# Validate with official CLI (use --decode, not validate!)
npx @toon-format/cli --decode file.toon > /dev/null

# Check exit code
echo $?  # 0 = valid, non-zero = errors
```

**Note:** Use `--decode`, not `validate`. The decode command is the validation mechanism.

## Auto-Fix Scripts

Run these in order when fixing TOON files:

```bash
# 1. Remove comments (TOON doesn't support them)
python3 .claude/ai-dev-kit/dev-tools/scripts/fix_toon_comments.py path/

# 2. Convert YAML-style lists to tabular arrays
python3 .claude/ai-dev-kit/dev-tools/scripts/fix_toon_yaml_lists.py path/

# 3. Fix nested lists in tabular cells
python3 .claude/ai-dev-kit/dev-tools/scripts/fix_toon_nested_lists.py path/

# 4. Replace commas with semicolons in quoted cells
python3 .claude/ai-dev-kit/dev-tools/scripts/fix_toon_commas.py path/

# 5. Replace pipes with valid delimiters
python3 .claude/ai-dev-kit/dev-tools/scripts/fix_toon_pipes.py path/

# 6. Convert multiline strings to escaped format
python3 .claude/ai-dev-kit/dev-tools/scripts/fix_toon_multiline.py path/

# 7. Add blank lines after tabular arrays
python3 .claude/ai-dev-kit/dev-tools/scripts/fix_toon_blank_lines.py path/
```

## Batch Validation

```bash
# Validate all .toon files in a directory
for f in ai-docs/**/*.toon; do
  if ! npx @toon-format/cli --decode "$f" > /dev/null 2>&1; then
    echo "Invalid: $f"
  fi
done
```

## Libraries

| Language | Package | Installation |
|----------|---------|--------------|
| TypeScript/JS | `@toon-format/toon` | `npm install @toon-format/toon` |
| Python | `python-toon` | `uv pip install python-toon` |

## Online Tools

- **Playground**: https://toontools.vercel.app/playground
- **Specification**: https://toonformat.dev/

## Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Unexpected character" | Comment in file | Remove `#` lines |
| "Expected count" | Missing `[N]` in array | Add `[count]` to array declaration |
| "Invalid row" | Missing indentation | Add 2-space indent to rows |
| "Unexpected end" | Missing blank line | Add blank line after arrays |

## Integration with CI

```yaml
# GitHub Actions example
- name: Validate TOON files
  run: |
    npm install -g @toon-format/cli
    find ai-docs -name "*.toon" -exec npx @toon-format/cli --decode {} \;
```
