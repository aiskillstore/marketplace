// --- report colours ------------------------------------------------------------
//
// One module, because two renderers painting the same report cannot be allowed
// to decide what "warning" looks like separately. They were: the severity
// orange is `#e07b00` in HTML and was `#e65100` in the PDF, the footer grey and
// the body text likewise. Nothing caught it, because no test compares them — a
// reader who opens both formats sees the same document twice, differently.
// `tests/palette.mjs` now counts the divergences so the list cannot grow
// quietly; each one is closed deliberately (PHASE-10-PLAN.md §6.9).
//
// Every entry is `{ pdf, html }`:
//
//   * `pdf` is the exact device-RGB string the PDF content stream carries,
//     three decimals per channel — not a colour that converts to it. That
//     matters: `0.45 0.45 0.45` round-trips through `#737373` as `0.451`, a
//     different byte in the stream, so the value is written as the writer
//     emits it.
//   * `html` is the `#rrggbb` the stylesheet interpolates.
//
// `pdf: null` marks a surface the PDF does not paint — it has no page
// background, no callout, no table header, only text, rules and banners.
//
// Palette (R1–R11 of PHASE-10-PLAN.md): Omar's navy for chrome, with body text
// at `#171b26` (17.20:1 on white) and the one meta grey darkened to `#616161`
// so the new light fills do not drop it below WCAG AA.

/** Severity marks. R2 keeps the hues; R12 aligns the one that disagreed. */
export const SEVERITY = {
  error: { pdf: '0.776 0.157 0.157', html: '#c62828' },
  // Was `0.902 0.318 0` (`#e65100`) in the PDF. R12 unified it on HTML's value,
  // because severity is a signal a reader has to recognise across formats.
  warning: { pdf: '0.878 0.482 0', html: '#e07b00' },
  note: { pdf: '0.082 0.396 0.753', html: '#1565c0' },
};

export const PALETTE = {
  // --- type -------------------------------------------------------------------
  // R6: a very dark navy-tinted near-black rather than pure black. 17.20:1 on
  // white, 15.21:1 on `#EEF1F8` — it reads as black and sits in the same hue
  // family as the chrome instead of fighting it.
  body: { pdf: '0.09 0.106 0.149', html: '#171b26' },
  // R10: darkened from `#6f6f6f`. Set at 0.72rem, and the light fills around
  // it are new — without this it lands at 4.3:1 and fails AA.
  meta: { pdf: '0.38 0.38 0.38', html: '#616161' },
  secondary: { pdf: null, html: '#4a4a4a' },
  // The footer sits on an `#EEF1F8` band, so `0.45 0.45 0.45` would measure
  // 4.11:1 against it — under AA for text at 7.5pt. Same reasoning as R10,
  // same answer: darken to `#616161`, 5.38:1. The three cells' wording, order
  // and position are untouched (R8); only the ink adapts to its ground.
  footer: { pdf: '0.38 0.38 0.38', html: '#616161' },

  // --- structure ---------------------------------------------------------------
  heading: { pdf: '0.122 0.227 0.478', html: '#1f3a7a' },
  rule: { pdf: '0.773 0.808 0.875', html: '#c5cedf' },
  border: { pdf: null, html: '#c5cedf' },
  findingBorder: { pdf: null, html: '#c5cedf' },
  emptyBorder: { pdf: null, html: '#c5cedf' },

  // --- surfaces ----------------------------------------------------------------
  // Omar's light fill. One value across the page ground, the panels, the
  // findings, the empty lanes and the table head: the old system graded five
  // barely-distinguishable warms apart, which read as inconsistency rather than
  // as hierarchy.
  page: { pdf: null, html: '#eef1f8' },
  surface: { pdf: '1 1 1', html: '#ffffff' },
  panel: { pdf: null, html: '#eef1f8' },
  finding: { pdf: null, html: '#eef1f8' },
  empty: { pdf: null, html: '#eef1f8' },
  tableHead: { pdf: null, html: '#eef1f8' },
  callout: { pdf: null, html: '#eef1f8' },
  // The callout's rule keeps its own warm accent: it is the one surface that
  // is not chrome but a quoted aside, and Omar's palette does not name a
  // colour for it.
  calloutBorder: { pdf: null, html: '#b9a05a' },
  clean: { pdf: null, html: '#e8f2e8' },
  cleanBorder: { pdf: null, html: '#7fa87f' },

  // --- the navy chrome (R7, R8) --------------------------------------------------
  // A filled band across the top of every page, with the header reversed out of
  // it in white: 11.69:1 against `#24356B`. Omar delegated the treatment; a
  // filled masthead rather than a rule because the report's header carries four
  // pieces of furniture and a rule was not holding them together.
  masthead: { pdf: '0.141 0.208 0.42', html: '#24356b' },
  // The closing rule under the masthead, and the rule above the footer band.
  // Darker than the masthead so it reads as a line rather than a shadow.
  divider: { pdf: '0.106 0.157 0.322', html: '#1b2852' },
  // The footer band. Also Omar's "light fill" for any pale surface.
  footerBand: { pdf: '0.933 0.945 0.973', html: '#eef1f8' },

  // --- marks and reversed fields ------------------------------------------------
  marker: { pdf: null, html: '#5c5850' },
  // White type sits on the marker chip and on every banner, so it is its own
  // role: the ground it sits on may change without dragging the type with it.
  onChip: { pdf: '1 1 1', html: '#ffffff' },
  // The code block inverts: dark ground, page-coloured type.
  codeGround: { pdf: null, html: '#1c1c1c' },
  codeType: { pdf: null, html: '#f4f4f2' },
  icon: { pdf: null, html: '#1d1b18' },

  severity: SEVERITY,
};

/**
 * `#rrggbb` for a PDF device-RGB string such as `'0.45 0.45 0.45'`, which is
 * how the two halves of an entry can be compared at all. Components are
 * rounded, as every PDF consumer rounds them on the way to a device value.
 */
export function pdfHex(decimal) {
  const parts = String(decimal).trim().split(/\s+/).map(Number);
  if (parts.length !== 3 || parts.some(Number.isNaN)) return null;
  return `#${parts
    .map(value => Math.max(0, Math.min(255, Math.round(value * 255))).toString(16).padStart(2, '0'))
    .join('')}`;
}

/**
 * Roles where the two renderers are not painting the same colour. Deliberately
 * a *derived* value: adding a palette entry that disagrees shows up here
 * without anyone having to remember to update a list.
 *
 * @returns {Array<[string, string, string]>} `[role, pdf hex, html hex]`
 */
export function divergences() {
  const found = [];
  for (const [role, entry] of Object.entries(PALETTE)) {
    if (role === 'severity') {
      for (const [name, value] of Object.entries(entry)) {
        const hex = pdfHex(value.pdf);
        if (hex && hex !== value.html) found.push([`severity.${name}`, hex, value.html]);
      }
      continue;
    }
    if (entry.pdf === null) continue;
    const hex = pdfHex(entry.pdf);
    if (hex && hex !== entry.html) found.push([role, hex, entry.html]);
  }
  return found;
}
