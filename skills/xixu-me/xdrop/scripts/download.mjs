import { mkdir, open } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'

import { resolveApiUrl } from './upload.mjs'

const MANIFEST_VERSION = 1
const encoder = new TextEncoder()
const decoder = new TextDecoder()
let quietMode = false

const HELP_TEXT = `Download files from an Xdrop share link and decrypt them locally.

Usage:
  bun <path-to-download.mjs> <share-url>

Options:
  --output <dir>     Destination directory. Defaults to ./xdrop-<transferId>.
  --api-url <url>    Override the API root. Defaults to <share-origin>/api/v1.
  --quiet            Suppress progress output and only print the final result.
  --json             Print JSON instead of a plain output path.
  --help             Show this help.

Examples:
  bun scripts/download.mjs "http://localhost:8080/t/abc#k=..."
  bun scripts/download.mjs --output ./downloads "http://localhost:8080/t/abc#k=..."
`

export async function main(argv = process.argv.slice(2)) {
  const options = parseArgs(argv)
  quietMode = options.quiet

  if (options.help) {
    process.stdout.write(`${HELP_TEXT}\n`)
    return
  }

  if (!options.shareUrl) {
    throw new Error('Provide a full Xdrop share link.')
  }

  const share = parseShareUrl(options.shareUrl)
  const api = new XdropDownloadApiClient(resolveApiUrl(share.serverUrl, options.apiUrl))

  logStatus(`Fetching transfer ${share.transferId}`)
  const descriptor = await api.getPublicTransfer(share.transferId)
  if (descriptor.status !== 'ready' || !descriptor.manifestUrl || !descriptor.wrappedRootKey) {
    throw new Error(getTransferStatusError(descriptor.status))
  }

  const manifestResponse = await fetch(descriptor.manifestUrl)
  if (!manifestResponse.ok) {
    throw new Error(`Couldn't load the encrypted manifest (${manifestResponse.status}).`)
  }

  const envelopeBytes = new Uint8Array(await manifestResponse.arrayBuffer())
  const rootKey = await unwrapRootKey(descriptor.wrappedRootKey, share.linkKey)
  const manifest = await decryptManifest(rootKey, envelopeBytes)
  const outputRoot = resolve(process.cwd(), options.output || `xdrop-${share.transferId}`)
  await mkdir(outputRoot, { recursive: true })

  const savedFiles = []
  for (const [index, file] of manifest.files.entries()) {
    const sanitizedPath = sanitizePath(file.relativePath || file.name)
    if (!sanitizedPath) {
      throw new Error(`Refusing to write an empty file path for ${file.fileId}.`)
    }

    const destination = resolve(outputRoot, ...sanitizedPath.split('/'))
    await mkdir(dirname(destination), { recursive: true })
    logStatus(`Downloading ${sanitizedPath} (${index + 1}/${manifest.files.length})`)
    await downloadFile({
      api,
      transferId: share.transferId,
      file,
      rootKey,
      destination,
    })
    savedFiles.push(destination)
  }

  if (options.json) {
    process.stdout.write(
      `${JSON.stringify(
        {
          transferId: share.transferId,
          outputRoot,
          files: savedFiles,
        },
        null,
        2,
      )}\n`,
    )
    return
  }

  process.stdout.write(`${savedFiles.length === 1 ? savedFiles[0] : outputRoot}\n`)
}

export function parseArgs(argv) {
  const options = {
    output: '',
    apiUrl: process.env.XDROP_API_URL?.trim() || '',
    quiet: false,
    json: false,
    help: false,
    shareUrl: '',
  }

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index]
    if (!value) {
      continue
    }

    if (value === '--help' || value === '-h') {
      options.help = true
      continue
    }
    if (value === '--quiet') {
      options.quiet = true
      continue
    }
    if (value === '--json') {
      options.json = true
      continue
    }
    if (value === '--output') {
      options.output = requireValue(argv, ++index, '--output')
      continue
    }
    if (value === '--api-url') {
      options.apiUrl = requireValue(argv, ++index, '--api-url')
      continue
    }
    if (value.startsWith('--')) {
      throw new Error(`Unknown option: ${value}`)
    }
    if (options.shareUrl) {
      throw new Error('Only one share link can be downloaded at a time.')
    }
    options.shareUrl = value
  }

  return options
}

function requireValue(argv, index, flag) {
  const value = argv[index]
  if (!value) {
    throw new Error(`Missing value for ${flag}`)
  }
  return value
}

export function parseShareUrl(input) {
  const url = new URL(input)
  const match = url.pathname.match(/\/t\/([^/]+)\/?$/u)
  if (!match?.[1]) {
    throw new Error('Share link must point to /t/:transferId.')
  }

  const params = new URLSearchParams(url.hash.startsWith('#') ? url.hash.slice(1) : url.hash)
  const key = params.get('k')
  if (!key) {
    throw new Error('Share link is missing the decryption key fragment.')
  }

  url.hash = ''
  url.search = ''
  url.pathname = '/'

  return {
    transferId: match[1],
    linkKey: fromBase64Url(key),
    serverUrl: url,
  }
}

