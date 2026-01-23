# Enforcement Setup Guide

This document provides copy-paste commands to set up automated enforcement for the GitHub Elements Tracking protocol.

---

## Core Philosophy

**Order matters. Time does not.**

- Enforcement validates STRUCTURE and SEQUENCE, not timing
- No stale detection, no heartbeat enforcement
- Validates: scope declarations, issue structure, conflict detection
- All commands use `gh` CLI only

---

## Quick Setup Checklist

- [ ] Create required labels (including thread types and violation labels)
- [ ] Install issue validation workflow
- [ ] Install thread initialization validator
- [ ] Install phase violation detector
- [ ] Install PR validation workflow (branch flow enforcement)
- [ ] Install scope conflict detector
- [ ] Install TEST thread scope enforcement
- [ ] Install demotion direction enforcement
- [ ] Install self-approval rejection

---

## Step 1: Create Required Labels

Run these commands ONCE per repository:

```bash
# Status labels
gh label create "ready" -d "Available for claiming" -c "0e8a16" 2>/dev/null || gh label edit "ready" -d "Available for claiming" -c "0e8a16"
gh label create "in-progress" -d "Actively being worked" -c "fbca04" 2>/dev/null || gh label edit "in-progress" -d "Actively being worked" -c "fbca04"
gh label create "needs-input" -d "Waiting for external input" -c "d93f0b" 2>/dev/null || gh label edit "needs-input" -d "Waiting for external input" -c "d93f0b"
gh label create "review-needed" -d "Ready for review" -c "1d76db" 2>/dev/null || gh label edit "review-needed" -d "Ready for review" -c "1d76db"
gh label create "completed" -d "Work finished" -c "0e8a16" 2>/dev/null || gh label edit "completed" -d "Work finished" -c "0e8a16"

# Completion label (review passed = completed + closed)
# Note: gate:passed/failed removed - use completed label and phase transitions instead

# Type labels (thread types)
gh label create "epic" -d "Epic/meta issue" -c "7057ff" 2>/dev/null || gh label edit "epic" -d "Epic/meta issue" -c "7057ff"
gh label create "type:implementation" -d "Implementation task" -c "0075ca" 2>/dev/null || gh label edit "type:implementation" -d "Implementation task" -c "0075ca"
gh label create "phase:dev" -d "Development thread" -c "0075ca" 2>/dev/null || gh label edit "phase:dev" -d "Development thread" -c "0075ca"
gh label create "phase:test" -d "Testing thread" -c "ffc107" 2>/dev/null || gh label edit "phase:test" -d "Testing thread" -c "ffc107"
gh label create "phase:review" -d "Review thread" -c "c5def5" 2>/dev/null || gh label edit "phase:review" -d "Review thread" -c "c5def5"
gh label create "sub-issue" -d "Part of larger issue" -c "bfd4f2" 2>/dev/null || gh label edit "sub-issue" -d "Part of larger issue" -c "bfd4f2"

# Violation labels
gh label create "violation:scope" -d "Scope declaration missing" -c "f9c5c5" 2>/dev/null || gh label edit "violation:scope" -d "Scope declaration missing" -c "f9c5c5"
gh label create "violation:phase" -d "Phase violation (wrong action for thread type)" -c "f9c5c5" 2>/dev/null || gh label edit "violation:phase" -d "Phase violation (wrong action for thread type)" -c "f9c5c5"
gh label create "violation:wave-order" -d "Wave order violation" -c "f9c5c5" 2>/dev/null || gh label edit "violation:wave-order" -d "Wave order violation" -c "f9c5c5"
gh label create "violation:self-approval" -d "Attempted self-approval" -c "f9c5c5" 2>/dev/null || gh label edit "violation:self-approval" -d "Attempted self-approval" -c "f9c5c5"

# Wave labels (ordered checklists)
for i in 1 2 3 4 5 6 7 8 9 10; do
  gh label create "wave:$i" -d "Wave $i" -c "bfdadc" 2>/dev/null || gh label edit "wave:$i" -d "Wave $i" -c "bfdadc"
done
gh label create "wave:eval" -d "Evaluation wave" -c "d4c5f9" 2>/dev/null || gh label edit "wave:eval" -d "Evaluation wave" -c "d4c5f9"
gh label create "wave:fix" -d "Fix wave (after eval fail)" -c "f9d4c5" 2>/dev/null || gh label edit "wave:fix" -d "Fix wave (after eval fail)" -c "f9d4c5"

echo "Labels created successfully!"
```

