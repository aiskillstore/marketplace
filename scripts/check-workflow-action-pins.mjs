#!/usr/bin/env node

import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const FULL_COMMIT_SHA = /^[0-9a-f]{40}$/i;
const FULL_DOCKER_DIGEST = /^docker:\/\/[^@\s]+@sha256:[0-9a-f]{64}$/i;
const EXTERNAL_GITHUB_TARGET = /^[^@\s/]+\/[^@\s/]+(?:\/[^@\s]+)*$/;
const FLOW_STYLE_USES_MESSAGE =
  'Flow-style uses entries are unsupported; write uses as a block-style key so its pin can be verified';

function parseUsesScalar(rawValue) {
  const value = rawValue.trim();
  if (value.startsWith("'")) {
    const match = value.match(/^'((?:[^']|'')*)'(?:\s+#.*)?$/);
    return match ? match[1].replaceAll("''", "'") : value;
  }
  if (value.startsWith('"')) {
    for (let index = 1; index < value.length; index += 1) {
      if (value[index] !== '"' || value[index - 1] === '\\') continue;
      const remainder = value.slice(index + 1).trim();
      if (remainder !== '' && !remainder.startsWith('#')) return value;
      try {
        return JSON.parse(value.slice(0, index + 1));
      } catch {
        return value;
      }
    }
    return value;
  }
  return value.replace(/\s+#.*$/, '').trim();
}

