---
name: mathjax-rendering
description: Render mathematical formulas in Obsidian using LaTeX/MathJax syntax. Use when writing equations, matrices, integrals, summations, or any mathematical notation in Obsidian notes.
---

# MathJax Rendering in Obsidian

Obsidian uses MathJax to render LaTeX math expressions. This skill covers essential syntax for mathematical notation.

For complete symbol tables and advanced commands, see [reference.md](reference.md).

## 1. Basic Syntax

### Inline vs Block

```markdown
Inline: The equation $E = mc^2$ appears within text.

Block (centered, display-style):
$$
\int_0^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

- **Inline** (`$...$`): Compact, flows with paragraph
- **Block** (`$$...$$`): Larger, centered, multi-line capable

---

## 2. Fractions and Roots

```latex
\frac{a}{b}       % Standard fraction
\sqrt{x}          % Square root
\sqrt[n]{x}       % n-th root
\binom{n}{k}      % Binomial coefficient
```

**Examples:**

```latex
$$
\frac{d}{dx}\left(\frac{f(x)}{g(x)}\right) = \frac{f'(x)g(x) - f(x)g'(x)}{[g(x)]^2}
$$

$$
\sqrt{a^2 + b^2} = c \qquad \sqrt[3]{27} = 3
$$
```

---

## 3. Superscripts and Subscripts

```latex
$x^2$           % Superscript
$x_1$           % Subscript
$x_i^2$         % Both combined
$x^{10}$        % Multiple characters need braces
$x_{n+1}$       % Expression as subscript
```

**Note**: Use braces `{}` for multi-character exponents/subscripts.

---

## 4. Greek Letters

### Common Letters

| Lowercase | | Uppercase | |
|-----------|--------|-----------|--------|
| `\alpha` α | `\beta` β | `\Gamma` Γ | `\Delta` Δ |
| `\gamma` γ | `\delta` δ | `\Theta` Θ | `\Lambda` Λ |
| `\epsilon` ε | `\theta` θ | `\Sigma` Σ | `\Phi` Φ |
| `\lambda` λ | `\mu` μ | `\Psi` Ψ | `\Omega` Ω |
| `\pi` π | `\sigma` σ | | |
| `\phi` φ | `\omega` ω | | |

See [reference.md](reference.md) for complete Greek alphabet.

---

## 5. Common Operators and Symbols

| Symbol | Syntax | | Symbol | Syntax |
|--------|--------|---|--------|--------|
| ≤ | `\leq` | | ∈ | `\in` |
| ≥ | `\geq` | | ∉ | `\notin` |
| ≠ | `\neq` | | ⊂ | `\subset` |
| ≈ | `\approx` | | ∪ | `\cup` |
| × | `\times` | | ∩ | `\cap` |
| · | `\cdot` | | ∞ | `\infty` |
| ± | `\pm` | | ∂ | `\partial` |
| ∀ | `\forall` | | ∇ | `\nabla` |
| ∃ | `\exists` | | ∅ | `\emptyset` |

See [reference.md](reference.md) for complete symbol tables.

---

## 6. Matrices

### Matrix Environments

| Environment | Brackets |
|-------------|----------|
| `pmatrix` | ( ) |
| `bmatrix` | [ ] |
| `vmatrix` | \| \| (determinant) |
| `Bmatrix` | { } |

### Examples

```latex
$$
A = \begin{pmatrix}
a & b \\
c & d
\end{pmatrix}
$$

$$
\det(A) = \begin{vmatrix}
a & b \\
c & d
\end{vmatrix} = ad - bc
$$

$$
I = \begin{bmatrix}
1 & 0 & 0 \\
0 & 1 & 0 \\
0 & 0 & 1
\end{bmatrix}
$$
```

### With Ellipsis

```latex
$$
\begin{pmatrix}
a_{11} & \cdots & a_{1n} \\
\vdots & \ddots & \vdots \\
a_{m1} & \cdots & a_{mn}
\end{pmatrix}
$$
```

---

## 7. Aligned Equations

Use `aligned` environment with `&` for alignment and `\\` for line breaks:

```latex
$$
\begin{aligned}
(a+b)^2 &= (a+b)(a+b) \\
        &= a^2 + 2ab + b^2
