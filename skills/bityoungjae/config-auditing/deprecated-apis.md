# Deprecated APIs by Neovim Version

Reference for identifying deprecated and removed APIs. Check user's Neovim version first, then flag applicable deprecations.

## Version Detection

```bash
# Get Neovim version
nvim --version | head -1
# Example: NVIM v0.10.0

# Check version in Lua
nvim --headless -c "lua print(vim.version().major, vim.version().minor)" -c "qa" 2>&1
```

---

## Neovim 0.9 Deprecations

APIs deprecated in 0.9, still working but should be migrated.

### vim.lsp.buf.range_formatting()

| Field | Value |
|-------|-------|
| Deprecated | 0.9 |
| Removed | 0.10 |
| Detection | `grep -rn "range_formatting\s*(" --include="*.lua"` |
| Replacement | `vim.lsp.buf.format({ range = ... })` |

```lua
-- Old
vim.lsp.buf.range_formatting()

-- New
vim.lsp.buf.format({
  range = {
    ["start"] = vim.api.nvim_buf_get_mark(0, "<"),
    ["end"] = vim.api.nvim_buf_get_mark(0, ">"),
  }
})
```

---

### vim.lsp.buf.formatting()

| Field | Value |
|-------|-------|
| Deprecated | 0.8 |
| Removed | 0.9 |
| Detection | `grep -rn "vim\.lsp\.buf\.formatting\s*(" --include="*.lua"` |
| Replacement | `vim.lsp.buf.format()` |

---

### vim.lsp.buf.formatting_sync()

| Field | Value |
|-------|-------|
| Deprecated | 0.8 |
| Removed | 0.9 |
| Detection | `grep -rn "formatting_sync\s*(" --include="*.lua"` |
| Replacement | `vim.lsp.buf.format({ async = false })` |

---

### vim.treesitter.query.get_query()

| Field | Value |
|-------|-------|
| Deprecated | 0.9 |
| Removed | 0.10 |
| Detection | `grep -rn "query\.get_query\s*(" --include="*.lua"` |
| Replacement | `vim.treesitter.query.get()` |

```lua
-- Old
local query = vim.treesitter.query.get_query("lua", "highlights")

-- New
local query = vim.treesitter.query.get("lua", "highlights")
```

---

### vim.treesitter.query.parse_query()

| Field | Value |
|-------|-------|
| Deprecated | 0.9 |
| Removed | 0.10 |
| Detection | `grep -rn "query\.parse_query\s*(" --include="*.lua"` |
| Replacement | `vim.treesitter.query.parse()` |

```lua
-- Old
local query = vim.treesitter.query.parse_query("lua", "(function_declaration) @func")

-- New
local query = vim.treesitter.query.parse("lua", "(function_declaration) @func")
```

---

## Neovim 0.10 Deprecations

APIs deprecated in 0.10.

### vim.api.nvim_buf_set_option()

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet (soft deprecation) |
| Detection | `grep -rn "nvim_buf_set_option\s*(" --include="*.lua"` |
| Replacement | `vim.bo[bufnr].option = value` |

```lua
-- Old
vim.api.nvim_buf_set_option(bufnr, "filetype", "lua")

-- New
vim.bo[bufnr].filetype = "lua"
```

---

### vim.api.nvim_win_set_option()

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet (soft deprecation) |
| Detection | `grep -rn "nvim_win_set_option\s*(" --include="*.lua"` |
| Replacement | `vim.wo[winid].option = value` |

```lua
-- Old
vim.api.nvim_win_set_option(winid, "wrap", false)

-- New
vim.wo[winid].wrap = false
```

---

### vim.api.nvim_set_option()

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet (soft deprecation) |
| Detection | `grep -rn "nvim_set_option\s*(" --include="*.lua"` |
| Replacement | `vim.o.option = value` |

---

### vim.api.nvim_buf_get_option()

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet |
| Detection | `grep -rn "nvim_buf_get_option\s*(" --include="*.lua"` |
| Replacement | `vim.bo[bufnr].option` |

---

### vim.api.nvim_win_get_option()

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet |
| Detection | `grep -rn "nvim_win_get_option\s*(" --include="*.lua"` |
| Replacement | `vim.wo[winid].option` |

---

### vim.lsp.get_active_clients()

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet |
| Detection | `grep -rn "get_active_clients\s*(" --include="*.lua"` |
| Replacement | `vim.lsp.get_clients()` |

```lua
-- Old
local clients = vim.lsp.get_active_clients({ bufnr = 0 })

-- New
local clients = vim.lsp.get_clients({ bufnr = 0 })
```

---

### vim.lsp.for_each_buffer_client()

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet |
| Detection | `grep -rn "for_each_buffer_client\s*(" --include="*.lua"` |
| Replacement | Use `vim.lsp.get_clients()` with loop |

---

### vim.diagnostic.disable() / enable() signature change

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet |
| Detection | `grep -rn "diagnostic\.disable\s*(\s*[0-9]\|diagnostic\.enable\s*(\s*[0-9]" --include="*.lua"` |
| Note | First argument changed from bufnr to namespace |

