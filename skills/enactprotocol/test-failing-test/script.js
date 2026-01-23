#!/usr/bin/env node

const message = process.argv[2] || "Hello from failing test";

console.log("=== Starting Test Tool ===");
console.log("Message:", message);
console.log("This is stdout output before the error");

console.error("=== Error Output ===");
console.error("This is stderr output");

// Simulate an error with a stack trace
const error = new Error("Simulated failure for testing error visibility");
console.error("Error:", error.message);
console.error("Stack trace:");
console.error(error.stack);

// Exit with error
process.exit(1);
