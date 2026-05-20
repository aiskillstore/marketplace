#!/usr/bin/env node
import fs from 'node:fs/promises';
import { analyze } from '../lib/analyze.js';

function usage() {
  return [
    'Usage:',
    '  agent-skill-trust-check <path-or-url> [--json]',
    '',
    'Examples:',
    '  agent-skill-trust-check SKILL.md',
    '  agent-skill-trust-check https://raw.githubusercontent.com/owner/repo/main/SKILL.md --json',
  ].join('\n');
}

async function readInput(target) {
  if (/^https?:\/\//i.test(target)) {
    const url = new URL(target);
    if (!['raw.githubusercontent.com', 'github.com', 'gist.githubusercontent.com'].includes(url.hostname)) {
      throw new Error('Only public GitHub/raw/Gist URLs are fetched by the local CLI.');
    }
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Fetch failed with HTTP ${response.status}`);
    return response.text();
  }
  return fs.readFile(target, 'utf8');
}

function printText(result) {
  console.log(`Agent Skill Trust Check: ${result.verdict}`);
  console.log(`Risk score: ${result.risk_score}`);
  console.log(`Target: ${result.target}`);
  console.log('');
  if (result.findings.length === 0) {
    console.log('No risky patterns matched in the static text pass.');
  } else {
    console.log('Findings:');
    for (const finding of result.findings) {
      console.log(`- [${finding.severity}] ${finding.label}: ${finding.advice}`);
    }
  }
  console.log('');
  console.log(`Missing signals: ${result.missing_signals.join(', ') || 'none'}`);
  console.log(result.next_step);
}

const args = process.argv.slice(2);
const json = args.includes('--json');
const target = args.find((arg) => arg !== '--json');

if (!target || args.includes('--help') || args.includes('-h')) {
  console.log(usage());
  process.exit(target ? 0 : 1);
}

try {
  const text = await readInput(target);
  const result = analyze(text, target);
  if (json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    printText(result);
  }
} catch (error) {
  console.error(`agent-skill-trust-check: ${error.message}`);
  process.exit(1);
}
