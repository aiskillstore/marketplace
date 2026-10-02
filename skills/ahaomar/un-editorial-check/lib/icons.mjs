// Category and severity icons — one set of hand-authored vector artwork, two
// renderers.
//
// PROVENANCE. Every path below was extracted verbatim from the artwork Omar
// approved as the report design, by `.feedbacks/design/extract-icons.mjs`, which
// reads `build-mockup.mjs` — the generator for that design — rather than the
// HTML it emits. Circles became four cubic Béziers (k = 0.5522847498 r) so the
// converter has one geometry to know about and the shipped data is exactly what
// was looked at, not a redrawn approximation of it. Re-run the extractor to
// regenerate `icons.json`; this table is its transcription.
//
// WHY PATHS AND NOT GLYPHS. The PDF is set in embedded Roboto Condensed,
// WinAnsi encoded. A glyph icon or an emoji there is either missing or a
// question mark, so PHASE-9-PLAN §5 rules them out. These are drawn: the same
// path data emitted as PDF path operators for the report PDF and as inline
// <svg> for the HTML report, with no image assets, no icon fonts and no fonts
// at all beyond the embedded Roboto Condensed.
//
// THE ICON IS NEVER THE ONLY SIGNAL. A marker is decoration beside the
// category's own name and code, and a severity's own label. The report has to
// read the same in greyscale and to a screen reader, so nothing here carries
// meaning that the surrounding text does not also carry.
//
// Stroke cap and join are round everywhere: both sources round their caps, and
// the one unclosed triangle (the warning severity) is closed, so line caps
// never appear in the artwork.

/** The icon coordinate system: a 16 x 16 box, y running downwards. */
export const ICON_BOX = 16;

/**
 * Stroke width for a shape that does not carry one. The artwork omits the
 * field when it is this value, so a renderer that reads `shape.w` directly
 * writes `undefined` into the HTML and `NaN` into the PDF content stream.
 */
const DEFAULT_STROKE_WIDTH = 1.5;

const strokeWidth = (shape) => shape.w ?? DEFAULT_STROKE_WIDTH;

/**
 * The thirteen category icons, keyed by exactly the names in `CATEGORY_LEGEND`.
 * `tests/icons.mjs` asserts the two key sets are equal, so a category cannot
 * gain a legend entry without an icon or lose an icon without a legend entry.
 *
 * Shape fields: `d` path data, `paint` 'stroke' | 'fill', `colour` 'current' |
 * 'white' (default 'current'), `w` stroke width (default 1.5).
 */
