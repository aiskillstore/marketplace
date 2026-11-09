# Formulas

`pptx-nova` treats mathematical formulas as first-class semantic assets, not as
ordinary decorative pictures. The goal is to preserve the author's math intent
while choosing the most reliable PowerPoint representation for the task.

## Formula policy

Record the formula policy in `deck_lock.json.typography.formulaPolicy`:

| policy        | Use when                                                                                            | Output behavior                                                                                                            |
| ------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `mixed`       | Default for technical, academic, and training decks                                                 | Keep simple inline math as editable text/Unicode; render complex formulas as formula assets.                               |
| `text-only`   | Business decks or user explicitly values editability over typesetting                               | Use ordinary text boxes and Unicode symbols; no rendered formula assets.                                                   |
| `rendered`    | Formula-heavy decks where visual fidelity matters                                                   | Render every formula-worthy expression as SVG formula assets and insert with `add-equation.assetSource`.                   |
| `native-omml` | User explicitly requests editable PowerPoint equations and the expression fits the supported subset | Use `add-equation` with `mode: "native-omml"`; fall back to rendered SVG for unsupported or typography-sensitive formulas. |

Default to `mixed` when the prompt contains LaTeX, `$...$`, `$$...$$`, equation-heavy
source text, or terms like formula / equation / 数学公式 / LaTeX / OMML. In Studio
or high-risk decks, include the formula policy in the one-time design lock confirmation.

Do not invent equations to make a slide look more technical. Formula assets must come
from the user prompt, source material, data, or a clearly stated derivation needed by the deck.

## Lock and manifest

When any formula is rendered or inserted natively, write formula intent into the run files:

`deck_lock.json`:

```json
{
  "typography": {
    "formulaPolicy": "mixed",
    "formulaFallback": "rendered",
    "mathFont": "Cambria Math, Latin Modern Math, Noto Sans Math"
  },
  "slides": [
    {
      "index": 2,
      "title": "Model objective",
      "slideType": "formulaSlide",
      "rhythm": "breathing",
      "formulas": ["objective_loss"]
    }
  ]
}
```

`assets_manifest.json`:

```json
{
  "schemaVersion": "pptx-nova-assets-manifest/v1",
  "assetRoot": "assets",
  "entries": [
    {
      "id": "objective_loss",
      "kind": "formula",
      "status": "rendered",
      "path": "assets/formulas/objective_loss.svg",
      "source": {
        "kind": "formula",
        "latex": "L(\\theta)=\\sum_{i=1}^{n}(y_i-f_\\theta(x_i))^2",
        "display": "block"
      },
      "pptxUse": {
        "role": "formula-block",
        "crop": "contain",
        "noCrop": true,
        "altText": "L(theta)=sum residual squared"
      }
    }
  ]
}
```

Formula entries use `kind: "formula"` and one of these statuses:

| status        | Meaning                                                       | Blocks delivery         |
| ------------- | ------------------------------------------------------------- | ----------------------- |
| `available`   | User supplied or existing formula asset is available          | No                      |
| `rendered`    | This run materialized an SVG; verify its provider and content | No                      |
| `native`      | This run inserted a native PowerPoint equation                | No                      |
| `placeholder` | Visual placeholder only                                       | Yes for formal delivery |
| `needs-user`  | Needs user source, approval, or missing LaTeX                 | Yes                     |
| `missing`     | Declared path does not exist                                  | Yes                     |

Always set `pptxUse.noCrop: true` for formulas. Cropping a formula is almost always a
semantic error.

## Patch guidance

Built-in SVG fallback (literal LaTeX text, without mathematical typesetting):

```json
{
  "op": "add-equation",
  "slide": 2,
  "x": "1.2in",
  "y": "2.0in",
  "w": "5.8in",
  "h": "0.9in",
  "latex": "\\frac{\\partial L}{\\partial \\theta}=0",
  "display": true,
  "name": "S3_Formula_Objective"
}
```

For typeset production output, supply an SVG produced by a suitable math renderer:

```json
{
  "op": "add-equation",
  "slide": 2,
  "x": "1.2in",
  "y": "2.0in",
  "w": "5.8in",
  "h": "0.9in",
  "latex": "\\frac{\\partial L}{\\partial \\theta}=0",
  "display": true,
  "assetSource": {
    "path": "formulas/s3-objective.svg",
    "mimeType": "image/svg+xml"
  },
  "name": "S3_Formula_Objective"
}
```

Preferred patch op for an editable PowerPoint equation when the formula fits the
native subset:

```json
{
  "op": "add-equation",
  "slide": 2,
  "x": "1.2in",
  "y": "2.0in",
  "w": "3.2in",
  "h": "0.7in",
  "latex": "E=mc^2",
  "mode": "native-omml",
  "name": "S3_Formula_Energy"
}
```

