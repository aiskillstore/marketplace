# Plugin-Specific Debugging

This document provides debugging knowledge for commonly problematic plugins and subsystems.

---

## lazy.nvim (Plugin Manager)

### Core Concepts

- **Lazy loading**: Plugins aren't loaded until triggered (event, command, keymap, filetype)
- **Plugin spec**: Table defining how/when to load a plugin
- **lazy-lock.json**: Pins exact commit hashes for reproducible installs

### Common Issues

#### Plugin Not Loading

```lua
-- Check if lazy knows about it
:Lazy  -- Search for plugin name

-- Force load for testing
:Lazy load plugin-name

-- Check why it's not loaded
:lua print(vim.inspect(require('lazy.core.config').plugins['plugin-name']))
```

**Lazy loading conditions**:
```lua
{
  "plugin/name",
  event = "VeryLazy",     -- After UI is ready
  event = "BufReadPre",   -- Before reading any buffer
  ft = "lua",             -- Only for Lua files
  cmd = "PluginCmd",      -- Only when command is run
  keys = "<leader>x",     -- Only when key is pressed
}
```

#### Config vs Opts

```lua
-- opts: Merged with defaults, passed to setup()
opts = { feature = true }

-- config: Full control, replaces default setup
config = function(_, opts)
  require('plugin').setup(opts)  -- You must call setup yourself
end
```

**Common mistake**: Defining `config` but forgetting to call `setup()`.

#### Dependencies Not Loaded

```lua
{
  "main-plugin",
  dependencies = {
    "dep-plugin",  -- Loaded before main-plugin
  },
}
```

Check dependency is listed and loaded first: `:Lazy` → check both plugins' state.

---

## which-key.nvim

### Core Concepts

- **Triggers**: Keys that activate which-key popup
- **Mappings**: Key descriptions shown in popup
- **Groups**: Nested key categories (e.g., `<leader>f` for "file" operations)

### Common Issues

#### Popup Not Appearing

```lua
-- Check which-key is loaded
:lua print(require('which-key'))

-- Manual trigger (always works if installed)
:lua require('which-key').show('<leader>')
:lua require('which-key').show('\\')  -- localleader
```

If manual works but automatic doesn't → trigger configuration issue.

#### Localleader Not Triggering Automatically

**This is extremely common with LazyVim**. By default, which-key auto-triggers for `<leader>` (Space) but not `<localleader>` (backslash).

```lua
-- Fix: Add to which-key setup
require('which-key').setup({
  triggers = {
    { "<auto>", mode = "nxso" },      -- Default auto triggers
    { "\\", mode = { "n", "v" } },    -- Add localleader!
  },
})
```

For LazyVim, add this in `lua/plugins/which-key.lua`:
```lua
return {
  "folke/which-key.nvim",
  opts = {
    triggers = {
      { "<auto>", mode = "nxso" },
      { "\\", mode = { "n", "v" } },
    },
  },
}
```

#### Mappings Not Showing

```lua
-- Check mappings using Neovim's built-in commands
:nmap <leader>       -- List all leader mappings
:verbose map <key>   -- Show where a specific mapping was defined

-- Mappings are registered via:
-- 1. Via which-key.add() (v3) or register() (v2, deprecated)
-- 2. Via opts.spec in setup
-- 3. Via vim.keymap.set with desc option
```

---

## LSP (Language Server Protocol)

### Core Concepts

- **Server**: External process providing intelligence (e.g., `typescript-language-server`)
- **Client**: Neovim's connection to the server
- **Capabilities**: What features server/client support
- **Root directory**: Project root for the server (affects file discovery)

### Common Issues

#### Server Not Attaching

```vim
:LspInfo         " Shows attached clients for current buffer
:LspLog          " Shows LSP communication log
:checkhealth lsp " Comprehensive check
```

**Common causes**:
| Symptom | Likely Cause | Check |
|---------|--------------|-------|
| No clients | Server not installed | `:Mason` → is it installed? |
| No clients | Filetype not detected | `:set ft?` |
| No clients | No root found | Need `.git`, `package.json`, etc. |
| Client attached but no features | Capability mismatch | `:lua print(vim.inspect(vim.lsp.get_clients()[1].server_capabilities))` |

#### Mason vs Manual Installation

```lua
-- Mason manages server binaries
:Mason  -- Check installed servers

-- Manual: Server must be in PATH
:!which typescript-language-server
```

#### No Completions

```lua
-- Check if client supports completion
:lua print(vim.lsp.get_clients()[1].server_capabilities.completionProvider)

-- Check nvim-cmp source is configured
:lua print(vim.inspect(require('cmp').get_config().sources))
```

#### No Diagnostics

```lua
-- Check if diagnostics are enabled
:lua print(vim.diagnostic.is_enabled())

-- Check diagnostic count
:lua print(vim.inspect(vim.diagnostic.get(0)))

-- Some servers need project config (tsconfig.json, pyproject.toml)
```

---

## Treesitter

### Core Concepts

- **Parser**: Generates syntax tree for a language
- **Query**: Pattern to match tree nodes (for highlights, folds, etc.)
- **Highlight**: Syntax highlighting via queries

### Common Issues

#### No Syntax Highlighting

```vim
:TSInstallInfo     " Check parser installation status
:InspectTree       " View syntax tree for current buffer
```

