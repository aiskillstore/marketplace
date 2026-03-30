import { createHash } from 'node:crypto'
import { open, readdir, stat } from 'node:fs/promises'
import { basename, extname, resolve } from 'node:path'

const MANIFEST_VERSION = 1
const WRAP_VERSION = 1
const DEFAULT_EXPIRY_SECONDS = 60 * 60
const MAX_UPLOAD_CONCURRENCY = 6
const MAX_TRANSFER_BYTES = 256 * 1024 * 1024

const encoder = new TextEncoder()
let quietMode = false

const HELP_TEXT = `Upload files to an Xdrop server and print the share link.

Usage:
  bun <path-to-upload.mjs> --server https://xdrop.example.com <file-or-directory> [...]

Options:
  --server <url>       Public Xdrop site URL. Can also be set with XDROP_SERVER.
  --api-url <url>      Override the API root. Defaults to <server>/api/v1.
  --expires-in <sec>   Transfer expiry in seconds. Default: ${DEFAULT_EXPIRY_SECONDS}.
  --name <value>       Custom transfer display name.
  --concurrency <n>    Parallel uploads per file. Default: 1, max: ${MAX_UPLOAD_CONCURRENCY}.
  --quiet              Suppress progress output and only print the final result.
  --json               Print JSON instead of a bare share link.
  --help               Show this help.

Examples:
  bun scripts/upload.mjs --server http://localhost:8080 ./dist/archive.zip
  bun scripts/upload.mjs --server https://xdrop.example.com ./photo.jpg ./notes.txt
`