In `mode: "native-omml"`, `display` is ignored. It only affects rendered SVG
fallback sizing (`display: false` uses the inline SVG fallback box).

Use the built-in fallback for quick drafts. For final formula-heavy decks, render the
formula asset into the run directory and insert it with `add-equation.assetSource`;
still keep the formula metadata in `assets_manifest.json`.

## Render manifest

Only when a literal-LaTeX draft SVG is intended, use the bundled helper with a dedicated
`formula-drafts.json` manifest containing just those entries and fresh output paths:

```bash
node <skill-root>/scripts/cli/assets/formula-render.mjs formula-drafts.json
```

Useful variants:

```bash
node <skill-root>/scripts/cli/assets/formula-render.mjs formula-drafts.json --dry-run
node <skill-root>/scripts/cli/assets/formula-render.mjs formula-drafts.json --out formula-drafts.rendered.json
node <skill-root>/scripts/cli/assets/formula-render.mjs formula-drafts.json --asset-root assets
```

The current bundled provider is `text-svg`: a deterministic offline SVG text wrapper.
It escapes and displays the literal LaTeX source; it does not typeset fractions,
radicals, matrices, or other LaTeX notation. Its `rendered` status means that an
SVG file was materialized, not that the formula was mathematically typeset.
It writes SVG files, updates formula entries to
`status: "rendered"`, records `render.mime: "image/svg+xml"`, and enforces
`pptxUse.noCrop: true`. For typography-sensitive final decks, prefer externally
typeset SVG assets when available and keep the same manifest fields. For expressions
in the editable native subset, use `native-omml` when that representation meets the task.

The helper processes every formula entry regardless of `available`, `rendered`, or `native`
status and overwrites the resolved SVG path. Do not pass a mixed manifest containing supplied,
externally typeset, or native formulas. `--out` redirects only the updated manifest, not the SVG
writes. After reviewing draft outputs, merge only their intended entries into the run's main
manifest; preserve other assets and formula records.

Simple inline formulas can stay in ordinary text when all of these are true:

- The expression is readable in plain text or Unicode (`E = mc^2`, `p < 0.05`, `A/B`).
- It does not need stacked fraction, large operator limits, matrix/cases, radical, or aligned equations.
- The user did not ask for formal mathematical typesetting.

Use rendered/native formula assets for:

- Fractions, matrices, cases, radicals, large operators with limits, aligned equations.
- Formula-heavy academic or engineering slides.
- Any expression where plain text would change meaning or readability.

The current native OMML subset is conservative: plain math text, superscript,
subscript, top-level `\frac{...}{...}`, and top-level `\sqrt{...}`. Use rendered
SVG for matrices, aligned equations, cases, and complex n-ary limits until the
native subset expands.

Native script handling is intentionally trailing-script-only. The whole expression
prefix before the final top-level `^` or `_` becomes the base expression; for
example `\frac{a}{b}^2` is emitted as a fraction with a trailing superscript.
`x_i^2` is emitted as nested subscript then superscript, not as aligned
`sSubSup`. Avoid native mode for expressions where exact LaTeX grouping,
simultaneous aligned super/subscripts, or operator limits are part of the meaning;
render those formulas to SVG instead.

## Verification

For imported MathType/OLE equations, keep the embedded object and its preview
relationship/crop. WMF comments carry baseline metadata, not horizontal padding;
the current renderer uses saved text alignment and window/viewport mapping.
Re-render the unchanged source before adding offsets, removing crop or replacing
the equation. A corrected preview is not native OMML conversion or newly editable
math. Follow `../edit/native-shape-editing.md` for host geometry and resource ownership.

Formula decks still pass the normal gates:

```
check-lock -> dry-run -> vision-check -> PNG/contact-sheet
```

Add formula-specific checks during PNG review:

1. Formula is not cropped and has enough padding.
2. Formula color has sufficient contrast on the slide background.
3. Inline formulas align with surrounding text baseline closely enough to read.
4. Block formulas have stable visual rhythm and do not overpower the slide title.
5. The final summary mentions whether formulas are editable text, rendered assets, or native equations.

For an imported native equation, retain attributed OMML text, including `m:t`
with `xml:space` or other attributes, whitespace, fractions and sub/superscript
structure. Re-render the same source with the current runtime before diagnosing
missing math text or replacing it with an image. Restored content and remaining
math metric differences are separate findings.

When exporting to PDF, run `xdoc check --checks fonts,links,compat` if the deck uses
native equations or math fonts, then review actual glyphs; the font preflight
does not prove codepoint coverage. SVG formula/image text needs resolved PDF font
bytes independently of browser CSS font readiness; inspect local SVG text and
inherited inline styles, and do not assume external images/stylesheets were
fetched. See `../review/export-and-check.md` for the distinct font-evidence boundaries.
