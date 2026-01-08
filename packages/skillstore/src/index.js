/**
 * Skillstore SDK
 * AI Skills marketplace for Claude Code
 */

export function hello() {
  return 'Hello, World!';
}

export function greet(name) {
  return `Hello, ${name}!`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  console.log(hello());
}
