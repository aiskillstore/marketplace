import { existsSync, readFileSync, realpathSync, statSync } from 'node:fs'
import { dirname, extname, isAbsolute, relative, sep } from 'node:path'
import { resolveFilesystemPath } from '../runtime/filesystem-paths.mjs'

export const ASSETS_MANIFEST_SCHEMA_VERSION = 'pptx-nova-assets-manifest/v1'

const READY_STATUSES = new Set(['available', 'generated', 'rendered'])
const IMAGE_KINDS = new Set(['image', 'screenshot', 'photo', 'illustration', 'logo'])
const FIT_POLICIES = new Set(['cover', 'contain', 'no-crop', 'crop-safe'])
const IMAGE_RATIOS = new Set(['21:9', '16:10', '16:9', '4:3', '3:2', '3:4', '1:1'])
const MIME_BY_EXTENSION = new Map([
  ['.apng', 'image/apng'],
  ['.gif', 'image/gif'],
  ['.jpeg', 'image/jpeg'],
  ['.jpg', 'image/jpeg'],
  ['.png', 'image/png'],
  ['.svg', 'image/svg+xml'],
  ['.webp', 'image/webp'],
])

function entriesOf(manifest) {
  if (manifest && Object.hasOwn(manifest, 'entries')) {
    if (!Array.isArray(manifest.entries))
      throw new Error('assets_manifest.json entries must be an array')
    return manifest.entries
  }
  if (manifest && Object.hasOwn(manifest, 'assets')) {
    if (!Array.isArray(manifest.assets))
      throw new Error('assets_manifest.json assets must be an array')
    return manifest.assets
  }
  throw new Error('assets_manifest.json must contain an entries or assets array')
}

function normalizePath(value) {
  return String(value ?? '')
    .trim()
    .replace(/\\/g, '/')
    .replace(/^(?:\.\/)+/, '')
    .replace(/\/+/g, '/')
}

function isPortableAbsolutePath(value) {
  const text = String(value ?? '').trim()
  return isAbsolute(text) || /^[A-Za-z]:[\\/]/.test(text) || /^\\\\/.test(text)
}

function imageSlotOf(entry) {
  const pptxUse = entry?.pptxUse && typeof entry.pptxUse === 'object' ? entry.pptxUse : {}
  const slot = entry?.slot && typeof entry.slot === 'object' ? entry.slot : {}
  const nested = pptxUse.slot && typeof pptxUse.slot === 'object' ? pptxUse.slot : {}
  return {
    id: pptxUse.slotId ?? nested.id ?? slot.id ?? entry?.slotId ?? '',
    ratio: pptxUse.ratio ?? nested.ratio ?? slot.ratio ?? '',
    fitPolicy:
      pptxUse.fitPolicy ??
      nested.fitPolicy ??
      slot.fitPolicy ??
      pptxUse.crop ??
      nested.crop ??
      slot.crop ??
      'contain',
  }
}

function sourcePathOf(entry) {
  return (
    entry?.path ?? entry?.pptxUse?.path ?? entry?.assetSource?.path ?? entry?.source?.path ?? ''
  )
}

function mimeOf(entry, path) {
  const explicit = entry?.mime ?? entry?.pptxUse?.mime ?? entry?.assetSource?.mime
  const extension = extname(String(path)).toLowerCase()
  const derived = MIME_BY_EXTENSION.get(extension) ?? ''
  if (explicit) {
    const mime = String(explicit).trim().toLowerCase()
    if (!mime.startsWith('image/')) return mime
    if (derived && mime !== derived) {
      throw new Error(
        `asset "${entry.id}" MIME ${mime} does not match file extension ${extension}; use ${derived}`,
      )
    }
    return mime
  }
  return derived
}

function isWithin(root, candidate) {
  const rel = relative(root, candidate)
  return rel === '' || (rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel))
}

function resolveLocalAssetPath(manifest, manifestPath, entry) {
  const sourcePath = String(sourcePathOf(entry) ?? '').trim()
  const raw = normalizePath(sourcePath)
  if (!raw) throw new Error(`asset "${entry?.id ?? '<unknown>'}" is missing a local path`)
  if (/^(?:https?:\/\/|data:)/i.test(sourcePath)) {
    throw new Error(`asset "${entry.id}" must use a local file path, not ${sourcePath}`)
  }
  if (isPortableAbsolutePath(sourcePath)) {
    throw new Error(
      `asset "${entry.id}" uses an absolute path; move it below the manifest assetRoot and use a relative path`,
    )
  }

  const baseDir = realpathSync.native(dirname(manifestPath))
  const assetRoot = normalizePath(manifest.assetRoot || '')
  const rootDir = resolveFilesystemPath(assetRoot || '.', baseDir)
  if (!isWithin(baseDir, rootDir)) {
    throw new Error(
      `assets_manifest.json assetRoot must stay inside the manifest directory: ${manifest.assetRoot}`,
    )
  }
  if (!existsSync(rootDir) || !statSync(rootDir).isDirectory()) {
    throw new Error(
      `assets_manifest.json assetRoot does not exist or is not a directory: ${assetRoot || '.'}`,
    )
  }

  const candidate =
    assetRoot && raw !== assetRoot && !raw.startsWith(`${assetRoot}/`)
      ? resolveFilesystemPath(raw, rootDir)
      : resolveFilesystemPath(raw, baseDir)
  if (!isWithin(rootDir, candidate)) {
    throw new Error(`asset "${entry.id}" resolves outside the manifest assetRoot: ${raw}`)
  }
  if (!existsSync(candidate) || !statSync(candidate).isFile()) {
    throw new Error(
      `asset "${entry.id}" file does not exist: ${raw}; check assets_manifest.json and the manifest directory`,
    )
  }

  const realBaseDir = realpathSync.native(baseDir)
  const realRootDir = realpathSync.native(rootDir)
  const realCandidate = realpathSync.native(candidate)
  if (!isWithin(realBaseDir, realRootDir) || !isWithin(realRootDir, realCandidate)) {
    throw new Error(`asset "${entry.id}" resolves outside the manifest assetRoot: ${raw}`)
  }

  return {
    path: normalizePath(relative(baseDir, candidate)),
    absolutePath: candidate,
  }
}

