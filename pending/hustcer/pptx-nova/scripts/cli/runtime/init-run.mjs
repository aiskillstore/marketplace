#!/usr/bin/env node
import { cliPath, SKILL_ROOT as skillRoot } from '../../lib/runtime/skill-paths.mjs'
import { existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { basename, isAbsolute, join, relative, resolve } from 'node:path'

const usage = `Usage:
  node <skill-root>/scripts/cli/runtime/init-run.mjs --slug <name> --deckkit <id> [options]

Options:
  --slug <name>       Human-readable run slug.
  --deckkit <id>      DeckKit id for deck_lock.json and content.json.
  --output <path>     Intended final PPTX path.
  --objective <text>  Short objective written to deck_lock.json and outline.json.
  --mode <mode>       express, studio, edit, or export. Defaults to express.
  --root <path>       Project root. Defaults to current working directory.
  --xdoc-bin <path>   xdoc executable. Defaults to xdoc.
  --json              Print machine-readable paths.
  --help              Show this help.
`

function parseArgs(argv) {
  const args = {
    slug: '',
    deckkit: '',
    output: '',
    objective: '',
    mode: 'express',
    root: process.cwd(),
    xdocBin: 'xdoc',
    json: false,
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--json') {
      args.json = true
    } else if (arg === '--slug') {
      args.slug = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--deckkit') {
      args.deckkit = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--output') {
      args.output = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--objective') {
      args.objective = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--mode') {
      args.mode = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--root') {
      args.root = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--xdoc-bin') {
      args.xdocBin = valueAfter(argv, i, arg)
      i += 1
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }
  if (!args.slug) throw new Error(`--slug is required\n\n${usage}`)
  if (!args.deckkit) throw new Error(`--deckkit is required\n\n${usage}`)
  return args
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function safeSlug(value) {
  return (
    String(value)
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 64) || 'deck'
  )
}

function timestamp(now = new Date()) {
  const pad = (value) => String(value).padStart(2, '0')
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
}

function writeJson(path, value) {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`)
}

function relativeOrAbsolute(path) {
  return isAbsolute(path) ? path : path
}

function shellQuote(value) {
  return `'${String(value).replaceAll("'", "'\\''")}'`
}

function relativeToRun(runDir, path) {
  return relative(runDir, path) || basename(path)
}

try {
  const args = parseArgs(process.argv.slice(2))
  const root = resolve(args.root)
  const runDir = join(root, '.pptx-nova', `${safeSlug(args.slug)}-${timestamp()}`)
  if (existsSync(runDir)) throw new Error(`run directory already exists: ${runDir}`)
  const assetsDir = join(runDir, 'assets')
  const previewsDir = join(runDir, 'previews')
  mkdirSync(assetsDir, { recursive: true })

  const finalPptx = args.output
    ? resolve(root, args.output)
    : join(root, `${safeSlug(args.slug)}.pptx`)
  if (existsSync(finalPptx)) {
    throw new Error(`final output already exists before run initialization: ${finalPptx}`)
  }

  const outlinePath = join(runDir, 'outline.json')
  const lockPath = join(runDir, 'deck_lock.json')
  const lockTemplatePath = join(runDir, 'deck_lock.template.json')
  const contentPath = join(runDir, 'content.json')
  const contentTemplatePath = join(runDir, 'content.template.json')
  const patchPath = join(runDir, 'patch.json')
  const qualityPath = join(runDir, 'quality.json')
  const capabilityPath = join(runDir, 'xdoc-capabilities.json')
  const dryRunPath = join(runDir, 'dry-run.json')
  const applyPath = join(runDir, 'apply.json')
  const visionPath = join(runDir, 'vision.json')
  const previewReportPath = join(runDir, 'preview.json')
  const visualEvidenceDir = join(runDir, 'visual-evidence')
  const visualEvidenceManifestPath = join(visualEvidenceDir, 'manifest.json')
  const visualEvidenceGatePath = join(runDir, 'visual-evidence-gate.json')
  const candidatePath = join(runDir, 'candidate.pptx')
  const contactSheetPath = join(previewsDir, 'contact-sheet.png')
  const commandsPath = join(runDir, 'commands.json')
  const probeScript = cliPath('runtime/probe.mjs')

  writeJson(outlinePath, {
    schemaVersion: 'pptx-nova-outline/v1',
    objective: args.objective || args.slug,
    slides: [],
  })
  writeJson(lockTemplatePath, {
    schemaVersion: 'pptx-nova-deck-lock/v1',
    _template: true,
    _instructions:
      'Copy this file to deck_lock.json or write deck_lock.json from scratch, then remove _template and _instructions. Do not append another JSON object to this template.',
    mode: args.mode,
    objective: args.objective || args.slug,
    outlinePath: basename(outlinePath),
    contentPath: basename(contentPath),
    patchPath: basename(patchPath),
    output: {
      finalPptx: relativeOrAbsolute(finalPptx),
      runDir,
    },
    canvas: {
      format: 'ppt169',
      width: '13.333in',
      height: '7.5in',
    },
    deckkit: {
      id: args.deckkit,
    },
    slides: [],
    assumptions: [],
  })
  writeJson(contentTemplatePath, {
    _template: true,
    _instructions:
      'Copy this file to content.json or write content.json from scratch, then remove _template and _instructions. Replace slides[] with real DeckKit content; do not append another JSON object to this template.',
    meta: {
      deckkit: args.deckkit,
    },
    slides: [],
  })

  const commands = {
    probe: `node ${shellQuote(probeScript)} --xdoc-bin ${shellQuote(args.xdocBin)} --output ${shellQuote(capabilityPath)}`,
    run: `node ${shellQuote(cliPath('create/run.mjs'))} --deckkit ${shellQuote(args.deckkit)} --content ${shellQuote(contentPath)} --lock ${shellQuote(lockPath)} --output ${shellQuote(finalPptx)} --run-dir ${shellQuote(runDir)} --xdoc-bin ${shellQuote(args.xdocBin)} --json`,
    build: `node ${shellQuote(cliPath('create/build.mjs'))} --deckkit ${shellQuote(args.deckkit)} ${shellQuote(contentPath)} -o ${shellQuote(patchPath)} --quality-json ${shellQuote(qualityPath)}`,
    validate: `node ${shellQuote(join(skillRoot, 'assets', 'deckkits', 'validate-content.mjs'))} ${shellQuote(contentPath)} --deckkit ${shellQuote(args.deckkit)} --mode delivery`,
    checkLock: `node ${shellQuote(cliPath('create/check-lock.mjs'))} --lock ${shellQuote(lockPath)} --content ${shellQuote(contentPath)} --patch ${shellQuote(patchPath)} --json`,
    dryRun: `${shellQuote(args.xdocBin)} pptx apply -p ${shellQuote(patchPath)} -o ${shellQuote(candidatePath)} --overwrite --dry-run --json > ${shellQuote(dryRunPath)}`,
    apply: `${shellQuote(args.xdocBin)} pptx apply -p ${shellQuote(patchPath)} -o ${shellQuote(candidatePath)} --overwrite --json > ${shellQuote(applyPath)}`,
    vision: `${shellQuote(args.xdocBin)} pptx vision-check ${shellQuote(candidatePath)} --json > ${shellQuote(visionPath)}`,
    preview: `${shellQuote(args.xdocBin)} pptx preview ${shellQuote(candidatePath)} --output-dir ${shellQuote(previewsDir)} --contact-sheet --contact-output ${shellQuote(contactSheetPath)} --overwrite --json > ${shellQuote(previewReportPath)}`,
    visualVerify: `${shellQuote(args.xdocBin)} pptx visual-audit --candidate ${shellQuote(candidatePath)} --visual-mode create --output-dir ${shellQuote(visualEvidenceDir)} --json`,
    visualEvidenceGate: `node ${shellQuote(cliPath('review/visual-evidence-gate.mjs'))} --manifest ${shellQuote(visualEvidenceManifestPath)} --candidate ${shellQuote(candidatePath)} --output ${shellQuote(visualEvidenceGatePath)} --json`,
  }
  commands.finalize = `${commands.run} --finalize --visual-review ${shellQuote(join(runDir, 'visual_review.json'))}`
  writeJson(commandsPath, commands)

  const result = {
    runDir,
    outlinePath,
    deckLockPath: lockPath,
    deckLockTemplatePath: lockTemplatePath,
    contentPath,
    contentTemplatePath,
    patchPath,
    qualityPath,
    capabilityPath,
    dryRunPath,
    applyPath,
    visionPath,
    previewReportPath,
    visualEvidenceDir,
    visualEvidenceManifestPath,
    visualEvidenceGatePath,
    commandsPath,
    assetsDir,
    previewsDir,
    candidatePath,
    contactSheetPath,
    finalPptx,
    reservedPaths: {
      deckLockPath: relativeToRun(runDir, lockPath),
      contentPath: relativeToRun(runDir, contentPath),
      candidatePath: relativeToRun(runDir, candidatePath),
    },
  }
  if (args.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
  else {
    process.stdout.write(`Run directory: ${runDir}\n`)
    process.stdout.write(`Content target: ${contentPath}\n`)
    process.stdout.write(`Content template: ${contentTemplatePath}\n`)
    process.stdout.write(`Deck lock target: ${lockPath}\n`)
    process.stdout.write(`Deck lock template: ${lockTemplatePath}\n`)
    process.stdout.write(`Commands: ${commandsPath}\n`)
    process.stdout.write(`Patch: ${patchPath}\n`)
  }
} catch (error) {
  console.error(`[error] ${error.message}`)
  process.exit(1)
}
