# Diagnostic Flowcharts

This document provides step-by-step diagnostic paths for different problem categories. Each path is designed to narrow down the root cause efficiently.

---

## 1. Keymap Not Working

### Initial Classification

```
User: "Key X doesn't work"
           │
           ▼
    ┌─────────────────────────────────────┐
    │ Is there an error message?          │
    ├─────────────────────────────────────┤
    │ YES → Go to error-patterns.md       │
    │ NO  → Continue below                │
    └─────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────┐
    │ Does the key work in vanilla Neovim?│
    │ nvim -u NONE -c "echo 'test'"       │
    ├─────────────────────────────────────┤
    │ YES → Config/plugin issue           │
    │ NO  → Terminal/system issue         │
    └─────────────────────────────────────┘
```

### Config/Plugin Path

```
Step 1: Is the mapping registered?
┌──────────────────────────────────────────────────────────┐
│ :map <the-key>                                           │
│ :verbose map <the-key>  (shows where it was defined)     │
├──────────────────────────────────────────────────────────┤
│ Shows mapping → Mapping exists, execution problem        │
│ No mapping   → Mapping not created, registration problem │
└──────────────────────────────────────────────────────────┘

Step 2a: Mapping exists but doesn't execute
┌──────────────────────────────────────────────────────────┐
│ Possible causes:                                         │
│ • Buffer-local mapping shadowed by global                │
│ • Mode mismatch (nmap vs vmap vs imap)                   │
│ • which-key timeout/trigger issue                        │
│ • Conflicting mapping with higher priority               │
├──────────────────────────────────────────────────────────┤
│ Test: :lua vim.keymap.set('n', '<the-key>', function()   │
│         print('test') end)                               │
│ Then press the key - if 'test' prints, original mapping  │
│ is being overwritten somewhere                           │
└──────────────────────────────────────────────────────────┘

Step 2b: Mapping not registered
┌──────────────────────────────────────────────────────────┐
│ Possible causes:                                         │
│ • Plugin not loaded (lazy loading)                       │
│ • Config file not sourced                                │
│ • Conditional logic excluding this setup                 │
│ • Syntax error in config (silent failure)                │
├──────────────────────────────────────────────────────────┤
│ Check: :Lazy → Is the plugin loaded?                     │
│ Check: :messages → Any errors during startup?            │
│ Check: :scriptnames → Was the config file sourced?       │
└──────────────────────────────────────────────────────────┘
```

### Leader/Localleader Specific Issues

```
Step 1: Verify the leader is set correctly
┌──────────────────────────────────────────────────────────┐
│ nvim --headless -c "lua print(vim.g.mapleader)" -c qa    │
│ nvim --headless -c "lua print(vim.g.maplocalleader)" -c qa│
├──────────────────────────────────────────────────────────┤
│ Expected: " " (space) for leader, "\" for localleader    │
│ Empty/nil → Leader not set, must be set BEFORE mappings  │
└──────────────────────────────────────────────────────────┘

Step 2: Check mapping uses correct notation
┌──────────────────────────────────────────────────────────┐
│ In config: vim.keymap.set('n', '<leader>x', ...)         │
│                               vs                          │
│            vim.keymap.set('n', '<localleader>x', ...)    │
├──────────────────────────────────────────────────────────┤
│ Note: <leader> and <localleader> are expanded at         │
│ definition time, not execution time!                     │
└──────────────────────────────────────────────────────────┘

Step 3: which-key popup not showing for localleader
┌──────────────────────────────────────────────────────────┐
│ Common issue: which-key auto-triggers for Space but not  │
│ for backslash                                            │
├──────────────────────────────────────────────────────────┤
│ Test: :lua require('which-key').show('\\')               │
│ If popup appears → Auto-trigger config issue             │
│ If no popup → which-key registration issue               │
├──────────────────────────────────────────────────────────┤
│ Fix: Add localleader to which-key triggers in config     │
│                                                          │
│ require('which-key').setup({                             │
│   triggers = {                                           │
│     { "<auto>", mode = "nxso" },                        │
│     { "\\", mode = { "n", "v" } },  -- Add this!        │
│   },                                                     │
│ })                                                       │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Plugin Not Loading

```
Step 1: Check if plugin is declared
┌──────────────────────────────────────────────────────────┐
│ :Lazy → Search for plugin name                           │
├──────────────────────────────────────────────────────────┤
│ Not listed → Plugin spec not added or has syntax error   │
│ Listed as "not loaded" → Lazy loading conditions not met │
│ Listed as "loaded" → Plugin loaded, feature issue        │
└──────────────────────────────────────────────────────────┘