export const CATEGORY_ICONS = {
  "spelling": [
    { d: 'M2.5 13.5 8 2.5l5.5 11M4.9 9.2h6.2', paint: 'stroke' },
  ],
  "grammar": [
    { d: 'M2.4 4h4.4v5.1c0 2.4-1.4 3.9-3.9 4.4v-1.9c1.4-.4 2-1.2 2-2.3H2.4zM9.2 4h4.4v5.1c0 2.4-1.4 3.9-3.9 4.4v-1.9c1.4-.4 2-1.2 2-2.3H9.2z', paint: 'stroke' },
  ],
  "numerals": [
    { d: 'M6.4 2.6 4.9 13.4M11.1 2.6 9.6 13.4M2.6 6.1h10.8M2.6 9.9h10.8', paint: 'stroke' },
  ],
  "terminology": [
    { d: 'M8.1 2.2h5.5v5.5L7.6 13.6 2.2 8.2z', paint: 'stroke' },
    { d: 'M12.15 4.8C12.15 5.3247 11.7247 5.75 11.2 5.75C10.6753 5.75 10.25 5.3247 10.25 4.8C10.25 4.2753 10.6753 3.85 11.2 3.85C11.7247 3.85 12.15 4.2753 12.15 4.8Z', paint: 'stroke' },
  ],
  "register": [
    { d: 'M2.4 4.4h11.2M2.4 8h11.2M2.4 11.6h11.2', paint: 'stroke' },
    { d: 'M7.3 4.4C7.3 5.3389 6.5389 6.1 5.6 6.1C4.6611 6.1 3.9 5.3389 3.9 4.4C3.9 3.4611 4.6611 2.7 5.6 2.7C6.5389 2.7 7.3 3.4611 7.3 4.4Z', paint: 'fill' },
    { d: 'M12.1 8C12.1 8.9389 11.3389 9.7 10.4 9.7C9.4611 9.7 8.7 8.9389 8.7 8C8.7 7.0611 9.4611 6.3 10.4 6.3C11.3389 6.3 12.1 7.0611 12.1 8Z', paint: 'fill' },
    { d: 'M8.5 11.6C8.5 12.5389 7.7389 13.3 6.8 13.3C5.8611 13.3 5.1 12.5389 5.1 11.6C5.1 10.6611 5.8611 9.9 6.8 9.9C7.7389 9.9 8.5 10.6611 8.5 11.6Z', paint: 'fill' },
  ],
  "agent-review": [
    { d: 'M1.4 8c2.6-3.7 10.6-3.7 13.2 0-2.6 3.7-10.6 3.7-13.2 0z', paint: 'stroke' },
    { d: 'M10.1 8C10.1 9.1598 9.1598 10.1 8 10.1C6.8402 10.1 5.9 9.1598 5.9 8C5.9 6.8402 6.8402 5.9 8 5.9C9.1598 5.9 10.1 6.8402 10.1 8Z', paint: 'stroke' },
  ],
  "hate-speech": [
    { d: 'M3.8 12.2 12.2 3.8', paint: 'stroke' },
    { d: 'M14 8C14 11.3137 11.3137 14 8 14C4.6863 14 2 11.3137 2 8C2 4.6863 4.6863 2 8 2C11.3137 2 14 4.6863 14 8Z', paint: 'stroke' },
  ],
  "discriminatory": [
    { d: 'M1.9 13.6c0-2.6 1.9-4.2 4.2-4.2s4.2 1.6 4.2 4.2', paint: 'stroke' },
    { d: 'M11.3 9.7c1.9 0 3.2 1.6 3.2 3.9', paint: 'stroke' },
    { d: 'M8.3 5.4C8.3 6.615 7.315 7.6 6.1 7.6C4.885 7.6 3.9 6.615 3.9 5.4C3.9 4.185 4.885 3.2 6.1 3.2C7.315 3.2 8.3 4.185 8.3 5.4Z', paint: 'stroke' },
    { d: 'M13.4 6.1C13.4 7.0389 12.6389 7.8 11.7 7.8C10.7611 7.8 10 7.0389 10 6.1C10 5.1611 10.7611 4.4 11.7 4.4C12.6389 4.4 13.4 5.1611 13.4 6.1Z', paint: 'stroke' },
  ],
  "diplomacy": [
    { d: 'M2 8h12M8 2c2.7 3.5 2.7 8.5 0 12M8 2c-2.7 3.5-2.7 8.5 0 12', paint: 'stroke' },
    { d: 'M14 8C14 11.3137 11.3137 14 8 14C4.6863 14 2 11.3137 2 8C2 4.6863 4.6863 2 8 2C11.3137 2 14 4.6863 14 8Z', paint: 'stroke' },
  ],
  "publishing": [
    { d: 'M4 2.2h5.4L12.8 5.6v8.2H4z', paint: 'stroke' },
    { d: 'M9.2 2.4V5.7h3.4', paint: 'stroke' },
  ],
  "accessibility": [
    { d: 'M4.2 6.4h7.6M8 6.4v3.7M8 10.1l-2.3 3.7M8 10.1l2.3 3.7', paint: 'stroke' },
    { d: 'M9.7 3.5C9.7 4.4389 8.9389 5.2 8 5.2C7.0611 5.2 6.3 4.4389 6.3 3.5C6.3 2.5611 7.0611 1.8 8 1.8C8.9389 1.8 9.7 2.5611 9.7 3.5Z', paint: 'stroke' },
  ],
  "security": [
    { d: 'M8 1.9 13.4 3.9V8c0 3.4-2.4 5.4-5.4 6.4C5 13.4 2.6 11.4 2.6 8V3.9z', paint: 'stroke' },
  ],
  "organisation": [
    { d: 'M4.2 2.2v11.6', paint: 'stroke' },
    { d: 'M4.2 3.1h8l-2.3 2.4 2.3 2.4h-8', paint: 'stroke' },
  ],
};

