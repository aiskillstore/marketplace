# LaTeX Poster Packages Reference

Detailed guide for beamerposter, tikzposter, and baposter packages.

## Package Comparison

| Feature | beamerposter | tikzposter | baposter |
|---------|-------------|-----------|----------|
| **Learning Curve** | Low (if you know Beamer) | Medium | Medium |
| **Customization** | Theme-based | High (TikZ) | Template-based |
| **Layout Control** | Manual | Manual | Automatic |
| **Best For** | Academic conferences | Modern designs | Multi-column layouts |
| **Default Themes** | Many Beamer themes | Built-in themes | Default styles |

## beamerposter

### Basic Structure

```latex
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}

% Theme selection
\usetheme{Madrid}
\usecolortheme{beaver}

% Typography
\usepackage{helvet}
\usefonttheme{professionalfonts}

% Packages
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multicol}
\usepackage{tikz}

\begin{document}

\begin{frame}
  \begin{center}
    \huge{Title Here}\\
    \Large{Authors and Affiliations}
  \end{center}

  \vspace{1cm}

  \begin{columns}[t]

    \begin{column}{0.32\paperwidth}
      \begin{block}{Introduction}
        Content here
      \end{block}
    \end{column}

    \begin{column}{0.32\paperwidth}
      \begin{block}{Methods}
        Content here
      \end{block}
    \end{column}

    \begin{column}{0.32\paperwidth}
      \begin{block}{Results}
        Content here
      \end{block}
    \end{column}

  \end{columns}
\end{frame}

\end{document}
```

### Advanced Features

**Custom blocks:**
```latex
% Define custom block style
\setbeamercolor{block title}{bg=blue,fg=white}
\setbeamercolor{block body}{bg=blue!10,fg=black}

% Rounded blocks
\setbeamertemplate{blocks}[rounded][shadow=true]

% Colored block
\begin{block}[red]{Important Finding}
  Content with red header
\end{block}
```

**Nested blocks:**
```latex
\begin{block}{Outer Block}
  \begin{block}{Inner Block}
    Nested content
  \end{block}
\end{block}
```

**Alert and example blocks:**
```latex
\begin{alertblock}{Key Finding}
  Important result
\end{alertblock}

\begin{exampleblock}{Example}
  Illustrative example
\end{exampleblock}
```

### Common Themes

**Academic themes:**
```latex
\usetheme{Madrid}        % Clean, professional
\usetheme{Berlin}        % Navigation bars
\usetheme{Antibes}        % Tree-like navigation
\usetheme{Boadilla}       % Minimal design
\usetheme{Frankfurt}      % Progress indicator
```

**Color themes:**
```latex
\usecolortheme{default}   % Blue and white
\usecolortheme{beaver}    % Red and gray
\usecolortheme{crane}     % Yellow and orange
\usecolortheme{dolphin}    % Blue and purple
\usecolortheme{seahorse}  % Light blue and gray
\usecolortheme{wolverine} % Yellow and blue
```

## tikzposter

### Basic Structure

```latex
\documentclass[25pt,a0paper,portrait,margin=10mm]{tikzposter}

% Theme and color
\usetheme{Default}
\usecolorstyle{Denmark}

% Packages
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tikz}
\usetikzlibrary{calc}

\begin{document}

\begin{poster}{
  grid=false,
  colspacing=1em,
  eyecatcher=true,
  background=plain
}{
  % Eyecatcher (logo or image)
  \begin{tikzpicture}
    \node[inner sep=0pt] {\includegraphics[width=5cm]{logo.png}};
  \end{tikzpicture}
}{
  % Title
  \title{Research Title}
  % Author
  \author{Author Names}
  % Institute
  \institute{Institution}
}{
  % Main content
  \block{Introduction}{
    Content here
  }
}

\end{document}
```

### Advanced Features

**Custom colors:**
```latex
\definecolor{myblue}{RGB}{0,102,204}
\definecolor{myred}{RGB}{204,0,0}

\usecolorstyle{Denmark}
\setcolorpalette{primary}{myblue}
\setcolorpalette{secondary}{myred}
```

**Custom block styles:**
```latex
% Create custom block style
\newblockstyle{custom}{
  titlewidthscale=1,
  bodywidthscale=1,
  titleleft,
  titleoffsetx=2em,
  titleoffsety=1ex,
  bodyoffsetx=2em,
  bodyoffsety=2ex,
  bodyverticalshift=2em,
  roundedcorners=10,
  linewidth=2pt,
  titleinnersep=1em,
  bodyinnersep=1em
}

% Use custom style
\begin{blockstyle}{custom}
  \block{Title}{Content}
\end{blockstyle}
```

