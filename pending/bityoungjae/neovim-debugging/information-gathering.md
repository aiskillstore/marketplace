# Information Gathering Protocols

This document describes when and how to gather information from users, and when to gather it yourself programmatically.

---

## The Golden Rule

> **Gather programmatically first, ask the user only when necessary.**

Every question you ask the user costs time and requires them to know what you need. Before asking, try:

1. **Headless commands** - Run Neovim non-interactively to check state
2. **File inspection** - Read config files directly
3. **Inference** - Deduce from context (LazyVim? Plugin manager? Error message details?)

---

## What You Can Gather Programmatically

### System Information

```bash
# Neovim version
nvim --version | head -1

# Operating system
uname -a

# Terminal emulator (from env, not always reliable)
echo $TERM_PROGRAM $TERM

# Config directory
nvim --headless -c "lua print(vim.fn.stdpath('config'))" -c "qa" 2>&1
```

### Configuration State

```bash
# Check a plugin is installed
nvim --headless -c "lua print(pcall(require, 'telescope'))" -c "qa" 2>&1

# Get option value
nvim --headless -c "lua print(vim.o.tabstop)" -c "qa" 2>&1

# Get global variable
nvim --headless -c "lua print(vim.g.mapleader)" -c "qa" 2>&1

# Check mapping exists
nvim --headless -c "verbose map <leader>ff" -c "qa" 2>&1

# Get plugin config
nvim --headless -c "lua print(vim.inspect(require('telescope').extensions))" -c "qa" 2>&1
```

### File Contents

```bash
# LazyVim extras enabled
cat ~/.config/nvim/lazyvim.json 2>/dev/null

# Plugin specs
cat ~/.config/nvim/lua/plugins/*.lua

# Check for specific pattern in config
grep -rn "which-key" ~/.config/nvim/lua/

# Recent plugin updates
git -C ~/.local/share/nvim/lazy/plugin-name log --oneline -5
```

### Plugin State

```bash
# List loaded plugins (using lazy.nvim)
nvim --headless -c "lua for name, _ in pairs(require('lazy.core.config').plugins) do print(name) end" -c "qa" 2>&1

# Check plugin version
cat ~/.local/share/nvim/lazy/telescope.nvim/.git/HEAD

# Check lazy-lock versions
cat ~/.config/nvim/lazy-lock.json | jq '.["telescope.nvim"]'
```

---

## What Requires User Input

### Interactive State (Cannot Be Reproduced Headlessly)

| Information Needed | Why Ask User |
|-------------------|--------------|
| "What do you see when you press X?" | Runtime behavior with their full state |
| "Does the popup appear?" | Visual confirmation |
| "What's in your clipboard?" | System clipboard state |
| "Which terminal are you using?" | GUI vs TUI behavior differs |

### Reproduction Steps

| Information Needed | Why Ask User |
|-------------------|--------------|
| "What file were you editing?" | Filetype-specific issues |
| "What did you do right before the error?" | Sequence matters for race conditions |
| "Is this a new project or existing?" | LSP root detection varies |

### Preference/Intent

| Information Needed | Why Ask User |
|-------------------|--------------|
| "Do you want to keep this behavior?" | Understanding desired vs actual |
| "Which solution do you prefer?" | Multiple valid fixes exist |

---

## How to Ask Effectively

### Principle 1: Ask Specific, Closed Questions

```
❌ Bad: "Can you share your config?"
   → Too broad, wastes user time, produces noise

✅ Good: "What's the output of `:lua print(vim.g.maplocalleader)`?"
   → Specific command, specific answer expected

✅ Good: "Does pressing Space show the which-key popup?"
   → Yes/No answer that discriminates between hypotheses
```

### Principle 2: Explain Why You're Asking

```
❌ Bad: "Run this command and tell me the output."
   → User doesn't know why, may skip if seems tedious

✅ Good: "To check if the plugin is loading correctly, run `:Lazy` and
   tell me if 'telescope' shows as 'loaded' or 'not loaded'."
   → User understands the diagnostic logic
```

