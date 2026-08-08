---
name: gemdesign-skill
description: Generate, save, and modify GemDesign prototype pages via CLI. Invoke when user wants to create UI prototypes, design pages, or batch-generate pages from requirements.
version: 0.1.1
license: MIT
compatibility: [claude, codex, cursor, trae, hermes, openclaw, qoder, opencode , workbuddy, qclaw]
---

# GemDesign Prototyping

Use the `gemdesign` CLI to create, save, and modify high-fidelity prototype pages on the GemDesign platform. You generate HTML following the GemDesign Page Spec, validate it, then save via CLI.

## When to Invoke

- User wants to create a UI prototype or design a page
- User has a requirements document and wants batch page generation
- User wants to modify an existing GemDesign page
- User wants to view existing GemDesign pages

## Prerequisites

> **CRITICAL: The following steps MUST be executed strictly in order. Each step MUST fully complete before proceeding to the next. Do NOT skip, parallelize, or advance until the current step is confirmed successful.**

### Step 1: Verify & Install GemDesign CLI (MUST complete before Step 2)

**ALWAYS verify CLI installation and version first** before doing any other work. This step is a hard gate — no other operations (`auth`, `app`, `page`, `style`, etc.) may run until this step is confirmed complete.

1. **Check if CLI is installed**:
   ```bash
   npm list -g @gemdesign-ai/cli
   ```
   - If the command returns version info (e.g., `@gemdesign-ai/cli@1.2.3`), CLI is installed - proceed to step 2.
   - If the command returns empty or error (e.g., `(empty)` or `ERR!`), CLI is NOT installed. Run:
     ```bash
     npm install -g @gemdesign-ai/cli
     ```
     Wait for the installation to finish, then re-verify with `npm list -g @gemdesign-ai/cli`. Do NOT proceed until re-verification confirms the installed version.

2. **Check if CLI is latest version** (only after step 1 confirms CLI is installed):
   ```bash
   npm outdated -g @gemdesign-ai/cli
   ```
   - If the command returns empty or shows `Current=Latest`, CLI is up-to-date - this step is complete, proceed to Step 2.
   - If the command shows version info with different `Current` and `Latest` values, CLI is outdated. Update to latest:
     ```bash
     npm update -g @gemdesign-ai/cli
     ```
     Wait for the update to finish, then re-verify with `npm outdated -g @gemdesign-ai/cli`. Do NOT proceed until re-verification confirms the CLI is up-to-date.

After this step is confirmed complete, the `gemdesign-ai` command is available globally at the latest version. **Only then** may you advance to Step 2.

### Step 2: Verify Login (MUST complete after Step 1, before Step 3)

**ALWAYS verify login status** after Step 1 is complete. Run this command:
```bash
gemdesign auth whoami
```
- If it succeeds (returns user info), the user is logged in — proceed to Step 3.
- If it fails (returns an error like "token 无效" or "未提供 token"), the user is NOT authenticated. You MUST:
  1. Tell the user: if they don't have an account or token yet, go to **https://design.gemcoder.com** to register an account and get an API token. The token retrieval path is: log in to the platform -> click **个人中心** (Personal Center) -> get the **MCP 令牌** (MCP token).
  2. Ask the user for their API token (use `AskUserQuestion` tool to prompt the user to input their token).
  3. Once the user provides their token, **automatically run** the login command for them:
     ```bash
     gemdesign auth login --token <user_provided_token>
     ```
  4. Re-verify with `gemdesign auth whoami` to confirm login succeeded.
  5. If login still fails, repeat from step 2 (ask the user to provide their token again).
  6. Only proceed to Step 3 after login is confirmed.

**HARD GATE**: Until login is confirmed via `gemdesign auth whoami`, you MUST NOT perform ANY page-generation work — this includes CLI commands (`app`, `page`, `style`, `validate`) AND local file operations (writing `.html`, creating `.stream.lock`, streaming write, creating the `./output/` directory). Local HTML generation is NOT a workaround for the login gate; a page can only be saved to the platform by an authenticated user, so generating it before login is wasted work. If login fails, stop and resolve authentication first — do not start writing any HTML.

### Step 3: Start the Local Server (MUST complete after Step 2, before any page generation)

> **CRITICAL - HARD GATE: You MUST open the browser in this step.** This is NON-NEGOTIABLE and MUST NOT be skipped, deferred, or treated as optional. Generating any page before the browser is open is a SERIOUS VIOLATION - the user needs the real-time preview surface to see pages as they are generated. You MUST actively open the browser yourself using your platform's built-in browser/preview tool (see step 3 below for the fallback strategy). Do NOT just output a URL in chat text and wait for the user to click it — you MUST programmatically open the browser.

After Step 1 (CLI installed) and Step 2 (Login verified) are both confirmed complete, start the local server for real-time streaming preview.

The local server provides real-time streaming preview of HTML pages as they are being generated. The server is built into the CLI and managed via the `gemdesign server` commands. The server runs on port `4056` by default; if that port is occupied it auto-retries the next available port (up to `4066`).

1. **Start the local server** using the CLI command:

   > **CRITICAL — If Step 1 updated the CLI, stop the old server first.** If you ran `npm update -g @gemdesign-ai/cli` in Step 1, any previously running server is still using the OLD CLI code. You MUST stop it before starting a new one, otherwise the new server code will not be loaded:
   > ```bash
   > gemdesign server stop
   > ```
   > - If it returns `{"success":true,"message":"本地服务已停止"}`, the old server has been stopped — continue to start a fresh server below.
   > - If it returns an error like `{"success":false,"error":"未发现运行中的本地服务"}`, no server was running — ignore this error and continue.
   > - **If Step 1 did NOT update the CLI** (CLI was already up-to-date), skip the stop command and let `server start` reuse the existing running server (if any).

   ```bash
   gemdesign server start
   ```
   - If a server is already running, the command will detect it and return the existing port — no duplicate server will be started.
   - If the server starts successfully, the command returns JSON: `{"success":true,"port":<port>,"url":"http://localhost:<port>"}`
   - If the server fails to start, the command returns JSON with an error: `{"success":false,"error":"<error message>"}`
   - **On error**: Read the error message carefully. Common errors:
     - `"服务文件不存在"`: The CLI installation is incomplete — reinstall the CLI.
     - `"服务启动失败，进程已退出"`: Possible port conflict or config file error — check `~/.gemdesign/config.json`.
   - Record the `<port>` from the success response for subsequent steps.

2. **Check server status** (optional, for debugging):
   ```bash
   gemdesign server status
   ```
   Returns: `{"success":true,"status":"running","port":<port>,"url":"http://localhost:<port>"}` or `{"success":true,"status":"stopped"}`