**Multi-column layout:**
```latex
\begin{columns}[c]

  \begin{column}{0.48\linewidth}
    \block{Column 1}{
      Content for first column
    }
  \end{column}

  \begin{column}{0.48\linewidth}
    \block{Column 2}{
      Content for second column
    }
  \end{column}

\end{columns}
```

**Nested blocks:**
```latex
\begin{block}{Outer}{
  \innerblock{Inner Title}{
    Nested content
  }
}
\end{block}
```

### Built-in Themes

**Themes:**
```latex
\usetheme{Default}      % Clean, simple
\usetheme{Envelope}     % Envelope shape
\usetheme{Wave}         % Wave header
\usetheme{Rays}         % Radial rays
\usetheme{VerticalGrad} % Vertical gradient
```

**Color styles:**
```latex
\usecolorstyle{Denmark}    % Nordic colors
\usecolorstyle{Germany}    % German flag colors
\usecolorstyle{Spain}      % Spanish flag colors
\usecolorstyle{France}     % French flag colors
\usecolorstyle{Sweden}     % Swedish flag colors
\usecolorstyle{Russia}     % Russian flag colors
\usecolorstyle{Brazil}     % Brazilian flag colors
```

## baposter

### Basic Structure

```latex
\documentclass[a0paper,portrait,fontscale=0.285]{baposter}

% Packages
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{tikz}

\begin{poster}{

  grid=false,
  columns=3,
  colspacing=1.5em,
  eyecatcher=true,
  background=plain,
  bgColorOne=white,
  borderColor=blue!50,
  headerheight=0.12\textheight,
  textborder=roundedleft,
  headerborder=closed,
  boxheaderheight=2em

}{

  % Header
  \begin{columns}
    \begin{column}{0.15\linewidth}
      \includegraphics[width=\linewidth]{logo.png}
    \end{column}
    \begin{column}{0.85\linewidth}
      \vspace{2em}
      \color{blue!80!black}
      \Huge{\textbf{Research Title}}\\[1ex]
      \large{Author Names \quad Institution}
    \end{column}
  \end{columns}

  % Content
  \headerbox{Introduction}{name=intro,column=0,row=0}{
    Content here
  }

  \headerbox{Methods}{name=methods,column=1,row=0}{
    Content here
  }

  \headerbox{Results}{name=results,column=2,row=0}{
    Content here
  }

}

\end{poster}
```

### Advanced Features

**Box positioning:**
```latex
% Absolute positioning with row/col
\headerbox{Title}{name=box1,column=0,row=0}{
  Content
}

% Automatic placement with spanning
\headerbox{Large Box}{name=box2,column=0,below=intro,span=2}{
  Spans two columns
}

% Manual positioning
\headerbox{Title}{name=box3,column=1,row=1}{
  Content
}
```

**Custom box styles:**
```latex
% Different border styles
\headerbox{Title}{name=box1,column=0,row=0,textborder=roundedleft}{
  Content
}

\headerbox{Title}{name=box2,column=1,row=0,textborder=rectangle}{
  Content
}

\headerbox{Title}{name=box3,column=2,row=0,textborder=none}{
  Content
}
```

**Color customization:**
```latex
\begin{poster}{
  bgColorOne=white,
  bgColorTwo=blue!10,
  borderColor=blue!50,
  headerColorOne=blue!80!black,
  headerColorTwo=blue!40,
  headerFontColor=white,
  boxColorOne=blue!10,
  boxColorTwo=white
}{...}{...}
```

### Layout Strategies

**Three-column layout:**
```latex
% Column 0: Introduction, Methods
\headerbox{Introduction}{name=intro,column=0,row=0}{...}
\headerbox{Methods}{name=methods,column=0,below=intro}{...}

% Column 1: Results
\headerbox{Results}{name=results,column=1,row=0,span=2}{...}

% Column 2: Conclusion, References
\headerbox{Conclusion}{name=conclusion,column=2,below=results}{...}
\headerbox{References}{name=refs,column=2,below=conclusion}{...}
```

