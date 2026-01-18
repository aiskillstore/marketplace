---
name: port-allocator
description: Automatically allocate and manage development server ports, avoiding port conflicts between multiple Claude Code instances
---

# Port Allocator

Smart port allocator that only assigns ports to real projects containing `package.json`.

## Usage

| Command | Description |
|---------|-------------|
| `/port-allocator` | Allocate/query port for current project |
| `/port-allocator list` | List all allocated ports |
| `/port-allocator scan` | Scan code directory, discover and allocate ports for new projects |
| `/port-allocator config <path>` | Set the main code directory path |
| `/port-allocator add <dir-path>` | Manually add port allocation for a project |
| `/port-allocator allow` | Configure Claude Code permissions for this skill's commands |

## Important Rules

### 1. Only Operate on Current Project's Ports When Restarting Services

When restarting the development server, **only kill processes within the current project's port range**, never affect other ports:

```bash
# Correct: Only kill current project ports (e.g., 3000-3009)
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# Wrong: Kill all node processes or other ports
pkill -f node  # Will affect other projects!
lsof -ti:3010 | xargs kill  # This is another project's port!
```

### 2. Append Rather Than Overwrite When Updating CLAUDE.md

When updating `~/.claude/CLAUDE.md`, **must preserve the user's existing content**:

```bash
# Correct: Check and append or update specific sections
# Wrong: Directly overwrite the entire file
```

## Execution Steps

### Command: `/port-allocator allow`

Configure Claude Code to allow commands used by this skill, avoiding manual confirmation each time:

1. Read `~/.claude/settings.json` (if exists)
2. Merge the following commands into `permissions.allow` array (preserve existing config):

```json
{
  "permissions": {
    "allow": [
      "Bash(ls -d *)",
      "Bash(find * -maxdepth * -name package.json *)",
      "Bash(cat ~/.claude/*)",
      "Bash(dirname *)",
      "Bash(lsof -i:3*)",
      "Bash(lsof -ti:3*)"
    ]
  }
}
```

3. Write updated settings.json
4. Output the list of added permissions

**Output Format:**
```
Configured Claude Code permissions

Added allowed command patterns:
  - Bash(ls -d *)
  - Bash(find * -maxdepth * -name package.json *)
  - Bash(cat ~/.claude/*)
  - Bash(lsof -i:3*)
  - Bash(lsof -ti:3*)

Config file: ~/.claude/settings.json
```

### Command: `/port-allocator config <path>`

Set the user's main code directory:

1. **Verify path exists** (required! Error and exit if not found)
2. Update `code_root` field in `~/.claude/port-registry.json`
3. Output confirmation

### First Run: Auto-Detection

On first run (when `~/.claude/port-registry.json` doesn't exist or has no `code_root`), automatically detect the code directory:

```bash
# Check common code directories
for dir in ~/Codes ~/Code ~/Projects ~/Dev ~/Development ~/repos; do
  if [ -d "$dir" ]; then
    CODE_ROOT="$dir"
    break
  fi
done

# If none exist, default to ~/Codes
CODE_ROOT="${CODE_ROOT:-~/Codes}"
```

**Auto-detection output:**
```
First run, detecting code directory...

Code directory detected: ~/Codes

Port registry initialized: ~/.claude/port-registry.json

To change, use:
   /port-allocator config ~/your/code/path
```

**If no directory found:**
```
Could not auto-detect code directory.

Please configure manually:
   /port-allocator config ~/your/code/path

Common locations:
   ~/Codes, ~/Code, ~/Projects, ~/Dev
```

### Command: `/port-allocator scan`

Scan code directory, automatically discover and register projects:

1. Read `~/.claude/port-registry.json` to get `code_root`
   - If config doesn't exist, run auto-detection first
   - If `code_root` directory doesn't exist, prompt user to configure
2. Find all directories containing `package.json` (exact to package.json location):

```bash
# Find all package.json, exclude build artifact directories
find <code_root> -maxdepth 3 -name "package.json" -type f \
  -not -path "*/.next/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" | while read pkg; do
  dirname "$pkg"
done
```

3. **Important**: Path must be exact to the directory containing `package.json`
   - Correct: `~/Codes/chekusu/landing`
   - Wrong: `~/Codes/chekusu` (if package.json is in subdirectory)

4. For each discovered project directory:
   - Check if already in registry
   - If not, allocate next available port range
5. Update config file (**append mode**, don't overwrite user content)
6. Output scan result summary

### Command: `/port-allocator` (default)

Allocate/query port for current project:

1. Get current working directory
2. Read config to get `code_root` and allocated ports
3. Match current directory to corresponding project
4. If no `package.json`, indicate this is not a project needing ports
5. If exists, check if port already allocated, auto-allocate if not
6. Output port info

### Command: `/port-allocator list`

List all allocated ports (read-only operation).

## Output Format

### Port Information
```
Project directory: ~/Codes/chekusu/landing
package.json: Detected
Port range: 3000-3009
   - Main app: 3000
   - API: 3001
   - Other services: 3002-3009

Warning: Only operate on ports 3000-3009 when restarting services!
```

### Scan Results
```
Scan complete: ~/Codes

Registered projects (N):
   - chekusu/landing: 3000-3009
   - saifuri: 3010-3019

Newly discovered projects (M):
   - new-project: 3090-3099 (newly allocated)

Skipped (K):
   - .next, node_modules (build artifacts)
   - research-folder (no package.json)
```

## Port Allocation Rules

- Each project is allocated **10 consecutive ports**
- Starting port: 3000
- Interval: 10
- `x0`: Main application (e.g., 3000, 3010, 3020)
- `x1`: API service (e.g., 3001, 3011, 3021)
- `x2-x9`: Other services (database, cache, etc.)

## Configuration Files

- **Port registry**: `~/.claude/port-registry.json`
- **Global instructions**: `~/.claude/CLAUDE.md` (append mode updates)
- **Claude Code settings**: `~/.claude/settings.json` (stores allowedCommands)
- **Skip patterns**: `.next`, `node_modules`, `dist`, `build`

## Notes

1. **Only operate on project ports** - Never affect other projects when restarting services
2. **Append not overwrite** - Preserve user's existing content when updating config files
3. **Precise paths** - Point to actual directory containing package.json
4. **Skip build artifacts** - .next, node_modules, etc. don't get port allocation
5. **First use** - Recommend running `/port-allocator allow` to configure permissions first