3. **Open the preview (MANDATORY — HARD GATE, DO NOT SKIP)**: After the server is confirmed running (the `server start` command returned success), you MUST open the browser and navigate to the service page named **GemDesign设计器** (URL: `http://localhost:<port>` - use the port from the `server start` response).

   > **This step is NON-NEGOTIABLE.** Do NOT proceed to any page generation workflow (Workflow A/B/C) until the browser is open at `http://localhost:<port>`. The server being up is NOT the same as the preview being open - the user must SEE the preview surface in the browser.
   >
   > **DO NOT just output a URL in chat text.** You MUST use a tool to actually open the browser. Outputting something like "服务器启动成功！请在浏览器中打开 http://localhost:4056" is a VIOLATION — the browser must be opened programmatically, not by asking the user to click a link.

   **How to open the browser — use the following methods in priority order:**

   Try the following methods in priority order. Use the FIRST one that is available and succeeds. If a method fails, skip it and try the next:

   | Priority | Method | How to use |
   |----------|--------|------------|
   | 1 | **Your platform's built-in browser/preview tool** | **You MUST check what browser/preview tools are available on your current agent platform and use the most appropriate one.** Different platforms provide different built-in tools — use whichever one your platform offers. Examples of platform-specific tools: Trae provides `OpenPreview` and the `integrated_browser` MCP's `browser_navigate`; Cursor provides its own preview mechanism; other platforms may have equivalent tools. **The key requirement is: you MUST use a tool to programmatically open the browser, not just output a URL in chat.** Navigate to `http://localhost:<port>/` using the tool. |
   | 2 | **OS default browser command** | If no built-in browser/preview tool is available (or it failed), open the default browser via OS command: Windows `start http://localhost:<port>/`, macOS `open http://localhost:<port>/`, Linux `xdg-open http://localhost:<port>/`. |
   | 3 | **Tell the user to open the URL** | If ALL above methods fail or are unavailable, as a **last resort**, clearly tell the user: "请在浏览器中打开 http://localhost:<port>/ 查看设计器预览" and wait for the user to confirm before proceeding. |

   **How to find your platform's built-in tool:** Check your available tools list — look for tools with names like `OpenPreview`, `browser_navigate`, `preview`, `browser`, or similar. Any tool that can open a URL in a browser panel qualifies. Use it with the URL `http://localhost:<port>/`.

   **Ensuring success:**
   - If the highest-priority method returned an error or you're unsure whether it succeeded, immediately fall back to the next method in the table.
   - After opening the browser, verify the server is still accessible by re-checking the debug endpoint (`http://localhost:<port>/api/local/stream/debug` returns 200).
   - Only proceed to page generation after you have made a best-effort attempt to open the browser using at least one available method.
   >
   > After the preview is open, you may proceed to page generation workflows.

   > **CRITICAL - The browser is opened EXACTLY ONCE, only here in Step 3.** Once the browser is open at `http://localhost:<port>` (the designer SPA root), you MUST NEVER open the browser again — not during page generation (Workflows A/B/C), not during modification flows, not to "refresh" or "show" a generated page. The designer SPA stays open for the entire session; generated HTML is loaded into an iframe INSIDE the designer via SSE (see "Streaming Write Workflow"), NOT by navigating the browser to a new URL.
   >
   > Opening the browser again will navigate it away from the designer to whatever URL you passed — this OVERWRITES the designer with the generated HTML (or a 404), destroying the preview surface the user needs. The URL used to open the browser MUST ALWAYS be the designer root URL `http://localhost:<port>/` — NEVER a path to a generated `.html` file (e.g. `http://localhost:<port>/output/<projectDir>/<pageuuid>.html`), NEVER a page-specific URL. Generated pages have no direct browser URL; they are only viewable through the designer's iframe via SSE.

## CLI Command Reference

### Server Management
```bash
gemdesign server start [--port <port>]   # 启动本地设计器服务（默认端口 4056）
gemdesign server stop                    # 停止本地设计器服务
gemdesign server status                  # 查看服务运行状态
```
> **server start** starts the local server as a background process. If a server is already running, it returns the existing port. On success, returns JSON with `port` and `url`. On failure, returns JSON with `error` message — read it carefully to diagnose and fix the issue before retrying.
> **server stop** stops the running server. On Windows, uses `taskkill` to terminate the process tree. Returns error if no server is running or if the process cannot be terminated.
> **server status** returns the current status (`running` or `stopped`), port, and URL if running.

### Authentication
```bash
gemdesign auth login --token <token>   # Configure API token
gemdesign auth whoami                  # Verify identity
```

### App Management
```bash
gemdesign app create --name "MyApp" [--type web|app]    # Create new app, --type defaults to web
gemdesign app list                     # List all apps
gemdesign app info [--appuuid <id>]    # App details
gemdesign app use --appuuid <id>       # Switch current default app
```
> **appuuid priority**: `--appuuid` flag > `defaultAppUuid` (set by `app create`/`app use`) > `GEMDESIGN_APPUUID` env
> Once you run `app create` or `app use`, subsequent `page` commands don't need `--appuuid`.
> **IMPORTANT**: Always check `gemdesign app list` BEFORE creating a new app. Reuse existing apps to keep all pages in the same project folder. Only create a new app when the user explicitly asks for one.
> **CRITICAL - Never create duplicate apps**: Never call `gemdesign app create` more than once in a single session/task. If you have already run `app create` in this session, you MUST NOT run it again — even if a later workflow step or retry seems to require app setup. Instead, reuse the existing app by running `gemdesign app list` to find it, then `gemdesign app use --appuuid <id>`. Creating a second app leaves the first one empty and orphaned on the platform.
> **IMPORTANT - Output app info to user**: After selecting/switching/creating an app (i.e., after any `app create`, `app use`, or `app info` call that establishes the working app), you MUST clearly tell the user in your text response which app is now the active target for page generation. At minimum, output the **app name** and **appuuid** (and ideally the computed `<projectDir>`). This ensures the user always knows which app pages will be generated/modified in, and can interrupt if the wrong app was picked. See the "Output current app info to user" step in each workflow for the exact format.
> **CRITICAL - App type determines page type**: Apps have a type - `web` (桌面端) or `app` (移动端) - returned by `app info` as the `pageScene` field. **When generating new pages, the page type MUST match the app type**: a `web` app can only contain `web` pages (desktop layout, wide screen), and an `app` app can only contain `app` pages (mobile layout, narrow screen). Before generating any HTML, check the app's `pageScene` from `app info` and design the page accordingly. Do NOT generate a desktop-width page for an `app` type app, or a mobile-width page for a `web` type app.

### Style Search (optional helper)
```bash
gemdesign style search --keywords "科技,深蓝,企业" --limit 5   # Search styles
gemdesign style get --id <styleId> --format html                 # Get full style
```
> Style search is optional. You can also design styles yourself or use other UI design skills.

### Page - View
```bash
gemdesign page list [--appuuid <id>]                                        # List pages
gemdesign page get --pageuuid <id> --file ./output/<projectDir>/<id>.html  # Get page HTML (auto-creates projectDir)
gemdesign page doc get --pageuuid <id> --file ./output/<projectDir>/<id>.md  # Get requirement doc
```

### Page - Save (with validation)
```bash
gemdesign page save --pageuuid <id> --file ./output/<projectDir>/<id>.html                                         # Update existing
gemdesign page save --new --pageuuid <readable-id> --name "Login" --file ./output/<projectDir>/<readable-id>.html  # Create new
gemdesign page doc save --pageuuid <id> --file ./doc.md                                                           # Save requirement doc
```
> `page save` automatically validates the HTML against the GemDesign Page Spec before uploading.
> `page doc save` saves an agent-generated requirement document to the platform.
> **`--pageuuid` for `--new`**: Use a human-readable id (e.g. filename without `.html`). Ensure uniqueness within the app. This id is used directly as `data-uuid` in navigation elements - no need to change them after saving.
> **Project subdirectory**: Always use `./output/<projectDir>/` in paths. The CLI is idempotent - if the path already contains `<projectDir>`, it won't duplicate it. See "Local File Management" for details.