**Note**: No priority labels. Order is determined by wave assignment, not urgency.

---

## Step 2: Issue Validation Workflow

Create `.github/workflows/issue-validation.yml`:

```yaml
name: Issue Validation

on:
  issues:
    types: [opened, edited, labeled, assigned]
  issue_comment:
    types: [created]

jobs:
  validate-issue:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Check Epic Label Requirements
        if: contains(github.event.issue.labels.*.name, 'epic')
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.issue.body || '';

            const required = ['## Vision', '## Scope', '## Acceptance Criteria'];
            const missing = required.filter(section => !body.includes(section));

            if (missing.length > 0) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: `## Validation Warning

This epic issue is missing required sections:
${missing.map(s => `- ${s}`).join('\n')}

Please update the issue body to include these sections.

See: [Epic Coordinator Playbook](../references/P2-epic-coordinator-playbook.md)`
              });
            }

      - name: Check Implementation Issue Requirements
        if: contains(github.event.issue.labels.*.name, 'type:implementation')
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.issue.body || '';

            const required = ['## Requirements', '## Acceptance Criteria'];
            const missing = required.filter(section => !body.includes(section));

            if (missing.length > 0) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: `## Validation Warning

This implementation issue is missing required sections:
${missing.map(s => `- ${s}`).join('\n')}

Please update the issue body to include these sections.`
              });
            }

      - name: Remind Scope Declaration on Claim
        if: github.event.action == 'assigned'
        uses: actions/github-script@v7
        with:
          script: |
            // Post reminder about required scope declaration
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## Reminder: Scope Declaration Required

@${context.payload.issue.assignee.login} - Please post a scope declaration before beginning work.

Required format:
\`\`\`markdown
### Scope Declaration
Files I will modify:
- path/to/file1.ts
- path/to/file2.ts

Files I will NOT modify:
- path/to/other.ts (belongs to #XXX)
\`\`\`

**Order**: claim → scope declaration → then work begins.

See: [Task Agent Playbook](../references/P1-task-agent-playbook.md)`
            });
```

---

## Step 3: Scope Conflict Detector

Create `.github/workflows/scope-conflict.yml`:

```yaml
name: Scope Conflict Detector

on:
  issue_comment:
    types: [created]

jobs:
  detect-scope-conflicts:
    runs-on: ubuntu-latest
    if: contains(github.event.comment.body, '### Scope Declaration') || contains(github.event.comment.body, '## Scope Declaration')
    permissions:
      issues: write
    steps:
      - name: Check for Scope Conflicts
        uses: actions/github-script@v7
        with:
          script: |
            const issueNumber = context.issue.number;
            const commentBody = context.payload.comment.body;

            // Extract files from scope declaration
            const filesMatch = commentBody.match(/Files I will modify:\n([\s\S]*?)(?:\n\n|Files I will NOT)/);
            if (!filesMatch) return;

            const myFiles = filesMatch[1]
              .split('\n')
              .map(line => line.replace(/^[-*]\s*/, '').trim())
              .filter(f => f.length > 0);

            if (myFiles.length === 0) return;

            // Get epic label to find related issues
            const issue = await github.rest.issues.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: issueNumber
            });

            const epicLabel = issue.data.labels.find(l => l.name.startsWith('epic:'));
            if (!epicLabel) return;

            // Get all in-progress issues in same epic
            const relatedIssues = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels: `in-progress,${epicLabel.name}`,
              state: 'open',
              per_page: 50
            });

            const conflicts = [];

            for (const relatedIssue of relatedIssues.data) {
              if (relatedIssue.number === issueNumber) continue;

              // Get comments for related issue
              const comments = await github.rest.issues.listComments({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: relatedIssue.number,
                per_page: 50
              });

              for (const comment of comments.data) {
                if (!comment.body.includes('Scope Declaration')) continue;

                // Extract their files
                const theirFilesMatch = comment.body.match(/Files I will modify:\n([\s\S]*?)(?:\n\n|Files I will NOT)/);
                if (!theirFilesMatch) continue;

                const theirFiles = theirFilesMatch[1]
                  .split('\n')
                  .map(line => line.replace(/^[-*]\s*/, '').trim())
                  .filter(f => f.length > 0);

                // Check for overlaps
                const overlaps = myFiles.filter(f => theirFiles.includes(f));
                if (overlaps.length > 0) {
                  conflicts.push({
                    issue: relatedIssue.number,
                    files: overlaps
                  });
                }
              }
            }

            if (conflicts.length > 0) {
              const conflictDetails = conflicts.map(c =>
                `- #${c.issue}: ${c.files.join(', ')}`
              ).join('\n');

              // Post to current issue
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issueNumber,
                body: `## Scope Conflict Detected

Your scope declaration overlaps with other in-progress issues:

${conflictDetails}

**Action Required**: Coordinate with the other issues before modifying shared files.

See: [Multi-Instance Protocol](../references/P5-multi-instance-protocol.md)`
              });

              // Post to conflicting issues
              for (const conflict of conflicts) {
                await github.rest.issues.createComment({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: conflict.issue,
                  body: `## Scope Conflict Alert

#${issueNumber} has declared scope that overlaps with your claimed files:

- ${conflict.files.join('\n- ')}

**Action Required**: Coordinate before either issue modifies these files.`
                });
              }
            }
