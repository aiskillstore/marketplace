#!/usr/bin/env node
import { SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { readFileSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { genericFallbackFor, isPlainObject, mergeFallbackFor } from '../../lib/refurbish/style.mjs'

const CATALOG_PATH = join(SKILL_ROOT, 'assets/deckkits/catalog.json')

const usage = `Usage:
  node <skill-root>/scripts/cli/refurbish/plan.mjs --deckkit <id> [options]

Options:
  --deckkit <id>       Target DeckKit id
  --source <path>      Source PPTX path used in suggested commands
  --output <path>      Candidate PPTX path used in suggested commands
  --catalog <path>     DeckKit catalog path. Defaults to <skill-root>/assets/deckkits/catalog.json
  --route <route>      auto|native|fallback. Defaults to auto
  --explicit           User explicitly named this DeckKit
  --json               Print machine-readable plan
  --help               Show this help
`

function parseArgs(argv) {
  const args = {
    deckkit: '',
    source: 'source.pptx',
    output: 'candidate.pptx',
    catalog: CATALOG_PATH,
    route: 'auto',
    explicit: false,
    json: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--explicit') {
      args.explicit = true
    } else if (arg === '--deckkit') {
      args.deckkit = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--source') {
      args.source = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--output') {
      args.output = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--catalog') {
      args.catalog = resolve(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--route') {
      args.route = valueAfter(argv, i, arg)
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.deckkit) throw new Error(`--deckkit is required.\n\n${usage}`)
  if (!['auto', 'native', 'fallback'].includes(args.route)) {
    throw new Error('--route must be one of auto|native|fallback')
  }
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

function stringArray(value) {
  return (Array.isArray(value) ? value : []).filter(
    (item) => typeof item === 'string' && item.trim(),
  )
}

function shell(value) {
  return JSON.stringify(value)
}

function nativeSkinningFor(entry) {
  const native = entry?.nativeSkinning
  if (!isPlainObject(native)) {
    return {
      supported: false,
      themePack: '',
      stylePack: '',
      chromeSource: '',
      commands: [],
    }
  }
  const supported = Boolean(native.themePack && native.stylePack && native.chromeSource)
  return {
    supported,
    themePack: native.themePack ?? '',
    stylePack: native.stylePack ?? '',
    chromeSource: native.chromeSource ?? '',
    commands: supported ? ['refurbish-skin', 'chrome-apply', 'remap-theme'] : [],
  }
}

function profileFor(entry, nativeSkinning) {
  const profile = entry?.refurbishProfile
  if (!isPlainObject(profile)) {
    const fallback = nativeSkinning.supported ? null : genericFallbackFor(entry)
    return {
      present: false,
      mode: nativeSkinning.supported ? 'native' : 'manual-fallback',
      nativeSkinning,
      fallback,
      requiredGates: defaultGates(nativeSkinning.supported),
      notes: fallback
        ? [
            'No DeckKit-specific refurbishProfile was found; use the generic inspect-driven fallback.',
          ]
        : [],
    }
  }
  const profileNative = isPlainObject(profile.nativeSkinning)
    ? {
        supported: profile.nativeSkinning.supported === true,
        themePack: profile.nativeSkinning.themePack ?? nativeSkinning.themePack,
        stylePack: profile.nativeSkinning.stylePack ?? nativeSkinning.stylePack,
        commands: stringArray(profile.nativeSkinning.commands),
      }
    : nativeSkinning
  const fallback = isPlainObject(profile.fallback)
    ? mergeFallbackFor(entry, profile.fallback)
    : profileNative.supported
      ? null
      : genericFallbackFor(entry)
  const result = {
    present: true,
    mode: profile.mode ?? (nativeSkinning.supported ? 'native' : 'manual-fallback'),
    nativeSkinning: profileNative,
    fallback,
    requiredGates: stringArray(profile.requiredGates).length
      ? stringArray(profile.requiredGates)
      : defaultGates(nativeSkinning.supported),
    notes: stringArray(profile.notes),
  }
  result.requiredGates = normalizeRequiredGates(result.requiredGates)
  return result
}

function defaultGates(nativeSupported) {
  const gates = [
    'dry-run',
    'vision-diff',
    'refurbish-audit',
    'semantic-diff',
    'fidelity-gate',
    'png-contact-review',
  ]
  return nativeSupported ? ['refurbish-skin-report', ...gates] : ['fallback-patch-report', ...gates]
}

function normalizeRequiredGates(gates) {
  const normalized = gates.filter((gate) => gate !== 'semantic-diff' && gate !== 'fidelity-gate')
  const auditIndex = normalized.indexOf('refurbish-audit')
  normalized.splice(
    auditIndex >= 0 ? auditIndex + 1 : normalized.length,
    0,
    'semantic-diff',
    'fidelity-gate',
  )
  return normalized
}

function requiredGatesForRoute(gates, usesFallback) {
  const routeGate = usesFallback ? 'fallback-patch-report' : 'refurbish-skin-report'
  const withoutRouteGate = gates.filter(
    (gate) => gate !== 'fallback-patch-report' && gate !== 'refurbish-skin-report',
  )
  return normalizeRequiredGates([routeGate, ...withoutRouteGate])
}

function buildCommands(args, entry, profile, usesFallback) {
  if (!usesFallback) {
    return [
      {
        name: 'native-refurbish-skin',
        required: true,
        command: `xdoc pptx refurbish-skin --source ${shell(args.source)} --deckkit ${shell(entry.id)} --output ${shell(args.output)} --json`,
      },
      {
        name: 'semantic-diff',
        required: true,
        command: `xdoc pptx diff --source ${shell(args.source)} --candidate ${shell(args.output)} --detail summary --json > pptx-diff.json`,
      },
    ]
  }

  const fallback = profile.fallback ?? {}
  const styleOps = stringArray(fallback.styleOps)
  return [
    {
      name: 'detect-existing-chrome',
      required: true,
      command: `xdoc pptx chrome-detect ${shell(args.source)} --json > chrome-detect.json`,
    },
    {
      name: 'generate-fallback-patch',
      required: true,
      command: `node ${shell(join(SKILL_ROOT, 'scripts/cli/refurbish/fallback-patch.mjs'))} --deckkit ${shell(entry.id)} --source ${shell(args.source)} --inspect reference-inspect.json --chrome-detect chrome-detect.json --output ${shell(args.output)} --patch patch.json --lock deck_lock.json --audit content-audit.json --map reference-map.json --json > fallback-patch-report.json`,
      notes: styleOps.length ? [`Generated patch uses ${styleOps.join(', ')}.`] : [],
    },
    {
      name: 'dry-run',
      required: true,
      command: `xdoc pptx apply -p patch.json -i ${shell(args.source)} -o ${shell(args.output)} --overwrite --dry-run --json > dry-run.json`,
    },
    {
      name: 'apply',
      required: true,
      command: `xdoc pptx apply -p patch.json -i ${shell(args.source)} -o ${shell(args.output)} --overwrite --json > apply.json`,
    },
    {
      name: 'vision-diff',
      required: true,
      command: `xdoc pptx vision-diff --source ${shell(args.source)} --candidate ${shell(args.output)} --json > vision-diff.json`,
    },
    {
      name: 'refurbish-audit',
      required: true,
      command: `xdoc pptx refurbish-audit --source ${shell(args.source)} --final ${shell(args.output)} --map reference-map.json --json > content-audit-final.json`,
    },
    {
      name: 'semantic-diff',
      required: true,
      command: `xdoc pptx diff --source ${shell(args.source)} --candidate ${shell(args.output)} --detail summary --json > pptx-diff.json`,
    },
    {
      name: 'fidelity-gate',
      required: true,
      command: `node ${shell(join(SKILL_ROOT, 'scripts/cli/review/fidelity-gate.mjs'))} --mode refurbish --source-inspect reference-inspect.json --source-pptx ${shell(args.source)} --candidate-pptx ${shell(args.output)} --reference-map reference-map.json --content-audit content-audit.json --final-audit content-audit-final.json --vision-diff vision-diff.json --layout-snapshot layout-final.json --review-evaluation review-policy-evaluation.json --json > fidelity-gate.json`,
      notes: [
        'The refurbish runner generates source/candidate layout, one review-policy evaluation, and shadow finding-analysis before this gate.',
      ],
    },
  ]
}

export function buildRefurbishPlan(args) {
  const catalog = readJson(args.catalog)
  const entry = catalog.entries.find((candidate) => candidate.id === args.deckkit)
  const blockers = []
  if (!entry) {
    blockers.push(`DeckKit "${args.deckkit}" is missing from catalog`)
    return planResult(args, null, blockers)
  }

  const requestedRoute = args.route ?? 'auto'
  if (!['auto', 'native', 'fallback'].includes(requestedRoute)) {
    throw new Error('route must be one of auto|native|fallback')
  }
  const nativeSkinning = nativeSkinningFor(entry)
  const catalogProfile = profileFor(entry, nativeSkinning)
  const selectedRoute =
    requestedRoute === 'fallback'
      ? 'fallback-patch'
      : requestedRoute === 'native'
        ? 'native-skin-first'
        : nativeSkinning.supported
          ? 'native-skin-first'
          : 'fallback-patch'
  const usesFallback = selectedRoute === 'fallback-patch'
  const selectedFallback =
    catalogProfile.fallback ?? (usesFallback ? genericFallbackFor(entry) : null)
  const profile = {
    ...catalogProfile,
    fallback: selectedFallback,
    requiredGates: requiredGatesForRoute(catalogProfile.requiredGates, usesFallback),
  }
  const readiness = entry.readiness ?? ''
  const explicitOnly = ['experimental', 'candidate'].includes(readiness)
  if (explicitOnly && !args.explicit) {
    blockers.push(
      `DeckKit "${entry.id}" readiness is "${readiness}"; pass --explicit only when the user named it`,
    )
  }
  if (selectedRoute === 'native-skin-first' && !nativeSkinning.supported) {
    blockers.push(`DeckKit "${entry.id}" does not declare native skinning support`)
  }
  if (usesFallback && !profile.fallback) {
    blockers.push(`DeckKit "${entry.id}" does not provide a refurbish fallback profile`)
  }

  const status = blockers.length
    ? 'blocked'
    : explicitOnly && args.explicit && usesFallback
      ? 'explicit-manual-fallback'
      : explicitOnly && args.explicit
        ? 'explicit-only'
        : usesFallback
          ? 'manual-fallback'
          : 'ready'
  return {
    ...planResult(args, entry, blockers),
    status,
    route: selectedRoute,
    routeSelection: {
      requested: requestedRoute,
      selected: selectedRoute,
      nativeAvailable: nativeSkinning.supported,
      fallbackAvailable: Boolean(profile.fallback),
    },
    explicitSelection: {
      requested: args.explicit,
      required: explicitOnly,
      mode: explicitOnly ? profile.mode : 'standard',
    },
    readiness,
    nativeSkinning,
    refurbishProfile: profile,
    chromePolicy:
      profile.fallback?.chromePolicy ??
      (nativeSkinning.supported ? 'replace-or-restyle-existing' : 'detect-and-restyle-existing'),
    requiredReferences: [
      ...(usesFallback
        ? [
            {
              path: 'references/create/reference-create.md',
              section: '6. Refurbish Existing Deck',
              reason: 'The selected route requires the catalog-driven fallback contract.',
            },
          ]
        : []),
      ...(explicitOnly
        ? [
            {
              path: 'references/create/deckkit-mode.md',
              section: 'Selection',
              reason: 'The explicitly selected DeckKit uses a readiness exception.',
            },
          ]
        : []),
    ],
    requiredGates: profile.requiredGates,
    commands: buildCommands(args, entry, profile, usesFallback),
  }
}

function planResult(args, entry, blockers) {
  return {
    schemaVersion: 'pptx-nova-refurbish-plan/v1',
    deckkit: args.deckkit,
    source: args.source,
    output: args.output,
    paths: {
      catalog: relative(SKILL_ROOT, args.catalog),
    },
    catalog: {
      found: Boolean(entry),
      id: entry?.id ?? '',
      path: entry?.path ?? '',
      benchmarkPassed: entry?.quality?.benchmark?.passed ?? null,
    },
    requiredReferences: entry
      ? []
      : [
          {
            path: 'references/create/deckkit-mode.md',
            section: 'Selection',
            reason: 'The requested DeckKit is missing from the catalog.',
          },
        ],
    blockers,
    status: blockers.length ? 'blocked' : 'ready',
  }
}

function printHuman(result) {
  process.stdout.write(`PPTX refurbish plan: ${result.deckkit}\n`)
  process.stdout.write(`- status: ${result.status}\n`)
  if (result.route) process.stdout.write(`- route: ${result.route}\n`)
  if (result.nativeSkinning) {
    process.stdout.write(
      `- native skinning: ${result.nativeSkinning.supported ? 'yes' : 'no'}${result.nativeSkinning.themePack ? ` theme=${result.nativeSkinning.themePack} style=${result.nativeSkinning.stylePack}` : ''}\n`,
    )
  }
  if (result.requiredGates?.length) {
    process.stdout.write(`- required gates: ${result.requiredGates.join(', ')}\n`)
  }
  for (const blocker of result.blockers) process.stdout.write(`- blocker: ${blocker}\n`)
  if (result.commands?.length) {
    process.stdout.write('- commands:\n')
    for (const command of result.commands) {
      process.stdout.write(`  - ${command.name}: ${command.command}\n`)
    }
  }
}

function main() {
  try {
    const args = parseArgs(process.argv.slice(2))
    const result = buildRefurbishPlan(args)
    if (args.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
    else printHuman(result)
    if (result.status === 'blocked') process.exit(1)
  } catch (error) {
    process.stderr.write(`[error] ${error.message}\n`)
    process.exit(1)
  }
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : ''
if (import.meta.url === invokedPath) main()
