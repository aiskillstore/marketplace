# Common Shell Scripting Patterns

This reference contains frequently-used patterns and solutions for shell scripting challenges.

## File and Directory Operations

### Check if file/directory exists
```bash
if [[ -f "$file" ]]; then
    echo "File exists"
fi

if [[ -d "$dir" ]]; then
    echo "Directory exists"
fi

# Check if file exists and is not empty
if [[ -s "$file" ]]; then
    echo "File exists and has content"
fi
```

### Create directory if it doesn't exist
```bash
mkdir -p "$dir"
```

### Find and process files safely
```bash
# Method 1: Using find with null delimiter (safest)
while IFS= read -r -d '' file; do
    echo "Processing: $file"
done < <(find . -type f -name "*.txt" -print0)

# Method 2: Using find with -exec
find . -type f -name "*.txt" -exec process_function {} \;

# Method 3: Simple glob (when no subdirectories)
shopt -s nullglob  # Bash only
for file in *.txt; do
    echo "Processing: $file"
done
```

### Read file line by line
```bash
# Correct way
while IFS= read -r line; do
    echo "$line"
done < file.txt

# Or with process substitution
while IFS= read -r line; do
    echo "$line"
done < <(command)
```

### Get file information
```bash
# File size
size=$(stat -f%z "$file")  # macOS
size=$(stat -c%s "$file")  # Linux

# File modification time
mtime=$(stat -f%m "$file")  # macOS
mtime=$(stat -c%Y "$file")  # Linux

# Portable basename and dirname
filename="${path##*/}"
dirname="${path%/*}"

# File extension
extension="${filename##*.}"
name="${filename%.*}"
```

## String Operations

### String manipulation
```bash
# Uppercase/lowercase (Bash 4+)
upper="${string^^}"
lower="${string,,}"

# Remove prefix/suffix
no_prefix="${string#prefix}"   # Remove shortest match
no_prefix="${string##prefix}"  # Remove longest match
no_suffix="${string%suffix}"   # Remove shortest match
no_suffix="${string%%suffix}"  # Remove longest match

# Replace substring
new_string="${string/old/new}"   # Replace first occurrence
new_string="${string//old/new}"  # Replace all occurrences

# String length
length="${#string}"

# Substring
substr="${string:start:length}"
```

### Check if string contains substring
```bash
if [[ "$string" == *"substring"* ]]; then
    echo "Contains substring"
fi

# Using grep
if echo "$string" | grep -q "pattern"; then
    echo "Contains pattern"
fi
```

### String comparison
```bash
# Equality
if [[ "$str1" == "$str2" ]]; then
    echo "Strings are equal"
fi

# Pattern matching
if [[ "$string" == pattern* ]]; then
    echo "Matches pattern"
fi

# Regular expression
if [[ "$string" =~ ^[0-9]+$ ]]; then
    echo "String is numeric"
fi
```

## Array Operations

### Array basics
```bash
# Create array
arr=("item1" "item2" "item3")

# Add to array
arr+=("item4")

# Access elements
echo "${arr[0]}"      # First element
echo "${arr[@]}"      # All elements
echo "${#arr[@]}"     # Array length

# Iterate over array
for item in "${arr[@]}"; do
    echo "$item"
done

# Iterate with index
for i in "${!arr[@]}"; do
    echo "Index $i: ${arr[$i]}"
done
```

### Check if array contains value
```bash
contains() {
    local value=$1
    shift
    local arr=("$@")
    
    for item in "${arr[@]}"; do
        if [[ "$item" == "$value" ]]; then
            return 0
        fi
    done
    return 1
}

if contains "target" "${arr[@]}"; then
    echo "Array contains target"
fi
```

## Process Management

### Background processes
```bash
# Run in background
command &
pid=$!

# Wait for background process
wait $pid

# Check if process is running
if kill -0 $pid 2>/dev/null; then
    echo "Process is running"
fi
```

### Process timeout
```bash
# Using timeout command (GNU coreutils)
timeout 30s command

# Manual implementation
command &
pid=$!
sleep 30
if kill -0 $pid 2>/dev/null; then
    kill $pid
    echo "Command timed out"
fi
```

### Parallel execution
```bash
# Using xargs
find . -name "*.txt" -print0 | xargs -0 -P 4 -I {} process_file {}

# Using GNU parallel (if available)
parallel process_file ::: file1 file2 file3

# Manual parallel execution
for file in *.txt; do
    process_file "$file" &
done
wait  # Wait for all background jobs
```

## Input/Output Redirection

### Standard redirections
```bash
# Redirect stdout to file
command > file

# Redirect stderr to file
command 2> file

# Redirect both stdout and stderr
command &> file
command > file 2>&1

# Append instead of overwrite
command >> file

# Redirect stderr to stdout
command 2>&1

# Discard output
command > /dev/null 2>&1
```

### Here documents
```bash
# Basic here document
cat <<EOF
This is a multi-line
string with variable expansion: $var
EOF

# Without variable expansion
cat <<'EOF'
This is a multi-line
string with literal $var
EOF

# Indented here document
cat <<-EOF
	This ignores leading tabs
	Useful for indenting
EOF
```

