#!/usr/bin/env node
import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import {
  constants,
  closeSync,
  existsSync,
  fstatSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  openSync,
  readFileSync,
  realpathSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path'
import { parseArgs, TextDecoder } from 'node:util'
import { resolveFilesystemPath } from '../../lib/runtime/filesystem-paths.mjs'
import {
  compactRemediationJson,
  parseRemediationJson,
  patchAssetPaths,
  prepareRemediation,
  remediationAt,
  requestJcsSha256,
} from '../../lib/runtime/remediation.mjs'

const VERSION = 'pptx-nova-remediation-context/v1'
const MAX_BUFFER = 16 * 1024 * 1024
const MAX_DOCUMENT = 512 * 1024 * 1024
const hash = (value) => createHash('sha256').update(value).digest('hex')
const utf8 = (bytes) => new TextDecoder('utf-8', { fatal: true }).decode(bytes)
function fail(code, message) {
  throw Object.assign(new Error(message), { code })
}
function required(value, name) {
  if (!value) fail('missing_argument', `Missing --${name}`)
  return value
}
function fresh(path) {
  if (existsSync(path)) fail('output_exists', 'Output must be a fresh path')
  return path
}
function write(path, bytes) {
  writeFileSync(path, bytes, { flag: 'wx', mode: 0o600 })
}
function writeJson(path, value) {
  write(path, JSON.stringify(value) + '\n')
}

function read(path, limit) {
  const fd = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0))
  try {
    const before = fstatSync(fd)
    if (!before.isFile() || before.size > limit)
      fail('snapshot_limit', 'Snapshot must be a regular file within the applicable byte budget')
    const bytes = readFileSync(fd)
    const after = fstatSync(fd)
    if (
      bytes.length !== before.size ||
      after.size !== before.size ||
      after.mtimeMs !== before.mtimeMs ||
      after.ctimeMs !== before.ctimeMs
    )
      fail('context_changed', 'Source changed while capturing its bytes')
    return bytes
  } finally {
    closeSync(fd)
  }
}

function relativeAsset(root, path) {
  if (
    typeof path !== 'string' ||
    !path ||
    isAbsolute(path) ||
    /^[A-Za-z]:/.test(path) ||
    path.includes('\\') ||
    path.split('/').some((part) => part === '..' || part === '')
  )
    fail('context_unavailable', 'Asset paths must remain relative to their original root')
  const candidate = resolve(root, path)
  const inside = relative(root, candidate)
  if (!inside || inside === '..' || inside.startsWith(`..${sep}`) || isAbsolute(inside))
    fail('context_unavailable', 'Asset escapes its original root')
  return candidate
}

function containedFile(root, path, limit) {
  const candidate = relativeAsset(root, path)
  if (realpathSync(candidate) !== candidate)
    fail('context_changed', 'Snapshot files and their parents must not be symlinks')
  return read(candidate, limit)
}

function execute(binary, args, { cwd, env, input } = {}) {
  const result = spawnSync(binary, args, {
    cwd,
    env,
    input,
    encoding: 'utf8',
    timeout: 60_000,
    maxBuffer: MAX_BUFFER,
  })
  if (result.error || result.signal)
    fail('execution_failed', result.error?.message ?? `xdoc terminated: ${result.signal}`)
  return result
}

function executable(value) {
  if (isAbsolute(value) || value.includes('/') || value.includes('\\'))
    return realpathSync.native(value)
  for (const directory of (process.env.PATH ?? '').split(
    process.platform === 'win32' ? ';' : ':',
  )) {
    for (const extension of process.platform === 'win32' ? ['', '.exe'] : ['']) {
      const path = join(directory, value + extension)
      if (existsSync(path)) {
        const canonical = realpathSync(path)
        if (lstatSync(canonical).isFile()) return canonical
      }
    }
  }
  fail('runtime_unavailable', 'Cannot locate xdoc; use --xdoc with its executable path')
}

function policy(binary, cwd) {
  const result = execute(binary, ['schema', '--mode', 'full'], { cwd, env: process.env })
  if (result.status !== 0) fail('runtime_unavailable', 'xdoc schema discovery failed')
  const contract = parseRemediationJson(result.stdout).commands?.pptx
  if (!contract?.remediationSchema || !contract.assetPolicy)
    fail('runtime_unavailable', 'This xdoc does not publish the required remediation contract')
  const values = {}
  for (const [field, key] of [
    ['maxPatchBytes', 'XDOC_PPTX_MAX_PATCH_BYTES'],
    ['maxAssetBytes', 'XDOC_PPTX_MAX_ASSET_BYTES'],
  ]) {
    const entry = contract.assetPolicy[field]
    if (entry?.env !== key) fail('runtime_unavailable', 'Unexpected asset policy contract')
    const raw = process.env[key]
    const value = raw === undefined || raw.trim() === '' ? entry.default : Number(raw)
    if (
      !Number.isSafeInteger(value) ||
      value <= 0 ||
      (raw !== undefined && raw.trim() !== '' && !/^\+?\d+$/.test(raw.trim()))
    )
      fail('invalid_policy', `Invalid ${key}`)
    values[field] = value
  }
  return values
}