/**
 * The three severity icons, keyed by **the engine's own severity values**:
 * `error`, `warning`, `info`. There is no fourth tier — an invented severity
 * would be a claim the tool cannot source. `info` is the value findings carry;
 * the report presents it to readers as NOTE (`lib/report.mjs` `severityKind`),
 * so the artwork the mockup labelled `note` is keyed `info` here.
 *
 * Order matters within an icon: a `white` shape knocks a mark out of a shape
 * drawn before it, so it must never be reordered.
 */
export const SEVERITY_ICONS = {
  "error": [
    { d: 'M8 1.6 15 13.6H1z', paint: 'fill' },
    { d: 'M8 5.6v3.6M8 10.6v1.2', paint: 'stroke', colour: 'white', w: 1.6 },
  ],
  "warning": [
    { d: 'M8 1.6 15 13.6H1z', paint: 'stroke', w: 1.6 },
    { d: 'M8 6v3.4M8 10.6v1.1', paint: 'stroke', w: 1.6 },
  ],
  "info": [
    { d: 'M14.4 8C14.4 11.5346 11.5346 14.4 8 14.4C4.4654 14.4 1.6 11.5346 1.6 8C1.6 4.4654 4.4654 1.6 8 1.6C11.5346 1.6 14.4 4.4654 14.4 8Z', paint: 'fill' },
    { d: 'M8 4.4v4.4M8 10.6v1.1', paint: 'stroke', colour: 'white', w: 1.6 },
  ],
};

/**
 * A category's shapes, or `null` when the catalogue has no icon for it.
 * `null` and not a substitute: the caller prints the category's own name and
 * code, which is what the reader needs, rather than borrowing a neighbouring
 * icon that means something else.
 */
export function categoryIcon(category) {
  return Object.hasOwn(CATEGORY_ICONS, category) ? CATEGORY_ICONS[category] : null;
}

/**
 * A severity's shapes.
 *
 * An unrecognised severity gets the generic `info` artwork rather than `null`:
 * `lib/report.mjs` `severityKind` presents `info` and anything unexpected as a
 * note, so every finding has exactly one presentation tier and an odd value
 * never borrows an icon that means error or warning. This mirrors that
 * existing fallback rather than inventing a fourth one.
 */
export function severityIcon(severity) {
  return Object.hasOwn(SEVERITY_ICONS, severity) ? SEVERITY_ICONS[severity] : SEVERITY_ICONS.info;
}

// ---------------------------------------------------------------------------
// Path data -> absolute geometry
// ---------------------------------------------------------------------------

/** Commands the artwork uses. Anything else fails loudly rather than silently. */
const SUPPORTED = new Set(['M', 'L', 'H', 'V', 'C', 'S', 'Z', 'm', 'l', 'h', 'v', 'c', 's', 'z']);

/** Split path data into command letters and numbers. */
function tokenize(d) {
  const out = [];
  let i = 0;
  while (i < d.length) {
    const c = d[i];
    if (/[A-Za-z]/.test(c)) { out.push(c); i += 1; continue; }
    if (/[\s,]/.test(c)) { i += 1; continue; }
    const m = /^-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/.exec(d.slice(i));
    if (!m) throw new Error(`icon path: unexpected character ${JSON.stringify(c)} at ${i}`);
    out.push(Number(m[0]));
    i += m[0].length;
  }
  return out;
}

/**
 * Path data as absolute move, line and cubic operations in icon space.
 *
 * Relative commands, horizontal and vertical shorthand, and the smooth cubic
 * `s`/`S` are all resolved here, so a renderer never has to think about them.
 * A smooth cubic reflects the previous curve's second control point about the
 * current point; when the previous operation was not a curve it has nothing to
 * reflect and starts from the current point, which is what SVG specifies.
 *
 * @param {string} d  SVG path data
 * @returns {Array<{op: 'M'|'L'|'C'|'Z'}>} absolute operations
 */
