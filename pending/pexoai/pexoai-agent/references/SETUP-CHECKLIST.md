# Setup Checklist

This guide covers first-time setup and environment diagnostics for the pexo-video skill.

## Quick Start

### 1. Create config file

```bash
mkdir -p ~/.pexo
cat > ~/.pexo/config << 'EOF'
PEXO_BASE_URL="https://pexo.ai"
PEXO_API_KEY="sk-<your-api-key>"
EOF
```

Get your API key at: https://pexo.ai

- If you are not logged in:
  follow the page guidance to sign up / log in first.
- If you are already logged in:
  click the top-right avatar → `API Keys` → `Create Key`, then copy the new key.

### 2. Run diagnostics

```bash
pexo-doctor.sh
```

This checks:
- Config file exists and is readable
- `PEXO_BASE_URL` and `PEXO_API_KEY` are set
- `curl`, `jq`, and `file` are installed
- Network connectivity to Pexo servers
- API key is valid (attempts to list projects)

Fix any issues reported before using other scripts.

### 3. Verify

```bash
pexo-project-list.sh
```

If this returns a JSON list (even if empty), setup is complete.

## Troubleshooting Setup Issues

### "Set PEXO_BASE_URL in ~/.pexo/config or env"

Config file is missing or doesn't contain the required variables. Create it per step 1 above.

### "Set PEXO_API_KEY in ~/.pexo/config or env"

Same as above — the API key line is missing from the config file.

### API key invalid (401 Unauthenticated)

Your API key may be expired or incorrect. Log in at https://pexo.ai to generate a new one. Replace the value in `~/.pexo/config`.

### curl, jq, or file not found

Install the missing dependency:

```bash
# macOS (file is usually preinstalled)
brew install curl jq

# Ubuntu/Debian
apt-get install -y curl jq file

# CentOS/RHEL
yum install -y curl jq file
```

### Network connectivity failure

If `pexo-doctor.sh` reports a connectivity issue:
- Check if your server can reach `pexo.ai` (e.g. `curl -I https://pexo.ai`)
- Check firewall rules for outbound HTTPS (port 443)
- If behind a proxy, configure `http_proxy`/`https_proxy` environment variables

## Environment Variables

All scripts read `~/.pexo/config` automatically. You can also override via environment variables:

| Variable | Description | Required |
|---|---|---|
| `PEXO_BASE_URL` | Pexo API base URL | Yes |
| `PEXO_API_KEY` | Your Pexo API key (starts with `sk-`) | Yes |
| `PEXO_CONFIG` | Custom path to config file (default: `~/.pexo/config`) | No |
