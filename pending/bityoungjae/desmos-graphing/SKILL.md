---
name: desmos-graphing
description: Create interactive Desmos graphs in Obsidian using desmos-graph code blocks. Use when visualizing functions, parametric curves, inequalities, or mathematical relationships with customizable styling and settings.
---

# Desmos Graphing in Obsidian

## ⚠️ CRITICAL: Dual Parser System

The plugin uses **different parsers** for different parts:

| Location | Parser | pi | sqrt | Example |
|----------|--------|-----|------|---------|
| Settings | mathjs | `pi` | - | `left=-2*pi+0.5` |
| Equations | Desmos (LaTeX) | `\pi` | `\sqrt{x}` | `y=\sqrt{x}+\pi` |
| Points | Desmos (LaTeX) | `\pi` | `\sqrt{x}` | `(\pi/2, 1)` |
| **Restrictions** | plain math | numeric | `x^0.5` | `x>-1.5708` |

```markdown
✅ CORRECT
left=-0.5; right=2*pi+0.5
---
y=\sqrt{x}|blue
y=x/\sqrt{3}|green|0<=x<=3^0.5
(\pi/2, 0)|label:cos(90°)=0

❌ WRONG (will error)
left=-2*\pi               # Error: "Syntax error in part '\pi'"
y=\sin(x+pi/4)            # Error: "Too many variables" (p*i)
(pi/2, 0)                 # Error: "Too many variables" ← Points need LaTeX!
y=x/sqrt(3)|0<=x<=sqrt(3) # Error: "Too many variables" (s*q*r*t)
```

**Key rule**: `\sqrt{x}` in equations, `x^0.5` in restrictions!

## Code Block Format

````markdown
```desmos-graph
[settings]
---
[equations]
```
````

- Settings (optional) above `---`, equations below
- Each equation on its own line
- Use `|` to add styling/restrictions to equations

## Quick Start

### Basic Function

````markdown
```desmos-graph
y=x^2
y=\sin(x)|blue
```
````

### With Settings

````markdown
```desmos-graph
left=-2*pi; right=2*pi
bottom=-2; top=2
---
y=\sin(x)|red
y=\cos(x)|blue|dashed
```
````

### Points and Labels

````markdown
```desmos-graph
(0, 0)|label:Origin
(3, 4)|red|label:Point A
(\pi/2, 1)|blue|label:π/2    # Use \pi in coordinates!
y=x|dashed
```
````

⚠️ Points use LaTeX: `(\pi/2, 0)` not `(pi/2, 0)`

## Essential Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `width` | 600 | Graph width in pixels |
| `height` | 400 | Graph height in pixels |
| `left` | -10 | Left boundary |
| `right` | 10 | Right boundary |
| `bottom` | -7 | Bottom boundary |
| `top` | 7 | Top boundary |
| `grid` | true | Show grid lines |
| `degreeMode` | radians | `radians` or `degrees` |

### Additional Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `hideAxisNumbers` | false | Hide axis number labels |
| `xAxisLabel` | - | Custom x-axis label |
| `yAxisLabel` | - | Custom y-axis label |
| `xAxisLogarithmic` | false | Logarithmic x-axis scale |
| `yAxisLogarithmic` | false | Logarithmic y-axis scale |
| `defaultColor` | - | Default color for all equations |

Settings use `=` for values, separated by `;` or newlines.
Bounds accept math expressions: `left=-2*pi`

## Equation Styling

Use `|` (pipe) to add styling after an equation:

```
equation|color|style|restrictions|label
```

Segment order is flexible - the parser auto-detects each segment type.

⚠️ **CRITICAL: `|` is RESERVED as delimiter!**

The pipe character cannot appear in equations or labels:

```
(1, 0)|label:|v|=5         # ❌ Error: label parsed as empty
(1, 0)|label:∥v∥=5         # ✅ Use Unicode ∥ (U+2225)
y=|x|                      # ❌ Error: pipes split the equation
y=abs(x)                   # ✅ Use abs() function
```

### Colors

**Supported names:** `red`, `green`, `blue`, `yellow`, `orange`, `purple`, `cyan`, `magenta`, `black`, `white`

**Hex codes:** `#rrggbb` or `#rgb` (e.g., `#ff6600`, `#f60`)

⚠️ **`gray`/`grey` are NOT supported!** Use hex instead:
- Light gray: `#c0c0c0`
- Medium gray: `#808080`
- Dark gray: `#404040`

```
y=x|gray           # ❌ Error: parsed as restriction
y=x|#808080        # ✅ Correct
```

### Line & Point Styles

| Line | Point | Effect |
|------|-------|--------|
| `solid` | `point` | Default (solid/filled) |
| `dashed` | `open` | Dashed/open circle |
| `dotted` | `cross` | Dotted/X mark |