export function pathOps(d) {
  const tk = tokenize(d);
  const ops = [];
  let i = 0;
  let cmd = null;
  let cx = 0; let cy = 0;   // current point
  let sx = 0; let sy = 0;   // subpath start, for closepath
  let c2 = null;            // last curve's second control point, for smooth

  const num = () => {
    if (i >= tk.length || typeof tk[i] !== 'number') {
      throw new Error(`icon path: ${cmd} ran out of numbers`);
    }
    const v = tk[i];
    i += 1;
    return v;
  };

  while (i < tk.length) {
    if (typeof tk[i] === 'string') { cmd = tk[i]; i += 1; }
    else if (cmd === null) throw new Error('icon path: data begins with a number');

    if (!SUPPORTED.has(cmd)) throw new Error(`icon path: unsupported command ${JSON.stringify(cmd)}`);

    const rel = cmd !== cmd.toUpperCase();
    const C = cmd.toUpperCase();

    if (C === 'Z') {
      if (i < tk.length && typeof tk[i] === 'number') {
        throw new Error('icon path: a command must follow closepath');
      }
      ops.push({ op: 'Z' });
      cx = sx; cy = sy;
      c2 = null;
      continue;
    }

    if (C === 'M') {
      const x = num(); const y = num();
      cx = rel ? cx + x : x;
      cy = rel ? cy + y : y;
      sx = cx; sy = cy;
      ops.push({ op: 'M', x: cx, y: cy });
      c2 = null;
      // Further coordinate pairs after a moveto are implicit linetos.
      cmd = rel ? 'l' : 'L';
    } else if (C === 'L') {
      const x = num(); const y = num();
      cx = rel ? cx + x : x;
      cy = rel ? cy + y : y;
      ops.push({ op: 'L', x: cx, y: cy });
      c2 = null;
    } else if (C === 'H') {
      const x = num();
      cx = rel ? cx + x : x;
      ops.push({ op: 'L', x: cx, y: cy });
      c2 = null;
    } else if (C === 'V') {
      const y = num();
      cy = rel ? cy + y : y;
      ops.push({ op: 'L', x: cx, y: cy });
      c2 = null;
    } else if (C === 'C') {
      const ax = num(); const ay = num();
      const bx = num(); const by = num();
      const ex = num(); const ey = num();
      const x1 = rel ? cx + ax : ax;
      const y1 = rel ? cy + ay : ay;
      const x2 = rel ? cx + bx : bx;
      const y2 = rel ? cy + by : by;
      const x3 = rel ? cx + ex : ex;
      const y3 = rel ? cy + ey : ey;
      ops.push({ op: 'C', x1, y1, x2, y2, x: x3, y: y3 });
      cx = x3; cy = y3;
      c2 = { x: x2, y: y2 };
    } else {
      // Smooth cubic: reflect the previous curve's control point, or start at
      // the current point when there is no previous curve to reflect.
      const bx = num(); const by = num();
      const ex = num(); const ey = num();
      const x1 = c2 ? 2 * cx - c2.x : cx;
      const y1 = c2 ? 2 * cy - c2.y : cy;
      const x2 = rel ? cx + bx : bx;
      const y2 = rel ? cy + by : by;
      const x3 = rel ? cx + ex : ex;
      const y3 = rel ? cy + ey : ey;
      ops.push({ op: 'C', x1, y1, x2, y2, x: x3, y: y3 });
      cx = x3; cy = y3;
      c2 = { x: x2, y: y2 };
    }
  }
  return ops;
}

// ---------------------------------------------------------------------------
// Renderers
// ---------------------------------------------------------------------------

/** Fixed to three decimals: enough for point coordinates, and always the same. */
const num = (v) => {
  const r = Number(v.toFixed(3));
  return String(Object.is(r, -0) ? 0 : r);
};

const WHITE = [1, 1, 1];

const paintValue = (shape) => {
  if (shape.colour === 'white') return '#ffffff';
  return 'currentColor';
};