## Error Handling

### Check command exit status
```bash
if command; then
    echo "Command succeeded"
else
    echo "Command failed"
fi

# Or store exit code
command
exit_code=$?
if [[ $exit_code -eq 0 ]]; then
    echo "Success"
fi
```

### Robust error handling
```bash
set -euo pipefail

# Custom error handler
error_exit() {
    echo "Error: $1" >&2
    exit "${2:-1}"
}

# Usage
[[ -f "$file" ]] || error_exit "File not found: $file" 2
```

### Trap signals
```bash
# Cleanup on exit
cleanup() {
    rm -f "$TEMP_FILE"
    echo "Cleanup complete"
}
trap cleanup EXIT

# Handle specific signals
trap 'echo "Interrupted"; exit 130' INT
trap 'echo "Terminated"; exit 143' TERM

# Error line number
trap 'echo "Error on line $LINENO"' ERR
```

## Text Processing

### Using grep
```bash
# Basic search
grep "pattern" file

# Case-insensitive
grep -i "pattern" file

# Recursive search
grep -r "pattern" directory/

# Show line numbers
grep -n "pattern" file

# Invert match (show non-matching lines)
grep -v "pattern" file

# Extended regex
grep -E "pattern1|pattern2" file
```

### Using sed
```bash
# Replace text
sed 's/old/new/' file           # Replace first occurrence per line
sed 's/old/new/g' file          # Replace all occurrences
sed 's/old/new/gi' file         # Case-insensitive replace

# Delete lines
sed '/pattern/d' file           # Delete matching lines
sed '1d' file                   # Delete first line
sed '$d' file                   # Delete last line

# Print specific lines
sed -n '5p' file                # Print line 5
sed -n '5,10p' file             # Print lines 5-10
sed -n '/pattern/p' file        # Print matching lines

# In-place editing
sed -i 's/old/new/g' file       # Linux
sed -i '' 's/old/new/g' file    # macOS
```

### Using awk
```bash
# Print specific columns
awk '{print $1, $3}' file

# Filter by column value
awk '$3 > 100' file

# Sum a column
awk '{sum += $1} END {print sum}' file

# Custom field separator
awk -F: '{print $1}' /etc/passwd

# Pattern matching
awk '/pattern/ {print $1}' file
```

## Date and Time

### Get current date/time
```bash
# Current timestamp
now=$(date +%s)

# Formatted date
date=$(date +"%Y-%m-%d")
datetime=$(date +"%Y-%m-%d %H:%M:%S")

# ISO 8601 format
iso_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```

### Date arithmetic
```bash
# Days ago (GNU date)
yesterday=$(date -d "yesterday" +%Y-%m-%d)
week_ago=$(date -d "7 days ago" +%Y-%m-%d)

# Days ago (BSD date - macOS)
yesterday=$(date -v-1d +%Y-%m-%d)
week_ago=$(date -v-7d +%Y-%m-%d)
```

## Network Operations

### Check if host is reachable
```bash
if ping -c 1 -W 1 example.com &> /dev/null; then
    echo "Host is reachable"
fi
```

### Download files
```bash
# Using curl
curl -O https://example.com/file
curl -o output.txt https://example.com/file

# Using wget
wget https://example.com/file
wget -O output.txt https://example.com/file

# Follow redirects and show progress
curl -L --progress-bar -o file https://example.com/file
```

### HTTP requests
```bash
# GET request
curl https://api.example.com/endpoint

# POST request with JSON
curl -X POST https://api.example.com/endpoint \
    -H "Content-Type: application/json" \
    -d '{"key": "value"}'

# Check HTTP status
status=$(curl -s -o /dev/null -w "%{http_code}" https://example.com)
```

## Temporary Files and Directories

### Create temporary files safely
```bash
# Create temporary file
TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT

# Create temporary directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Create in specific location
TEMP_FILE=$(mktemp /tmp/myapp.XXXXXX)
```

## Miscellaneous

### Generate random numbers
```bash
# Random number 0-32767
random=$RANDOM

# Random number in range 1-100
random=$((RANDOM % 100 + 1))

# Better random (if available)
random=$(shuf -i 1-100 -n 1)
```

### URL encoding
```bash
urlencode() {
    local string="$1"
    local strlen=${#string}
    local encoded=""
    local pos c o
    
    for (( pos=0; pos<strlen; pos++ )); do
        c=${string:$pos:1}
        case "$c" in
            [-_.~a-zA-Z0-9] ) o="$c" ;;
            * ) printf -v o '%%%02x' "'$c" ;;
        esac
        encoded+="$o"
    done
    echo "$encoded"
}
```

### JSON parsing (with jq)
```bash
# Extract value
value=$(echo '{"key": "value"}' | jq -r '.key')

# Extract from array
items=$(echo '[{"name": "a"}, {"name": "b"}]' | jq -r '.[].name')

# Create JSON
json=$(jq -n --arg name "value" '{key: $name}')
```