Step 2: For "not loaded" plugins
┌──────────────────────────────────────────────────────────┐
│ Check lazy loading conditions in plugin spec:            │
│                                                          │
│ {                                                        │
│   "plugin/name",                                         │
│   event = "VeryLazy",        -- Loads after UI          │
│   ft = "markdown",           -- Loads for filetype      │
│   cmd = "PluginCommand",     -- Loads on command        │
│   keys = { "<leader>p" },    -- Loads on keypress       │
│ }                                                        │
├──────────────────────────────────────────────────────────┤
│ Force load for testing: :Lazy load plugin-name           │
│ If plugin works after → Lazy loading condition problem   │
│ If still broken → Plugin itself has issues               │
└──────────────────────────────────────────────────────────┘

Step 3: For loaded but not working plugins
┌──────────────────────────────────────────────────────────┐
│ nvim --headless -c "lua print(require('plugin').setup)"  │
│   -c "qa" 2>&1                                           │
├──────────────────────────────────────────────────────────┤
│ "function" → Setup function exists                       │
│ "nil" → Module doesn't export setup (API issue)          │
├──────────────────────────────────────────────────────────┤
│ Check if your config calls setup():                      │
│ grep -rn "require.*plugin.*setup" ~/.config/nvim/        │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Performance Issues

### Startup Time Analysis

```
Step 1: Measure baseline
┌──────────────────────────────────────────────────────────┐
│ nvim --startuptime /tmp/startup.log +q                   │
│ tail -1 /tmp/startup.log  # Total time                   │
├──────────────────────────────────────────────────────────┤
│ < 100ms  → Fast (good)                                   │
│ 100-300ms → Acceptable                                   │
│ > 300ms  → Slow, needs investigation                     │
│ > 1000ms → Very slow, likely plugin problem              │
└──────────────────────────────────────────────────────────┘

Step 2: Identify slow components
┌──────────────────────────────────────────────────────────┐
│ Sort by time:                                            │
│ sort -t: -k2 -n /tmp/startup.log | tail -20              │
├──────────────────────────────────────────────────────────┤
│ Look for:                                                │
│ • Large require() times (plugin loading)                 │
│ • Long sourcing times (config files)                     │
│ • Repeated entries (multiple loads)                      │
└──────────────────────────────────────────────────────────┘

Step 3: Test with minimal config
┌──────────────────────────────────────────────────────────┐
│ nvim -u NONE --startuptime /tmp/minimal.log +q           │
│ Compare with full config - difference is plugin overhead │
└──────────────────────────────────────────────────────────┘
```

### Runtime Performance

```
Step 1: Identify symptom
┌──────────────────────────────────────────────────────────┐
│ • Lag when typing → Completion/LSP issue                 │
│ • Lag when scrolling → Treesitter/syntax issue           │
│ • Freeze on save → Format/lint issue                     │
│ • Periodic freezes → Async operation blocking            │
└──────────────────────────────────────────────────────────┘

Step 2: Profile runtime
┌──────────────────────────────────────────────────────────┐
│ :profile start /tmp/profile.log                          │
│ :profile func *                                          │
│ :profile file *                                          │
│ [Do the action that causes lag]                          │
│ :profile stop                                            │
│ :e /tmp/profile.log                                      │
├──────────────────────────────────────────────────────────┤
│ Look for functions with high "Total" time                │
└──────────────────────────────────────────────────────────┘
```