### Validate Only
```bash
gemdesign validate --file ./page.html    # Validate without saving
```

### Local File Management

For every page, save HTML files locally under `./output/`, organized by project subdirectory:

| File | Purpose | How to generate |
|------|---------|-----------------|
| `./output/<projectDir>/<pageuuid>.html` | **Page HTML** (contains DSL, for editing and saving) | The file you generate and write |

> **Project subdirectory naming**: `<projectDir> = {projectName}__{appuuid}`
> - `projectName` comes from `app info` (illegal filesystem chars `\/:*?"<>|` removed, whitespace collapsed to `_`)
> - Empty `projectName` falls back to `默认项目`; empty `appuuid` falls back to `local`
> - Examples: `CRM系统__abc-123`, `电商App__9f3e`, `默认项目__local`
>
> **How to write files**:
> - **Always use `./output/<projectDir>/<pageuuid>.html`** in all file paths, whether writing files directly or passing to CLI commands.
> - The CLI is **idempotent**: if the path already contains `<projectDir>`, it will NOT duplicate it. You can safely pass `./output/CRM系统__abc-123/home.html` to `page get --file` or `page save --file` without worrying about nesting.
> - **Compute `<projectDir>` first**: Run `gemdesign app info` -> get `{appuuid}` and `{projectName}` -> compute `<projectDir> = {projectName}__{appuuid}` (sanitize projectName).
> - **Validate `<projectDir>` before creating files**: Ensure `<projectDir>` is non-empty and matches `{nonEmptyName}__{nonEmptyUuid}`. If `projectName` or `appuuid` is empty/undefined, re-run `gemdesign app info`. Never create files with an empty or partial `<projectDir>` (e.g. `__abc` or `MyApp__`) - this creates orphaned unnamed directories.
>
> The local server automatically serves pages from the project subdirectory path.

## Streaming Write Workflow (Real-time Display)

When generating HTML pages, use the **streaming write workflow** to enable real-time display in the browser. The GemDesign local server watches for file changes and pushes incremental content to the browser via Server-Sent Events (SSE).

> **CRITICAL — Do NOT open the browser again during streaming write (or at any point after Step 3).** The designer SPA (already open in the browser from Step 3) watches for `.stream.lock` and `.html` file changes and auto-loads the generated HTML into its inner iframe via SSE. You do NOT need to "open" or "refresh" anything — just write the files and the designer updates itself in real time. Navigating the browser to the generated `.html` URL (e.g. via a preview tool or OS browser command with a page-specific URL) will OVERWRITE the designer with the generated HTML and break the preview surface. The only valid URL for opening the browser is the designer root `http://localhost:<port>/`, and even that should NOT be re-used after Step 3.

### How It Works

The local server watches `.stream.lock` files and `.html` files:
1. **Create `.stream.lock`** → browser enters streaming mode for that page
2. **Append to `.html`** → browser receives incremental HTML and re-renders
3. **Delete `.stream.lock`** → browser fetches the complete HTML and switches to final render

### Steps

For each page you generate, follow this workflow instead of writing the complete HTML in one shot:

1. **Compute paths**:
   - `htmlPath = ./output/<projectDir>/<pageuuid>.html`
   - `lockPath = ./output/<projectDir>/<pageuuid>.stream.lock`

2. **Create the stream lock file** (signals browser to enter streaming mode AND triggers designer to switch to this project):
   ```bash
   # Windows PowerShell:
   Set-Content -Path "./output/<projectDir>/<pageuuid>.stream.lock" -Value '{"pageUuid":"<pageuuid>","startTime":"<iso-timestamp>"}'
   # macOS/Linux:
   echo '{"pageUuid":"<pageuuid>","startTime":"<iso-timestamp>"}' > ./output/<projectDir>/<pageuuid>.stream.lock
   ```
   Wait ~300ms for the browser to subscribe to the SSE channel.
   
   > **CRITICAL - Designer auto-switches project**: When the `.stream.lock` file is created, the local server pushes a `switch` event via the `project:list` SSE channel. The designer SPA (already open in the browser) receives this event and automatically switches to the project being generated (matching by `appuuid` extracted from the `<projectDir>` path). This ensures the designer's SSE subscriptions (`page:list:<appuuid>` and `page:stream:<pageUuid>`) are aligned with the project whose page is being generated. **No manual action is needed** - the switch happens automatically as part of creating the stream lock. If this is the first page being generated for a different project than what the designer currently shows, allow ~1-2 seconds for the designer to complete the project switch (destroy old canvas, reinitialize, re-subscribe SSE) before writing HTML content.

3. **Write the HTML file** (append-only after the first write, NEVER overwrite with shorter content):
   - You may write the HTML in one shot or in multiple appends — the stream poller detects file changes every 10ms and pushes each append to the browser in real-time.
   - The HTML must be a complete document: `<!DOCTYPE html>` + `<head>` (with all dependencies and styles) + `<body>...</body>` + `</html>`.
   - If writing in multiple appends, ensure the first write includes the `<body>` tag so the browser can start rendering immediately (the browser only renders after `<body>` appears).

   > **CRITICAL RULES**:
   > - Always **append** to the file after the first write. Never overwrite with shorter content during streaming — this triggers a `pageReset` event and forces the browser to re-render from scratch.
   > - If you must rewrite from scratch, delete the `.html` file first, then start over.
   > - The first write creates the file (length goes from 0 to N), subsequent writes append (length goes from N to N+M).
   > - **No delays or chunk-size limits**: Write as fast as you like, in any size. The stream poller pushes every file change to the browser within ~10ms.
   > - **Clean up on failure**: If streaming write fails or is interrupted, delete the `.stream.lock` file and any partial `.html` file for that page. Never leave orphaned lock files - they keep the browser in streaming mode indefinitely. The local server also cleans up orphaned lock files and empty project directories on startup.

4. **Validate the HTML** (while streaming is still active — this ensures the browser stays in streaming mode until validation passes):
   ```bash
   gemdesign validate --file ./output/<projectDir>/<pageuuid>.html
   ```
   If validation fails, fix the HTML and re-validate. The browser continues to show the streaming state, giving immediate feedback on fixes. **Do NOT delete the `.stream.lock` file until validation passes.**

5. **Delete the stream lock file** (only after validation passes — signals browser that streaming is complete):
   ```bash
   # Windows PowerShell:
   Remove-Item "./output/<projectDir>/<pageuuid>.stream.lock"
   # macOS/Linux:
   rm ./output/<projectDir>/<pageuuid>.stream.lock
   ```
   The browser will automatically fetch the complete HTML and switch to the final rendered version.

6. **Save to platform**:
   ```bash
   gemdesign page save --new --pageuuid <pageuuid> --name "<pageName>" --file ./output/<projectDir>/<pageuuid>.html
   ```

### Example (Streaming Write for a "home" page)