function isYamlCommentStart(line, index) {
  return line[index] === '#' &&
    (index === 0 || /[\s,[{]/.test(line[index - 1]));
}

function isYamlQuoteStart(line, index) {
  return (line[index] === "'" || line[index] === '"') &&
    (index === 0 || !/[\w]/.test(line[index - 1]));
}

function findQuotedScalarEnd(line, start) {
  const quote = line[start];
  for (let index = start + 1; index < line.length; index += 1) {
    if (quote === "'" && line[index] === "'" && line[index + 1] === "'") {
      index += 1;
    } else if (quote === '"' && line[index] === '\\') {
      index += 1;
    } else if (line[index] === quote) {
      return index;
    }
  }
  return line.length - 1;
}

function stripYamlComment(line) {
  for (let index = 0; index < line.length; index += 1) {
    if (isYamlQuoteStart(line, index)) {
      index = findQuotedScalarEnd(line, index);
    } else if (isYamlCommentStart(line, index)) {
      return line.slice(0, index);
    }
  }
  return line;
}

function parseFlowUsesScalar(line, colonIndex) {
  let depth = 0;
  let end = line.length;

  for (let index = colonIndex + 1; index < line.length; index += 1) {
    const character = line[index];
    if (isYamlQuoteStart(line, index)) {
      index = findQuotedScalarEnd(line, index);
    } else if (isYamlCommentStart(line, index)) {
      end = index;
      break;
    } else if (character === '{' || character === '[') {
      depth += 1;
    } else if (character === '}' || character === ']') {
      if (depth === 0) {
        end = index;
        break;
      }
      depth -= 1;
    } else if (character === ',' && depth === 0) {
      end = index;
      break;
    }
  }

  return parseUsesScalar(line.slice(colonIndex + 1, end));
}

function findFlowStyleUses(line) {
  const entries = [];
  let flowDepth = 0;
  let previousSignificant = '';

  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (isYamlCommentStart(line, index)) break;

    if (isYamlQuoteStart(line, index)) {
      const end = findQuotedScalarEnd(line, index);
      const key = parseUsesScalar(line.slice(index, end + 1));
      let colonIndex = end + 1;
      while (/\s/.test(line[colonIndex] ?? '')) colonIndex += 1;
      if (
        flowDepth > 0 &&
        '[{,'.includes(previousSignificant) &&
        key === 'uses' &&
        line[colonIndex] === ':'
      ) {
        entries.push(parseFlowUsesScalar(line, colonIndex));
      }
      previousSignificant = 'scalar';
      index = end;
      continue;
    }

    if (character === '{' || character === '[') {
      flowDepth += 1;
    } else if (character === '}' || character === ']') {
      flowDepth = Math.max(0, flowDepth - 1);
    } else if (
      flowDepth > 0 &&
      '[{,'.includes(previousSignificant) &&
      line.startsWith('uses', index)
    ) {
      let colonIndex = index + 'uses'.length;
      while (/\s/.test(line[colonIndex] ?? '')) colonIndex += 1;
      if (line[colonIndex] === ':') {
        entries.push(parseFlowUsesScalar(line, colonIndex));
      }
    }

    if (!/\s/.test(character)) previousSignificant = character;
  }

  return entries;
}

export function validateWorkflowUsesReference(uses) {
  if (uses.startsWith('./')) return null;

  if (uses.startsWith('docker://')) {
    if (FULL_DOCKER_DIGEST.test(uses)) return null;
    return 'Docker action references must use docker://image@sha256:<64-hex-digest>';
  }

  const separator = uses.lastIndexOf('@');
  const target = separator === -1 ? '' : uses.slice(0, separator);
  const reference = separator === -1 ? '' : uses.slice(separator + 1);

  if (!EXTERNAL_GITHUB_TARGET.test(target)) {
    return 'External action and reusable workflow references must use owner/repository[/path]@<commit>';
  }
  if (!FULL_COMMIT_SHA.test(reference)) {
    return 'External action and reusable workflow references must use an exact 40-character commit SHA';
  }
  return null;
}

export function findWorkflowUsesViolations(content, file) {
  const violations = [];
  const lines = content.split(/\r?\n/);
  let blockScalarIndent = null;

  for (const [index, line] of lines.entries()) {
    const indentation = line.match(/^\s*/)[0].length;
    if (blockScalarIndent !== null) {
      if (line.trim() === '' || indentation > blockScalarIndent) continue;
      blockScalarIndent = null;
    }

    const uncommentedLine = stripYamlComment(line);
    const startsBlockScalar =
      /:\s*[|>](?:[1-9][+-]?|[+-][1-9]?)?\s*$/.test(uncommentedLine);

    for (const uses of findFlowStyleUses(line)) {
      violations.push({
        file,
        line: index + 1,
        message: FLOW_STYLE_USES_MESSAGE,
        uses,
      });
    }

    if (startsBlockScalar) blockScalarIndent = indentation;

    const match = line.match(/^\s*(?:-\s*)?uses\s*:\s*(.*?)\s*$/);
    if (!match) continue;

    const uses = parseUsesScalar(match[1]);
    const message = validateWorkflowUsesReference(uses);
    if (message) {
      violations.push({
        file,
        line: index + 1,
        message,
        uses,
      });
    }
  }

  return violations;
}

export function scanWorkflowDirectory(root) {
  const violations = [];

  function walk(directory) {
    const entries = readdirSync(directory, { withFileTypes: true })
      .sort((left, right) => left.name.localeCompare(right.name));
    for (const entry of entries) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) {
        walk(path);
      } else if (entry.isFile() && /\.ya?ml$/i.test(entry.name)) {
        violations.push(
          ...findWorkflowUsesViolations(readFileSync(path, 'utf8'), path),
        );
      }
    }
  }

  walk(root);
  return violations;
}

function main() {
  const roots = process.argv.slice(2);
  if (roots.length === 0) roots.push('.github/workflows');

  const violations = roots.flatMap((root) => scanWorkflowDirectory(root));
  if (violations.length === 0) {
    console.log('Workflow action pin policy passed');
    return;
  }

  for (const violation of violations) {
    console.error(
      `${violation.file}:${violation.line}: ${violation.message}: ${violation.uses}`,
    );
  }
  console.error(`Workflow action pin policy failed with ${violations.length} violation(s)`);
  process.exitCode = 1;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`Workflow action pin policy failed: ${error.message}`);
    process.exitCode = 1;
  }
}
