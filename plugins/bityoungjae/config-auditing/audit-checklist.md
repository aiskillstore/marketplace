# Audit Checklist

Structured audit categories with detection patterns and severity levels.

## 1. Structure & Organization

### 1.1 Monolithic init.lua
**Severity**: Suggestion
**Description**: Single large init.lua instead of modular structure

```bash
# Detection: init.lua over 200 lines
wc -l ~/.config/nvim/init.lua 2>/dev/null | awk '{if($1>200) print "FOUND: "$1" lines"}'
```

**Recommendation**: Split into `lua/config/`, `lua/plugins/` modules for maintainability.

---

### 1.2 Missing lazy-lock.json in .gitignore
**Severity**: Warning
**Description**: Lock file should typically be committed for reproducibility, but some setups ignore it

```bash
# Detection: Check if ignored
grep -q "lazy-lock" ~/.config/nvim/.gitignore 2>/dev/null && echo "FOUND: lazy-lock in .gitignore"
```

**Note**: This is a project decision - some prefer to commit, some ignore.

---

### 1.3 Hardcoded Paths
**Severity**: Warning
**Description**: Using absolute paths instead of stdpath()

```bash
# Detection: Hardcoded home paths
grep -rn '"/home/\|"/Users/\|"~/' ~/.config/nvim --include="*.lua" 2>/dev/null
```

**Fix**: Use `vim.fn.stdpath('config')`, `vim.fn.stdpath('data')`, etc.

---

### 1.4 Mixed Plugin Manager Configs
**Severity**: Critical
**Description**: Multiple plugin manager configurations present

```bash
# Detection: Multiple plugin managers
ls ~/.config/nvim/lua/plugins.lua ~/.config/nvim/lua/packer*.lua ~/.config/nvim/plugin/packer*.lua 2>/dev/null
grep -l "use\s*{" ~/.config/nvim --include="*.lua" -r 2>/dev/null | head -3
```

**Fix**: Remove legacy plugin manager configs when migrating.

---

## 2. Performance

### 2.1 Synchronous Plugin Loading
**Severity**: Warning
**Description**: Plugins loaded at startup without lazy loading

```bash
# Detection: require without lazy event/cmd/ft
grep -rn "require\s*(\s*['\"]" ~/.config/nvim/init.lua --include="*.lua" 2>/dev/null | grep -v "lazy\|pcall" | head -10
```

**Fix**: Use lazy.nvim's `event`, `cmd`, `ft`, or `keys` for deferred loading.

---

### 2.2 Large Number of Startup Plugins
**Severity**: Warning
**Description**: More than 30 plugins loading at startup

```bash
# Detection: Check lazy.nvim startup stats
nvim --headless -c "lua local s=require('lazy').stats(); print('Startup plugins:', s.loaded, '/', s.count)" -c "qa" 2>&1
```

**Recommendation**: Review plugin necessity and add lazy loading triggers.

---

### 2.3 Heavy Autocmds on BufEnter
**Severity**: Warning
**Description**: Expensive operations on frequently-triggered events

```bash
# Detection: Complex BufEnter/BufRead autocmds
grep -rn "BufEnter\|BufRead\|BufWinEnter" ~/.config/nvim --include="*.lua" 2>/dev/null | grep -v "\.lazy" | head -10
```

**Recommendation**: Use BufReadPost or more specific events when possible.

---

### 2.4 Slow Startup Time
**Severity**: Warning (>200ms) / Critical (>500ms)
**Description**: Startup taking too long

```bash
# Detection: Measure startup
nvim --startuptime /tmp/startup.log +q && awk '/^[0-9].*--- NVIM/ {print "Total: "$1"ms"}' /tmp/startup.log
```

**Action**: Profile with `:Lazy profile` or `--startuptime` flag.

---

### 2.5 Unprotected requires
**Severity**: Suggestion
**Description**: require() calls without pcall can crash on missing plugins

```bash
# Detection: Unprotected require
grep -rn "^local.*=.*require\s*(" ~/.config/nvim --include="*.lua" 2>/dev/null | grep -v pcall | head -10
```

**Fix**: Wrap optional plugin requires in pcall:
```lua
local ok, module = pcall(require, "plugin")
if not ok then return end
```

---

## 3. Security

### 3.1 Exposed Credentials
**Severity**: Critical
**Description**: API keys, tokens, or passwords in config files

```bash
# Detection: Potential secrets
grep -rniE "(api_key|apikey|token|password|secret)\s*=\s*['\"][^'\"]+['\"]" ~/.config/nvim --include="*.lua" 2>/dev/null
```

**Fix**: Use environment variables: `vim.env.MY_API_KEY`

---

### 3.2 Insecure Shell Commands
**Severity**: Critical
**Description**: Unescaped user input in shell commands

```bash
# Detection: String concatenation in vim.fn.system
grep -rn "vim\.fn\.system.*\.\." ~/.config/nvim --include="*.lua" 2>/dev/null
```

**Fix**: Use `vim.fn.shellescape()` for user-provided arguments.

---

### 3.3 Modeline Enabled
**Severity**: Warning
**Description**: Modelines can execute arbitrary settings from file comments

