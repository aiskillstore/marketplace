---
description: Guide for using MCP symbol search tools effectively
---

# MCP Tools vs Grep - When to Use What

The context-tools plugin provides fast MCP tools for code symbol lookups using a pre-built SQLite index. Use these **instead of grep** when searching for functions, classes, or methods.

## Quick Reference

### ✅ Use MCP Tools When:
- **Finding functions/classes by name**: `search_symbols` with patterns like `setup_*`, `*Handler`, `Config*`
- **Listing what's in a file**: `get_file_symbols` shows all functions/classes without reading the file
- **Getting function source**: `get_symbol_content` retrieves the full source by name
- **Exploring unfamiliar codebases**: Much faster than grep for discovering structure

### ❌ Use Grep When:
- Searching for arbitrary text or comments
- Finding string literals or configuration values
- Searching in non-code files (markdown, JSON, etc.)

## Real-World Example

**Scenario**: User asks "Can we compare our generated code against OSDI?"

**Inefficient approach** (using grep):
```bash
grep -r "setup_model\|setup_instance" jax_spice/devices/*.py
# Problems:
# - Slow on large codebases
# - Pattern matching with wildcards is error-prone
# - Doesn't show function signatures
# - Gets interrupted easily
```

**Efficient approach** (using MCP tools):
```
mcp__plugin_context-tools_repo-map__search_symbols
pattern: "setup_*"
# Result: Instant list of all matching functions with file locations

mcp__plugin_context-tools_repo-map__get_symbol_content
name: "setup_model"
# Result: Full function source code without knowing which file
```

### Example 2: Finding Rust enum variants (Real user interaction)

**Scenario**: Need to find the correct variant name for `enum InstructionData` (e.g., is it `Phi` or `PhiNode`?)

**Inefficient approach** (using grep):
```bash
grep -n "enum InstructionData" openvaf-py/vendor/OpenVAF/openvaf/mir/src
grep -n "Phi" openvaf-py/vendor/OpenVAF/openvaf/mir/src/instructions.rs | head -10
# Problems:
# - Multiple searches needed
# - Have to manually parse enum definition
# - Easy to miss the correct variant name
```

**Efficient approach** (using MCP tools):
```
mcp__plugin_context-tools_repo-map__search_symbols
pattern: "InstructionData"
# Result: Finds the enum definition location instantly

mcp__plugin_context-tools_repo-map__get_symbol_content
name: "InstructionData"
# Result: Complete enum definition showing all variants including PhiNode(_)
```

Benefits: One search, complete enum definition, see all variants at once.

### Example 3: Finding files in directory structure (Real user interaction)

**Scenario**: Need to find PSP103 or BSIM4 models in vendor directory

**Inefficient approach** (using find/ls):
```bash
find vendor/OpenVAF/integration_tests -name "*.va" | grep -E "(psp103|bsim4)"
ls -la openvaf-py/vendor/OpenVAF/
ls -la vendor/
ls -la vendor/VACASK/devices/
ls -la vendor/VACASK/devices/psp103v4/
# Problems:
# - Trial and error with directory paths
# - Multiple ls commands to explore structure
# - Slow on large directory trees
```

**Efficient approach** (using MCP tools):
```
mcp__plugin_context-tools_repo-map__list_files
pattern: "*psp103*"
# Result: Instant list of all PSP103-related files

mcp__plugin_context-tools_repo-map__list_files
pattern: "*.va"
# Result: All Verilog-A model files
```

Benefits: One query, instant results, no trial-and-error with paths.

## Available MCP Tools

**Search for symbols by pattern:**
```
mcp__plugin_context-tools_repo-map__search_symbols
pattern: "get_*"          # Functions starting with "get_"
pattern: "*Handler"       # Classes ending with "Handler"
pattern: "*config*"       # Anything containing "config"
```

**List all symbols in a file:**
```
mcp__plugin_context-tools_repo-map__get_file_symbols
file: "src/models/user.py"
```

**Get source code by exact name:**
```
mcp__plugin_context-tools_repo-map__get_symbol_content
name: "UserModel"         # Class name
name: "process_data"      # Function name
name: "User.save"         # Method name
```

**List indexed files (discover file structure):**
```
mcp__plugin_context-tools_repo-map__list_files
# List all indexed files

mcp__plugin_context-tools_repo-map__list_files
pattern: "*.va"           # All Verilog-A files
pattern: "*psp103*"       # PSP103 model files
pattern: "**/devices/*"   # All files under devices/
```

**Check index status:**
```
mcp__plugin_context-tools_repo-map__repo_map_status
```

**Manually reindex:**
```
mcp__plugin_context-tools_repo-map__reindex_repo_map
```

## Performance

MCP tools use a pre-built SQLite index:
- **10-100x faster** than grep for symbol lookups
- Works instantly even on massive codebases
- No risk of interruption from large result sets

## Multi-Project Support (v0.8.0+)

MCP tools automatically adapt to your current directory:
```bash
cd /path/to/project-A
# MCP tools query project-A's index

cd /path/to/project-B
# MCP tools now query project-B's index (no restart needed!)
```

Each project maintains its own `.claude/repo-map.db` index.

## Troubleshooting

**If MCP tools aren't working:**
1. Check if index exists: `ls -la .claude/repo-map.db`
2. Check status: `/context-tools:status` or use `repo_map_status` tool
3. Manually reindex: `/context-tools:repo-map` or use `reindex_repo_map` tool
4. After plugin updates: Restart Claude Code session (Ctrl+C, then `claude continue`)