**Common causes**:
| Symptom | Likely Cause | Check |
|---------|--------------|-------|
| No colors | Parser not installed | `:TSInstall {lang}` |
| Wrong colors | Parser outdated | `:TSUpdate` |
| Partial colors | Query error | Check `:messages` for query errors |

#### Parser Installation Failed

```bash
# Compilers required
# Linux: gcc/clang
# Mac: Xcode command line tools
# Windows: MSVC or MinGW

# Check compiler
:checkhealth nvim-treesitter
```

#### Query Errors After Update

```
query: invalid node type at position X for language Y
```

Parser update changed node names. Solutions:
1. Update all plugins that use queries
2. Or pin treesitter parsers in lazy-lock.json

---

## Telescope

### Core Concepts

- **Picker**: UI for selecting items (files, buffers, etc.)
- **Finder**: Generates list of items
- **Sorter**: Orders results
- **Extension**: Additional pickers (fzf, file_browser, etc.)

### Common Issues

#### Picker Not Found

```lua
-- List available pickers
:lua print(vim.inspect(vim.tbl_keys(require('telescope.builtin'))))

-- Check extension loaded
:lua print(require('telescope').extensions.fzf)
```

#### Extension Not Working

```lua
-- Extensions must be loaded after setup
require('telescope').setup({})
require('telescope').load_extension('fzf')
```

For lazy.nvim:
```lua
{
  'nvim-telescope/telescope.nvim',
  dependencies = {
    'nvim-telescope/telescope-fzf-native.nvim',
    build = 'make',  -- Must compile native code
  },
  config = function()
    require('telescope').setup({})
    require('telescope').load_extension('fzf')
  end,
}
```

#### Slow Performance

```lua
-- Check if using native fzf sorter
:lua print(require('telescope').extensions.fzf)

-- Preview causing lag? Disable for testing:
:Telescope find_files previewer=false
```

---

## nvim-cmp (Completion)

### Core Concepts

- **Source**: Where completions come from (LSP, buffer, path, snippets)
- **Mapping**: Keys to navigate/confirm completions
- **Sorting**: Priority and ordering of completions

### Common Issues

#### No Completions Appearing

```lua
-- Check sources configured
:lua print(vim.inspect(require('cmp').get_config().sources))

-- Force completion manually
<C-Space>  -- or whatever mapping you have

-- Check if completion is enabled
:lua print(require('cmp').visible())
```

#### LSP Completions Missing

```lua
-- Verify LSP client attached
:LspInfo

-- Check LSP source is in cmp sources
:lua for _, s in ipairs(require('cmp').get_config().sources) do print(s.name) end
-- Should see 'nvim_lsp'
```

#### Snippet Completions Not Expanding

```lua
-- Check snippet engine configured
:lua print(vim.inspect(require('cmp').get_config().snippet))

-- Verify LuaSnip (or your engine) is loaded
:lua print(require('luasnip'))
```

---

## Snacks.nvim (Folke's Utilities)

### Common Issues

#### Picker Errors

```
attempt to index local 'opts' (a nil value)
```

**Cause**: Another plugin/code calling snacks picker without passing options table.

**Solution**: Find the caller in stack trace, ensure it passes `{}` at minimum.

#### Dashboard Not Showing

```lua
-- Check if Snacks dashboard is enabled
:lua print(require('snacks').config.dashboard.enabled)

-- Force show
:lua require('snacks').dashboard()
```

---

## LazyVim Specifics

### Understanding LazyVim Structure

```
~/.config/nvim/
├── init.lua              # Bootstrap lazy.nvim
├── lazyvim.json          # Enabled extras
└── lua/
    ├── config/
    │   ├── autocmds.lua  # User autocmds (extend LazyVim)
    │   ├── keymaps.lua   # User keymaps (extend LazyVim)
    │   ├── lazy.lua      # lazy.nvim setup
    │   └── options.lua   # User options (extend LazyVim)
    └── plugins/
        └── *.lua         # User plugin specs (extend LazyVim)
```

### Extras

LazyVim extras add optional functionality. Enabled extras are in `lazyvim.json`:

```json
{
  "extras": [
    "lazyvim.plugins.extras.lang.typescript",
    "lazyvim.plugins.extras.editor.mini-files"
  ]
}
```

To check what an extra provides:
```bash
cat ~/.local/share/nvim/lazy/LazyVim/lua/lazyvim/plugins/extras/lang/typescript.lua
```

### Overriding LazyVim Defaults

```lua
-- In lua/plugins/example.lua

-- Override opts (merged with defaults)
return {
  "plugin/name",
  opts = { your_option = true },
}

-- Full override (replaces LazyVim config)
return {
  "plugin/name",
  opts = function(_, opts)
    opts.your_option = true
    return opts
  end,
}

-- Disable a LazyVim plugin
return {
  "plugin/name",
  enabled = false,
}
```

### Common LazyVim Issues

#### "I added a plugin but nothing happened"

Check you're using the right file path: `lua/plugins/filename.lua` (not `plugin/`)

#### "My keymaps are overwritten"

LazyVim loads after user config. Use `vim.api.nvim_create_autocmd("User", { pattern = "LazyVimStarted", callback = ... })` for guaranteed last execution.

#### "Which extra provides X?"

```bash
grep -rn "the-feature" ~/.local/share/nvim/lazy/LazyVim/lua/lazyvim/plugins/extras/
```
