#!/usr/bin/env node
import { SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, extname, join, resolve } from 'node:path'

const CAPABILITY_AXIS_NAMES = ['create', 'edit', 'inspect', 'preserve', 'render', 'verify']
const CAPABILITY_AXIS_STATUSES = [
  'supported',
  'partial',
  'preserve-only',
  'unsupported',
  'inconclusive',
  'skipped',
]
const CAPABILITY_AXIS_REQUIRED_IDENTITIES = [
  'slide-animation/basic-shape-and-text-builds',
  'slide-transition/morph-authoring',
]
const CAPABILITY_ENTRY_STATUSES = ['supported', 'partial', 'preserve-only', 'unsupported']

const usage = `Usage:
  node <skill-root>/scripts/cli/runtime/probe.mjs [options]

Discover the runtime xdoc capability index without turning that index into an
allowlist. A missing disclosure is reported as "undisclosed", not "unsupported".

Options:
  --xdoc-bin <path>                 xdoc executable. Defaults to xdoc.
  --output <path>                   Write the capability snapshot to this path.
  --require-command <name>          Require a top-level or pptx.<subcommand> disclosure.
  --require-op <name>               Require a patch or recipe op disclosure.
  --require-feature <feature/subset> Require a fully supported capability-truth entry.
  --require-enum <name>             Require an enum registry disclosure.
  --require-theme <id>              Require a theme pack disclosure.
  --require-style <id>              Require a style pack disclosure.
  --require-native-deckkit <id>     Require native xdoc skinning disclosure.
  --require-generator-deckkit <id>  Require bundled DeckKit generator disclosure.
  --strict                          Exit 2 when any requirement is not satisfied.
  --overwrite                       Replace an existing current-run output file.
  --json                            Print the complete JSON report to stdout.
  --help                            Show this help.

Requirement flags may be repeated or use comma-separated values.
`

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function addValues(target, value) {
  for (const item of String(value).split(',')) {
    const normalized = item.trim()
    if (normalized) target.push(normalized)
  }
}

function parseArgs(argv) {
  const args = {
    xdocBin: 'xdoc',
    output: '',
    strict: false,
    overwrite: false,
    json: false,
    requirements: {
      commands: [],
      operations: [],
      features: [],
      enums: [],
      themes: [],
      styles: [],
      nativeDeckkits: [],
      generatorDeckkits: [],
    },
  }
  const requirementFlags = {
    '--require-command': 'commands',
    '--require-op': 'operations',
    '--require-feature': 'features',
    '--require-enum': 'enums',
    '--require-theme': 'themes',
    '--require-style': 'styles',
    '--require-native-deckkit': 'nativeDeckkits',
    '--require-generator-deckkit': 'generatorDeckkits',
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--strict') {
      args.strict = true
    } else if (arg === '--overwrite') {
      args.overwrite = true
    } else if (arg === '--xdoc-bin') {
      args.xdocBin = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--output' || arg === '-o') {
      args.output = valueAfter(argv, i, arg)
      i += 1
    } else if (requirementFlags[arg]) {
      addValues(args.requirements[requirementFlags[arg]], valueAfter(argv, i, arg))
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  for (const values of Object.values(args.requirements)) {
    values.splice(0, values.length, ...[...new Set(values)])
  }
  for (const feature of args.requirements.features) {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*\/[a-z0-9]+(?:-[a-z0-9]+)*$/.test(feature)) {
      throw new Error(`--require-feature expects feature/subset, got: ${feature}`)
    }
  }
  return args
}

function run(bin, args) {
  const javascriptPath =
    ['.js', '.mjs', '.cjs'].includes(extname(bin).toLowerCase()) && existsSync(bin)
  const executable = javascriptPath ? process.execPath : bin
  const executableArgs = javascriptPath ? [bin, ...args] : args
  const result = spawnSync(executable, executableArgs, {
    encoding: 'utf8',
    maxBuffer: 32 * 1024 * 1024,
  })
  return {
    ok: !result.error && result.status === 0,
    status: result.status,
    stdout: result.stdout ?? '',
    stderr: result.stderr ?? '',
    error: result.error
      ? {
          code: result.error.code ?? 'spawn-error',
          message: result.error.message,
        }
      : null,
  }
}

