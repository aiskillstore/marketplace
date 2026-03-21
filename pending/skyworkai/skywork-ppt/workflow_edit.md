# PPT Edit Workflow

Edit an existing PPT via natural language: modify individual slides, add new slides, change the overall style, split or merge slides.

Follow these steps in order: get pptx_url → confirm intent → run script (background) → **read log every 5s and report progress** (required) → deliver. **Never go silent — always report status as you poll the log.**

---

## 1. Get the PPTX URL

The user must supply a publicly accessible OSS/CDN URL of the existing PPTX to edit.

- If the user provides a **local file path** instead of a URL, upload it first:
  ```bash
  $PYTHON_CMD scripts/upload_files.py "/absolute/path/to/file.pptx"
  ```
  Extract the URL from the `[OK] ... -> https://...` output line.

- If the URL is already provided (e.g. from a previous generation's `Download URL:` output), use it directly.

---

## 2. Confirm edit intent

Understand what the user wants to change. Supported operations include:

| Operation | Example user intent |
|-----------|---------------------|
| Modify a slide | "change page 4 background to black, text to white" |
| Add a new slide | "insert a new slide after page 3 about X" |
| Change overall style | "make all slides use a dark theme" |
| Split a slide | "split page 5 into two slides" |
| Merge slides | "merge pages 2 and 3 into one slide" |

Pass the user's original instruction verbatim as `query`. Do not paraphrase — the backend interprets it directly.

---

## 3. Run the script

Run in the **background**, then read the progress log file every 5 seconds until done.

### 3a. Choose a log path and start in background
```bash
PPT_LOG=/tmp/ppt_$(date +%s).log

$PYTHON_CMD scripts/run_ppt_write.py "user's edit instruction" \
  --language Chinese \
  --pptx-url "https://cdn.example.com/path/to/file.pptx" \
  --log_path "$PPT_LOG" \
  -o /absolute/path/to/output.pptx \
  > /dev/null 2>&1 &

echo "Log: $PPT_LOG"
```

- **`--log_path`** (required): Pass the pre-chosen path. The script writes all progress here.
- **`--pptx-url`** (required): OSS URL of the PPTX to edit. This triggers edit mode.
- **`--language`** (required): Detect from user input — `Chinese` or `English`.
- **`-o`** (required): Absolute output path for the edited PPTX.

### 3b. Monitor progress （REQUIRED）

> **STRICT RULES — no exceptions:**
> 1. **Read the log exactly every 5 seconds.** Do NOT extend the interval, do NOT skip reads.
> 2. **Before every read, check if the process is still alive.** If alive → only read log, NEVER restart.

**Every 5 seconds, run this exact sequence:**
```bash
# Step 1: extract PID from log
PPT_PID=$(grep '^\[PID\]' "$PPT_LOG" | tail -1 | awk '{print $2}')
# Step 2: check if process is alive
kill -0 "$PPT_PID" 2>/dev/null && PPT_ALIVE=true || PPT_ALIVE=false
# Step 3: read the log regardless
tail -20 "$PPT_LOG"
```
- If process is **RUNNING** → report status to user, wait 5s, repeat. Do NOT touch the script.
- If process is **not running** AND log ends with `[DONE]` or `[ERROR]` → stop polling, proceed to deliver/handle error.
- If process is **not running** AND no `[DONE]`/`[ERROR]` in log → the script crashed; report error to user, ask whether to retry. **Both conditions must hold: PID gone AND no terminal log line. NEVER retry without explicit user confirmation.**

Each line is plain text: 
- `[PID] <pid>` — process ID written at startup
- `[START]` — job started
- `[PHASE] <message>` — in progress
- `[DONE] saved=<path> download_url=<url>` — finished
- `[ERROR] <message>` — failed

**After each read, report status to the user:**
```
[Main stage] | [current action] 
Example: Generating slides | Working on page 3 
```

Progress phases:

| Message contains | Main stage |
|-----------------|------------|
| "Parsing existing PPTX" | Parsing original PPTX |
| "update plan" | Planning updates |
| "updated slides" / "Slide N updated" | Generating updated slides |
| "Exporting" / "Export complete" | Exporting PPTX |

**Stop polling** as soon as you see `[DONE]` or `[ERROR]`.

---

## 4. Deliver

Provide all of the following:
1. Download link (`download_url` from the completion event)
2. Local `.pptx` absolute path
3. Brief summary of what was changed (which pages, what modifications)

### Failure

Briefly explain the error.
