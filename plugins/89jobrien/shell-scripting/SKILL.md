---
name: shell-scripting
description: Shell scripting best practices and patterns. Use when writing bash/zsh
  scripts, automating tasks, creating CLI tools, or debugging shell commands.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Shell Scripting

Comprehensive shell scripting skill covering bash/zsh patterns, automation, error handling, and CLI tool development.

## When to Use This Skill

- Writing automation scripts
- Creating CLI tools
- System administration tasks
- Build and deployment scripts
- Log processing and analysis
- File manipulation and batch operations
- Cron jobs and scheduled tasks

## Script Structure

### Template

```bash
#!/usr/bin/env bash
# Script: name.sh
# Description: What this script does
# Usage: ./name.sh [options] <args>

set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'        # Safer word splitting

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Default values
VERBOSE=false
DRY_RUN=false

# Functions
usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [options] <argument>

Options:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -n, --dry-run   Show what would be done
EOF
}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

error() {
    log "ERROR: $*"
    exit 1
}

# Main logic
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            *)
                break
                ;;
        esac
    done

    # Your logic here
}

main "$@"
```

## Error Handling

### Set Options

```bash
set -e          # Exit on any error
set -u          # Error on undefined variables
set -o pipefail # Pipe failure is script failure
set -x          # Debug: print each command (use sparingly)
```

### Trap for Cleanup

```bash
cleanup() {
    rm -f "$TEMP_FILE"
    log "Cleanup complete"
}
trap cleanup EXIT

# Also handle specific signals
trap 'error "Script interrupted"' INT TERM
```

### Error Checking Patterns

```bash
# Check command exists
command -v jq >/dev/null 2>&1 || error "jq is required but not installed"

# Check file exists
[[ -f "$FILE" ]] || error "File not found: $FILE"

# Check directory exists
[[ -d "$DIR" ]] || mkdir -p "$DIR"

# Check variable is set
[[ -n "${VAR:-}" ]] || error "VAR is not set"

# Check exit status explicitly
if ! some_command; then
    error "some_command failed"
fi
```

## Variables & Substitution

### Variable Expansion

```bash
# Default values
${VAR:-default}     # Use default if VAR is unset or empty
${VAR:=default}     # Set VAR to default if unset or empty
${VAR:+value}       # Use value if VAR is set
${VAR:?error msg}   # Error if VAR is unset or empty

# String manipulation
${VAR#pattern}      # Remove shortest prefix match
${VAR##pattern}     # Remove longest prefix match
${VAR%pattern}      # Remove shortest suffix match
${VAR%%pattern}     # Remove longest suffix match
${VAR/old/new}      # Replace first occurrence
${VAR//old/new}     # Replace all occurrences
${#VAR}             # Length of VAR
```

### Arrays

```bash
# Declare array
declare -a ARRAY=("one" "two" "three")

# Access elements
echo "${ARRAY[0]}"     # First element
echo "${ARRAY[@]}"     # All elements
echo "${#ARRAY[@]}"    # Number of elements
echo "${!ARRAY[@]}"    # All indices

# Iterate
for item in "${ARRAY[@]}"; do
    echo "$item"
done

# Append
ARRAY+=("four")
```

### Associative Arrays

```bash
declare -A MAP
MAP["key1"]="value1"
MAP["key2"]="value2"

# Access
echo "${MAP[key1]}"

# Check key exists
[[ -v MAP[key1] ]] && echo "key1 exists"

# Iterate
for key in "${!MAP[@]}"; do
    echo "$key: ${MAP[$key]}"
done
```

## Control Flow

### Conditionals

```bash
# String comparison
[[ "$str" == "value" ]]
[[ "$str" != "value" ]]
[[ -z "$str" ]]  # Empty
[[ -n "$str" ]]  # Not empty

# Numeric comparison
[[ "$num" -eq 5 ]]  # Equal
[[ "$num" -ne 5 ]]  # Not equal
[[ "$num" -lt 5 ]]  # Less than
[[ "$num" -gt 5 ]]  # Greater than

# File tests
[[ -f "$file" ]]  # File exists
[[ -d "$dir" ]]   # Directory exists
[[ -r "$file" ]]  # Readable
[[ -w "$file" ]]  # Writable
[[ -x "$file" ]]  # Executable

# Logical operators
[[ "$a" && "$b" ]]  # AND
[[ "$a" || "$b" ]]  # OR
[[ ! "$a" ]]        # NOT
```

### Loops

```bash
# For loop
for i in {1..10}; do
    echo "$i"
done

# While loop
while read -r line; do
    echo "$line"
done < "$file"

# Process substitution
while read -r line; do
    echo "$line"
done < <(command)

# C-style for
for ((i=0; i<10; i++)); do
    echo "$i"
done
```

## Input/Output

### Reading Input

```bash
# Read from user
read -r -p "Enter name: " name

# Read password (hidden)
read -r -s -p "Password: " password

# Read with timeout
read -r -t 5 -p "Quick! " answer

# Read file line by line
while IFS= read -r line; do
    echo "$line"
done < "$file"
```

### Output & Redirection

```bash
# Redirect stdout
command > file      # Overwrite
command >> file     # Append

# Redirect stderr
command 2> file

# Redirect both
command &> file
command > file 2>&1

# Discard output
command > /dev/null 2>&1

# Tee (output and save)
command | tee file
```

## Text Processing

### Common Patterns

```bash
# Find and process files
find . -name "*.log" -exec grep "ERROR" {} +

# Process CSV
while IFS=, read -r col1 col2 col3; do
    echo "$col1: $col2"
done < file.csv

# JSON processing (with jq)
jq '.key' file.json
jq -r '.items[]' file.json

# AWK one-liners
awk '{print $1}' file           # First column
awk -F: '{print $1}' /etc/passwd  # Custom delimiter
awk 'NR > 1' file               # Skip header

# SED one-liners
sed 's/old/new/g' file          # Replace all
sed -i 's/old/new/g' file       # In-place edit
sed -n '10,20p' file            # Print lines 10-20
```

## Best Practices

### Do

- Quote all variable expansions: `"$VAR"`
- Use `[[ ]]` over `[ ]` for tests
- Use `$(command)` over backticks
- Check return values
- Use `readonly` for constants
- Use `local` in functions
- Provide `--help` option
- Use meaningful exit codes

### Don't

- Parse `ls` output
- Use `eval` with untrusted input
- Assume paths don't have spaces
- Ignore shellcheck warnings
- Write one giant script (modularize)

## Reference Files

- **`references/one_liners.md`** - Useful one-liner commands

## Integration with Other Skills

- **developer-experience** - For tooling automation
- **debugging** - For script debugging
- **testing** - For script testing patterns
