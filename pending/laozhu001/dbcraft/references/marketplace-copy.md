# DB Craft Marketplace Copy

## One-Line Intro

DB Craft is a visual schema design workspace that helps users move from table ideas to exportable SQL faster.

## Short Marketplace Description

Design database tables visually, validate structure, save reusable models, and export SQL for MySQL, PostgreSQL, SQLite, and MSSQL.

## Full Marketplace Description

DB Craft is a visual database modeling skill for users who want a faster and clearer workflow than writing schema notes by hand. It opens a local schema studio where users can create or edit tables, shape relationships, import `CREATE TABLE` scripts, generate tables with AI, validate the design, and export SQL when the model is ready.

DB Craft is especially useful when a user wants to:

- sketch a schema before implementation
- evolve an existing model over time
- turn screenshots, requirements, or plain-language ideas into structured tables
- keep model files and SQL exports together in one workspace
- hand off clean schema artifacts to a migration or deployment workflow

## Key Selling Points

- Visual schema design instead of manual note-taking
- Supports `MySQL 8`, `PostgreSQL 14`, `SQLite`, and `MSSQL`
- AI-assisted table generation from natural language
- Import from existing `CREATE TABLE` SQL
- Save reusable `*.dbmodel.json` models
- Export SQL for downstream engineering workflows
- Clean handoff boundary between design and deployment

## Installation And Prerequisites

- Current public package supports `Windows` only
- Requires local `Node.js`
- Launches a local DB Craft service and opens it in the browser
- Reuses an existing local service when already running
- If the local service is not running, the skill starts it automatically before opening the page
- If startup fails, the user should see a clear blocker instead of a blank page

## Data And Security Notes

- DB Craft is a local tool, not a hosted SaaS product
- Model files, SQL exports, and Codex handoff files are written into the active local workspace
- AI Build may send prompts to the user-configured model provider
- Users should use their own API keys and treat them as sensitive credentials
- Public positioning should avoid implying silent cloud sync or automatic live database execution

## Best For

- backend engineers designing new tables
- full-stack developers aligning schema and UI work
- technical leads reviewing table structure before implementation
- analysts or product-minded builders who think better visually

## Positioning Notes

- DB Craft is a design-to-SQL skill, not a database execution skill.
- It should be presented as a modeling workspace that can hand off to migration or deployment workflows when needed.
- For public marketplace positioning, avoid implying that it automatically executes schema changes against a live database.
