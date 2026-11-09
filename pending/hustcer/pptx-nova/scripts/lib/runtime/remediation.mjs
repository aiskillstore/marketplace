import { createHash } from 'node:crypto'

export const REMEDIATION_LIMIT = 1024 * 1024
const digestPattern = /^[0-9a-f]{64}$/
const digest = (value) => typeof value === 'string' && digestPattern.test(value)
const unavailableReasons = new Set([
  'identity-unavailable',
  'context-unavailable',
  'ambiguous-source',
  'target-unavailable',
  'payload-limit',
])
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex')
const object = (value) =>
  value !== null &&
  typeof value === 'object' &&
  !Array.isArray(value) &&
  [Object.prototype, null].includes(Object.getPrototypeOf(value))
const has = (value, key) => Object.hasOwn(value, key)

function fail(code, message) {
  const error = new Error(message)
  error.code = code
  throw error
}

function closed(value, keys, label) {
  if (
    !object(value) ||
    Object.keys(value).length !== keys.length ||
    keys.some((key) => !has(value, key))
  ) {
    fail('invalid_remediation', `${label} must contain exactly: ${keys.join(', ')}`)
  }
}

function validUnicode(text) {
  for (let i = 0; i < text.length; i++) {
    const unit = text.charCodeAt(i)
    if (unit >= 0xd800 && unit <= 0xdbff) {
      const next = text.charCodeAt(++i)
      if (!(next >= 0xdc00 && next <= 0xdfff)) return false
    } else if (unit >= 0xdc00 && unit <= 0xdfff) return false
  }
  return true
}

// Independent ECMAScript verification of the producer's RFC 8785 identity.
// This deliberately does not reuse canonicalJsonV1, whose historical rules differ.
export function requestJcsSha256(value) {
  const visiting = new Set()
  function canonical(node, depth) {
    if (depth > 1024) fail('identity_unavailable', 'Request nesting exceeds the verifier limit')
    if (node === null || typeof node === 'boolean') return JSON.stringify(node)
    if (typeof node === 'string') {
      if (!validUnicode(node)) fail('identity_unavailable', 'Request contains invalid Unicode')
      return JSON.stringify(node)
    }
    if (typeof node === 'number') {
      if (!Number.isFinite(node) || (Number.isInteger(node) && !Number.isSafeInteger(node))) {
        fail('identity_unavailable', 'Request contains an unsafe identity number')
      }
      return JSON.stringify(node)
    }
    if ((!Array.isArray(node) && !object(node)) || visiting.has(node)) {
      fail('identity_unavailable', 'Request must be an acyclic JSON value')
    }
    visiting.add(node)
    let result
    if (Array.isArray(node))
      result = `[${Array.from(node, (item) => canonical(item, depth + 1)).join(',')}]`
    else {
      result = `{${Object.keys(node)
        .sort()
        .map((key) => {
          if (!validUnicode(key))
            fail('identity_unavailable', 'Request key contains invalid Unicode')
          return `${JSON.stringify(key)}:${canonical(node[key], depth + 1)}`
        })
        .join(',')}}`
    }
    visiting.delete(node)
    return result
  }
  return sha256(canonical(value, 0))
}

// Retain raw tokens until decoded duplicate keys have been rejected. JSON.parse
// remains the syntax authority; this small scanner does not interpret operations.
export function parseRemediationJson(raw) {
  if (typeof raw !== 'string') fail('invalid_json', 'JSON input must be text')
  let at = 0
  const whitespace = () => {
    while (/\s/.test(raw[at] ?? '') && at < raw.length) at++
  }
  const string = () => {
    const start = at++
    while (at < raw.length) {
      if (raw[at] === '\\') at += 2
      else if (raw[at++] === '"') return JSON.parse(raw.slice(start, at))
    }
    fail('invalid_json', 'Unterminated JSON string')
  }
  function scan(depth) {
    if (depth > 1024) fail('invalid_json', 'JSON nesting exceeds the verifier limit')
    whitespace()
    if (raw[at] === '"') {
      string()
      return
    }
    if (raw[at] === '{' || raw[at] === '[') {
      const isObject = raw[at++] === '{'
      const end = isObject ? '}' : ']'
      const keys = new Set()
      whitespace()
      if (raw[at] === end) {
        at++
        return
      }
      while (at < raw.length) {
        if (isObject) {
          if (raw[at] !== '"') fail('invalid_json', 'Expected an object key')
          const key = string()
          if (keys.has(key)) fail('duplicate_key', 'Duplicate decoded JSON key')
          keys.add(key)
          whitespace()
          if (raw[at++] !== ':') fail('invalid_json', 'Expected a key separator')
        }
        scan(depth + 1)
        whitespace()
        if (raw[at] === end) {
          at++
          return
        }
        if (raw[at++] !== ',') fail('invalid_json', 'Expected a member separator')
        whitespace()
      }
      fail('invalid_json', 'Unterminated JSON container')
    }
    const start = at
    while (at < raw.length && !/[\s,}\]]/.test(raw[at])) at++
    if (at === start) fail('invalid_json', 'Expected a JSON value')
  }
  scan(0)
  whitespace()
  if (at !== raw.length) fail('invalid_json', 'Trailing JSON content')
  return JSON.parse(raw)
}