```bash
# 1. Create stream lock
Set-Content -Path "./output/MyApp__abc-123/home.stream.lock" -Value '{"pageUuid":"home","startTime":"2026-07-22T10:00:00Z"}'
# Wait ~300ms

# 2. Write the HTML file (one shot or multiple appends — your choice)
#    Use Write tool to create ./output/MyApp__abc-123/home.html with the complete HTML:
#    <!DOCTYPE html><html><head>...<script src="tailwind"></script>...</head><body>...content...</body></html>
#    Or write in multiple appends (ensure first write includes <body> tag).

# 3. Validate (while streaming is still active)
gemdesign validate --file ./output/MyApp__abc-123/home.html
# Fix any validation errors and re-validate before proceeding

# 4. Delete stream lock (only after validation passes)
Remove-Item "./output/MyApp__abc-123/home.stream.lock"

# 5. Save to platform
gemdesign page save --new --pageuuid home --name "首页" --file ./output/MyApp__abc-123/home.html
```

## Workflows

> **PRECONDITION FOR ALL WORKFLOWS**: Step 1 (CLI installed & up-to-date), Step 2 (Login verified via `gemdesign auth whoami`), AND Step 3 (local server running AND browser preview opened) MUST ALL be confirmed complete BEFORE starting any workflow. If login is not confirmed, do NOT generate HTML, do NOT create `./output/` files, do NOT start streaming write - stop and resolve authentication first. If the browser preview is NOT open yet, do NOT start generating any page — go back and complete Step 3 (open the browser) first. This applies to Workflow A, B, and C alike.

### Workflow A: Batch Generation from Requirements

1. **Complete Prerequisites**: Ensure Step 1 (CLI install/update), Step 2 (Login), AND Step 3 (local server running + browser preview opened) are ALL confirmed complete before proceeding. If the browser preview is not open yet, go back to Step 3 and open the browser ONCE to the designer at `http://localhost:<port>`. If the preview is ALREADY open, do NOT open the browser again - the designer stays open and auto-loads generated pages via SSE for the entire session. Never open the browser with a generated-page URL (e.g. `http://localhost:<port>/output/<projectDir>/<pageuuid>.html`) - that overwrites the designer with the generated HTML and destroys the preview surface.
2. **Ensure app exists (reuse first!)**:
   - Run `gemdesign app list` to check existing apps
   - **If apps already exist**: Run `gemdesign app use --appuuid <id>` to set the target app as default. Do NOT create a new app unless the user explicitly asks for a new one.
   - **If no apps exist**: Run `gemdesign app create --name "<AppName>" [--type web|app]` to create one (default type is `web`). **After creating, immediately run `gemdesign app info` to confirm the app exists and record its appuuid. Do NOT run `app create` again for any reason in this session.**
   - **CRITICAL - No duplicate apps**: If you already ran `app create` earlier in this session (even in a previous workflow attempt), do NOT run it again. Reuse the existing app via `app list` + `app use`. Creating a second app leaves the first one empty and orphaned.
   - **CRITICAL**: All pages in the same batch MUST go into the same app. Reusing an existing app prevents pages from being scattered across different project folders.
3. **Get project directory name**: 
   - Run `gemdesign app info` to get `{appuuid}` and `{projectName}`
   - Compute `<projectDir> = {projectName}__{appuuid}` (remove illegal chars `\/:*?"<>|` from projectName, collapse whitespace to `_`)
   - Example: project name "电商 App" with appuuid "abc-123" → `<projectDir> = "电商_App__abc-123"`
4. **Output current app info to user** (CRITICAL — user must know which app pages will be generated into):
   - Before generating any HTML, clearly tell the user in your text response which app you are generating pages into. At minimum, output:
     - **App name** (`projectName` from `app info`)
     - **App UUID** (`appuuid` from `app info`)
     - **App type** (`pageScene` from `app info` - `web` for 桌面端, `app` for 移动端)
     - **Project directory** (`<projectDir>` computed in step 3)
     - **Page count** to be generated in this batch (from step 5 analysis)
   - Example output format:
     ```
     📦 当前应用信息
     - 应用名称：电商 App
     - 应用 ID：abc-123
     - 应用类型：app（移动端）
     - 项目目录：电商_App__abc-123
     - 本次将生成页面数：5
     ```
   - **Type matching**: The `pageScene` value determines the page layout you MUST follow. Generate `web` (desktop, wide-screen) pages for `web` apps, `app` (mobile, narrow-screen) pages for `app` apps. Do NOT mix types - a web app cannot contain app pages, and vice versa.
   - If the user did not explicitly specify an app and you reused an existing app, also tell the user which app was selected (e.g. "已复用现有应用：电商 App") so they can interrupt if it's the wrong one.
   - **Pause-friendly**: This is informational only - no user reply is required unless the user wants to switch apps. Continue to the next step immediately after outputting.
5. **Search style** (optional): `gemdesign style search --keywords "电商,现代,简洁"` → select one → `gemdesign style get --id <id>`
6. **Analyze requirements**: Read the requirements doc, break down into individual pages. Assign each page a readable `pageuuid` (e.g. `home`, `product-list`, `cart`).
7. **Generate design system page (only for newly created apps)**: If a new app was created in step 2 (not reused), generate a design system page as the visual style baseline before generating business pages. All subsequent business pages should follow this style. Determine the design system type based on `pageScene` from `app info`, and generate the page following the type table and page structure in the dedicated **"Design System Page Spec"** section below. The pageuuid is fixed as `design-system` and is NOT counted as a business page. **You MUST save the design system page to the platform (not just write it locally) - otherwise it will not appear in the app and cannot serve as the style baseline.** Use the **Streaming Write Workflow** with these explicit steps (same create-validate-save process as business pages):
   - Create `./output/<projectDir>/design-system.stream.lock` (wait ~300ms for the browser to subscribe to SSE)
   - Write the HTML file to `./output/<projectDir>/design-system.html` (follow the Design System Page Spec; pageuuid is `design-system`)
   - Validate: `gemdesign validate --file ./output/<projectDir>/design-system.html` (fix errors and re-validate; do NOT delete `.stream.lock` until validation passes)
   - Delete `./output/<projectDir>/design-system.stream.lock` (only after validation passes)
   - **Save to platform (MANDATORY - do NOT skip)**: `gemdesign page save --new --pageuuid design-system --name "设计系统" --file ./output/<projectDir>/design-system.html` (uploads the design system page into the app so it persists on the platform and shows up in `page list`)
   - Verify it was saved: `gemdesign page list` (confirm `design-system` appears in the list)
   If the app was reused (switched via `app use` in step 2), skip this step AND skip step 8.