function descriptor(path, bytes) {
  return { path, bytes: bytes.length, sha256: hash(bytes) }
}
function sameEnvironment(manifest) {
  for (const key of ['XDOC_CONFIG_PATH', 'CI']) {
    if ((process.env[key] ?? null) !== manifest.environment[key])
      fail('context_mismatch', `Original ${key} context changed`)
  }
  return {
    ...process.env,
    XDOC_PPTX_MAX_PATCH_BYTES: String(manifest.policy.maxPatchBytes),
    XDOC_PPTX_MAX_ASSET_BYTES: String(manifest.policy.maxAssetBytes),
  }
}

function load(capsule) {
  const root = realpathSync(capsule)
  if (resolve(capsule) !== root)
    fail('context_unavailable', 'Use the original canonical capsule path')
  const manifest = parseRemediationJson(utf8(containedFile(root, 'context.json', MAX_BUFFER)))
  if (
    manifest.schemaVersion !== VERSION ||
    manifest.root !== root ||
    !['cli', 'json-rpc'].includes(manifest.transport) ||
    !Array.isArray(manifest.assets) ||
    typeof manifest.allowRawXml !== 'boolean'
  )
    fail('context_unavailable', 'Invalid original submission context')
  for (const key of ['maxPatchBytes', 'maxAssetBytes'])
    if (!Number.isSafeInteger(manifest.policy?.[key]) || manifest.policy[key] <= 0)
      fail('context_unavailable', 'Missing original byte policy')
  const verify = (entry, limit) => {
    if (
      !entry ||
      !Number.isSafeInteger(entry.bytes) ||
      entry.bytes < 0 ||
      !/^[a-f0-9]{64}$/.test(entry.sha256)
    )
      fail('context_unavailable', 'Missing snapshot identity')
    const bytes = containedFile(root, entry.path, limit)
    if (bytes.length !== entry.bytes || hash(bytes) !== entry.sha256)
      fail('context_changed', 'Original snapshot bytes changed')
    return bytes
  }
  const requestText = utf8(verify(manifest.request, manifest.policy.maxPatchBytes))
  const inputBytes = manifest.input === null ? null : verify(manifest.input, MAX_DOCUMENT)
  const intent =
    manifest.intent === null ? undefined : parseRemediationJson(utf8(verify(manifest.intent, 8192)))
  const paths = patchAssetPaths(parseRemediationJson(requestText))
  if (JSON.stringify(paths) !== JSON.stringify(manifest.assets.map((entry) => entry.sourcePath)))
    fail('context_changed', 'Original asset inventory changed')
  for (const entry of manifest.assets) {
    if (entry.path !== `assets/${entry.sourcePath}`)
      fail('context_changed', 'Asset snapshot mapping changed')
    verify(entry, manifest.policy.maxAssetBytes)
  }
  if (hash(read(manifest.binary.path, MAX_DOCUMENT)) !== manifest.binary.sha256)
    fail('runtime_changed', 'The xdoc executable changed after the original submission')
  const env = sameEnvironment(manifest)
  return {
    manifest,
    env,
    submitted: {
      requestText,
      inputBytes,
      intent,
      allowRawXml: manifest.allowRawXml,
      assetRoot: join(root, 'assets'),
      assets: manifest.assets.map((entry) => ({ path: entry.sourcePath })),
    },
  }
}

