# PM2 Commands Reference

## Single Project Commands

```bash
# Start Empathy Ledger
pm2 start npm --name "empathy-ledger" -- run dev

# Restart
pm2 restart empathy-ledger

# Stop
pm2 stop empathy-ledger

# View logs
pm2 logs empathy-ledger

# Delete from PM2
pm2 delete empathy-ledger
```

## ACT Ecosystem Commands

```bash
# Start all projects
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh start

# Restart all
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh restart

# Stop all
/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh stop

# View all logs
pm2 logs

# Monitor dashboard
pm2 monit
```

## PM2 Cheat Sheet

| Command | Purpose |
|---------|---------|
| `pm2 list` | Show all processes |
| `pm2 logs` | View all logs (live) |
| `pm2 logs <name>` | View specific logs |
| `pm2 restart <name>` | Restart process |
| `pm2 stop <name>` | Stop process |
| `pm2 delete <name>` | Remove from PM2 |
| `pm2 monit` | Monitoring dashboard |
| `pm2 flush` | Clear all logs |
| `pm2 save` | Save process list |

## Port Configuration

| Project | Port |
|---------|------|
| Empathy Ledger | 3030 |
| ACT Studio | 3002 |
| JusticeHub | 3003 |
| Harvest | 3004 |
| ACT Farm | 3005 |
| Placemat | 3999 |

## Troubleshooting

### Address Already in Use
```bash
lsof -ti :3030 | xargs kill -9
pm2 start npm --name "empathy-ledger" -- run dev
```

### Check Port Availability
```bash
lsof -i :3030
```

### Force Kill and Restart
```bash
pm2 delete empathy-ledger
lsof -ti :3030 | xargs kill -9
pm2 start npm --name "empathy-ledger" -- run dev
```

### View Error Logs
```bash
pm2 logs empathy-ledger --err --lines 100
```

## Shell Aliases (add to ~/.zshrc)

```bash
alias el-start='pm2 start npm --name empathy-ledger -- run dev'
alias el-restart='pm2 restart empathy-ledger'
alias el-stop='pm2 stop empathy-ledger && pm2 delete empathy-ledger'
alias el-logs='pm2 logs empathy-ledger'
alias act-start='/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh start'
alias act-stop='/Users/benknight/act-global-infrastructure/deployment/scripts/deploy-act-ecosystem.sh stop'
```