8. **Design System Review Gate (CRITICAL — only when step 7 generated a design system page)**: Before generating any business page, you MUST apply the **"Design System Review Gate"** rules (see that section below). Evaluate the continue conditions; if none apply, STOP and ask the user for confirmation/feedback on the design system using the format specified in that section. Do not proceed to step 9 until the design system is confirmed by the user or a continue condition is met. If the app was reused (step 7 was skipped), skip this step too.
9. **For each page** (use **Streaming Write Workflow** above for real-time display):
   - Generate HTML following the Page Spec below (incorporate style if available). Use the assigned `pageuuid` as `data-uuid` in navigation elements. All business pages MUST follow the style baseline established (and, if applicable, confirmed) in the design system page.
   - **Use streaming write**: Create `<pageuuid>.stream.lock` → write the HTML file (see "Streaming Write Workflow" section for details). Save HTML locally to: `./output/<projectDir>/<pageuuid>.html` (create the directory if it doesn't exist; use the `<projectDir>` computed in step 3)
   - Validate: `gemdesign validate --file ./output/<projectDir>/<pageuuid>.html`
   - Fix any validation errors, re-validate (**do NOT delete `.stream.lock` until validation passes**)
   - Delete `<pageuuid>.stream.lock` (only after validation passes — signals browser that streaming is complete)
   - Save to platform: `gemdesign page save --new --pageuuid <pageuuid> --name "页面名" --file ./output/<projectDir>/<pageuuid>.html`
     (uploads to platform)
10. **Verify**: `gemdesign page list`

### Workflow B: Conversational Generation

When user asks for a page in conversation:
1. **Complete Prerequisites**: Ensure Step 1 (CLI install/update), Step 2 (Login), AND Step 3 (local server running + browser preview opened) are ALL confirmed complete before proceeding. If the browser preview is not open yet, go back to Step 3 and open the browser ONCE to the designer at `http://localhost:<port>`. If the preview is ALREADY open, do NOT open the browser again - the designer stays open and auto-loads generated pages via SSE for the entire session. Never open the browser with a generated-page URL (e.g. `http://localhost:<port>/output/<projectDir>/<pageuuid>.html`) - that overwrites the designer with the generated HTML and destroys the preview surface.
2. **Ensure app exists (reuse first!)**:
   - Run `gemdesign app list` to check existing apps
   - **If apps already exist**: Run `gemdesign app use --appuuid <id>` to set the target app as default. Do NOT create a new app unless the user explicitly asks for a new one.
   - **If no apps exist**: Run `gemdesign app create --name "<AppName>" [--type web|app]` to create one (default type is `web`). **After creating, immediately run `gemdesign app info` to confirm the app exists and record its appuuid. Do NOT run `app create` again for any reason in this session.**
   - **CRITICAL - No duplicate apps**: If you already ran `app create` earlier in this session (even in a previous workflow attempt), do NOT run it again. Reuse the existing app via `app list` + `app use`. Creating a second app leaves the first one empty and orphaned.
   - **CRITICAL**: All pages MUST go into the same app. Reusing an existing app prevents pages from being scattered across different project folders.
3. **Get project directory name**: 
   - Run `gemdesign app info` to get `{appuuid}` and `{projectName}`
   - Compute `<projectDir> = {projectName}__{appuuid}` (remove illegal chars `\/:*?"<>|` from projectName, collapse whitespace to `_`)
4. **Output current app info to user** (CRITICAL — user must know which app the page will be generated into):
   - Before generating any HTML, clearly tell the user in your text response which app you are generating the page into. At minimum, output:
     - **App name** (`projectName` from `app info`)
     - **App UUID** (`appuuid` from `app info`)
     - **App type** (`pageScene` from `app info` - `web` for 桌面端, `app` for 移动端)
     - **Project directory** (`<projectDir>` computed in step 3)
   - Example output format:
     ```
     📦 当前应用信息
     - 应用名称：电商 App
     - 应用 ID：abc-123
     - 应用类型：app（移动端）
     - 项目目录：电商_App__abc-123
     ```
   - **Type matching**: The `pageScene` value determines the page layout you MUST follow. Generate `web` (desktop, wide-screen) pages for `web` apps, `app` (mobile, narrow-screen) pages for `app` apps. Do NOT mix types - a web app cannot contain app pages, and vice versa.
   - If the user did not explicitly specify an app and you reused an existing app, also tell the user which app was selected (e.g. "已复用现有应用：电商 App") so they can interrupt if it's the wrong one.
   - **Pause-friendly**: This is informational only — no user reply is required unless the user wants to switch apps. Continue to the next step immediately after outputting.
5. **Generate design system page (only for newly created apps)**: If a new app was created in step 2 (not reused), generate a design system page as the visual style baseline before generating business pages. All subsequent business pages should follow this style. Determine the design system type based on `pageScene` from `app info`, and generate the page following the type table and page structure in the dedicated **"Design System Page Spec"** section below. The pageuuid is fixed as `design-system` and is NOT counted as a business page. **You MUST save the design system page to the platform (not just write it locally) - otherwise it will not appear in the app and cannot serve as the style baseline.** Use the **Streaming Write Workflow** with these explicit steps (same create-validate-save process as business pages):
   - Create `./output/<projectDir>/design-system.stream.lock` (wait ~300ms for the browser to subscribe to SSE)
   - Write the HTML file to `./output/<projectDir>/design-system.html` (follow the Design System Page Spec; pageuuid is `design-system`)
   - Validate: `gemdesign validate --file ./output/<projectDir>/design-system.html` (fix errors and re-validate; do NOT delete `.stream.lock` until validation passes)
   - Delete `./output/<projectDir>/design-system.stream.lock` (only after validation passes)
   - **Save to platform (MANDATORY - do NOT skip)**: `gemdesign page save --new --pageuuid design-system --name "设计系统" --file ./output/<projectDir>/design-system.html` (uploads the design system page into the app so it persists on the platform and shows up in `page list`)
   - Verify it was saved: `gemdesign page list` (confirm `design-system` appears in the list)
   If the app was reused (switched via `app use` in step 2), skip this step AND skip step 6.
6. **Design System Review Gate (CRITICAL — only when step 5 generated a design system page)**: Apply the **"Design System Review Gate"** rules (see that section below). If no continue condition applies, STOP and ask the user for confirmation/feedback before proceeding. Do not proceed to step 7 until the design system is confirmed or a continue condition is met. If the app was reused (step 5 was skipped), skip this step too.
7. Determine a readable `pageuuid` (e.g. filename without `.html`, unique within the app)
8. Generate HTML following the Page Spec, using `pageuuid` as `data-uuid` in navigation elements. Follow the style baseline established (and, if applicable, confirmed) in the design system page.
9. **Use streaming write** (see "Streaming Write Workflow" section): Create `<pageuuid>.stream.lock` → write the HTML file to `./output/<projectDir>/<pageuuid>.html` (create the directory if it doesn't exist; use the `<projectDir>` computed in step 3)
10. `gemdesign validate --file ./output/<projectDir>/<pageuuid>.html`
11. Fix errors if any, re-validate (**do NOT delete `.stream.lock` until validation passes**)
12. Delete `<pageuuid>.stream.lock` (only after validation passes — signals browser that streaming is complete)
13. `gemdesign page save --new --pageuuid <pageuuid> --name "<pageName>" --file ./output/<projectDir>/<pageuuid>.html`
   (uploads to platform)
14. Describe the result to the user

When user requests modifications:
1. `gemdesign page get --pageuuid <id> --file ./output/<projectDir>/<id>.html` to retrieve HTML+DSL for editing
2. Modify the HTML (adjust DOM, add/remove interaction DSL, update jsHandle)
   - For substantial modifications, use the **Streaming Write Workflow**: create `<id>.stream.lock` → rewrite the HTML (delete the old file first if starting fresh, or append if only adding)
3. `gemdesign validate --file ./output/<projectDir>/<id>.html`
4. Fix errors if any, re-validate (**do NOT delete `.stream.lock` until validation passes**)
5. Delete `<id>.stream.lock` (only after validation passes — signals browser that streaming is complete)
6. `gemdesign page save --pageuuid <id> --file ./output/<projectDir>/<id>.html`
7. If requirement doc needs updating: `gemdesign page doc save --pageuuid <id> --file <updated-doc.md>`

### Workflow C: Modify Existing Page

1. **Complete Prerequisites**: Ensure Step 1 (CLI install/update), Step 2 (Login), AND Step 3 (local server running + browser preview opened) are ALL confirmed complete before proceeding. If the browser preview is not open yet, go back to Step 3 and open the browser ONCE to the designer at `http://localhost:<port>`. If the preview is ALREADY open, do NOT open the browser again - the designer stays open and auto-loads generated pages via SSE for the entire session. Never open the browser with a generated-page URL (e.g. `http://localhost:<port>/output/<projectDir>/<pageuuid>.html`) - that overwrites the designer with the generated HTML and destroys the preview surface.
2. **Get project directory name**: Run `gemdesign app info` → compute `<projectDir> = {projectName}__{appuuid}` (remove illegal chars `\/:*?"<>|` from projectName, collapse whitespace to `_`)
3. **Output current app info to user** (CRITICAL — user must know which app the page being modified belongs to):
   - Before modifying any HTML, clearly tell the user in your text response which app the target page belongs to. At minimum, output:
     - **App name** (`projectName` from `app info`)
     - **App UUID** (`appuuid` from `app info`)
     - **App type** (`pageScene` from `app info` - `web` for 桌面端, `app` for 移动端)
     - **Project directory** (`<projectDir>` computed in step 2)
   - Example output format:
     ```
     📦 当前应用信息
     - 应用名称：电商 App
     - 应用 ID：abc-123
     - 应用类型：app（移动端）
     - 项目目录：电商_App__abc-123
     ```
   - **Type matching**: The `pageScene` value determines the page layout you MUST follow. Generate `web` (desktop, wide-screen) pages for `web` apps, `app` (mobile, narrow-screen) pages for `app` apps. Do NOT mix types - a web app cannot contain app pages, and vice versa.
   - This confirms to the user that the modification will land in the correct app, especially when multiple apps exist. If the user wanted a different app, they can interrupt here to switch via `gemdesign app use`.
   - **Pause-friendly**: This is informational only — no user reply is required unless the user wants to switch apps. Continue to the next step immediately after outputting.
4. `gemdesign page list` -> find the target page
5. `gemdesign page get --pageuuid <id> --file ./output/<projectDir>/<id>.html` -> retrieve HTML+DSL for editing
6. Analyze HTML structure and interactions
7. Modify HTML as needed
   - For substantial modifications, use the **Streaming Write Workflow** (see above): create `<id>.stream.lock` → rewrite the HTML
8. `gemdesign validate --file ./output/<projectDir>/<id>.html`
9. Fix errors if any, re-validate (**do NOT delete `.stream.lock` until validation passes**)
10. Delete `<id>.stream.lock` (only after validation passes — signals browser that streaming is complete)
11. `gemdesign page save --pageuuid <id> --file ./output/<projectDir>/<id>.html`
12. If requirement doc needs updating: `gemdesign page doc save --pageuuid <id> --file <updated-doc.md>`

---

## Design System Page Spec

When the app is newly created, generate a design system page (with pageuuid fixed as `design-system`) before generating business pages, serving as the visual style baseline for the app. All subsequent business pages should follow the colors, border radii, shadows, and component styles established in this design system. The design system page also follows the GemDesign Page Specification (see below), including tech stack rules, CSS rules, Lite-Interaction DSL, etc.

### Type Determination

Determine the design system type based on the `pageScene` field returned by `app info`:

| pageScene | Design System Type | Core Objective |
|-----------|-------------------|----------------|
| `app` | Mobile C-end experience-driven | Create a consumer-facing, experience-and-emotion-driven mobile app UI design system showcase page. Showcase common interaction patterns and visual components of C-end apps, emphasizing content consumption, social interaction, and personalized experience. The entire page is wrapped in a phone frame, simulating a real mobile app interface. |
| `web` | Enterprise admin function-driven | Create a function-driven, enterprise/admin-management-oriented Web UI design system showcase page. Showcase common framework structures, data operations, and form input components of admin systems, emphasizing information density, operational efficiency, and status feedback. The page uses a full-width admin layout, simulating a real admin management system interface. |
| Other | Flexible analysis | Analyze the most suitable design system type based on requirements, and design flexibly using the Header + Design Tokens + Components basic structure. |

### Page Structure — `app` Type (Mobile C-end)

**Header**

- Include system logo/icon, system name (Chinese), and brief description
- Use dark or brand-color background with white text
- Fixed at top or as a page-top banner

**Section 1: Design Tokens**

- **Section title style**: Use a left-side colored border bar (`border-l-4`, using the style's primary color) + large title + tag badge combination
- **Color system**: Use color swatch cards to display primary, secondary, functional, and neutral colors, with Hex values and usage notes
- **Border radius & shadows**: Use physicalized blocks to display shadow effects at different levels, large radius specs (e.g. 16px/24px), soft shadows or diffuse glow

**Section 2: Components**

- **Media Cards**: Image-text cards (large image mode), masonry/waterfall cards, video/live cover containers
- **Social Elements**: User avatars, like/favorite/comment icons (with micro-interaction styles), follow buttons
- **Interactive Containers**: Bottom sheet panels (Bottom Sheet/Drawer), Toast notifications (shown only as style effect displays within containers — do NOT simulate real popup effects fixed in page layout)
- **Navigation**: Immersive top bar (transparent gradient), bottom navigation bar (icon + text, with selected-state animation hints)
- **Empty/Loading**: Loading placeholders (Skeleton), empty-state illustration placeholders

### Page Structure — `web` Type (Enterprise Admin)

**Header**

- Include system logo/icon, system name (Chinese), and brief description
- Use dark or brand-color background with white text
- Fixed at top or as a page-top banner

**Section 1: Design Tokens**

- **Section title style**: Use a left-side colored border bar (`border-l-4`, using the style's primary color) + large title + tag badge combination
- **Color system**: Use color swatch cards to display primary, secondary, functional, and neutral colors, with Hex values and usage notes
- **Typography hierarchy**: Display H1-H4, Body, and Caption level comparisons within cards, with font/size/weight annotations
- **Border radius & shadows**: Use physicalized blocks to display shadow effects at different levels

**Section 2: Components**

- Use grid layout (`grid-cols-1 lg:grid-cols-2/3`) to organize component displays
- **Structure/Shell**: Sidebar nav items (selected/hover), top breadcrumb, Page Header
- **Data Display**: Data tables (header, zebra striping, row hover, pagination), Tab pages, Tags (Tag/Badge), key-value pair lists
- **Form Elements**: Input boxes (Input), dropdown selects (Select), checkboxes/radio buttons (Checkbox/Radio), switches (Switch) — must include default, Hover, Focus, and Error states
- **Actions**: Action buttons (Primary, Secondary, Ghost, Icon Button)
- **Feedback/Overlays**: Global messages (Message), notifications (Notification), dialogs (Modal/Dialog, shown as example displays — do NOT use full-screen modals), loading states (Skeleton/Spinner)

### Page Structure — Other Types

Follow the Header + Design Tokens + Components basic structure, and determine suitable components and visual style based on requirements analysis.

---

## Design System Review Gate (CRITICAL)

> **When the design system page is generated (newly created apps only), you MUST apply this review gate before generating any business page.** This gate does not apply to reused apps (which skip design system generation) or to Workflow C (modify existing page).

### Why this gate exists (first principles)

The design system page is a **high-leverage decision point**. It locks in the colors, typography, shadows, radii, and component styles that every subsequent business page will inherit. Two properties make the moment right after its generation a natural checkpoint:

1. **Asymmetric error cost.** A wrong style decision made here propagates to every business page generated afterward. Correcting it after N pages exist means reworking N pages; correcting it immediately costs one round-trip with the user. The expected cost of skipping the gate grows linearly with page count, while the cost of pausing is constant and tiny.

2. **Information-state flip.** Before generation, the agent can only *infer* the user's visual preference from the requirements doc — an uncertain state. After generation, the user can *see* a concrete proposal rendered in the browser — a certain state. This is the first moment the user possesses actionable information to confirm or redirect. Capturing that signal here yields maximum value: it is the cheapest point in the whole workflow to correct course.

### Decision rule — stop or continue?

After the design system page is generated, validated, and saved, evaluate the **continue conditions** below. The default is **STOP and ask**; you may only continue without asking if at least one continue condition is clearly met.

**Continue conditions** (any ONE is sufficient to skip the pause and proceed directly to business pages):

| # | Condition | Why it's safe to continue |
|---|-----------|---------------------------|
| C1 | The user explicitly specified the visual style in their original request (e.g. specific brand colors, "深蓝科技风", "参考某App的样式", a mood-board, a hex code) | The style direction is already locked by the user — there is no information gap for the gate to close. |
| C2 | The user ran `style search` + `style get` earlier in this session AND the design system page faithfully reflects that selected style | The user pre-signaled their preference through an explicit selection action; the design system is executing that choice, not proposing a new one. |
| C3 | The user explicitly waived the review (e.g. "不用确认，直接全部生成", "全自动跑完", "不要中途停") | The user has voluntarily forfeited the checkpoint. Respect their stated preference. |

**If NO continue condition applies → you MUST stop.** This is the default and the most common case for a freshly created app driven only by a requirements document.

### When you stop — what to present

Do not merely announce "设计系统已生成". Present a **decision-ready summary** so the user can confirm or redirect with minimal effort:

1. **Style decisions made** — primary/secondary colors (with hex), overall direction (e.g. 科技感/温暖/极简), key component treatments (card radius, shadow style, button style). Be concrete, not vague.
2. **Reasoning link** — connect the decisions back to the requirements (e.g. "基于需求文档中'面向年轻人的社交平台'定位，主色选用高饱和的紫色…").
3. **Explicit ask** — use the `AskUserQuestion` tool to structure the choice. Suggested options:
   - "确认，继续生成业务页面"
   - "调整配色方案"
   - "调整整体风格方向"
   - (the user can also type a custom response via "其他")

### After the user responds

- **User confirms** → proceed to business page generation, treating the confirmed design system as the locked style baseline for all pages.
- **User requests adjustments** -> modify the design system page first (edit -> validate -> save), then either re-present (if the change is major/subjective, e.g. a pivot from "科技蓝" to "温暖橙") or proceed (if the change is minor and clearly resolved, e.g. a single hex value tweak). Use judgment here. The "save" step here means re-running `gemdesign page save --pageuuid design-system --file ./output/<projectDir>/design-system.html` (NO `--new` flag - the page already exists on the platform from step 7/5; `--new` would error on duplicate pageuuid). Confirm the update with `gemdesign page list`.
- **Never start business pages** until the design system is either (a) confirmed by the user or (b) covered by a continue condition above.

---

## GemDesign Page Specification

You MUST follow this spec when generating HTML. The `gemdesign validate` command checks all these rules.

### Overview

A GemDesign page = **HTML(DOM) + TailwindCSS(style) + Lite-Interaction DSL(interaction)**.

### Tech Stack Rules

**Allowed**: HTML native tags, TailwindCSS (via `<script>` tag), CSS (`<style>`), Font Awesome, ECharts
**Forbidden**: Any JS framework (Vue/React/jQuery), hand-written DOM JS (except jsHandle), CSS Hack, `vh` unit

### Only Two Types of Scripts Allowed

1. `<script id="interaction-data">` — Lite-Interaction JSON string (interaction logic)
2. `<script id="funcName">function funcName(event){...}</script>` — jsHandle custom function

### Dependencies

```html
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdn.bootcdn.net/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<!-- ECharts (only when using charts): -->
<script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
<!-- ECharts China map (only when using china map): -->
<script src="https://cdn.jsdmirror.com/npm/echarts/map/js/china.js"></script>
```

### Layout Rules

1. Use TailwindCSS for layout component classes.
2. Prefer flexbox layout; Flexbox, padding, and gap are the core tools for interface layout.
3. Block elements can be used for simple elements (text, decorative images), but NOT for layout. All elements default to the `border-box` box model.
4. Fixed elements (sidebars, nav bars) must have explicit height/width; content area needs matching padding.
5. Masks and modals/drawers must be nested. The mask/overlay layer MUST have a semi-transparent background color (e.g. `bg-black/50`), and the inner modal/drawer content container MUST have an opaque background color (e.g. `bg-white`) - a transparent content container is a SERIOUS VIOLATION, as it lets the mask color bleed through.
6. When centering elements, absolutely do NOT use `mx-auto` or `m-auto` - you MUST use flex layout's `justify-center` and `items-center` on the parent element.

### CSS Rules

#### Rule 1: No `vh` unit

Forbidden: the `vh` unit, any Tailwind CSS class containing `vh`, and any class containing `vh` (e.g. `h-[80vh]`).

#### Rule 2: HIGHEST-LEVEL RED LINE - ABSOLUTELY NO Margin

The entire page is ABSOLUTELY FORBIDDEN from using ANY margin! This includes native CSS and ALL Tailwind class names with margin semantics! The model is highly prone to habitually using margin for "icon spacing" and "element top/bottom spacing" - you MUST overcome this habit!

If your output code contains ANY of the following prefixes (positive OR negative), it is a SERIOUS VIOLATION:

- `m-` (e.g. `m-2`, `m-auto`)
- `mt-` (e.g. `mt-4`)
- `mb-` (e.g. `mb-3`, `mb-4`, `mb-6`)
- `ml-` (e.g. `ml-2`)
- `mr-` (e.g. `mr-1`, `mr-2`)
- `mx-` (e.g. `mx-auto`)
- `my-` (e.g. `my-4`)
- `space-x-` / `space-y-` (the underlying implementation is also margin, ABSOLUTELY forbidden)

**Mandatory alternatives - for the scenarios you are most prone to violating**:

- ❌ Violation habit 1 (icon and text spacing): `<i class="fas fa-edit mr-1"></i>编辑`
- ✅ Correct practice 1 (use flex + gap): `<div class="flex items-center gap-1"><i class="fas fa-edit"></i><span>编辑</span></div>`

- ❌ Violation habit 2 (title/paragraph bottom spacing): `<h3 class="mb-4">标题</h3><form>...</form>`
- ✅ Correct practice 2 (parent flex + gap): `<div class="flex flex-col gap-4"><h3>标题</h3><form>...</form></div>`

- ❌ Violation habit 3 (center alignment): `class="mx-auto"` or `class="m-auto"`
- ✅ Correct practice 3 (parent centering): use `flex justify-center items-center` on the parent element

### Lite-Interaction DSL (Core)

All interactions are declared in `<script id="interaction-data">` as a JSON array wrapped in backticks.

```typescript
interface TriggerEvent {
  original: string;        // Selector: #id or .class only
  trigger: 'click' | 'mouseover' | 'mouseenter' | 'mouseleave' | 'mousedown' | 'mouseup';
  actions: Action[];
}

interface Action {
  operation: 'show' | 'hide' | 'openModal' | 'closeModal' | 'addClass' | 'removeClass' | 'openPage' | 'back' | 'openLink' | 'jsHandle';
  target?: string;         // Required for show/hide/addClass/removeClass. #id only, multiple: "#id1,#id2"
  params?: string;         // addClass/removeClass: class names (comma-separated); openPage: pageUuid; openLink: URL. Forbidden for jsHandle. Must be a plain string, no code/variables.
  funcName?: string;       // Only for jsHandle
  operationTitle?: string; // Required for jsHandle/addClass/removeClass (2-8 Chinese chars)
  animation?: string;      // Animation effect name
  animationTime?: number;  // Animation duration in seconds
  delayTime?: number;      // Delay before execution in seconds
}
```

#### Selector Rules (CRITICAL)

| Rule | Detail |
|------|--------|
| `original` and `target` | Only `#id` or `.class` — NO attribute selectors (`[data-xxx]`) |
| `original` | Single element only — no multiple selectors |
| `target` | Multiple IDs allowed: `"#id1,#id2"` — NO `.class` allowed |
| If element only has data attributes | You MUST add an `id` to it, then use `#id` in DSL |

#### Operation Priority

1. `show`/`hide` — preferred for opening/closing modals
2. `addClass`/`removeClass` — CSS changes
3. `openPage` — page navigation (params must be pageUuid string only)
4. `back` — go back
5. `jsHandle` — only when above can't satisfy the requirement

#### jsHandle Rules

1. Each function in its own `<script>` tag
2. Script `id` MUST match function name exactly
3. Only one parameter: `event`
4. No API calls inside

```html
<script id="tabSwitchXxx">
function tabSwitchXxx(event) {
  // full implementation
}
</script>
```

### Page Navigation

For navigation elements, add `id` AND `data-uuid` to the HTML tag. The `data-uuid` value MUST match the `--pageuuid` you pass to `page save --new`:
```html
<!-- If you will save this target page with: page save --new --pageuuid home --name "首页" -->
<a id="nav-home" data-uuid="home" href="javascript:void(0);">首页</a>
```
Do NOT add openPage events in interaction-data for these — they are auto-generated.

### Image Placeholders

Use placeholder URLs, the platform replaces them with real images:
```html
<img src="./api/searchImage?query=premium laptop on white background&width=400&height=400" class="w-full h-full object-cover" />
```

### Button Rules

- ALL buttons must have `type="button"`
- NO `type="submit"`
- Use `href="javascript:void(0);"` for links, never `href="#"`

### Design Constraints

- **Shadows**: Use diffuse shadows: `shadow-[0_8px_30px_rgba(0,0,0,0.04)]`, not short dark shadows
- **Native controls**: No `<select>` or radio buttons for option switching — use capsule segmented controls
- **Horizontal scroll**: Hide scrollbar with `scrollbar-hide`
- **Modals/masks/drawers**: Add `hidden` class by default; use nested structure. The mask/overlay layer MUST have a semi-transparent background color (e.g. `bg-black/50`), and the inner modal/drawer content container MUST have an opaque background color (e.g. `bg-white`). A transparent content container is a SERIOUS VIOLATION - the mask color will bleed through and the popup content area will appear as the mask color. Example:
  ```html
  <div id="modalMask" class="modal-mask hidden fixed inset-0 bg-black/50 flex justify-center items-center z-50">
    <div class="bg-white rounded-lg p-6">
      <!-- Modal content - inner container MUST have bg-white or other opaque color -->
    </div>
  </div>
  ```
- **CSS override**: When status class (like `hidden`) overrides component class, combine in stylesheet: `.modal-mask.hidden { display: none; }` — do NOT use `@apply hidden`

### Script Order

1. TailwindCSS (in `<head>`)
2. ECharts dependency (in `<head>`, optional)
3. `tailwind.config` configuration
4. ECharts config scripts (`<script id="echarts_*" type="echarts">`, optional)
5. jsHandle function scripts (`<script id="funcName">`, optional)
6. **`interaction-data` MUST be the last `<script>` tag**

### Complete Page Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdn.bootcdn.net/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: { primary: '#1890ff' }
        }
      }
    };
  </script>
  <style>
    .modal-mask.hidden { display: none; }
  </style>
</head>
<body>
  <div id="app">
    <!-- Page DOM -->
  </div>

  <!-- jsHandle functions (optional) -->
  <!-- <script id="funcName">function funcName(event) {...}</script> -->

  <!-- Interaction DSL (MUST be last script) -->
  <script id="interaction-data">
`
[
  {
    "original": "#elementId",
    "trigger": "click",
    "actions": [
      { "operation": "show", "target": "#targetId" }
    ]
  }
]
`
  </script>
</body>
</html>
```

## Validation Rules Summary

The `gemdesign validate` command checks:

| # | Rule | What it checks |
|---|------|---------------|
| 1 | interaction_data_exists | `<script id="interaction-data">` present |
| 2 | dsl_json_valid | Content is valid JSON array |
| 3 | selector_exists | All original/target selectors exist in DOM |
| 4 | selector_format | Only #id and .class, no attribute selectors |
| 5 | original_single | original has only one selector |
| 6 | target_no_class | target uses only #id, no .class |
| 7 | jshandle_func_match | Each funcName has matching `<script id="funcName">` |
| 8 | script_id_funcname_match | script id equals function name |
| 9 | button_type | All buttons have type="button", no type="submit" |
| 10 | no_vh | No vh unit in classes or styles |
| 11 | no_hash_href | No href="#" |
| 12 | image_url_format | Placeholder image URLs use `./api/searchImage?query=...&width=...&height=...` with numeric width/height, no spaces around `&` |
| 13 | data_uuid_complete | Tags with data-uuid also have id |
| 14 | interaction_data_last | interaction-data is the last script tag |

## Tips

- Always validate before saving — `gemdesign validate` catches errors early
- For batch generation, validate each page individually before saving
- **Save HTML locally** for every page: `./output/<projectDir>/<pageuuid>.html` for editing and saving to the platform. Always compute `<projectDir> = {projectName}__{appuuid>` first via `gemdesign app info`. The CLI is idempotent - passing a path that already contains `<projectDir>` will not duplicate it.
- When creating a new page, pass a readable `--pageuuid` (e.g. `home`, `login`) - use the same value as `data-uuid` in navigation elements, so you don't need to update them after saving
- Use `gemdesign page get --file <path>` to retrieve editable HTML+DSL before modifying
- The full page spec is available at `page-spec.md` in the CLI project directory