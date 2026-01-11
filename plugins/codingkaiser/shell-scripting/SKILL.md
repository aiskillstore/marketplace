---
name: shell-scripting
description: Specialized knowledge of Bash and Zsh scripting, shell automation, command-line tools, and scripting best practices. Use when the user needs to write, debug, or optimize shell scripts, work with command-line tools, automate tasks with bash/zsh, or asks for shell script help.
---

# Shell Scripting Expert

Expert guidance for writing robust, maintainable Bash and Zsh scripts with best practices for automation and command-line tool usage.

## Script Structure Essentials

Start every script with:
```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

- `set -e`: Exit on error
- `set -u`: Error on undefined variables
- `set -o pipefail`: Catch errors in pipes
- `IFS=$'\n\t'`: Safer word splitting

## Critical Best Practices

1. **Always quote variables**: `"$variable"` not `$variable`
2. **Use `[[` for conditionals** (Bash): `if [[ "$var" == "value" ]]; then`
3. **Check command existence**: `if command -v git &> /dev/null; then`
4. **Avoid parsing `ls`**: Use globs or `find` instead
5. **Use arrays for lists**: `files=("file1" "file2")` not space-separated strings
6. **Handle errors with traps**:
   ```bash
   trap cleanup EXIT
   trap 'echo "Error on line $LINENO"' ERR
   ```

## Common Patterns

### Argument Parsing
```bash
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help) usage; exit 0 ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -*) echo "Unknown option: $1"; exit 1 ;;
        *) break ;;
    esac
done
```

### Safe File Iteration
```bash
# Prefer this (handles spaces, newlines correctly):
while IFS= read -r -d '' file; do
    echo "Processing: $file"
done < <(find . -type f -name "*.txt" -print0)

# Or with simple globs:
for file in *.txt; do
    [[ -e "$file" ]] || continue  # Skip if no matches
    echo "Processing: $file"
done
```

### User Confirmation
```bash
read -rp "Continue? [y/N] " response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Continuing..."
fi
```

### Colored Output
```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

echo -e "${GREEN}Success${NC}"
echo -e "${RED}Error${NC}" >&2
```

## Modern Tool Alternatives

When appropriate, suggest these modern replacements:
- `ripgrep` (rg) → faster than grep
- `fd` → faster than find
- `fzf` → interactive filtering
- `jq` → JSON processing
- `yq` → YAML processing
- `bat` → cat with syntax highlighting
- `eza` → enhanced ls

## Function Organization

```bash
usage() {
    cat <<EOF
Usage: ${0##*/} [OPTIONS] <args>
Description of what this script does.
OPTIONS:
    -h, --help      Show this help
    -v, --verbose   Verbose output
EOF
}

main() {
    # Main logic here
    :
}
```

## Zsh-Specific Features

When user specifies Zsh:
- Advanced globbing: `**/*.txt` (recursive), `*.txt~*test*` (exclude pattern)
- Parameter expansion: `${var:u}` (uppercase), `${var:l}` (lowercase)
- Associative arrays: `typeset -A hash; hash[key]=value`
- Extended globbing: Enable with `setopt extended_glob`

## Security Considerations

- **Never** `eval` untrusted input
- Validate user input before use
- Use `mktemp` for temporary files: `TEMP_FILE=$(mktemp)`
- Be explicit with `rm -rf` operations
- Check for TOCTOU (Time-Of-Check-Time-Of-Use) race conditions
- Don't store secrets in scripts; use environment variables or secret managers

## Performance Tips

- Use built-ins over external commands (`[[ ]]` vs `test`, `$(( ))` vs `expr`)
- Avoid unnecessary subshells: `var=$(cat file)` → `var=$(<file)`
- Use `read` not `cat | while`: `while read -r line; do ... done < file`
- Consider `xargs -P` or GNU `parallel` for parallel processing

## Quick Reference Template

See references/template.sh for a complete, production-ready script template with all best practices incorporated.
