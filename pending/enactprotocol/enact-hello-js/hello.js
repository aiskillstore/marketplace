#!/usr/bin/env node

/**
 * Hello JS - A simple greeting tool
 *
 * Usage: node hello.js [name]
 */

const name = process.argv[2] || "World";

console.log(`Hello, ${name}! 👋`);

// Add some extra info to show it's working
const now = new Date().toISOString();
console.log(`Generated at: ${now}`);
console.log(`Node version: ${process.version}`);
