import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

export const SKILL_ROOT = fileURLToPath(new URL('../../../', import.meta.url))
export const cliPath = (name) => join(SKILL_ROOT, 'scripts/cli', name)