---

## 4. UI/Visual Issues

```
Step 1: Terminal vs Neovim
┌──────────────────────────────────────────────────────────┐
│ echo $TERM          # Should be xterm-256color or better │
│ nvim -c "echo &t_Co" -c "q"  # Should be 256 or higher   │
├──────────────────────────────────────────────────────────┤
│ Wrong colors often caused by:                            │
│ • TERM not set correctly                                 │
│ • termguicolors not enabled                              │
│ • Colorscheme not installed/loaded                       │
└──────────────────────────────────────────────────────────┘

Step 2: Check termguicolors
┌──────────────────────────────────────────────────────────┐
│ nvim --headless -c "lua print(vim.o.termguicolors)"      │
│   -c "qa" 2>&1                                           │
├──────────────────────────────────────────────────────────┤
│ true → 24-bit color enabled (good for modern terminals)  │
│ false → Using terminal palette (may cause color issues)  │
└──────────────────────────────────────────────────────────┘

Step 3: Missing UI elements
┌──────────────────────────────────────────────────────────┐
│ • No statusline → Check lualine/statusline plugin loaded │
│ • No icons → Font doesn't have Nerd Font glyphs          │
│ • Broken borders → Unicode not rendering (font/terminal) │
│ • No highlights → Colorscheme not applied after plugins  │
└──────────────────────────────────────────────────────────┘
```

---

## 5. LSP Issues

```
Step 1: Check LSP server status
┌──────────────────────────────────────────────────────────┐
│ :LspInfo         # Shows attached clients               │
│ :LspLog          # Shows LSP communication log          │
│ :checkhealth lsp # Comprehensive LSP health check       │
└──────────────────────────────────────────────────────────┘

Step 2: Server not attaching
┌──────────────────────────────────────────────────────────┐
│ Possible causes:                                         │
│ • Server not installed (check :Mason)                    │
│ • Filetype not detected (:set ft?)                       │
│ • Root directory not found (no .git, package.json, etc.) │
│ • Server crashed on startup (check :LspLog)              │
├──────────────────────────────────────────────────────────┤
│ Manual attach test:                                      │
│ :lua vim.lsp.start({ name = "server", cmd = {"cmd"} })   │
└──────────────────────────────────────────────────────────┘

Step 3: Server attached but not working
┌──────────────────────────────────────────────────────────┐
│ • No completions → Check capabilities and nvim-cmp setup │
│ • No diagnostics → Server might need project config      │
│ • Slow responses → Server overloaded or misconfigured    │
├──────────────────────────────────────────────────────────┤
│ Debug: :lua print(vim.inspect(vim.lsp.get_clients()))    │
└──────────────────────────────────────────────────────────┘
```

---

## 6. After Plugin Update

```
Step 1: Identify what changed
┌──────────────────────────────────────────────────────────┐
│ Check lazy-lock.json for version changes:                │
│ git diff ~/.config/nvim/lazy-lock.json                   │
├──────────────────────────────────────────────────────────┤
│ If tracked in git, you can see exact version changes     │
└──────────────────────────────────────────────────────────┘

Step 2: Rollback test
┌──────────────────────────────────────────────────────────┐
│ :Lazy restore plugin-name  # Restore to locked version   │
│ Or manually edit lazy-lock.json with previous commit     │
├──────────────────────────────────────────────────────────┤
│ If rollback fixes it → Plugin update introduced bug      │
│ → Check plugin's GitHub Issues/Changelog                 │
└──────────────────────────────────────────────────────────┘

Step 3: Breaking change detection
┌──────────────────────────────────────────────────────────┐
│ Common breaking change patterns:                         │
│ • Function renamed or removed                            │
│ • Config option changed                                  │
│ • Dependency added/removed                               │
│ • Default behavior changed                               │
├──────────────────────────────────────────────────────────┤
│ Check: Plugin's CHANGELOG.md, Releases page, commit msgs │
└──────────────────────────────────────────────────────────┘
```