### Labels

`(1, 2)|label` shows "(1, 2)", `(1, 2)|label:Point A` shows custom text

### Restrictions

Limit where equations are drawn:

```
y=x^2|0<x<5           # Only draw for 0 < x < 5
y=\sin(x)|x>0|y>0     # Multiple restrictions
y=2x|0<=x<=1          # <= and >= supported
y=\tan(x)|x>-1.5708|x<1.5708   # Use numeric values (π/2≈1.5708)
```

**⚠️ CRITICAL: Use plain math, NOT LaTeX in restrictions!**

| ✅ Correct | ❌ Wrong | Why |
|-----------|---------|-----|
| `x/2<y` | `\frac{x}{2}<y` | No LaTeX commands |
| `x^0.5<2` | `\sqrt{x}<2` | Use `^0.5` not `\sqrt` |
| `0<x<3^0.5` | `0<x<sqrt(3)` | `sqrt()` → s*q*r*t |
| `x>-1.5708` | `x>-pi/2` | `pi` → p*i, use numeric |
| `0<x<1` | `\{0<x<1\}` | No braces needed |

The plugin auto-wraps restrictions with `{}` - don't add them yourself.

### Hidden & Special Tags

```
f(x)=x^2|hidden       # Define but don't display
y=f(x)+1              # Use the hidden function
y=\sin(x)|noline      # Points only, no connecting line
```

## Combining Styles

Order doesn't matter:

```
y=x^2|red|dashed|0<x<5
(1, 2)|open|blue|label:Start
```

## Equation Types

| Type | Example |
|------|---------|
| Explicit | `y=x^2` |
| Implicit | `x^2+y^2=25` |
| Parametric | `(\cos(t), \sin(t))` |
| Polar | `r=1+\cos(\theta)` |
| Piecewise | `y=\{x<0: -x, x\}` |
| Point | `(3, 4)` |
| Function def | `f(x)=x^2` |

### ⚠️ Polar Equations Must Be Linear in r

Desmos only supports polar equations where r appears linearly:

```
r=1+\cos(\theta)       # ✅ Linear in r
r^2=\cos(2\theta)      # ❌ Error: "must be linear in r"
```

**Solution**: Convert to parametric curve:

```
# Lemniscate (r² = cos(2θ)) → parametric form
(\cos(t)\sqrt{\cos(2t)}, \sin(t)\sqrt{\cos(2t)})|blue
```

### Parametric Curves Warning

⚠️ Expand parenthetical expressions to avoid parsing errors:

```
(2t, 4t(1-t))|blue     # ⚠️ May be misinterpreted as piecewise
(2t, 4t-4t^2)|blue     # ✅ Expanded form is safer
```

### Piecewise Functions

⚠️ **Escape curly braces** with backslash:

```
y={x<0: -x, x}         # ❌ Error
y=\{x<0: -x, x\}       # ✅ Correct
```

## Complete Examples

### Trigonometric Phase Shifts

````markdown
```desmos-graph
left=-2*pi; right=2*pi
bottom=-2; top=2
---
y=\sin(x)|blue
y=\sin(x+\pi/4)|red
y=\sin(x+\pi/2)|green
y=\sin(x+\pi)|purple|dashed
```
````

### Bezier Curve with Control Points

````markdown
```desmos-graph
left=-0.5; right=2.5
bottom=-0.5; top=2.5
---
(2t, 4t-4t^2)|blue
(0, 0)|black|label:P0
(1, 2)|black|label:P1
(2, 0)|black|label:P2
y=2x|#808080|dashed|0<x<1
y=-2x+4|#808080|dashed|1<x<2
```
````

### Easing Functions

````markdown
```desmos-graph
left=-0.2; right=1.2
bottom=-0.2; top=1.2
---
y=x|dashed|black
y=1-\cos(\pi*x/2)|blue|0<=x<=1
y=\sin(\pi*x/2)|red|0<=x<=1
```
````

### Cosine with Special Points

````markdown
```desmos-graph
left=-0.5; right=2*pi+0.5
bottom=-1.5; top=1.5
---
y=\cos(x)|blue
(0, 1)|red|label:cos(0)=1
(\pi/2, 0)|red|label:cos(π/2)=0
(\pi, -1)|red|label:cos(π)=-1
(3*\pi/2, 0)|red|label:cos(3π/2)=0
```
````

⚠️ Note: Settings use `2*pi`, points use `\pi`, `3*\pi/2`, etc.

## Advanced

For complete documentation, see [reference.md](reference.md):
- All 13 settings with defaults and auto-adjustment rules
- Hex codes for unsupported colors (gray, pink, brown, etc.)
- 13 error messages with causes and fixes
- Detailed troubleshooting for common issues
- Polar-to-parametric conversion examples
