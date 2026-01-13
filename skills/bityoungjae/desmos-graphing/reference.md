# Desmos Graphing Reference

Complete reference for obsidian-desmos plugin syntax and options.

---

## Settings Reference

### All Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `width` | number | 600 | Graph width in pixels (max: 99999) |
| `height` | number | 400 | Graph height in pixels (max: 99999) |
| `left` | number | -10 | Left x-boundary |
| `right` | number | 10 | Right x-boundary |
| `bottom` | number | -7 | Bottom y-boundary |
| `top` | number | 7 | Top y-boundary |
| `grid` | boolean | true | Show grid lines |
| `degreeMode` | string | radians | `radians` or `degrees` |
| `hideAxisNumbers` | boolean | false | Hide axis number labels |
| `xAxisLabel` | string | - | Custom x-axis label |
| `yAxisLabel` | string | - | Custom y-axis label |
| `xAxisLogarithmic` | boolean | false | Logarithmic x-axis scale |
| `yAxisLogarithmic` | boolean | false | Logarithmic y-axis scale |
| `defaultColor` | color | - | Default color for all equations |

### Settings Syntax

```
key=value; key2=value2    # Semicolon separated
```

or

```
key=value
key2=value2               # Newline separated
```

### Math Expressions in Settings

Bounds accept math expressions evaluated by **mathjs** (NOT LaTeX):

```
left=-2*pi       # ✅ Correct (mathjs syntax)
right=2*pi       # ✅ Correct
top=pi/2         # ✅ Correct
bottom=-pi/2     # ✅ Correct
```

⚠️ **DO NOT use LaTeX in settings:**

```
left=-2*\pi      # ❌ Error: "Syntax error in part '\pi'"
```

**Rule**: Settings use `pi`, equations use `\pi`.

### Boolean Settings

```
grid                # true (no value = true)
grid=true           # true
grid=false          # false
hideAxisNumbers     # true
```

### Auto-Adjustment

If only one boundary is set, the opposite adjusts automatically:
- `left` only → `right = left + 20`
- `right` only → `left = right - 20`
- `top` only → `bottom = top - 14`
- `bottom` only → `top = bottom + 14`

---

## Color Constants

**ONLY these 10 colors are supported by name:**

| Name | Hex Code |
|------|----------|
| `red` | #ff0000 |
| `green` | #00ff00 |
| `blue` | #0000ff |
| `yellow` | #ffff00 |
| `orange` | #ffa500 |
| `purple` | #6042a6 |
| `cyan` | #00ffff |
| `magenta` | #ff00ff |
| `black` | #000000 |
| `white` | #ffffff |

Colors are case-insensitive: `RED`, `Red`, `red` all work.

⚠️ **Common unsupported colors** - use hex instead:

| Color | Use This Hex |
|-------|--------------|
| gray/grey | `#808080` |
| silver | `#c0c0c0` |
| pink | `#ffc0cb` |
| brown | `#a52a2a` |
| navy | `#000080` |

### Hex Colors

```
y=x|#ff6600         # 6-digit hex
y=x|#f60            # 3-digit hex
y=x|#FF6600         # Case insensitive
```

---

## Line Styles

| Style | Description |
|-------|-------------|
| `solid` | Solid line (default) |
| `dashed` | Dashed line |
| `dotted` | Dotted line |

Styles are case-insensitive.

---

## Point Styles

| Style | Description |
|-------|-------------|
| `point` | Filled circle (default) |
| `open` | Open/hollow circle |
| `cross` | X-shaped marker |

---

## Special Tags

| Tag | Effect |
|-----|--------|
| `hidden` | Equation computed but not displayed |
| `noline` | No line drawn (points only visible) |
| `label` | Show equation as label |
| `label:text` | Show custom label text |

### Examples

```
f(x)=x^2|hidden           # Hidden helper function
y=f(x)+1                  # Uses hidden function

(1, 2)|label              # Shows "(1, 2)"
(1, 2)|label:Point A      # Shows "Point A"

y=\sin(x)|noline          # Only points, no connecting line
```

---

## Restriction Syntax

### Basic Restrictions

Restrictions limit where equations are drawn. Add after `|`:

```
y=x^2|x>0                 # x > 0 only
y=x^2|0<x<5               # 0 < x < 5
y=\sin(x)|x>0|y>0         # Multiple restrictions
y=2x|0<=x<=1              # <= and >= supported
```

### Comparison Operators

