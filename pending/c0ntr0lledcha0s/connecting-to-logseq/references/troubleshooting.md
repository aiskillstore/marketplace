# Logseq Connection Troubleshooting

## Quick Diagnostics

Run the diagnostic script:
```bash
python logseq-expert/scripts/preflight-checks.sh
```

Or test connectivity:
```bash
python logseq-expert/scripts/test-connection.py --verbose
```

## Common Issues

---

### Issue: "Connection refused" or "Cannot connect"

**Symptoms**:
- `Connection refused` errors
- `ECONNREFUSED` in logs
- Timeout when connecting

**Causes & Solutions**:

1. **Logseq not running**
   - Start Logseq application
   - Wait for it to fully load

2. **HTTP API not enabled**
   - Settings → Advanced → Developer mode: ON
   - Settings → Advanced → HTTP APIs server: ON
   - Restart Logseq after changing

3. **Wrong port**
   - Default is 12315
   - Check Settings → Advanced for custom port
   - Update `LOGSEQ_API_URL` if different

4. **Firewall blocking**
   ```bash
   # Test port directly
   nc -zv 127.0.0.1 12315

   # Or with curl
   curl -v http://127.0.0.1:12315/api
   ```

---

### Issue: "401 Unauthorized" or "Invalid token"

**Symptoms**:
- HTTP 401 response
- "Authentication failed" message

**Causes & Solutions**:

1. **No token set**
   ```bash
   # Check if set
   echo $LOGSEQ_API_TOKEN

   # Set it
   export LOGSEQ_API_TOKEN="your-token"
   ```

2. **Wrong token**
   - Create new token in Logseq: Settings → Advanced → Authorization tokens
   - Copy carefully (no extra spaces)
   - Update environment variable

3. **Token revoked**
   - Check Logseq settings for active tokens
   - Create new token if needed

4. **Bearer prefix issues**
   - Ensure header is: `Authorization: Bearer TOKEN`
   - No extra "Bearer" if using raw token

---

### Issue: "CLI command not found"

**Symptoms**:
- `logseq: command not found`
- `'logseq' is not recognized`

**Solutions**:

1. **Install CLI**
   ```bash
   npm install -g @logseq/cli
   ```

2. **Check npm path**
   ```bash
   # Find npm global bin
   npm bin -g

   # Add to PATH if needed
   export PATH="$PATH:$(npm bin -g)"
   ```

3. **Use npx instead**
   ```bash
   npx @logseq/cli --help
   ```

---

### Issue: "Graph not found" (CLI)

**Symptoms**:
- "Graph not found at path"
- "Invalid graph directory"

**Solutions**:

1. **Verify path exists**
   ```bash
   ls -la /path/to/graph
   ```

2. **Check graph structure**
   - DB graph: should have `db.sqlite`
   - MD graph: should have `logseq/` folder

3. **Use absolute path**
   ```bash
   logseq query "..." --graph /full/path/to/graph
   ```

4. **Check permissions**
   ```bash
   # Ensure readable
   ls -la /path/to/graph/db.sqlite
   ```

---

### Issue: "Query syntax error"

**Symptoms**:
- "Invalid query"
- Datalog parse errors

**Common Causes**:

1. **Wrong attribute names (MD vs DB)**

   | MD Version | DB Version |
   |------------|------------|
   | `:block/content` | `:block/title` |
   | `:block/name` | `:block/title` |
   | `:page/tags` | `:block/tags` |

2. **Missing brackets**
   ```clojure
   ;; Wrong
   :find ?title :where [?p :block/title ?title]

   ;; Correct
   [:find ?title :where [?p :block/title ?title]]
   ```

3. **Incorrect pull syntax**
   ```clojure
   ;; Wrong
   [:find ?e :where ...]

   ;; Correct for entities
   [:find (pull ?e [*]) :where ...]
   ```

---

### Issue: "MCP server not responding"

**Symptoms**:
- MCP tools not appearing
- Server timeout errors

**Solutions**:

1. **Build the server**
   ```bash
   cd logseq-expert/servers/logseq-mcp
   npm install
   npm run build
   ```

2. **Check Node.js version**
   ```bash
   node --version  # Should be 18+
   ```

3. **Verify HTTP API works first**
   - MCP server uses HTTP API internally
   - Fix HTTP connection issues first

4. **Check server logs**
   - MCP server logs to stderr
   - Look for startup errors

---

### Issue: Windows-specific "EBADF" errors

**Symptoms**:
- `EBADF: bad file descriptor` on Windows
- Intermittent connection failures

**Solutions**:

1. **Run Logseq as Administrator**
   - Right-click → Run as administrator

2. **Disable antivirus temporarily**
   - Some AV software interferes with localhost connections

3. **Use WSL**
   - Run scripts from WSL if native Windows fails

4. **Check Windows Firewall**
   - Allow Logseq through firewall
   - Allow Node.js if using MCP

---

## Diagnostic Commands

### Check all backends
```bash
python logseq-expert/scripts/detect-backend.py
```

### Test HTTP API manually
```bash
curl -X POST http://127.0.0.1:12315/api \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LOGSEQ_API_TOKEN" \
  -d '{"method":"logseq.App.getCurrentGraph"}'
```

### Test CLI
```bash
logseq --version
logseq graphs list
```

### Check environment
```bash
echo "API URL: ${LOGSEQ_API_URL:-http://127.0.0.1:12315}"
echo "Token set: $([ -n "$LOGSEQ_API_TOKEN" ] && echo 'yes' || echo 'no')"
```

### Full diagnostic
```bash
python logseq-expert/scripts/test-connection.py --verbose
```

## Getting Help

If issues persist:

1. Check Logseq forum: https://discuss.logseq.com/
2. Logseq GitHub issues: https://github.com/logseq/logseq/issues
3. Plugin API docs: https://plugins-doc.logseq.com/
