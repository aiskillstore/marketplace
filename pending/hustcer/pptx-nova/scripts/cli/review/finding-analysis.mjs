#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { evaluateFindings } from '../../lib/review/finding-analysis.mjs'
import { layoutSemanticSha256 } from '../../lib/review/layout-snapshot.mjs'

const SCHEMA_VERSION = 'pptx-nova-finding-analysis/v1-draft'
const RULE_SET_VERSION = 'pptx-nova-finding-rules/v1-shadow.1'

const usage = `Usage:
  node <skill-root>/scripts/cli/review/finding-analysis.mjs \\
    --source-layout layout-source.json --candidate-layout layout-final.json \\
    --source-pptx source.pptx --candidate-pptx candidate.pptx \\
    --semantic-diff pptx-diff.json --output finding-analysis.json [options]

Options:
  --dry-run <path>            Optional pptx-dry-run/v1 evidence.
  --apply <path>              Optional pptx-apply/v1 evidence.
  --patch <path>              Patch bytes shared by dry-run/apply evidence.
  --review-evaluation <path>  Optional complete review-policy evaluation.
  --automation <mode>         human-in-loop|unattended. Defaults to human-in-loop.
  --enforcement <mode>        shadow|required. Defaults to shadow.
  --json                      Print a compact machine summary.
  --json-full                 Print the complete report.
  --help                      Show this help.

The standalone CLI always marks bindings as advisory-replay. Only a trusted runner can
produce runner-observed evidence for a required gate.
`

const valueFlags = {
  '--source-layout': 'sourceLayout',
  '--candidate-layout': 'candidateLayout',
  '--source-pptx': 'sourcePptx',
  '--candidate-pptx': 'candidatePptx',
  '--semantic-diff': 'semanticDiff',
  '--dry-run': 'dryRun',
  '--apply': 'apply',
  '--patch': 'patch',
  '--review-evaluation': 'reviewEvaluation',
  '--output': 'output',
  '--automation': 'automation',
  '--enforcement': 'enforcement',
}

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseArgs(argv) {
  const args = {
    sourceLayout: '',
    candidateLayout: '',
    sourcePptx: '',
    candidatePptx: '',
    semanticDiff: '',
    dryRun: '',
    apply: '',
    patch: '',
    reviewEvaluation: '',
    output: '',
    automation: 'human-in-loop',
    enforcement: 'shadow',
    json: false,
    jsonFull: false,
  }
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    }
    if (arg === '--json' || arg === '--json-full') {
      args.json = true
      args.jsonFull = arg === '--json-full'
      continue
    }
    if (!(arg in valueFlags)) throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    const key = valueFlags[arg]
    const value = valueAfter(argv, index, arg)
    args[key] = ['automation', 'enforcement'].includes(key) ? value : resolve(value)
    index += 1
  }
  for (const key of [
    'sourceLayout',
    'candidateLayout',
    'sourcePptx',
    'candidatePptx',
    'semanticDiff',
    'output',
  ]) {
    if (!args[key])
      throw new Error(
        `--${key.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)} is required`,
      )
  }
  if (!['human-in-loop', 'unattended'].includes(args.automation)) {
    throw new Error('--automation must be human-in-loop or unattended')
  }
  if (!['shadow', 'required'].includes(args.enforcement)) {
    throw new Error('--enforcement must be shadow or required')
  }
  if ((args.dryRun || args.apply) && !args.patch) {
    throw new Error('--patch is required when --dry-run or --apply is present')
  }
  return args
}

function sha256Bytes(bytes) {
  return createHash('sha256').update(bytes).digest('hex')
}