```

---

## Step 4: PR Validation

Create `.github/workflows/pr-validation.yml`:

```yaml
name: PR Validation

on:
  pull_request:
    types: [opened, synchronize, ready_for_review]

jobs:
  validate-pr:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      issues: read
    steps:
      - name: Check Linked Issue
        uses: actions/github-script@v7
        with:
          script: |
            const prBody = context.payload.pull_request.body || '';

            // Check for issue reference
            const issueMatch = prBody.match(/#(\d+)/);
            if (!issueMatch) {
              await github.rest.pulls.createReview({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: context.issue.number,
                event: 'REQUEST_CHANGES',
                body: `## PR Validation Failed

This PR must be linked to an issue.

Please add "Closes #XXX" or "Part of #XXX" to the PR description.`
              });
              return;
            }

            // Check if issue exists and is in-progress or review-needed
            const issueNumber = parseInt(issueMatch[1]);
            try {
              const issue = await github.rest.issues.get({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issueNumber
              });

              const validLabels = ['in-progress', 'review-needed'];
              const hasValidLabel = issue.data.labels.some(l =>
                validLabels.includes(l.name)
              );

              if (!hasValidLabel) {
                await github.rest.pulls.createReview({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  pull_number: context.issue.number,
                  event: 'COMMENT',
                  body: `## Warning

Linked issue #${issueNumber} is not in "in-progress" or "review-needed" state.

Current labels: ${issue.data.labels.map(l => l.name).join(', ')}`
                });
              }
            } catch (error) {
              console.log(`Issue #${issueNumber} not found or inaccessible`);
            }

      - name: Check for Scope Conflicts
        uses: actions/github-script@v7
        with:
          script: |
            // Get files changed in this PR
            const files = await github.rest.pulls.listFiles({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.issue.number,
              per_page: 100
            });

            const myFiles = files.data.map(f => f.filename);

            // Get other open PRs
            const prs = await github.rest.pulls.list({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              per_page: 50
            });

            const conflicts = [];

            for (const pr of prs.data) {
              if (pr.number === context.issue.number) continue;

              const theirFiles = await github.rest.pulls.listFiles({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: pr.number,
                per_page: 100
              });

              const overlaps = myFiles.filter(f =>
                theirFiles.data.some(tf => tf.filename === f)
              );

              if (overlaps.length > 0) {
                conflicts.push({
                  pr: pr.number,
                  title: pr.title,
                  files: overlaps
                });
              }
            }

            if (conflicts.length > 0) {
              const conflictDetails = conflicts.map(c =>
                `- PR #${c.pr} (${c.title}): ${c.files.join(', ')}`
              ).join('\n');

              await github.rest.pulls.createReview({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: context.issue.number,
                event: 'COMMENT',
                body: `## File Conflict Warning

This PR modifies files that are also modified by other open PRs:

${conflictDetails}

**Action**: Coordinate merge order or rebase after other PRs merge.`
              });
            }
```

---

## Step 5: Thread Initialization Validator

Create `.github/workflows/thread-init.yml`:

```yaml
name: Thread Initialization Validator

on:
  issues:
    types: [opened]

jobs:
  validate-thread-init:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'phase:dev') || contains(github.event.issue.labels.*.name, 'phase:test') || contains(github.event.issue.labels.*.name, 'phase:review')
    permissions:
      issues: write
    steps:
      - name: Check Required Skills Section
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.issue.body || '';

            const required = ['### Required Skills', '### Thread Type', '### Scope'];
            const missing = required.filter(section => !body.includes(section));

            if (missing.length > 0) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: `## Thread Initialization Warning

This thread is missing required sections:
${missing.map(s => \`- \${s}\`).join('\\n')}

**Required Format:**
\\\`\\\`\\\`markdown
### Required Skills
- skill-name-1
- skill-name-2

### Thread Type
<dev | test | review>

### Scope
<what this thread covers>
\\\`\\\`\\\`

Agents must know which skills to activate before participating.`
              });
            }