```lua
-- Old (0.9)
vim.diagnostic.disable(bufnr)
vim.diagnostic.enable(bufnr)

-- New (0.10+)
vim.diagnostic.enable(false, { bufnr = bufnr })
vim.diagnostic.enable(true, { bufnr = bufnr })
```

---

### vim.treesitter.get_node_text() table parameter

| Field | Value |
|-------|-------|
| Deprecated | 0.10 |
| Removed | Not yet |
| Detection | Pattern changed, check for third non-table arg |
| Replacement | Pass options as table |

```lua
-- Old
vim.treesitter.get_node_text(node, bufnr, { concat = false })

-- Still works, but signature is now:
vim.treesitter.get_node_text(node, source, opts)
```

---

## Neovim 0.11 Deprecations

APIs deprecated in 0.11.

### vim.lsp.buf.execute_command()

| Field | Value |
|-------|-------|
| Deprecated | 0.11 |
| Removed | Not yet |
| Detection | `grep -rn "lsp\.buf\.execute_command\s*(" --include="*.lua"` |
| Replacement | Use client-specific method |

---

### vim.lsp.util.make_position_params() without arguments

| Field | Value |
|-------|-------|
| Deprecated | 0.11 |
| Removed | Not yet |
| Detection | `grep -rn "make_position_params\s*()" --include="*.lua"` |
| Replacement | Pass window and client explicitly |

```lua
-- Old
local params = vim.lsp.util.make_position_params()

-- New
local params = vim.lsp.util.make_position_params(win, client.offset_encoding)
```

---

### vim.lsp.util.make_range_params() without arguments

| Field | Value |
|-------|-------|
| Deprecated | 0.11 |
| Removed | Not yet |
| Detection | `grep -rn "make_range_params\s*()" --include="*.lua"` |
| Replacement | Pass window and client explicitly |

---

### vim.lsp.start_client()

| Field | Value |
|-------|-------|
| Deprecated | 0.11 |
| Removed | Not yet |
| Detection | `grep -rn "lsp\.start_client\s*(" --include="*.lua"` |
| Replacement | `vim.lsp.start()` |

---

## Neovim 0.12 Deprecations (Nightly)

APIs deprecated in 0.12 nightly builds. Subject to change.

### vim.treesitter.get_parser() without bufnr

| Field | Value |
|-------|-------|
| Deprecated | 0.12 |
| Removed | Not yet |
| Detection | `grep -rn "treesitter\.get_parser\s*()" --include="*.lua"` |
| Replacement | Explicitly pass buffer: `vim.treesitter.get_parser(0)` |

---

## Quick Audit Script

Run this to check for common deprecated APIs:

```bash
#!/bin/bash
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/nvim"

echo "=== Deprecated API Audit ==="
echo "Config: $CONFIG_DIR"
echo ""

# 0.10 deprecations (most common)
echo "--- nvim_*_set/get_option (deprecated 0.10) ---"
grep -rn "nvim_buf_set_option\|nvim_win_set_option\|nvim_set_option\|nvim_buf_get_option\|nvim_win_get_option" "$CONFIG_DIR" --include="*.lua" 2>/dev/null || echo "None found"
echo ""

echo "--- get_active_clients (deprecated 0.10) ---"
grep -rn "get_active_clients" "$CONFIG_DIR" --include="*.lua" 2>/dev/null || echo "None found"
echo ""

# 0.9 deprecations
echo "--- formatting_sync/range_formatting (removed 0.9-0.10) ---"
grep -rn "formatting_sync\|range_formatting" "$CONFIG_DIR" --include="*.lua" 2>/dev/null || echo "None found"
echo ""

# 0.11 deprecations
echo "--- make_position_params/make_range_params without args (deprecated 0.11) ---"
grep -rn "make_position_params\s*()\|make_range_params\s*()" "$CONFIG_DIR" --include="*.lua" 2>/dev/null || echo "None found"
echo ""

# 0.9 deprecations (removed in 0.10)
echo "--- get_query/parse_query (deprecated 0.9, removed 0.10) ---"
grep -rn "query\.get_query\|query\.parse_query" "$CONFIG_DIR" --include="*.lua" 2>/dev/null || echo "None found"
echo ""

echo "=== Audit Complete ==="
```

---

## Summary Table

| API | Deprecated | Removed | Severity |
|-----|------------|---------|----------|
| `vim.lsp.buf.formatting()` | 0.8 | 0.9 | Critical |
| `vim.lsp.buf.formatting_sync()` | 0.8 | 0.9 | Critical |
| `vim.lsp.buf.range_formatting()` | 0.9 | 0.10 | Critical |
| `nvim_buf_set_option()` | 0.10 | — | Warning |
| `nvim_win_set_option()` | 0.10 | — | Warning |
| `nvim_set_option()` | 0.10 | — | Warning |
| `get_active_clients()` | 0.10 | — | Warning |
| `vim.diagnostic.disable/enable()` sig | 0.10 | — | Warning |
| `make_position_params()` no args | 0.11 | — | Warning |
| `lsp.start_client()` | 0.11 | — | Warning |
| `query.get_query()` | 0.9 | 0.10 | Critical |
| `query.parse_query()` | 0.9 | 0.10 | Critical |
