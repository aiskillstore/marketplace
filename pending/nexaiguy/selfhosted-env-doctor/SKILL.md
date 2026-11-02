---
name: selfhosted-env-doctor
description: 'Safe, read-only diagnostic tool for troubleshooting self-hosted stacks, port conflicts, and service failures. Use when: Identify port conflicts between Docker containers and host services; Debug Cloudflare Tunnel configuration and credential path issues; Detect Nginx default_server collisions and syntax errors.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: selfhosted-env-doctor
compatibility: Compatible with SKILL.md-compatible agents including Claude Code and Cursor.
---

# Selfhosted Env Doctor

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/selfhosted-env-doctor). Scripts, extension source, and templates from the original package are not in this folder.

## What it does

Self-Hosted Env Doctor is a non-destructive diagnostic engine designed to identify why local services on Linux stacks (like Raspberry Pi) fail to launch. It systematically scans for port conflicts, misconfigured Nginx blocks, Cloudflare Tunnel errors, and database authentication failures without making any changes to your system.

## How it works

The skill performs a comprehensive audit across multiple layers of your infrastructure. It checks systemd unit health, validates Nginx configuration syntax, audits listening sockets against your documentation, and verifies file permissions for sensitive items like .env files. Instead of generic error messages, it provides the specific root cause and the exact command needed to fix the issue manually.

## Why use this skill

Manually debugging a broken home lab or production server is time-consuming. This skill automates the "triage" phase by cross-referencing system state with common failure patterns (like port drift or disk space exhaustion). Because it is strictly read-only, it is safe to run on critical systems where you don't want an AI accidentally modifying configuration files or restarting services without supervision.

## Supported Tools

- **Web:** NginX, Cloudflared Tunnels
- **System:** Systemd, Netstat/SS, df/du
- **Database:** PostgreSQL
- **Security:** Linux Permissions, .env audit

## When to use

- Identify port conflicts between Docker containers and host services
- Debug Cloudflare Tunnel configuration and credential path issues
- Detect Nginx default_server collisions and syntax errors
- Verify database authentication and .env file permission risks
- Audit systemd service failures and surface hidden journald errors

## Known limitations

- Cannot fix issues automatically (read-only by design).
- Requires Python 3 and local shell access.
- Does not support Docker container internal networking audits.

## Example

**Request**

My nginx service won't start after I added the new dashboard. Can you run a diagnosis on the server?

**Result**

Found 1 Critical Issue:
[Nginx] Port Conflict: Port 80 is already bound by 'apache2'.
Fix: Run `sudo systemctl stop apache2 && sudo systemctl disable apache2` or change the listen port in `/etc/nginx/sites-available/dashboard`.

## Questions

### Does this skill automatically make changes to my server configuration or files?

No, this skill is strictly read-only. It identifies the root cause of service failures and provides you with the exact command to fix it manually, ensuring you maintain full control over your server configuration.

### Which operating systems and services are compatible with Env Doctor?

This skill is optimized for Linux-based environments, including Raspberry Pi (Debian/Ubuntu), and supports diagnostic checks for Nginx, Cloudflare Tunnels, systemd, and PostgreSQL databases.

### How does this skill save me time compared to manual debugging?

Env Doctor automates the 'triage' phase of troubleshooting, instantly spotting common issues like port conflicts, disk space exhaustion, and permission errors that usually take hours of manual log-checking to find.

### What is required to get this skill up and running on my local stack?

Setup is minimal; once the skill is added to your AI agent, you simply provide the agent with the necessary read access to your terminal or logs to begin the diagnostic scan.

### What exactly is included with my purchase of the selfhosted-env-doctor skill?

Your purchase includes the full diagnostic engine, all current service modules (Nginx, Systemd, etc.), and lifetime access to any future logic updates or new service modules added to the skill.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