export async function main(argv = process.argv.slice(2)) {
  const options = parseArgs(argv)
  quietMode = options.quiet

  if (options.help) {
    process.stdout.write(`${HELP_TEXT}\n`)
    return
  }

  if (!options.server) {
    throw new Error('Missing --server. Pass the public Xdrop site URL or set XDROP_SERVER.')
  }

  if (options.inputs.length === 0) {
    throw new Error('Choose at least one file or directory to upload.')
  }

  const serverUrl = normalizeSiteUrl(options.server)
  const apiUrl = resolveApiUrl(serverUrl, options.apiUrl)
  const files = await collectTransferInputs(options.inputs)
  if (files.length === 0) {
    throw new Error('No files were found in the selected paths.')
  }

  const displayName = options.name ?? defaultDisplayName(files)
  const api = new XdropApiClient(apiUrl)

  logStatus(`Creating transfer on ${serverUrl.toString()}`)
  const created = await api.createTransfer(options.expiresInSeconds)
  const chunkSize = created.uploadConfig.chunkSize
  const maxFileCount = created.uploadConfig.maxFileCount
  const maxTransferBytes = created.uploadConfig.maxTransferBytes || MAX_TRANSFER_BYTES

  if (files.length > maxFileCount) {
    throw new Error(
      `This selection has ${files.length} files. The server limit is ${maxFileCount}.`,
    )
  }

  const rootKey = randomBytes(32)
  const linkKey = randomBytes(32)
  const preparedFiles = prepareFiles(files, chunkSize)
  const totalCiphertextBytes = preparedFiles.reduce(
    (sum, file) => sum + file.ciphertextSizes.reduce((next, size) => next + size, 0),
    0,
  )

  if (totalCiphertextBytes > maxTransferBytes) {
    throw new Error(
      `Encrypted upload size ${formatBytes(totalCiphertextBytes)} exceeds the server limit ${formatBytes(maxTransferBytes)}.`,
    )
  }

  const shareUrl = new URL(`/t/${created.transferId}`, serverUrl)
  shareUrl.hash = `k=${toBase64Url(linkKey)}`

  let finalized = false
  try {
    await api.registerFiles(
      created.transferId,
      created.manageToken,
      preparedFiles.map((file) => ({
        fileId: file.fileId,
        totalChunks: file.totalChunks,
        ciphertextBytes: file.ciphertextSizes.reduce((sum, size) => sum + size, 0),
        plaintextBytes: file.plaintextSize,
        chunkSize: file.chunkSize,
      })),
    )

    let uploadedCiphertextBytes = 0
    for (const [index, file] of preparedFiles.entries()) {
      logStatus(`Uploading ${file.relativePath} (${index + 1}/${preparedFiles.length})`)
      const uploadUrls = await api.createUploadUrls(
        created.transferId,
        created.manageToken,
        Array.from({ length: file.totalChunks }, (_, chunkIndex) => ({
          fileId: file.fileId,
          chunkIndex,
        })),
      )
      const uploadUrlMap = new Map(uploadUrls.map((item) => [item.chunkIndex, item.url]))
      const completedChunks = await uploadFileChunks({
        transferId: created.transferId,
        file,
        uploadUrlMap,
        rootKey,
        concurrency: options.concurrency,
      })
      uploadedCiphertextBytes += completedChunks.reduce(
        (sum, chunk) => sum + chunk.ciphertextSize,
        0,
      )
      await api.completeChunks(created.transferId, created.manageToken, completedChunks)
      logStatus(
        `Uploaded ${file.relativePath} (${formatBytes(uploadedCiphertextBytes)} / ${formatBytes(totalCiphertextBytes)})`,
      )
    }

    const manifest = {
      version: 1,
      displayName,
      createdAt: new Date().toISOString(),
      chunkSize,
      files: preparedFiles.map((file) => ({
        fileId: file.fileId,
        name: file.name,
        relativePath: file.relativePath,
        mimeType: file.mimeType,
        plaintextSize: file.plaintextSize,
        modifiedAt: file.modifiedAt,
        chunkSize: file.chunkSize,
        totalChunks: file.totalChunks,
        ciphertextSizes: file.ciphertextSizes,
        noncePrefix: toBase64Url(file.noncePrefix),
        metadataStripped: false,
      })),
    }

    const manifestBytes = await encryptManifest(rootKey, manifest)
    const wrappedRootKey = await wrapRootKey(rootKey, linkKey)
    await api.uploadManifest(created.transferId, created.manageToken, toBase64(manifestBytes))
    await api.finalizeTransfer(
      created.transferId,
      created.manageToken,
      wrappedRootKey,
      preparedFiles.length,
      totalCiphertextBytes,
    )

    finalized = true

    if (options.json) {
      process.stdout.write(
        `${JSON.stringify(
          {
            transferId: created.transferId,
            shareUrl: shareUrl.toString(),
            expiresAt: created.expiresAt,
          },
          null,
          2,
        )}\n`,
      )
      return
    }

    process.stdout.write(`${shareUrl.toString()}\n`)
  } finally {
    if (!finalized) {
      await api.deleteTransfer(created.transferId, created.manageToken).catch(() => {})
    }
  }
}