function normalizeEntry(entry, manifest, manifestPath) {
  if (!entry || typeof entry !== 'object')
    throw new Error('assets_manifest.json contains a non-object entry')
  const id = String(entry.id ?? '').trim()
  if (!id) throw new Error('assets_manifest.json contains an asset entry without an id')
  const status = String(entry.status ?? 'available').toLowerCase()
  if (!READY_STATUSES.has(status)) {
    throw new Error(`asset "${id}" is not ready for insertion: status=${status}`)
  }
  const kind = String(entry.kind ?? '').toLowerCase()
  if (!IMAGE_KINDS.has(kind)) throw new Error(`asset "${id}" is not an image asset: kind=${kind}`)
  const path = resolveLocalAssetPath(manifest, manifestPath, entry)
  const mime = mimeOf(entry, path.path)
  if (!mime.startsWith('image/') || !MIME_BY_EXTENSION.has(extname(path.path).toLowerCase())) {
    throw new Error(
      `asset "${id}" has no supported image MIME type; use a local PNG, JPEG, GIF, APNG, SVG, WebP, or matching MIME`,
    )
  }
  const slot = imageSlotOf(entry)
  if (!slot.ratio) {
    throw new Error(
      `image asset "${id}" must declare pptxUse.ratio (for example 16:9) before it can fill a DeckKit slot`,
    )
  }
  if (!IMAGE_RATIOS.has(String(slot.ratio))) {
    throw new Error(`asset "${id}" uses unsupported image ratio "${slot.ratio}"`)
  }
  if (!FIT_POLICIES.has(String(slot.fitPolicy))) {
    throw new Error(`asset "${id}" uses unsupported fitPolicy "${slot.fitPolicy}"`)
  }
  return {
    id,
    kind,
    path: path.path,
    absolutePath: path.absolutePath,
    mime,
    ratio: slot.ratio,
    fitPolicy: slot.fitPolicy || 'contain',
    slotId: slot.id || '',
    entry,
  }
}

export function readAssetManifest(path) {
  if (!existsSync(path)) throw new Error(`assets_manifest.json does not exist: ${path}`)
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    throw new Error(`assets_manifest.json is not valid JSON: ${error.message}`)
  }
}

export function createAssetContext(manifest, manifestPath) {
  if (!manifest || typeof manifest !== 'object') {
    throw new Error('assets_manifest.json must contain an object')
  }
  if (manifest.schemaVersion !== ASSETS_MANIFEST_SCHEMA_VERSION) {
    throw new Error(`assets_manifest.json schemaVersion must be ${ASSETS_MANIFEST_SCHEMA_VERSION}`)
  }
  const absoluteManifestPath = resolveFilesystemPath(manifestPath)
  const rawEntries = entriesOf(manifest)
  const byId = new Map()
  for (const entry of rawEntries) {
    if (!entry || typeof entry !== 'object') {
      throw new Error('assets_manifest.json contains a non-object entry')
    }
    const id = String(entry.id ?? '').trim()
    if (!id) throw new Error('assets_manifest.json contains an asset entry without an id')
    if (byId.has(id)) throw new Error(`duplicate asset id in assets_manifest.json: ${id}`)
    byId.set(id, entry)
  }
  const normalizedCache = new Map()
  const normalizeById = (id) => {
    const key = String(id ?? '')
    if (!byId.has(key)) return null
    if (!normalizedCache.has(key)) {
      normalizedCache.set(key, normalizeEntry(byId.get(key), manifest, absoluteManifestPath))
    }
    return normalizedCache.get(key)
  }

  return {
    manifestPath: absoluteManifestPath,
    assetRoot: dirname(absoluteManifestPath),
    get(id) {
      return normalizeById(id)
    },
    resolveImageSlot(slide, slotId) {
      const slots = slide?.imageSlots
      if (!slots || typeof slots !== 'object' || Array.isArray(slots) || !(slotId in slots))
        return null
      const assetId = String(slots[slotId] ?? '').trim()
      if (!assetId) throw new Error(`image slot "${slotId}" must reference a non-empty asset id`)
      const asset = normalizeById(assetId)
      if (!asset) {
        throw new Error(
          `image slot "${slotId}" references unknown asset "${assetId}"; add it to assets_manifest.json`,
        )
      }
      if (asset.slotId && asset.slotId !== slotId) {
        throw new Error(
          `asset "${assetId}" is registered for slot "${asset.slotId}", not "${slotId}"`,
        )
      }
      return asset
    },
  }
}