export function sanitizePath(input) {
  return input
    .split(/[\\/]+/u)
    .filter((segment) => segment && segment !== '.' && segment !== '..')
    .map((segment) =>
      Array.from(segment.replace(/[<>:"|?*]/gu, '_'))
        .map((char) => ((char.codePointAt(0) ?? 0) < 32 ? '_' : char))
        .join(''),
    )
    .join('/')
}

async function downloadFile({ api, transferId, file, rootKey, destination }) {
  const chunks = Array.from({ length: file.totalChunks }, (_, chunkIndex) => ({
    fileId: file.fileId,
    chunkIndex,
  }))
  const urls = await api.createDownloadUrls(transferId, chunks)
  const urlMap = new Map(urls.map((item) => [item.chunkIndex, item.url]))
  const noncePrefix = fromBase64Url(file.noncePrefix)
  const fileHandle = await open(destination, 'w')

  try {
    for (let chunkIndex = 0; chunkIndex < file.totalChunks; chunkIndex += 1) {
      const url = urlMap.get(chunkIndex)
      if (!url) {
        throw new Error(`Missing download URL for ${file.relativePath} chunk ${chunkIndex}.`)
      }

      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`Chunk download failed with ${response.status}.`)
      }

      const ciphertext = new Uint8Array(await response.arrayBuffer())
      const remainingBytes = Math.max(file.plaintextSize - chunkIndex * file.chunkSize, 0)
      const plaintextChunkSize = Math.min(file.chunkSize, remainingBytes)
      const plaintext = await decryptChunk({
        rootKey,
        transferId,
        fileId: file.fileId,
        chunkIndex,
        noncePrefix,
        plaintextChunkSize,
        ciphertext,
      })

      await fileHandle.write(plaintext)
    }
  } finally {
    await fileHandle.close()
  }
}

async function unwrapRootKey(serializedEnvelope, linkKey) {
  const envelope = JSON.parse(serializedEnvelope)
  const wrappingKey = await deriveHkdfKey(linkKey, 'wrap-root')
  const plaintext = await crypto.subtle.decrypt(
    {
      name: 'AES-GCM',
      iv: fromBase64Url(envelope.iv),
    },
    wrappingKey,
    fromBase64(envelope.ciphertext),
  )

  return new Uint8Array(plaintext)
}

async function decryptManifest(rootKey, envelopeBytes) {
  const envelope = JSON.parse(decoder.decode(envelopeBytes))
  const manifestKey = await deriveHkdfKey(rootKey, 'manifest')
  const plaintext = await crypto.subtle.decrypt(
    {
      name: 'AES-GCM',
      iv: fromBase64Url(envelope.iv),
    },
    manifestKey,
    fromBase64(envelope.ciphertext),
  )

  return JSON.parse(decoder.decode(plaintext))
}

async function decryptChunk(options) {
  const fileKey = await deriveHkdfKey(options.rootKey, `file:${options.fileId}`)
  const iv = buildChunkIv(options.noncePrefix, options.chunkIndex)
  const additionalData = encoder.encode(
    [
      options.transferId,
      options.fileId,
      options.chunkIndex,
      options.plaintextChunkSize,
      MANIFEST_VERSION,
    ].join('|'),
  )
  const plaintext = await crypto.subtle.decrypt(
    {
      name: 'AES-GCM',
      iv,
      additionalData,
    },
    fileKey,
    options.ciphertext,
  )

  return new Uint8Array(plaintext)
}

async function deriveHkdfKey(source, info) {
  const sourceKey = await crypto.subtle.importKey('raw', source, 'HKDF', false, ['deriveKey'])
  return crypto.subtle.deriveKey(
    {
      name: 'HKDF',
      hash: 'SHA-256',
      salt: new Uint8Array(),
      info: encoder.encode(info),
    },
    sourceKey,
    {
      name: 'AES-GCM',
      length: 256,
    },
    false,
    ['encrypt', 'decrypt'],
  )
}

function buildChunkIv(noncePrefix, chunkIndex) {
  const iv = new Uint8Array(12)
  iv.set(noncePrefix.slice(0, 8), 0)
  new DataView(iv.buffer).setUint32(8, chunkIndex, false)
  return iv
}

function fromBase64Url(value) {
  const normalized = value.replace(/-/gu, '+').replace(/_/gu, '/')
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
  return new Uint8Array(Buffer.from(padded, 'base64'))
}

function fromBase64(value) {
  return new Uint8Array(Buffer.from(value, 'base64'))
}

function getTransferStatusError(status) {
  switch (status) {
    case 'expired':
      return 'This share link has expired.'
    case 'deleted':
      return 'This transfer was deleted.'
    case 'incomplete':
      return 'This transfer is still uploading.'
    default:
      return 'This transfer is unavailable.'
  }
}

function logStatus(message) {
  if (quietMode) {
    return
  }
  process.stderr.write(`${message}\n`)
}

class XdropDownloadApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl
  }

  async getPublicTransfer(transferId) {
    return this.request(`/public/transfers/${transferId}`)
  }

  async createDownloadUrls(transferId, chunks) {
    const response = await this.request(`/public/transfers/${transferId}/download-urls`, {
      method: 'POST',
      body: { chunks },
    })
    return response.items
  }

  async request(path, options = { method: 'GET' }) {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: options.method ?? 'GET',
      headers: {
        ...(options.body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      ...(options.body === undefined ? {} : { body: JSON.stringify(options.body) }),
    })

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}))
      const detail = payload.message ?? payload.error ?? `Request failed with ${response.status}`
      throw new Error(detail)
    }

    return response.json()
  }
}

if (import.meta.main) {
  main().catch(async (error) => {
    if (quietMode) {
      process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
      process.exit(1)
    }
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
    process.exit(1)
  })
}
