# Neovim Configuration Best Practices

Recommendations for maintainable, performant, and idiomatic Neovim configuration.

## 1. Plugin Manager Patterns

### 1.1 lazy.nvim

#### opts vs config

| Approach | When to Use | Example |
|----------|-------------|---------|
| `opts = {}` | Simple configuration tables | Most plugins |
| `config = function()` | Complex setup, conditionals, multiple calls | LSP, custom logic |
| `opts` + `config` | Merge opts then run additional setup | Advanced customization |

**Prefer `opts`** - it enables lazy.nvim's automatic config merging:

```lua
-- Good: Using opts
{
  "nvim-telescope/telescope.nvim",
  opts = {
    defaults = {
      layout_strategy = "horizontal",
    },
  },
}

-- Avoid: Unnecessary config function
{
  "nvim-telescope/telescope.nvim",
  config = function()
    require("telescope").setup({
      defaults = {
        layout_strategy = "horizontal",
      },
    })
  end,
}
```

**Use `config`** when you need:
- Conditional logic
- Multiple function calls
- Access to plugin functions beyond setup()

```lua
-- Good: Complex setup needs config
{
  "neovim/nvim-lspconfig",
  config = function()
    local lspconfig = require("lspconfig")
    lspconfig.lua_ls.setup({})
    lspconfig.pyright.setup({})
    -- Multiple servers, conditional setup
  end,
}
```

#### Lazy Loading Triggers

| Trigger | Use Case | Example |
|---------|----------|---------|
| `event` | Feature needed on buffer actions | `event = "BufReadPost"` |
| `cmd` | Command-only plugins | `cmd = "Telescope"` |
| `ft` | Filetype-specific | `ft = { "lua", "python" }` |
| `keys` | Keymap-triggered | `keys = { "<leader>ff" }` |
| `lazy = false` | Always needed | colorschemes, core UI |

**Common Events**:
```lua
event = "VeryLazy"        -- After UI loads, good for UI plugins
event = "BufReadPost"     -- When opening existing file
event = "BufNewFile"      -- When creating new file
event = "InsertEnter"     -- When entering insert mode
event = "LspAttach"       -- When LSP attaches to buffer
```

#### Dependencies

```lua
-- Good: Explicit dependencies
{
  "nvim-telescope/telescope.nvim",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "nvim-tree/nvim-web-devicons",
  },
}

-- Avoid: Separate entries for tightly-coupled plugins
-- (they may load in wrong order)
```

---

### 1.2 packer.nvim (Legacy)

For migration reference:

| packer | lazy.nvim |
|--------|-----------|
| `use { "plugin" }` | `{ "plugin" }` |
| `config = function() ... end` | Same |
| `requires = { }` | `dependencies = { }` |
| `run = ":TSUpdate"` | `build = ":TSUpdate"` |
| `opt = true` | `lazy = true` |
| `event = "BufRead"` | `event = "BufReadPost"` |

---

## 2. Option Setting Patterns

### vim.opt vs vim.o vs vim.g

| API | Use For | Lua Type | Example |
|-----|---------|----------|---------|
| `vim.opt` | List/map options | Lua tables | `vim.opt.completeopt = {"menu", "menuone"}` |
| `vim.o` | Simple options | Strings/numbers/booleans | `vim.o.number = true` |
| `vim.g` | Global variables | Any | `vim.g.mapleader = " "` |
| `vim.bo` | Buffer-local options | Any | `vim.bo.filetype = "lua"` |
| `vim.wo` | Window-local options | Any | `vim.wo.wrap = false` |

**Key Differences**:

```lua
-- vim.opt: Supports append/prepend/remove
vim.opt.path:append("**")
vim.opt.wildignore:append({ "*.o", "*.a" })

-- vim.o: Direct assignment only
vim.o.path = vim.o.path .. ",**"  -- Manual concatenation

-- vim.opt: Returns Option object
print(vim.opt.number)        -- prints Option object
print(vim.opt.number:get())  -- prints actual value

-- vim.o: Returns value directly
print(vim.o.number)          -- prints true/false
```

**Recommendation**: Use `vim.opt` for list-like options, `vim.o` for simple values.

---

### Common Settings Template

```lua
-- Leader keys (MUST be set before lazy.nvim)
vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- UI
vim.o.number = true
vim.o.relativenumber = true
vim.o.signcolumn = "yes"
vim.o.cursorline = true
vim.o.termguicolors = true

-- Editing
vim.o.expandtab = true
vim.o.shiftwidth = 2
vim.o.tabstop = 2
vim.o.smartindent = true

-- Search
vim.o.ignorecase = true
vim.o.smartcase = true
vim.o.hlsearch = true

-- Performance
vim.o.updatetime = 250
vim.o.timeoutlen = 300

-- Completion
vim.opt.completeopt = { "menu", "menuone", "noselect" }

-- Clipboard (use system clipboard)
vim.opt.clipboard:append("unnamedplus")
```

---

## 3. Keymap Best Practices

### Using vim.keymap.set

