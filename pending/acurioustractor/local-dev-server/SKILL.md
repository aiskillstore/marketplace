# Local Development Server Management

**Purpose:** Zero-friction local development server management for Empathy Ledger using PM2

**Trigger:** When user needs to start/stop/restart local dev server, or when "address already in use" errors occur

---

## Quick Commands

```bash
# Single project (Empathy Ledger only)
pm2 start empathy-ledger       # Start server
pm2 restart empathy-ledger     # Restart server
pm2 stop empathy-ledger        # Stop server
pm2 logs empathy-ledger        # View logs

# Full ACT ecosystem (all projects)
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh start
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh restart
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh stop
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh logs
```

---

## Problem This Solves

**Pain Points:**
- ❌ "address already in use" errors when port is occupied
- ❌ Forgetting to restart server after code changes
- ❌ Server crashes and doesn't auto-restart
- ❌ Can't find which process is using the port
- ❌ Manual `npm run dev` is fragile and doesn't persist

**Solution:**
- ✅ PM2 manages process lifecycle automatically
- ✅ Auto-restart on crashes
- ✅ Centralized logging
- ✅ Works with ACT ecosystem deployment script
- ✅ Simple commands for start/stop/restart

---

## When to Use PM2 vs npm run dev

### Use PM2 When:
- Working on multiple ACT projects simultaneously
- Need auto-restart on file changes
- Want centralized logging across projects
- Deploying locally for testing
- Server keeps crashing and you need persistence

### Use `npm run dev` When:
- Quick one-off testing
- Actively debugging with console logs
- Only working on Empathy Ledger
- Making rapid code changes and want instant feedback

---

## Setup (One-Time)

### 1. Install PM2 Globally

```bash
npm install -g pm2
```

### 2. Create Empathy Ledger PM2 Config

The global ecosystem config already has Empathy Ledger configured at:
`/Users/benknight/act-global-infrastructure/deployment/ecosystem.config.cjs`

**Empathy Ledger Config:**
```javascript
{
  name: 'empathy-ledger',
  script: '/Users/benknight/.nvm/versions/node/v20.19.3/bin/npm',
  args: 'run dev',
  cwd: '/Users/benknight/Code/empathy-ledger-v2',
  env: {
    PORT: 3001,  // Note: Different from standalone (3030)
    NODE_ENV: 'development',
  },
  autorestart: true,
  max_restarts: 10,
  min_uptime: '10s',
}
```

---

## Usage Patterns

### Pattern 1: Single Project (Empathy Ledger Only)

**Start Server:**
```bash
cd /Users/benknight/Code/empathy-ledger-v2
pm2 start npm --name "empathy-ledger-solo" -- run dev
```

**Check Status:**
```bash
pm2 list
```

**View Logs:**
```bash
pm2 logs empathy-ledger-solo
```

**Restart After Code Changes:**
```bash
pm2 restart empathy-ledger-solo
```

**Stop Server:**
```bash
pm2 stop empathy-ledger-solo
pm2 delete empathy-ledger-solo  # Remove from PM2
```

---

### Pattern 2: Full ACT Ecosystem

**Start All Projects (Recommended):**
```bash
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh start
```

This starts:
- ACT Regenerative Studio (port 3002)
- Empathy Ledger (port 3001)
- JusticeHub (port 3003)
- The Harvest Website (port 3004)
- ACT Farm (port 3005)
- ACT Placemat (port 3999)

**Restart All:**
```bash
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh restart
```

**Stop All:**
```bash
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh stop
```

**View All Logs:**
```bash
pm2 logs
```

**Monitor All Projects:**
```bash
pm2 monit
```

---

### Pattern 3: Fix "Address Already in Use" Errors

**Problem:** Port 3030 (or any port) is occupied

**Solution 1: Kill Process and Restart with PM2**
```bash
# Find and kill process on port
lsof -ti :3030 | xargs kill -9

# Start with PM2 for auto-recovery
pm2 start npm --name "empathy-ledger-solo" -- run dev
```

**Solution 2: Use PM2 Restart (Handles Cleanup)**
```bash
pm2 restart empathy-ledger
```

**Solution 3: Use Ecosystem Script**
```bash
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh restart
```

---

## Troubleshooting

### Server Won't Start

**Check PM2 Status:**
```bash
pm2 list
pm2 logs empathy-ledger --lines 50
```

**Check Port Availability:**
```bash
lsof -i :3030
lsof -i :3001  # If using ecosystem config
```