```bash
# Detection: Check if modeline is enabled (default is on)
nvim --headless -c "lua print('modeline:', vim.o.modeline)" -c "qa" 2>&1
```

**Recommendation**: Disable with `vim.o.modeline = false` if not needed.

---

### 3.4 Exrc Enabled Without Secure
**Severity**: Critical
**Description**: Loading project-local configs without security checks

```bash
# Detection: exrc without secure
nvim --headless -c "lua print('exrc:', vim.o.exrc, 'secure:', vim.o.secure)" -c "qa" 2>&1
```

**Fix**: If using exrc, ensure `vim.o.secure = true`.

---

## 4. Compatibility

### 4.1 Deprecated API Usage
**Severity**: Warning (deprecated) / Critical (removed)
**Description**: Using APIs that are deprecated or removed in current Neovim version

```bash
# Detection: See deprecated-apis.md for version-specific patterns
# Common deprecated APIs:
grep -rn "nvim_buf_set_option\|nvim_win_set_option\|nvim_set_option" ~/.config/nvim --include="*.lua" 2>/dev/null
```

**Action**: Cross-reference with [deprecated-apis.md](deprecated-apis.md).

---

### 4.2 VimScript in Lua Config
**Severity**: Suggestion
**Description**: Using vim.cmd for things that have Lua equivalents

```bash
# Detection: vim.cmd with simple settings
grep -rn "vim\.cmd.*set\s\|vim\.cmd.*let\s\|vim\.cmd.*autocmd" ~/.config/nvim --include="*.lua" 2>/dev/null | head -10
```

**Fix**: Convert to native Lua:
- `vim.cmd("set number")` → `vim.o.number = true`
- `vim.cmd("let g:var = 1")` → `vim.g.var = 1`

---

### 4.3 Lua 5.1 vs LuaJIT Incompatibilities
**Severity**: Warning
**Description**: Using Lua features not in LuaJIT

```bash
# Detection: goto statement (not in LuaJIT by default)
grep -rn "goto\s\+\w" ~/.config/nvim --include="*.lua" 2>/dev/null
```

**Note**: Neovim uses LuaJIT, which is based on Lua 5.1 with extensions.

---

### 4.4 Neovim Version Checks Missing
**Severity**: Suggestion
**Description**: Using new APIs without version guards

```bash
# Detection: Calls to vim.lsp.inlay_hint (0.10+) without version check
grep -rn "vim\.lsp\.inlay_hint\|vim\.snippet" ~/.config/nvim --include="*.lua" 2>/dev/null
```

**Fix**: Add version checks:
```lua
if vim.fn.has("nvim-0.10") == 1 then
  vim.lsp.inlay_hint.enable(true)
end
```

---

## 5. Redundancy

### 5.1 Duplicate Keymaps
**Severity**: Warning
**Description**: Same key mapped multiple times

```bash
# Detection: Find duplicate keymap definitions
grep -rhn "vim\.keymap\.set\|map\s*(" ~/.config/nvim --include="*.lua" 2>/dev/null | \
  sed 's/.*["\x27]\([^"\x27]*\)["\x27].*/\1/' | sort | uniq -d
```

**Action**: Review and consolidate keymap definitions.

---

### 5.2 Redundant Option Settings
**Severity**: Suggestion
**Description**: Setting options to their default values

```bash
# Detection: Common defaults being explicitly set
grep -rn "vim\.o\.compatible\s*=\s*false\|vim\.o\.magic\s*=\s*true" ~/.config/nvim --include="*.lua" 2>/dev/null
```

**Note**: Some prefer explicit defaults for documentation purposes.

---

### 5.3 Unused Plugin Configurations
**Severity**: Suggestion
**Description**: Config for plugins that aren't installed

```bash
# Detection: Compare configured vs installed plugins
# List configured plugins
grep -roh "require\s*['\"][^'\"]*['\"]" ~/.config/nvim/lua/plugins --include="*.lua" 2>/dev/null | sort -u
# Compare with ~/.local/share/nvim/lazy/
```

**Action**: Remove configurations for uninstalled plugins.

---

### 5.4 Both vim.opt and vim.o for Same Option
**Severity**: Suggestion
**Description**: Mixing vim.opt and vim.o for the same option creates confusion

```bash
# Detection: Find options set both ways
comm -12 \
  <(grep -roh "vim\.opt\.\w*" ~/.config/nvim --include="*.lua" 2>/dev/null | sed 's/vim\.opt\.//' | sort -u) \
  <(grep -roh "vim\.o\.\w*" ~/.config/nvim --include="*.lua" 2>/dev/null | sed 's/vim\.o\.//' | sort -u)
```

**Fix**: Standardize on one approach (typically vim.opt for list-like options).

---

## Summary Table

| Category | Critical | Warning | Suggestion |
|----------|----------|---------|------------|
| Structure | 1 | 2 | 1 |
| Performance | 1 | 4 | 1 |
| Security | 3 | 1 | 0 |
| Compatibility | 1 | 2 | 2 |
| Redundancy | 0 | 1 | 3 |
| **Total** | **6** | **10** | **7** |
