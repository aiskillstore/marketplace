---
name: create-issue
description: Create an issue in GitHub or Jira. Automatically detects if GitHub issues are enabled; if so creates a GitHub issue, otherwise creates a Jira issue.
allowed-tools: Bash(gh:*), Bash(jira:*), Bash(git:*), Read, Write
---

# Create Issue

Create an issue in the appropriate tracker (GitHub Issues or Jira).

## Step 1: Detect Issue Tracker

1. **Get repository name**: `basename $(git rev-parse --show-toplevel)`
2. **Check if GitHub issues are enabled**:

   ```bash
   gh repo view --json hasIssuesEnabled --jq '.hasIssuesEnabled'
   ```

   - If `true` → Create GitHub issue
   - If `false` → Create Jira issue

3. **Determine issue type**: Task, Bug, or Story
4. **Check for assignee** in user's request
5. **Determine priority/labels** based on severity

---

## GitHub Issues

If GitHub issues are enabled, use `gh issue create`.

### Step 2a: Write issue body to `issue-body.md`

Use the appropriate template based on issue type (see Templates section below).

**Note:** This file will be deleted after the command runs.

### Step 2b: Run gh command

```bash
gh issue create \
  --title "<SUMMARY>" \
  --body-file issue-body.md \
  --label "<LABEL>" && rm issue-body.md
```

Add `--assignee "<username>"` if user specified an assignee.

**Note:** No repo name prefix needed - GitHub issues are already scoped to the repository.

---

## Jira Issues

If GitHub issues are disabled, use `jira issue create`.

### Step 2a: Write issue body to `issue-body.md`

Use the appropriate template based on issue type (see Templates section below).

**Note:** This file will be deleted after the command runs.

### Step 2b: Run jira command

```bash
jira issue create --no-input \
  --type "<TYPE>" \
  --priority "<PRIORITY>" \
  --label "<LABEL>" \
  --summary "[<REPO-NAME>] <SUMMARY>" \
  --template issue-body.md && rm issue-body.md
```

Add `--assignee "<username>"` if user specified an assignee.

---

## Templates

Choose the appropriate template based on issue type:

### Template: Task

```markdown
## What

Provide a clear and concise description of the task.

## In Scope

- Define what is included in this task

## Out of Scope

- Clarify what is not covered

## Security and Compliance

- If no security/compliance impact, write: "No direct security or compliance impact."
- If there IS impact, be specific about which control/requirement is violated and the actual risk

## Testing Details

- Outline the testing strategy

## Technical Details

Include any remaining details such as code snippets, file locations, or tool suggestions.
```

---

### Template: Bug

```markdown
## Description

A concise description of the bug.

## Environment

- **Environment:** (e.g., Test, Production)
- **App Version:**
- **Browser/OS:**
- **Affected Component:**

## Actual Behaviour

Detailed description of what actually happened. Include any error messages, logs, or screenshots.

## Expected Behaviour

Detailed explanation of what should have happened.

## Steps to Reproduce

1. Step one
2. Step two
3. Step three

**Reproducibility:** (Always, Sometimes, Rarely)

## Impact & Severity

- **Impact:** Describe the impact on users or business operations
- **Severity:** (Critical, Major, Minor)

## Troubleshooting & Workaround

- Steps already taken to diagnose or fix the issue
- Temporary workaround available (if any)

## Additional Information

- Screenshots, videos, or additional logs
- Related bugs or tickets
- Potential fixes or areas to investigate (optional)
```

---

### Template: Story

```markdown
## Who

- **User Group:** Who will use or benefit from this feature (end-users, admins, editors, etc.)
- **Stakeholders:** Relevant internal teams or customer segments

## What

- **Intent:** Describe the goal of the story; focus on what needs to be achieved, not on technical implementation
- **Scope:** Outline the high-level functionality without UI specifics or library details

## Why

- **Business Value:** Explain how this feature improves UX, increases retention, or shortens the journey to issue resolution
- **Metrics/KPIs:** Connect the story to relevant performance indicators
- **Non-Functional Requirements:** Include performance, security, compliance, and any other quality requirements

## High-Level Description & Design

- **Overview:** Provide a brief narrative of the feature
- **Figma/Design Link:** [Insert link] with all relevant design notes
- **Design Requirements:** UI/UX must cater to all screen sizes, including very small devices. Include designs for buttons with text on two rows to support multiple languages

## Backend API & Contract Changes

- **API Changes:** Describe any required changes or new endpoints
- **Integration:** Specify the method for frontend integration
- **Performance & Security:** Highlight any potential performance issues or security considerations

## Frontend Considerations

- **Platform-Specific Notes:** List any particular requirements for different platforms
- **Error & Success Paths:** Clearly define both success and error flows

## Infrastructure & Compliance

- **Impact Assessment:** Evaluate any effects on infrastructure or security compliance standards
- **Performance & Cost:** Highlight any potential performance or cost implications

## Dashboard & Asset Management

- **Dashboard Impact:** Assess any configuration changes or new dashboard requirements
- **Asset Requirements:** Ensure all assets (images, text, translations) are available

## Dependencies & Risks

- **Dependencies:** List any related stories, external dependencies, or systems
- **Blockers:** Identify potential blockers that might impact progress
- **Risks:** Outline possible risks affecting feature delivery
- **Mitigation Strategies:** Describe actions to minimize or manage these risks

## Technical Documentation

- **Documentation Links:** Include links to relevant technical documentation or architecture diagrams
- **Additional Context:** Provide any extra technical notes that could aid implementation

## Environment & Release Notes

- **Environment Considerations:** Note any environment-specific details
- **Release Planning:** Detail feature flags, rollback plans, or special deployment instructions

## Testing Strategy

- **Testing Requirements:** Define testing requirements beyond acceptance criteria
- **Test Scenarios:** Outline key test cases and scenarios

## Acceptance Criteria

- Draft detailed acceptance criteria covering all success scenarios and all error paths
- Variations due to dynamic factors
- Ensure the criteria are measurable and leave no room for ambiguity

## Post-Release Monitoring

- **Monitoring Metrics:** Specify metrics or logs to monitor after release
- **Feedback Mechanism:** Outline how to gather user feedback and performance data post-deployment
```

---

## Priority Mapping (Jira only)

| Severity | Jira Priority |
| -------- | ------------- |
| Critical | Blocker |
| High | Critical |
| Medium | Major |
| Low | Minor |
| Info | Minor |

## Important Rules

- **GitHub Issues:**
  - Use `gh issue create` with `--body-file`
  - No repo name prefix needed (issues are scoped to repo)
  - Labels are simple strings (e.g., `bug`, `enhancement`, `documentation`)
- **Jira Issues:**
  - Always prefix summary with repo name: `[repo-name] Brief description`
  - Always use `--no-input` flag to prevent interactive prompts
  - Do NOT specify a project (`-p` or `--project`) - use default from user's config
  - Set 15 second timeout - if it hangs, the command is malformed
- **Both:**
  - Use Markdown format
  - Use `##` for main headings, `-` for bullet points
  - Use backticks for inline code
  - For sections not applicable, write "N/A" or "Nothing to mention"
  - Delete the temp file (`issue-body.md`) after creating the issue
