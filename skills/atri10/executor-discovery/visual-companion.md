# Visual Companion Guide

Browser-based companion for showing mockups, diagrams, and visual options
during an Executor discovery phase. It is a tool, not a mode: accepting it
means it is available for the questions that benefit from it, not that every
question goes through the browser.

Session files land inside the initiative's **tracked** thinking store. Read
[safety](../executor/references/safety.md) before putting anything on screen.

## Offering It (just-in-time)

Do **not** offer it upfront. Wait until a question is genuinely clearer shown
than told — a real mockup, layout, or diagram question, not merely a UI
*topic*. The first time that happens, offer it then:

> "This next part might be easier if I show you — I can put together mockups,
> diagrams, and comparisons in a browser tab as we go. It's still new and can
> be token-intensive. Want me to? I'll open it for you."

**The offer MUST be its own message.** Only the offer — no clarifying
question, no summary, no other content — then wait for the answer. Bundling
the offer with a question means the answer covers one of them and you guess
at the other. If they accept, start the server with `--open`. If they decline,
continue text-only and do not offer again unless they raise it.

## When to Use It

Decide **per question**, not per session. The test: *would the user understand
this better by seeing it than reading it?*

**Use the browser** when the content itself is visual:

- **UI mockups** — wireframes, layouts, navigation structures, component designs
- **Architecture diagrams** — system components, data flow, relationship maps
- **Side-by-side visual comparisons** — two layouts, two colour schemes, two design directions
- **Design polish** — look and feel, spacing, visual hierarchy
- **Spatial relationships** — state machines, flowcharts, entity relationships rendered as diagrams

**Use the terminal** when the content is text or tabular:

- **Requirements and scope questions** — "what does X mean?", "which features are in scope?"
- **Conceptual A/B/C choices** — approaches described in words
- **Tradeoff lists** — pros/cons, comparison tables
- **Technical decisions** — API design, data modelling, approach selection
- **Clarifying questions** — anything whose answer is words, not a visual preference

A question *about* a UI topic is not automatically a visual question. "What
kind of wizard do you want?" is conceptual — terminal. "Which of these wizard
layouts feels right?" is visual — browser.

## How It Works

The server watches a directory for HTML files and serves the newest one. You
write HTML to `screen_dir`, the user sees it and can click to select options,
and selections are recorded to `events_file` for you to read on your next
turn.

**Content fragments vs full documents:** if your HTML file starts with
`<!DOCTYPE` or `<html`, the server serves it as-is (injecting only the helper
script). Otherwise it wraps your content in the frame template — header, CSS
theme, connection status, and all interactive infrastructure. **Write content
fragments by default.** Write full documents only when you need complete
control over the page.

## Starting a Session — Executor Paths

Sessions belong to the initiative, at
`docs/executor/INIT-NNNN-<slug>/brainstorm/sessions/<UTC-timestamp>-<topic>/`.
They are **tracked**: the mockups and the options shown are part of the
reasoning record.

`--project-dir` is the **record** directory: the launcher writes `content/`
(the screens shown) and `events` (the choices clicked) directly inside it.
Point it at the session topic directory and the whole reasoning record lands
in the initiative that owns it.

Operational state — `server-info`, `server.log`, `server.pid`, and the
persisted `.last-port` / `.last-token` — is **never** written there. It goes
to a runtime directory outside the repository, keyed by a digest of the
record path so a restart reuses the same port and key and the tab the user
already has open reconnects on its own.

```bash
INIT_DIR=$(../executor/scripts/exec-initiative resolve INIT-0004)
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
SESSION="$INIT_DIR/brainstorm/sessions/$STAMP-layout-options"
mkdir -p "$SESSION"

../executor/scripts/visual-companion/start-server.sh --project-dir "$SESSION" --open

# Returns: {"type":"server-started","port":52341,
#           "url":"http://localhost:52341/?key=…",
#           "screen_dir":".../<STAMP>-layout-options/content",
#           "events_file":".../<STAMP>-layout-options/events",
#           "state_dir":"<os-temp>/executor-visual-companion/<digest>/<pid>-<epoch>"}
```

**Save `screen_dir`, `events_file`, and `state_dir` from the response and use
them verbatim.** Never hand-build `state_dir`: the digest and `<pid>-<epoch>`
segments are generated at launch, and one topic session may produce several
run directories because the server exits after 4 hours idle.

`state_dir` is the argument `stop-server.sh` takes.

**Why the split:** `docs/executor/` is tracked and
[safety](../executor/references/safety.md) declares it public. The session key
is an access token; writing `server-info` or `.last-token` into the initiative
would commit a live credential to a public tree. Content and events carry no
secret and belong in the record.

Do **not** add anything to `.gitignore`. The record files are meant to be
tracked, and nothing secret is written beside them.

