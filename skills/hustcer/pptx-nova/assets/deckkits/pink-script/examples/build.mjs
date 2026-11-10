#!/usr/bin/env node
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { createAssetContext } from '../../../../scripts/lib/assets/asset-manifest.mjs'
import { validateDeckkitContent } from '../../shared/validate-deckkit.mjs'
import { createDeck } from '../pink-script.kit.mjs'
const content = JSON.parse(
  readFileSync(process.argv[2] ?? new URL('./content.json', import.meta.url)),
)
const validation = validateDeckkitContent(content, { deckkit: 'pink-script', mode: 'delivery' })
if (!validation.valid) throw Error(JSON.stringify(validation.errors))
const path = fileURLToPath(
  new URL('../../../examples/deckkits/pink-script/assets_manifest.json', import.meta.url),
)
const assets = createAssetContext(JSON.parse(readFileSync(path)), path)
process.stdout.write(JSON.stringify(createDeck(content, { assets }).patch, null, 2))
