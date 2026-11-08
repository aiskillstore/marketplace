#!/usr/bin/env node
import { SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { readFileSync } from 'node:fs'
import { relative, resolve } from 'node:path'
import { normalizeVisionLowBuckets } from '../../lib/review/vision-baseline.mjs'

const CATALOG_PATH = resolve(SKILL_ROOT, 'assets/deckkits/catalog.json')
const VALID_TARGETS = ['candidate', 'delivery', 'default']
const VALID_READINESS = ['experimental', 'candidate', 'production', 'default']
const VISUAL_GRAMMAR_SCHEMA_VERSION = 'pptx-nova-visual-grammar/v1'
const REQUIRED_VISUAL_GRAMMAR_ARRAYS = [
  'mood',
  'layoutPrinciples',
  'signatureElements',
  'compositionRules',
  'avoid',
]
const REQUIRED_VISUAL_GRAMMAR_OBJECTS = ['typography', 'colorSystem', 'slideRhythm']

const usage = `Usage:
  node <skill-root>/scripts/cli/deckkits/select.mjs [options]

Options:
  --scenario <name>          Target scenario, e.g. roadshow or executive consulting
  --brief <text>             Infer a known scenario from a short brief; explicit --scenario wins
  --language <code>          Language coverage requirement, e.g. zh|en|mixed
  --density <level>          Density coverage requirement, e.g. normal|dense
  --slide-types <list>       Comma-separated required slide types
  --target <level>           candidate|delivery|default. Defaults to delivery
  --catalog <path>           Catalog path. Defaults to <skill-root>/assets/deckkits/catalog.json
  --json                     Print machine-readable selection result
  --help                     Show this help

Example:
  node <skill-root>/scripts/cli/deckkits/select.mjs \\
    --scenario roadshow \\
    --language mixed \\
    --density dense \\
    --slide-types heroSlide,multiCardSlide,benchmarkSlide,timelineSlide,askSlide \\
    --target delivery \\
    --json
`

function parseArgs(argv) {
  const args = {
    scenario: '',
    brief: '',
    language: '',
    density: '',
    slideTypes: [],
    target: 'delivery',
    catalog: CATALOG_PATH,
    json: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--scenario') {
      args.scenario = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--brief') {
      args.brief = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--language') {
      args.language = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--density') {
      args.density = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--slide-types') {
      args.slideTypes = splitList(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--target') {
      args.target = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--catalog') {
      args.catalog = resolve(valueAfter(argv, i, arg))
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!VALID_TARGETS.includes(args.target)) {
    throw new Error(`--target must be one of ${VALID_TARGETS.join('|')}`)
  }
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function splitList(value) {
  return String(value)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function normalize(value) {
  return String(value ?? '')
    .trim()
    .toLowerCase()
}

function listIncludes(values, value) {
  if (!value) return true
  const normalized = normalize(value)
  return (Array.isArray(values) ? values : []).some((item) => normalize(item) === normalized)
}

function matchWeight(values, value, weight) {
  return normalize(value) && listIncludes(values, value) ? weight : 0
}

// Topic routing only. These aliases do not select a palette or override a pinned visual brief.
const SCENARIO_ALIASES = [
  [
    'product-platform',
    [
      '产品介绍',
      '产品发布',
      '产品平台',
      'product introduction',
      'product launch',
      'product overview',
    ],
  ],
  [
    'engineering-platform',
    ['技术架构', '开发者平台', 'technical architecture', 'developer platform'],
  ],
  ['research courseware', ['研究课件', 'research courseware']],
  ['board review', ['董事会报告', 'board review']],
  ['annual report', ['年度经营汇报', 'annual report']],
]

function resolveScenario(args) {
  const explicit = normalize(args.scenario)
  const text = explicit || normalize(args.brief)
  const match = SCENARIO_ALIASES.find(([id, aliases]) =>
    explicit
      ? [id, ...aliases].includes(text)
      : [id, ...aliases].some((alias) => text.includes(alias)),
  )
  return {
    scenario: match?.[0] ?? explicit,
    scenarioSource: explicit ? 'explicit' : match ? 'brief' : 'unspecified',
  }
}

function slideTypeSet(entry) {
  const types = Array.isArray(entry.supportedSlideTypes)
    ? entry.supportedSlideTypes
    : entry.coverage?.slideTypes
  return new Set(Array.isArray(types) ? types : [])
}

function missingSlideTypes(entry, requiredSlideTypes) {
  const supported = slideTypeSet(entry)
  return requiredSlideTypes.filter((type) => !supported.has(type))
}

function qualityBlockers(entry, target) {
  if (target === 'candidate') return []

  const blockers = []
  const quality = entry.quality ?? {}
  const readiness = entry.readiness ?? ''
  const knownBlockingLimits = Array.isArray(quality.knownBlockingLimits)
    ? quality.knownBlockingLimits
    : []

  if (!['production', 'default'].includes(readiness)) {
    blockers.push(`readiness "${readiness || 'missing'}" is not eligible for delivery`)
  }
  if (!quality.lastBenchmark) blockers.push('quality.lastBenchmark is missing')
  if (quality.manualHardDefects !== 0) {
    blockers.push('quality.manualHardDefects must be 0')
  }
  if (knownBlockingLimits.length > 0) {
    blockers.push('quality.knownBlockingLimits must be empty')
  }
  if ((quality.vision?.high ?? null) !== 0 || (quality.vision?.medium ?? null) !== 0) {
    blockers.push('quality.vision high/medium must both be 0')
  }
  if (quality.benchmark?.passed !== true) blockers.push('quality.benchmark.passed must be true')
  if (
    (quality.benchmark?.vision?.high ?? 0) !== 0 ||
    (quality.benchmark?.vision?.medium ?? 0) !== 0
  ) {
    blockers.push('quality.benchmark.vision high/medium must both be 0')
  }
  const lowBuckets = normalizeVisionLowBuckets(quality.benchmark?.vision?.lowBuckets)
  if (lowBuckets.new !== 0 || lowBuckets.changed !== 0) {
    blockers.push('quality.benchmark.vision new/changed low issues must both be 0')
  }
  if ((quality.benchmark?.vision?.lowBuckets?.baselineUnavailableCases ?? 0) !== 0) {
    blockers.push('quality.benchmark.vision low baselines must be available')
  }
  if (target === 'default' && readiness !== 'default') {
    blockers.push(`readiness "${readiness || 'missing'}" is not eligible for default`)
  }
  return blockers
}

function stringArray(value) {
  return (Array.isArray(value) ? value : []).filter(
    (item) => typeof item === 'string' && item.trim(),
  )
}

function hasNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0
}

function isPlainObject(value) {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value))
}

function visualGrammarIssues(grammar) {
  const issues = []
  if (!isPlainObject(grammar)) {
    return ['visualGrammar is missing']
  }
  if (grammar.schemaVersion !== VISUAL_GRAMMAR_SCHEMA_VERSION) {
    issues.push(`visualGrammar.schemaVersion must be ${VISUAL_GRAMMAR_SCHEMA_VERSION}`)
  }
  if (!hasNonEmptyString(grammar.positioning)) {
    issues.push('visualGrammar.positioning is missing')
  }
  for (const field of REQUIRED_VISUAL_GRAMMAR_ARRAYS) {
    if (stringArray(grammar[field]).length === 0) {
      issues.push(`visualGrammar.${field} must be a non-empty string array`)
    }
  }
  for (const field of REQUIRED_VISUAL_GRAMMAR_OBJECTS) {
    if (!isPlainObject(grammar[field])) {
      issues.push(`visualGrammar.${field} must be an object`)
    }
  }
  return issues
}

function summarizeVisualGrammar(grammar) {
  if (!isPlainObject(grammar)) return null
  return {
    schemaVersion: grammar.schemaVersion ?? '',
    positioning: grammar.positioning ?? '',
    mood: stringArray(grammar.mood),
    layoutPrinciples: stringArray(grammar.layoutPrinciples),
    signatureElements: stringArray(grammar.signatureElements),
    typography: isPlainObject(grammar.typography) ? grammar.typography : {},
    colorSystem: isPlainObject(grammar.colorSystem) ? grammar.colorSystem : {},
    slideRhythm: isPlainObject(grammar.slideRhythm) ? grammar.slideRhythm : {},
    compositionRules: stringArray(grammar.compositionRules),
    avoid: stringArray(grammar.avoid),
  }
}

function readinessBlockers(entry, target) {
  const blockers = []
  const readiness = entry.readiness ?? ''
  if (!VALID_READINESS.includes(readiness)) {
    blockers.push(`readiness "${readiness || 'missing'}" is not valid`)
  }
  if (target === 'candidate' && !['candidate', 'production', 'default'].includes(readiness)) {
    blockers.push(`readiness "${readiness || 'missing'}" is not eligible for candidate`)
  }
  return blockers
}

function evaluateEntry(entry, args) {
  const blockers = []
  const warnings = []
  const missingTypes = missingSlideTypes(entry, args.slideTypes)
  const coverage = entry.coverage ?? {}
  const quality = entry.quality ?? {}
  const visualGrammar = summarizeVisualGrammar(entry.visualGrammar)
  const visualGrammarProblems = visualGrammarIssues(entry.visualGrammar)

  blockers.push(...readinessBlockers(entry, args.target))
  blockers.push(...qualityBlockers(entry, args.target))
  if (visualGrammarProblems.length > 0) {
    if (['delivery', 'default'].includes(args.target)) {
      blockers.push(...visualGrammarProblems)
    } else {
      warnings.push(...visualGrammarProblems)
    }
  }
  if (missingTypes.length > 0) {
    blockers.push(`missing slide types: ${missingTypes.join(', ')}`)
  }
  if (args.language && !listIncludes(coverage.languages, args.language)) {
    blockers.push(`language "${args.language}" is not covered`)
  }
  if (args.density && !listIncludes(coverage.density, args.density)) {
    blockers.push(`density "${args.density}" is not covered`)
  }
  if (!Array.isArray(entry.supportedSlideTypes) && !Array.isArray(coverage.slideTypes)) {
    blockers.push('supportedSlideTypes or coverage.slideTypes is missing')
  }
  if (!quality.lastBenchmark && ['production', 'default'].includes(entry.readiness)) {
    warnings.push('production/default DeckKit has no lastBenchmark')
  }

  const exactScenario = normalize(args.scenario)
  const scoreParts = {
    readiness: entry.readiness === 'default' ? 300 : entry.readiness === 'production' ? 240 : 120,
    defaultFor: matchWeight(entry.defaultFor, exactScenario, 120),
    bestFor: matchWeight(entry.bestFor, exactScenario, 80),
    language: matchWeight(coverage.languages, args.language, 40),
    density: matchWeight(coverage.density, args.density, 30),
    slideCoverage: args.slideTypes.length * 10,
    benchmark: quality.benchmark?.passed === true ? 30 : 0,
    manualReview: quality.manualHardDefects === 0 ? 30 : 0,
    recency: quality.lastBenchmark ? 10 : 0,
  }
  const score = Object.values(scoreParts).reduce((sum, item) => sum + item, 0)

  return {
    id: entry.id,
    version: entry.version ?? '',
    path: entry.path ?? '',
    readiness: entry.readiness ?? '',
    defaultFor: entry.defaultFor ?? [],
    bestFor: entry.bestFor ?? [],
    coverage: {
      languages: coverage.languages ?? [],
      density: coverage.density ?? [],
      slideTypes: coverage.slideTypes ?? entry.supportedSlideTypes ?? [],
    },
    visualGrammar,
    quality: {
      lastBenchmark: quality.lastBenchmark ?? null,
      vision: quality.vision ?? null,
      manualHardDefects: quality.manualHardDefects ?? null,
      benchmarkPassed: quality.benchmark?.passed ?? null,
      benchmarkVision: quality.benchmark?.vision ?? null,
    },
    score,
    scoreParts,
    scenarioMatched: Boolean(scoreParts.defaultFor || scoreParts.bestFor),
    missingSlideTypes: missingTypes,
    eligible: blockers.length === 0,
    blockers,
    warnings,
  }
}

function selectDeckKit(args) {
  args = { ...args, ...resolveScenario(args) }
  const catalog = readJson(args.catalog)
  const evaluated = (catalog.entries ?? []).map((entry) => evaluateEntry(entry, args))
  const ranked = evaluated
    .filter((entry) => entry.eligible)
    .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id))
  const rejected = evaluated
    .filter((entry) => !entry.eligible)
    .sort((a, b) => a.id.localeCompare(b.id))

  const selected = ranked[0] ?? null
  return {
    schemaVersion: 'pptx-nova-deckkit-selection/v1',
    passed: Boolean(selected),
    query: {
      scenario: args.scenario || null,
      scenarioSource: args.scenarioSource,
      language: args.language || null,
      density: args.density || null,
      slideTypes: args.slideTypes,
      target: args.target,
    },
    paths: {
      catalog: relative(SKILL_ROOT, args.catalog),
    },
    selected,
    warnings: !args.scenario
      ? [
          'No scenario supplied or recognized; ranking is a readiness shortlist, not an art-direction decision.',
        ]
      : !ranked.some((entry) => entry.scenarioMatched)
        ? ['No scenario match in eligible DeckKits; inspect rendered examples before choosing.']
        : [],
    ranked,
    rejected,
  }
}