**The URL contains a session key (`?key=…`).** The server rejects any request
without it, so always give the user the **complete** URL from the `url` field
— never strip the query string, never hand out a bare `http://host:port`. The
key gates HTTP and WebSocket access so a stray tab or another machine on the
network cannot read the screens or inject events. After the first load the
browser remembers the key via a cookie, so reloads and `/files/*` assets work
without repeating it.

With `--open`, the browser opens itself when you push the first screen — you
do not need to ask the user to open it, but still share the URL as a fallback
(headless and remote setups will not auto-open).

**Finding connection info:** the server writes its startup JSON to
`$STATE_DIR/server-info` in the runtime directory. If you launched it in the
background and did not capture stdout, read that file for the URL and port.

### Launching by platform

**Claude Code:**
```bash
# Default mode works — the script backgrounds the server itself.
../executor/scripts/visual-companion/start-server.sh --project-dir "$SESSION" --open
```

On other runtimes, the default mode works — the script backgrounds the
server itself.

On Windows the script auto-detects and switches to foreground mode (which
blocks the tool call). Run it with the harness's background mechanism so the
server survives across turns, then read `$STATE_DIR/server-info` next turn.

**Codex:**
```bash
# Codex reaps background processes. The script auto-detects CODEX_CI and
# switches to foreground mode. Run it normally — no extra flags needed.
../executor/scripts/visual-companion/start-server.sh --project-dir "$SESSION" --open
```

**Gemini CLI:**
```bash
# Use --foreground and set is_background: true on your shell tool call
# so the process survives across turns.
../executor/scripts/visual-companion/start-server.sh --project-dir "$SESSION" --open --foreground
```

**Copilot CLI:**
```bash
# Start it with Copilot CLI's non-blocking/background shell mechanism so the
# server survives across turns. Keep --foreground so the harness, not the
# script, owns backgrounding. The launcher is a .sh, so invoke it via bash
# (on Windows, call Git Bash's bash.exe from the PowerShell tool).
bash ../executor/scripts/visual-companion/start-server.sh --project-dir "$SESSION" --open --foreground
```

**Other environments:** the server must keep running in the background across
turns. If your environment reaps detached processes, use `--foreground` and
launch it with your platform's background execution mechanism.

If the URL is unreachable from the user's browser (common in remote or
containerised setups), bind a non-loopback host:

```bash
../executor/scripts/visual-companion/start-server.sh \
  --project-dir "$SESSION" \
  --host 0.0.0.0 \
  --url-host localhost
```

`--url-host` controls only the hostname printed in the returned URL JSON.

## The Loop

1. **Check the server is alive**, then **write HTML** to a new file in
   `screen_dir`:
   - **Required: confirm the server is alive before referring to the URL or
     pushing a screen.** Check that `$STATE_DIR/server-info` exists and
     `$STATE_DIR/server-stopped` does not. If it has shut down, restart with
     the **same `--project-dir`** — it reuses the port, so the user's open tab
     reconnects on its own (it shows a "paused" overlay while the server is
     down) and you do not need to send a new URL. Idle timeout is 4 hours,
     configurable with `--idle-timeout-minutes`. A restart creates a new run
     directory: re-read `screen_dir`, `events_file`, and `state_dir` from the new JSON.
   - Use semantic filenames: `platform.html`, `visual-style.html`, `layout.html`
   - **Never reuse filenames** — each screen gets a fresh file
   - Use your file-creation tool — **never `cat`/heredoc** (dumps noise into the terminal)
   - The server serves the newest file automatically

2. **Tell the user what to expect and end your turn:**
   - Remind them of the URL every step, not just the first
   - Give a brief text summary of what is on screen ("Showing 3 layout options for the homepage")
   - Ask them to respond in the terminal: "Take a look and let me know what you think. Click to select an option if you'd like."

3. **On your next turn**, after the user responds:
   - Read `$EVENTS_FILE` if it exists — their browser interactions as JSON lines
   - Merge with their terminal text for the full picture
   - The terminal message is the primary feedback; `events` provides structured interaction data

4. **Iterate or advance** — if feedback changes the current screen, write a new
   file (`layout-v2.html`). Move to the next question only when the current
   step is validated.

5. **Unload when returning to the terminal** — when the next step does not need
   the browser (a clarifying question, a tradeoff discussion), push a waiting
   screen to clear stale content:

   ```html
   <!-- filename: waiting.html (or waiting-2.html, etc.) -->
   <div style="display:flex;align-items:center;justify-content:center;min-height:60vh">
     <p class="subtitle">Continuing in terminal...</p>
   </div>
   ```

   This stops the user staring at a resolved choice while the conversation has
   moved on. Push a new content file when the next visual question arrives.

6. Repeat until done.

## Writing Content Fragments

Write just the content that goes inside the page. The server wraps it in the
frame template automatically (header, theme CSS, connection status, and all
interactive infrastructure).

