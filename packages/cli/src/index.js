#!/usr/bin/env node
/**
 * Skillstore CLI
 * AI Skills marketplace for Claude Code
 */

export function hello() {
  return 'Hello from @skillstore/cli!';
}

export function greet(name) {
  return `Hello, ${name}!`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(hello());
}