function previewList(values, limit = 4) {
  const items = stringArray(values).slice(0, limit)
  return items.length > 0 ? items.join('; ') : ''
}

function printHuman(result) {
  for (const warning of result.warnings) process.stdout.write(`Warning: ${warning}\n`)
  if (result.selected) {
    process.stdout.write(`Selected DeckKit: ${result.selected.id}\n`)
    process.stdout.write(`- readiness: ${result.selected.readiness}\n`)
    process.stdout.write(`- score: ${result.selected.score}\n`)
    process.stdout.write(`- path: ${result.selected.path}\n`)
    if (result.selected.visualGrammar) {
      const grammar = result.selected.visualGrammar
      process.stdout.write(`- visual: ${grammar.positioning || 'missing'}\n`)
      const signatures = previewList(grammar.signatureElements)
      if (signatures) process.stdout.write(`- signatures: ${signatures}\n`)
      const avoid = previewList(grammar.avoid)
      if (avoid) process.stdout.write(`- avoid: ${avoid}\n`)
    }
  } else {
    process.stdout.write('No eligible DeckKit found.\n')
  }
  if (result.rejected.length > 0) {
    process.stdout.write('Rejected DeckKits:\n')
    for (const entry of result.rejected) {
      process.stdout.write(`- ${entry.id}: ${entry.blockers.join('; ')}\n`)
    }
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const result = selectDeckKit(args)
  if (args.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
  else printHuman(result)
  if (!result.passed) process.exit(1)
}

try {
  main()
} catch (error) {
  process.stderr.write(`[error] ${error.message}\n`)
  process.exit(1)
}