| Input | Meaning | Converted to |
|-------|---------|--------------|
| `<` | Less than | `\le` |
| `>` | Greater than | `\ge` |
| `<=` | Less than or equal | `\leq` |
| `>=` | Greater than or equal | `\geq` |

### ⚠️ CRITICAL: No LaTeX in Restrictions

Restrictions use **plain math syntax**, NOT LaTeX:

| ✅ Correct | ❌ Incorrect | Error |
|-----------|-------------|-------|
| `x/2<y` | `\frac{x}{2}<y` | Piecewise error |
| `x^(1/2)<2` | `\sqrt{x}<2` | Piecewise error |
| `0<x<1` | `\{0<x<1\}` | Plugin adds braces |
| `x>-1.5708` | `x>-pi/2` | `pi` → p*i error |

**Why errors occur**: The plugin auto-wraps restrictions with `{}` and converts operators. LaTeX backslashes break this process. Also, `pi` is interpreted as `p*i` (two variables).

**Note**: Use numeric values for pi in restrictions (π≈3.1416, π/2≈1.5708).

### Multiple Restrictions

Each restriction is added with a separate `|`:

```
y=x^2|x>0|x<5|y<10        # Three restrictions
```

---

## Equation Types

### Explicit Functions

```
y=x^2
y=\sin(x)
y=e^x
y=\ln(x)
y=\frac{1}{x}
```

### Implicit Equations

```
x^2+y^2=25                # Circle
x^2/9+y^2/4=1             # Ellipse
xy=4                      # Hyperbola
y^2=4x                    # Parabola
```

### Parametric Curves

```
(\cos(t), \sin(t))        # Unit circle
(t, t^2)                  # Parabola
(2\cos(t), \sin(t))       # Ellipse
```

Default parameter range: t ∈ [0, 1]

⚠️ **Tip**: Expand parenthetical expressions to avoid piecewise errors:

```
(2t, 4t(1-t))             # ⚠️ May cause "piecewise" error
(2t, 4t-4t^2)             # ✅ Expanded form is safer
```

### Polar Equations

⚠️ **Must be linear in r** (r to the first power only):

```
r=\theta                  # ✅ Spiral
r=1+\cos(\theta)          # ✅ Cardioid
r=\sin(3\theta)           # ✅ Rose curve
r^2=\cos(2\theta)         # ❌ Error: not linear in r
```

For non-linear polar equations, convert to parametric (see Troubleshooting).

### Points

```
(1, 2)                    # Single point
(\pi, 0)                  # Using constants (LaTeX!)
(\pi/2, 1)                # Must use \pi, not pi
```

⚠️ **Points use LaTeX syntax** - use `\pi`, not `pi`!

### Variables and Sliders

```
a=5                       # Defines variable
b=-2
y=ax+b                    # Uses variables (creates sliders)
```

### Function Definitions

```
f(x)=x^2+1
g(x)=\sin(x)
y=f(x)+g(x)               # Combines functions
```

### Piecewise Functions

⚠️ **Curly braces MUST be escaped** with backslash:

```
y={x<0: -x, x}            # ❌ Error
y=\{x<0: -x, x\}          # ✅ Correct - absolute value
y=\{x<0: \sin(x), x>=0: 2x\}  # ✅ Multiple conditions
```

---

## Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `Too many graph segments` | More than one `---` | Use only one `---` separator |
| `Too many segments` | Setting has multiple `=` | Check setting format |
| `Duplicate key` | Same setting repeated | Remove duplicate |
| `Field must have a value` | Empty required field | Provide a value |
| `Equation label must have a value` | `\|` in label text | Use `∥` (U+2225) instead |
| `Duplicate style identifiers` | Two line/point styles | Use only one style |
| `Duplicate color identifiers` | Two colors on same equation | Use only one color |
| `Duplicate equation labels` | Two labels on same equation | Use only one label |
| `Right boundary must be > left` | left >= right | Adjust boundaries |
| `Top boundary must be > bottom` | bottom >= top | Adjust boundaries |
| `Unrecognised field` | Unknown setting name | Check setting spelling |
| `Graph size outside bounds` | Width/height > 99999 | Reduce size |
| `Polar equations must be linear in r` | Using r², r³, etc. | Convert to parametric |
| `Expected '(' to match ')'` | Bad LaTeX exponent/fraction | Use `^{}`, `\frac{}{}` |

---

## Troubleshooting Guide

### Error: `Syntax error in part "\pi"` (viewport settings)

**Cause**: Using LaTeX `\pi` in settings where mathjs expects `pi`.

**Wrong**:
```
left=-2*\pi; right=2*\pi
```