function applyXdoc(context, { patchPath, inputPath, outputPath, intentPath, dryRun = false }) {
  const { manifest, submitted, env } = context
  if (manifest.transport === 'cli') {
    const args = [
      'pptx',
      'apply',
      '--patch',
      patchPath,
      '--output',
      outputPath,
      '--asset-root',
      submitted.assetRoot,
      '--no-sidecar',
      '--json',
    ]
    if (inputPath) args.push('--input', inputPath)
    if (intentPath) args.push('--intent', intentPath)
    if (manifest.allowRawXml) args.push('--allow-raw-xml')
    if (dryRun) args.push('--dry-run')
    const result = execute(manifest.binary.path, args, { cwd: manifest.root, env })
    return { code: result.status, report: parseRemediationJson(result.stdout) }
  }
  const params = { outputPath, assetRoot: submitted.assetRoot, noSidecar: true, dryRun }
  if (inputPath) params.inputPath = inputPath
  if (intentPath) params.intent = parseRemediationJson(utf8(read(intentPath, 8192)))
  if (manifest.allowRawXml) params.allowRawXml = true
  // Insert the validated raw JSON token directly: a parse/stringify round trip
  // could erase a number representation before the engine freezes the request.
  const rawPatch = compactRemediationJson(utf8(read(patchPath, manifest.policy.maxPatchBytes)))
  const rawParams = JSON.stringify(params)
  const input = `{"jsonrpc":"2.0","id":1,"method":"pptx.apply","params":{${rawParams.slice(1, -1)},"patch":${rawPatch}}}\n`
  const result = execute(manifest.binary.path, ['json-rpc'], { cwd: manifest.root, env, input })
  if (result.status !== 0) fail('execution_failed', 'JSON-RPC process failed')
  const frames = result.stdout.trim().split('\n').map(parseRemediationJson)
  const frame = frames.find((value) => value.id === 1)
  const report = frame?.result?.value ?? frame?.error?.data?.report
  const code = frame?.result?.exitCode ?? frame?.error?.data?.exitCode
  if (report === undefined || !Number.isInteger(code))
    fail('execution_failed', frame?.error?.message ?? 'Missing JSON-RPC apply report')
  return { code, report }
}

function run(options) {
  const submittedPatch = resolveFilesystemPath(required(options.patch, 'patch'))
  const patch = realpathSync.native(submittedPatch)
  const output = fresh(resolveFilesystemPath(required(options.output, 'output')))
  const binary = executable(options.xdoc ?? 'xdoc')
  const root = resolveFilesystemPath(required(options.capsule, 'capsule'))
  const sourceRoot = realpathSync.native(options['asset-root'] ?? dirname(submittedPatch))
  if (!['cli', 'json-rpc'].includes(options.transport ?? 'cli'))
    fail('invalid_argument', 'Transport must be cli or json-rpc')
  mkdirSync(root, { mode: 0o700 })
  if (realpathSync(root) !== root)
    fail('context_unavailable', 'Use a canonical capsule parent directory')
  mkdirSync(join(root, 'assets'), { mode: 0o700 })
  const limits = policy(binary, root)
  const requestBytes = read(patch, limits.maxPatchBytes)
  const authored = parseRemediationJson(utf8(requestBytes))
  write(join(root, 'request.json'), requestBytes)
  const inputBytes = options.input ? read(realpathSync.native(options.input), MAX_DOCUMENT) : null
  if (inputBytes !== null) write(join(root, 'input.pptx'), inputBytes)
  let intent = null
  if (options.intent) {
    const bytes = read(realpathSync.native(options.intent), 8192)
    parseRemediationJson(utf8(bytes))
    write(join(root, 'intent.json'), bytes)
    intent = descriptor('intent.json', bytes)
  }
  const assets = []
  for (const sourcePath of patchAssetPaths(authored)) {
    const originalPath = relativeAsset(sourceRoot, sourcePath)
    const canonical = realpathSync(originalPath)
    const inside = relative(sourceRoot, canonical)
    if (inside === '..' || inside.startsWith(`..${sep}`) || isAbsolute(inside))
      fail('context_unavailable', 'An asset symlink escapes the original root')
    const bytes = read(canonical, limits.maxAssetBytes)
    const destination = relativeAsset(join(root, 'assets'), sourcePath)
    mkdirSync(dirname(destination), { recursive: true, mode: 0o700 })
    write(destination, bytes)
    assets.push({ ...descriptor(`assets/${sourcePath}`, bytes), sourcePath })
  }
  const manifest = {
    schemaVersion: VERSION,
    root,
    sourceRoot,
    transport: options.transport ?? 'cli',
    binary: { path: binary, sha256: hash(read(binary, MAX_DOCUMENT)) },
    policy: limits,
    environment: {
      XDOC_CONFIG_PATH: process.env.XDOC_CONFIG_PATH ?? null,
      CI: process.env.CI ?? null,
    },
    allowRawXml: options['allow-raw-xml'] === true,
    request: descriptor('request.json', requestBytes),
    input: inputBytes === null ? null : descriptor('input.pptx', inputBytes),
    intent,
    assets,
  }
  writeJson(join(root, 'context.json'), manifest)
  const result = applyXdoc(load(root), {
    patchPath: join(root, 'request.json'),
    inputPath: manifest.input ? join(root, 'input.pptx') : undefined,
    outputPath: output,
    intentPath: intent ? join(root, 'intent.json') : undefined,
    dryRun: options['dry-run'] === true,
  })
  writeJson(join(root, 'first-report.json'), result.report)
  load(root)
  return result
}