// NDJSON framing removes only insignificant whitespace. Keep every string and
// numeric token exactly as submitted so the engine owns numeric interpretation.
export function compactRemediationJson(raw) {
  parseRemediationJson(raw)
  let quoted = false
  let escaped = false
  const output = []
  for (const character of raw) {
    if (quoted) {
      output.push(character)
      if (escaped) escaped = false
      else if (character === '\\') escaped = true
      else if (character === '"') quoted = false
    } else if (character === '"') {
      quoted = true
      output.push(character)
    } else if (!/[\t\r\n ]/.test(character)) output.push(character)
  }
  return output.join('')
}

function patchEnvelope(value, authored) {
  if (!object(value) || value.schemaVersion !== 'pptx-patch/v1' || !Array.isArray(value.ops)) {
    fail('invalid_remediation', 'Remediation requires a complete versioned patch envelope')
  }
  if (!authored && Object.keys(value).some((key) => !['schemaVersion', 'ops'].includes(key))) {
    fail('invalid_remediation', 'Document repair patch has unknown fields')
  }
  for (const op of value.ops) {
    if (!object(op) || typeof op.op !== 'string' || !op.op.trim())
      fail('invalid_remediation', 'Every patch operation needs its op discriminator')
  }
}

export function validateRemediation(value) {
  if (!object(value)) fail('invalid_remediation', 'Remediation must be an object')
  const common = ['kind', 'target', 'reason', 'confidence', 'autoRetry']
  if (value.kind === 'replace-request') {
    closed(value, [...common, 'request'], 'replace-request')
    closed(
      value.target,
      ['kind', 'requestCanonicalization', 'requestSha256', 'inputSha256'],
      'original-input target',
    )
    if (
      value.target.kind !== 'original-input' ||
      value.target.requestCanonicalization !== 'jcs-rfc8785' ||
      !digest(value.target.requestSha256)
    ) {
      fail('invalid_remediation', 'Invalid request identity target')
    }
    if (value.target.inputSha256 !== null && !digest(value.target.inputSha256))
      fail('invalid_remediation', 'Invalid original input digest')
    patchEnvelope(value.request, true)
  } else if (value.kind === 'apply-to-document') {
    closed(value, [...common, 'patch', 'requiresRawXml'], 'apply-to-document')
    closed(value.target, ['kind', 'inputSha256'], 'document target')
    if (value.target.kind !== 'document' || !digest(value.target.inputSha256))
      fail('invalid_remediation', 'A document target needs an exact SHA-256')
    if (typeof value.requiresRawXml !== 'boolean')
      fail('invalid_remediation', 'requiresRawXml must be boolean')
    patchEnvelope(value.patch, false)
    if (value.patch.ops.length === 0)
      fail('invalid_remediation', 'A document repair must contain operations')
  } else fail('invalid_remediation', 'Unknown remediation discriminator')
  if (
    typeof value.reason !== 'string' ||
    !value.reason.trim() ||
    typeof value.confidence !== 'number' ||
    !Number.isFinite(value.confidence) ||
    value.confidence < 0 ||
    value.confidence > 1 ||
    typeof value.autoRetry !== 'boolean'
  ) {
    fail('invalid_remediation', 'Invalid remediation reason, confidence or autoRetry')
  }
  // Reject non-JSON values before stringify can silently replace or omit them.
  requestJcsSha256(value)
  if (Buffer.byteLength(JSON.stringify(value), 'utf8') > REMEDIATION_LIMIT)
    fail('payload_limit', 'Executable remediation exceeds 1 MiB')
  return value
}

