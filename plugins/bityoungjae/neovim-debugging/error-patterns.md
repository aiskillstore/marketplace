# Error Patterns & Heuristics

This document maps common Neovim error messages to their typical causes and solutions. When you see an error, find the matching pattern and follow the diagnostic path.

---

## How to Read Lua Error Messages

A typical Neovim Lua error looks like:

```
E5108: Error executing lua: /path/to/file.lua:42: attempt to index local 'opts' (a nil value)
stack traceback:
        /path/to/file.lua:42: in function 'setup'
        /path/to/other.lua:10: in main chunk
```

| Component | Meaning |
|-----------|---------|
| `E5108` | Neovim error code for Lua errors |
| `/path/to/file.lua:42` | File and line number where error occurred |
| `attempt to index local 'opts'` | The operation that failed |
| `(a nil value)` | The value that caused the failure |
| `stack traceback` | Call chain leading to the error |

**Pro tip**: The stack traceback reads bottom-to-top. The bottom entry is where the call originated (often your config), the top is where it crashed (often plugin code).

---

## Pattern Categories

### 1. Nil Access Errors

#### `attempt to index (local/field/global) 'X' (a nil value)`

**What it means**: Code tried to access `X.something` or `X["something"]` but `X` is nil.

**Common causes**:
| Pattern | Typical Cause | Diagnostic |
|---------|---------------|------------|
| `opts` is nil | Function called without arguments | Check the caller—should pass `{}` at minimum |
| `config` is nil | Plugin not configured | Ensure `setup()` was called before use |
| `M.something` is nil | Module doesn't export this field | Check module's API (may have changed) |
| `client` is nil | No LSP client attached | Check `:LspInfo` for this buffer |

**Quick fix template**:
```lua
-- Add defensive check
local value = opts and opts.field or default_value

-- Or ensure opts is never nil
function M.setup(opts)
  opts = opts or {}  -- Add this line
  -- rest of function
end
```

<example>
Error: `attempt to index local 'opts' (a nil value)` in snacks/provider.lua:1098

Analysis:
- Snacks.nvim picker was called
- A function expected `opts` table but received nil
- Caller (probably another plugin or custom code) didn't pass options

Solution:
1. Find the caller in stack trace
2. Ensure it passes `{}` instead of nil/nothing
3. Or patch the receiving function: `opts = opts or {}`
</example>

---

#### `attempt to call (method/field) 'X' (a nil value)`