function parseJson(text) {
  try {
    const value = JSON.parse(text)
    return value && typeof value === 'object' && !Array.isArray(value) ? value : null
  } catch {
    return null
  }
}

function hasFlag(helpText, flag) {
  // xdoc help declares options at two-space indentation. Descriptions,
  // continuation prose and examples can mention flags belonging to other commands.
  const declarations = /^ {2}(?:(-[A-Za-z0-9]),[ \t]+)?(--[A-Za-z0-9][A-Za-z0-9-]*)(?=\s|$)/gm
  for (const match of helpText.matchAll(declarations)) {
    if (match[1] === flag || match[2] === flag) return true
  }
  return false
}

function helpFlagIndex(bin) {
  const convertHelp = run(bin, ['convert', '--help'])
  const checkHelp = run(bin, ['check', '--help'])
  const pptxHelp = run(bin, ['pptx', '--help'])
  const fromHelp = (result, flag) => (result.ok ? hasFlag(result.stdout, flag) : null)

  return {
    convert: {
      helpAvailable: convertHelp.ok,
      jsonStdout: fromHelp(convertHelp, '--json') === true,
      reportFile: fromHelp(convertHelp, '--report') === true,
      outputFile:
        fromHelp(convertHelp, '--output') === true || fromHelp(convertHelp, '-o') === true,
      notes:
        'Top-level convert is a generic export fallback. Do not assume JSON stdout unless jsonStdout is true.',
    },
    check: {
      helpAvailable: checkHelp.ok,
      jsonStdout: fromHelp(checkHelp, '--json') === true,
      reportFile: fromHelp(checkHelp, '--report') === true,
      outputFile: fromHelp(checkHelp, '--output') === true || fromHelp(checkHelp, '-o') === true,
      notes:
        'For single-file preflight diagnostics, write the structured check result with -o/--output. --report is a batch summary when available.',
    },
    pptx: {
      helpAvailable: pptxHelp.ok,
      jsonStdout: fromHelp(pptxHelp, '--json') === true,
      previewManifest: pptxHelp.ok && pptxHelp.stdout.includes('preview'),
      notes:
        'PPTX subcommands such as preview/inspect/apply emit machine-readable stdout when --json is disclosed.',
    },
  }
}

function objectKeys(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? Object.keys(value) : []
}

function uniqueSorted(values) {
  return [...new Set(values.filter((value) => typeof value === 'string' && value))].sort()
}

function namesFromCollection(value, fields = ['op', 'name', 'id']) {
  if (Array.isArray(value)) {
    return uniqueSorted(
      value.flatMap((item) => {
        if (typeof item === 'string') return [item]
        if (!item || typeof item !== 'object') return []
        for (const field of fields) {
          if (typeof item[field] === 'string') return [item[field]]
        }
        return []
      }),
    )
  }
  return objectKeys(value).sort()
}

function idsFromCatalog(value) {
  if (Array.isArray(value)) return namesFromCollection(value, ['id', 'name'])
  if (!value || typeof value !== 'object') return []
  if (Array.isArray(value.ids)) return uniqueSorted(value.ids)
  return namesFromCollection(value.entries ?? value.items ?? value, ['id', 'name'])
}

function aliasCount(value) {
  if (Array.isArray(value)) return value.length
  return objectKeys(value).length
}

function enumIndex(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return []
  return Object.entries(value)
    .map(([name, definition]) => ({
      name,
      availability: definition?.availability ?? null,
      strict: definition?.strict ?? definition?.strictness?.strict ?? null,
      valueCount: Array.isArray(definition?.values) ? definition.values.length : null,
      aliasCount: aliasCount(definition?.aliases),
    }))
    .sort((a, b) => a.name.localeCompare(b.name))
}

function nativeDeckkitIndex(value) {
  const entries = Array.isArray(value?.deckkits) ? value.deckkits : []
  return entries
    .filter((entry) => entry && typeof entry.id === 'string')
    .map((entry) => ({
      id: entry.id,
      readiness: entry.readiness ?? null,
      themePack: entry.themePack ?? null,
      stylePack: entry.stylePack ?? null,
    }))
    .sort((a, b) => a.id.localeCompare(b.id))
}

