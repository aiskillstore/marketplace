# NotebookLM Manager Commands

## Command Reference

| Command | Description |
|---------|-------------|
| `list` | Show active notebooks |
| `list --all` | Include archived |
| `show <id>` | Notebook details |
| `add <url>` | Smart add (auto-discover) |
| `add <url> --manual` | Manual add (skip discovery) |
| `search <query>` | Find notebooks |
| `enable/disable <id>` | Toggle status |
| `remove <id>` | Delete (confirm required) |

## Smart Add Mode

When user provides a URL with `add <url>` (without `--manual`):

### Workflow

1. **Extract notebook ID from URL**
   ```
   https://notebooklm.google.com/notebook/<notebook-id>
   → notebook-id
   ```

2. **Invoke agent in discover mode**
   ```
   Task({
     subagent_type: "notebooklm-connector:chrome-mcp-query",
     prompt: "URL: {url}\nQuestion: What is the main topic and content of this notebook? List the document titles.\nmode: discover\nclearHistory: false"
   })
   ```

3. **Parse agent response**
   - Extract notebook title from agent output
   - Extract topics from `**Extracted Metadata**` section
   - Extract description from response summary

4. **Generate ID from title**
   ```
   "Claude API Documentation" → "claude-api-documentation"
   ```

5. **Register in library.json**
   ```json
   {
     "id": "claude-api-documentation",
     "name": "Claude API Documentation",
     "url": "https://notebooklm.google.com/notebook/...",
     "topics": ["API", "Claude", "Documentation"],
     "added_at": "<ISO timestamp - use current datetime>",
     "discovered_by": "smart-add"
   }
   ```

6. **Confirm to user**
   ```
   Notebook added successfully!

   Name: Claude API Documentation
   ID: claude-api-documentation
   Topics: API, Claude, Documentation

   Discovered content:
   [Summary from agent response]
   ```

### Manual Add (--manual flag)

Skip discovery, prompt user for metadata:
```
AskUserQuestion({
  questions: [
    { question: "What is the notebook name?", header: "Name", ... },
    { question: "What topics does it cover?", header: "Topics", ... }
  ]
})
```