function readBytes(path, label) {
  if (!existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  return readFileSync(path)
}

function readJsonArtifact(path, label) {
  const bytes = readBytes(path, label)
  try {
    return { report: JSON.parse(bytes.toString('utf8')), artifactSha256: sha256Bytes(bytes) }
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`)
  }
}

function buildInput(args) {
  const sourceLayout = readJsonArtifact(args.sourceLayout, 'source layout')
  const candidateLayout = readJsonArtifact(args.candidateLayout, 'candidate layout')
  const semanticDiff = readJsonArtifact(args.semanticDiff, 'semantic diff')
  const sourceSha256 = sha256Bytes(readBytes(args.sourcePptx, 'source PPTX'))
  const candidateSha256 = sha256Bytes(readBytes(args.candidatePptx, 'candidate PPTX'))
  const patchSha256 = args.patch ? sha256Bytes(readBytes(args.patch, 'patch')) : null
  const dryRun = args.dryRun ? readJsonArtifact(args.dryRun, 'dry-run evidence') : null
  const apply = args.apply ? readJsonArtifact(args.apply, 'apply evidence') : null
  const reviewEvaluation = args.reviewEvaluation
    ? readJsonArtifact(args.reviewEvaluation, 'review evaluation')
    : null
  return {
    workflowProfile: {
      profileId: 'refurbish-shadow/v1-draft',
      kind: 'refurbish',
      mode: 'standard',
      mutationIntent: 'style',
      deliveryStage: 'final',
    },
    bindingContext: { assurance: 'advisory-replay', schemaDeclaredInputs: [] },
    sourceLayout: {
      report: sourceLayout.report,
      binding: {
        pptxSha256: sourceSha256,
        layoutArtifactSha256: sourceLayout.artifactSha256,
        layoutSemanticSha256: layoutSemanticSha256(sourceLayout.report),
      },
    },
    candidateLayout: {
      report: candidateLayout.report,
      binding: {
        pptxSha256: candidateSha256,
        layoutArtifactSha256: candidateLayout.artifactSha256,
        layoutSemanticSha256: layoutSemanticSha256(candidateLayout.report),
      },
    },
    changedScope: {
      mode: 'full-deck',
      slideIndexes: [],
      objectIds: [],
      origin: 'workflow-profile',
      binding: {
        sourcePptxSha256: sourceSha256,
        candidatePptxSha256: candidateSha256,
        evidenceArtifactSha256: null,
      },
    },
    mutationEvidence: {
      dryRun: dryRun
        ? {
            ...dryRun,
            binding: { sourcePptxSha256: sourceSha256, patchSha256 },
          }
        : null,
      apply: apply
        ? {
            ...apply,
            binding: {
              sourcePptxSha256: sourceSha256,
              candidatePptxSha256: candidateSha256,
              patchSha256,
            },
          }
        : null,
      semanticDiff: {
        ...semanticDiff,
        binding: {
          sourcePptxSha256: sourceSha256,
          candidatePptxSha256: candidateSha256,
        },
      },
    },
    reviewEvaluation,
    executionPolicy: { automation: args.automation, enforcement: args.enforcement },
  }
}

function adapterFailure(args, error) {
  return {
    schemaVersion: SCHEMA_VERSION,
    evaluation: {
      status: 'failed',
      errors: [
        {
          code: 'finding-analysis-artifact-unreadable',
          message: error.message,
        },
      ],
      diagnostics: [],
    },
    workflowProfile: {
      profileId: 'refurbish-shadow/v1-draft',
      kind: 'refurbish',
      mode: 'standard',
      mutationIntent: 'style',
      deliveryStage: 'final',
    },
    bindings: {
      assurance: 'advisory-replay',
      schemaDeclaredInputs: [],
      source: null,
      candidate: null,
      changedScope: null,
      mutationEvidence: {},
      reviewEvaluation: null,
    },
    policy: { ruleSetVersion: RULE_SET_VERSION },
    analysisIdentity: null,
    findings: [],
    resolvedFindings: [],
    summary: { countsComplete: false, errorCount: 1 },
    agentGate: {
      enforcement: args?.enforcement ?? 'shadow',
      proposedStatus: 'fail',
      effectiveStatus: args?.enforcement === 'required' ? 'fail' : 'not-applied',
      governingFindingKeys: [],
      nextAction: 'regenerate-bound-evidence',
    },
  }
}

function compactResult(report, output) {
  return {
    schemaVersion: report.schemaVersion,
    status: report.evaluation.status,
    analysisIdentity: report.analysisIdentity,
    summary: report.summary,
    agentGate: report.agentGate,
    output,
  }
}

function printHuman(report, output) {
  process.stdout.write(`pptx-nova Finding Analysis: ${report.evaluation.status}\n`)
  process.stdout.write(`- proposed gate: ${report.agentGate.proposedStatus}\n`)
  process.stdout.write(`- effective gate: ${report.agentGate.effectiveStatus}\n`)
  process.stdout.write(`- findings: ${report.summary.findingCount ?? 'unknown'}\n`)
  process.stdout.write(`- unresolved: ${report.summary.unresolvedFindingCount ?? 'unknown'}\n`)
  process.stdout.write(`- next action: ${report.agentGate.nextAction}\n`)
  process.stdout.write(`- output: ${output}\n`)
}

let args = null
let report = null
try {
  args = parseArgs(process.argv.slice(2))
  report = evaluateFindings(buildInput(args))
} catch (error) {
  report = adapterFailure(args, error)
}

if (args?.output) writeFileSync(args.output, `${JSON.stringify(report, null, 2)}\n`)
if (args?.jsonFull) process.stdout.write(`${JSON.stringify(report, null, 2)}\n`)
else if (args?.json)
  process.stdout.write(`${JSON.stringify(compactResult(report, args.output), null, 2)}\n`)
else printHuman(report, args?.output ?? '')
if (report.evaluation.status === 'failed') process.exitCode = 1
