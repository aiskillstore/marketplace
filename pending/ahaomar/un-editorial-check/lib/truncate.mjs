// Per-platform character preview (`--preview`).
//
// This is a counting tool, not an editorial scan: it shows how much of a file
// fits a platform's character budget and where the cut lands. The platform
// numbers are stated assumptions, documented in the README, not guarantees
// from the platforms themselves:
//   * x        — 280 characters; every link counts as 23 characters.
//   * linkedin — 3000 characters; a link counts exactly as written.
//   * bluesky  — 300 characters; a link counts exactly as written.
//   * mastodon — 500 characters; a link counts exactly as written.
//
// Tokens are split on whitespace. A token containing a link is atomic — the
// cut never lands in the middle of a URL — and everything else is cut code
// point by code point, so the preview is deterministic for a given input.

export const PLATFORMS = {
  x: { label: 'X', limit: 280, linkCost: 23 },
  linkedin: { label: 'LinkedIn', limit: 3000, linkCost: null },
  bluesky: { label: 'Bluesky', limit: 300, linkCost: null },
  mastodon: { label: 'Mastodon', limit: 500, linkCost: null },
};

const URL_RE = /https?:\/\//i;

const codePoints = (text) => [...text];
const isLink = (token) => URL_RE.test(token);

/**
 * Count and cut one file for one platform.
 *
 * @param {string} text   the file's full contents
 * @param {string} platform  one of Object.keys(PLATFORMS)
 * @returns {{platform: string, label: string, limit: number, counted: number,
 *   fits: boolean, overBy: number, preview: string, links: number,
 *   linkCharacters: number, linkCost: number|null}}
 */
export function previewTruncate(text, platform) {
  const spec = PLATFORMS[platform];
  if (!spec) throw new Error(`unknown preview platform "${platform}"`);

  // NFC first: a composed and a decomposed spelling of the same characters
  // must count alike, so the preview does not depend on how the file was typed.
  const source = String(text).normalize('NFC');
  // Even indices are tokens, odd indices are the whitespace separators between
  // them — split with a capturing group keeps the original text intact.
  const parts = source.split(/(\s+)/);

  let counted = 0;
  let links = 0;
  let linkCharacters = 0;
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    if (!part) continue;
    if (i % 2 === 1) {
      counted += codePoints(part).length;
      continue;
    }
    if (isLink(part)) {
      links += 1;
      linkCharacters += codePoints(part).length;
      counted += spec.linkCost ?? codePoints(part).length;
      continue;
    }
    counted += codePoints(part).length;
  }

  // The cut: separators are appended before the token they precede, so a
  // budget that runs out in front of a link leaves the space in place and the
  // link untouched; a plain token is cut to the remaining budget exactly.
  const budget = spec.limit;
  let used = 0;
  let out = '';
  let stopped = false;
  for (let i = 0; i < parts.length && !stopped; i++) {
    const part = parts[i];
    if (!part) continue;
    if (i % 2 === 1) {
      if (used + codePoints(part).length <= budget) {
        out += part;
        used += codePoints(part).length;
      } else {
        stopped = true;
      }
      continue;
    }
    const link = isLink(part);
    const cost = link ? (spec.linkCost ?? codePoints(part).length) : codePoints(part).length;
    if (used + cost <= budget) {
      out += part;
      used += cost;
      continue;
    }
    if (link) {
      stopped = true; // never cut a URL in half
      continue;
    }
    out += codePoints(part).slice(0, Math.max(0, budget - used)).join('');
    stopped = true;
  }

  return {
    platform,
    label: spec.label,
    limit: spec.limit,
    counted,
    fits: counted <= budget,
    overBy: Math.max(0, counted - budget),
    preview: out,
    links,
    linkCharacters,
    linkCost: spec.linkCost,
  };
}

/**
 * The pinned, user-facing rendering of a preview. Over budget is stated in
 * the text, never in the exit code: the CLI exits 0 whenever a preview is
 * produced.
 */
export function formatPreview(result, file) {
  const links = result.links === 0
    ? 'links: 0'
    : result.linkCost === null
      ? `links: ${result.links} counted as written`
      : `links: ${result.links} at ${result.linkCost} characters`;
  const lines = [
    `${result.label} preview: ${file} — limit ${result.limit} characters`,
    `counted ${result.counted}, ${result.fits ? 'fits' : `over budget by ${result.overBy}`}; ${links}`,
  ];
  if (!result.fits) {
    lines.push('--- cut to the budget ---');
    lines.push(result.preview);
  }
  lines.push('Preview only: this is not an editorial scan; exit code 0 means the preview was produced.');
  return lines.join('\n');
}
