#!/usr/bin/env node
import { analyze } from '../lib/analyze.js';

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString('utf8');
}

function parseInput(raw) {
  const trimmed = raw.trim();
  if (!trimmed) {
    throw new Error('Expected SKILL.md text or JSON with a text/content/skill_md field on stdin.');
  }

  try {
    const parsed = JSON.parse(trimmed);
    const text = parsed.text || parsed.content || parsed.skill_md || parsed.skill || '';
    return {
      text: String(text),
      target: parsed.target || parsed.name || 'stdin',
    };
  } catch {
    return {
      text: raw,
      target: 'stdin',
    };
  }
}

try {
  const raw = await readStdin();
  const input = parseInput(raw);
  const result = analyze(input.text, input.target);
  console.log(JSON.stringify(result));
} catch (error) {
  console.log(JSON.stringify({
    verdict: 'input_error',
    risk_score: 0,
    findings: [{
      id: 'input-error',
      label: 'Input error',
      severity: 'high',
      advice: error.message,
    }],
    positives: [],
    missing_signals: [],
    patch_order: [error.message],
  }));
  process.exit(1);
}
