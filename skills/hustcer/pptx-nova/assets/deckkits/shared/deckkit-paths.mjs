import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

// Anchor resource lookup to the distributed skill, independently of cwd.
export const DECKKIT_ROOT = fileURLToPath(new URL('../', import.meta.url))
export const deckkitSchemaPath = (id, type) =>
  join(DECKKIT_ROOT, id, 'schemas', `${type}.schema.json`)
