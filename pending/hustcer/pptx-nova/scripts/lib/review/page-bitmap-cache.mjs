import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, statSync } from 'node:fs'
import { delimiter, join, resolve } from 'node:path'
import { inflateSync } from 'node:zlib'
import { renderContextForDate } from './render-context.mjs'

const RGB_CACHE_MAGIC = Buffer.from('XDRGB04\n')
const RGB_CACHE_HEADER_BYTES = 100
const MAX_RGB_CACHE_BYTES = 360_000_000

const CRC32_TABLE = Array.from({ length: 256 }, (_, index) => {
  let value = index
  for (let bit = 0; bit < 8; bit += 1) {
    value = (value & 1) === 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1
  }
  return value >>> 0
})

function crc32(buffer) {
  let value = 0xffffffff
  for (const byte of buffer) value = CRC32_TABLE[(value ^ byte) & 0xff] ^ (value >>> 8)
  return (value ^ 0xffffffff) >>> 0
}

export function isValidPageBitmapCacheEntry(path, { dpi, slide, identity, pdfSha256 } = {}) {
  if (!existsSync(path)) return false
  try {
    const state = statSync(path)
    if (!state.isFile() || state.size < RGB_CACHE_HEADER_BYTES) return false
    const record = readFileSync(path)
    if (!record.subarray(0, 8).equals(RGB_CACHE_MAGIC)) return false
    const width = record.readUInt32LE(8)
    const height = record.readUInt32LE(12)
    const rawSize = record.readUInt32LE(16)
    const compressedSize = record.readUInt32LE(20)
    const expectedCrc = record.readUInt32LE(24)
    const cachedDpi = record.readUInt32LE(28)
    const cachedSlide = record.readUInt32LE(32)
    const cachedIdentity = record.subarray(36, 68).toString('hex')
    const cachedPdfSha256 = record.subarray(68, 100).toString('hex')
    if (
      width === 0 ||
      height === 0 ||
      rawSize === 0 ||
      rawSize > MAX_RGB_CACHE_BYTES ||
      width * height * 3 !== rawSize ||
      compressedSize === 0 ||
      (dpi !== undefined && cachedDpi !== dpi) ||
      (slide !== undefined && cachedSlide !== slide) ||
      (identity !== undefined && cachedIdentity !== identity) ||
      (pdfSha256 !== undefined && cachedPdfSha256 !== pdfSha256) ||
      RGB_CACHE_HEADER_BYTES + compressedSize !== record.length
    ) {
      return false
    }
    const pixels = inflateSync(record.subarray(RGB_CACHE_HEADER_BYTES), {
      maxOutputLength: rawSize,
    })
    return pixels.length === rawSize && crc32(pixels) === expectedCrc
  } catch {
    return false
  }
}

function sha256File(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

function resolveExecutable(bin) {
  if (bin.includes('/') || bin.includes('\\')) return resolve(bin)
  for (const directory of String(process.env.PATH ?? '').split(delimiter)) {
    if (!directory) continue
    const candidate = join(directory, bin)
    if (existsSync(candidate) && statSync(candidate).isFile()) return resolve(candidate)
  }
  return bin
}

export function createPageBitmapCacheBinding({
  cacheDir,
  pptxPath,
  dpi,
  xdocBin,
  renderContext = renderContextForDate(),
}) {
  const pptxSha256 = sha256File(pptxPath)
  const executable = resolveExecutable(xdocBin)
  const rendererVersion =
    existsSync(executable) && statSync(executable).isFile()
      ? sha256File(executable)
      : createHash('sha256').update(`unresolved:${executable}`).digest('hex')
  const identity = createHash('sha256')
    .update(
      JSON.stringify({
        schemaVersion: 'pptx-nova-page-bitmap-cache-key/v2',
        pptxSha256,
        dpi,
        rendererVersion,
        renderContext,
      }),
    )
    .digest('hex')
  const directory = join(
    resolve(cacheDir),
    'page-bitmap-v2',
    pptxSha256,
    String(dpi),
    rendererVersion,
    `id-${identity}`,
  )
  mkdirSync(directory, { recursive: true })
  return {
    schemaVersion: 'pptx-nova-page-bitmap-cache-key/v2',
    pptxSha256,
    dpi,
    rendererVersion,
    renderContext,
    identity,
    prefix: join(directory, 'page'),
  }
}

export function pageBitmapCachePath(binding, slide) {
  return `${binding.prefix}-slide-${String(slide).padStart(6, '0')}.rgbz`
}

export function snapshotPageBitmapCache(binding, slides) {
  const cachedSlides = slides.filter((slide) =>
    isValidPageBitmapCacheEntry(pageBitmapCachePath(binding, slide), {
      dpi: binding.dpi,
      slide,
      identity: binding.identity,
    }),
  )
  return {
    requestedSlides: slides,
    cachedSlides,
    pdfHashes: Object.fromEntries(
      cachedSlides.map((slide) => [
        slide,
        readFileSync(pageBitmapCachePath(binding, slide)).subarray(68, 100).toString('hex'),
      ]),
    ),
    hitCount: cachedSlides.length,
    missCount: slides.length - cachedSlides.length,
  }
}

export function pageBitmapCacheMetrics(binding, before, after) {
  const retainedHits = before.cachedSlides.filter(
    (slide) =>
      after.cachedSlides.includes(slide) && before.pdfHashes[slide] === after.pdfHashes[slide],
  ).length
  return {
    schemaVersion: binding.schemaVersion,
    pptxSha256: binding.pptxSha256,
    dpi: binding.dpi,
    rendererVersion: binding.rendererVersion,
    requestedPageCount: before.requestedSlides.length,
    hitCount: retainedHits,
    missCount: before.requestedSlides.length - retainedHits,
    populatedCount: after.hitCount - retainedHits,
    invalidatedCount: before.hitCount - retainedHits,
    complete: after.missCount === 0,
  }
}
