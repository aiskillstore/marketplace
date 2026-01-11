---
name: tikzjax-diagramming
description: Create TikZ diagrams in Obsidian using TikZJax plugin. Use when visualizing geometric shapes, coordinate systems, game scenes, circuit diagrams, chemical structures, or complex technical drawings that require precise positioning.
---

# TikZJax Diagramming for Obsidian

TikZJax enables LaTeX/TikZ diagrams in Obsidian. Use for complex technical drawings where Mermaid lacks precision:
- Geometric shapes and coordinate systems
- Game scenes with precise positioning
- Circuit diagrams (circuitikz)
- Chemical structures (chemfig)
- 3D plots (tikz-3dplot, pgfplots)
- Commutative diagrams (tikz-cd)

## Basic Syntax

```tikz
\begin{document}
\begin{tikzpicture}[scale=1]
  \draw[thick] (0,0) rectangle (4,2);
  \fill[cyan] (1,0.5) rectangle (3,1.5);
\end{tikzpicture}
\end{document}
```

**Required Structure:**
- Code block language: `tikz`
- Must include `\begin{document}` and `\end{document}`
- Drawing code inside `\begin{tikzpicture}...\end{tikzpicture}`
- Recommended: `scale=1` (smaller values reduce text readability)

## Supported Packages

Load with `\usepackage{}`:

| Package | Purpose |
|---------|---------|
| tikz | Core drawing (implicit) |
| tikz-cd | Commutative diagrams |
| circuitikz | Electronic circuits |
| pgfplots | Data visualization, plots |
| chemfig | Chemical structures |
| tikz-3dplot | 3D coordinate systems |
| array | Table environments |
| amsmath | Math typesetting |
| amsfonts | Mathematical fonts |
| amssymb | Mathematical symbols |

## TikZ Libraries

Load with `\usetikzlibrary{}`:

```latex
\usepackage{tikz}
\usetikzlibrary{decorations.pathreplacing}
\usetikzlibrary{arrows.meta}
\usetikzlibrary{calc}
\begin{document}
  % Drawing commands here
\end{document}
```

## Dark Mode Behavior

TikZJax plugin can automatically invert `black` ↔ `white` in dark mode (configurable in plugin settings).

### Text Color

Omit color specification in `\node` for automatic theme adaptation:

```latex
% Explicit color - fixed, won't adapt
\node[black] at (2,0) {Label};

% No color - adapts automatically (recommended)
\node at (2,0) {Label};
```

### Black/White Inversion

When dark mode inversion is enabled:
- `black` becomes `white` (and vice versa)
- Other named colors remain unchanged
- `\definecolor{}` custom colors are NOT inverted

## Unsupported Features

| Feature | Status | Alternative |
|---------|--------|-------------|
| Color mixing (`blue!30`, `cyan!20!white`) | Not supported | Use base colors only |
| Korean text | Not supported | Use English |
| `\definecolor{}{RGB}{}` | Not inverted in dark mode | Use named colors if inversion needed |
| `\definecolor{}{HTML}{}` | Not inverted in dark mode | Use named colors if inversion needed |

## Quick Start Examples

### Simple Rectangle with Fill

```tikz
\begin{document}
\begin{tikzpicture}[scale=1]
  \draw[thick, gray] (0,0) rectangle (4,3);
  \fill[cyan, opacity=0.3] (0.5,0.5) rectangle (3.5,2.5);
  \node at (2,1.5) {Content Area};
\end{tikzpicture}
\end{document}
```

### Coordinate System

```tikz
\begin{document}
\begin{tikzpicture}[scale=1]
  % Axes
  \draw[thick, gray, ->] (-0.5,0) -- (4,0) node[right] {$x$};
  \draw[thick, gray, ->] (0,-0.5) -- (0,3) node[above] {$y$};

  % Point
  \fill[red] (2,1.5) circle (3pt) node[above right] {$P(2,1.5)$};

  % Dashed guides
  \draw[dashed, yellow] (2,0) -- (2,1.5);
  \draw[dashed, yellow] (0,1.5) -- (2,1.5);
\end{tikzpicture}
\end{document}
```

### Circuit Diagram

```tikz
\usepackage{circuitikz}
\begin{document}
\begin{circuitikz}[scale=1]
  \draw (0,0) to[R, l=$R_1$] (2,0)
              to[C, l=$C_1$] (4,0)
              to[short] (4,-2)
              to[battery1, l=$V$] (0,-2)
              to[short] (0,0);
\end{circuitikz}
\end{document}
```

### Chemical Structure

```tikz
\usepackage{chemfig}
\begin{document}
\chemfig{H-C(-[2]H)(-[6]H)-C(-[2]H)(-[6]H)-H}
\end{document}
```

### Commutative Diagram

```tikz
\usepackage{tikz-cd}
\begin{document}
\begin{tikzcd}
  A \arrow[r, "f"] \arrow[d, "g"'] & B \arrow[d, "h"] \\
  C \arrow[r, "k"'] & D
\end{tikzcd}
\end{document}
```

### 3D Plot

```tikz
\usepackage{pgfplots}
\begin{document}
\begin{tikzpicture}
\begin{axis}[
  view={60}{30},
  colormap/cool
]
\addplot3[
  surf,
  domain=-2:2,
  domain y=-2:2
] {exp(-x^2-y^2)};
\end{axis}
\end{tikzpicture}
\end{document}
```

## When to Use TikZJax vs Other Tools

| Use Case | Tool |
|----------|------|
| Flowcharts, sequences, ER diagrams | Mermaid |
| Mathematical functions, interactive graphs | Desmos |
| Inline math, equations | MathJax |
| Precise geometry, coordinate systems | **TikZJax** |
| Game scenes, sprites, positioning | **TikZJax** |
| Circuit diagrams | **TikZJax** |
| Chemical structures | **TikZJax** |
| 3D visualizations | **TikZJax** |

## Reference

For complete syntax reference, color tables, and advanced examples, see [reference.md](reference.md).
