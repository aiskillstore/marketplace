---
name: chronicle-remote-summarizer
description: Automate cross-system summarization workflow for Chronicle sessions. Export sessions from remote systems (like FreeBSD) and import/summarize on local machine with Gemini API. Use when you have sessions on a system without Gemini API access and need to summarize them on another machine.
---

# Chronicle Remote Summarizer

This skill automates the workflow for summarizing Chronicle sessions across different systems (e.g., FreeBSD dev machine → Mac with Gemini API).

## Auto-Activation

> **This skill auto-activates!** (Milestone #13)
>
> Prompts like "summarize session on remote" or "import session from FreeBSD" automatically trigger this skill!
>
> **Trigger patterns:** remote, freebsd, import session, summarize on remote
> **See:** `docs/HOOKS.md` for full details

## When to Use This Skill

Use this skill when:
- You have Chronicle sessions on a remote system without Gemini API configured
- You want to summarize those sessions on your local machine (which has Gemini API)
- You need to transfer the summary back to the original system
- You're working across multiple development environments (FreeBSD, Linux, macOS)

**Common scenario**: FreeBSD development server (no Gemini API) → macOS laptop (has Gemini API key)

## How It Works

Chronicle provides `import-and-summarize --quiet` which:
1. Creates temporary session with negative ID (e.g., `-3`)
2. Generates AI summary using Gemini
3. **Auto-cleanup**: Deletes temporary session and files
4. Outputs **clean JSON** to stdout (no status messages with `--quiet`)

**No pollution between systems** - the remote session stays on the remote system, only the summary is transferred.

## Recommended Workflow: One-Line Command

**Prerequisites:**
- SSH access from local machine to remote machine
- Chronicle installed on both systems
- Gemini API key configured on local machine (`chronicle config ai.gemini_api_key YOUR_KEY`)
- **Optional**: Remote system configured in Chronicle config (automates hostname/path)

**Step 1: Configure Remote System (One-Time Setup)**

```bash
# Configure FreeBSD remote system
chronicle config remote_systems.freebsd.hostname "chandlerhardy-dev.aws0.pla-net.cc"
chronicle config remote_systems.freebsd.chronicle_path "/home/chandlerhardy/.local/bin/chronicle"

# Verify configuration
chronicle config --list | grep freebsd
```

**Step 2: Use the Skill**

When Claude uses this skill and finds remote system configuration, it will automatically construct the command:

```bash
ssh chandlerhardy-dev.aws0.pla-net.cc "/home/chandlerhardy/.local/bin/chronicle export-session 7" | chronicle import-and-summarize --quiet 2>&1 | grep -A 999999 '^{$' | ssh chandlerhardy-dev.aws0.pla-net.cc "/home/chandlerhardy/.local/bin/chronicle import-summary"
```

**If no config found**, Claude will ask for the hostname and construct the command interactively:

**Command (Manual):**
```bash
ssh <remote-host> "chronicle export-session <id>" | chronicle import-and-summarize --quiet 2>&1 | grep -A 999999 '^{$' | ssh <remote-host> "chronicle import-summary"
```

**Example:**
```bash
ssh freebsd "chronicle export-session 7" | chronicle import-and-summarize --quiet 2>&1 | grep -A 999999 '^{$' | ssh freebsd "chronicle import-summary"
```

**Note:** The `grep -A 999999 '^{$'` filters out Google library warnings that can leak through even with `--quiet` and `2>/dev/null`.

**What this does:**
1. **Remote → Local**: Export session 7 as JSON
2. **Local**: Import, summarize with Gemini, auto-cleanup temporary session
3. **Local → Remote**: Send summary JSON back
4. **Remote**: Update session 7 with the summary

**Why `--quiet` works:**
- Suppresses ALL status messages from summarizer
- Outputs ONLY clean JSON to stdout (essential for piping)
- No need to manually extract JSON from verbose output
- `2>/dev/null` suppresses Google library warnings (harmless)

**Time:** Typically 30-60 seconds for large sessions (depends on transcript size)

## Alternative: Manual 3-Step Workflow

If SSH pipes hang or you need to inspect intermediate files:

### Step 1: Export session from remote
```bash
ssh <remote-host> "chronicle export-session <id>" > /tmp/session_<id>.json
```

**Example:**
```bash
ssh freebsd "chronicle export-session 7" > /tmp/session_7.json
```

### Step 2: Summarize locally (transient)
```bash
cat /tmp/session_<id>.json | chronicle import-and-summarize --quiet 2>/dev/null > /tmp/summary.json
```

**Example:**
```bash
cat /tmp/session_7.json | chronicle import-and-summarize --quiet 2>/dev/null > /tmp/summary.json
```

**What happens:**
- Creates temporary session (negative ID like `-3`)
- Generates summary with Gemini
- **Auto-cleanup**: Deletes temporary session and transcript files
- Outputs summary JSON to `/tmp/summary.json`

### Step 3: Send summary back to remote
```bash
cat /tmp/summary.json | ssh <remote-host> "chronicle import-summary"
```

**Example:**
```bash
cat /tmp/summary.json | ssh freebsd "chronicle import-summary"
```

**Result:**
- ✅ Summary stored in remote database linked to original session
- ✅ Local system stays clean (temporary session auto-deleted)
- ✅ No data pollution between systems

## What Actually Happens (Under the Hood)

**On `import-and-summarize --quiet`:**

1. **Import**: Reads session JSON from stdin
2. **Create Temporary Session**:
   - Assigns negative ID (e.g., `-1`, `-2`, `-3`)
   - Stores transcript in `~/.ai-session/sessions/session_-3.cleaned`
   - Creates database entry with `is_session=True`
3. **Summarize**:
   - Runs `summarize_session_chunked()` with Gemini API
   - Processes large transcripts in chunks (10,000 lines per chunk)
   - Updates session with AI-generated summary
4. **Output JSON**:
   ```json
   {
     "version": "1.0",
     "original_id": 7,
     "summary": "AI-generated summary...",
     "summary_generated": true,
     "keywords": ["feature", "implementation", "testing"]
   }
   ```
5. **Auto-Cleanup**:
   - Deletes transcript file (`session_-3.cleaned`)
   - Deletes database entry (temporary session)
   - **Only the summary JSON remains** (piped to stdout)

**On `import-summary` (remote side):**

1. **Read JSON**: Reads summary from stdin
2. **Find Session**: Looks up session by `original_id` (e.g., 7)
3. **Update**: Sets `response_summary`, `summary_generated=True`, `keywords`
4. **Done**: Session 7 now has the AI summary

## Session Examples

**Tested with:**
- Session 1: 16.3 minutes, system test
- Session 2: 66.7 minutes, large session
- Session 4: 23KB JSON export

All sessions work perfectly with this workflow.

## Troubleshooting

### SSH Pipes Hang

**Symptom:** Command hangs indefinitely

**Solution:** Use manual 3-step workflow instead:
```bash
# Step 1: Export to file
ssh freebsd "chronicle export-session 7" > /tmp/session.json

# Step 2: Process locally
cat /tmp/session.json | chronicle import-and-summarize --quiet > /tmp/summary.json

# Step 3: Send back
cat /tmp/summary.json | ssh freebsd "chronicle import-summary"
```

### Gemini API Not Configured

**Symptom:** `ImportError: google-generativeai package not installed`

**Solution:** Configure Gemini API key on local machine:
```bash
chronicle config ai.gemini_api_key YOUR_API_KEY_HERE
```

Get free API key: https://ai.google.dev/

### Session Not Found

**Symptom:** `Session 7 not found`

**Solution:** Check session exists on remote:
```bash
ssh freebsd "chronicle sessions --limit 20"
```

### Summary Already Exists

**Behavior:** `import-and-summarize` will **overwrite** existing summaries

**Note:** This is by design - you can re-summarize sessions if needed.

## Tips

- **Use `--quiet` flag**: Essential for piping - suppresses status messages
- **Suppress stderr**: Add `2>/dev/null` to hide Google library warnings
- **Check SSH paths**: Remote Chronicle might be in `~/.local/bin/chronicle`
- **Inspect files**: Use 3-step workflow to save intermediate JSON for debugging
- **Large sessions**: 10K+ line transcripts are chunked automatically (no action needed)
- **Network failures**: Use 3-step workflow for unreliable connections
- **Batch processing**: You can script this to process multiple sessions

## How Claude Should Use This Skill

**When invoked, Claude should:**

1. **Check for remote system config:**
   ```bash
   chronicle config --list | grep remote_systems
   ```

2. **If config exists** (e.g., `remote_systems.freebsd.hostname`):
   - Read hostname: `chronicle config remote_systems.freebsd.hostname`
   - Read chronicle path: `chronicle config remote_systems.freebsd.chronicle_path`
   - Construct command automatically
   - Announce: "Found FreeBSD config, using: `<hostname>`"

3. **If no config exists:**
   - Ask user: "What's the hostname of your remote system?"
   - Ask: "What's the path to chronicle on the remote? (default: chronicle)"
   - Optionally suggest: "I can save this to config for future use"
   - Construct command with user-provided values

4. **Run the command** and monitor output

5. **Confirm success** or handle errors

## Example Usage

**User:** "I have session 7 on my FreeBSD dev machine that needs summarization, but FreeBSD doesn't have Gemini API. Can you summarize it here on my Mac?"

**Assistant (with config):**
1. Checks config: `chronicle config remote_systems.freebsd.hostname`
2. Finds: `chandlerhardy-dev.aws0.pla-net.cc`
3. Announces: "Found FreeBSD config, using chandlerhardy-dev.aws0.pla-net.cc"
4. Runs the command:
   ```bash
   ssh chandlerhardy-dev.aws0.pla-net.cc "/home/chandlerhardy/.local/bin/chronicle export-session 7" | chronicle import-and-summarize --quiet 2>&1 | grep -A 999999 '^{$' | ssh chandlerhardy-dev.aws0.pla-net.cc "/home/chandlerhardy/.local/bin/chronicle import-summary"
   ```
5. Confirms: "Session 7 summarized successfully and summary imported back to FreeBSD"

**Assistant (without config):**
1. Checks config: `chronicle config --list | grep remote_systems`
2. No FreeBSD config found
3. Asks: "What's your FreeBSD hostname?"
4. User provides: `chandlerhardy-dev.aws0.pla-net.cc`
5. Asks: "What's the path to chronicle on FreeBSD? (press Enter for default 'chronicle')"
6. User provides: `/home/chandlerhardy/.local/bin/chronicle`
7. Suggests: "I can save this to config for future use. Would you like me to?"
8. Runs the command with provided values
9. If user agrees, saves config for next time

**If one-liner hangs:**
1. Falls back to 3-step workflow
2. Exports to `/tmp/session_7.json`
3. Processes locally → `/tmp/summary.json`
4. Imports summary back to remote
5. Confirms success

## Advanced Usage

### Batch Summarize Multiple Sessions

```bash
# List unsummarized sessions on remote
ssh freebsd "chronicle sessions --limit 50" | grep "No summary"

# For each session ID (7, 8, 9):
for id in 7 8 9; do
  echo "Summarizing session $id..."
  ssh freebsd "chronicle export-session $id" | \
    chronicle import-and-summarize --quiet 2>/dev/null | \
    ssh freebsd "chronicle import-summary"
done
```

### Inspect Summary Before Importing

```bash
# Export and summarize
ssh freebsd "chronicle export-session 7" | \
  chronicle import-and-summarize --quiet 2>/dev/null > /tmp/summary.json

# Review summary
cat /tmp/summary.json | jq '.summary'

# If satisfied, import
cat /tmp/summary.json | ssh freebsd "chronicle import-summary"
```

### Debug Verbose Output

If you need to see what's happening, remove `--quiet`:

```bash
ssh freebsd "chronicle export-session 7" | chronicle import-and-summarize
# Shows: "Importing session...", "Summarizing...", "Cleaning up...", then JSON
```

**Note:** Without `--quiet`, JSON is NOT at line 1, so it won't pipe cleanly to `import-summary`.

## Related Commands

- `chronicle export-session <id>` - Export session as JSON
- `chronicle import-session` - Import session (permanent, gets new ID)
- `chronicle import-and-summarize` - Import + summarize + auto-cleanup (transient)
- `chronicle import-summary` - Update existing session with summary
- `chronicle session <id>` - View session details and summary

## See Also

- **REMOTE_SUMMARIZE_WORKFLOW.md** - Full workflow documentation with examples
- **tests/test_import_export.py** - 17 tests covering all import/export scenarios
- **chronicle-session-documenter** - Document sessions to Obsidian vault after summarization
