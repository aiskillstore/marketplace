#!/usr/bin/env node
/*
 * refresh-component-tokens.js — regenerate references/component-tokens.md
 *
 * m3.material.io publishes most per-component measurements only inside images, and its token tables
 * load from a design-system service that refresh-m3.js cannot reach. The same values are generated
 * into the androidx Compose source as plain Kotlin, so that is what this reads.
 *
 * Fetches every *Tokens.kt from androidx-main, keeps the geometry declarations (dp / sp / shape key /
 * elevation level / bare opacity floats), drops the colour and typography key-token rows, and writes a
 * grouped markdown reference mirroring references/components/*.md.
 *
 * Usage:  node scripts/refresh-component-tokens.js [outFile]
 *         default outFile = ../references/component-tokens.md relative to this script
 */
'use strict';
const fs = require('fs');
const path = require('path');
const https = require('https');

const DIR = 'compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens';
const RAW = `https://raw.githubusercontent.com/androidx/androidx/androidx-main/${DIR}/`;
const API = `https://api.github.com/repos/androidx/androidx/contents/${DIR}?ref=androidx-main`;

// Covered by references/tokens.md, or bulk colour/type data we don't want as raw values.
const SKIP = new Set([
  'ColorDarkTokens.kt', 'ColorLightTokens.kt', 'PaletteTokens.kt', 'ColorSchemeKeyTokens.kt',
  'TypographyTokens.kt', 'TypeScaleTokens.kt', 'TypefaceTokens.kt', 'TypographyKeyTokens.kt',
  'ShapeTokens.kt', 'ShapeKeyTokens.kt', 'ElevationTokens.kt', 'MotionTokens.kt',
  'ExpressiveMotionTokens.kt', 'StandardMotionTokens.kt', 'MotionSchemeKeyTokens.kt',
]);

const FAMILIES = [
  ['Buttons', 'components/buttons.md', [
    'BaselineButton', 'ButtonXSmall', 'ButtonSmall', 'ButtonMedium', 'ButtonLarge', 'ButtonXLarge',
    'FilledButton', 'FilledTonalButton', 'TonalButton', 'ElevatedButton', 'OutlinedButton', 'TextButton',
    'ButtonGroupSmall', 'ConnectedButtonGroupSmall',
    'SplitButtonXSmall', 'SplitButtonSmall', 'SplitButtonMedium', 'SplitButtonLarge', 'SplitButtonXLarge',
    'IconButton', 'XSmallIconButton', 'SmallIconButton', 'MediumIconButton', 'LargeIconButton', 'XLargeIconButton',
    'FilledIconButton', 'FilledTonalIconButton', 'OutlinedIconButton', 'OutlinedSegmentedButton',
  ]],
  ['FABs', 'components/fabs.md', [
    'FabBaseline', 'FabSmall', 'FabMedium', 'FabLarge', 'FabPrimaryContainer', 'FabSecondaryContainer',
    'ExtendedFabPrimary', 'ExtendedFabSmall', 'ExtendedFabMedium', 'ExtendedFabLarge', 'FabMenuBaseline',
  ]],
  ['Navigation', 'components/navigation.md', [
    'NavigationBar', 'NavigationBarHorizontalItem', 'NavigationBarVerticalItem',
    'NavigationRailCollapsed', 'NavigationRailExpanded', 'NavigationRailBaselineItem',
    'NavigationRailHorizontalItem', 'NavigationRailVerticalItem',
    'NavigationDrawer', 'PrimaryNavigationTab', 'SecondaryNavigationTab',
  ]],
  ['App bars and toolbars', 'components/bars.md', [
    'AppBar', 'AppBarSmall', 'AppBarMedium', 'AppBarMediumFlexible', 'AppBarLarge', 'AppBarLargeFlexible',
    'BottomAppBar', 'DockedToolbar', 'FloatingToolbar',
  ]],
  ['Containment', 'components/containment.md', [
    'FilledCard', 'ElevatedCard', 'OutlinedCard',
    'List', 'ExpandedList', 'ReorderList', 'RevealList',
    'Divider', 'SheetBottom', 'DragHandle', 'Dialog',
  ]],
  ['Input and selection', 'components/input.md', [
    'Checkbox', 'RadioButton', 'Switch', 'Slider',
    'Chips', 'AssistChip', 'FilterChip', 'InputChip', 'SuggestionChip',
    'FilledTextField', 'OutlinedTextField', 'FilledAutocomplete', 'OutlinedAutocomplete',
    'SearchBar', 'SearchView',
  ]],
  ['Feedback and overlays', 'components/feedback.md', [
    'Badge', 'ProgressIndicator', 'LinearProgressIndicator', 'CircularProgressIndicator', 'LoadingIndicator',
    'Snackbar', 'PlainTooltip', 'RichTooltip',
    'Menu', 'StandardMenu', 'VibrantMenu', 'SegmentedMenu',
    'DatePickerModal', 'DateInputModal', 'TimePicker', 'TimeInput',
  ]],
  ['Interaction states', 'interaction.md', ['State', 'Scrim']],
];