function agentTransportIndex(commands) {
  const mcpCommand = commands?.mcp
  const mcpProtocol = mcpCommand?.protocolContract
  const jsonRpcCommand = commands?.['json-rpc']
  const protocol = jsonRpcCommand?.protocolContract
  const daemonCommand = commands?.daemon
  const mcpDisclosed =
    mcpProtocol &&
    typeof mcpProtocol === 'object' &&
    !Array.isArray(mcpProtocol) &&
    mcpProtocol.transport === 'stdio'
  const jsonRpcDisclosed =
    protocol &&
    typeof protocol === 'object' &&
    !Array.isArray(protocol) &&
    protocol.transport === 'stdio'
  const daemonDisclosed =
    daemonCommand && typeof daemonCommand === 'object' && !Array.isArray(daemonCommand)
  return {
    mcp: mcpDisclosed
      ? {
          status: 'disclosed',
          schemaVersion: mcpProtocol.schemaVersion ?? null,
          protocol: mcpProtocol.protocol ?? null,
          transport: mcpProtocol.transport,
          scope: mcpProtocol.scope ?? null,
          inputMode: mcpCommand.inputMode ?? null,
          ioContract: mcpCommand.ioContract ?? null,
          contract: mcpProtocol,
          tools: Array.isArray(mcpProtocol.tools) ? mcpProtocol.tools : [],
          usageNotes: Array.isArray(mcpCommand.usageNotes) ? mcpCommand.usageNotes : [],
        }
      : {
          status: 'undisclosed',
          schemaVersion: mcpProtocol?.schemaVersion ?? null,
        },
    jsonRpc: jsonRpcDisclosed
      ? {
          status: 'disclosed',
          schemaVersion: protocol.schemaVersion ?? null,
          protocol: protocol.protocol ?? null,
          transport: protocol.transport,
          framing: protocol.framing ?? null,
          ordering: protocol.ordering ?? null,
          lifecycle: protocol.lifecycle ?? null,
          notifications: protocol.notifications ?? null,
          progress: protocol.progress ?? null,
          cancellation: protocol.cancellation ?? null,
          methods: Object.entries(protocol.methods ?? {})
            .map(([name, contract]) => ({ name, ...contract }))
            .sort((a, b) => a.name.localeCompare(b.name)),
          resultEnvelope: protocol.resultEnvelope ?? null,
          artifactRef: protocol.artifactRef ?? null,
          errors: Array.isArray(protocol.errors) ? protocol.errors : [],
        }
      : {
          status: 'undisclosed',
          schemaVersion: protocol?.schemaVersion ?? null,
        },
    daemon: daemonDisclosed
      ? {
          status: 'disclosed',
          contract: daemonCommand,
          inputMode: daemonCommand.inputMode ?? null,
          environment: daemonCommand.environment ?? {},
          defaults: daemonCommand.defaults ?? {},
          subcommands: objectKeys(daemonCommand.subcommands).sort(),
        }
      : { status: 'undisclosed' },
  }
}

function readLocalJson(path) {
  try {
    return parseJson(readFileSync(path, 'utf8'))
  } catch {
    return null
  }
}

function generatorDeckkitIndex() {
  const catalog = readLocalJson(join(SKILL_ROOT, 'assets', 'deckkits', 'catalog.json'))
  const entries = Array.isArray(catalog?.entries) ? catalog.entries : []
  return entries
    .filter((entry) => entry && typeof entry.id === 'string')
    .map((entry) => ({
      id: entry.id,
      readiness: entry.readiness ?? null,
      themePack: entry.themePack ?? entry.nativeSkinning?.themePack ?? null,
      stylePack: entry.stylePack ?? entry.nativeSkinning?.stylePack ?? null,
      path: entry.path ?? null,
      creation: 'deckkit-generator',
      nativeSkinning: entry.nativeSkinning?.supported === true,
    }))
    .sort((a, b) => a.id.localeCompare(b.id))
}

function hasExactKeys(value, expected) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false
  const actual = Object.keys(value).sort()
  const wanted = [...expected].sort()
  return actual.length === wanted.length && actual.every((key, index) => key === wanted[index])
}