**Minimal example:**

```html
<h2>Which layout works better?</h2>
<p class="subtitle">Consider readability and visual hierarchy</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Single Column</h3>
      <p>Clean, focused reading experience</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Two Column</h3>
      <p>Sidebar navigation with main content</p>
    </div>
  </div>
</div>
```

That is it. No `<html>`, no CSS, no `<script>` tags. The server provides all of
that.

## CSS Classes Available

The frame template provides these classes for your content.

### Options (A/B/C choices)

```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Title</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

**Multi-select:** add `data-multiselect` to the container to let users select
multiple options. Each click toggles that item's selected styling.

```html
<div class="options" data-multiselect>
  <!-- same option markup — users can select/deselect multiple -->
</div>
```

### Cards (visual designs)

```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup content --></div>
    <div class="card-body">
      <h3>Name</h3>
      <p>Description</p>
    </div>
  </div>
</div>
```

### Mockup container

```html
<div class="mockup">
  <div class="mockup-header">Preview: Dashboard Layout</div>
  <div class="mockup-body"><!-- your mockup HTML --></div>
</div>
```

### Split view (side-by-side)

```html
<div class="split">
  <div class="mockup"><!-- left --></div>
  <div class="mockup"><!-- right --></div>
</div>
```

### Pros/Cons

```html
<div class="pros-cons">
  <div class="pros"><h4>Pros</h4><ul><li>Benefit</li></ul></div>
  <div class="cons"><h4>Cons</h4><ul><li>Drawback</li></ul></div>
</div>
```

### Mock elements (wireframe building blocks)

```html
<div class="mock-nav">Logo | Home | About | Contact</div>
<div style="display: flex;">
  <div class="mock-sidebar">Navigation</div>
  <div class="mock-content">Main content area</div>
</div>
<button class="mock-button">Action Button</button>
<input class="mock-input" placeholder="Input field">
<div class="placeholder">Placeholder area</div>
```

### Typography and sections

- `h2` — page title
- `h3` — section heading
- `.subtitle` — secondary text below title
- `.section` — content block with bottom margin
- `.label` — small uppercase label text

## Browser Events Format

Clicks are recorded to `$EVENTS_FILE`, one JSON object per line. The file
is cleared automatically when you push a new screen.

```jsonl
{"type":"click","choice":"a","text":"Option A - Simple Layout","timestamp":1706000101}
{"type":"click","choice":"c","text":"Option C - Complex Grid","timestamp":1706000108}
{"type":"click","choice":"b","text":"Option B - Hybrid","timestamp":1706000115}
```

The full stream shows the exploration path — the user may click several
options before settling. The last `choice` event is typically the final
selection, but the click pattern can reveal hesitation worth asking about.

If `$EVENTS_FILE` does not exist, the user did not interact with the
browser — use only their terminal text.

## Data in Mockups — Synthetic Only

**Never put real customer, user, or production data on a screen.** Session
state and event logs capture whatever was shown, and this directory is tracked
from the moment it is written — a realistic mockup built from a real record
commits that record to the repository.

- Invent names, emails, IDs, amounts, and message bodies.
- Do not paste rows from a real database, real support tickets, real logs, or
  a real user's account.
- No credentials, tokens, or connection strings anywhere on a screen, in a
  URL, or in a code sample inside a mockup.
- Public stock imagery (Unsplash and similar) is fine — it is not customer
  data.

See [safety](../executor/references/safety.md) for the required scan and what
to do if something sensitive has already landed.

## Design Tips

- **Scale fidelity to the question** — wireframes for layout, polish for polish questions
- **Explain the question on each page** — "Which layout feels more professional?", not just "Pick one"
- **Iterate before advancing** — if feedback changes the current screen, write a new version
- **2-4 options max** per screen
- **Use representative content when it matters** — for a photography portfolio, real stock images beat grey boxes; placeholder content hides design problems. Representative, never real customer data.
- **Keep mockups simple** — layout and structure, not pixel-perfect design

## File Naming

- Semantic names: `platform.html`, `visual-style.html`, `layout.html`
- Never reuse a filename — each screen is a new file
- Iterations get a version suffix: `layout-v2.html`, `layout-v3.html`
- The server serves the newest file by modification time

## Closing the Session

```bash
../executor/scripts/visual-companion/stop-server.sh "$state_dir"
```

`stop-server.sh` takes `state_dir` — the runtime directory, which is outside
the repository. The screens and events are **kept**: they live under
`docs/executor/` and are never touched by shutdown. Record the session
directory in the frontmatter `sources` of any `RSCH` or `OPTS` document it
produced, so the mockups are reachable from the document that used them.

## Reference

- Frame template (CSS reference): `../executor/scripts/visual-companion/frame-template.html`
- Helper script (client-side): `../executor/scripts/visual-companion/helper.js`
