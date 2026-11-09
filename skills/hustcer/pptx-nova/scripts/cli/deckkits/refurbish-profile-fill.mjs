#!/usr/bin/env node
import { SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { genericFallbackFor, isPlainObject } from '../../lib/refurbish/style.mjs'

const CATALOG_PATH = join(SKILL_ROOT, 'assets/deckkits/catalog.json')
const DELIVERY_READINESS = new Set(['production', 'default'])
const COMMON_STYLE_OPS = [
  'set-theme',
  'set-master',
  'set-default-text-style',
  'set-slide-background',
  'set-text-frame',
  'set-shape',
]
const MANUAL_GATES = [
  'fallback-patch-report',
  'dry-run',
  'vision-diff',
  'refurbish-audit',
  'fidelity-gate',
  'png-contact-review',
]
const NATIVE_GATES = [
  'refurbish-skin-report',
  'dry-run',
  'vision-diff',
  'refurbish-audit',
  'fidelity-gate',
  'png-contact-review',
]

const PROFILE_OVERRIDES = {
  'consulting-dark': {
    palette: {
      background: '0E2638',
      text: 'F5F2EA',
      accent: 'C8583A',
      softAccent: '15334A',
      secondary: 'AEC0CE',
      surface: '13233A',
      rule: '20435E',
    },
    fonts: {
      heading: 'Inter',
      body: 'Inter',
      label: 'Inter',
      cjk: 'PingFang SC',
    },
    titleZone: {
      placement: 'top executive header with quiet eyebrow and decision headline',
      headingStyle: 'Inter semibold, off-white, compact line height',
      labelStyle: 'Inter uppercase, secondary blue-gray',
      accentRule: 'thin copper rule or small copper label marker',
      avoid: ['oversized poster titles', 'bright full-width title bars'],
    },
    tableRemap: {
      structure: 'dense consulting benchmark table on dark evidence panel',
      headerFill: 'palette.softAccent',
      headerText: 'palette.text',
      bodyFill: 'palette.surface',
      borderColor: 'palette.rule',
      emphasis: 'use palette.accent only for winning cells, deltas, or callout rows',
      rules: [
        'Keep table geometry and row count from the source deck.',
        'Use tight Inter body text and muted secondary labels for sources or units.',
        'Prefer thin internal rules over heavy boxed cells.',
      ],
    },
    chartRemap: {
      structure: 'compact data-first chart on dark surface panel',
      backgroundFill: 'palette.surface',
      primarySeries: 'palette.accent',
      secondarySeries: 'palette.secondary',
      axisColor: 'palette.secondary',
      gridColor: 'palette.rule',
      rules: [
        'Keep native chart data and chart type unchanged unless the source is non-editable.',
        'Use warm accent only for the key series or highlighted bar.',
        'Keep labels concise and put interpretation in the title zone or callout.',
      ],
    },
  },
  'mckinsey-blue': {
    palette: {
      background: 'FFFFFF',
      text: '0F172A',
      accent: '005587',
      softAccent: 'EFF6FF',
      secondary: '475569',
      surface: 'F8FAFC',
      rule: 'CBD5E1',
    },
    fonts: {
      heading: 'Arial',
      body: 'Arial',
      label: 'Arial',
      cjk: 'Arial',
    },
    chromePolicy: 'replace-or-restyle-existing',
    titleZone: {
      placement: 'top boardroom header with blue subtitle bar',
      headingStyle: 'Arial bold, dark navy, implication-led sentence case',
      labelStyle: 'Arial uppercase, medium blue or slate',
      accentRule: 'deep blue title bar with narrow cyan accent when subtitle exists',
      avoid: ['poster typography', 'playful badges', 'decorative image headers'],
    },
    tableRemap: {
      structure: 'white consulting matrix with blue header and light grid',
      headerFill: 'palette.accent',
      headerText: 'palette.background',
      bodyFill: 'palette.surface',
      borderColor: 'palette.rule',
      emphasis: 'use medium blue for priority cells and muted green/red only for semantic deltas',
      rules: [
        'Preserve analytical row and column structure.',
        'Use compact Arial text and clear source or assumption notes below the table.',
        'Avoid rounded card-heavy table treatments.',
      ],
    },
    chartRemap: {
      structure: 'quiet boardroom chart with blue hierarchy',
      backgroundFill: 'palette.background',
      primarySeries: 'palette.accent',
      secondarySeries: 'palette.secondary',
      axisColor: 'palette.secondary',
      gridColor: 'palette.rule',
      rules: [
        'Keep chart type and data series stable for auditability.',
        'Use blue for the main proof series and slate for baselines.',
        'Keep legends, axes, and notes compact rather than decorative.',
      ],
    },
  },
  broadside: {
    palette: {
      background: '111111',
      text: 'F0ECE5',
      accent: 'E85D26',
      softAccent: '331D14',
      secondary: 'B8B8AE',
      surface: '1A1A18',
      rule: '282826',
    },
    fonts: {
      heading: 'Barlow',
      body: 'Barlow',
      label: 'IBM Plex Mono',
      cjk: 'Noto Sans SC',
    },
    titleZone: {
      placement: 'poster-scale typographic block, usually left or low on the page',
      headingStyle: 'Barlow 900 lowercase, oversized, tight and flat',
      labelStyle: 'IBM Plex Mono uppercase catalogue label',
      accentRule: '1px rule or slash label, never a glossy title bar',
      avoid: ['cream paper slides', 'multi-color title badges', 'rounded title cards'],
    },
    tableRemap: {
      structure: 'editorial ledger or manifesto list rather than spreadsheet-like table',
      headerFill: 'palette.background',
      headerText: 'palette.accent',
      bodyFill: 'palette.background',
      borderColor: 'palette.rule',
      emphasis: 'use fire orange for payoff cells or one comparison column only',
      rules: [
        'Convert dense tables into flat ledgers with mono labels when possible.',
        'Use slash bullets and thin rules as table chrome.',
        'Keep cell backgrounds flat and avoid alternating multicolor bands.',
      ],
    },
    chartRemap: {
      structure: 'flat editorial chart with one orange proof gesture',
      backgroundFill: 'palette.background',
      primarySeries: 'palette.accent',
      secondarySeries: 'palette.secondary',
      axisColor: 'palette.secondary',
      gridColor: 'palette.rule',
      rules: [
        'Use orange for the dominant series or payoff panel only.',
        'Reduce grid and legend chrome to mono labels and thin rules.',
        'Prefer large labels and direct annotation over small decorative legends.',
      ],
    },
  },
  'long-table': {
    palette: {
      background: 'FAF1E2',
      text: 'B53D2A',
      accent: '8E2D1F',
      softAccent: 'F2E5CF',
      secondary: 'DEC0A5',
      surface: 'FAF1E2',
      rule: 'DEC0A5',
    },
    fonts: {
      heading: 'Bricolage Grotesque',
      body: 'Fraunces',
      label: 'Fraunces',
      cjk: 'Microsoft YaHei',
    },
    titleZone: {
      placement: 'warm editorial title with optional edition badge or small right metadata',
      headingStyle: 'Bricolage Grotesque bold, oversized, rust ink',
      labelStyle: 'Fraunces small serif metadata',
      accentRule: 'thin rust rule, badge outline, or menu divider',
      avoid: ['stock food photo headers', 'SaaS cards', 'blue corporate title bars'],
    },
    tableRemap: {
      structure: 'menu ledger or calendar row system on warm paper',
      headerFill: 'palette.softAccent',
      headerText: 'palette.text',
      bodyFill: 'palette.background',
      borderColor: 'palette.secondary',
      emphasis: 'use deep rust for section labels, prices, or selected row markers',
      rules: [
        'Prefer row ledgers and menu sections over boxed spreadsheet grids.',
        'Use thin rust dividers and serif metadata for units or dates.',
        'Keep body copy short and editorial; dense data belongs in menu/calendar rows.',
      ],
    },
    chartRemap: {
      structure: 'simple editorial bar or count ledger in rust ink',
      backgroundFill: 'palette.background',
      primarySeries: 'palette.accent',
      secondarySeries: 'palette.secondary',
      axisColor: 'palette.text',
      gridColor: 'palette.secondary',
      rules: [
        'Use charts sparingly; favor menu-style ledgers when data is categorical.',
        'Keep all marks flat rust or soft paper tones.',
        'Avoid multi-color infographic palettes.',
      ],
    },
  },
  'biennale-yellow': {
    palette: {
      background: 'E9E5DB',
      text: '1B2566',
      accent: 'F1EE2E',
      softAccent: 'F8F39B',
      secondary: 'E26B4A',
      surface: 'DCD6C4',
      rule: '1B2566',
    },
    fonts: {
      heading: 'Times New Roman',
      body: 'Arial',
      label: 'Courier New',
      cjk: 'Microsoft YaHei',
    },
    titleZone: {
      placement: 'large editorial serif title on warm paper with mono page chrome',
      headingStyle: 'Times New Roman large, ink blue, generous line height',
      labelStyle: 'Courier New mono metadata for dates, page numbers, and strands',
      accentRule: 'solar yellow block, translucent tile, or thin ink rule',
      avoid: ['rounded cards', 'decorative icons', 'bitmap image headers'],
    },
    tableRemap: {
      structure: 'institutional ledger with hairline ink rules and yellow markers',
      headerFill: 'palette.surface',
      headerText: 'palette.text',
      bodyFill: 'palette.background',
      borderColor: 'palette.rule',
      emphasis: 'use solar yellow as a row marker or header plane, not colored body text',
      rules: [
        'Preserve editable rows and columns while reducing visual noise.',
        'Use Arial for compact body cells and Courier New for dates or codes.',
        'Keep separators thin and low-contrast except for structural ink rules.',
      ],
    },
    chartRemap: {
      structure: 'editable native bar/data block with solar yellow emphasis',
      backgroundFill: 'palette.background',
      primarySeries: 'palette.accent',
      secondarySeries: 'palette.secondary',
      axisColor: 'palette.text',
      gridColor: 'palette.surface',
      rules: [
        'Use yellow as plane or bar emphasis and keep labels ink blue.',
        'Keep atmospheric ember only for soft bloom shapes, not chart series.',
        'Avoid multi-color infographic palettes and decorative chart frames.',
      ],
    },
  },
}

const usage = `Usage:
  node <skill-root>/scripts/cli/deckkits/refurbish-profile-fill.mjs [options]

Options:
  --catalog <path>     DeckKit catalog path. Defaults to <skill-root>/assets/deckkits/catalog.json
  --deckkit <id>       Limit to one DeckKit. May be repeated or comma-separated.
  --write              Persist generated refurbishProfile entries. Defaults to dry run.
  --overwrite          Replace existing refurbishProfile entries for selected DeckKits.
  --check              Fail when selected production/default DeckKits lack refurbishProfile.
  --json               Print machine-readable output.
  --help               Show this help

Examples:
  node <skill-root>/scripts/cli/deckkits/refurbish-profile-fill.mjs --json
  node <skill-root>/scripts/cli/deckkits/refurbish-profile-fill.mjs --write --json
  node <skill-root>/scripts/cli/deckkits/refurbish-profile-fill.mjs --deckkit broadside --write --json
`

function parseArgs(argv) {
  const args = {
    catalog: CATALOG_PATH,
    deckkits: [],
    write: false,
    overwrite: false,
    check: false,
    json: false,
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--write') {
      args.write = true
    } else if (arg === '--overwrite') {
      args.overwrite = true
    } else if (arg === '--check') {
      args.check = true
    } else if (arg === '--catalog') {
      args.catalog = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--deckkit') {
      pushDeckkits(args, valueAfter(argv, i, arg))
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  if (args.check && args.write) throw new Error('--check cannot be combined with --write')
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function pushDeckkits(args, value) {
  for (const item of value.split(',')) {
    const id = item.trim()
    if (id) args.deckkits.push(id)
  }
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function writeJson(path, value) {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function nativeSkinningFor(entry) {
  const native = entry?.nativeSkinning
  const supported = Boolean(native?.themePack && native?.stylePack && native?.chromeSource)
  return {
    supported,
    themePack: native?.themePack ?? '',
    stylePack: native?.stylePack ?? '',
    commands: supported ? ['refurbish-skin', 'chrome-apply', 'remap-theme'] : [],
  }
}

function fallbackFor(entry, nativeSkinning) {
  const generic = genericFallbackFor(entry)
  const override = PROFILE_OVERRIDES[entry.id] ?? {}
  const palette = { ...generic.palette, ...(override.palette ?? {}) }
  const fonts = { ...generic.fonts, ...(override.fonts ?? {}) }
  const chromePolicy =
    override.chromePolicy ??
    (nativeSkinning.supported ? 'replace-or-restyle-existing' : 'preserve-and-restyle-existing')
  return {
    schemaVersion: 'pptx-nova-refurbish-fallback/v1',
    source: `${entry.id}-refurbish-profile`,
    strategy: `inspect-driven-${entry.id}-editable-object-restyle`,
    patchScript: 'scripts/cli/refurbish/fallback-patch.mjs',
    palette,
    fonts,
    styleOps: override.styleOps ?? COMMON_STYLE_OPS,
    chromePolicy,
    contentPolicy: 'preserve-source-slides-and-editable-objects',
    titleZone: override.titleZone ?? {
      placement: 'preserve source title geometry and restyle into DeckKit typography',
      headingStyle: fonts.heading + ' heading with palette.text',
      labelStyle: fonts.label + ' label with palette.secondary',
      accentRule: 'use palette.accent only for rule, marker, or short label emphasis',
      avoid: [
        'generic theme title bars',
        'decorative title containers unrelated to source content',
      ],
    },
    tableRemap: override.tableRemap ?? {
      structure: 'preserve native table data and restyle cells into DeckKit palette',
      headerFill: 'palette.softAccent',
      headerText: 'palette.text',
      bodyFill: 'palette.surface',
      borderColor: 'palette.rule',
      emphasis: 'use palette.accent for header, deltas, or selected cells only',
      rules: [
        'Keep source row and column semantics stable.',
        'Use DeckKit fonts and high-contrast text for all readable cells.',
        'Avoid decorative fills that obscure table data.',
      ],
    },
    chartRemap: override.chartRemap ?? {
      structure: 'preserve native chart data and restyle chart chrome into DeckKit palette',
      backgroundFill: 'palette.background',
      primarySeries: 'palette.accent',
      secondarySeries: 'palette.secondary',
      axisColor: 'palette.secondary',
      gridColor: 'palette.rule',
      rules: [
        'Keep source chart type and data series stable.',
        'Use palette.accent for the primary proof series.',
        'Keep axes, gridlines, and legends quiet and readable.',
      ],
    },
  }
}

function profileFor(entry) {
  const nativeSkinning = nativeSkinningFor(entry)
  return {
    schemaVersion: 'pptx-nova-refurbish-profile/v1',
    mode: nativeSkinning.supported ? 'native' : 'manual-fallback',
    nativeSkinning,
    fallback: fallbackFor(entry, nativeSkinning),
    requiredGates: nativeSkinning.supported ? NATIVE_GATES : MANUAL_GATES,
    notes: [
      `Generated by cli/deckkits/refurbish-profile-fill.mjs for ${entry.id}.`,
      nativeSkinning.supported
        ? 'Use native skinning first; keep the fallback profile for catalog-driven recovery without switching DeckKits.'
        : 'Use the DeckKit-specific fallback profile instead of generic visualGrammar derivation.',
      'Preserve source slides and editable objects; restyle theme colors, fonts, backgrounds, text, shapes, tables, charts, and existing page chrome.',
    ],
  }
}

function withRefurbishProfile(entry, profile) {
  const next = {}
  let inserted = false
  for (const [key, value] of Object.entries(entry)) {
    if (key === 'refurbishProfile') continue
    next[key] = value
    if (key === 'visualGrammar') {
      next.refurbishProfile = profile
      inserted = true
    }
  }
  if (!inserted) next.refurbishProfile = profile
  return next
}

function selectedEntry(entry, selected) {
  return selected.size === 0 || selected.has(entry.id)
}

function buildPlan(catalog, args) {
  const selected = new Set(args.deckkits)
  const unknown = [...selected].filter((id) => !catalog.entries.some((entry) => entry.id === id))
  if (unknown.length) throw new Error(`Unknown DeckKit id(s): ${unknown.join(', ')}`)

  const results = []
  const nextEntries = catalog.entries.map((entry) => {
    if (!selectedEntry(entry, selected)) {
      results.push({ deckkit: entry.id, action: 'skipped-filter' })
      return entry
    }
    if (!DELIVERY_READINESS.has(entry.readiness)) {
      results.push({
        deckkit: entry.id,
        readiness: entry.readiness ?? '',
        action: 'skipped-readiness',
      })
      return entry
    }
    if (isPlainObject(entry.refurbishProfile) && !args.overwrite) {
      results.push({
        deckkit: entry.id,
        readiness: entry.readiness,
        action: 'skipped-existing',
        fallbackSource: entry.refurbishProfile?.fallback?.source ?? null,
      })
      return entry
    }

    const profile = profileFor(entry)
    const action = isPlainObject(entry.refurbishProfile) ? 'updated' : 'generated'
    results.push({
      deckkit: entry.id,
      readiness: entry.readiness,
      action: args.write ? action : `would-${action}`,
      nativeSkinning: profile.nativeSkinning,
      fallbackSource: profile.fallback.source,
      fallbackStrategy: profile.fallback.strategy,
      palette: profile.fallback.palette,
      fonts: profile.fallback.fonts,
      requiredGates: profile.requiredGates,
    })
    return args.write ? withRefurbishProfile(entry, profile) : entry
  })

  return {
    catalog: { ...catalog, entries: nextEntries },
    results,
  }
}

function summarize(results, args) {
  const considered = results.filter((item) => item.action !== 'skipped-filter')
  const missingProfiles = considered.filter(
    (item) =>
      DELIVERY_READINESS.has(item.readiness) &&
      !['skipped-existing', 'generated', 'updated', 'would-generated', 'would-updated'].includes(
        item.action,
      ),
  )
  const generated = considered.filter((item) => ['generated', 'updated'].includes(item.action))
  const planned = considered.filter((item) =>
    ['would-generated', 'would-updated'].includes(item.action),
  )
  const existing = considered.filter((item) => item.action === 'skipped-existing')
  return {
    selected: args.deckkits.length ? args.deckkits : 'all',
    considered: considered.length,
    generated: generated.length,
    planned: planned.length,
    existing: existing.length,
    missingProfiles: missingProfiles.length,
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  const catalog = readJson(args.catalog)
  if (!Array.isArray(catalog.entries)) throw new Error('catalog.entries must be an array')

  if (args.check) {
    const selected = new Set(args.deckkits)
    const selectedEntries = catalog.entries.filter((entry) => selectedEntry(entry, selected))
    const unknown = [...selected].filter((id) => !catalog.entries.some((entry) => entry.id === id))
    if (unknown.length) throw new Error(`Unknown DeckKit id(s): ${unknown.join(', ')}`)
    const missing = selectedEntries
      .filter((entry) => DELIVERY_READINESS.has(entry.readiness))
      .filter((entry) => !isPlainObject(entry.refurbishProfile))
      .map((entry) => entry.id)
    const result = {
      schemaVersion: 'pptx-nova-deckkit-refurbish-profile-fill/v1',
      status: missing.length ? 'failed' : 'passed',
      written: false,
      catalog: args.catalog,
      missing,
      summary: {
        selected: args.deckkits.length ? args.deckkits : 'all',
        missingProfiles: missing.length,
      },
    }
    if (args.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
    else if (missing.length) process.stdout.write(`Missing profiles: ${missing.join(', ')}\n`)
    else process.stdout.write('All selected delivery DeckKits have refurbishProfile.\n')
    process.exit(missing.length ? 1 : 0)
  }

  const { catalog: nextCatalog, results } = buildPlan(catalog, args)
  if (args.write) writeJson(args.catalog, nextCatalog)
  const result = {
    schemaVersion: 'pptx-nova-deckkit-refurbish-profile-fill/v1',
    status: 'success',
    written: args.write,
    overwrite: args.overwrite,
    catalog: args.catalog,
    summary: summarize(results, args),
    results,
  }
  if (args.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
  else {
    const summary = result.summary
    process.stdout.write(
      `${args.write ? 'Updated' : 'Planned'} refurbish profiles: ${summary.generated + summary.planned}\n`,
    )
  }
} catch (error) {
  process.stderr.write(`[error] ${error.message}\n`)
  process.exit(1)
}