function isNonEmptyString(value) {
  return typeof value === 'string' && value.trim().length > 0
}

function isCapabilityIdentityPart(value) {
  return typeof value === 'string' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)
}

function capabilityAxisContract(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null
  const names = Array.isArray(value.names) ? value.names : []
  const statuses = Array.isArray(value.statuses) ? value.statuses : []
  const requiredFor = Array.isArray(value.requiredFor) ? value.requiredFor : null
  if (
    value.schemaVersion !== 'pptx-capability-axis-contract/v1' ||
    names.length !== CAPABILITY_AXIS_NAMES.length ||
    !names.every((name, index) => name === CAPABILITY_AXIS_NAMES[index]) ||
    statuses.length !== CAPABILITY_AXIS_STATUSES.length ||
    !statuses.every((status, index) => status === CAPABILITY_AXIS_STATUSES[index]) ||
    !hasExactKeys(value.definitions, CAPABILITY_AXIS_NAMES) ||
    !CAPABILITY_AXIS_NAMES.every((name) => isNonEmptyString(value.definitions[name])) ||
    !hasExactKeys(value.statusDefinitions, CAPABILITY_AXIS_STATUSES) ||
    !CAPABILITY_AXIS_STATUSES.every((status) =>
      isNonEmptyString(value.statusDefinitions[status]),
    ) ||
    !requiredFor ||
    !requiredFor.every(
      (target) =>
        target &&
        typeof target === 'object' &&
        !Array.isArray(target) &&
        isCapabilityIdentityPart(target.feature) &&
        isCapabilityIdentityPart(target.subset),
    )
  ) {
    return null
  }
  const requiredIdentities = requiredFor.map(({ feature, subset }) => `${feature}/${subset}`)
  const requiredIdentitySet = new Set(requiredIdentities)
  // requiredFor is an extensible runtime list, not a fixed enum. Keep the v1
  // baseline and validate axes for every additional identity disclosed by xdoc.
  if (
    requiredIdentitySet.size !== requiredIdentities.length ||
    !CAPABILITY_AXIS_REQUIRED_IDENTITIES.every((identity) => requiredIdentitySet.has(identity))
  ) {
    return null
  }
  return {
    schemaVersion: value.schemaVersion,
    names,
    statuses,
    definitions: value.definitions,
    statusDefinitions: value.statusDefinitions,
    requiredFor: requiredFor.map(({ feature, subset }) => ({ feature, subset })),
  }
}

function capabilityAxes(value, contract, truthEvidenceIds) {
  if (!contract || !hasExactKeys(value, contract.names)) return null
  const normalized = {}
  for (const name of contract.names) {
    const axis = value[name]
    const limits = Array.isArray(axis?.limits) ? axis.limits : []
    const limitCodes = limits.map((limit) => limit?.code)
    const platforms = Array.isArray(axis?.officeTarget?.platforms)
      ? axis.officeTarget.platforms
      : []
    const evidenceIds = Array.isArray(axis?.evidenceIds) ? axis.evidenceIds : []
    if (
      !axis ||
      typeof axis !== 'object' ||
      Array.isArray(axis) ||
      !contract.statuses.includes(axis.status) ||
      !isNonEmptyString(axis.summary) ||
      limits.length === 0 ||
      !limits.every(
        (limit) =>
          limit &&
          typeof limit === 'object' &&
          !Array.isArray(limit) &&
          isNonEmptyString(limit.code) &&
          isNonEmptyString(limit.description),
      ) ||
      new Set(limitCodes).size !== limitCodes.length ||
      !axis.officeTarget ||
      typeof axis.officeTarget !== 'object' ||
      Array.isArray(axis.officeTarget) ||
      axis.officeTarget.application !== 'powerpoint' ||
      !isNonEmptyString(axis.officeTarget.minimumVersion) ||
      platforms.length !== 2 ||
      !platforms.every(isNonEmptyString) ||
      new Set(platforms).size !== platforms.length ||
      [...platforms].sort().join(',') !== 'macos,windows' ||
      evidenceIds.length === 0 ||
      !evidenceIds.every(isNonEmptyString) ||
      new Set(evidenceIds).size !== evidenceIds.length ||
      !evidenceIds.every((id) => truthEvidenceIds.has(id))
    ) {
      return null
    }
    normalized[name] = {
      status: axis.status,
      summary: axis.summary,
      limits,
      officeTarget: {
        application: axis.officeTarget.application ?? null,
        minimumVersion: axis.officeTarget.minimumVersion ?? null,
        platforms: [...platforms].sort(),
      },
      evidenceIds: [...evidenceIds].sort(),
    }
  }
  return normalized
}

