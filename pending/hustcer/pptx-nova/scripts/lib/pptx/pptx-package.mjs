// Read-only OPC/XML access for evidence, not a full OOXML validator.
import { readFileSync } from 'node:fs'
import { posix } from 'node:path'
import { inflateRawSync } from 'node:zlib'

const EOCD_SIGNATURE = 0x06054b50
const CENTRAL_DIRECTORY_SIGNATURE = 0x02014b50
const LOCAL_FILE_SIGNATURE = 0x04034b50

function findEndOfCentralDirectory(bytes) {
  const minimum = Math.max(0, bytes.length - 65_557)
  for (let offset = bytes.length - 22; offset >= minimum; offset -= 1) {
    if (bytes.readUInt32LE(offset) === EOCD_SIGNATURE) return offset
  }
  throw new Error('PPTX ZIP central directory was not found')
}

function readZipEntries(path) {
  const bytes = readFileSync(path)
  const eocd = findEndOfCentralDirectory(bytes)
  const entryCount = bytes.readUInt16LE(eocd + 10)
  let offset = bytes.readUInt32LE(eocd + 16)
  const entries = new Map()

  for (let index = 0; index < entryCount; index += 1) {
    if (bytes.readUInt32LE(offset) !== CENTRAL_DIRECTORY_SIGNATURE) {
      throw new Error(`Invalid PPTX ZIP central directory entry at offset ${offset}`)
    }
    const flags = bytes.readUInt16LE(offset + 8)
    const compression = bytes.readUInt16LE(offset + 10)
    const compressedSize = bytes.readUInt32LE(offset + 20)
    const uncompressedSize = bytes.readUInt32LE(offset + 24)
    const nameLength = bytes.readUInt16LE(offset + 28)
    const extraLength = bytes.readUInt16LE(offset + 30)
    const commentLength = bytes.readUInt16LE(offset + 32)
    const localHeaderOffset = bytes.readUInt32LE(offset + 42)
    const name = bytes.subarray(offset + 46, offset + 46 + nameLength).toString('utf8')
    entries.set(name, {
      bytes,
      name,
      flags,
      compression,
      compressedSize,
      uncompressedSize,
      localHeaderOffset,
    })
    offset += 46 + nameLength + extraLength + commentLength
  }
  return entries
}

function readZipEntry(entry) {
  if ((entry.flags & 0x1) !== 0)
    throw new Error(`Encrypted ZIP entry is unsupported: ${entry.name}`)
  const bytes = entry.bytes
  const offset = entry.localHeaderOffset
  if (bytes.readUInt32LE(offset) !== LOCAL_FILE_SIGNATURE) {
    throw new Error(`Invalid PPTX ZIP local header for ${entry.name}`)
  }
  const nameLength = bytes.readUInt16LE(offset + 26)
  const extraLength = bytes.readUInt16LE(offset + 28)
  const start = offset + 30 + nameLength + extraLength
  const compressed = bytes.subarray(start, start + entry.compressedSize)
  let result
  if (entry.compression === 0) result = compressed
  else if (entry.compression === 8)
    result = inflateRawSync(compressed, { maxOutputLength: 64 * 1024 * 1024 })
  else throw new Error(`Unsupported PPTX ZIP compression method ${entry.compression}`)
  if (result.length !== entry.uncompressedSize) {
    throw new Error(`PPTX ZIP entry size mismatch for ${entry.name}`)
  }
  return result
}

const P = new Set([
  'http://schemas.openxmlformats.org/presentationml/2006/main',
  'http://purl.oclc.org/ooxml/presentationml/main',
])
const R = new Set([
  'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
  'http://purl.oclc.org/ooxml/officeDocument/relationships',
])
const CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
const REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
const MIME = 'application/vnd.openxmlformats-officedocument.presentationml.'
const CHARTEX = 'application/vnd.ms-office.chartex+xml'

function decodeEntities(text) {
  return text.replace(/&([^;]*);/g, (_, entity) => {
    const named = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" }
    if (Object.hasOwn(named, entity)) return named[entity]
    if (/^#(?:[0-9]+|x[0-9a-f]+)$/i.test(entity)) {
      const code = entity[1] === 'x' ? parseInt(entity.slice(2), 16) : Number(entity.slice(1))
      if (code > 0 && code <= 0x10ffff && !(code >= 0xd800 && code <= 0xdfff))
        return String.fromCodePoint(code)
    }
    throw new Error('Unsupported XML entity in OPC metadata')
  })
}

