# DB Craft Usage

## App Path

- Source app directory: `D:\DBdesigner`
- Local server entry: `server.js`
- Default URL: `http://127.0.0.1:3000`

## Supported Databases

- MySQL 8
- PostgreSQL 14
- SQLite
- MSSQL

## Core Tasks

- Create a new model.
- Open an existing model from the workspace directory.
- Add tables manually.
- Modify existing tables and keep the diagram updated.
- Generate tables with AI.
- Build tables from `CREATE TABLE` SQL.
- Check model syntax.
- Auto-layout tables.
- Export SQL.
- Continue adding newly requested tables into the same current model for the same workspace.
- Reflect table edits in the same current model for the same workspace.
- If the user wants the designed tables created in an actual database, continue from modeling into export/handoff instead of stopping at the UI.
- Think of DB Craft as a design-to-SQL workspace: model first, export second, deploy elsewhere.
- When using `交给Codex`, DB Craft now writes a project handoff file named `dbcraft-codex-handoff.md` in the active project directory.

## Open Behavior

- When opening DB Craft, first check whether `http://127.0.0.1:3000` is already available.
- If it is available, reuse the existing local service and open the page directly.
- If it is unavailable, start the local service first and then open the page.
- Tell the user which case happened so they know whether DB Craft was reused or freshly started.
- After opening, remind the user that model files are saved in the active project directory.
- If `dbcraft-codex-handoff.md` exists in that project directory, Codex can continue from it directly.

## Design To Handoff Flow

1. Open DB Craft in the current workspace.
2. Update or add the requested tables in the current model.
3. Save the `*.dbmodel.json` model in the workspace so the diagram reflects the latest create/update changes.
4. Export SQL or generate schema SQL from the model into the same workspace.
5. Hand off the saved model and SQL to a separate migration/deployment workflow when actual database execution is needed.

## Important Menu Paths

- `File -> New (MySQL 8 / PostgreSQL 14 / SQLite / MSSQL)`
- `File -> Open`
- `File -> Save`
- `Model -> Add Table`
- `Model -> AI Build Table`
- `Model -> Build from SQL Script`
- `Model -> Syntax Check`
- `Model -> Auto Layout`
- `Model -> Export SQL`
- `Settings -> Set Workspace`
- `Settings -> Set Workspace Path Note`
- `Settings -> AI Config`

## Useful Shortcuts

- `Ctrl+O`: Open model
- `Ctrl+S`: Save model
- `Ctrl+Shift+S`: Save as
- `Ctrl+Alt+1`: New MySQL 8 model
- `Ctrl+Alt+2`: New PostgreSQL 14 model
- `Ctrl+Alt+3`: New SQLite model
- `Ctrl+Alt+4`: New MSSQL model
- `Ctrl+Alt+E`: Export SQL
- `Alt+A`: Add table
- `Alt+L`: AI table generation
- `Alt+J`: Build from SQL script
- `Alt+Q`: Syntax check
- `Alt+R`: Auto-layout tables
- `Alt+T`: Template table
- `Alt+K`: AI config
- `Alt+W`: Set workspace

## AI Notes

- Preferred key source: saved key in `Settings -> AI Config`
- Fallback key source: server env var `OPENAI_API_KEY`
- The app now provides built-in mainstream model presets for database design, including OpenAI, Kimi, DeepSeek, and Qwen options.
- You can either select a preset or type a custom model name manually.
- Compatible Base URL is auto-inferred for Kimi / DeepSeek / Qwen when no custom Base URL is filled.
- The local `server.js` uses OpenAI `responses` for OpenAI-hosted models and OpenAI-compatible `chat/completions` for third-party compatible providers.
- AI-built tables also append the active global template fields by default, just like SQL script import does.
- If no API key is available, use the built-in `AI建表 -> 交给Codex生成` fallback so the requirement can still be handed to Codex in a ready-to-send format.

## Browser Notes

- Prefer checking and reusing the running local service before starting a new one.
- The workspace flow uses browser directory access when the local bridge is unavailable. Prefer current Chrome or Edge.
- When launched through the skill, DB Craft will prefill the current shell directory as the workspace path hint. Browser directory permission may still require one manual selection.
- When opening DB Craft for the user, remind them that the model files should be kept in the active workspace directory.
- If the page asks for directory permission, let the user complete that browser prompt.
- If SQL export fails because directory access is unavailable, use the app's export flow again after granting permission.
- Model state is browser-session local until saved. If one browser window cannot see a newly created table from another window, save the model as `*.dbmodel.json` and open that file in the target window.
- When the user asks for multiple tables for the same workspace across several turns or conversations, keep appending them into the current workspace model instead of starting a fresh model each time unless the user explicitly asks for a new one.
- When the user edits existing tables across multiple conversations in the same workspace, keep applying those changes back into the same model so the diagram remains the source of truth.
- Template tables may inject default fields such as `Field1`. Keep them by default unless the user explicitly asks to remove them.
