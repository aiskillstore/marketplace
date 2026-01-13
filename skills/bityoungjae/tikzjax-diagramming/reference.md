# TikZJax Complete Reference

## Document Structure

```latex
\usepackage{tikz}                    % Optional: explicitly load tikz
\usetikzlibrary{arrows.meta,calc}    % Optional: load libraries
\begin{document}
\begin{tikzpicture}[options]
  % Drawing commands
\end{tikzpicture}
\end{document}
```

## TikZPicture Options

| Option | Example | Description |
|--------|---------|-------------|
| `scale` | `scale=1` | Global scaling (1 recommended) |
| `xscale`, `yscale` | `xscale=2` | Axis-specific scaling |
| `rotate` | `rotate=45` | Rotation in degrees |
| `shift` | `shift={(2,1)}` | Translation |
| `baseline` | `baseline=(current bounding box.center)` | Vertical alignment |

## Basic Drawing Commands

### Lines and Paths

```latex
\draw (0,0) -- (2,0);                    % Line segment
\draw (0,0) -- (2,0) -- (2,2) -- cycle;  % Closed path
\draw[->] (0,0) -- (2,0);                % Arrow
\draw[<->] (0,0) -- (2,0);               % Double arrow
\draw[dashed] (0,0) -- (2,0);            % Dashed line
\draw[dotted] (0,0) -- (2,0);            % Dotted line
\draw[thick] (0,0) -- (2,0);             % Thick line
\draw[very thick] (0,0) -- (2,0);        % Very thick line
\draw[line width=2pt] (0,0) -- (2,0);    % Custom width
```

### Shapes

```latex
\draw (0,0) rectangle (2,1);             % Rectangle
\draw (0,0) circle (1);                  % Circle (radius)
\draw (0,0) ellipse (2 and 1);           % Ellipse (x-radius and y-radius)
\draw (0,0) arc (0:90:1);                % Arc (start:end:radius)
\draw[rounded corners=5pt] (0,0) rectangle (2,1);  % Rounded rectangle
```

### Fill and Stroke

```latex
\fill[cyan] (0,0) rectangle (2,1);       % Filled shape
\filldraw[fill=cyan, draw=gray] (0,0) rectangle (2,1);  % Fill + stroke
\fill[cyan, opacity=0.5] (0,0) circle (1);  % Semi-transparent
\shade[left color=cyan, right color=white] (0,0) rectangle (2,1);  % Gradient
```

### Points and Markers

```latex
\fill[red] (1,1) circle (3pt);           % Filled point
\node[circle, fill=red, inner sep=2pt] at (1,1) {};  % Node as point
\draw[red] (1,1) node[cross out, draw] {};  % Cross marker
```

## Node Syntax

```latex
\node at (1,1) {Text};                   % Basic node
\node[above] at (1,1) {Text};            % Positioned above point
\node[below left] at (1,1) {Text};       % Below-left of point
\node[anchor=north] at (1,1) {Text};     % Anchored at north edge
\node[draw] at (1,1) {Boxed};            % Bordered node
\node[draw, rounded corners] at (1,1) {Rounded};  % Rounded box
\node[circle, draw] at (1,1) {O};        % Circle node
\node[fill=cyan] at (1,1) {Filled};      % Background color
```

### Node Positioning

| Position | Meaning |
|----------|---------|
| `above`, `below` | Vertical placement |
| `left`, `right` | Horizontal placement |
| `above left`, `below right` | Diagonal placement |
| `anchor=south` | Anchor node's south edge at point |

### Node Shapes

| Shape | Usage |
|-------|-------|
| `rectangle` | Default |
| `circle` | Round node |
| `ellipse` | Oval node |
| `diamond` | Diamond shape |
| `trapezium` | Trapezoid (requires shapes library) |

## Coordinate Systems

```latex
(2,3)                    % Cartesian coordinates
(30:2)                   % Polar coordinates (angle:radius)
++(1,0)                  % Relative to last point
+(1,0)                   % Relative offset (doesn't update position)
($(A)!0.5!(B)$)          % Midpoint (requires calc library)
(A |- B)                 % Intersection: x of A, y of B
(A -| B)                 % Intersection: x of B, y of A
```

## Line Styles Reference

| Style | Description |
|-------|-------------|
| `solid` | Default solid line |
| `dashed` | Dashed line |
| `dotted` | Dotted line |
| `dashdotted` | Alternating dash-dot |
| `densely dashed` | Closer dashes |
| `loosely dashed` | Wider dashes |

## Line Width Reference

| Width | Value |
|-------|-------|
| `ultra thin` | 0.1pt |
| `very thin` | 0.2pt |
| `thin` | 0.4pt |
| `semithick` | 0.6pt |
| `thick` | 0.8pt |
| `very thick` | 1.2pt |
| `ultra thick` | 1.6pt |

## Arrow Styles

```latex
\draw[->] (0,0) -- (2,0);               % Single arrow
\draw[<-] (0,0) -- (2,0);               % Reverse arrow
\draw[<->] (0,0) -- (2,0);              % Double arrow
\draw[->>] (0,0) -- (2,0);              % Double head
\draw[->>, >=stealth] (0,0) -- (2,0);   % Stealth style
\draw[-{Latex[length=3mm]}] (0,0) -- (2,0);  % Custom arrow (arrows.meta)
```

## Color Reference

### Available Named Colors

Standard LaTeX/TikZ named colors:
`black`, `white`, `red`, `green`, `blue`, `cyan`, `magenta`, `yellow`, `gray`, `lightgray`, `darkgray`, `brown`, `orange`, `purple`, `pink`

### Dark Mode Behavior