export function parseArgs(argv) {
  const options = {
    server: process.env.XDROP_SERVER?.trim() || '',
    apiUrl: process.env.XDROP_API_URL?.trim() || '',
    expiresInSeconds: DEFAULT_EXPIRY_SECONDS,
    name: '',
    concurrency: 1,
    quiet: false,
    json: false,
    help: false,
    inputs: [],
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
    if (value === '--json') {
      options.json = true
      continue
    }
    if (value === '--quiet') {
      options.quiet = true
      continue
    }
    if (value === '--server') {
      options.server = requireValue(argv, ++index, '--server')
      continue
    }
    if (value === '--api-url') {
      options.apiUrl = requireValue(argv, ++index, '--api-url')
      continue
    }
    if (value === '--expires-in') {
      const parsed = Number.parseInt(requireValue(argv, ++index, '--expires-in'), 10)
      if (!Number.isInteger(parsed) || parsed <= 0) {
        throw new Error('--expires-in must be a positive integer number of seconds.')
      }
      options.expiresInSeconds = parsed
      continue
    }
    if (value === '--name') {
      options.name = requireValue(argv, ++index, '--name')
      continue
    }
    if (value === '--concurrency') {
      const parsed = Number.parseInt(requireValue(argv, ++index, '--concurrency'), 10)
      if (!Number.isInteger(parsed) || parsed <= 0) {
        throw new Error('--concurrency must be a positive integer.')
      }
      options.concurrency = Math.min(parsed, MAX_UPLOAD_CONCURRENCY)
      continue
    }
    if (value.startsWith('--')) {
      throw new Error(`Unknown option: ${value}`)
    }
    options.inputs.push(value)
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

function normalizeSiteUrl(value) {
  const url = new URL(value)
  url.hash = ''
  url.search = ''
  if (url.pathname.endsWith('/api/v1')) {
    url.pathname = url.pathname.slice(0, -'/api/v1'.length) || '/'
  }
  if (!url.pathname.endsWith('/')) {
    url.pathname = `${url.pathname}/`
  }
  return url
}

function normalizeApiUrl(value) {
  const url = new URL(value)
  url.hash = ''
  url.search = ''
  return url.toString().replace(/\/$/u, '')
}

export function resolveApiUrl(serverUrl, apiUrl) {
  return normalizeApiUrl(apiUrl || new URL('/api/v1', serverUrl).toString())
}

export async function collectTransferInputs(inputPaths) {
  const files = []
  const seenPaths = new Set()

  for (const inputPath of inputPaths) {
    const absolutePath = resolve(process.cwd(), inputPath)
    const inputStat = await stat(absolutePath)
    if (inputStat.isDirectory()) {
      const rootName = basename(absolutePath)
      const nestedFiles = await collectDirectoryFiles(absolutePath, rootName)
      files.push(...nestedFiles)
      continue
    }

    if (!inputStat.isFile()) {
      throw new Error(`Only files and directories are supported: ${inputPath}`)
    }

    files.push({
      absolutePath,
      relativePath: basename(absolutePath),
      size: inputStat.size,
      modifiedAt: Math.round(inputStat.mtimeMs),
      name: basename(absolutePath),
      mimeType: mimeTypeFromName(absolutePath),
    })
  }

  for (const file of files) {
    if (seenPaths.has(file.relativePath)) {
      throw new Error(`Duplicate relative path in upload set: ${file.relativePath}`)
    }
    seenPaths.add(file.relativePath)
  }

  return files
}

async function collectDirectoryFiles(directoryPath, relativePrefix) {
  const entries = (await readdir(directoryPath, { withFileTypes: true })).sort((left, right) =>
    left.name.localeCompare(right.name),
  )
  const files = []

  for (const entry of entries) {
    const absolutePath = resolve(directoryPath, entry.name)
    const relativePath = `${relativePrefix}/${entry.name}`.replace(/\\/gu, '/')
    if (entry.isDirectory()) {
      files.push(...(await collectDirectoryFiles(absolutePath, relativePath)))
      continue
    }
    if (!entry.isFile()) {
      continue
    }

    const entryStat = await stat(absolutePath)
    files.push({
      absolutePath,
      relativePath,
      size: entryStat.size,
      modifiedAt: Math.round(entryStat.mtimeMs),
      name: entry.name,
      mimeType: mimeTypeFromName(entry.name),
    })
  }

  return files
}

export function defaultDisplayName(files) {
  if (files.length === 0) {
    return 'Untitled transfer'
  }
  if (files.length === 1) {
    return files[0].relativePath
  }

  const roots = new Set(files.map((file) => file.relativePath.split('/')[0]))
  if (roots.size === 1) {
    return files[0].relativePath.split('/')[0]
  }

  return `${files[0].name} and ${files.length - 1} more items`
}

export function prepareFiles(files, chunkSize) {
  return files.map((file) => {
    const fileId = toBase64Url(randomBytes(18))
    const noncePrefix = randomBytes(8)
    const totalChunks = Math.max(1, Math.ceil(file.size / chunkSize))
    const ciphertextSizes = Array.from({ length: totalChunks }, (_, chunkIndex) => {
      const plaintextChunkSize = Math.min(
        chunkSize,
        Math.max(file.size - chunkIndex * chunkSize, 0),
      )
      return plaintextChunkSize + 16
    })

    return {
      ...file,
      fileId,
      noncePrefix,
      chunkSize,
      totalChunks,
      plaintextSize: file.size,
      ciphertextSizes,
    }
  })
}

async function uploadFileChunks({ transferId, file, uploadUrlMap, rootKey, concurrency }) {
  const completedChunks = new Array(file.totalChunks)
  await parallelLimit(
    Array.from({ length: file.totalChunks }, (_, chunkIndex) => chunkIndex),
    concurrency,
    async (chunkIndex) => {
      const uploadUrl = uploadUrlMap.get(chunkIndex)
      if (!uploadUrl) {
        throw new Error(`Missing upload URL for ${file.relativePath} chunk ${chunkIndex}.`)
      }

      const plaintext = await readFileChunk(
        file.absolutePath,
        chunkIndex * file.chunkSize,
        file.chunkSize,
      )
      const encrypted = await encryptChunk({
        rootKey,
        transferId,
        fileId: file.fileId,
        chunkIndex,
        noncePrefix: file.noncePrefix,
        plaintextChunkSize: plaintext.byteLength,
        plaintext,
      })

      const response = await fetch(uploadUrl, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/octet-stream' },
        body: encrypted.ciphertext,
      })
      if (!response.ok) {
        throw new Error(
          `Chunk upload failed for ${file.relativePath} chunk ${chunkIndex} with ${response.status}.`,
        )
      }

      completedChunks[chunkIndex] = {
        fileId: file.fileId,
        chunkIndex,
        ciphertextSize: encrypted.ciphertext.byteLength,
        checksumSha256: encrypted.checksumHex,
      }
    },
  )

  return completedChunks
}

async function readFileChunk(filePath, start, chunkSize) {
  const fileHandle = await open(filePath, 'r')
  try {
    const buffer = Buffer.alloc(Math.max(0, chunkSize))
    const { bytesRead } = await fileHandle.read(buffer, 0, chunkSize, start)
    return new Uint8Array(buffer.subarray(0, bytesRead))
  } finally {
    await fileHandle.close()
  }
}

async function parallelLimit(items, concurrency, worker) {
  let cursor = 0

  await Promise.all(
    Array.from({ length: Math.min(concurrency, items.length) }, async () => {
      while (cursor < items.length) {
        const index = cursor
        cursor += 1
        const item = items[index]
        if (item === undefined) {
          continue
        }
        await worker(item, index)
      }
    }),
  )
}

async function encryptChunk(options) {
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
  const ciphertext = new Uint8Array(
    await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv,
        additionalData,
      },
      fileKey,
      options.plaintext,
    ),
  )

  return {
    ciphertext,
    checksumHex: createHash('sha256').update(ciphertext).digest('hex'),
  }
}