function capabilityTruthIndex(value) {
  const schemaVersion = value?.schemaVersion ?? null
  const schemaTrusted = schemaVersion === 'pptx-capability-truth/v3'
  const axisContract = schemaTrusted ? capabilityAxisContract(value?.axisContract) : null
  const trusted = schemaTrusted && axisContract !== null
  const axesRequiredFor = new Set(
    (axisContract?.requiredFor ?? []).map(({ feature, subset }) => `${feature}/${subset}`),
  )
  const truthEvidenceIds = new Set(
    trusted && Array.isArray(value?.entries)
      ? value.entries.flatMap((entry) =>
          Array.isArray(entry?.evidence)
            ? entry.evidence.map((evidence) => evidence?.id).filter(isNonEmptyString)
            : [],
        )
      : [],
  )
  const entries =
    trusted && Array.isArray(value?.entries)
      ? value.entries
          .filter(
            (entry) =>
              entry &&
              isCapabilityIdentityPart(entry.feature) &&
              isCapabilityIdentityPart(entry.subset) &&
              CAPABILITY_ENTRY_STATUSES.includes(entry.status),
          )
          .map((entry) => ({
            feature: entry.feature,
            subset: entry.subset,
            status: entry.status,
            summary: entry.summary ?? null,
            operations: uniqueSorted(Array.isArray(entry.operations) ? entry.operations : []),
            limits: Array.isArray(entry.limits) ? entry.limits : [],
            evidence: Array.isArray(entry.evidence) ? entry.evidence : [],
            recommendation: entry.recommendation ?? null,
            axes: capabilityAxes(entry.axes, axisContract, truthEvidenceIds),
          }))
          .filter(
            (entry) =>
              !axesRequiredFor.has(`${entry.feature}/${entry.subset}`) || entry.axes !== null,
          )
      : []
  return {
    schemaVersion,
    available: trusted,
    coverage: trusted ? (value?.coverage ?? null) : null,
    missingMeans: trusted ? (value?.missingMeans ?? 'undisclosed') : 'undisclosed',
    axisContract,
    entries,
    operationIndex:
      trusted && value?.operationIndex && typeof value.operationIndex === 'object'
        ? value.operationIndex
        : {},
  }
}

function requirementResults(requirements, capabilities) {
  const featureEntries = new Map(
    capabilities.capabilityTruth.entries.map((entry) => [
      `${entry.feature}/${entry.subset}`,
      entry,
    ]),
  )
  const indexes = {
    commands: new Set([
      ...capabilities.commands,
      ...capabilities.pptxSubcommands,
      ...capabilities.pptxSubcommands.map((name) => `pptx.${name}`),
    ]),
    operations: new Set([...capabilities.patchOperations, ...capabilities.recipeOperations]),
    features: new Set(featureEntries.keys()),
    enums: new Set(capabilities.enums.map((entry) => entry.name)),
    themes: new Set(capabilities.themePacks),
    styles: new Set(capabilities.stylePacks),
    nativeDeckkits: new Set(capabilities.nativeDeckkits.map((entry) => entry.id)),
    generatorDeckkits: new Set(capabilities.generatorDeckkits.map((entry) => entry.id)),
  }
  const results = []
  const disclosedMeaning = {
    commands: 'present in the runtime xdoc command index',
    operations: 'present in the runtime xdoc patch/recipe operation index',
    features: 'declared by the runtime xdoc capability truth',
    enums: 'present in the runtime xdoc enum registry',
    themes: 'present in the runtime xdoc theme catalog',
    styles: 'present in the runtime xdoc style catalog',
    nativeDeckkits: 'present in the runtime xdoc native skinning DeckKit catalog',
    generatorDeckkits: 'present in the bundled DeckKit generator catalog',
  }
  for (const [kind, values] of Object.entries(requirements)) {
    for (const value of values) {
      if (kind === 'features') {
        const entry = featureEntries.get(value)
        if (!entry) {
          results.push({
            kind,
            value,
            state: 'undisclosed',
            satisfied: false,
            meaning: 'not declared by capability truth; this is not proof of unsupported behavior',
          })
          continue
        }
        results.push({
          kind,
          value,
          state: entry.status,
          satisfied: entry.status === 'supported',
          meaning:
            entry.status === 'supported'
              ? 'the exact feature/subset is supported within its declared limits'
              : `the exact feature/subset is ${entry.status}; follow its recommendation instead of inferring support from operation presence`,
          limits: entry.limits,
          recommendation: entry.recommendation,
          axes: entry.axes,
        })
        continue
      }
      const disclosed = indexes[kind].has(value)
      results.push({
        kind,
        value,
        state: disclosed ? 'disclosed' : 'undisclosed',
        satisfied: disclosed,
        meaning: disclosed
          ? disclosedMeaning[kind] || 'present in the capability index'
          : 'not present in the capability index; this is not proof of unsupported behavior',
      })
    }
  }
  return results
}