TikZJax plugin can invert `black` ↔ `white` in dark mode (configurable in settings).

```latex
% Text color - omit for automatic theme adaptation
\node at (1,0.5) {Text};              % Adapts to theme

% Explicit color - fixed, won't adapt
\node[black] at (1,1) {Text};         % Always black
```

**Note:** `\definecolor{}` custom colors are NOT affected by dark mode inversion.

## Loops and Iteration

```latex
\foreach \x in {0,1,2,3} {
  \fill[red] (\x,0) circle (2pt);
}

\foreach \x/\y in {0/A, 1/B, 2/C} {
  \node at (\x,0) {\y};
}

\foreach \i in {1,...,5} {
  \draw (0,0) -- (\i*72:1);
}
```

## Transformations

```latex
\begin{scope}[shift={(2,0)}]
  \draw (0,0) rectangle (1,1);
\end{scope}

\begin{scope}[rotate=45]
  \draw (0,0) rectangle (1,1);
\end{scope}

\begin{scope}[scale=0.5]
  \draw (0,0) circle (1);
\end{scope}
```

## Clipping

```latex
\begin{scope}
  \clip (0,0) rectangle (2,2);
  \fill[cyan] (1,1) circle (2);  % Only visible inside clip region
\end{scope}
```

## Layers

```latex
\begin{scope}[on background layer]
  \fill[lightgray] (0,0) rectangle (3,2);  % Behind main content
\end{scope}
```

## Package-Specific Syntax

### circuitikz (Circuits)

```tikz
\usepackage{circuitikz}
\begin{document}
\begin{circuitikz}
  \draw (0,0) to[R=$R$] (2,0);           % Resistor
  \draw (0,0) to[C=$C$] (2,0);           % Capacitor
  \draw (0,0) to[L=$L$] (2,0);           % Inductor
  \draw (0,0) to[battery1=$V$] (2,0);    % Battery
  \draw (0,0) to[diode] (2,0);           % Diode
  \draw (0,0) to[led] (2,0);             % LED
  \draw (0,0) node[ground] {};           % Ground symbol
\end{circuitikz}
\end{document}
```

### tikz-cd (Commutative Diagrams)

```tikz
\usepackage{tikz-cd}
\begin{document}
\begin{tikzcd}
  A \arrow[r, "f"] \arrow[d, "g"'] & B \arrow[d, "h"] \\
  C \arrow[r, "k"'] & D
\end{tikzcd}
\end{document}
```

Arrow modifiers:
- `'` - Label on opposite side
- `description` - Label on arrow
- `bend left`, `bend right` - Curved arrows
- `dashed`, `dotted` - Line styles
- `hook`, `two heads` - Special arrow tips

### chemfig (Chemistry)

```tikz
\usepackage{chemfig}
\begin{document}
\chemfig{H-C(-[2]H)(-[6]H)-H}           % Methane
\chemfig{*6(------)}                     % Benzene ring
\chemfig{A-[:30]B-[:-30]C}              % Angled bonds
\end{document}
```

### pgfplots (Plots)

```tikz
\usepackage{pgfplots}
\begin{document}
\begin{tikzpicture}
\begin{axis}[
  xlabel=$x$,
  ylabel=$y$,
  grid=major
]
\addplot[domain=-2:2] {x^2};
\end{axis}
\end{tikzpicture}
\end{document}
```

### tikz-3dplot (3D)

```tikz
\usepackage{tikz-3dplot}
\begin{document}
\tdplotsetmaincoords{60}{110}
\begin{tikzpicture}[tdplot_main_coords]
  \draw[thick,->] (0,0,0) -- (2,0,0) node[anchor=north east]{$x$};
  \draw[thick,->] (0,0,0) -- (0,2,0) node[anchor=north west]{$y$};
  \draw[thick,->] (0,0,0) -- (0,0,2) node[anchor=south]{$z$};
\end{tikzpicture}
\end{document}
```

## Common Patterns

### Grid with Labels

```tikz
\begin{document}
\begin{tikzpicture}[scale=1]
  % Grid
  \draw[lightgray, thin] (0,0) grid (4,3);

  % Axes
  \draw[thick, gray, ->] (-0.3,0) -- (4.5,0) node[right] {$x$};
  \draw[thick, gray, ->] (0,-0.3) -- (0,3.5) node[above] {$y$};

  % Tick labels
  \foreach \x in {1,2,3,4} \node[below] at (\x,0) {$\x$};
  \foreach \y in {1,2,3} \node[left] at (0,\y) {$\y$};
\end{tikzpicture}
\end{document}
```

### Legend Box

```latex
\begin{scope}[shift={(5,2)}]
  \fill[black] (0,0) rectangle (2,1.2);
  \draw[cyan, thick] (0.1,0.9) -- (0.5,0.9);
  \node[right] at (0.5,0.9) {Line A};
  \draw[red, thick] (0.1,0.5) -- (0.5,0.5);
  \node[right] at (0.5,0.5) {Line B};
\end{scope}
```

### Brace Annotation

```tikz
\usepackage{tikz}
\usetikzlibrary{decorations.pathreplacing}
\begin{document}
\begin{tikzpicture}
  \draw[decorate, decoration={brace, amplitude=5pt}] (0,0) -- (2,0)
    node[midway, below=5pt] {Width};
\end{tikzpicture}
\end{document}
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| Diagram not rendering | Missing `\begin{document}` | Add document wrapper |
| Text not adapting to theme | Explicit color in `\node` | Omit color specification |
| Color mixing syntax error | `blue!30` not supported | Use base colors only |
| Korean text broken | Unsupported encoding | Use English only |
| Scale too small | `scale < 1` | Use `scale=1` |
