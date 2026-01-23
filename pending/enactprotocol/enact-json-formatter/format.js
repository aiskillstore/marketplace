#!/usr/bin/env node

const jsonInput = process.argv[2];
const indent = parseInt(process.argv[3] || '2', 10);

try {
  const parsed = JSON.parse(jsonInput);
  const formatted = JSON.stringify(parsed, null, indent);
  
  console.log(JSON.stringify({
    formatted: formatted,
    valid: true
  }));
} catch (err) {
  console.log(JSON.stringify({
    formatted: null,
    valid: false,
    error: err.message
  }));
  process.exit(1);
}
