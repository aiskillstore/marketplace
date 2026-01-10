# Resolve Naming Clashes

Interactively review and resolve naming clashes in the codebase.

First, get the list of clashes:

```bash
python3 << 'PYSCRIPT'
import json
import re
from pathlib import Path

repo_map = Path(".claude/repo-map.md")
config_path = Path(".claude/clash-config.json")

# Load existing config
config = {"ignoredPairs": [], "ignoredDirs": [], "ignoredPatterns": []}
if config_path.exists():
    try:
        config = json.loads(config_path.read_text())
    except:
        pass

if not repo_map.exists():
    print(json.dumps({"error": "No repo map found. Run /repo-map first."}))
    exit(0)

content = repo_map.read_text()
clashes = []

# Parse clashes (multi-line format)
# Format: - **Name1** (file1.py)\n  ↔ **Name2** (file2.py)\n  Reason: ...
clash_pattern = re.compile(
    r'- \*\*([^*]+)\*\* \(([^)]+)\)\n\s+↔ \*\*([^*]+)\*\* \(([^)]+)\)\n\s+Reason: ([^\n]+)',
    re.MULTILINE
)

# Parse similar classes
class_section = re.search(r'## ⚠️ Potentially Similar Classes.*?(?=\n## |\Z)', content, re.DOTALL)
if class_section:
    for match in clash_pattern.finditer(class_section.group(0)):
        clashes.append({
            'type': 'class',
            'name1': match.group(1), 'loc1': match.group(2),
            'name2': match.group(3), 'loc2': match.group(4),
            'reason': match.group(5)
        })

# Parse similar functions
func_section = re.search(r'## ⚠️ Potentially Similar Functions.*?(?=\n## |\Z)', content, re.DOTALL)
if func_section:
    for match in clash_pattern.finditer(func_section.group(0)):
        clashes.append({
            'type': 'function',
            'name1': match.group(1), 'loc1': match.group(2),
            'name2': match.group(3), 'loc2': match.group(4),
            'reason': match.group(5)
        })

# Filter out already-ignored clashes
def is_ignored(clash):
    pair_key = tuple(sorted([f"{clash['loc1']}::{clash['name1']}", f"{clash['loc2']}::{clash['name2']}"]))
    if list(pair_key) in config.get("ignoredPairs", []):
        return True
    for d in config.get("ignoredDirs", []):
        if clash['loc1'].startswith(d) or clash['loc2'].startswith(d):
            return True
    return False

unresolved = [c for c in clashes if not is_ignored(c)]

print(json.dumps({
    "total": len(clashes),
    "resolved": len(clashes) - len(unresolved),
    "unresolved": len(unresolved),
    "clashes": unresolved[:20],  # Show first 20
    "config": config
}, indent=2))
PYSCRIPT
```

After getting the clashes, present them to the user one at a time using AskUserQuestion with these options:

For each clash, show:
- The two symbols and their locations
- The reason they were flagged (similar names, similar docstrings)

Resolution options:
1. **Ignore this pair** - Add to ignoredPairs in clash-config.json
2. **Ignore directory** - Add the common parent directory to ignoredDirs
3. **Rename symbol** - Help user rename one of the symbols
4. **Skip for now** - Move to next clash without action

To save an ignore decision:

```bash
python3 << 'PYSCRIPT'
import json
from pathlib import Path

config_path = Path(".claude/clash-config.json")
config = {"ignoredPairs": [], "ignoredDirs": [], "ignoredPatterns": []}
if config_path.exists():
    try:
        config = json.loads(config_path.read_text())
    except:
        pass

# Add ignore - replace IGNORE_TYPE and IGNORE_VALUE
# For pairs: config["ignoredPairs"].append(["loc1::name1", "loc2::name2"])
# For dirs: config["ignoredDirs"].append("path/to/dir")

config_path.write_text(json.dumps(config, indent=2))
print("Configuration saved.")
PYSCRIPT
```