```

---

## Step 6: Phase Violation Detector

Create `.github/workflows/phase-violation.yml`:

```yaml
name: Phase Violation Detector

on:
  issue_comment:
    types: [created]

jobs:
  detect-phase-violations:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Check for Verdict in Dev Thread
        if: contains(github.event.issue.labels.*.name, 'phase:dev')
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.comment.body || '';

            // Detect verdict language in dev thread
            const verdictPatterns = [
              /## .*VERDICT.*PASS/i,
              /## .*VERDICT.*FAIL/i,
              /### Verdict: PASS/i,
              /### Verdict: FAIL/i,
              /APPROVED/i,
              /REJECTED/i
            ];

            const hasVerdict = verdictPatterns.some(p => p.test(body));

            if (hasVerdict) {
              // Add violation label
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                labels: ['violation:phase']
              });

              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: `## Phase Violation Notice

@${context.payload.comment.user.login} - This is a **dev thread**. Definitive verdicts belong in **review threads**.

### What Happened
You posted what appears to be a verdict or approval/rejection.

### Correct Approach
- In dev threads: Post observations, questions, suggestions
- Wait for: testing phase → review phase
- Then: Post verdicts in the review thread

### Action Required
Please retract the verdict. Development is ongoing.

**Order: Dev → Test → Review. Cannot skip phases.**`
              });
            }
```

---

## Step 7: TEST Thread Scope Enforcement

Create `.github/workflows/test-scope.yml`:

```yaml
name: TEST Thread Scope Enforcement

on:
  issue_comment:
    types: [created]

jobs:
  enforce-test-scope:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'phase:test')
    permissions:
      issues: write
    steps:
      - name: Check for Scope Violations in TEST Thread
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.comment.body || '';
            const violations = [];

            // Patterns that indicate TEST scope violations
            const newTestPatterns = [
              /wrote.*new.*test/i,
              /added.*test/i,
              /created.*test/i,
              /implementing.*test/i,
              /writing.*test/i,
              /new test case/i,
              /test file.*created/i
            ];

            const structuralPatterns = [
              /refactor/i,
              /restructur/i,
              /rewrit/i,
              /major change/i,
              /architecture/i,
              /redesign/i
            ];

            // Check for new test writing (TEST cannot write tests)
            const hasNewTest = newTestPatterns.some(p => p.test(body));
            if (hasNewTest) {
              violations.push({
                type: 'NEW_TEST',
                message: 'Writing new tests is DEV work, not TEST work'
              });
            }

            // Check for structural changes
            const hasStructural = structuralPatterns.some(p => p.test(body));
            if (hasStructural) {
              violations.push({
                type: 'STRUCTURAL',
                message: 'Structural changes belong in DEV thread'
              });
            }

            if (violations.length > 0) {
              // Add violation label
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                labels: ['violation:phase']
              });

              const violationDetails = violations.map(v =>
                `- **${v.type}**: ${v.message}`
              ).join('\n');

              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: `## TEST Thread Scope Violation

@${context.payload.comment.user.login} - This is a **TEST thread**. The following actions are not allowed:

${violationDetails}

### What TEST Threads Can Do
- [x] Run existing tests
- [x] Fix bugs that cause test failures (minimal changes)
- [x] Report test results

### What TEST Threads CANNOT Do
- [ ] Write new tests (tests are CODE = DEV work)
- [ ] Make structural changes
- [ ] Do rewrites or refactoring

### Correct Approach
If you need to write new tests or make structural changes:
1. **Close this TEST thread**
2. **Reopen the DEV thread**
3. Do the work in DEV
4. When done, advance back to TEST

**Order: DEV (write tests) → TEST (run tests) → REVIEW (evaluate)**`
              });
            }
