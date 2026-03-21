# PPT Generate Workflow

Follow these steps in order: confirm inputs → run script (streaming) → **output progress at every phase** (required) → save file → deliver. **Never go silent for an extended period — always stream progress as it arrives.**

---

## 1. Parse reference files (optional — only if the user provides local files)

If the user provides local files (PDF, DOCX, PPTX, images, etc.) as content source for the PPT, parse each file with the document parse service. This uploads the file, extracts its content, and returns metadata (file_id, file_url).

Run `parse_file.py` once per filet, his may cost a few minutes to finish completely::

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

Pass this array to `--files` in Step 3. If no local files are provided, skip this step entirely.

---

## 2. Web search (required if no relevant content is already in the conversation)

Skip this step if the user has already provided sufficient reference material or reference files.
Otherwise, run up to 3 targeted searches on the topic, make sure your query contains the date if you need to search the latest information:

### Run searches

```bash
$PYTHON_CMD scripts/web_search.py "query1" "query2" "query3"
```

- Break the topic into 1–3 focused queries (e.g. for "Beijing travel guide": "Beijing top attractions", "Beijing food recommendations", "Beijing transportation tips").
- **If the topic involves current events, trends, statistics, or anything time-sensitive**, append the current year (e.g. `2026`) or a date range to each query to ensure results are up to date. Example: `"AI agent market trends 2026"` instead of `"AI agent market trends"`.
- Deduplicate and distill all results into a `reference` text to enrich the PPT content.

### Synthesize search results

**If reference files were parsed in Step 1**, use their `parsed_content` as the primary source and supplement with search results. The parsed content contains the full document text — extract and preserve all detail, do not compress it into a short summary.

Produce a detailed **reference report**. **Target 800–2000 words — do not stop early.** Write as much specific detail as the sources provide:

```
## Key Findings
3–5 sentences covering the main conclusions, background, and why it matters.

## Key Data & Facts
- List every specific number, percentage, date, and metric found. Do not skip data.
- Format: "Exact figure — what it measures (source)"
- Aim for at least 5 data points if the source contains them.

## Topic Breakdown
Organize by sub-topic. For each sub-topic write 3–5 specific bullet points.
Do not use vague phrases like "it is important" — state the actual fact.
Preserve names of people, companies, products, places, and dates exactly as found.

## Cases & Examples (if available)
Concrete examples, case studies, or use cases with specific details and outcomes.

## Summary
3–5 bullet points capturing the core message the PPT must convey.
```

**Hard constraints**:
- Only include information that **explicitly appears** in the sources. Do not invent or infer.
- Numbers, percentages, and proper nouns must be quoted exactly — do not paraphrase or round.
- **Never produce fewer than 500 words** unless the source material is genuinely sparse.
- If a section has no relevant information, omit that section entirely.
- **Note the publication date of each source.** Always include the current date context in the summary where relevant.

After writing the reference report, save it to a local temp file to avoid shell encoding issues:
```bash
cat > /tmp/ppt_reference.md << 'REFERENCE_EOF'
<paste the full reference report here>
REFERENCE_EOF
```
Use this file path as `--reference-file` in Step 3.

---

## 2. Confirm inputs

- **query** (required): Faithfully reproduce the user's full request — include every instruction the user mentioned. Cover the following if the user specified them; do not add anything they didn't mention:
  - Slide count (if the user set a limit, it must be included — never drop it)
  - Topic / content direction
  - Style preference (e.g. business, academic, playful, minimalist)
  - Audience / purpose (e.g. "exec briefing for the CXO", "science explainer for kids")
  - Structure preference (e.g. "data-heavy", "one case study per slide")
  - Other constraints (tone, things to avoid, required talking points, etc.)

  **Rule**: Do not fabricate requirements the user never mentioned, and do not omit anything they explicitly said. If the user gives only a title, the query is exactly that title — don't add qualifiers.

  **Examples**:

  | User input | Correct query |
  |------------|---------------|
  | Make me a PPT about Beijing travel | `Beijing Travel Guide PPT` |
  | 8-page English slides on AI Agent, clean business style, targeting investors | `8-page English slides on AI Agent, clean business style, targeting investors` |
  | PPT for our Q1 sales summary, 10 slides, with data charts, formal style | `Q1 Sales Summary PPT, 10 slides, data charts, formal business style` |
  | A fun solar system PPT for elementary school kids, 6 pages | `Solar System explainer PPT for elementary school kids, fun and engaging style, 6 slides` |

- **language** (required): Detect from the user's input language — if the user writes in Chinese pass `Chinese`; English → `English`; etc. Never default to a fixed value.
- **--reference-file** (optional): Pass the path to the temp file written at the end of Step 2 (e.g. `/tmp/ppt_reference.md`). Omit if no search was performed.
- **--files** (optional): Pass the JSON array assembled from the `PARSED_FILE:` lines in Step 1. Omit if no files were provided. Format: `[{"file_name":"...","url":"...","file_id":"...", "file_type": "pdf"},...]`

---

## 3. Run the script

PPT generation takes ~10 minutes. Choose a log path first, pass it to the script, then read it every 5 seconds.

### 3a. Choose a log path and start in background
```bash
PPT_LOG=/tmp/ppt_$(date +%s).log

$PYTHON_CMD scripts/run_ppt_write.py "user query" \
  --language English \
  --reference-file /tmp/ppt_reference.md \
  --files '[{"file_name":"report.pdf","url":"https://...", "file_id":"1212121", "file_type":"pdf"}]' \
  --log_path "$PPT_LOG" \
  -o /absolute/path/to/output.pptx \
  > /dev/null 2>&1 &

echo "Log: $PPT_LOG"
```

- **`--log_path`** (required): Pass the pre-chosen path. The script writes all progress here.
- **`-o`** (required): Use an absolute path.
- **`--files`**: JSON array from `DOC_FILES_JSON:` lines **verbatim**. Omit if no reference files.

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
- `[PHASE] <message>` — stage transition (outline, slides, export, etc.)
- `[PING] <progress>% | <stage>` — heartbeat every few seconds with current progress and stage label
- `[OUTLINE]` — outline content (appears once after outline_done)
- `[DONE] saved=<path> download_url=<url>` — finished
- `[ERROR] <message>` — failed

**After each read, report status to the user:**
```
[Main stage] | [current action]
Example: Generating slides | Working on page 3 
```

Map phase messages to main stages:

| Message contains | Main stage |
|-----------------|------------|
| "outline" | Generating outline |
| "slide" / "page" / "content" | Generating slides |
| "image" / "HTML" | Rendering images |
| "Export" / "export" | Exporting PPTX |
| "Parsing existing PPTX" | Parsing original PPTX |
| "update plan" | Planning updates |
| "template" | Processing template |

**Stop polling** as soon as you see `[DONE]` or `[ERROR]`.

---

## 4. Deliver

### Success

Provide all of the following:
1. Download link
2. Local `.pptx` absolute path
3. Presentation title
4. Brief description of each slide's content

### Failure

Briefly explain the error. 

## Technical Notes
- **Timeout**: PPT generation takes ~10 minutes, set sufficient timeout
