// `--init`: a starter configuration plus the paste snippet for the host in
// the current directory.
//
// Guarantees locked by tests/audit-adoption.mjs:
//   * the starter uses only fields the `--config` loader accepts and is inert
//     until it is edited (the same scan with and without it reports the same
//     findings);
//   * an existing configuration is refused unless `--init-overwrite` is given;
//   * host detection inspects the working directory only — it walks no parent
//     directories — in the documented priority order: GitHub Actions, GitLab
//     CI, CircleCI, Jenkins, pre-commit, git;
//   * the git snippet carries byte-for-byte the staged-files line that
//     templates/pre-commit pins (PRE_COMMIT_HOOK below is that file's body;
//     the contract test asserts they are identical).

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { parseJsonStrict, validateConfig } from './config.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');

export class InitError extends Error {}

/**
 * The pre-commit hook body, duplicated verbatim in templates/pre-commit so an
 * npm-installed package (which ships no templates directory) can still print
 * it. tests/audit-adoption.mjs asserts the two are byte-identical.
 */
export const PRE_COMMIT_HOOK = `#!/bin/sh
# un-editorial-check pre-commit hook.
# Install: cp templates/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# Staged files of an extractable type are passed to the checker; a non-zero
# exit (error-severity findings, or a usage failure) blocks the commit.
staged=$(git diff --cached --name-only --diff-filter=ACM)
set --
while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || continue
  case "$f" in
    *.md|*.markdown|*.txt|*.html|*.htm|*.js|*.mjs|*.cjs|*.jsx|*.ts|*.tsx)
      set -- "$@" "$f"
      ;;
  esac
done <<EOF
$staged
EOF
[ $# -eq 0 ] && exit 0
if [ -n "\${UE_CHECK:-}" ]; then
  # UE_CHECK is a command with arguments; the word splitting is on purpose.
  exec $UE_CHECK "$@"
fi
exec npx --no-install un-editorial-check "$@"
`;

/**
 * Detect the CI or git host of `cwd` itself. No parent-directory walk: the
 * caller's working directory is the unit of detection, and the returned
 * markers are what the report prints next to each host.
 */
export function detectHosts(cwd) {
  const hosts = [];
  const isDir = (rel) => {
    try { return fs.statSync(path.join(cwd, rel)).isDirectory(); } catch { return false; }
  };
  const isFile = (rel) => {
    try { return fs.statSync(path.join(cwd, rel)).isFile(); } catch { return false; }
  };
  if (isDir('.github/workflows')) hosts.push({ id: 'GitHub Actions', marker: '.github/workflows' });
  if (isFile('.gitlab-ci.yml')) hosts.push({ id: 'gitlab-ci', marker: '.gitlab-ci.yml' });
  if (isDir('.circleci')) hosts.push({ id: 'circleci', marker: '.circleci' });
  if (isFile('Jenkinsfile')) hosts.push({ id: 'jenkins', marker: 'Jenkinsfile' });
  if (isFile('.pre-commit-config.yaml')) hosts.push({ id: 'pre-commit', marker: '.pre-commit-config.yaml' });
  // In a worktree `.git` is a file, not a directory: existence is the test.
  if (fs.existsSync(path.join(cwd, '.git'))) hosts.push({ id: 'git', marker: '.git' });
  return hosts;
}

/**
 * The starter configuration: exactly the fields the loader accepts, carrying
 * the bundled defaults so writing it changes nothing, plus `allowlist.claims`
 * so the one allowlist key the defaults leave implicit is visible for editing.
 * Reading the defaults keeps the starter in step with them by construction.
 */
export function starterConfig() {
  const defaults = parseJsonStrict(
    fs.readFileSync(path.join(ROOT, 'config', 'default.json'), 'utf8'), 'config/default.json');
  // Validated through the same validator the loader uses, so a starter that
  // would be rejected is caught before it is offered to anyone.
  const cfg = validateConfig({ ...defaults, allowlist: { claims: [], ...defaults.allowlist } });
  return JSON.parse(JSON.stringify({
    ignoredPaths: cfg.ignoredPaths,
    allowlist: cfg.allowlist,
    severities: cfg.severities,
    rules: cfg.rules,
    spellingReview: cfg.spellingReview,
    baseOrigin: cfg.baseOrigin,
    renderTargets: cfg.renderTargets,
  }));
}

/**
 * Write the starter configuration to `file` (absolute or cwd-relative).
 * Refuses an existing file unless `overwrite` is set.
 * @returns {string} the resolved path written
 */
export function writeStarterConfig(file, { overwrite = false } = {}) {
  const target = path.resolve(file);
  if (fs.existsSync(target) && !overwrite) {
    throw new InitError(`config already exists: ${target} (use --init-overwrite to replace it)`);
  }
  try {
    fs.writeFileSync(target, `${JSON.stringify(starterConfig(), null, 2)}\n`);
  } catch (err) {
    throw new InitError(`cannot write config ${target}: ${err.message}`);
  }
  return target;
}

const SNIPPETS = {
  'GitHub Actions': [
    'Paste the GitHub Actions snippet:',
    '',
    '- uses: ahaomar/un-editorial-check@main',
    '  with:',
    '    path: .',
  ],
  'gitlab-ci': [
    'Paste the GitLab CI snippet:',
    '',
    'editorial-check:',
    '  image: node:20',
    '  script:',
    '    - npx --yes un-editorial-check .',
  ],
  circleci: [
    'Paste the CircleCI snippet:',
    '',
    'jobs:',
    '  editorial-check:',
    '    docker:',
    '      - image: cimg/node:current',
    '    steps:',
    '      - checkout',
    '      - run: npx --yes un-editorial-check .',
  ],
  jenkins: [
    'Paste the Jenkins snippet:',
    '',
    "stage('editorial') {",
    '  steps {',
    "    sh 'npx --yes un-editorial-check .'",
    '  }',
    '}',
  ],
  'pre-commit': [
    'Paste the pre-commit snippet:',
    '',
    '- repo: https://github.com/ahaomar/un-editorial-check',
    '  rev: main',
    '  hooks:',
    '    - id: un-editorial-check',
    '      entry: npx --no-install un-editorial-check',
  ],
  git: [
    'Paste this into .git/hooks/pre-commit (or copy templates/pre-commit):',
    '',
    ...PRE_COMMIT_HOOK.replace(/\n$/, '').split('\n'),
  ],
};

/**
 * The full `--init` report: what was written, how to scan with it, the host
 * detected in this directory and its snippet, then the one-command
 * verification. Pure — the caller writes the file and prints the string.
 *
 * @param {object} input
 * @param {string} input.relative  the config path, as it was written
 * @param {Array<{id: string, marker: string}>} input.hosts  detectHosts result
 */
export function formatInitReport({ relative, hosts }) {
  const lines = [
    `Wrote ${relative} (starter configuration; it changes no behaviour until you edit it).`,
    '',
    `Scan with it: npx un-editorial-check --config ${relative} <paths>`,
    '',
  ];
  if (!hosts.length) {
    lines.push('No CI or git host detected in this directory.');
  } else {
    lines.push(`Detected: ${hosts.map(host => `${host.id} (${host.marker})`).join(', ')}`);
    lines.push('');
    lines.push(...SNIPPETS[hosts[0].id]);
  }
  lines.push('');
  lines.push('Verify the installation with: npx un-editorial-check --self-test');
  lines.push('');
  return lines.join('\n');
}
