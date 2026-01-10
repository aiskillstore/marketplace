# difft (difftastic) Advanced Usage

Semantic, AST-aware diff tool for meaningful code comparisons.

## Display Modes

### Side-by-Side (Default)

```bash
difft old.ts new.ts
# Shows files side by side with syntax highlighting
```

### Inline (Unified Style)

```bash
difft --display=inline old.ts new.ts
# Traditional unified diff format
```

### Side-by-Side in Terminal

```bash
difft --display=side-by-side old.ts new.ts
# Explicit side-by-side
```

## Filtering Options

### Skip Unchanged

```bash
difft --skip-unchanged old.ts new.ts
# Only show files that changed
```

### Context Lines

```bash
difft --context 5 old.ts new.ts
# Show 5 lines of context around changes
```

### Language Override

```bash
difft --language=python file1 file2
# Force specific language parser

# List supported languages
difft --list-languages
```

## Color and Formatting

```bash
# Force color output (for piping)
difft --color=always old.ts new.ts | less -R

# Disable color
difft --color=never old.ts new.ts

# Set terminal width
difft --width 120 old.ts new.ts

# Tab width
difft --tab-width 4 old.ts new.ts
```

## Git Integration

### As External Diff

```bash
# One-time use
GIT_EXTERNAL_DIFF=difft git diff
GIT_EXTERNAL_DIFF=difft git show HEAD~1
GIT_EXTERNAL_DIFF=difft git log -p

# With options
GIT_EXTERNAL_DIFF="difft --display=inline" git diff
```

### Configure as Default

```bash
# Add to ~/.gitconfig
git config --global diff.external difft

# Or add to .gitconfig directly:
# [diff]
#     external = difft

# Disable for specific command
git --no-ext-diff diff
```

### As Difftool

```bash
# Configure
git config --global diff.tool difftastic
git config --global difftool.difftastic.cmd 'difft "$LOCAL" "$REMOTE"'
git config --global difftool.prompt false

# Use
git difftool HEAD~1
git difftool main feature-branch
```

### Per-Repository

```bash
# In repo's .git/config
git config diff.external difft

# Or in .gitattributes for specific files
*.rs diff=difftastic
```

## Directory Comparison

```bash
# Compare directories
difft dir1/ dir2/

# Compare with options
difft --skip-unchanged dir1/ dir2/
```

## Why Semantic Diffs?

### Traditional diff vs difft

| Scenario | Traditional | difft |
|----------|-------------|-------|
| Reformatted code | Shows all lines as changed | Shows only semantic changes |
| Moved function | Delete + Add | Recognizes as move |
| Renamed variable | Many line changes | Highlights just the rename |
| Added whitespace | Shows as change | Ignores (no semantic change) |
| Reordered imports | All imports changed | Shows specific additions/removals |

### Example: Reformatting

Traditional diff:
```diff
-function foo() { return 42; }
+function foo() {
+  return 42;
+}
```

difft:
```
(no changes - semantically identical)
```

### Example: Moved Code

Traditional diff:
```diff
-function helper() { ... }
 function main() { ... }
+function helper() { ... }
```

difft:
```
function helper() { ... }  →  (moved to line 10)
```

## Supported Languages

difft parses actual ASTs for many languages:

- **Web**: JavaScript, TypeScript, JSX, TSX, CSS, HTML, JSON
- **Systems**: C, C++, Rust, Go, Zig
- **Scripting**: Python, Ruby, Perl, Lua, Bash
- **JVM**: Java, Kotlin, Scala, Clojure
- **Functional**: Haskell, OCaml, Elixir, Erlang
- **Others**: SQL, YAML, TOML, Nix, Terraform

```bash
# List all
difft --list-languages
```

## Performance Tips

```bash
# For large files, limit context
difft --context 3 large1.ts large2.ts

# Skip binary files
difft --skip-unchanged dir1/ dir2/

# Force text mode for unknown formats
difft --language=text file1 file2
```

## Piping and Scripting

```bash
# Pipe to pager
difft old.ts new.ts | less -R

# Save to file
difft --color=never old.ts new.ts > changes.txt

# Check if files differ (exit code)
difft old.ts new.ts > /dev/null
echo $?  # 0 = same, 1 = different
```

## Common Workflows

### Code Review

```bash
# Review specific commit
GIT_EXTERNAL_DIFF=difft git show abc123

# Review PR changes
GIT_EXTERNAL_DIFF=difft git diff main...feature-branch

# Review staged changes
GIT_EXTERNAL_DIFF=difft git diff --cached
```

### Before/After Refactoring

```bash
# Save original
cp module.ts module.ts.bak

# Refactor...

# Compare
difft module.ts.bak module.ts
```

### Comparing Branches

```bash
# Full diff between branches
GIT_EXTERNAL_DIFF=difft git diff main feature-branch

# Specific file across branches
difft <(git show main:src/index.ts) <(git show feature:src/index.ts)
```

### Comparing Commits

```bash
# Specific file between commits
difft <(git show HEAD~2:src/index.ts) <(git show HEAD:src/index.ts)
```

## Configuration

Create `~/.config/difft/config.toml`:

```toml
# Display mode
display = "side-by-side"

# Context lines
context = 3

# Tab width
tab-width = 4

# Color theme (try different values)
color = "always"
```

## Tips

1. **Use with git always** - `GIT_EXTERNAL_DIFF=difft` or configure globally
2. **Skip unchanged in directories** - `--skip-unchanged` for cleaner output
3. **Inline for copy/paste** - `--display=inline` when sharing diffs
4. **Force language** - `--language=X` when auto-detection fails
5. **Combine with delta** - Use difft for semantic diffs, delta for line-level