**What it means**: Code tried to call `X()` or `obj:X()` but `X` is nil (function doesn't exist).

**Common causes**:
| Pattern | Typical Cause | Diagnostic |
|---------|---------------|------------|
| Plugin method nil | API changed in update | Check plugin changelog, compare with docs |
| require() returns nil | Module not found/failed to load | Check plugin installation |
| Object method nil | Wrong object type or not initialized | Verify object creation succeeded |

**Diagnostic steps**:
```bash
# Check if function exists
nvim --headless -c "lua print(type(require('MODULE').FUNCTION))" -c "qa" 2>&1

# Check module structure
nvim --headless -c "lua print(vim.inspect(require('MODULE')))" -c "qa" 2>&1
```

---

### 2. Module Errors

#### `module 'X' not found`

**Full error**:
```
module 'telescope' not found:
        no field package.preload['telescope']
        no file './telescope.lua'
        ...
```

**Common causes**:
| Cause | Diagnostic | Fix |
|-------|------------|-----|
| Plugin not installed | `:Lazy` doesn't show plugin | Add to plugin specs |
| Plugin not loaded (lazy) | `:Lazy` shows "not loaded" | Trigger loading condition or `:Lazy load X` |
| Typo in module name | Check spelling | Common: `nvim-tree` vs `nvim_tree` |
| Wrong require path | Check plugin docs | Module path may differ from plugin name |

**Lazy loading gotcha**:
```lua
-- This fails if telescope not yet loaded:
local telescope = require('telescope')  -- At top of file

-- This works:
vim.keymap.set('n', '<leader>ff', function()
  require('telescope.builtin').find_files()  -- Loaded on demand
end)
```

---

#### `loop or previous error loading module 'X'`

**What it means**: Circular dependency—module A requires B which requires A.

**Diagnostic**:
```lua
-- Problematic pattern:
-- file_a.lua
local b = require('file_b')

-- file_b.lua
local a = require('file_a')  -- Circular!
```

**Solutions**:
1. Move shared code to a third module
2. Use lazy require (require inside function, not at top)
3. Restructure dependencies

---

### 3. Type Errors

#### `bad argument #N to 'X' (Y expected, got Z)`

**What it means**: Function X received wrong type at argument position N.

**Common patterns**:
```
bad argument #1 to 'nvim_buf_set_lines' (number expected, got nil)
→ Buffer handle is nil (buffer doesn't exist or wrong variable)

bad argument #2 to 'format' (string expected, got table)
→ Trying to use string.format with a table (missing serialization)

bad argument #1 to 'pairs' (table expected, got nil)
→ Iterating over nil (data not loaded or wrong variable)
```

**Quick diagnostic**:
```lua
-- Before the failing call, add:
print(vim.inspect(suspicious_variable))
-- Or
assert(type(var) == "expected_type", "var was: " .. type(var))
```

---

### 4. Vim API Errors

#### `E5107: Error loading lua [...] Undefined variable`

**What it means**: Vimscript variable referenced from Lua doesn't exist.

**Examples**:
```
Undefined variable: g:my_option
→ Use vim.g.my_option in Lua, but if never set, it's nil not "undefined"

Undefined variable: some_function
→ Calling Vimscript function wrong, use vim.fn.some_function()
```

---

#### `E523: Not allowed here`

**What it means**: Tried to modify buffer/window in a context that doesn't allow it.

**Common triggers**:
- Modifying buffer in `TextChangedI` autocmd while inserting
- Changing windows in certain callback contexts
- Recursive autocommand triggers

**Solution**: Defer the action:
```lua
vim.schedule(function()
  -- Do the modification here
end)
```

---

#### `E565: Not allowed to change text or change window`

**What it means**: Similar to E523, blocked due to textlock.

**Typical context**: Completion popup is open, snippet is expanding

**Solution**: Use `vim.schedule()` or check `vim.fn.mode()` before action.

---

### 5. Plugin-Specific Patterns

#### LSP: `client.server_capabilities is nil`

**Cause**: LSP client not properly initialized or server crashed.

**Diagnostic**:
```vim
:LspInfo
:LspLog
```

---

#### Treesitter: `query: invalid node type at position X`

**Cause**: Tree-sitter query uses node type that doesn't exist in grammar.

**Common after**: Language parser update changed node names.

**Fix**: Update queries or pin parser version.

---

#### Telescope: `pickers.X is nil`

**Cause**: Picker extension not loaded or doesn't exist.

**Diagnostic**:
```lua
:lua print(vim.inspect(require('telescope.builtin')))
:lua require('telescope').extensions.fzf  -- Check extension
```

---

### 6. Startup Errors

#### Errors at Neovim start that disappear on `:messages`

**Cause**: Error happens before UI is ready, message buffer clears.

**Diagnostic**:
```bash
# Capture all startup output
nvim 2>&1 | tee /tmp/nvim-startup.log

# Or use startuptime with verbose
nvim -V10/tmp/verbose.log --startuptime /tmp/startup.log +q
```

---

#### `E475: Invalid argument: 'X'` during startup

**Common causes**:
- Invalid option name (typo or deprecated option)
- Option doesn't accept given value
- Setting option too early (before feature loaded)

**Diagnostic**:
```vim
:help 'X'  " Check if option exists
:set X?    " Check current value
```

---

## Error Analysis Framework

When you see an error, work through this framework:

```
<analysis>
1. WHAT failed?
   - Extract the operation from error message
   - What was it trying to do?

2. WHERE did it fail?
   - File and line number from error
   - Who called it? (check stack trace)

3. WHY did it fail?
   - What value was unexpected?
   - What state was wrong?

4. WHO is responsible?
   - Plugin code? → Check for updates, issues
   - User config? → Review recent changes
   - Interaction? → Check plugin compatibility

5. WHEN does it happen?
   - Always? → Static config issue
   - Sometimes? → Race condition, async issue
   - After update? → Breaking change
</analysis>
```

---

## Quick Reference: Error Code Meanings

| Code | Category | Common Cause |
|------|----------|--------------|
| E5108 | Lua error | See patterns above |
| E5107 | Lua variable | Undefined vimscript var in Lua |
| E523 | Not allowed | Buffer modification blocked |
| E565 | Textlock | Change blocked during completion |
| E475 | Invalid argument | Wrong value for option |
| E492 | Not editor command | Typo in Ex command |
| E5113 | Lua string | Invalid UTF-8 or string operation |