\end{aligned}
$$
```

### Conditional Definitions (cases)

```latex
$$
f(x) = \begin{cases}
x^2 & \text{if } x \geq 0 \\
-x  & \text{if } x < 0
\end{cases}
$$
```

### Text in Math

Use `\text{...}` for regular text:

```latex
$$
x = 5 \text{ where } x \in \mathbb{N}
$$
```

---

## 8. Integrals, Sums, and Limits

### Integrals

```latex
$$
\int_a^b f(x) \, dx \qquad \iint_D f \, dA \qquad \oint_C \mathbf{F} \cdot d\mathbf{r}
$$
```

**Tip**: Use `\,` before `dx` for proper spacing.

### Sums and Products

```latex
$$
\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
$$

$$
\prod_{i=1}^{n} a_i
$$
```

### Limits

```latex
$$
\lim_{x \to 0} \frac{\sin x}{x} = 1
$$

$$
\lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n = e
$$
```

---

## 9. Delimiters

Use `\left` and `\right` for auto-sizing:

```latex
$$
\left( \frac{a}{b} \right) \qquad \left[ \sum_{i=1}^{n} x_i \right] \qquad \left\{ x : x > 0 \right\}
$$
```

### One-sided Delimiter

Use `\left.` or `\right.` for invisible delimiter:

```latex
$$
\left. \frac{df}{dx} \right|_{x=0}
$$
```

---

## 10. Font Styles

| Style | Syntax | Use Case |
|-------|--------|----------|
| Bold | `\mathbf{v}` | Vectors |
| Roman | `\mathrm{d}x` | Differential d |
| Blackboard | `\mathbb{R}` | Number sets |
| Calligraphic | `\mathcal{L}` | Operators |

### Number Sets

```latex
$$
\mathbb{N} \subset \mathbb{Z} \subset \mathbb{Q} \subset \mathbb{R} \subset \mathbb{C}
$$
```

---

## 11. Decorations

| Decoration | Syntax |
|------------|--------|
| Hat | `\hat{x}` |
| Bar | `\bar{x}` |
| Tilde | `\tilde{x}` |
| Vector | `\vec{x}` |
| Dot | `\dot{x}` |
| Double dot | `\ddot{x}` |

### Overbrace/Underbrace

```latex
$$
\overbrace{a + b + c}^{\text{sum}} = \underbrace{x + y + z}_{\text{total}}
$$
```

### Arrows

```latex
$$
\overrightarrow{AB} \qquad \overleftarrow{CD}
$$
```

---

## 12. Common Patterns

### Derivatives

```latex
$$
\frac{dy}{dx} \qquad \frac{\partial f}{\partial x} \qquad \nabla f
$$
```

### Norm and Absolute Value

```latex
$$
\|x\| = \sqrt{\sum x_i^2} \qquad |x - y| \leq |x| + |y|
$$
```

### Probability

```latex
$$
P(A \mid B) = \frac{P(B \mid A) P(A)}{P(B)}
$$

$$
\mathbb{E}[X] = \sum_{i} x_i P(X = x_i)
$$
```

---

## Quick Reference

```latex
% Fractions and roots
\frac{a}{b}  \sqrt{x}  \sqrt[n]{x}

% Greek (common)
\alpha \beta \gamma \theta \lambda \pi \sigma \omega
\Gamma \Delta \Sigma \Omega

% Relations
= \neq \leq \geq \approx \equiv \in \subset

% Operations
+ - \times \div \cdot \pm

% Calculus
\int \sum \prod \lim \partial \nabla

% Sets
\mathbb{R} \mathbb{N} \mathbb{Z} \mathbb{Q} \mathbb{C}

% Decorations
\hat{x} \bar{x} \vec{x} \dot{x}
```
