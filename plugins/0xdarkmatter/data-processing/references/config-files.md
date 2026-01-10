# Config File Patterns

Common patterns for processing configuration files.

## package.json

```bash
# List all dependencies
jq '.dependencies | keys' package.json

# Get all scripts
jq '.scripts' package.json

# Find outdated patterns
jq '.dependencies | to_entries | map(select(.value | startswith("^")))' package.json

# Extract dev dependencies
jq '.devDependencies | keys | .[]' package.json
```

## tsconfig.json

```bash
# Get compiler options
jq '.compilerOptions' tsconfig.json

# Check strict mode
jq '.compilerOptions.strict' tsconfig.json

# List paths aliases
jq '.compilerOptions.paths' tsconfig.json
```

## ESLint/Prettier

```bash
# Get enabled rules
jq '.rules | to_entries | map(select(.value != "off"))' .eslintrc.json

# Check prettier options
jq '.' .prettierrc.json
```
