# JavaScript/TypeScript Patterns

Complete pattern library for ast-grep in JavaScript and TypeScript.

## Function Calls

```bash
# Find all console.log calls
sg -p 'console.log($_)'

# Find all console methods
sg -p 'console.$_($_)'

# Find fetch calls
sg -p 'fetch($_)'

# Find await fetch
sg -p 'await fetch($_)'

# Find specific function calls
sg -p 'getUserById($_)'

# Find method chaining
sg -p '$_.then($_).catch($_)'
```

## React Patterns

```bash
# Find useState hooks
sg -p 'const [$_, $_] = useState($_)'

# Find useEffect with dependencies
sg -p 'useEffect($_, [$$$])'

# Find useEffect without dependencies (runs every render)
sg -p 'useEffect($_, [])'

# Find component definitions
sg -p 'function $NAME($$$) { return <$$$> }'

# Find specific prop usage
sg -p '<Button onClick={$_}>'

# Find useState without destructuring
sg -p 'useState($_)'
```

## Imports

```bash
# Find all imports from a module
sg -p 'import $_ from "react"'

# Find named imports
sg -p 'import { $_ } from "lodash"'

# Find default and named imports
sg -p 'import $_, { $$$ } from $_'

# Find dynamic imports
sg -p 'import($_)'

# Find require calls
sg -p 'require($_)'
```

## Async Patterns

```bash
# Find async functions
sg -p 'async function $NAME($$$) { $$$ }'

# Find async arrow functions
sg -p 'async ($$$) => { $$$ }'

# Find try-catch blocks
sg -p 'try { $$$ } catch ($_) { $$$ }'

# Find Promise.all
sg -p 'Promise.all([$$$])'

# Find unhandled promises (no await)
sg -p '$_.then($_)'
```

## Error Prone Patterns

```bash
# Find == instead of ===
sg -p '$_ == $_'

# Find assignments in conditions
sg -p 'if ($_ = $_)'

# Find empty catch blocks
sg -p 'catch ($_) {}'

# Find console.log (for cleanup)
sg -p 'console.log($$$)'

# Find TODO comments
sg -p '// TODO$$$'

# Find debugger statements
sg -p 'debugger'
```

## Refactoring Patterns

### Find and Replace

```bash
# Preview replacement
sg -p 'console.log($_)' -r 'logger.info($_)'

# Replace in place
sg -p 'console.log($_)' -r 'logger.info($_)' --rewrite

# Replace with context
sg -p 'var $NAME = $_' -r 'const $NAME = $_'
```

### Common Refactors

```bash
# Convert function to arrow
sg -p 'function $NAME($ARGS) { return $BODY }' \
   -r 'const $NAME = ($ARGS) => $BODY'

# Convert require to import
sg -p 'const $NAME = require("$MOD")' \
   -r 'import $NAME from "$MOD"'

# Add optional chaining
sg -p '$OBJ.$PROP' -r '$OBJ?.$PROP'
```
