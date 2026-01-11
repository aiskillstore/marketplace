# Agent Color Palette Reference

This reference provides color recommendations for Claude Code agents organized by domain and plugin.

## Color Format

All colors must be:
- 6-digit hexadecimal format
- Prefixed with `#`
- Quoted in YAML: `color: "#3498DB"`

## Domain Color Palettes

### Meta/Building (Purple Family)
For meta-programming, agent builders, and tools that create other tools.

| Color | Hex | Use For |
|-------|-----|---------|
| ![#9B59B6](https://placehold.co/20x20/9B59B6/9B59B6.png) Primary | `#9B59B6` | Main orchestrators, primary architects |
| ![#8E44AD](https://placehold.co/20x20/8E44AD/8E44AD.png) Dark | `#8E44AD` | Specialized builders |
| ![#7D3C98](https://placehold.co/20x20/7D3C98/7D3C98.png) Darker | `#7D3C98` | Secondary builders |
| ![#6C3483](https://placehold.co/20x20/6C3483/6C3483.png) Deep | `#6C3483` | Tertiary builders |
| ![#5B2C6F](https://placehold.co/20x20/5B2C6F/5B2C6F.png) Deepest | `#5B2C6F` | Supporting builders |

**Example (agent-builder plugin)**:
```yaml
meta-architect:    "#9B59B6"  # Orchestrator
agent-builder:     "#8E44AD"
skill-builder:     "#7D3C98"
hook-builder:      "#6C3483"
command-builder:   "#5B2C6F"
```

### GitHub/Git (Blue Family)
For version control, GitHub workflows, and collaboration tools.

| Color | Hex | Use For |
|-------|-----|---------|
| ![#3498DB](https://placehold.co/20x20/3498DB/3498DB.png) Primary | `#3498DB` | Main workflow orchestrators |
| ![#2980B9](https://placehold.co/20x20/2980B9/2980B9.png) Dark | `#2980B9` | Issue management |
| ![#1F618D](https://placehold.co/20x20/1F618D/1F618D.png) Darker | `#1F618D` | PR management |
| ![#1A5276](https://placehold.co/20x20/1A5276/1A5276.png) Deep | `#1A5276` | Release management |
| ![#154360](https://placehold.co/20x20/154360/154360.png) Deepest | `#154360` | Supporting agents |

**Example (github-workflows plugin)**:
```yaml
workflow-orchestrator: "#3498DB"  # Orchestrator
issue-manager:         "#2980B9"
pr-reviewer:           "#1F618D"
release-manager:       "#1A5276"
```

### Testing/QA (Red Family)
For test execution, quality assurance, and validation tools.

| Color | Hex | Use For |
|-------|-----|---------|
| ![#E74C3C](https://placehold.co/20x20/E74C3C/E74C3C.png) Primary | `#E74C3C` | Main test orchestrators |
| ![#C0392B](https://placehold.co/20x20/C0392B/C0392B.png) Dark | `#C0392B` | Unit test runners |
| ![#A93226](https://placehold.co/20x20/A93226/A93226.png) Darker | `#A93226` | Integration test runners |
| ![#922B21](https://placehold.co/20x20/922B21/922B21.png) Deep | `#922B21` | E2E test runners |
| ![#7B241C](https://placehold.co/20x20/7B241C/7B241C.png) Deepest | `#7B241C` | Coverage analyzers |

**Example (testing-expert plugin)**:
```yaml
test-reviewer:     "#E74C3C"  # Main reviewer
jest-runner:       "#C0392B"
playwright-runner: "#A93226"
coverage-analyzer: "#922B21"
```

### Documentation (Green Family)
For documentation generation, README creation, and guides.

| Color | Hex | Use For |
|-------|-----|---------|
| ![#27AE60](https://placehold.co/20x20/27AE60/27AE60.png) Primary | `#27AE60` | Main doc generators |
| ![#229954](https://placehold.co/20x20/229954/229954.png) Dark | `#229954` | API documentation |
| ![#1E8449](https://placehold.co/20x20/1E8449/1E8449.png) Darker | `#1E8449` | User guides |
| ![#196F3D](https://placehold.co/20x20/196F3D/196F3D.png) Deep | `#196F3D` | Technical specs |
| ![#145A32](https://placehold.co/20x20/145A32/145A32.png) Deepest | `#145A32` | Changelog generators |

### Security (Orange/Gold Family)
For security analysis, vulnerability scanning, and compliance tools.

| Color | Hex | Use For |
|-------|-----|---------|
| ![#F39C12](https://placehold.co/20x20/F39C12/F39C12.png) Primary | `#F39C12` | Main security auditors |
| ![#D68910](https://placehold.co/20x20/D68910/D68910.png) Dark | `#D68910` | Vulnerability scanners |
| ![#B9770E](https://placehold.co/20x20/B9770E/B9770E.png) Darker | `#B9770E` | Compliance checkers |
| ![#9C640C](https://placehold.co/20x20/9C640C/9C640C.png) Deep | `#9C640C` | Secret detectors |
| ![#7E5109](https://placehold.co/20x20/7E5109/7E5109.png) Deepest | `#7E5109` | Policy enforcers |

### Performance (Teal Family)
For optimization, profiling, and performance analysis tools.

| Color | Hex | Use For |
|-------|-----|---------|
| ![#1ABC9C](https://placehold.co/20x20/1ABC9C/1ABC9C.png) Primary | `#1ABC9C` | Main optimizers |
| ![#16A085](https://placehold.co/20x20/16A085/16A085.png) Dark | `#16A085` | Profilers |
| ![#138D75](https://placehold.co/20x20/138D75/138D75.png) Darker | `#138D75` | Memory analyzers |
| ![#117A65](https://placehold.co/20x20/117A65/117A65.png) Deep | `#117A65` | Load testers |
| ![#0E6655](https://placehold.co/20x20/0E6655/0E6655.png) Deepest | `#0E6655` | Bundle analyzers |

### Research/Exploration (Purple-Blue Family)
For research agents, codebase exploration, and investigation tools.

| Color | Hex | Use For |
|-------|-----|---------|
| ![#8E44AD](https://placehold.co/20x20/8E44AD/8E44AD.png) Primary | `#8E44AD` | Main investigators |
| ![#7D3C98](https://placehold.co/20x20/7D3C98/7D3C98.png) Dark | `#7D3C98` | Pattern analyzers |
| ![#6C3483](https://placehold.co/20x20/6C3483/6C3483.png) Darker | `#6C3483` | Best practice researchers |
| ![#5B2C6F](https://placehold.co/20x20/5B2C6F/5B2C6F.png) Deep | `#5B2C6F` | Comparison analyzers |
| ![#4A235A](https://placehold.co/20x20/4A235A/4A235A.png) Deepest | `#4A235A` | Deep dive investigators |

### Self-Improvement (Magenta Family)
For self-critique, quality analysis, and feedback tools.

| Color | Hex | Use For |
|-------|-----|---------|
| ![#E91E63](https://placehold.co/20x20/E91E63/E91E63.png) Primary | `#E91E63` | Main critics |
| ![#C2185B](https://placehold.co/20x20/C2185B/C2185B.png) Dark | `#C2185B` | Quality analyzers |
| ![#AD1457](https://placehold.co/20x20/AD1457/AD1457.png) Darker | `#AD1457` | Improvement suggesters |
| ![#880E4F](https://placehold.co/20x20/880E4F/880E4F.png) Deep | `#880E4F` | Pattern trackers |
| ![#6D0A3C](https://placehold.co/20x20/6D0A3C/6D0A3C.png) Deepest | `#6D0A3C` | Feedback analyzers |

## Color Selection Best Practices

### 1. Plugin Consistency
Use related shades from the same color family for agents in the same plugin.

```yaml
# Good - consistent blue family for github-workflows
workflow-orchestrator: "#3498DB"
issue-manager:         "#2980B9"
pr-reviewer:           "#1F618D"

# Bad - random unrelated colors
workflow-orchestrator: "#3498DB"  # Blue
issue-manager:         "#E74C3C"  # Red
pr-reviewer:           "#27AE60"  # Green
```

### 2. Hierarchy Through Shade
Use lighter shades for primary/orchestrator agents and progressively darker shades for specialized agents.

### 3. Domain Matching
Choose colors that intuitively match the agent's purpose:
- Red for testing/errors (warning connotation)
- Green for documentation/success
- Blue for workflows/processes
- Orange for security/caution
- Purple for meta/building

### 4. Terminal Visibility
Avoid colors that are:
- Too light (invisible on white backgrounds): `#FFFFFF`, `#F5F5F5`
- Too dark (invisible on dark backgrounds): `#000000`, `#1A1A1A`
- Too saturated (eye strain): Pure `#FF0000`, `#00FF00`

### 5. Accessibility
Consider users with color blindness:
- Don't rely solely on color to convey information
- Use sufficient contrast
- Avoid red-green combinations for critical distinctions

## Quick Reference

| Domain | Primary Color | Hex |
|--------|--------------|-----|
| Meta/Building | Purple | `#9B59B6` |
| GitHub/Git | Blue | `#3498DB` |
| Testing/QA | Red | `#E74C3C` |
| Documentation | Green | `#27AE60` |
| Security | Orange | `#F39C12` |
| Performance | Teal | `#1ABC9C` |
| Research | Purple-Blue | `#8E44AD` |
| Self-Improvement | Magenta | `#E91E63` |
