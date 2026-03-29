# Doc-Verified Notes

This skill is anchored to Xi Xu's article from December 2, 2025:

- [Run Claude Code Cheaply: A Complete Guide to Using LiteLLM with the GitHub Copilot Chat API](https://blog.xi-xu.me/en/2025/12/02/Run-Claude-Code-Cheaply-With-LiteLLM-And-GitHub-Copilot.html)

It is also tightened against current LiteLLM documentation retrieved during package creation:

- LiteLLM GitHub Copilot provider docs, version `v1.81.9-stable`

## Safe Carryovers From The Article

These parts of the article match the current provider model closely enough to keep as the skill's default narrative:

- Claude Code can be pointed at a local LiteLLM endpoint through `ANTHROPIC_BASE_URL`
- Claude Code still expects a non-empty local Anthropic auth token value even though LiteLLM forwards to Copilot instead
- LiteLLM acts as the middle layer between Claude Code and the GitHub Copilot API
- `drop_params: true` remains an important compatibility setting for Anthropic-shaped requests
- the first working request can trigger GitHub device authorization
- verification should be done by watching LiteLLM logs while sending a small Claude Code request

## Doc-Verified Deltas

### Provider naming

The current LiteLLM provider route uses this pattern:

```text
github_copilot/<model>
```

That is the stable rule the skill should teach. The article's example `github_copilot/claude-opus-4.5` still fits this pattern.

### Exact model-name matching

The `ANTHROPIC_MODEL` value in Claude Code must match LiteLLM `model_name` exactly. Treat this as a first-line troubleshooting rule, not a footnote.

### `drop_params: true`

Keep this in the default config examples. It strips Anthropic-specific request fields before forwarding to Copilot and helps avoid avoidable 4xx errors.

### Optional token storage overrides

LiteLLM currently documents these optional environment variables for GitHub Copilot token storage:

- `GITHUB_COPILOT_TOKEN_DIR`
- `GITHUB_COPILOT_ACCESS_TOKEN_FILE`

Only mention them when the user needs custom storage paths or auth troubleshooting. They are not part of the minimum happy path.

### Header overrides are advanced fallback, not default

The article explicitly adds editor-style headers. Current LiteLLM docs also document header override support, but the provider itself is now clearly modeled as `github_copilot/...`.

For this skill, treat explicit `extra_headers` as an advanced fallback when:

- the user already has evidence that header shape matters in their environment
- the basic provider route is reaching Copilot but still needs client emulation tweaks

Do not present custom headers as universally required for the first setup attempt.

## Guidance For Future Revisions

- Preserve the article's user-facing flow because it is clear and practical.
- Prefer current LiteLLM provider mechanics over historical assumptions when they conflict.
- If a user asks for a different Copilot-backed model, keep the `github_copilot/<model>` pattern and avoid claiming that a specific Copilot model is permanently available unless it was re-verified from current docs.
