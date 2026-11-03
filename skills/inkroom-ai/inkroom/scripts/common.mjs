import { randomUUID } from 'node:crypto';
import { chmod, mkdir, rename, writeFile, unlink } from 'node:fs/promises';
import { dirname } from 'node:path';

export const MAX_BYTES = 100 * 1024 * 1024;
export function fail(code, message, details = {}) {
  const error = new Error(message);
  Object.assign(error, { code, details });
  throw error;
}
export async function atomicWrite(path, data, mode = 0o600) {
  await mkdir(dirname(path), { recursive: true, mode: 0o700 });
  const temporary = `${path}.${process.pid}.${randomUUID()}.tmp`;
  try {
    await writeFile(temporary, data, { mode });
    await rename(temporary, path);
    await chmod(path, mode);
  } finally {
    await unlink(temporary).catch(() => {});
  }
}
export async function readResponseBytes(response) {
  const chunks = [];
  let size = 0;
  try {
    for await (const chunk of response.body || []) {
      size += chunk.length;
      if (size > MAX_BYTES) fail('response_too_large', 'Response exceeds 100 MiB');
      chunks.push(Buffer.from(chunk));
    }
  } catch (error) {
    error.details = { ...(error.details || {}), response: Buffer.concat(chunks) };
    throw error;
  }
  return Buffer.concat(chunks);
}
