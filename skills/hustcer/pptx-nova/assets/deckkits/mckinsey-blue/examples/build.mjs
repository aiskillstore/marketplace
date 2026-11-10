#!/usr/bin/env node
// mckinsey-blue-build.mjs - content -> McKinsey-blue DeckKit -> patch
import { loadContent } from '../../shared/core-primitives.kit.mjs'
import { validateDeckkitContent } from '../../shared/validate-deckkit.mjs'
import { createDeck } from '../mckinsey-blue.kit.mjs'
import { fileURLToPath } from 'node:url'

const deckkitId = 'mckinsey-blue'
const content = await loadContent(
  process.argv[2] ?? fileURLToPath(new URL('./content.json', import.meta.url)),
)

const validation = validateDeckkitContent(content, { deckkit: deckkitId, mode: 'delivery' })
const { errors, warnings: valWarnings, fitDiagnostics } = validation
const blockingFitDiagnostics = fitDiagnostics.filter((d) => d.blocking === true)
if (errors.length > 0 || blockingFitDiagnostics.length > 0) {
  for (const e of errors) console.error(`[error] ${e.message}`)
  for (const d of blockingFitDiagnostics) console.error(`[fit-error:${d.code}] ${d.message}`)
  process.exit(1)
}
for (const w of valWarnings) console.error(`[warn:${w.diagnostic?.code ?? w.type}] ${w.message}`)

const { patch, warnings } = createDeck(content)
for (const w of warnings) console.error(`[content-warning] ${w}`)
process.stdout.write(JSON.stringify(patch, null, 2))