function apply(options) {
  const report = parseRemediationJson(utf8(read(required(options.report, 'report'), MAX_BUFFER)))
  const remediation = remediationAt(report, required(options.pointer, 'pointer'))
  const context = load(required(options.capsule, 'capsule'))
  const documentBytes = options.document
    ? read(realpathSync.native(options.document), MAX_DOCUMENT)
    : undefined
  const prepared = prepareRemediation(remediation, context.submitted, {
    documentBytes,
    reviewed: options.reviewed === true,
  })
  const output = fresh(resolveFilesystemPath(required(options.output, 'output')))
  const root = context.manifest.root
  const id = requestJcsSha256(remediation)
  const receipt = join(root, `applied-${id}.json`)
  if (existsSync(receipt))
    fail(
      'already_applied',
      'This remediation already succeeded in this original submission context',
    )
  const lockPath = join(root, 'apply.lock')
  let lock
  try {
    lock = openSync(lockPath, 'wx', 0o600)
  } catch (error) {
    if (error.code === 'EEXIST')
      fail('context_busy', 'Another attempt owns this original submission context')
    throw error
  }
  try {
    if (existsSync(receipt)) fail('already_applied', 'This remediation already succeeded')
    const attempt = mkdtempSync(join(root, 'attempt-'))
    const patchPath = join(attempt, 'patch.json')
    const inputPath = prepared.inputBytes === null ? undefined : join(attempt, 'input.pptx')
    const intentPath = prepared.intent === undefined ? undefined : join(attempt, 'intent.json')
    writeJson(patchPath, prepared.patch)
    if (inputPath) write(inputPath, prepared.inputBytes)
    if (intentPath) writeJson(intentPath, prepared.intent)
    const invocation = { patchPath, inputPath, intentPath, outputPath: output }
    const validated = applyXdoc(context, { ...invocation, dryRun: true })
    writeJson(join(attempt, 'dry-run-report.json'), validated.report)
    if (validated.code !== 0) return validated
    // Re-read original snapshots after validation. xdoc re-runs the current
    // authorization policy on the actual write with the preserved intent.
    load(root)
    const result = applyXdoc(context, invocation)
    writeJson(join(attempt, 'apply-report.json'), result.report)
    if (result.code === 0)
      writeJson(receipt, { remediationSha256: id, outputSha256: hash(read(output, MAX_DOCUMENT)) })
    load(root)
    return result
  } finally {
    closeSync(lock)
    unlinkSync(lockPath)
  }
}

try {
  const { values, positionals } = parseArgs({
    allowPositionals: true,
    options: Object.fromEntries([
      ...[
        'patch',
        'input',
        'asset-root',
        'capsule',
        'output',
        'xdoc',
        'transport',
        'intent',
        'report',
        'pointer',
        'document',
      ].map((name) => [name, { type: 'string' }]),
      ...['allow-raw-xml', 'dry-run', 'reviewed', 'help'].map((name) => [
        name,
        { type: 'boolean' },
      ]),
    ]),
  })
  if (values.help) {
    process.stdout.write(
      'Capture before the first submission:\n  node <skill-root>/scripts/cli/runtime/remediation.mjs run --patch request.json --capsule NEW_DIR --output NEW.pptx [--input original.pptx] [--asset-root DIR] [--intent intent.json] [--allow-raw-xml] [--dry-run] [--transport cli|json-rpc] [--xdoc PATH]\nApply one verified suggestion:\n  node <skill-root>/scripts/cli/runtime/remediation.mjs apply --capsule DIR --report report.json --pointer /error/suggestions/0 --output NEW.pptx [--document diagnosed.pptx] [--reviewed]\nThe capsule retains private request, input and asset snapshots. A report alone cannot restore the original context. Document snapshots are limited to 512 MiB. Review is mandatory when autoRetry is false.\n',
    )
  } else {
    if (positionals.length !== 1 || !['run', 'apply'].includes(positionals[0]))
      fail('invalid_argument', 'Choose run or apply; see --help')
    const accepted =
      positionals[0] === 'run'
        ? [
            'patch',
            'input',
            'asset-root',
            'capsule',
            'output',
            'xdoc',
            'transport',
            'intent',
            'allow-raw-xml',
            'dry-run',
          ]
        : ['capsule', 'report', 'pointer', 'output', 'document', 'reviewed']
    for (const key of Object.keys(values))
      if (!accepted.includes(key))
        fail('invalid_argument', `Option --${key} does not apply to ${positionals[0]}`)
    const result = positionals[0] === 'run' ? run(values) : apply(values)
    process.stdout.write(JSON.stringify(result.report) + '\n')
    process.exitCode = result.code
  }
} catch (error) {
  process.stdout.write(
    JSON.stringify({
      schemaVersion: 'pptx-nova-remediation-error/v1',
      error: { code: error.code ?? 'remediation_failed', message: error.message },
    }) + '\n',
  )
  process.exitCode = 1
}