**Force Kill and Restart:**
```bash
pm2 delete empathy-ledger
lsof -ti :3030 | xargs kill -9
pm2 start npm --name "empathy-ledger-solo" -- run dev
```

### Server Crashes Repeatedly

**Check Max Restarts:**
```bash
pm2 logs empathy-ledger --err --lines 100
```

If you see "max restarts reached", there's likely a code error. Check the error logs:
```bash
cat /Users/benknight/act-global-infrastructure/deployment/logs/empathy-ledger-error.log
```

**Increase Max Restarts (if needed):**
Edit ecosystem config and increase `max_restarts: 10` → `max_restarts: 20`

### Code Changes Not Reflecting

**PM2 Doesn't Auto-Reload by Default**

Option 1: Restart manually after changes:
```bash
pm2 restart empathy-ledger
```

Option 2: Enable watch mode (not recommended for Next.js):
```bash
pm2 start npm --name "empathy-ledger-solo" --watch -- run dev
```

Option 3: Use `npm run dev` directly for active development

---

## Best Practices

### Development Workflow

1. **Morning Startup:**
   ```bash
   /Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh start
   ```

2. **Check All Running:**
   ```bash
   pm2 list
   ```

3. **Work on Code (Auto-Restart Handles Crashes)**

4. **View Logs When Needed:**
   ```bash
   pm2 logs empathy-ledger
   ```

5. **End of Day:**
   ```bash
   /Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh stop
   ```

### Testing Workflow

1. **Make Code Changes**

2. **Restart Server:**
   ```bash
   pm2 restart empathy-ledger
   ```

3. **Wait 3-5 Seconds for Startup**

4. **Test API/Feature**

5. **Check Logs for Errors:**
   ```bash
   pm2 logs empathy-ledger --lines 20
   ```

---

## Integration with Existing Tools

### Works With Supabase Local Dev

```bash
# Start Supabase
npx supabase start

# Start Empathy Ledger with PM2
pm2 start npm --name "empathy-ledger-solo" -- run dev

# Both run together
pm2 list
```

### Works With Database Migrations

```bash
# Run migration
npx supabase db push

# Restart server to load new schema
pm2 restart empathy-ledger
```

### Works With Testing Scripts

```bash
# Server already running via PM2
pm2 list

# Run test script
bash test-syndication.sh

# Logs show the requests
pm2 logs empathy-ledger --lines 30
```

---

## PM2 Cheat Sheet

| Command | Purpose |
|---------|---------|
| `pm2 start <script>` | Start a process |
| `pm2 list` | Show all processes |
| `pm2 logs` | View all logs (live) |
| `pm2 logs <name>` | View specific process logs |
| `pm2 restart <name>` | Restart process |
| `pm2 stop <name>` | Stop process |
| `pm2 delete <name>` | Remove from PM2 |
| `pm2 monit` | Open monitoring dashboard |
| `pm2 flush` | Clear all logs |
| `pm2 save` | Save current process list |
| `pm2 startup` | Enable PM2 on system boot |

---

## Automation Recommendations

### Create Project-Specific Script

Add to `package.json`:

```json
{
  "scripts": {
    "dev": "next dev -p 3030",
    "dev:pm2": "pm2 start npm --name empathy-ledger-solo -- run dev",
    "dev:restart": "pm2 restart empathy-ledger-solo",
    "dev:stop": "pm2 stop empathy-ledger-solo && pm2 delete empathy-ledger-solo",
    "dev:logs": "pm2 logs empathy-ledger-solo"
  }
}
```

**Usage:**
```bash
npm run dev:pm2        # Start with PM2
npm run dev:restart    # Restart
npm run dev:logs       # View logs
npm run dev:stop       # Stop and remove
```

### Create Alias in Shell (.zshrc or .bashrc)

```bash
# Empathy Ledger shortcuts
alias el-start='pm2 start npm --name empathy-ledger-solo -- run dev'
alias el-restart='pm2 restart empathy-ledger-solo'
alias el-stop='pm2 stop empathy-ledger-solo && pm2 delete empathy-ledger-solo'
alias el-logs='pm2 logs empathy-ledger-solo'
alias el-status='pm2 list | grep empathy'

# ACT Ecosystem shortcuts
alias act-start='/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh start'
alias act-restart='/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh restart'
alias act-stop='/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh stop'
alias act-logs='pm2 logs'
alias act-status='pm2 list'
```

Reload shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

**Usage:**
```bash
el-start      # Start Empathy Ledger
el-restart    # Restart
el-logs       # View logs
el-stop       # Stop
```

---