### Principle 3: Provide Copy-Paste Commands

```
❌ Bad: "Check your leader key setting."
   → User may not know how

✅ Good: "Run this in Neovim and paste the result:
   `:lua print('leader=' .. vim.inspect(vim.g.mapleader))`"
   → Ready to copy, exact format expected
```

### Principle 4: Use Comparative Questions to Narrow Scope

```
"Does `<leader>` (Space) work with which-key but `<localleader>` (\\) doesn't?"

If YES → Problem isolated to localleader handling
If NO → which-key itself may be broken
```

---

## Question Templates by Problem Type

### Error Messages

```markdown
Please share:
1. The complete error message (including any "stack traceback" lines)
2. What action triggered the error
3. Whether this happens every time or intermittently

Copy the error by pressing `q` to dismiss, then `:messages` to see history.
```

### Key Not Working

```markdown
Let me understand the issue:

1. When you press [KEY], what happens?
   - Nothing at all
   - Something different than expected
   - Error message appears

2. Run `:map [KEY]` and share the output.
   (If blank, the key isn't mapped)

3. Does pressing Space (leader) show the which-key popup?
```

### Plugin Not Working

```markdown
Let's check the plugin status:

1. Run `:Lazy` and search for "[PLUGIN]"
   - Is it listed?
   - Does it show as "loaded" or "not loaded"?

2. Run `:checkhealth [plugin]` if available and share any warnings.
```

### LSP Issues

```markdown
Let's check your LSP setup:

1. Open a file of the type that's having issues
2. Run `:LspInfo` and share the output
3. Run `:lua print(vim.bo.filetype)` to confirm the detected filetype
```

### Performance Issues

```markdown
Let's measure:

1. Run this and share the last line:
   `nvim --startuptime /tmp/startup.log +q && tail -1 /tmp/startup.log`

2. Does the lag happen:
   - During startup
   - When typing
   - When opening specific files
   - When running specific commands
```

---

## Information Request Checklist

Before asking the user anything, verify:

- [ ] I cannot get this information via headless commands
- [ ] I cannot infer this from files I can read
- [ ] This information will actually help narrow down the cause
- [ ] I'm asking the minimum necessary to make progress
- [ ] My question is specific and actionable
- [ ] I've explained why I need this information

---

## Common Mistakes

### Over-Asking

```
❌ "Can you share:
   - Your init.lua
   - Your plugins folder
   - Your lazy-lock.json
   - Output of :Lazy
   - Output of :checkhealth
   - Your terminal and version
   - ..."
```

This overwhelms users. Instead, start with the minimum:
```
✅ "The error mentions 'telescope'. Let's verify it's installed:
   Run `:Lazy` and tell me if telescope shows as 'loaded'."
```

### Asking Before Understanding

```
❌ User: "My config is broken"
   You: "Can you share your config files?"
```

First understand the symptom:
```
✅ User: "My config is broken"
   You: "What specifically is broken? Error message, missing feature,
        or unexpected behavior?"
```

### Asking for Things You Can Check

```
❌ "What's your Neovim version?"
   (You can run: nvim --version | head -1)

❌ "Do you use LazyVim?"
   (You can run: cat ~/.config/nvim/lazyvim.json)

❌ "What plugins do you have?"
   (You can run: ls ~/.local/share/nvim/lazy/)
```

---

## Building a Diagnostic Picture

Structure your information gathering like an interview:

```
<gathering_strategy>
1. SYMPTOM: What exactly is the user experiencing?
   → Get specific, observable behavior

2. CONTEXT: Where does this happen?
   → Filetype, plugin, buffer, mode

3. HISTORY: Did this work before?
   → Yes → What changed? (Updates, config edits)
   → No → New setup, may be missing prerequisites

4. REPRODUCTION: Can you reliably trigger this?
   → Yes → Get exact steps
   → No → Intermittent issue, may need state analysis

5. ISOLATION: Does this happen in minimal config?
   → nvim -u NONE (no plugins)
   → nvim -u NORC (no user config)
   → Single plugin enabled
</gathering_strategy>
```