function disclosedFlagValues(flags, prefix) {
  const flag = flags.find((value) => value.startsWith(prefix))
  if (!flag) return []
  const raw = flag
    .slice(prefix.length)
    .trim()
    .replace(/[<>[\]]/g, '')
  return raw.includes('|')
    ? raw
        .split('|')
        .map((value) => value.trim())
        .filter(Boolean)
    : []
}

function compactFailure(result) {
  return {
    exitCode: result.status,
    error: result.error,
    stderr: result.stderr.trim().slice(0, 1000) || null,
  }
}

function createReport(args) {
  let schemaRun = run(args.xdocBin, ['schema', '--mode', 'capabilities'])
  if (!schemaRun.ok || !parseJson(schemaRun.stdout)) schemaRun = run(args.xdocBin, ['schema'])
  const schema = schemaRun.ok ? parseJson(schemaRun.stdout) : null
  let version = typeof schema?.version === 'string' ? schema.version : null
  let fallbackVersion = null
  let fallbackHelp = null

  if (!schema) {
    fallbackVersion = run(args.xdocBin, ['--version'])
    fallbackHelp = run(args.xdocBin, ['--help'])
    if (fallbackVersion.ok) version = fallbackVersion.stdout.trim() || null
  } else if (!version) {
    fallbackVersion = run(args.xdocBin, ['--version'])
    if (fallbackVersion.ok) version = fallbackVersion.stdout.trim() || null
  }

  const executableMissing =
    schemaRun.error?.code === 'ENOENT' ||
    fallbackVersion?.error?.code === 'ENOENT' ||
    fallbackHelp?.error?.code === 'ENOENT'
  const pptx = schema?.commands?.pptx ?? {}
  const patchSchema = pptx.patchSchema ?? {}
  const capabilityTruth = capabilityTruthIndex(pptx.capabilityTruth)
  const catalogs = pptx.catalogs ?? {}
  const schemaDisclosure = pptx.schemaDisclosure ?? schema?.commands?.schema?.disclosure
  const schemaSlicingModes = namesFromCollection(schemaDisclosure?.modes, ['flag'])
  const schemaRefinements = namesFromCollection(schemaDisclosure?.refinements, ['flag'])
  // Older schemas listed projection flags as modes; current contracts separate refinements.
  const schemaSlicingFlags = uniqueSorted([...schemaSlicingModes, ...schemaRefinements])
  const fieldsAvailable = schemaSlicingFlags.some((flag) => /^--fields(?:\s|$)/.test(flag))
  const defsAvailable = schemaSlicingFlags.some((flag) => /^--defs(?:\s|$)/.test(flag))
  const defsModes = disclosedFlagValues(schemaSlicingFlags, '--defs')
  const summaryDefsAvailable = defsModes.includes('summary')
  const capabilities = {
    commands: objectKeys(schema?.commands).sort(),
    pptxSubcommands: objectKeys(pptx.subcommands).sort(),
    visualAudit: {
      modes: pptx.subcommands?.['visual-audit']?.visualModes?.values ?? [],
      defaultMode: pptx.subcommands?.['visual-audit']?.visualModes?.default ?? null,
    },
    patchOperations: uniqueSorted([
      ...namesFromCollection(patchSchema.supportedOps),
      ...namesFromCollection(patchSchema.operations),
    ]),
    recipeOperations: namesFromCollection(pptx.recipeOps),
    capabilityTruth,
    enums: enumIndex(pptx.enumRegistry?.enums),
    themePacks: idsFromCatalog(catalogs.themes),
    stylePacks: idsFromCatalog(catalogs.styles),
    nativeDeckkits: nativeDeckkitIndex(catalogs.nativeDeckkits),
    nativeSkinningDeckkits: nativeDeckkitIndex(catalogs.nativeDeckkits),
    generatorDeckkits: generatorDeckkitIndex(),
    agentTransports: agentTransportIndex(schema?.commands),
    schemaSlicing: {
      available: Boolean(schemaDisclosure),
      modes: schemaSlicingModes,
      refinements: schemaRefinements,
      fieldsAvailable,
      defsAvailable,
      defsModes,
      summaryDefsAvailable,
      recommended: schemaDisclosure?.agentHint ?? null,
    },
    commandFlags: helpFlagIndex(args.xdocBin),
  }
  const requirements = requirementResults(args.requirements, capabilities)
  const attentionRequired = requirements.filter((item) => item.satisfied !== true)
  const undisclosedRequired = attentionRequired.filter((item) => item.state === 'undisclosed')
  const warnings = []
  if (!schema) {
    warnings.push({
      code: 'schema-unavailable',
      message:
        'xdoc schema was unavailable or not valid JSON; use command help and dry-run for further discovery instead of treating capabilities as unsupported.',
      detail: compactFailure(schemaRun),
    })
  }
  if (schema && schema.schemaVersion !== 'cli-agent/v1') {
    warnings.push({
      code: 'unknown-cli-schema-version',
      message: `Observed ${schema.schemaVersion ?? 'an unversioned schema'}; retain discovery data and review schema changes before high-risk writes.`,
    })
  }
  if (schema && !capabilityTruth.available) {
    warnings.push({
      code: 'capability-truth-unavailable',
      message:
        capabilityTruth.schemaVersion !== 'pptx-capability-truth/v3'
          ? 'The runtime does not disclose pptx-capability-truth/v3; feature requirements remain undisclosed and operation presence must not be interpreted as full feature support.'
          : 'The runtime discloses pptx-capability-truth/v3 with an invalid six-axis contract; the entire truth is unavailable, feature requirements remain undisclosed, and operation presence must not be interpreted as full feature support.',
    })
  }
  if (undisclosedRequired.length > 0) {
    warnings.push({
      code: 'required-capability-undisclosed',
      message:
        'One or more task requirements were not disclosed. Explore targeted help/schema or choose a documented fallback; do not classify them as unsupported from this snapshot alone.',
    })
  }
  const constrainedRequired = attentionRequired.filter((item) => item.state !== 'undisclosed')
  if (constrainedRequired.length > 0) {
    warnings.push({
      code: 'required-feature-not-fully-supported',
      message:
        'One or more required feature/subset entries are partial, preserve-only, or unsupported. Follow their limits and recommended alternative; operation disclosure does not override capability truth.',
    })
  }

  return {
    report: {
      schemaVersion: 'pptx-nova-xdoc-capabilities/v3',
      observedAt: new Date().toISOString(),
      status: executableMissing ? 'dependency-missing' : schema ? 'ready' : 'degraded',
      xdoc: {
        executable: args.xdocBin,
        version,
        cliSchemaVersion: schema?.schemaVersion ?? null,
        capabilitySchemaVersion: schema?.capabilities?.schemaVersion ?? null,
        patchCapabilityVersion: patchSchema.capabilityVersion ?? null,
        capabilityTruthVersion: capabilityTruth.schemaVersion,
        schemaSha256: schema ? createHash('sha256').update(schemaRun.stdout).digest('hex') : null,
        schemaDigest: schema?.disclosure?.schemaDigest ?? null,
      },
      disclosure: {
        source:
          schema?.disclosure?.mode === 'capabilities'
            ? 'xdoc schema --mode capabilities'
            : schema
              ? 'xdoc schema'
              : 'xdoc --help fallback',
        scope: schema ? 'runtime-schema-name-index' : 'unstructured-fallback',
        notAnAllowlist: true,
        missingMeans: 'undisclosed, not unsupported',
        targetedLookup: {
          operationIndex:
            'read xdoc-capabilities.json#capabilities.patchOperations; refresh with xdoc schema --mode index only when needed',
          operationSchema:
            fieldsAvailable && summaryDefsAvailable
              ? 'xdoc schema --mode ops --ops <name> --fields <needed-fields> --defs summary --minimal; use --defs full before constructing nested values; omit --fields or apply --dry-run for complete operation validation'
              : fieldsAvailable
                ? 'xdoc schema --mode ops --ops <name> --fields <needed-fields> --minimal; omit --fields or use apply --dry-run for complete validation'
                : 'xdoc schema --mode ops --ops <name> --minimal',
          featureTruth:
            'read xdoc-capabilities.json#capabilities.capabilityTruth.entries by exact feature/subset; when axes is non-null, route create/edit/inspect/preserve/render/verify independently and follow each axis status, limits, Office target, and evidence ids',
          commandHelp: 'xdoc <command...> --help',
          commandSchema: 'xdoc schema --command <command.action>',
          reportSchema: 'xdoc schema --report <schemaVersion>',
          agentTransport:
            'read xdoc-capabilities.json#capabilities.agentTransports; use the exact disclosed daemon, JSON-RPC, or MCP contract rather than inferring transport behavior from command presence',
          selectorEvidence: 'inspect output -> op schema -> dry-run suggestions',
          deckkitGeneratorCatalog:
            'read xdoc-capabilities.json#capabilities.generatorDeckkits for DeckKit-first creation support',
          nativeSkinningCatalog:
            'read xdoc-capabilities.json#capabilities.nativeSkinningDeckkits for native refurbish/skin support',
        },
      },
      capabilities,
      requirements: {
        strict: args.strict,
        status: attentionRequired.length === 0 ? 'satisfied' : 'attention',
        results: requirements,
        undisclosedRequired: undisclosedRequired.map(({ kind, value }) => ({ kind, value })),
        attentionRequired: attentionRequired.map(({ kind, value, state }) => ({
          kind,
          value,
          state,
        })),
      },
      fallback: schema
        ? null
        : {
            versionAvailable: Boolean(fallbackVersion?.ok),
            helpAvailable: Boolean(fallbackHelp?.ok),
            helpIsStructuredJson: false,
          },
      warnings,
      error: executableMissing
        ? {
            kind: 'ENOENT',
            message: `xdoc executable was not found: ${args.xdocBin}`,
          }
        : null,
    },
    executableMissing,
    strictFailure: args.strict && attentionRequired.length > 0,
  }
}

function writeReport(args, report) {
  const text = `${JSON.stringify(report, null, 2)}\n`
  if (args.output) {
    const output = resolve(args.output)
    if (existsSync(output) && !args.overwrite) {
      throw new Error(
        `output already exists: ${output}; use --overwrite only for a current-run artifact`,
      )
    }
    mkdirSync(dirname(output), { recursive: true })
    writeFileSync(output, text)
  }
  if (args.json || !args.output) {
    process.stdout.write(text)
  } else {
    process.stdout.write(`xdoc capability status: ${report.status}\n`)
    process.stdout.write(`xdoc version: ${report.xdoc.version ?? 'unknown'}\n`)
    process.stdout.write(`snapshot: ${resolve(args.output)}\n`)
    process.stdout.write(`requirements: ${report.requirements.status}\n`)
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  const { report, executableMissing, strictFailure } = createReport(args)
  writeReport(args, report)
  if (executableMissing) process.exit(1)
  if (strictFailure) process.exit(2)
} catch (error) {
  process.stderr.write(`[error] ${error.message}\n`)
  process.exit(1)
}
