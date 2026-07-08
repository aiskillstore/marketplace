#!/usr/bin/env node

import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

console.log("🌐 Web Browser Subagent - Usage Examples\n");

const examples = [
  {
    name: "Basic Usage - Page Research",
    description: "Research a webpage and extract key information",
    steps: [
      "cd ~/.pi/agent/skills/web-browser",
      "node scripts/start.js",
      "node scripts/nav.js https://example.com",
      'node scripts/eval.js \'document.title\'',
      'node scripts/eval.js \'document.querySelectorAll("a").length\'',
      'node scripts/screenshot.js',
      "node scripts/stop.js"
    ]
  },
  {
    name: "Data Extraction - Scraping Links",
    description: "Extract all links from a webpage",
    steps: [
      "cd ~/.pi/agent/skills/web-browser",
      "node scripts/start.js",
      "node scripts/nav.js https://news.ycombinator.com",
      'node scripts/eval.js \'JSON.stringify(Array.from(document.querySelectorAll(".titleline > a")).map(a => ({ text: a.textContent, href: a.href })))\'',
      "node scripts/stop.js"
    ]
  },
  {
    name: "Authentication - Using Profile",
    description: "Browse with your login credentials",
    steps: [
      "cd ~/.pi/agent/skills/web-browser",
      "node scripts/start.js --profile",
      "node scripts/nav.js https://github.com",
      'node scripts/eval.js \'document.cookie\'',
      "node scripts/stop.js"
    ]
  },
  {
    name: "Form Interaction - Search",
    description: "Fill and submit a search form",
    steps: [
      "cd ~/.pi/agent/skills/web-browser",
      "node scripts/start.js",
      "node scripts/nav.js https://www.google.com",
      'node scripts/eval.js \'document.querySelector("input[name=\\"q\\"]").value = "web scraping"\'; document.querySelector("form").submit()',
      "node scripts/eval.js 'document.title'",
      "node scripts/stop.js"
    ]
  },
  {
    name: "Element Selection - Interactive Picker",
    description: "Select elements interactively",
    steps: [
      "cd ~/.pi/agent/skills/web-browser",
      "node scripts/start.js",
      "node scripts/nav.js https://example.com",
      'node scripts/pick.js "Click the main link"',
      "node scripts/stop.js"
    ]
  }
];

examples.forEach((example, index) => {
  console.log(`${index + 1}. ${example.name}`);
  console.log(`   ${example.description}`);
  console.log("   Steps:");
  example.steps.forEach(step => {
    console.log(`   $ ${step}`);
  });
  console.log();
});

console.log("📖 Documentation:");
console.log("   - Agent config: ~/.pi/agent/agents/web-browser.md");
console.log("   - Skill docs: ~/.pi/agent/skills/web-browser/SKILL.md");
console.log("   - Fix notes: ~/.pi/agent/skills/web-browser/FIX_NOTE.md");
console.log();

console.log("🚀 Quick Start:");
console.log("   Run test: cd ~/.pi/agent/skills/web-browser && node test-subagent.js");
console.log("   Run demo: cd ~/.pi/agent/skills/web-browser && node demo.js");
console.log();

console.log("💡 Tips:");
console.log("   - Use subagent command: /web-browser research https://example.com");
console.log("   - Check port: node scripts/get-port.js");
console.log("   - Stop browser: node scripts/stop.js");
console.log("   - Reset port: rm ~/.cache/scraping-web-browser/port.txt");