**Two-column layout:**
```latex
\begin{poster}{columns=2,...}{...}{...}
  \headerbox{Introduction}{name=intro,column=0,row=0}{...}
  \headerbox{Methods}{name=methods,column=1,row=0}{...}
  \headerbox{Results}{name=results,column=0,below=intro,span=2}{...}
  \headerbox{Conclusion}{name=conclusion,column=0,below=results}{...}
\end{poster}
```

## Cross-Package Comparison

### Code Examples for Same Layout

**Three-column layout with title, intro, methods, results, conclusion:**

**beamerposter:**
```latex
\begin{columns}[t]
  \begin{column}{0.32\paperwidth}
    \begin{block}{Introduction}...\end{block}
    \begin{block}{Methods}...\end{block}
  \end{column}
  \begin{column}{0.32\paperwidth}
    \begin{block}{Results}...\end{block}
  \end{column}
  \begin{column}{0.32\paperwidth}
    \begin{block}{Conclusion}...\end{block}
  \end{column}
\end{columns}
```

**tikzposter:**
```latex
\begin{columns}
  \begin{column}{0.32\linewidth}
    \block{Introduction}{...}
    \block{Methods}{...}
  \end{column}
  \begin{column}{0.32\linewidth}
    \block{Results}{...}
  \end{column}
  \begin{column}{0.32\linewidth}
    \block{Conclusion}{...}
  \end{column}
\end{columns}
```

**baposter:**
```latex
\headerbox{Introduction}{name=intro,column=0,row=0}{...}
\headerbox{Methods}{name=methods,column=0,below=intro}{...}
\headerbox{Results}{name=results,column=1,row=0}{...}
\headerbox{Conclusion}{name=conclusion,column=2,row=0}{...}
```

## Package Selection Guide

### Choose beamerposter when:
- You're familiar with Beamer presentations
- Need institutional or standard academic themes
- Want quick setup with minimal customization
- Attend traditional academic conferences

### Choose tikzposter when:
- Want modern, colorful designs
- Need extensive customization
- Like TikZ and want full control
- Creating posters for digital display or modern conferences

### Choose baposter when:
- Need multi-column layouts with automatic spacing
- Want consistent box positioning
- Creating complex layouts with many sections
- Need precise control over box placement

## Common Patterns

### Figure with Caption

**beamerposter:**
```latex
\begin{block}{Results}
  \begin{figure}
    \centering
    \includegraphics[width=0.9\linewidth]{figure.png}
    \caption{Figure description}
  \end{figure}
\end{block}
```

**tikzposter:**
```latex
\block{Results}{
  \begin{tikzfigure}
    \includegraphics[width=0.9\linewidth]{figure.png}
    \caption{Figure description}
  \end{tikzfigure}
}
\end{block}
```

**baposter:**
```latex
\headerbox{Results}{name=results,column=1,row=0}{
  \begin{figure}
    \centering
    \includegraphics[width=0.9\linewidth]{figure.png}
    \caption{Figure description}
  \end{figure}
}
```

### Table Integration

```latex
\usepackage{booktabs}

\begin{table}
  \centering
  \begin{tabular}{lcc}
    \toprule
    Group & Sample & Value \\
    \midrule
    Control & 50 & 12.3 \\
    Treatment & 50 & 15.7 \\
    \bottomrule
  \end{tabular}
  \caption{Comparison table}
\end{table}
```

### Math Equations

```latex
\begin{equation}
  f(x) = \sum_{i=1}^{n} w_i x_i + b
\end{equation}

Inline math: $y = mx + b$
```

## Troubleshooting

### Common Issues

**beamerposter issues:**
- Wrong page size: Check `\usepackage[size=a0,...]` setting
- Content cut off: Adjust `\setbeamersize{text margin left=...}`
- Font too small: Increase `scale` factor in documentclass

**tikzposter issues:**
- Blocks overlapping: Check column widths and total width
- Colors not showing: Ensure color package loaded
- Theme not applying: Check theme spelling and availability

**baposter issues:**
- Boxes not positioning: Verify row/column numbers
- Overflow: Adjust box sizes or span properties
- Header issues: Check `headerheight` parameter

### Debugging

**Show page boundaries:**
```latex
\usepackage{eso-pic}
\AddToShipoutPictureBG{
  \AtPageLowerLeft{
    \put(0,0){
      \framebox(\LenToUnit{\paperwidth},\LenToUnit{\paperheight}){}
    }
  }
}
```

**Check margins:**
```latex
\usepackage{layout}
\begin{document}
  \layout
\end{document}
```