async function encryptManifest(rootKey, manifest) {
  const manifestKey = await deriveHkdfKey(rootKey, 'manifest')
  const iv = randomBytes(12)
  const ciphertext = new Uint8Array(
    await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv,
      },
      manifestKey,
      encoder.encode(JSON.stringify(manifest)),
    ),
  )

  return encoder.encode(
    JSON.stringify({
      version: MANIFEST_VERSION,
      iv: toBase64Url(iv),
      ciphertext: toBase64(ciphertext),
    }),
  )
}

async function wrapRootKey(rootKey, linkKey) {
  const wrappingKey = await deriveHkdfKey(linkKey, 'wrap-root')
  const iv = randomBytes(12)
  const ciphertext = new Uint8Array(
    await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv,
      },
      wrappingKey,
      rootKey,
    ),
  )

  return JSON.stringify({
    version: WRAP_VERSION,
    iv: toBase64Url(iv),
    ciphertext: toBase64(ciphertext),
  })
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

function randomBytes(length) {
  const value = new Uint8Array(length)
  crypto.getRandomValues(value)
  return value
}

function toBase64Url(input) {
  return Buffer.from(input)
    .toString('base64')
    .replace(/\+/gu, '-')
    .replace(/\//gu, '_')
    .replace(/=+$/u, '')
}

function toBase64(input) {
  return Buffer.from(input).toString('base64')
}

function formatBytes(value) {
  if (value >= 1024 * 1024 * 1024) {
    return `${(value / (1024 * 1024 * 1024)).toFixed(1)} GiB`
  }
  if (value >= 1024 * 1024) {
    return `${(value / (1024 * 1024)).toFixed(1)} MiB`
  }
  if (value >= 1024) {
    return `${(value / 1024).toFixed(1)} KiB`
  }
  return `${value} B`
}

function mimeTypeFromName(filePath) {
  const extension = extname(filePath).toLowerCase()
  return MIME_TYPES[extension] ?? 'application/octet-stream'
}

function logStatus(message) {
  if (quietMode) {
    return
  }
  process.stderr.write(`${message}\n`)
}

class XdropApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl
  }

  async createTransfer(expiresInSeconds) {
    return this.request('/transfers', {
      method: 'POST',
      body: { expiresInSeconds },
    })
  }

  async registerFiles(transferId, manageToken, files) {
    await this.request(`/transfers/${transferId}/files`, {
      method: 'POST',
      token: manageToken,
      body: files,
    })
  }

  async createUploadUrls(transferId, manageToken, chunks) {
    const response = await this.request(`/transfers/${transferId}/upload-urls`, {
      method: 'POST',
      token: manageToken,
      body: { chunks },
    })
    return response.items
  }

  async completeChunks(transferId, manageToken, chunks) {
    await this.request(`/transfers/${transferId}/chunks/complete`, {
      method: 'POST',
      token: manageToken,
      body: chunks,
    })
  }

  async uploadManifest(transferId, manageToken, ciphertextBase64) {
    await this.request(`/transfers/${transferId}/manifest`, {
      method: 'POST',
      token: manageToken,
      body: { ciphertextBase64 },
    })
  }

  async finalizeTransfer(
    transferId,
    manageToken,
    wrappedRootKey,
    totalFiles,
    totalCiphertextBytes,
  ) {
    await this.request(`/transfers/${transferId}/finalize`, {
      method: 'POST',
      token: manageToken,
      body: { wrappedRootKey, totalFiles, totalCiphertextBytes },
    })
  }

  async deleteTransfer(transferId, manageToken) {
    await this.request(`/transfers/${transferId}`, {
      method: 'DELETE',
      token: manageToken,
    })
  }

  async request(path, options) {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: options.method,
      headers: {
        ...(options.body === undefined ? {} : { 'Content-Type': 'application/json' }),
        ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      },
      ...(options.body === undefined ? {} : { body: JSON.stringify(options.body) }),
    })

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}))
      const detail = payload.message ?? payload.error ?? `Request failed with ${response.status}`
      throw new Error(detail)
    }

    if (response.status === 204) {
      return undefined
    }

    return response.json()
  }
}

const MIME_TYPES = {
  '.7z': 'application/x-7z-compressed',
  '.bin': 'application/octet-stream',
  '.csv': 'text/csv',
  '.gif': 'image/gif',
  '.gz': 'application/gzip',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.json': 'application/json',
  '.md': 'text/markdown',
  '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4',
  '.pdf': 'application/pdf',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.tar': 'application/x-tar',
  '.txt': 'text/plain',
  '.wav': 'audio/wav',
  '.webm': 'video/webm',
  '.webp': 'image/webp',
  '.zip': 'application/zip',
}

if (import.meta.main) {
  main().catch((error) => {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
    process.exit(1)
  })
}
