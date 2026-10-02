// Minimal ZIP writer for document-container fixtures.
//
// The reader in lib/office.mjs is the subject under test; this writer exists so
// the suite can prove it against containers built byte by byte, with the entry
// set, compression methods and layout a real document writer produces. Entries
// are written stored or deflate-compressed as asked, a central directory and an
// End of Central Directory record close the file, and an optional trailing
// comment exercises the EOCD backward scan.

import zlib from 'node:zlib';

const CRC_TABLE = (() => {
  const table = new Int32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
    table[n] = c;
  }
  return table;
})();

function crc32(buffer) {
  let crc = -1;
  for (let i = 0; i < buffer.length; i++) {
    crc = (crc >>> 8) ^ CRC_TABLE[(crc ^ buffer[i]) & 0xff];
  }
  return (crc ^ -1) >>> 0;
}

const u16 = (v) => { const b = Buffer.alloc(2); b.writeUInt16LE(v & 0xffff, 0); return b; };
const u32 = (v) => { const b = Buffer.alloc(4); b.writeUInt32LE(v >>> 0, 0); return b; };

/**
 * @param {Array<{name: string, data: Buffer|string, compress?: boolean}>} entries
 * @param {{comment?: string}} [options]
 * @returns {Buffer} a complete ZIP container
 */
export function makeZip(entries, { comment = '' } = {}) {
  const localParts = [];
  const centralParts = [];
  let offset = 0;
  for (const entry of entries) {
    const name = Buffer.from(entry.name, 'utf8');
    const raw = Buffer.isBuffer(entry.data) ? entry.data : Buffer.from(entry.data, 'utf8');
    const compress = entry.compress !== false;
    const stored = compress ? zlib.deflateRawSync(raw, { level: 9 }) : raw;
    const method = compress ? 8 : 0;
    const crc = crc32(raw);

    const local = Buffer.concat([
      u32(0x04034b50), u16(20), u16(0x0800), u16(method), u16(0), u16(0),
      u32(crc), u32(stored.length), u32(raw.length), u16(name.length), u16(0),
      name, stored,
    ]);
    localParts.push(local);

    const central = Buffer.concat([
      u32(0x02014b50), u16(20), u16(20), u16(0x0800), u16(method), u16(0), u16(0),
      u32(crc), u32(stored.length), u32(raw.length), u16(name.length),
      u16(0), u16(0), u16(0), u16(0), u32(0), u32(offset),
      name,
    ]);
    centralParts.push(central);
    offset += local.length;
  }

  const central = Buffer.concat(centralParts);
  const commentBuffer = Buffer.from(comment, 'utf8');
  const eocd = Buffer.concat([
    u32(0x06054b50), u16(0), u16(0), u16(entries.length), u16(entries.length),
    u32(central.length), u32(offset), u16(commentBuffer.length),
    commentBuffer,
  ]);
  return Buffer.concat([...localParts, central, eocd]);
}

const xmlEscape = (text) => text
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');

const run = (text) => `<w:r><w:t xml:space="preserve">${xmlEscape(text)}</w:t></w:r>`;

/**
 * A DOCX body: one XML fragment per paragraph spec.
 * @param {Array<{text?: string, heading?: number, title?: boolean,
 *                 deleted?: string, instruction?: string}>} paragraphs
 */
export function docxBody(paragraphs) {
  const parts = paragraphs.map((p) => {
    let style = '';
    if (p.heading) style = `<w:pPr><w:pStyle w:val="Heading${p.heading}"/></w:pPr>`;
    else if (p.title) style = `<w:pPr><w:pStyle w:val="Title"/></w:pPr>`;
    let content = '';
    if (p.text !== undefined) content += run(p.text);
    if (p.deleted !== undefined) {
      content += `<w:r><w:delText xml:space="preserve">${xmlEscape(p.deleted)}</w:delText></w:r>`;
    }
    if (p.instruction !== undefined) {
      content += `<w:r><w:instrText xml:space="preserve">${xmlEscape(p.instruction)}</w:instrText></w:r>`;
    }
    return `<w:p>${style}${content}</w:p>`;
  });
  return parts.join('');
}

/** A complete minimal DOCX container with the given paragraphs. */
export function makeDocx(paragraphs, { comment } = {}) {
  const document = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>${docxBody(paragraphs)}<w:sectPr/></w:body>
</w:document>`;
  return makeZip([
    { name: '[Content_Types].xml', data: '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>', compress: false },
    { name: 'word/document.xml', data: document },
    { name: '_rels/.rels', data: '<?xml version="1.0"?><Relationships/>' },
  ], { comment });
}

/** A complete minimal ODT container with the given paragraph texts. */
export function makeOdt(paragraphs) {
  const body = paragraphs.map((p) => {
    if (typeof p === 'string') return `<text:p>${xmlEscape(p)}</text:p>`;
    return `<text:h text:outline-level="${p.heading}">${xmlEscape(p.text)}</text:h>`;
  }).join('');
  const content = `<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
<office:body><office:text>${body}</office:text></office:body>
</office:document-content>`;
  return makeZip([
    { name: 'mimetype', data: 'application/vnd.oasis.opendocument.text', compress: false },
    { name: 'content.xml', data: content },
    { name: 'META-INF/manifest.xml', data: '<?xml version="1.0"?><manifest:manifest/>' },
  ]);
}
