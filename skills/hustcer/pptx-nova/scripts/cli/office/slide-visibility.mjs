#!/usr/bin/env node
import { readPptxPackage } from '../../lib/pptx/pptx-package.mjs'

try {
  if (process.argv.length !== 3) throw new Error('Expected one PPTX path')
  process.stdout.write(JSON.stringify(readPptxPackage(process.argv[2]).slides()) + '\n')
} catch (error) {
  process.stderr.write(error.message + '\n')
  process.exitCode = 1
}
