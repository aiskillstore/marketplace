#!/usr/bin/env node
import { fileURLToPath } from 'node:url'
import { loadContent } from '../../shared/core-primitives.kit.mjs'
import { validateDeckkitContent } from '../../shared/validate-deckkit.mjs'
import { createDeck } from '../teal-journal.kit.mjs'
const content = await loadContent(
  process.argv[2] ?? fileURLToPath(new URL('./content.json', import.meta.url)),
)
const validation = validateDeckkitContent(content, { deckkit: 'teal-journal', mode: 'delivery' })
if (!validation.valid) {
  console.error(JSON.stringify(validation.errors))
  process.exit(1)
}
process.stdout.write(JSON.stringify(createDeck(content).patch, null, 2))