export function remediationAt(report, pointer) {
  if (typeof pointer !== 'string' || !pointer.startsWith('/'))
    fail('invalid_pointer', 'Use an absolute JSON Pointer to one diagnostic or remediation')
  let node = report
  for (const raw of pointer.slice(1).split('/')) {
    if (/~(?![01])/.test(raw)) fail('invalid_pointer', 'Malformed JSON Pointer escape')
    const key = raw.replaceAll('~1', '/').replaceAll('~0', '~')
    if (node === null || typeof node !== 'object' || !has(node, key))
      fail('missing_remediation', 'The selected report location does not exist')
    node = node[key]
  }
  if (object(node) && has(node, 'remediationUnavailable')) {
    closed(node.remediationUnavailable, ['reason'], 'remediationUnavailable')
    if (!unavailableReasons.has(node.remediationUnavailable.reason) || has(node, 'remediation'))
      fail('invalid_remediation', 'Invalid unavailable branch')
    fail('remediation_unavailable', node.remediationUnavailable.reason)
  }
  if (object(node) && has(node, 'remediation')) node = node.remediation
  return validateRemediation(node)
}

export function patchAssetPaths(patch) {
  const paths = new Set()
  function walk(node) {
    if (Array.isArray(node)) {
      for (const child of node) walk(child)
      return
    }
    if (!object(node)) return
    if (typeof node.op === 'string') {
      for (const source of [
        node.assetSource,
        node.icon,
        node.posterFrame,
        node.fill?.assetSource,
      ]) {
        if (object(source) && typeof source.path === 'string') paths.add(source.path)
      }
      if (node.op === 'bind-data' && node.source !== undefined) {
        const source = typeof node.source === 'string' ? node.source : node.source?.path
        if (typeof source === 'string') paths.add(source)
      }
    }
    for (const child of Object.values(node)) walk(child)
  }
  walk(patch)
  return [...paths].sort()
}

// The caller creates this from its own first-submission snapshots, never from
// a report's self-declared target. Filesystem storage and authorization remain
// the host's responsibility; prepareRemediation never writes or authorizes.
export function prepareRemediation(value, submitted, { documentBytes, reviewed = false } = {}) {
  const remediation = validateRemediation(value)
  if (!remediation.autoRetry && !reviewed)
    fail('review_required', 'This remediation requires review before execution')
  if (
    !object(submitted) ||
    typeof submitted.requestText !== 'string' ||
    !Array.isArray(submitted.assets) ||
    typeof submitted.assetRoot !== 'string' ||
    (submitted.inputBytes !== null &&
      !Buffer.isBuffer(submitted.inputBytes) &&
      !(submitted.inputBytes instanceof Uint8Array))
  ) {
    fail(
      'context_unavailable',
      'The original submitted request, input and asset snapshots are required',
    )
  }
  let inputBytes
  let patch
  if (remediation.kind === 'replace-request') {
    const original = parseRemediationJson(submitted.requestText)
    const expectedRequest = requestJcsSha256(original)
    const expectedInput = submitted.inputBytes === null ? null : sha256(submitted.inputBytes)
    if (remediation.target.requestSha256 !== expectedRequest)
      fail('request_mismatch', 'Remediation belongs to another authored request')
    if (remediation.target.inputSha256 !== expectedInput)
      fail('input_mismatch', 'Remediation belongs to another original input')
    patch = remediation.request
    inputBytes = submitted.inputBytes
  } else {
    if (!Buffer.isBuffer(documentBytes) && !(documentBytes instanceof Uint8Array))
      fail('target_unavailable', 'Retain the exact document before applying its remediation')
    if (sha256(documentBytes) !== remediation.target.inputSha256)
      fail('document_mismatch', 'The document changed after this diagnosis')
    if (remediation.requiresRawXml && submitted.allowRawXml !== true)
      fail('authorization_required', 'Existing raw XML permission does not allow this proposal')
    patch = remediation.patch
    inputBytes = documentBytes
  }
  const assets = new Set(submitted.assets.map((asset) => asset.path))
  if (patchAssetPaths(patch).some((path) => !assets.has(path)))
    fail('context_mismatch', 'Remediation introduces an asset absent from the original snapshot')
  return {
    kind: remediation.kind,
    patch: structuredClone(patch),
    inputBytes: inputBytes === null ? null : Buffer.from(inputBytes),
    assetRoot: submitted.assetRoot,
    allowRawXml: submitted.allowRawXml === true,
    intent: submitted.intent === undefined ? undefined : structuredClone(submitted.intent),
  }
}