// Small namespace-aware tree reader: no DTD, external entities or XML editing.
// Consumers interpret the returned namespace-aware trees; this reader never edits XML.
function xmlTree(bytes) {
  if (bytes.length > 64 * 1024 * 1024) throw new Error('OPC XML exceeds 64 MiB')
  const encoding =
    bytes[0] === 0xff && bytes[1] === 0xfe
      ? 'utf-16le'
      : bytes[0] === 0xfe && bytes[1] === 0xff
        ? 'utf-16be'
        : 'utf-8'
  const xml = new TextDecoder(encoding, { fatal: true }).decode(bytes)
  const stack = []
  let root = null
  const tokens =
    /<!--[^]*?-->|<\?[^]*?\?>|<!\[CDATA\[[^]*?\]\]>|<\/?[^<>"']*(?:(?:"[^"]*"|'[^']*')[^<>"']*)*>|[^<]+/gy
  let offset = 0
  for (;;) {
    tokens.lastIndex = offset
    const match = tokens.exec(xml)
    if (!match) break
    const token = match[0]
    offset = tokens.lastIndex
    if (token.startsWith('<!--') || token.startsWith('<?')) continue
    if (!token.startsWith('<') || token.startsWith('<![CDATA[')) {
      if (!stack.length && token.trim()) throw new Error('Text outside OPC XML root')
      if (stack.length)
        stack.at(-1).text += token.startsWith('<![CDATA[')
          ? token.slice(9, -3)
          : decodeEntities(token)
      continue
    }
    if (token.startsWith('<!')) throw new Error('DTD is unsupported in OPC metadata')
    if (token.startsWith('</')) {
      if (stack.pop()?.qname !== token.slice(2, -1).trim()) throw new Error('Unbalanced OPC XML')
      continue
    }
    const tag = token.match(/^<([A-Za-z_][\w.:-]*)([^]*?)\/?\s*>$/)
    if (!tag) throw new Error('Unsupported OPC XML tag')
    const attrs = new Map()
    let rest = tag[2]
    while (rest.trim()) {
      const attribute = rest.match(/^\s+([A-Za-z_][\w.:-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')/)
      if (!attribute || attrs.has(attribute[1])) throw new Error('Invalid OPC XML attribute')
      attrs.set(attribute[1], decodeEntities(attribute[2] ?? attribute[3]))
      rest = rest.slice(attribute[0].length)
    }
    const ns = new Map(stack.at(-1)?.ns ?? [['xml', 'http://www.w3.org/XML/1998/namespace']])
    for (const [name, value] of attrs) {
      if (name === 'xmlns') ns.set('', value)
      else if (name.startsWith('xmlns:')) ns.set(name.slice(6), value)
    }
    function expanded(name, attribute = false) {
      const segments = name.split(':')
      if (segments.length > 2) throw new Error('Invalid OPC XML qualified name')
      const prefix = segments.length === 2 ? segments[0] : ''
      if (prefix && !ns.has(prefix)) throw new Error('Unbound OPC XML prefix')
      return { local: segments.at(-1), uri: !prefix && attribute ? '' : (ns.get(prefix) ?? '') }
    }
    const node = { ...expanded(tag[1]), qname: tag[1], ns, attrs: [], children: [], text: '' }
    for (const [name, value] of attrs) {
      if (name !== 'xmlns' && !name.startsWith('xmlns:'))
        node.attrs.push({ ...expanded(name, true), value })
    }
    if (stack.length) stack.at(-1).children.push(node)
    else if (root) throw new Error('Multiple OPC XML roots')
    else root = node
    if (!/\/\s*>$/.test(token)) stack.push(node)
    if (stack.length > 256) throw new Error('OPC XML depth exceeds 256')
  }
  if (offset !== xml.length || stack.length || !root) throw new Error('Malformed OPC XML')
  return root
}

function attr(node, local, namespaces = new Set([''])) {
  const matches = node.attrs.filter((a) => a.local === local && namespaces.has(a.uri))
  if (matches.length > 1) throw new Error(`Ambiguous OPC attribute: ${local}`)
  return matches[0]?.value
}

function targetPart(owner, target) {
  if (
    !target ||
    // eslint-disable-next-line no-control-regex -- Reject control bytes in untrusted OPC targets.
    /[\\\x00-\x20]/.test(target) ||
    /^[a-z][a-z0-9+.-]*:/i.test(target) ||
    target.startsWith('//') ||
    /[?#]|%2f|%5c/i.test(target)
  )
    throw new Error(`Invalid OPC target: ${target}`)
  const decoded = decodeURIComponent(target)
  const part = posix.normalize(
    decoded.startsWith('/') ? decoded.slice(1) : posix.join(posix.dirname(owner), decoded),
  )
  // eslint-disable-next-line no-control-regex -- Recheck control bytes after percent decoding.
  if (part === '..' || part.startsWith('../') || part.startsWith('/') || /[\\\x00-\x1f]/.test(part))
    throw new Error('OPC target escapes package')
  return part
}

export function readPptxPackage(path) {
  const entries = readZipEntries(path)
  const cache = new Map()
  const root = (part) => {
    if (!entries.has(part)) throw new Error(`Missing OPC part: ${part}`)
    if (!cache.has(part)) cache.set(part, xmlTree(readZipEntry(entries.get(part))))
    return cache.get(part)
  }
  const types = root('[Content_Types].xml')
  if (types.uri !== CT || types.local !== 'Types') throw new Error('Invalid OPC content types')
  const overrides = new Map()
  const defaults = new Map()
  for (const node of types.children) {
    if (node.uri !== CT) continue
    const key = attr(node, node.local === 'Override' ? 'PartName' : 'Extension')
    const type = attr(node, 'ContentType')
    if (!key || !type || !['Override', 'Default'].includes(node.local))
      throw new Error('Invalid OPC content type entry')
    const table = node.local === 'Override' ? overrides : defaults
    const normalized = node.local === 'Override' ? targetPart('', key) : key.toLowerCase()
    if (table.has(normalized)) throw new Error('Duplicate OPC content type entry')
    table.set(normalized, type)
  }
  const contentType = (part) =>
    overrides.get(part) ?? defaults.get(posix.extname(part).slice(1).toLowerCase()) ?? ''
  const sharedParts = [...entries.keys()]
    .filter((part) =>
      ['slideLayout+xml', 'slideMaster+xml'].some((suffix) => contentType(part) === MIME + suffix),
    )
    .sort()
  const chartExParts = [...entries.keys()].filter((part) => contentType(part) === CHARTEX).sort()
  function relations(owner) {
    const part = posix.join(posix.dirname(owner), '_rels', posix.basename(owner) + '.rels')
    if (!entries.has(part)) return []
    const document = root(part)
    if (document.uri !== REL || document.local !== 'Relationships')
      throw new Error('Invalid OPC relationships')
    const ids = new Set()
    return document.children
      .filter((n) => n.uri === REL && n.local === 'Relationship')
      .map((node) => {
        const id = attr(node, 'Id')
        const type = attr(node, 'Type')
        const target = attr(node, 'Target')
        if (!id || !type || !target || ids.has(id))
          throw new Error('Invalid or duplicate OPC relationship')
        ids.add(id)
        return { id, type, target, external: attr(node, 'TargetMode') === 'External' }
      })
  }
  function internalTarget(owner, edge, expected) {
    if (edge.external) throw new Error('Expected internal OPC relationship')
    const part = targetPart(owner, edge.target)
    if (!entries.has(part) || contentType(part) !== expected)
      throw new Error(`Missing or wrong-type OPC target: ${part}`)
    return part
  }
  function slides() {
    const owner = 'ppt/presentation.xml'
    const document = root(owner)
    if (!P.has(document.uri) || document.local !== 'presentation')
      throw new Error('Invalid presentation root')
    const edges = relations(owner)
    const list = document.children.find((n) => P.has(n.uri) && n.local === 'sldIdLst')
    const seen = new Set()
    return (list?.children ?? [])
      .filter((n) => P.has(n.uri) && n.local === 'sldId')
      .map((node, index) => {
        const edge = edges.find((e) => e.id === attr(node, 'id', R))
        if (!edge || ![...R].some((ns) => edge.type === `${ns}/slide`))
          throw new Error('Invalid registered slide relationship')
        const part = internalTarget(owner, edge, MIME + 'slide+xml')
        if (seen.has(part)) throw new Error('Duplicate registered slide')
        seen.add(part)
        const slide = root(part)
        if (!P.has(slide.uri) || slide.local !== 'sld') throw new Error('Invalid slide root')
        const show = attr(slide, 'show')
        if (show !== undefined && !['0', '1', 'false', 'true'].includes(show))
          throw new Error('Invalid slide visibility')
        return { slide: index + 1, part, hidden: show === '0' || show === 'false' }
      })
  }
  function chartExScope() {
    const mapped = new Set()
    const chartExSlides = []
    if (chartExParts.length)
      for (const slide of slides()) {
        const pending = [slide.part]
        const visited = new Set()
        let found = false
        while (pending.length) {
          const owner = pending.pop()
          if (visited.has(owner)) continue
          visited.add(owner)
          for (const edge of relations(owner)) {
            if (edge.type === 'http://schemas.microsoft.com/office/2014/relationships/chartEx') {
              mapped.add(internalTarget(owner, edge, CHARTEX))
              found = true
            } else
              for (const kind of ['slideLayout', 'slideMaster']) {
                // A master's layout registry lists siblings, not inherited content.
                if (kind === 'slideLayout' && contentType(owner) === MIME + 'slideMaster+xml')
                  continue
                if ([...R].some((ns) => edge.type === `${ns}/${kind}`))
                  pending.push(internalTarget(owner, edge, MIME + kind + '+xml'))
              }
          }
        }
        if (found) chartExSlides.push(slide.slide)
      }
    return {
      hasChartEx: chartExParts.length > 0,
      chartExParts,
      chartExSlides,
      unmappedParts: chartExParts.filter((part) => !mapped.has(part)),
    }
  }
  const relatedPart = (owner, id) => {
    const edge = relations(owner).find((e) => e.id === id)
    if (!edge || edge.external) throw new Error(`Missing internal OPC relationship: ${owner}#${id}`)
    const part = targetPart(owner, edge.target)
    if (!entries.has(part)) throw new Error(`Missing OPC relationship target: ${part}`)
    return part
  }
  return { sharedParts, slides, chartExScope, partTree: root, relatedPart }
}