**Correct**:
```
left=-2*pi; right=2*pi
```

**Rule**: Settings use mathjs syntax (`pi`), equations use LaTeX (`\pi`).

---

### Error: `Too many variables. Try defining 'p' or 'i'`

**Cause**: Using plain `pi` in equations or **point coordinates** where LaTeX `\pi` is required.

Desmos interprets `pi` as two separate variables: `p` and `i`.

**Common mistakes**:

1. **In equations**:
   ```
   y=\sin(x+pi/4)         # ❌ Wrong
   y=\sin(x+\pi/4)        # ✅ Correct
   ```

2. **In point coordinates** (often overlooked!):
   ```
   (pi/2, 0)|label:A      # ❌ Wrong
   (\pi/2, 0)|label:A     # ✅ Correct

   (pi, -1)               # ❌ Wrong
   (\pi, -1)              # ✅ Correct
   ```

**Rule**: Everything below `---` uses Desmos/LaTeX syntax, including points.

---

### Error: `Too many variables. Try defining 's', 'q', 'r' or 't'`

**Cause**: Using `sqrt()` instead of `\sqrt{}` in equations, or using `\sqrt{}` in restrictions.

Desmos interprets `sqrt` as four separate variables: `s`, `q`, `r`, `t`.

**Common mistakes**:

1. **In equations** (use LaTeX `\sqrt{}`):
   ```
   y=x/sqrt(3)            # ❌ Wrong
   y=x/\sqrt{3}           # ✅ Correct
   ```

2. **In restrictions** (use `^0.5` instead):
   ```
   y=x|0<=x<=sqrt(3)      # ❌ Wrong (sqrt not recognized)
   y=x|0<=x<=\sqrt{3}     # ❌ Wrong (no LaTeX in restrictions)
   y=x|0<=x<=3^0.5        # ✅ Correct
   ```

**Rule**: Equations use `\sqrt{x}`, restrictions use `x^0.5` or `x^(1/2)`.

---

### Error: `Equation label must have a value`

**Cause**: Pipe character (`|`) in label text splits it incorrectly.

The parser uses `|` as segment delimiter. If your label contains `|`, it gets split:

```
(1, 0)|label:|v|=5
```

Parsed as:
- Segment 1: `label:` (empty value → error)
- Segment 2: `v`
- Segment 3: `=5`

**Solution**: Use Unicode double vertical line `∥` (U+2225):

```
(1, 0)|label:|v|=5         # ❌ Error
(1, 0)|label:∥v∥=5         # ✅ Correct

(4, 3)|label:v=(4,3), |v|=5   # ❌ Error
(4, 3)|label:v=(4,3), ∥v∥=5   # ✅ Correct
```

**For absolute value in equations**:

```
y=|x|                      # ❌ Error: pipe splits equation
y=abs(x)                   # ✅ Use abs() function
```

---

### Error: `Polar equations must be linear in r`

**Cause**: Using `r²`, `r³`, etc. in polar equations.

Desmos only supports polar equations where r appears linearly (to the first power):

| ✅ Supported | ❌ Not Supported |
|-------------|-----------------|
| `r=2` | `r^2=cos(2θ)` |
| `r=1+cos(θ)` | `r^3=sin(θ)` |
| `r=θ` | `r^2=a^2*cos(2θ)` |

**Solution**: Convert to parametric curve.

Example - Lemniscate ($r^2 = \cos(2\theta)$):

```
r^2=\cos(2\theta)          # ❌ Error

# Convert using x = r*cos(θ), y = r*sin(θ), r = √cos(2θ)
(\cos(t)\sqrt{\cos(2t)}, \sin(t)\sqrt{\cos(2t)})|blue  # ✅
```

> **Note**: `sqrt` of negative values is automatically skipped by Desmos.

---

### Error: `Expected '(' to match ')'`

**Cause**: Improper LaTeX syntax for exponents or complex expressions.

**Common issues**:

1. **Exponents with parentheses** - use braces instead:
   ```
   y=2^(-10*x)              # ⚠️ May cause issues
   y=2^{-10x}               # ✅ Proper LaTeX
   ```

2. **Multiplication with Greek letters**:
   ```
   y=2*\pi*x                # ⚠️ May cause issues
   y=2\pi x                 # ✅ Implicit multiplication
   ```

3. **Complex fractions**:
   ```
   y=(x-0.5)*2*\pi/0.3      # ⚠️ Ambiguous
   y=\frac{(x-0.5)\cdot 2\pi}{0.3}  # ✅ Clear structure
   ```

