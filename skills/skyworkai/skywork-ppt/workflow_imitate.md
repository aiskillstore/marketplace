# PPT Imitation Workflow

The user provides an existing PPTX file as a layout/style reference. Generate a new presentation on a different topic that follows the same visual structure.

Follow these steps in order: identify intent → locate template → web search → upload template → run script (streaming) → **output progress at every phase** (required) → save file → deliver. **Never go silent for an extended period — always stream progress as it arrives.**

---

## 0. Confirm imitation intent

Use this workflow (instead of the standard generate flow) when **both** of the following are true:

- The user mentions a template, style reference, or an existing file — e.g. "use this template", "match the style of this PPT", "imitate this layout" — **or** provides a `.pptx` file path or filename.
- The user has a new generation request (topic, content, slide count, etc.).

If the user provides a template but no new topic, **ask what they want to create** before proceeding.

---

## 1. Locate the local template file

Extract the local PPTX path from the user's message. It may appear as:

- An absolute path: `/Users/xxx/templates/style.pptx`
- A relative path or filename: `my_template.pptx` (infer the full path from context)
- An attachment uploaded in the conversation (the platform will provide a local temp path)

**If the path is ambiguous, ask the user for the full absolute path.**

---

## 2. Parse reference files (optional — only if the user provides local files as content source)

If the user provides additional local files (PDF, DOCX, PPTX, images, etc.) to use as content source — separate from the template — parse each file with the document parse service.

Run `parse_file.py` once per file, this may cost a few minutes to finish completely:

```bash
$PYTHON_CMD scripts/parse_file.py /path/to/file1.pdf
$PYTHON_CMD scripts/parse_file.py /path/to/file2.docx
```
- **exec tool `yieldMs`**: Must be set to `600000` (10 minutes) when invoking the exec tool.

Each call prints a `PARSED_FILE:` line on success:
```
PARSED_FILE: {"filename": "file1.pdf", "url": "https://...", "file_id": "123456789"}
```

Collect every `PARSED_FILE:` result and assemble them into a JSON array as `DOC_FILES_JSON`:
```json
[
  {"filename":"file1.pdf","url":"https://...","file_id":"123456789","file_type":"pdf"},
  {"filename":"file2.docx","url":"https://...","file_id":"987654321","file_type":"docx"}
]
```

Pass this array to `--files` in Step 6. If no additional content files are provided, skip this step entirely.

---

## 3. Web search (required if no relevant content is already in the conversation)

Skip if the user has already provided sufficient reference material or reference files.
Otherwise, run up to 3 targeted searches on the **new PPT topic**:

```bash
$PYTHON_CMD scripts/web_search.py "query1" "query2" "query3"
```

Produce a detailed reference report following the same format and constraints as the generate workflow (target 800–2000 words, preserve all specific details, never fewer than 500 words).

After writing the reference report, save it to a local temp file:
```bash
cat > /tmp/ppt_reference.md << 'REFERENCE_EOF'
<paste the full reference report here>
REFERENCE_EOF
```
Use this file path as `--reference-file` in Step 6.

---

## 4. Upload the template to OSS

```bash
$PYTHON_CMD scripts/upload_files.py "/absolute/path/to/template.pptx"
```

- Script output format: `[OK] /path/to/file.pptx -> https://cdn.xxx/skills/upload/yyyy-mm-dd/uuid_filename.pptx`
- Extract the OSS URL from the output and call it `TEMPLATE_URL`.
- If the upload fails, inform the user and stop.

---

## 5. Confirm generation parameters

- **query** (required): Faithfully reproduce the user's full request — include every instruction (slide count, style, audience, etc.). Do not fabricate or omit anything.
- **language** (required): Language for the slides, e.g. `Chinese`, `English`.
- **language** (required): Detect from the user's input language — if the user writes in Chinese pass `Chinese`; English → `English`; etc. Never default to a fixed value.
- **template_urls** (required): The OSS URL(s) from Step 4. Multiple URLs are supported (comma-separated) — the backend selects the best-matching layout from each. One URL is sufficient in most cases; pass multiple only if the user provided several template files.
- **--reference-file** (optional): Path to the temp file written at the end of Step 3 (e.g. `/tmp/ppt_reference.md`). Omit if no search was performed.
- **--files** (optional): Pass the JSON array assembled from the `PARSED_FILE:` lines in Step 2. Omit if no content files were provided. Format: `[{"filename":"...","url":"...","file_id":"...", "file_type": "pdf"},...]`

---

## 6. Run the script

PPT generation takes ~10 minutes. Run it in the **background**, then read the progress log file every 5 seconds until done.

### 6a. Choose a log path and start in background
```bash
PPT_LOG=/tmp/ppt_$(date +%s).log

$PYTHON_CMD scripts/run_ppt_write.py "user query" \
  --language Chinese \
  --template_urls "TEMPLATE_URL1,TEMPLATE_URL2" \
  --reference-file /tmp/ppt_reference.md \
  --files '[{"file_name":"report.pdf","url":"https://...", "file_id":"1212121", "file_type":"pdf"}]' \
  --log_path "$PPT_LOG" \
  -o /absolute/path/to/output.pptx \
  > /dev/null 2>&1 &

echo "Log: $PPT_LOG"
```

- **`--log_path`** (required): Pass the pre-chosen path. The script writes all progress here.
- **`-o`** (required): Use an absolute path for reliable delivery.
- **`--template_urls`**: Comma-separated OSS URLs of template files from Step 4.
- **`--files`**: Pass the JSON array assembled from `PARSED_FILE:` lines **verbatim**. Omit if no reference files.

### 6b. Monitor progress （REQUIRED）

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

**Stop polling** as soon as you see `[DONE]` or `[ERROR]`.


## 7. Deliver

### Success

Provide all of the following:
1. Download link
2. Local `.pptx` absolute path
3. Presentation title
4. Brief description of each slide's content
5. Template filename used (so the user can verify)

### Failure

Briefly explain the error.
---

## Appendix — Intent classification examples

| User input | Use this workflow? |
|------------|--------------------|
| Make me a PPT about Beijing travel | ❌ Standard generate |
| Use this template to make a PPT on AI trends — template at `/tmp/style.pptx` | ✅ Imitate |
| Imitate the uploaded pptx style, 10-slide quarterly review | ✅ Imitate |
| What style is this template? | ❌ Not a generation request — just answer the question |
