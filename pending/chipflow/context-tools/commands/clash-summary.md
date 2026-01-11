# Clash Summary

Show a summary of potential naming clashes detected in the codebase with analysis.

```bash
python3 << 'PYSCRIPT'
import re
import json
from pathlib import Path

repo_map = Path(".claude/repo-map.md")
if not repo_map.exists():
    print("No repo map found. Run /repo-map first.")
    exit(0)

content = repo_map.read_text()

# Parse similar classes (multi-line format)
# Format: - **Name1** (file1.py)\n  ↔ **Name2** (file2.py)\n  Reason: ...
similar_classes = []
class_pattern = re.compile(
    r'- \*\*([^*]+)\*\* \(([^)]+)\)\n\s+↔ \*\*([^*]+)\*\* \(([^)]+)\)\n\s+Reason: ([^\n]+)',
    re.MULTILINE
)
class_section = re.search(r'## ⚠️ Potentially Similar Classes.*?(?=\n## |\Z)', content, re.DOTALL)
if class_section:
    for match in class_pattern.finditer(class_section.group(0)):
        similar_classes.append({
            'name1': match.group(1), 'loc1': match.group(2),
            'name2': match.group(3), 'loc2': match.group(4),
            'reason': match.group(5)
        })

# Parse similar functions (multi-line format)
similar_functions = []
func_section = re.search(r'## ⚠️ Potentially Similar Functions.*?(?=\n## |\Z)', content, re.DOTALL)
if func_section:
    for match in class_pattern.finditer(func_section.group(0)):
        similar_functions.append({
            'name1': match.group(1), 'loc1': match.group(2),
            'name2': match.group(3), 'loc2': match.group(4),
            'reason': match.group(5)
        })

total = len(similar_classes) + len(similar_functions)
if total == 0:
    print("No naming clashes detected in this codebase.")
    exit(0)

print(f"{total} potential naming clash(es) detected\n")

# Output detailed clash info for Claude to analyze
if similar_classes:
    print(f"=== Similar Classes ({len(similar_classes)}) ===\n")
    for c in similar_classes:
        print(f"  {c['name1']} ({c['loc1']})")
        print(f"    <-> {c['name2']} ({c['loc2']})")
        print(f"    Reason: {c['reason']}")
        print()

if similar_functions:
    print(f"=== Similar Functions ({len(similar_functions)}) ===\n")
    for f in similar_functions:
        print(f"  {f['name1']} ({f['loc1']})")
        print(f"    <-> {f['name2']} ({f['loc2']})")
        print(f"    Reason: {f['reason']}")
        print()

print("---")
print("Run /resolve-clashes to review and resolve interactively.")
PYSCRIPT
```

After running this command:
1. Review the clashes listed above
2. Analyze each clash to determine if it's:
   - **Intentional**: Different purposes (e.g., Setup vs Result, strategy patterns, test utilities)
   - **Candidate for consolidation**: True duplicates that could be merged
   - **Naming issue**: Similar names that could be made more distinct
3. Suggest specific resolutions for clashes that appear problematic
4. Use `/resolve-clashes` to interactively resolve them
