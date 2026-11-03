import { inflateSync } from 'node:zlib';
import { fail, MAX_BYTES } from './common.mjs';

export function imageInfo(bytes) {
  if (bytes.length >= 24 && bytes.subarray(0, 8).equals(Buffer.from('89504e470d0a1a0a', 'hex'))) {
    return { format: 'png', width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
  }
  if (bytes.length >= 12 && bytes.subarray(0, 3).equals(Buffer.from([0xff, 0xd8, 0xff]))) {
    let offset = 2;
    while (offset + 9 < bytes.length) {
      if (bytes[offset] !== 0xff) { offset += 1; continue; }
      const marker = bytes[offset + 1];
      if (marker === 0xd9 || marker === 0xda) break;
      const length = bytes.readUInt16BE(offset + 2);
      if ([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)) {
        return { format: 'jpg', width: bytes.readUInt16BE(offset + 7), height: bytes.readUInt16BE(offset + 5) };
      }
      if (length < 2) break;
      offset += length + 2;
    }
    fail('invalid_image', 'JPEG dimensions could not be read');
  }
  if (bytes.length >= 30 && bytes.toString('ascii', 0, 4) === 'RIFF' && bytes.toString('ascii', 8, 12) === 'WEBP') {
    const kind = bytes.toString('ascii', 12, 16);
    if (kind === 'VP8X') return { format: 'webp', width: 1 + bytes.readUIntLE(24, 3), height: 1 + bytes.readUIntLE(27, 3) };
    if (kind === 'VP8L') {
      const bits = bytes.readUInt32LE(21);
      return { format: 'webp', width: 1 + (bits & 0x3fff), height: 1 + ((bits >> 14) & 0x3fff) };
    }
    if (kind === 'VP8 ' && bytes.length >= 30) return { format: 'webp', width: bytes.readUInt16LE(26) & 0x3fff, height: bytes.readUInt16LE(28) & 0x3fff };
    fail('invalid_image', 'WebP dimensions could not be read');
  }
  fail('invalid_image', 'Only PNG, JPEG, and WebP images are accepted');
}

function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
  }
  return (crc ^ 0xffffffff) >>> 0;
}
export function validateImage(bytes) {
  const info = imageInfo(bytes);
  if (!info.width || !info.height || info.width * info.height > 100_000_000 || bytes.length > MAX_BYTES) fail('invalid_image', 'Image dimensions exceed limits');
  if (info.format === 'png') {
    const compressed = [];
    let offset = 8, ended = false, header;
    while (offset + 12 <= bytes.length) {
      const size = bytes.readUInt32BE(offset);
      const end = offset + 12 + size;
      if (end > bytes.length) fail('invalid_image', 'PNG chunk is truncated');
      const kind = bytes.toString('ascii', offset + 4, offset + 8);
      if (crc32(bytes.subarray(offset + 4, end - 4)) !== bytes.readUInt32BE(end - 4)) fail('invalid_image', 'PNG checksum failed');
      const chunk = bytes.subarray(offset + 8, end - 4);
      if (kind === 'IHDR') {
        if (header || offset !== 8 || size !== 13) fail('invalid_image', 'Invalid PNG header');
        header = chunk;
      }
      if (kind === 'IDAT') compressed.push(chunk);
      if (kind === 'IEND') { ended = size === 0 && end === bytes.length; break; }
      offset = end;
    }
    if (!ended || !header || !compressed.length) fail('invalid_image', 'PNG is incomplete');
    const depth = header[8], color = header[9];
    const channels = { 0: 1, 2: 3, 3: 1, 4: 2, 6: 4 }[color];
    const depths = { 0: [1, 2, 4, 8, 16], 2: [8, 16], 3: [1, 2, 4, 8], 4: [8, 16], 6: [8, 16] }[color];
    if (!channels || !depths.includes(depth) || header[10] !== 0 || header[11] !== 0 || header[12] > 1) fail('invalid_image', 'Unsupported PNG header');
    const passes = header[12] ? [[0,0,8,8],[4,0,8,8],[0,4,4,8],[2,0,4,4],[0,2,2,4],[1,0,2,2],[0,1,1,2]] : [[0,0,1,1]];
    const rows = [];
    let expected = 0;
    for (const [x, y, dx, dy] of passes) {
      const width = Math.max(0, Math.ceil((info.width - x) / dx));
      const height = Math.max(0, Math.ceil((info.height - y) / dy));
      if (!width || !height) continue;
      const row = 1 + Math.ceil(width * channels * depth / 8);
      rows.push({ row, height }); expected += row * height;
    }
    if (expected > MAX_BYTES) fail('invalid_image', 'Decoded PNG exceeds 100 MiB');
    let inflated;
    try { inflated = inflateSync(Buffer.concat(compressed), { maxOutputLength: expected + 1 }); }
    catch { fail('invalid_image', 'PNG decompression failed'); }
    if (inflated.length !== expected) fail('invalid_image', 'PNG pixel rows are incomplete');
    let position = 0;
    for (const { row, height } of rows) for (let y = 0; y < height; y++) {
      if (inflated[position] > 4) fail('invalid_image', 'Invalid PNG filter');
      position += row;
    }
    return { ...info, decoded: false, validation: 'png_chunks_and_inflated_rows', needsHostDecode: true };
  }
  if (info.format === 'jpg') {
    if (bytes[bytes.length - 2] !== 0xff || bytes[bytes.length - 1] !== 0xd9) fail('invalid_image', 'JPEG end marker is missing');
    let offset = 2, scans = 0;
    while (offset < bytes.length) {
      if (bytes[offset++] !== 0xff) fail('invalid_image', 'Invalid JPEG marker');
      while (bytes[offset] === 0xff) offset++;
      const marker = bytes[offset++];
      if (marker === 0xd9) break;
      if (marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) continue;
      if (offset + 2 > bytes.length) fail('invalid_image', 'JPEG marker is truncated');
      const length = bytes.readUInt16BE(offset);
      if (length < 2 || offset + length > bytes.length) fail('invalid_image', 'JPEG segment is truncated');
      offset += length;
      if (marker === 0xda) {
        scans++;
        while (offset < bytes.length) {
          if (bytes[offset] !== 0xff) { offset++; continue; }
          if (bytes[offset + 1] === 0 || (bytes[offset + 1] >= 0xd0 && bytes[offset + 1] <= 0xd7)) { offset += 2; continue; }
          break;
        }
      }
    }
    if (!scans) fail('invalid_image', 'JPEG has no image scan');
  } else {
    if (bytes.readUInt32LE(4) + 8 !== bytes.length) fail('invalid_image', 'WebP length is incomplete');
    let offset = 12, pixels = false;
    while (offset + 8 <= bytes.length) {
      const kind = bytes.toString('ascii', offset, offset + 4);
      const size = bytes.readUInt32LE(offset + 4);
      offset += 8 + size + (size & 1);
      if (offset > bytes.length) fail('invalid_image', 'WebP chunk is truncated');
      if (kind === 'VP8 ' || kind === 'VP8L' || kind === 'ANMF') pixels = true;
    }
    if (!pixels || offset !== bytes.length) fail('invalid_image', 'WebP image data is missing');
  }
  // Node's built-in modules do not decode JPEG/WebP pixels. Report the boundary.
  return { ...info, decoded: false, validation: 'container_and_dimensions', needsHostDecode: true };
}