```lua
-- Basic structure
vim.keymap.set(mode, lhs, rhs, opts)

-- Good: Descriptive options
vim.keymap.set("n", "<leader>ff", "<cmd>Telescope find_files<cr>", {
  desc = "Find files",
  silent = true,
})

-- Good: Buffer-local mapping
vim.keymap.set("n", "K", vim.lsp.buf.hover, {
  buffer = bufnr,
  desc = "Hover documentation",
})

-- Good: Lua function RHS
vim.keymap.set("n", "<leader>q", function()
  vim.diagnostic.setloclist()
end, { desc = "Open diagnostic list" })
```

### Common Patterns

```lua
-- Use <cmd> for Ex commands (no mode switching)
vim.keymap.set("n", "<leader>w", "<cmd>w<cr>")  -- Good
vim.keymap.set("n", "<leader>w", ":w<cr>")      -- Works but less efficient

-- Use callback for complex logic
vim.keymap.set("n", "<leader>t", function()
  if vim.bo.filetype == "lua" then
    vim.cmd("source %")
  else
    print("Not a Lua file")
  end
end)

-- Escape special characters
vim.keymap.set("n", "<C-\\>", ...)  -- Backslash needs escaping
vim.keymap.set("n", "<lt>", ...)   -- Literal < character
```

### Keymap Organization

```lua
-- Group by functionality
local map = vim.keymap.set

-- File operations
map("n", "<leader>fs", "<cmd>w<cr>", { desc = "Save file" })
map("n", "<leader>fq", "<cmd>q<cr>", { desc = "Quit" })

-- Buffer operations
map("n", "<leader>bd", "<cmd>bdelete<cr>", { desc = "Delete buffer" })
map("n", "<leader>bn", "<cmd>bnext<cr>", { desc = "Next buffer" })

-- LSP (set in on_attach)
local function on_attach(client, bufnr)
  local opts = { buffer = bufnr }
  map("n", "gd", vim.lsp.buf.definition, opts)
  map("n", "gr", vim.lsp.buf.references, opts)
  map("n", "K", vim.lsp.buf.hover, opts)
end
```

---

## 4. Directory Structure

### Recommended Layout

```
~/.config/nvim/
├── init.lua                  # Entry point (minimal)
├── lazy-lock.json            # Plugin versions (commit this)
├── lua/
│   ├── config/
│   │   ├── options.lua       # vim.opt settings
│   │   ├── keymaps.lua       # Global keymaps
│   │   ├── autocmds.lua      # Autocommands
│   │   └── lazy.lua          # lazy.nvim bootstrap
│   └── plugins/
│       ├── init.lua          # Plugin list OR
│       ├── colorscheme.lua   # Per-plugin files
│       ├── lsp.lua
│       ├── completion.lua
│       ├── treesitter.lua
│       └── ui.lua
├── after/
│   └── ftplugin/             # Filetype-specific settings
│       ├── lua.lua
│       └── python.lua
└── snippets/                 # Custom snippets (if using LuaSnip)
```

### init.lua Structure

```lua
-- init.lua (minimal, just loads modules)
require("config.options")
require("config.lazy")      -- Loads lazy.nvim and plugins
require("config.keymaps")
require("config.autocmds")
```

### Modular Plugin Specs

```lua
-- lua/plugins/telescope.lua
return {
  "nvim-telescope/telescope.nvim",
  dependencies = { "nvim-lua/plenary.nvim" },
  cmd = "Telescope",
  keys = {
    { "<leader>ff", "<cmd>Telescope find_files<cr>", desc = "Find files" },
    { "<leader>fg", "<cmd>Telescope live_grep<cr>", desc = "Live grep" },
  },
  opts = {
    defaults = {
      layout_strategy = "horizontal",
    },
  },
}
```

---

## 5. Anti-Patterns

### Avoid These

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| `vim.cmd("set number")` | Extra VimScript execution | `vim.o.number = true` |
| `vim.api.nvim_set_keymap` | Low-level API, no Lua function RHS | `vim.keymap.set` |
| `autocmd` in vim.cmd | Not native, harder to manage | `vim.api.nvim_create_autocmd` |
| Nested `pcall` everywhere | Hides errors, hard to debug | pcall at entry points only |
| `require` at top of lazy spec | Loads plugin immediately | Move inside `config` function |

### Common Mistakes

```lua
-- Wrong: This loads telescope immediately
{
  "nvim-telescope/telescope.nvim",
  config = require("telescope").setup({}),  -- Evaluates now!
}

-- Correct: Defer execution
{
  "nvim-telescope/telescope.nvim",
  config = function()
    require("telescope").setup({})
  end,
}

-- Wrong: Creating autocmds that reference unloaded plugins
vim.api.nvim_create_autocmd("BufWritePre", {
  callback = function()
    require("conform").format()  -- May not be loaded yet
  end,
})

-- Correct: Let plugin handle its own autocmds or use event trigger
{
  "stevearc/conform.nvim",
  event = "BufWritePre",
  opts = { format_on_save = true },
}
```

---

## 6. Performance Tips

1. **Defer non-essential plugins**: Use `event = "VeryLazy"` for UI enhancements
2. **Profile regularly**: `:Lazy profile` shows plugin load times
3. **Minimize startup plugins**: Only colorscheme and essential UI should load immediately
4. **Use filetype triggers**: `ft = "lua"` instead of loading for all files
5. **Avoid synchronous HTTP**: Use async methods for remote operations
6. **Cache expensive computations**: Store results of heavy operations
7. **Lazy-load large language servers**: Use `mason-lspconfig` for on-demand installation
