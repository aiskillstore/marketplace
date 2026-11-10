#!/usr/bin/env node
import { runCli } from '../../lib/assets/tabler-icons.mjs'

try {
  runCli(process.argv.slice(2))
} catch (error) {
  process.stderr.write(`${error.message}\n`)
  process.exitCode = 1
}