function get(url) {
  return new Promise((res, rej) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0', Accept: 'application/vnd.github+json' } }, r => {
      if (r.statusCode !== 200) { r.resume(); return rej(new Error('HTTP ' + r.statusCode + ' ' + url)); }
      let b = ''; r.setEncoding('utf8'); r.on('data', c => b += c); r.on('end', () => res(b));
    }).on('error', rej);
  });
}
async function pool(items, fn, conc = 12) {
  let i = 0;
  await Promise.all(Array.from({ length: Math.min(conc, items.length) }, async () => {
    while (i < items.length) await fn(items[i++]);
  }));
}

// `val X = 12.0.dp` / `const val X = 0.16f` / `val X = ShapeKeyTokens.CornerFull`
const DECL = /^\s*(?:const\s+)?val\s+([A-Za-z0-9]+)\s*=\s*(.+)$/;
const GEOM = /\.dp\b|\.sp\b|ShapeKeyTokens\.|ElevationTokens\.|^\d+(\.\d+)?f?$/;

function extract(src) {
  const version = (src.match(/\/\/ VERSION: ?(\S+)/) || [, '?'])[1];
  const rows = [];
  for (const line of src.split('\n')) {
    const m = line.match(DECL);
    if (!m) continue;
    const val = m[2].trimEnd();
    if (!GEOM.test(val)) continue;   // skips ColorSchemeKeyTokens.* / TypographyKeyTokens.* rows
    rows.push({
      name: m[1],
      val: val.replace(/^ElevationTokens\./, 'elevation ').replace(/^ShapeKeyTokens\./, 'shape '),
    });
  }
  return { version, rows };
}

(async () => {
  const out = process.argv[2] || path.join(__dirname, '..', 'references', 'component-tokens.md');

  const listing = JSON.parse(await get(API));
  if (!Array.isArray(listing)) throw new Error('GitHub listing failed (rate limit?): ' + JSON.stringify(listing).slice(0, 200));
  const files = listing.filter(x => x.name.endsWith('Tokens.kt') && !SKIP.has(x.name)).map(x => x.name);
  console.error('token files to read: ' + files.length);

  const byName = {};
  let fail = 0;
  await pool(files, async name => {
    try { byName[name.replace(/Tokens\.kt$/, '')] = extract(await get(RAW + name)); }
    catch (e) { fail++; console.error('  fail ' + name + ': ' + e.message); }
  });

  const L = [];
  L.push('# Component token geometry');
  L.push('');
  L.push('Every dp/sp measurement, shape assignment, and elevation level for M3 components, from the');
  L.push('**generated `androidx.compose.material3.tokens` files** (the `md.comp.*` token set expressed in');
  L.push('Kotlin). Use this when `components/*.md` records a measurement as a gap — m3.material.io publishes');
  L.push('many of these only inside images, so this is the machine-readable source for them.');
  L.push('');
  L.push('**Provenance matters.** These are the *Compose* token values. They are authoritative for');
  L.push('implementation and match the guidelines where the guidelines state a number, but a value here is');
  L.push('not the same as a value quoted on m3.material.io. When it matters, say "per the Compose M3 tokens"');
  L.push('rather than "per the M3 guidelines". Each group carries the generator VERSION stamp it came from —');
  L.push('different components are generated from different token versions, which is normal.');
  L.push('');
  L.push('Shape values are scale steps, not numbers. Resolve them with the corner radius scale in');
  L.push('`tokens.md`: CornerNone 0 · ExtraSmall 4 · Small 8 · Medium 12 · Large 16 · LargeIncreased 20 ·');
  L.push('ExtraLarge 28 · ExtraLargeIncreased 32 · ExtraExtraLarge 48 · Full = fully rounded.');
  L.push('Elevation levels resolve as: Level0 0dp · Level1 1dp · Level2 3dp · Level3 6dp · Level4 8dp ·');
  L.push('Level5 12dp.');
  L.push('');
  L.push('Refresh with: `node scripts/refresh-component-tokens.js`');
  L.push('');
  L.push('---');

  const used = new Set();
  const emit = (name) => {
    const g = byName[name];
    used.add(name);
    L.push('');
    L.push('### ' + name + '  *(VERSION ' + g.version + ')*');
    L.push('');
    L.push('| Token | Value |');
    L.push('|---|---|');
    for (const r of g.rows) L.push('| `' + r.name + '` | ' + r.val + ' |');
  };

  for (const [family, ref, members] of FAMILIES) {
    const present = members.filter(m => byName[m] && byName[m].rows.length);
    if (!present.length) continue;
    L.push('');
    L.push('## ' + family);
    L.push('');
    L.push('Design guidance for these lives in `' + ref + '`.');
    present.forEach(emit);
  }

  const leftover = Object.keys(byName).filter(k => !used.has(k) && byName[k].rows.length).sort();
  if (leftover.length) {
    L.push('');
    L.push('## Other');
    L.push('');
    L.push('Not yet assigned to a family above — add them to FAMILIES in this script.');
    leftover.forEach(emit);
  }

  fs.writeFileSync(out, L.join('\n') + '\n');
  console.error(`wrote ${out} — ${used.size} groups, ${leftover.length} unassigned, ${fail} fetch failures`);
})().catch(e => { console.error('ERROR: ' + e.message); process.exit(1); });
