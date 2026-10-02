// Document furniture: the repeating header block and the three-column footer
// that frame a report, in both formats.
//
// Everything here is derived from the scan input and nothing else — no clock
// and no environment. Two runs over the same input draw the same document
// symbol, the same date line and the same footer, so a report can be diffed
// and hashed the way lib/html.mjs already promises.
//
// The shape of both is fixed by REPORT-REDESIGN-PLAN decisions D1 to D3, and
// the plan's working mockup is the spec for shape and order. The header is two
// rows, each a left cell and a right cell: the tool and its version beside the
// boundary word, then the document symbol beside the distribution marking. The
// document title and the scan's targets are cover material, not repeating
// furniture — the mockup draws them nowhere near the header, and Omar's own
// sample asks for the skills name as the top heading and nothing else.
//
// The endorsement boundary, stated once because it is a real constraint: a
// neutral credit line and UN document conventions (document symbol, date,
// distribution marking) are normal and fine. What this project must not do is
// print a masthead that makes the tool appear to speak for the United Nations
// — claim row 22 promises the report never presents itself as United Nations
// endorsement. So the header says EDITORIAL REVIEW, never UNITED NATIONS, and
// the footer credits a group of contributors, never a person, a title or an
// affiliation.
//
// The copyright year is read from the input's date rather than from the host
// clock, because a report whose footer changes with the day it was printed is
// not byte-identical to the one before it.

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

/**
 * The document title (D1).
 *
 * One constant rather than four literals: it appears as the PDF's title
 * banner, as the HTML `<h1>` and `<title>`, and nowhere else. It replaces
 * `UN Editorial Review`, which is retired everywhere it appeared — including
 * the header fallback this module used to carry, since the repeating header no
 * longer draws a title row at all.
 */
export const TITLE = 'Editorial Review Report';

/**
 * The repository address printed in the footer's right cell (D3).
 *
 * Deliberately the bare host-and-path form, with no scheme: it reads the same
 * in print and in the terminal, and neither format turns it into a link the
 * other cannot follow.
 */
export const REPOSITORY = 'github.com/ahaomar/un-editorial-check';

/**
 * ISO date (`2026-09-28`) to `28 September 2026`.
 *
 * A fixed month table rather than `toLocaleDateString`: locale and ICU data
 * differ between machines, and a report whose date line changes with the host
 * is not byte-identical to the one before it.
 *
 * Anything that is not an ISO date passes through untouched, so a hand-built
 * input cannot be silently turned into an invented date.
 */
export function formatDate(iso) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ''));
  if (!match) return String(iso || '');
  const month = MONTHS[Number(match[2]) - 1];
  if (!month) return String(iso);
  return `${Number(match[3])} ${month} ${match[1]}`;
}

function fnv1a(text) {
  let hash = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash >>> 0;
}

/**
 * The document symbol, `UE/<year>/<four digits>`.
 *
 * Derived from the scan date, targets and tool version, so the same scan
 * identifies the same document and two different scans do not collide. This is
 * a reference this tool assigns — it is not a United Nations registry number
 * and no sequence is read from anywhere, because the checker is offline and
 * stateless and cannot know what number came before it.
 *
 * @param {{date?: string, targets?: string[], version?: string}} input
 * @returns {string}
 */
export function documentSymbol(input) {
  const date = String((input && input.date) || '');
  const year = /^\d{4}/.exec(date) ? date.slice(0, 4) : '0000';
  const key = [
    date,
    ((input && input.targets) || []).join(' '),
    (input && input.version) || '',
  ].join('|');
  const n = String(fnv1a(key) % 10000).padStart(4, '0');
  return `UE/${year}/${n}`;
}

/**
 * The repeating header block (D2): two rows, each a left cell and a right cell.
 *
 * Row one is the tool and its version against the boundary word — Omar's own
 * sample asks for the skills name as the top heading, repeated on every page —
 * and row two is the document symbol and the scan's date against the
 * distribution marking.
 *
 * The rows are objects rather than concatenated strings because both renderers
 * must place the right cell at the right edge. A single string would push that
 * alignment into each renderer separately, which is exactly where the two
 * formats used to be able to drift apart.
 *
 * Nothing here is a title or a target. The title is `TITLE` and it lives in
 * the cover; targets are cover rows in both formats; the old fourth-row
 * fallback that produced `UN Editorial Review` when a scan had no targets is
 * gone with it, which is what decision D1 retires at this site.
 *
 * @param {{date?: string}} input
 * @param {string} [version]
 * @returns {Array<{left: string, right: string}>}
 */
export function headerRows(input, version) {
  const date = formatDate(input && input.date);
  const symbol = `Document symbol: ${documentSymbol(input)}`;
  return [
    {
      left: version ? `un-editorial-check ${version}` : 'un-editorial-check',
      right: 'EDITORIAL REVIEW',
    },
    {
      // The date is joined with a middle dot rather than a `Date:` label so
      // the line reads as one stamp; it is dropped rather than left dangling
      // when the scan carries no date, so a sparse input cannot print a
      // trailing separator.
      left: date ? `${symbol} · ${date}` : symbol,
      right: 'Distribution: General',
    },
  ];
}

/**
 * The copyright cell's text (D3).
 *
 * The year is read from the scan's own date, never from the host clock: a
 * report whose footer changed with the day it was printed would not be
 * byte-identical to the one before it, and the module's first promise is that
 * it is.
 *
 * When the date carries no four-digit year the year is omitted rather than
 * guessed. `© 0000 …` would be a claim the input does not support, and
 * reaching for the current year would reintroduce exactly the clock this
 * module is built to avoid — so the line shortens, and shortens the same way
 * every time for the same input.
 *
 * @param {string} [date]
 * @returns {string}
 */
export function copyrightLine(date) {
  const year = /(\d{4})/.exec(String(date || ''));
  return year
    ? `© ${year[1]} un-editorial-check contributors`
    : '© un-editorial-check contributors';
}

/**
 * The footer (D3): three cells, left, centre and right.
 *
 * The page numbers arrive from the renderer, which is the only place that
 * knows how many pages it drew; the year comes from the input's date; the
 * repository address is a constant. The renderer places them at the three
 * edges, so this function returns text and never coordinates.
 *
 * @param {{date?: string, page: number, pages: number}} info
 * @returns {{left: string, centre: string, right: string}}
 */
export function footerCells({ date, page, pages }) {
  return {
    left: `Page ${page} of ${pages}`,
    centre: copyrightLine(date),
    right: REPOSITORY,
  };
}
