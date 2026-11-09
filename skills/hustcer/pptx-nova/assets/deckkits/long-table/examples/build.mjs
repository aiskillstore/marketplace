#!/usr/bin/env node
import { readFileSync } from 'node:fs'
import { createDeck } from '../long-table.kit.mjs'

const input = process.argv[2] ?? new URL('./content.json', import.meta.url)

const content = JSON.parse(readFileSync(input, 'utf8'))
const { patch, warnings } = createDeck(content)
if (warnings.length > 0) {
  for (const warning of warnings) {
    const message = typeof warning === 'string' ? warning : JSON.stringify(warning)
    process.stderr.write(`${message}\n`)
  }
}
process.stdout.write(JSON.stringify(patch, null, 2))
