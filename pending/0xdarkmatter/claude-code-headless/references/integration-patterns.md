# Integration Patterns

Patterns for integrating Claude Code into CI/CD, scripts, and automation.

## CI/CD Pipelines

### GitHub Actions

```yaml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Get PR diff
        id: diff
        run: |
          gh pr diff ${{ github.event.pull_request.number }} > diff.txt
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Run Claude review
        run: |
          result=$(cat diff.txt | claude -p "Review this PR diff for:
          - Security vulnerabilities
          - Performance issues
          - Code quality

          Output as markdown." \
            --output-format json \
            --allowedTools "Read,Grep")

          echo "$result" | jq -r '.result' > review.md
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Post review comment
        run: |
          gh pr comment ${{ github.event.pull_request.number }} \
            --body-file review.md
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### GitLab CI

```yaml
claude-review:
  stage: review
  script:
    - git diff origin/main...HEAD > diff.txt
    - |
      cat diff.txt | claude -p "Security review" \
        --output-format json \
        --allowedTools "Read" \
        > review.json
    - cat review.json | jq -r '.result' > review.md
  artifacts:
    paths:
      - review.md
  only:
    - merge_requests
```

### Jenkins

```groovy
pipeline {
    agent any
    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-api-key')
    }
    stages {
        stage('Claude Analysis') {
            steps {
                script {
                    def result = sh(
                        script: '''
                            claude -p "Analyze build issues" \
                                --output-format json \
                                --allowedTools "Read,Bash"
                        ''',
                        returnStdout: true
                    )
                    def json = readJSON text: result
                    if (json.is_error) {
                        error "Claude analysis failed: ${json.result}"
                    }
                }
            }
        }
    }
}
```

## Shell Scripts

### PR Review Script

```bash
#!/bin/bash
set -euo pipefail

audit_pr() {
    local pr_number="$1"

    # Get PR diff
    diff=$(gh pr diff "$pr_number")

    # Run Claude analysis
    result=$(echo "$diff" | claude -p \
        --append-system-prompt "Security review. Output JSON: {severity, findings, recommendations}" \
        --output-format json \
        --allowedTools "Read,Grep,WebSearch")

    # Check for errors
    if [[ $(echo "$result" | jq -r '.is_error') == "true" ]]; then
        echo "Error: $(echo "$result" | jq -r '.result')" >&2
        return 1
    fi

    echo "$result" | jq -r '.result'
}

# Usage
audit_pr 123
```

### Batch Processing

```bash
#!/bin/bash
set -euo pipefail

process_files() {
    local pattern="$1"
    local prompt="$2"

    find . -name "$pattern" -print0 | while IFS= read -r -d '' file; do
        echo "Processing: $file"

        result=$(cat "$file" | claude -p "$prompt" \
            --output-format json \
            --allowedTools "Read")

        if [[ $(echo "$result" | jq -r '.is_error') == "false" ]]; then
            echo "$result" | jq -r '.result' > "${file}.analysis.md"
        fi
    done
}

# Usage
process_files "*.py" "Analyze this Python file for issues"
```

### Multi-Turn Workflow

```bash
#!/bin/bash
set -euo pipefail

run_workflow() {
    # Step 1: Initial analysis
    result=$(claude -p "Analyze the codebase structure" \
        --output-format json \
        --allowedTools "Read,Glob,Grep")

    session=$(echo "$result" | jq -r '.session_id')
    echo "Session: $session"

    # Step 2: Deep dive with context
    result=$(claude --resume "$session" \
        "Now examine the authentication module in detail" \
        --output-format json)

    # Step 3: Generate report
    claude --resume "$session" \
        "Generate a security report in markdown" \
        --output-format json | jq -r '.result' > report.md

    echo "Report saved to report.md"
}

run_workflow
```

## Pre-commit Hooks

### Python Code Review

```bash
#!/bin/bash
# .git/hooks/pre-commit

staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [[ -n "$staged_files" ]]; then
    echo "Running Claude review on staged Python files..."

    for file in $staged_files; do
        result=$(cat "$file" | claude -p \
            "Quick code review. Report only critical issues. Be concise." \
            --output-format json \
            --allowedTools "Read" 2>/dev/null)

        if [[ $(echo "$result" | jq -r '.is_error') == "false" ]]; then
            review=$(echo "$result" | jq -r '.result')
            if [[ "$review" != *"no issues"* ]] && [[ "$review" != *"looks good"* ]]; then
                echo "Review for $file:"
                echo "$review"
                echo ""
            fi
        fi
    done
fi
```

## Scheduled Tasks

### Daily Code Quality Report

```bash
#!/bin/bash
# Run via cron: 0 8 * * * /path/to/daily-report.sh

REPORT_DIR="/var/reports/claude"
DATE=$(date +%Y-%m-%d)

mkdir -p "$REPORT_DIR"

cd /path/to/project

result=$(claude -p "Generate a daily code quality report covering:
1. Recent changes summary
2. Potential issues
3. Recommendations

Use git log for recent changes." \
    --output-format json \
    --allowedTools "Bash,Read,Grep")

echo "$result" | jq -r '.result' > "$REPORT_DIR/report-$DATE.md"

# Email or Slack notification
# curl -X POST "$SLACK_WEBHOOK" -d "{\"text\": \"Daily report ready\"}"
```

## Web Application Integration

### Express.js Endpoint

```javascript
const express = require('express');
const { spawn } = require('child_process');

const app = express();
app.use(express.json());

app.post('/api/claude', async (req, res) => {
    const { prompt, tools } = req.body;

    const args = ['-p', prompt, '--output-format', 'json'];
    if (tools) {
        args.push('--allowedTools', tools.join(','));
    }

    const claude = spawn('claude', args);
    let output = '';

    claude.stdout.on('data', (data) => {
        output += data.toString();
    });

    claude.on('close', (code) => {
        try {
            const result = JSON.parse(output);
            res.json(result);
        } catch (e) {
            res.status(500).json({ error: 'Failed to parse response' });
        }
    });
});

app.listen(3000);
```

### Python FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json

app = FastAPI()

class ClaudeRequest(BaseModel):
    prompt: str
    tools: list[str] | None = None

@app.post("/api/claude")
async def run_claude(request: ClaudeRequest):
    args = ["claude", "-p", request.prompt, "--output-format", "json"]

    if request.tools:
        args.extend(["--allowedTools", ",".join(request.tools)])

    proc = subprocess.run(args, capture_output=True, text=True)

    try:
        result = json.loads(proc.stdout)
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse response")
```

## Error Handling Patterns

### Retry with Backoff

```bash
#!/bin/bash

run_with_retry() {
    local max_attempts=3
    local attempt=1
    local delay=5

    while [[ $attempt -le $max_attempts ]]; do
        result=$(claude -p "$1" --output-format json 2>&1)

        if [[ $(echo "$result" | jq -r '.is_error // true') == "false" ]]; then
            echo "$result"
            return 0
        fi

        echo "Attempt $attempt failed, retrying in ${delay}s..." >&2
        sleep $delay
        attempt=$((attempt + 1))
        delay=$((delay * 2))
    done

    echo "All attempts failed" >&2
    return 1
}
```

### Graceful Degradation

```bash
#!/bin/bash

analyze_with_fallback() {
    # Try Claude first
    result=$(claude -p "$1" --output-format json 2>/dev/null)

    if [[ -z "$result" ]] || [[ $(echo "$result" | jq -r '.is_error') == "true" ]]; then
        echo "Claude unavailable, using fallback analysis" >&2
        # Fallback to simpler analysis
        run_basic_linter "$2"
        return
    fi

    echo "$result" | jq -r '.result'
}
```
