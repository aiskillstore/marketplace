# DB Craft Data And Security Notes

## Product Shape

- DB Craft is a `local visual schema tool`.
- The core modeling experience runs on the user's machine.
- Model files and exported SQL are intended to stay in the user's local project/workspace unless the user explicitly routes data into an AI provider or another workflow.

## What DB Craft Stores Locally

- `*.dbmodel.json` model files
- exported `*.sql` files
- `dbcraft-codex-handoff.md` handoff files when the user chooses `Send to Codex`
- local UI preferences such as language and view settings
- locally saved AI configuration values when the user stores them in the app UI

## Where User Data Usually Lives

- In the active local project/workspace directory
- In the browser's local storage for UI preferences and saved AI configuration
- In the local DB Craft application directory only when sample files or app assets are involved

## AI Requests And Third-Party Providers

- AI table generation may send the user's prompt and schema request to the selected model provider.
- This depends on the model/provider the user configures in `Settings -> AI Config`.
- Supported compatible providers may include:
  - OpenAI
  - Kimi / Moonshot
  - DeepSeek
  - Qwen
- Users should assume that prompts sent through AI Build are transmitted to the configured provider endpoint.

## API Keys

- API keys can be entered through the DB Craft UI.
- These keys should be treated as sensitive credentials.
- Marketplace-facing guidance should recommend that users:
  - use their own keys
  - avoid sharing screenshots that expose keys
  - rotate keys if they suspect accidental exposure

## Send To Codex Flow

- `Send to Codex` writes a local handoff file named `dbcraft-codex-handoff.md` into the current project/workspace.
- This file may contain:
  - model summary
  - project path
  - user request text
  - SQL or schema-oriented handoff notes
- Users should treat this file as project data and manage it according to their own repository or workspace policies.

## What DB Craft Does Not Imply

- It is not a hosted cloud database design service by default.
- It should not be positioned as silently syncing project schema data to a remote server.
- It should not be presented as directly executing schema changes against a live database in the public marketplace version.

## Recommended Marketplace Disclosure

- Tell users clearly that DB Craft is a local tool.
- Tell users clearly that AI Build can send prompts to the configured AI provider.
- Tell users clearly that model files, SQL exports, and Codex handoff files are written locally in the active workspace.

## Recommended User Safety Guidance

- Avoid placing secrets inside schema comments or AI prompts unless necessary.
- Review generated SQL before executing it in any real database workflow.
- Treat `dbcraft-codex-handoff.md` as a human-readable project artifact that may contain requirement details.
