#!/usr/bin/env node
import { SKILL_ROOT } from '../../lib/runtime/skill-paths.mjs'
import { readFileSync, writeFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import {
  checkDesignReadback,
  designHash,
  loadDesignContract,
} from '../../../assets/deckkits/shared/design-contract.mjs'
import { validateDeckkitContent } from '../../../assets/deckkits/shared/validate-deckkit.mjs'
import { registeredDesignFamily } from '../../../assets/deckkits/shared/design-family-registry.mjs'
import { readNativeCharts } from '../../lib/pptx/native-chart-readback.mjs'

const usage = `Usage:
  node <skill-root>/scripts/cli/deckkits/design.mjs --deckkit <id> [--content content.json] [--output report.json]
  node <skill-root>/scripts/cli/deckkits/design.mjs --deckkit <id> --plan design-plan.json --patch patch.json --inspect inspect.json [--model model.json] [--output report.json]

Without content: discover tokens, rules and layout capacities.
With content: validate and resolve a deterministic plan without invoking xdoc.
With plan/patch/inspect: verify applied objects; native charts/tables require the xdoc JSON model.
All output is JSON. Unknown arguments fail. Does not publish or certify visual quality.
`
const read = (p) => JSON.parse(readFileSync(resolve(p), 'utf8'))
try {
  const args = {}
  const values = new Set(['deckkit', 'content', 'output', 'plan', 'patch', 'inspect', 'model'])
  const argv = process.argv.slice(2)
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--help') {
      console.log(usage)
      process.exit(0)
    }
    const key = argv[i].replace(/^--/, '')
    if (!values.has(key) || !argv[i + 1] || argv[i + 1].startsWith('--')) {
      throw new Error(`Unknown or incomplete argument: ${argv[i]}`)
    }
    args[key] = argv[++i]
  }
  if (!args.deckkit) throw new Error('--deckkit is required')
  const d = loadDesignContract(args.deckkit)
  if (!d) throw new Error(`${args.deckkit} has no design contract; use the legacy slots reference`)
  let report
  if (args.inspect || args.plan || args.patch || args.model) {
    if (!args.plan || !args.patch || !args.inspect || args.content) {
      throw new Error('Readback requires --plan, --patch and --inspect; omit --content')
    }
    const plan = read(args.plan)
    if (plan.contractHash !== designHash(d) || plan.designId !== d.id) {
      throw new Error('Design contract changed since build; rebuild and inspect the same candidate')
    }
    const inspect = read(args.inspect)
    const patch = read(args.patch)
    const nativeCharts =
      patch.ops.some((op) => op.op === 'add-chart') && typeof inspect.input === 'string'
        ? readNativeCharts(inspect.input)
        : null
    report = checkDesignReadback(
      plan,
      patch,
      inspect,
      args.model ? read(args.model) : null,
      nativeCharts,
    )
    if (inspect.input && typeof inspect.input === 'string') {
      report.candidateSha256 = createHash('sha256')
        .update(readFileSync(inspect.input))
        .digest('hex')
    }
  } else if (args.content) {
    const content = read(args.content)
    const validation = validateDeckkitContent(content, { deckkit: args.deckkit, mode: 'delivery' })
    if (!validation.valid) throw new Error(validation.errors.map((e) => e.message).join('; '))
    const catalog = readFileSync(
      new URL('../../../assets/deckkits/catalog.json', import.meta.url),
      'utf8',
    )
    const entry = JSON.parse(catalog).entries.find((e) => e.id === args.deckkit)
    const root = resolve(SKILL_ROOT, 'assets/deckkits')
    const mod = await import(pathToFileURL(resolve(root, entry.path)).href)
    const built = mod.createDeck(content)
    report = {
      status: 'pass',
      designPlan: built.designPlan,
      designCheck: built.designCheck,
      warnings: validation.warnings,
    }
  } else {
    report = {
      schemaVersion: 'pptx-nova-design-discovery/v2',
      designId: d.id,
      version: d.version,
      contractHash: designHash(d),
      colors: d.colors,
      fonts: d.fonts,
      rules: d.rules,
      registeredSlideTypes: [
        ...Object.keys(
          (d[registeredDesignFamily(d)?.key] ?? d.biennale ?? d.editorial ?? d.strategy ?? d.annual)
            ?.families ?? {},
        ),
        ...(d.evidence ? [d.evidence.slideType] : []),
      ],
      ...(d.biennale ? { biennale: d.biennale } : {}),
      evidence: d.evidence,
      annual: d.annual,
      ...(d.editorial ? { editorial: d.editorial } : {}),
      ...(d.strategy ? { strategy: d.strategy } : {}),
      ...(registeredDesignFamily(d)
        ? { [registeredDesignFamily(d).key]: d[registeredDesignFamily(d).key] }
        : {}),
      inputGuide:
        'Use registered content schemas and layoutId=auto. Raw coordinates/colors/fonts are not content inputs.',
      visualReviewRequired: true,
    }
  }
  const text = JSON.stringify(report, null, 2) + '\n'
  if (args.output) writeFileSync(resolve(args.output), text)
  process.stdout.write(text)
  if (report.status === 'fail') process.exitCode = 1
} catch (error) {
  process.stdout.write(JSON.stringify({ status: 'fail', error: error.message }) + '\n')
  process.exitCode = 1
}
