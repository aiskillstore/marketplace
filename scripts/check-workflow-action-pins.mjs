#!/usr/bin/env node

import {
  lstatSync,
  readFileSync,
  readdirSync,
  statSync,
} from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import {
  isAlias,
  isScalar,
  LineCounter,
  parseDocument,
  visit,
} from 'yaml';

const FULL_COMMIT_SHA = /^[0-9a-f]{40}$/i;
const FULL_DOCKER_DIGEST = /^docker:\/\/[^@\s]+@sha256:[0-9a-f]{64}$/i;
const EXTERNAL_GITHUB_TARGET = /^[^@\s/]+\/[^@\s/]+(?:\/[^@\s]+)*$/;
const YAML_PARSE_ERROR = '<yaml-parse-error>';

function lineForOffset(lineCounter, offset = 0) {
  return lineCounter.linePos(Math.max(0, offset)).line;
}

function diagnosticLine(diagnostic, lineCounter) {
  return diagnostic.linePos?.[0]?.line ??
    lineForOffset(lineCounter, diagnostic.pos?.[0] ?? 0);
}

function nodeLine(node, lineCounter) {
  return lineForOffset(lineCounter, node?.range?.[0] ?? 0);
}

function yamlDiagnosticViolation(file, lineCounter, diagnostic, kind) {
  return {
    file,
    line: diagnosticLine(diagnostic, lineCounter),
    message: `YAML parse ${kind}: ${diagnostic.message}`,
    uses: YAML_PARSE_ERROR,
  };
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

function normalizedMappingKey(key, document) {
  if (isScalar(key)) return key.value;
  if (isAlias(key)) {
    const resolved = key.resolve(document);
    return isScalar(resolved) ? resolved.value : undefined;
  }
  return undefined;
}

export function findWorkflowUsesViolations(content, file) {
  const lineCounter = new LineCounter();
  const document = parseDocument(content, {
    lineCounter,
    prettyErrors: false,
    strict: true,
    uniqueKeys: true,
  });

  if (document.errors.length > 0) {
    return [yamlDiagnosticViolation(
      file,
      lineCounter,
      document.errors[0],
      'error',
    )];
  }
  if (document.warnings.length > 0) {
    return [yamlDiagnosticViolation(
      file,
      lineCounter,
      document.warnings[0],
      'warning',
    )];
  }

  const violations = [];
  visit(document, {
    Pair(_key, pair) {
      if (normalizedMappingKey(pair.key, document) !== 'uses') return;

      const line = nodeLine(pair.key, lineCounter);
      if (!isScalar(pair.value) || typeof pair.value.value !== 'string') {
        violations.push({
          file,
          line,
          message: 'Workflow uses values are non-scalar; pins can only be verified for scalar strings',
          uses: '<non-scalar>',
        });
        return;
      }

      const uses = pair.value.value.trim();
      const message = validateWorkflowUsesReference(uses);
      if (message) violations.push({ file, line, message, uses });
    },
  });
  return violations;
}

export function findWorkflowUsesReferences(content, file) {
  const lineCounter = new LineCounter();
  const document = parseDocument(content, {
    lineCounter,
    prettyErrors: false,
    strict: true,
    uniqueKeys: true,
  });
  if (document.errors.length > 0 || document.warnings.length > 0) return [];

  const references = [];
  visit(document, {
    Pair(_key, pair) {
      if (normalizedMappingKey(pair.key, document) !== 'uses') return;
      references.push({
        file,
        line: nodeLine(pair.key, lineCounter),
        uses: isScalar(pair.value) && typeof pair.value.value === 'string'
          ? pair.value.value.trim()
          : '<non-scalar>',
      });
    },
  });
  return references;
}

function symlinkViolation(path) {
  try {
    const target = statSync(path);
    if (target.isDirectory()) {
      return {
        file: path,
        line: 1,
        message: 'Directory symbolic links are not allowed in workflow or action policy roots',
        uses: '<directory-symlink>',
      };
    }
    return {
      file: path,
      line: 1,
      message: 'Manifest symbolic links are not allowed in workflow or action policy roots',
      uses: /\.ya?ml$/i.test(path) ? '<manifest-symlink>' : '<file-symlink>',
    };
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
    return {
      file: path,
      line: 1,
      message: 'Dangling symbolic links are not allowed in workflow or action policy roots',
      uses: '<dangling-symlink>',
    };
  }
}

export function scanWorkflowDirectory(root) {
  const violations = [];
  let rootEntry;
  try {
    rootEntry = lstatSync(root);
  } catch (error) {
    if (error?.code === 'ENOENT') return violations;
    throw error;
  }

  if (rootEntry.isSymbolicLink()) return [symlinkViolation(root)];
  if (!rootEntry.isDirectory()) {
    if (rootEntry.isFile() && /\.ya?ml$/i.test(root)) {
      return findWorkflowUsesViolations(readFileSync(root, 'utf8'), root);
    }
    return violations;
  }

  function walk(directory) {
    const entries = readdirSync(directory, { withFileTypes: true })
      .sort((left, right) => left.name.localeCompare(right.name));
    for (const entry of entries) {
      const path = join(directory, entry.name);
      if (entry.isSymbolicLink()) {
        violations.push(symlinkViolation(path));
      } else if (entry.isDirectory()) {
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
  if (roots.length === 0) {
    roots.push('.github/workflows', '.github/actions');
  }

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
