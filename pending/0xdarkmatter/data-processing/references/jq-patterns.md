# jq Patterns Reference

Complete jq patterns for JSON processing.

## Array Operations

```bash
# Get all array elements
jq '.users[]' data.json

# Get specific index
jq '.users[0]' data.json

# Slice array
jq '.users[0:3]' data.json           # First 3 elements
jq '.users[-2:]' data.json           # Last 2 elements

# Array length
jq '.users | length' data.json

# Get array of specific field
jq '.users[].name' data.json

# Wrap results in array
jq '[.users[].name]' data.json
```

## Filtering with select

```bash
# Filter by condition
jq '.users[] | select(.active == true)' data.json

# Multiple conditions
jq '.users[] | select(.age > 21 and .status == "active")' data.json

# String contains
jq '.users[] | select(.email | contains("@gmail"))' data.json

# Regex match
jq '.users[] | select(.email | test("@(gmail|yahoo)"))' data.json

# Not null check
jq '.users[] | select(.profile != null)' data.json
```

## Transformation with map

```bash
# Transform each element
jq '.users | map({id, name})' data.json

# Add computed field
jq '.users | map(. + {full_name: (.first + " " + .last)})' data.json

# Filter and transform
jq '.users | map(select(.active)) | map(.email)' data.json

# map_values for objects
jq '.config | map_values(. * 2)' data.json
```

## Object Manipulation

```bash
# Add/update field
jq '.version = "2.0.0"' package.json

# Delete field
jq 'del(.devDependencies)' package.json

# Rename key
jq '.dependencies | to_entries | map(.key |= gsub("@"; ""))' package.json

# Merge objects
jq '. + {newField: "value"}' data.json

# Update nested field
jq '.scripts.test = "jest --coverage"' package.json

# Conditional update
jq 'if .version == "1.0.0" then .version = "1.0.1" else . end' package.json
```

## Aggregation

```bash
# Count
jq '.users | length' data.json

# Sum
jq '[.items[].price] | add' data.json

# Min/Max
jq '[.scores[]] | min' data.json
jq '[.scores[]] | max' data.json

# Average
jq '[.scores[]] | add / length' data.json

# Group by
jq 'group_by(.category) | map({category: .[0].category, count: length})' data.json

# Unique values
jq '[.users[].role] | unique' data.json

# Sort
jq '.users | sort_by(.created_at)' data.json
jq '.users | sort_by(.name) | reverse' data.json
```

## Output Formatting

```bash
# Pretty print
jq '.' response.json

# Compact output (single line)
jq -c '.results[]' data.json

# Raw strings (no quotes)
jq -r '.name' package.json

# Tab-separated output
jq -r '.users[] | [.id, .name, .email] | @tsv' data.json

# CSV output
jq -r '.users[] | [.id, .name, .email] | @csv' data.json

# URI encoding
jq -r '.query | @uri' data.json
```

## Advanced Patterns

```bash
# Process multiple files
for f in *.json; do jq '.name' "$f"; done

# Pipeline with other tools
curl -s https://api.github.com/users/octocat | jq '.login'

# Assign to variable
VERSION=$(jq -r '.version' package.json)

# Conditional logic
jq -e '.errors | length == 0' response.json && echo "Success"

# Flatten nested structure
jq '[.categories[].items[]] | flatten' data.json

# Reshape data
jq '.users | map({(.id | tostring): .name}) | add' data.json

# Pivot data
jq 'group_by(.date) | map({date: .[0].date, values: map(.value)})' data.json

# Join arrays
jq -s '.[0] + .[1]' file1.json file2.json
```