```

---

## Step 8: Demotion Direction Enforcement

Create `.github/workflows/demotion-enforcement.yml`:

```yaml
name: Demotion Direction Enforcement

on:
  issue_comment:
    types: [created]

jobs:
  enforce-demotion-direction:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'phase:review')
    permissions:
      issues: write
    steps:
      - name: Check for Incorrect Demotion
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.comment.body || '';

            // Patterns that indicate incorrect demotion to TEST
            const wrongDemotionPatterns = [
              /demot.*to.*test/i,
              /back.*to.*test/i,
              /return.*to.*test/i,
              /reopen.*test.*thread/i,
              /test.*thread.*reopen/i
            ];

            const hasWrongDemotion = wrongDemotionPatterns.some(p => p.test(body));

            if (hasWrongDemotion) {
              // Add violation label
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                labels: ['violation:phase']
              });

              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: `## Demotion Direction Violation

@${context.payload.comment.user.login} - **REVIEW can ONLY demote to DEV, never to TEST.**

### Why?
- TEST can only RUN existing tests
- TEST can only FIX bugs (minimal changes)
- TEST cannot write new tests or make structural fixes
- Any fix from REVIEW findings requires DEV work

### Correct Demotion Flow
\`\`\`
REVIEW fails → Demote to DEV → DEV fixes issues → TEST runs tests → REVIEW re-evaluates
\`\`\`

### Never
\`\`\`
REVIEW fails → Demote to TEST  ← WRONG
\`\`\`

Please update your comment to demote to DEV thread instead.`
              });
            }
```

---

## Step 9: Self-Approval Rejection

Add to PR Validation workflow (`.github/workflows/pr-validation.yml`):

```yaml
      - name: Check for Self-Approval Claims
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.pull_request.body || '';

            // Detect self-approval language
            const selfApprovalPatterns = [
              /tested.*myself/i,
              /reviewed.*myself/i,
              /self.*tested/i,
              /self.*reviewed/i,
              /i.*tested.*this/i,
              /i.*reviewed.*this/i,
              /ready.*to.*merge/i
            ];

            const hasSelfApproval = selfApprovalPatterns.some(p => p.test(body));

            if (hasSelfApproval) {
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                labels: ['violation:self-approval']
              });

              await github.rest.pulls.createReview({
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: context.issue.number,
                event: 'REQUEST_CHANGES',
                body: `## PR Rejected: Self-Approval Not Allowed

PRs cannot be self-approved.

### Correct Flow
1. PR merges to **testing branch** first
2. **Test thread** opened, independent testing performed
3. If tests pass 100% → merges to **review branch**
4. **Review thread** opened, independent review performed
5. If review passes unanimously → merges to **main**

### Action Required
1. Remove self-approval claims from PR description
2. Wait for independent testing and review
3. Do NOT merge to main directly

**This is not negotiable.**`
              });
            }
```

---

## Verification

After setup, verify everything works:

```bash
# Check labels
gh label list | grep -E "(ready|in-progress|epic|wave)"

# Check workflows
gh workflow list

# Test issue validation
gh issue create --title "Test Issue" --label "type:implementation" --body "Test"
# Should trigger validation warning

# Clean up test
gh issue close <number> --reason "not planned"
gh issue delete <number> --yes
```

---

## Customization

### Add Custom Labels

```bash
gh label create "your-label" -d "Description" -c "color"
```

### Add Custom Wave Labels

```bash
for i in 11 12 13 14 15; do
  gh label create "wave:$i" -d "Wave $i" -c "bfdadc"
done
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not running | Check workflow permissions in repo settings |
| Labels not created | Run `gh auth login` first |
| Conflicts not detected | Ensure scope declarations use exact format |
| PR validation not triggering | Check PR has linked issue reference |

---

## Uninstall

To remove enforcement:

```bash
# Remove workflows
rm .github/workflows/issue-validation.yml
rm .github/workflows/scope-conflict.yml
rm .github/workflows/pr-validation.yml
rm .github/workflows/thread-init.yml
rm .github/workflows/phase-violation.yml
rm .github/workflows/test-scope.yml
rm .github/workflows/demotion-enforcement.yml

# Remove violation labels (optional)
gh label delete "violation:scope" --yes
gh label delete "violation:phase" --yes
gh label delete "violation:wave-order" --yes
gh label delete "violation:self-approval" --yes

# Keep other labels - they're useful even without automation
```