const escape = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/**
 * An icon as inline SVG for the HTML report.
 *
 * Every shape carries its own fill and stroke attributes rather than inheriting
 * from a wrapper, so an icon is self-contained wherever it is dropped and the
 * white knockouts stay white. The icon is hidden from assistive technology
 * unless the caller passes a label, because a decorated icon beside a word must
 * not be announced twice.
 *
 * No xmlns declaration: the report is `<!DOCTYPE html>` and the HTML parser
 * puts an inline `<svg>` in the SVG namespace itself, so the attribute buys
 * nothing. What it would cost is an absolute http URI in a document whose own
 * rule is that outside the sources appendix no http(s) address may appear —
 * the same rule that keeps the file from reaching for anything.
 *
 * @param {object[]} shapes  from `categoryIcon` or `severityIcon`
 * @param {{size?: number, className?: string, label?: string}} [opts]
 * @returns {string}
 */
export function svgIcon(shapes, opts = {}) {
  const { size, className, label } = opts;
  const head = [
    '<svg',
    'viewBox="0 0 16 16"',
    label ? 'role="img"' : 'aria-hidden="true"',
    size ? `width="${num(size)}" height="${num(size)}"` : '',
    className ? `class="${escape(className)}"` : '',
  ].filter(Boolean).join(' ');

  const body = shapes.map((s) => {
    const stroked = s.paint === 'stroke';
    const stroke = stroked ? paintValue(s) : 'none';
    const fill = stroked ? 'none' : paintValue(s);
    const strokeAttrs = stroked
      ? ` stroke-width="${strokeWidth(s)}" stroke-linecap="round" stroke-linejoin="round"`
      : '';
    return `<path d="${escape(s.d)}" fill="${fill}" stroke="${stroke}"${strokeAttrs}/>`;
  }).join('');

  const title = label ? `<title>${escape(label)}</title>` : '';
  return `${head}>${title}${body}</svg>`;
}

/**
 * An icon as PDF path operators, for the report PDF.
 *
 * The icon box's **bottom-left** is `x`, `y`: PDF user space runs y upwards and
 * the icon's own coordinate system runs downwards, so each point is flipped
 * about the box and scaled into place. The whole icon is wrapped in `q`/`Q`,
 * so a caller cannot leak line width or colour into the page furniture that
 * follows it.
 *
 * Only drawing operators appear — no fonts, no text, nothing WinAnsi has to
 * encode — which is what keeps the artwork intact in the PDF.
 *
 * @param {object[]} shapes  from `categoryIcon` or `severityIcon`
 * @param {{x: number, y: number, size: number, colour?: number[]}} opts
 * @returns {string}
 */
export function pdfIcon(shapes, opts = {}) {
  const { x = 0, y = 0, size = ICON_BOX, colour = [0, 0, 0] } = opts;
  if (!Number.isFinite(x) || !Number.isFinite(y) || !Number.isFinite(size) || size <= 0) {
    throw new Error(`pdfIcon: bad placement ${JSON.stringify({ x, y, size })}`);
  }

  const f = size / ICON_BOX;
  const X = (u) => x + u * f;
  const Y = (v) => y + (ICON_BOX - v) * f;

  const lines = ['q', '1 J', '1 j'];
  for (const s of shapes) {
    let base = colour;
    if (s.colour === 'white') base = WHITE;
    const rgb = base.map(num).join(' ');
    const path = [];
    for (const op of pathOps(s.d)) {
      if (op.op === 'M') path.push(`${num(X(op.x))} ${num(Y(op.y))} m`);
      else if (op.op === 'L') path.push(`${num(X(op.x))} ${num(Y(op.y))} l`);
      else if (op.op === 'Z') path.push('h');
      else path.push(
        `${num(X(op.x1))} ${num(Y(op.y1))} ${num(X(op.x2))} ${num(Y(op.y2))} `
        + `${num(X(op.x))} ${num(Y(op.y))} c`,
      );
    }
    if (s.paint === 'fill') lines.push(`${rgb} rg`, ...path, 'f');
    else lines.push(`${rgb} RG`, `${num(strokeWidth(s) * f)} w`, ...path, 'S');
  }
  lines.push('Q');
  return lines.join('\n');
}
