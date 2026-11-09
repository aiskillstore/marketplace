#!/usr/bin/env node
// validate-content.mjs — schema + DeckKit density 校验入口
// 用法: node validate-content.mjs content.json --deckkit consulting-dark
import { loadContent } from './shared/core-primitives.kit.mjs'
import { validateDeckkitContent as validateContent } from './shared/validate-deckkit.mjs'

const argValue = (name, fallback = '') => {
  const idx = process.argv.indexOf(name)
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : fallback
}

const contentPath = process.argv[2]
if (!contentPath) {
  console.error('Usage: node validate-content.mjs <content.json> --deckkit <deckkit-id>')
  process.exit(1)
}

const deckkitId = argValue('--deckkit', '')
const ignoreSoft = process.argv.includes('--ignore-soft-limits')
const mode = argValue('--mode', 'draft')

let content
try {
  content = await loadContent(contentPath)
} catch (e) {
  console.error(`[error] Failed to load content: ${e.message}`)
  process.exit(1)
}

const result = validateContent(content, {
  deckkit: deckkitId || content?.meta?.deckkit,
  ignoreSoftLimits: ignoreSoft,
  mode,
})

output(result)
if (result.errors.length > 0) process.exit(1)

function output(result) {
  const publicResult = {
    errors: result.errors,
    warnings: result.warnings,
    fitDiagnostics: result.fitDiagnostics,
    valid: result.valid,
    ...(result.designDiversity ? { designDiversity: result.designDiversity } : {}),
  }
  if (process.argv.includes('--json')) {
    process.stdout.write(JSON.stringify(publicResult, null, 2) + '\n')
  } else {
    for (const e of publicResult.errors) console.error(`[error] ${e.message}`)
    for (const w of publicResult.warnings) console.error(`[warn]  ${w.message}`)
    if (publicResult.valid)
      console.log(
        publicResult.warnings.length > 0
          ? `Valid with ${publicResult.warnings.length} warning(s).`
          : 'Valid.',
      )
    else console.log(`Failed: ${publicResult.errors.length} error(s).`)
  }
}
