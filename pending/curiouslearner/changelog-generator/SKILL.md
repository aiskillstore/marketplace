---
name: changelog-generator
description: Automatically generate changelogs from git commits following conventional commits, semantic versi...
---

# Changelog Generator Skill

Automatically generate changelogs from git commits following conventional commits, semantic versioning, and best practices.

## Instructions

You are a changelog generation expert. When invoked:

1. **Analyze Commit History**:
   - Parse git commit messages
   - Identify conventional commit types
   - Group related changes
   - Determine version bumps (major, minor, patch)

2. **Generate Changelog Entries**:
   - Follow Keep a Changelog format
   - Categorize by change type
   - Include breaking changes prominently
   - Add relevant metadata (dates, versions, authors)

3. **Format Output**:
   - Use markdown formatting
   - Create clear section headers
   - Add links to commits and PRs
   - Include migration guides for breaking changes

4. **Version Management**:
   - Suggest semantic version numbers
   - Identify breaking changes
   - Track deprecations
   - Handle pre-release versions

## Conventional Commit Types

- **feat**: New feature (minor version bump)
- **fix**: Bug fix (patch version bump)
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Test additions or changes
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Maintenance tasks
- **revert**: Revert previous changes

**Breaking Change**: Any commit with `BREAKING CHANGE:` in body or `!` after type (major version bump)

## Usage Examples

```
@changelog-generator
@changelog-generator --since v1.2.0
@changelog-generator --unreleased
@changelog-generator --version 2.0.0
@changelog-generator --format keep-a-changelog
@changelog-generator --include-authors
```

## Changelog Formats

### Keep a Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New feature X for improved user experience
- Support for configuration option Y

### Changed
- Updated dependency Z to version 2.0
- Improved performance of data processing

### Deprecated
- Function `oldMethod()` - use `newMethod()` instead

### Removed
- Removed deprecated API endpoint `/api/v1/old`

### Fixed
- Fixed memory leak in cache implementation
- Corrected timezone handling in date formatter

### Security
- Fixed XSS vulnerability in user input handling
- Updated crypto library to address CVE-2024-1234

## [1.5.0] - 2024-01-15

### Added
- User authentication with OAuth2
- Export functionality for reports
- Dark mode theme support

### Changed
- Redesigned dashboard UI
- Optimized database queries

### Fixed
- Fixed bug in pagination logic
- Resolved CORS issues with API

## [1.4.2] - 2024-01-10

### Fixed
- Critical bug in payment processing
- Memory leak in WebSocket connections

### Security
- Patched authentication bypass vulnerability

## [1.4.1] - 2024-01-05

### Fixed
- Hotfix for broken deployment script
- Fixed typo in error messages

## [1.4.0] - 2024-01-01

### Added
- Real-time notifications
- File upload with drag and drop
- Advanced search filters

### Changed
- Migrated from REST to GraphQL
- Updated UI components library

### Deprecated
- Old REST API endpoints (will be removed in 2.0)

[Unreleased]: https://github.com/user/repo/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/user/repo/compare/v1.4.2...v1.5.0
[1.4.2]: https://github.com/user/repo/compare/v1.4.1...v1.4.2
[1.4.1]: https://github.com/user/repo/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/user/repo/releases/tag/v1.4.0
```

## Automated Changelog Generation

### Using Git Commits

```bash
#!/bin/bash
# generate-changelog.sh - Generate changelog from git commits

VERSION=${1:-"Unreleased"}
PREV_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

echo "# Changelog"
echo ""
echo "## [$VERSION] - $(date +%Y-%m-%d)"
echo ""

# Get commits since last tag
if [ -z "$PREV_TAG" ]; then
  COMMITS=$(git log --pretty=format:"%s|||%h|||%an" --reverse)
else
  COMMITS=$(git log ${PREV_TAG}..HEAD --pretty=format:"%s|||%h|||%an" --reverse)
fi

# Arrays for different categories
declare -a features=()
declare -a fixes=()
declare -a breaking=()
declare -a docs=()
declare -a chores=()
declare -a other=()

