# Reviewdog Reporter Formats

This reference documents the available reporter formats and output modes for reviewdog.

## Table of Contents

- [Reporter Types](#reporter-types)
- [GitHub Reporters](#github-reporters)
- [GitLab Reporters](#gitlab-reporters)
- [Generic Reporters](#generic-reporters)
- [Input Formats](#input-formats)
- [Configuration Examples](#configuration-examples)

## Reporter Types

Reviewdog supports multiple reporter formats for different CI/CD platforms and use cases.

### Quick Reference

| Reporter | Platform | Use Case | Requires Token |
|----------|----------|----------|----------------|
| `local` | Any | Local development, terminal output | No |
| `github-check` | GitHub | Check Runs API | Yes |
| `github-pr-check` | GitHub | Check Runs on PR | Yes |
| `github-pr-review` | GitHub | PR review comments | Yes |
| `gitlab-mr-discussion` | GitLab | MR discussion threads | Yes |
| `gitlab-mr-commit` | GitLab | MR commit comments | Yes |
| `bitbucket-code-report` | Bitbucket | Code Insights | Yes |
| `gerrit-change-review` | Gerrit | Change review comments | Yes |

## GitHub Reporters

### github-check

Posts findings as GitHub Check Runs (visible in PR checks tab).

**Usage**:
```bash
reviewdog -reporter=github-check
```

**Environment Variables**:
```bash
export REVIEWDOG_GITHUB_API_TOKEN="ghp_xxxxxxxxxxxx"
# or use GitHub Actions built-in token
export REVIEWDOG_GITHUB_API_TOKEN="${GITHUB_TOKEN}"
```

**Permissions Required**:
- `checks: write`
- `contents: read`

**Output**:
- Appears in "Checks" tab of PR
- Shows annotation count
- Can block PR merge if configured

**Example**:
```yaml
- name: Run security scan
  env:
    REVIEWDOG_GITHUB_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    bandit -r . -f json | reviewdog -f=bandit -reporter=github-check
```

---

### github-pr-check

Similar to `github-check` but specifically for pull requests.

**Usage**:
```bash
reviewdog -reporter=github-pr-check
```

**Differences from github-check**:
- Only runs on PRs (not on push to branches)
- Better integration with PR workflow
- Recommended for most PR-based workflows

---

### github-pr-review

Posts findings as inline PR review comments.

**Usage**:
```bash
reviewdog -reporter=github-pr-review
```

**Permissions Required**:
- `pull-requests: write`
- `contents: read`

**Features**:
- Inline comments on specific lines
- Grouped by file
- Shows in "Files changed" tab
- Can suggest changes

**Filter Modes**:
```bash
# Only comment on added lines
reviewdog -reporter=github-pr-review -filter-mode=added

# Comment on modified context (added + surrounding)
reviewdog -reporter=github-pr-review -filter-mode=diff_context

# Comment on all findings in changed files
reviewdog -reporter=github-pr-review -filter-mode=file
```

**Example with Suggested Changes**:
```bash
# Some tools can suggest fixes
semgrep --config=auto --json | \
  reviewdog -f=semgrep -reporter=github-pr-review
```

---

## GitLab Reporters

### gitlab-mr-discussion

Posts findings as GitLab merge request discussion threads.

**Usage**:
```bash
reviewdog -reporter=gitlab-mr-discussion
```

**Environment Variables**:
```bash
export REVIEWDOG_GITLAB_API_TOKEN="glpat-xxxxxxxxxxxx"
export CI_API_V4_URL="https://gitlab.com/api/v4"
export CI_MERGE_REQUEST_IID="123"
export CI_PROJECT_ID="456"
```

**Permissions Required**:
- API access with `api` scope
- Write access to merge requests

**Features**:
- Creates discussion threads on specific lines
- Supports threaded conversations
- Can mark as resolved

**Example (.gitlab-ci.yml)**:
```yaml
security_review:
  script:
    - bandit -r . -f json | reviewdog -f=bandit -reporter=gitlab-mr-discussion
  variables:
    REVIEWDOG_GITLAB_API_TOKEN: $GITLAB_TOKEN
  only:
    - merge_requests
```

---

### gitlab-mr-commit

Posts findings as commit comments on merge request.

**Usage**:
```bash
reviewdog -reporter=gitlab-mr-commit
```

**Differences from gitlab-mr-discussion**:
- Comments attached to specific commits
- Less conversational
- Good for historical tracking

---

## Generic Reporters

### local

Outputs findings to terminal/console (default for local development).

**Usage**:
```bash
reviewdog -reporter=local
```

**Output Format**:
```
app/models.py:42:10: [error] SQL Injection vulnerability (CWE-89) [bandit]
app/views.py:15:5: [warning] Use of hardcoded password (CWE-798) [semgrep]
```

**Features**:
- No API token required
- Color-coded severity levels
- File path and line numbers
- Works in any CI environment

**Example**:
```bash
# Quick local scan
semgrep --config=auto --json | reviewdog -f=semgrep -reporter=local
```

---

### bitbucket-code-report

Posts findings to Bitbucket Code Insights.

**Usage**:
```bash
reviewdog -reporter=bitbucket-code-report
```

**Environment Variables**:
```bash
export BITBUCKET_USER="username"
export BITBUCKET_PASSWORD="app_password"
```

---

### gerrit-change-review

Posts findings as Gerrit change review comments.

**Usage**:
```bash
reviewdog -reporter=gerrit-change-review
```

**Environment Variables**:
```bash
export GERRIT_USERNAME="user"
export GERRIT_PASSWORD="password"
export GERRIT_CHANGE_ID="I1234567890abcdef"
export GERRIT_REVISION_ID="1"
export GERRIT_ADDRESS="https://gerrit.example.com"
```

---

## Input Formats

Reviewdog supports multiple input formats from security tools:

### Supported Formats

| Format | Tools | Description |
|--------|-------|-------------|
| `checkstyle` | Generic XML | Checkstyle XML format |
| `sarif` | Many SAST tools | Static Analysis Results Interchange Format |
| `rdjson` | Custom tools | Reviewdog Diagnostic Format (JSON) |
| `rdjsonl` | Custom tools | Reviewdog Diagnostic Format (JSON Lines) |
| `diff` | diff, git-diff | Unified diff format |
| `bandit` | Bandit | Bandit JSON output |
| `semgrep` | Semgrep | Semgrep JSON output |
| `gitleaks` | Gitleaks | Gitleaks JSON output |
| `hadolint` | Hadolint | Hadolint JSON output |
| `checkov` | Checkov | Checkov JSON output |
| `shellcheck` | ShellCheck | ShellCheck JSON output |
| `eslint` | ESLint | ESLint JSON output |

### rdjson Format (Custom Tools)

Use this format to integrate custom security scanners:

```json
{
  "source": {
    "name": "my-security-scanner",
    "url": "https://github.com/example/scanner"
  },
  "severity": "ERROR",
  "diagnostics": [
    {
      "message": "Vulnerability description",
      "location": {
        "path": "src/app.py",
        "range": {
          "start": {"line": 42, "column": 10},
          "end": {"line": 42, "column": 30}
        }
      },
      "severity": "ERROR",
      "code": {
        "value": "CWE-89",
        "url": "https://cwe.mitre.org/data/definitions/89.html"
      },
      "suggestions": [
        {
          "text": "Use parameterized queries",
          "range": {
            "start": {"line": 42, "column": 10},
            "end": {"line": 42, "column": 30}
          },
          "replacement": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
        }
      ]
    }
  ]
}
```

**Severity Levels**:
- `ERROR` - High severity, should block PR
- `WARNING` - Medium severity, should review
- `INFO` - Low severity, informational

**Usage**:
```bash
./my-scanner --output json | reviewdog -f=rdjson -reporter=github-pr-review
```

---

## Configuration Examples

### Multi-Reporter Setup

Run the same scan with different reporters based on environment:

```bash
#!/bin/bash

if [ -n "$GITHUB_ACTIONS" ]; then
  REPORTER="github-pr-review"
elif [ -n "$GITLAB_CI" ]; then
  REPORTER="gitlab-mr-discussion"
else
  REPORTER="local"
fi

semgrep --config=auto --json | \
  reviewdog -f=semgrep -reporter="$REPORTER"
```

---

### .reviewdog.yml Configuration

Define multiple runners with different reporters:

```yaml
runner:
  critical-findings:
    cmd: semgrep --severity=ERROR --json
    format: semgrep
    name: Critical Security Issues
    level: error
    reporter: github-pr-review

  warnings:
    cmd: semgrep --severity=WARNING --json
    format: semgrep
    name: Security Warnings
    level: warning
    reporter: github-pr-check

  info:
    cmd: semgrep --severity=INFO --json
    format: semgrep
    name: Security Info
    level: info
    reporter: local
```

---

### Advanced GitHub Actions Example

```yaml
name: Security Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  checks: write

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup reviewdog
        uses: reviewdog/action-setup@v1

      # Critical findings - Block PR
      - name: Critical Security Scan
        env:
          REVIEWDOG_GITHUB_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          semgrep --severity=ERROR --json | \
            reviewdog -f=semgrep \
                     -name="Critical" \
                     -reporter=github-pr-review \
                     -filter-mode=added \
                     -fail-on-error=true \
                     -level=error

      # Warnings - Comment but don't block
      - name: Security Warnings
        if: always()
        env:
          REVIEWDOG_GITHUB_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          semgrep --severity=WARNING --json | \
            reviewdog -f=semgrep \
                     -name="Warnings" \
                     -reporter=github-pr-check \
                     -filter-mode=diff_context \
                     -level=warning
```

---

## Troubleshooting

### Issue: Comments not appearing

**Check**:
1. Token has correct permissions
2. Reporter matches CI platform
3. Running in PR/MR context (not on main branch)
4. Filter mode is not too restrictive

### Issue: Duplicate comments

**Solution**:
- Use `filter-mode=added` to only comment on new code
- Configure reviewdog to run only once per PR

### Issue: Rate limiting

**Solution**:
- Batch findings with `github-pr-check` instead of individual comments
- Use GitHub App token instead of PAT for higher rate limits

---

## References

- [Reviewdog Reporter Documentation](https://github.com/reviewdog/reviewdog#reporters)
- [rdjson Format Specification](https://github.com/reviewdog/reviewdog/tree/master/proto/rdf)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