**LaTeX best practices**:

| Situation | Avoid | Prefer |
|-----------|-------|--------|
| Exponents | `2^(-10*x)` | `2^{-10x}` |
| Multiplication | `*\pi` | `\cdot\pi` or just `\pi` |
| Fractions | `a/b/c` | `\frac{a}{bc}` |
| Large brackets | `(\frac{a}{b})` | `\left(\frac{a}{b}\right)` |

---

### Error: `A piecewise expression must have at least one condition`

**Possible causes**:

1. **Unsupported color name**: Colors like `gray`, `grey`, `silver` are not recognized and get parsed as restrictions.

   **Wrong**:
   ```
   y=x|gray|dashed
   ```

   **Correct**:
   ```
   y=x|#808080|dashed
   ```

2. **LaTeX in restrictions**: Backslash commands in restriction segments.

   **Wrong**:
   ```
   y=x|\frac{x}{2}<1
   ```

   **Correct**:
   ```
   y=x|x/2<1
   ```

3. **Parenthetical expressions in parametric**: `(1-t)` may be misinterpreted.

   **Wrong** (sometimes):
   ```
   (2t, 4t(1-t))
   ```

   **Correct**:
   ```
   (2t, 4t-4t^2)
   ```

---

### Color Not Applied

**Symptom**: Color is ignored, graph uses default color.

**Cause**: Color name misspelled or not in supported list.

**Supported colors** (case-insensitive):
```
red, green, blue, yellow, orange, purple, cyan, magenta, black, white
```

**NOT supported**: `gray`, `grey`, `silver`, `pink`, `brown`, `navy`, etc.

**Solution**: Use hex codes for unsupported colors:
```
y=x|#808080     # gray
y=x|#ffc0cb     # pink
y=x|#a52a2a     # brown
```

---

### Restriction Not Working

**Symptom**: Entire curve is drawn despite restrictions.

**Check these issues**:

1. **LaTeX syntax used**: Don't use `\sqrt`, `\frac`, etc.
   ```
   y=x|\sqrt{x}<2     # ❌ Wrong
   y=x|x^(1/2)<2      # ✅ Correct
   ```

2. **Curly braces included**: Plugin adds them automatically.
   ```
   y=x|\{0<x<1\}      # ❌ Wrong
   y=x|0<x<1          # ✅ Correct
   ```

3. **Comparison operator issues**: Use `<`, `>`, `<=`, `>=`.
   ```
   y=x|x≤1            # ❌ Wrong (Unicode)
   y=x|x<=1           # ✅ Correct
   ```

---

### Settings vs Equations Quick Reference

**The plugin uses TWO different parsers:**

| Feature | Settings (above ---) | Equations & Points (below ---) | Restrictions |
|---------|---------------------|-------------------------------|--------------|
| Parser | **mathjs** | **Desmos API (LaTeX)** | **plain math** |
| Pi | `pi` | `\pi` | numeric (3.1416) |
| Tau | `tau` | `\tau` | numeric (6.2832) |
| Math | `2*pi`, `pi/2` | `\frac{\pi}{2}` | `x/2`, `x^2` |
| Example | `left=-2*pi+0.5` | `y=\sin(x+\pi)` | `x>-1.5708` |
| **Points** | N/A | `(\pi/2, 0)` ← LaTeX required! | N/A |

⚠️ **Point coordinates are parsed by Desmos, NOT mathjs!**
⚠️ **Restrictions: use numeric values, NOT `pi` or `\pi`!**

```
(pi/2, 0)      # ❌ Error: "Too many variables"
(\pi/2, 0)     # ✅ Correct
```

---

## Full Examples

### Trigonometric Functions

````markdown
```desmos-graph
left=-2*pi; right=2*pi
bottom=-2; top=2
degreeMode=radians
---
y=\sin(x)|red
y=\cos(x)|blue|dashed
y=\tan(x)|orange|x>-1.5708|x<1.5708
```
````

### Circle with Points

````markdown
```desmos-graph
left=-6; right=6
bottom=-6; top=6
---
x^2+y^2=25|blue
(3, 4)|red|label:P
(0, 0)|black|label:O
```
````

### Parametric with Sliders

````markdown
```desmos-graph
a=2
b=3
(a\cos(t), b\sin(t))
```
````

### Piecewise Function

````markdown
```desmos-graph
y=\{x<0: x^2, x>=0: \sqrt{x}\}|purple
(0, 0)|open|label:Junction
```
````