# Parse commits
while IFS='|||' read -r message hash author; do
  case "$message" in
    feat:*|feat\(*\):*)
      features+=("- ${message#feat*: } ([${hash}](../../commit/${hash}))")
      ;;
    fix:*|fix\(*\):*)
      fixes+=("- ${message#fix*: } ([${hash}](../../commit/${hash}))")
      ;;
    *BREAKING*|*\!:*)
      breaking+=("- ${message} ([${hash}](../../commit/${hash}))")
      ;;
    docs:*)
      docs+=("- ${message#docs: } ([${hash}](../../commit/${hash}))")
      ;;
    chore:*|build:*|ci:*)
      chores+=("- ${message#*: } ([${hash}](../../commit/${hash}))")
      ;;
    *)
      other+=("- ${message} ([${hash}](../../commit/${hash}))")
      ;;
  esac
done <<< "$COMMITS"

# Output sections
if [ ${#breaking[@]} -gt 0 ]; then
  echo "### ⚠️ BREAKING CHANGES"
  echo ""
  printf '%s\n' "${breaking[@]}"
  echo ""
fi

if [ ${#features[@]} -gt 0 ]; then
  echo "### Added"
  echo ""
  printf '%s\n' "${features[@]}"
  echo ""
fi

if [ ${#fixes[@]} -gt 0 ]; then
  echo "### Fixed"
  echo ""
  printf '%s\n' "${fixes[@]}"
  echo ""
fi

if [ ${#docs[@]} -gt 0 ]; then
  echo "### Documentation"
  echo ""
  printf '%s\n' "${docs[@]}"
  echo ""
fi

if [ ${#chores[@]} -gt 0 ]; then
  echo "### Internal"
  echo ""
  printf '%s\n' "${chores[@]}"
  echo ""
fi

if [ ${#other[@]} -gt 0 ]; then
  echo "### Other Changes"
  echo ""
  printf '%s\n' "${other[@]}"
  echo ""
fi
```

### Using conventional-changelog

```bash
# Install
npm install -g conventional-changelog-cli

# Generate changelog
conventional-changelog -p angular -i CHANGELOG.md -s

# For first release
conventional-changelog -p angular -i CHANGELOG.md -s -r 0

# With specific version
conventional-changelog -p angular -i CHANGELOG.md -s --release-count 0 \
  --tag-prefix v --preset angular
```

**package.json configuration:**
```json
{
  "scripts": {
    "changelog": "conventional-changelog -p angular -i CHANGELOG.md -s",
    "version": "npm run changelog && git add CHANGELOG.md"
  },
  "devDependencies": {
    "conventional-changelog-cli": "^4.1.0"
  }
}
```

### Using standard-version

```bash
# Install
npm install -D standard-version

# Generate changelog and bump version
npx standard-version

# Preview without committing
npx standard-version --dry-run

# First release
npx standard-version --first-release

# Specific version
npx standard-version --release-as minor
npx standard-version --release-as 1.1.0

# Pre-release
npx standard-version --prerelease alpha
```

**package.json:**
```json
{
  "scripts": {
    "release": "standard-version",
    "release:minor": "standard-version --release-as minor",
    "release:major": "standard-version --release-as major",
    "release:alpha": "standard-version --prerelease alpha"
  },
  "standard-version": {
    "types": [
      {"type": "feat", "section": "Features"},
      {"type": "fix", "section": "Bug Fixes"},
      {"type": "chore", "hidden": true},
      {"type": "docs", "section": "Documentation"},
      {"type": "style", "hidden": true},
      {"type": "refactor", "section": "Code Refactoring"},
      {"type": "perf", "section": "Performance Improvements"},
      {"type": "test", "hidden": true}
    ]
  }
}
```

### Using release-please (GitHub Action)

**.github/workflows/release.yml:**
```yaml
name: Release

on:
  push:
    branches:
      - main

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: google-github-actions/release-please-action@v3
        id: release
        with:
          release-type: node
          package-name: my-package

      - uses: actions/checkout@v3
        if: ${{ steps.release.outputs.release_created }}

      - uses: actions/setup-node@v3
        if: ${{ steps.release.outputs.release_created }}
        with:
          node-version: 18
          registry-url: 'https://registry.npmjs.org'

      - run: npm ci
        if: ${{ steps.release.outputs.release_created }}

      - run: npm publish
        if: ${{ steps.release.outputs.release_created }}
        env:
          NODE_AUTH_TOKEN: ${{secrets.NPM_TOKEN}}
```

## Advanced Changelog Generation

### Node.js Script with Full Features

```javascript
#!/usr/bin/env node
// generate-changelog.js

const { execSync } = require('child_process');
const fs = require('fs');

const COMMIT_PATTERN = /^(\w+)(\([\w-]+\))?(!)?:\s(.+)$/;

const TYPES = {
  feat: { section: 'Added', bump: 'minor' },
  fix: { section: 'Fixed', bump: 'patch' },
  docs: { section: 'Documentation', bump: null },
  style: { section: 'Style', bump: null },
  refactor: { section: 'Changed', bump: null },
  perf: { section: 'Performance', bump: 'patch' },
  test: { section: 'Tests', bump: null },
  build: { section: 'Build System', bump: null },
  ci: { section: 'CI', bump: null },
  chore: { section: 'Chores', bump: null },
  revert: { section: 'Reverts', bump: 'patch' },
};

function getCommitsSinceTag(tag) {
  const cmd = tag
    ? `git log ${tag}..HEAD --pretty=format:"%H|||%s|||%b|||%an|||%ae|||%ai"`
    : `git log --pretty=format:"%H|||%s|||%b|||%an|||%ae|||%ai"`;

  try {
    const output = execSync(cmd, { encoding: 'utf-8' });
    return output.split('\n').filter(Boolean);
  } catch (error) {
    return [];
  }
}

function parseCommit(commitLine) {
  const [hash, subject, body, author, email, date] = commitLine.split('|||');

  const match = subject.match(COMMIT_PATTERN);
  if (!match) {
    return {
      hash,
      subject,
      body,
      author,
      email,
      date,
      type: 'other',
      scope: null,
      breaking: false,
      description: subject,
    };
  }

  const [, type, scope, breaking, description] = match;

  return {
    hash,
    subject,
    body,
    author,
    email,
    date,
    type,
    scope: scope ? scope.slice(1, -1) : null,
    breaking: Boolean(breaking) || body.includes('BREAKING CHANGE'),
    description,
  };
}

function groupCommits(commits) {
  const groups = {};
  const breaking = [];

  for (const commit of commits) {
    if (commit.breaking) {
      breaking.push(commit);
    }

    const typeInfo = TYPES[commit.type] || { section: 'Other Changes' };
    const section = typeInfo.section;

    if (!groups[section]) {
      groups[section] = [];
    }

    groups[section].push(commit);
  }

  return { groups, breaking };
}

function generateMarkdown(version, date, groups, breaking, options = {}) {
  const lines = [];

  lines.push(`## [${version}] - ${date}`);
  lines.push('');

  // Breaking changes first
  if (breaking.length > 0) {
    lines.push('### ⚠️ BREAKING CHANGES');
    lines.push('');
    for (const commit of breaking) {
      lines.push(`- **${commit.description}** ([${commit.hash.slice(0, 7)}](../../commit/${commit.hash}))`);
      if (commit.body) {
        const breakingNote = commit.body.match(/BREAKING CHANGE:\s*(.+)/);
        if (breakingNote) {
          lines.push(`  ${breakingNote[1]}`);
        }
      }
    }
    lines.push('');
  }

  // Other sections
  const sectionOrder = [
    'Added',
    'Changed',
    'Deprecated',
    'Removed',
    'Fixed',
    'Security',
    'Performance',
    'Documentation',
  ];

  for (const section of sectionOrder) {
    if (groups[section] && groups[section].length > 0) {
      lines.push(`### ${section}`);
      lines.push('');

      const commits = groups[section];
      const grouped = {};

      // Group by scope if present
      for (const commit of commits) {
        const key = commit.scope || '_default';
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(commit);
      }

      for (const [scope, scopeCommits] of Object.entries(grouped)) {
        if (scope !== '_default') {
          lines.push(`#### ${scope}`);
          lines.push('');
        }

        for (const commit of scopeCommits) {
          let line = `- ${commit.description}`;

          if (options.includeHash) {
            line += ` ([${commit.hash.slice(0, 7)}](../../commit/${commit.hash}))`;
          }

          if (options.includeAuthor) {
            line += ` - @${commit.author}`;
          }

          lines.push(line);
        }
      }

      lines.push('');
    }
  }

  return lines.join('\n');
}

function getLatestTag() {
  try {
    return execSync('git describe --tags --abbrev=0', { encoding: 'utf-8' }).trim();
  } catch (error) {
    return null;
  }
}

function suggestVersion(breaking, groups) {
  const latestTag = getLatestTag();
  if (!latestTag) return '1.0.0';

  const [major, minor, patch] = latestTag.replace('v', '').split('.').map(Number);

  if (breaking.length > 0) {
    return `${major + 1}.0.0`;
  }

  const hasFeatures = groups['Added'] && groups['Added'].length > 0;
  if (hasFeatures) {
    return `${major}.${minor + 1}.0`;
  }

  return `${major}.${minor}.${patch + 1}`;
}

// Main execution
function main() {
  const args = process.argv.slice(2);
  const options = {
    includeHash: !args.includes('--no-hash'),
    includeAuthor: args.includes('--author'),
    version: args.find(a => a.startsWith('--version='))?.split('=')[1],
    since: args.find(a => a.startsWith('--since='))?.split('=')[1],
  };

  const latestTag = options.since || getLatestTag();
  const commits = getCommitsSinceTag(latestTag);
  const parsed = commits.map(parseCommit);
  const { groups, breaking } = groupCommits(parsed);

  const version = options.version || suggestVersion(breaking, groups);
  const date = new Date().toISOString().split('T')[0];

  const changelog = generateMarkdown(version, date, groups, breaking, options);

  // Read existing changelog or create new
  let existingChangelog = '';
  try {
    existingChangelog = fs.readFileSync('CHANGELOG.md', 'utf-8');
  } catch (error) {
    existingChangelog = '# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n';
  }

  // Insert new version after header
  const lines = existingChangelog.split('\n');
  const headerEnd = lines.findIndex(l => l.startsWith('## '));
  const newLines = [
    ...lines.slice(0, headerEnd === -1 ? lines.length : headerEnd),
    changelog,
    ...lines.slice(headerEnd === -1 ? lines.length : headerEnd),
  ];

  fs.writeFileSync('CHANGELOG.md', newLines.join('\n'));

  console.log(`✓ Generated changelog for version ${version}`);
  console.log(`  - ${commits.length} commits processed`);
  console.log(`  - ${breaking.length} breaking changes`);
  console.log(`  - Suggested version: ${version}`);
}

if (require.main === module) {
  main();
}

module.exports = { parseCommit, groupCommits, generateMarkdown };
```

**Usage:**
```bash
# Make executable
chmod +x generate-changelog.js

# Run
./generate-changelog.js

# With options
./generate-changelog.js --version=2.0.0 --author --since=v1.5.0
```

## Python Version

```python
#!/usr/bin/env python3
# generate_changelog.py

import re
import subprocess
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

COMMIT_PATTERN = re.compile(r'^(\w+)(\([\w-]+\))?(!)?:\s(.+)$')

TYPES = {
    'feat': {'section': 'Added', 'bump': 'minor'},
    'fix': {'section': 'Fixed', 'bump': 'patch'},
    'docs': {'section': 'Documentation', 'bump': None},
    'style': {'section': 'Style', 'bump': None},
    'refactor': {'section': 'Changed', 'bump': None},
    'perf': {'section': 'Performance', 'bump': 'patch'},
    'test': {'section': 'Tests', 'bump': None},
    'build': {'section': 'Build System', 'bump': None},
    'ci': {'section': 'CI', 'bump': None},
    'chore': {'section': 'Chores', 'bump': None},
}

def get_commits_since_tag(tag: str = None) -> List[str]:
    cmd = ['git', 'log', '--pretty=format:%H|||%s|||%b|||%an|||%ae|||%ai']
    if tag:
        cmd.insert(2, f'{tag}..HEAD')

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [line for line in result.stdout.split('\n') if line]
    except subprocess.CalledProcessError:
        return []

def parse_commit(commit_line: str) -> Dict:
    parts = commit_line.split('|||')
    if len(parts) < 6:
        return None

    hash_val, subject, body, author, email, date = parts

    match = COMMIT_PATTERN.match(subject)
    if not match:
        return {
            'hash': hash_val,
            'subject': subject,
            'body': body,
            'author': author,
            'type': 'other',
            'scope': None,
            'breaking': False,
            'description': subject,
        }

    type_val, scope, breaking, description = match.groups()

    return {
        'hash': hash_val,
        'subject': subject,
        'body': body,
        'author': author,
        'type': type_val,
        'scope': scope[1:-1] if scope else None,
        'breaking': bool(breaking) or 'BREAKING CHANGE' in body,
        'description': description,
    }

def group_commits(commits: List[Dict]) -> Tuple[Dict, List]:
    groups = defaultdict(list)
    breaking = []

    for commit in commits:
        if commit['breaking']:
            breaking.append(commit)

        type_info = TYPES.get(commit['type'], {'section': 'Other Changes'})
        section = type_info['section']
        groups[section].append(commit)

    return dict(groups), breaking

def generate_markdown(version: str, groups: Dict, breaking: List) -> str:
    lines = [f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}", ""]

    if breaking:
        lines.append("### ⚠️ BREAKING CHANGES")
        lines.append("")
        for commit in breaking:
            lines.append(f"- **{commit['description']}** ([{commit['hash'][:7]}](../../commit/{commit['hash']}))")
        lines.append("")

    section_order = ['Added', 'Changed', 'Fixed', 'Security', 'Performance', 'Documentation']

    for section in section_order:
        if section in groups and groups[section]:
            lines.append(f"### {section}")
            lines.append("")
            for commit in groups[section]:
                lines.append(f"- {commit['description']} ([{commit['hash'][:7]}](../../commit/{commit['hash']}))")
            lines.append("")

    return '\n'.join(lines)

def main():
    commits = get_commits_since_tag()
    parsed = [parse_commit(c) for c in commits if parse_commit(c)]
    groups, breaking = group_commits(parsed)

    version = input("Enter version number (or press Enter for auto): ").strip() or "1.0.0"
    changelog = generate_markdown(version, groups, breaking)

    print(changelog)

    # Optionally write to file
    with open('CHANGELOG.md', 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(changelog + '\n\n' + content)

if __name__ == '__main__':
    main()
```

## GitHub Release Notes

### Automated Release with Notes

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Generate changelog
        id: changelog
        run: |
          # Get previous tag
          PREV_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")

          # Generate changelog
          if [ -z "$PREV_TAG" ]; then
            CHANGELOG=$(git log --pretty=format:"- %s (%h)" --reverse)
          else
            CHANGELOG=$(git log ${PREV_TAG}..HEAD --pretty=format:"- %s (%h)" --reverse)
          fi

          # Set output
          echo "changelog<<EOF" >> $GITHUB_OUTPUT
          echo "$CHANGELOG" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body: |
            ## Changes in this release
            ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: false
```

## Best Practices

### Commit Messages
- **Use conventional commits**: Enables automated changelog generation
- **Be descriptive**: Clear, concise descriptions of changes
- **Include context**: Why the change was made, not just what
- **Reference issues**: Link to related issue numbers

### Changelog Organization
- **Group by type**: Features, fixes, breaking changes, etc.
- **Sort chronologically**: Newest changes first
- **Include dates**: Each version should have a release date
- **Link to commits**: Provide links for detailed information

### Version Management
- **Follow semver**: Major.Minor.Patch versioning
- **Document breaking changes**: Prominently display breaking changes
- **Provide migration guides**: Help users upgrade
- **Track deprecations**: Warn before removing features

### Maintenance
- **Update regularly**: Generate changelog with each release
- **Review before release**: Manually verify automated output
- **Keep format consistent**: Use same structure throughout
- **Archive old versions**: Keep full history available

## Notes

- Always use conventional commits for automatic changelog generation
- Include breaking changes at the top of changelog
- Provide migration guides for major version bumps
- Link to detailed documentation when needed
- Keep changelog entries user-focused (not technical)
- Review and edit generated changelogs before release
- Use semantic versioning consistently
- Automate changelog generation in CI/CD pipeline
- Consider using tools like standard-version or release-please
- Maintain changelog in git repository alongside code