## ACT Ecosystem Deployment Script

**Location:** `/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh`

**Commands:**
```bash
./deploy-act-ecosystem.sh start    # Start all projects
./deploy-act-ecosystem.sh stop     # Stop all projects
./deploy-act-ecosystem.sh restart  # Restart all projects
./deploy-act-ecosystem.sh status   # Show status
./deploy-act-ecosystem.sh logs     # Show all logs
./deploy-act-ecosystem.sh monitor  # Open PM2 dashboard
```

**Features:**
- ✅ Starts all 6 ACT projects
- ✅ Auto-opens sites in Chrome (via AppleScript)
- ✅ Centralized logging to `/Users/benknight/act-global-infrastructure/deployment/logs/`
- ✅ Auto-restart on crashes
- ✅ Color-coded status output

**Ports:**
- ACT Studio: 3002
- Empathy Ledger: 3030
- JusticeHub: 3003
- Harvest: 3004
- ACT Farm: 3005
- Placemat: 3999

**Note:** All projects use consistent ports across standalone and ecosystem modes

---

## Common Scenarios

### Scenario 1: "Address Already in Use" Error

**User sees:**
```
Error: listen EADDRINUSE: address already in use :::3030
```

**Claude Response:**
```bash
# Kill existing process
lsof -ti :3030 | xargs kill -9

# Start with PM2 for reliability
pm2 start npm --name "empathy-ledger-solo" -- run dev

# Verify running
pm2 list
```

### Scenario 2: Server Needs Restart After Schema Fix

**User says:** "I fixed the schema, now restart the server"

**Claude Response:**
```bash
# If using PM2
pm2 restart empathy-ledger

# If using ecosystem
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh restart

# Wait for startup
sleep 5

# Test
curl http://localhost:3030
```

### Scenario 3: Testing Syndication System

**User says:** "Test the syndication API"

**Claude Response:**
```bash
# Ensure server is running
pm2 list | grep empathy || pm2 start npm --name "empathy-ledger-solo" -- run dev

# Wait for startup
sleep 5

# Run test
bash test-syndication.sh

# Check logs if errors
pm2 logs empathy-ledger-solo --lines 50
```

---

## Integration with Development Workflow

### Sprint Development Cycle

**Sprint Start:**
```bash
act-start  # Start all ACT projects
```

**During Development:**
```bash
# Make code changes
# ...

# Restart to test
pm2 restart empathy-ledger

# View logs
pm2 logs empathy-ledger
```

**End of Sprint:**
```bash
# Stop all projects
act-stop

# Or keep running if continuing tomorrow
pm2 save  # Save current state
```

---

## Log Management

**View Live Logs:**
```bash
pm2 logs empathy-ledger
```

**View Last N Lines:**
```bash
pm2 logs empathy-ledger --lines 100
```

**View Error Logs Only:**
```bash
pm2 logs empathy-ledger --err
```

**Clear All Logs:**
```bash
pm2 flush
```

**Log File Locations (Ecosystem):**
```
/Users/benknight/act-global-infrastructure/deployment/logs/empathy-ledger-out.log
/Users/benknight/act-global-infrastructure/deployment/logs/empathy-ledger-error.log
```

---

## When Claude Should Use This Skill

**Trigger Phrases:**
- "Start the dev server"
- "Restart the server"
- "Address already in use"
- "Port 3030 is busy"
- "Server won't start"
- "Test the API" (ensure server running first)
- "Deploy locally"
- "Run all ACT projects"

**Actions Claude Should Take:**

1. **Check if server is running:**
   ```bash
   pm2 list | grep empathy
   ```

2. **If not running, start it:**
   ```bash
   pm2 start npm --name "empathy-ledger-solo" -- run dev
   ```

3. **If running but needs restart:**
   ```bash
   pm2 restart empathy-ledger-solo
   ```

4. **Wait for startup:**
   ```bash
   sleep 5
   ```

5. **Verify responsive:**
   ```bash
   curl -s http://localhost:3030 > /dev/null && echo "✅ Server running" || echo "❌ Server not responding"
   ```

6. **Proceed with testing/development**

---

## Success Criteria

After following this skill, user should:
- ✅ Have server running reliably
- ✅ Be able to restart server easily
- ✅ No more "address already in use" errors
- ✅ Have access to centralized logs
- ✅ Know how to use PM2 for all ACT projects

---

**This skill eliminates the "local deployment shit fight" by providing a consistent, reliable, PM2-based workflow that aligns with the ACT ecosystem deployment strategy.**
