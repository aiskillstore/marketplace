# Issue Comment Format Template

This template defines the standard format for posting conversation exchanges to GitHub Issue threads.

## Avatar URLs

| Name | Agent ID | Avatar URL |
|------|----------|------------|
| **Emasoft** | Owner | `https://avatars.githubusercontent.com/u/713559?v=4&s=77` |
| **Claude** | Orchestrator | `../../../../assets/avatars/claude.png` |
| **Hephaestus** | `ghe:dev-thread-manager` | `../../../../assets/avatars/hephaestus.png` |
| **Artemis** | `ghe:test-thread-manager` | `../../../../assets/avatars/artemis.png` |
| **Hera** | `ghe:review-thread-manager` | `../../../../assets/avatars/hera.png` |
| **Athena** | `ghe:github-elements-orchestrator` | `../../../../assets/avatars/athena.png` |
| **Themis** | `ghe:phase-gate` | `../../../../assets/avatars/themis.png` |
| **Mnemosyne** | `ghe:memory-sync` | `../../../../assets/avatars/mnemosyne.png` |
| **Ares** | `ghe:enforcement` | `../../../../assets/avatars/ares.png` |
| **Hermes** | `ghe:reporter` | `../../../../assets/avatars/hermes.png` |
| **Chronos** | `ghe:ci-issue-opener` | `../../../../assets/avatars/chronos.png` |
| **Cerberus** | `ghe:pr-checker` | `../../../../assets/avatars/cerberus.png` |

## Comment Template

```markdown
<img src="AVATAR_URL" width="77" align="left"/>

**NAME said:**
<br><br>

CONTENT_HERE
```

**Note:** Only add `---` separator if the message includes file links, citations, or references that need to be visually separated from the main text.

## Template Variables

- `AVATAR_URL`: The avatar URL from the table above
- `NAME`: The display name (e.g., "Emasoft", "Claude", "Hephaestus", "Artemis")
- `CONTENT_HERE`: The message content (only use `>` when quoting someone else, not for direct text)

## Example: User Message

```markdown
<img src="https://avatars.githubusercontent.com/u/713559?v=4&s=77" width="77" align="left"/>

**Emasoft said:**
<br><br>

This is the user's direct message text.
No quote marks needed for direct text.

Use `>` quote marks only when actually quoting someone else.
```

## Example: Agent Response

```markdown
<img src="../../../../assets/avatars/claude.png" width="77" align="left"/>

**Claude (Orchestrator) said:**
<br><br>

Response content here.

**Actions taken:**
- Action 1
- Action 2
```

## Example: Message with References

```markdown
<img src="../../../../assets/avatars/claude.png" width="77" align="left"/>

**Claude (Orchestrator) said:**
<br><br>

Here is my analysis of the issue.

---

**Files modified:**
- `src/main.py`
- `tests/test_main.py`

**References:**
- Issue #42
- PR #15
```

## Important Notes

1. **Empty line after avatar**: Always leave an empty line after the `<img>` tag
2. **`<br><br>` after name**: Always add double `<br><br>` after "**Name said:**" for proper spacing
3. **Separator**: Only use `---` when message has file links, citations, or references to separate
4. **Avatar size**: Always use `width="77"` for consistency
5. **Alignment**: Always use `align="left"` for the avatar

## Usage by Agents

When posting to issue threads, agents should:

1. Read this template
2. Replace variables with actual values
3. Use `gh issue comment NUMBER --body "..."` to post
