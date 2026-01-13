# WordPress Skills Installation Guide

Quick-start guide to install and use the WordPress development skills with Claude Code.

---

## Overview

The WordPress Skills package provides Claude Code with comprehensive WordPress development capabilities:

- **18 specialized skills** for all aspects of WordPress development
- **3 slash commands** for common workflows (`/wp-setup`, `/wp-audit`, `/wp-launch`)
- **Automated scripts** for SEO audits, visual QA, and white-labeling
- **Docker templates** for instant local development
- **Theme scaffolding** with demo content system

---

## Quick Install

### Option 1: Clone from GitHub

```bash
# Clone the WordPress skills repository
cd /root/.claude/skills
git clone https://github.com/CrazySwami/wordpress-dev-skills.git

# Or clone individual skills
git clone https://github.com/CrazySwami/wordpress-dev-skills/wp-orchestrator
git clone https://github.com/CrazySwami/wordpress-dev-skills/wp-docker
# ... etc
```

### Option 2: Manual Copy

Copy the skills directory structure to your Claude Code skills folder:

```
~/.claude/skills/
├── wp-orchestrator/       # Master coordinator
├── wp-docker/             # Docker environment
├── wp-playground/         # WordPress Playground
├── wordpress-dev/         # Development standards
├── wordpress-admin/       # Site management
├── seo-optimizer/         # SEO auditing
├── visual-qa/             # Screenshot testing
├── brand-guide/           # Brand documentation
├── white-label/           # Admin branding
├── gsap-animations/       # Animation guide
├── wp-performance/        # Speed optimization
└── form-testing/          # Form & email testing
```

---

## Required Dependencies

### System Requirements

```bash
# Python 3.8+ with pip
python3 --version
pip3 --version

# Node.js 18+ with npm
node --version
npm --version

# Docker & Docker Compose
docker --version
docker-compose --version

# Git
git --version

# GitHub CLI (optional but recommended)
gh --version
```

### Python Packages

```bash
# For visual-qa screenshots
pip3 install playwright
playwright install chromium

# For SEO auditing
pip3 install requests beautifulsoup4

# For brand extraction
pip3 install cssutils pillow
```

### Node Packages (for E2E testing)

```bash
# Install Playwright for testing
npm install -D @playwright/test
npx playwright install
```

---

## Skill Configuration

### Global CLAUDE.md Setup

Add to your `~/.claude/CLAUDE.md`:

```markdown
## WordPress Development Skills

A complete WordPress automation toolkit is installed. Use these skills for any WordPress project:

### Slash Commands (Quick Actions)

| Command | What It Does |
|---------|--------------|
| `/wp-setup` | Set up a new WordPress site with Docker, plugins, white-labeling |
| `/wp-audit` | Run comprehensive site audit (SEO, visual, performance, security) |
| `/wp-launch` | Pre-launch checklist and handoff documentation |

### Available Skills

| Skill | Use When |
|-------|----------|
| **wp-orchestrator** | Coordinating WordPress projects |
| **wp-docker** | Setting up Docker WordPress environments |
| **wordpress-dev** | Writing WordPress code (CPT, hooks, security) |
| **wordpress-admin** | Managing WordPress content via WP-CLI/REST |
| **seo-optimizer** | Auditing SEO (Yoast/Rank Math) |
| **visual-qa** | Screenshot testing at multiple viewports |
| **brand-guide** | Documenting brand guidelines |
| **white-label** | Branding admin for client handoff |
| **gsap-animations** | GSAP/ScrollTrigger best practices |
| **wp-performance** | Core Web Vitals, caching, optimization |

### When to Use WordPress Skills

- **"Set up a new WordPress site"** → Use `/wp-setup` or wp-docker skill
- **"Audit this site"** → Use `/wp-audit`
- **"Check SEO"** → Use seo-optimizer skill
- **"Take screenshots"** → Use visual-qa skill
- **"White label for client"** → Use white-label skill
```

### Slash Commands Setup

Create the slash command files in `~/.claude/commands/`:

**wp-setup.md:**
```markdown
---
name: wp-setup
description: Set up a new WordPress site with Docker, install plugins, configure white-labeling
---

Use the wp-orchestrator skill to set up a new WordPress project.

1. Run discovery interview to gather requirements
2. Create Docker environment with wp-docker skill
3. Install and configure required plugins
4. Apply white-label settings for client admin
5. Generate todo list for remaining setup tasks
```

**wp-audit.md:**
```markdown
---
name: wp-audit
description: Comprehensive WordPress site audit - SEO, performance, security, visual QA
---

Use the wp-orchestrator skill to run a comprehensive site audit.

Run these audits in parallel:
1. SEO audit (seo-optimizer skill)
2. Visual QA screenshots (visual-qa skill)
3. Performance check (wp-performance skill)
4. Security review (white-label skill for settings)

Compile results and generate action items.
```

**wp-launch.md:**
```markdown
---
name: wp-launch
description: Pre-launch checklist and final deployment preparation for WordPress sites
---

Use the wp-orchestrator skill to prepare for launch.

Pre-launch checklist:
1. All pages have content
2. SEO configured for all pages
3. Forms tested and working
4. Performance optimized
5. Security hardened
6. Backups configured
7. Analytics installed
8. Admin white-labeled
9. Documentation prepared
10. Client training complete
```

---

## Testing Installation

### Verify Skills Are Loaded

In Claude Code, type:
```
What WordPress skills do you have available?
```

Expected response should list all installed skills.

### Test Visual QA

```bash
# Test screenshot script
python3 ~/.claude/skills/visual-qa/screenshot.py \
  --url https://wordpress.org \
  --output /tmp/test-screenshots

# Check output
ls -la /tmp/test-screenshots
```

### Test SEO Audit

```bash
# Test SEO audit script
python3 ~/.claude/skills/seo-optimizer/audit.py \
  --base-url https://wordpress.org \
  --json
```

### Test Docker Setup

```bash
# Create test project
mkdir -p /tmp/wp-test
cd /tmp/wp-test

# Copy Docker template
cp ~/.claude/skills/wp-docker/templates/docker-compose.yml .
cp ~/.claude/skills/wp-docker/templates/.env.example .env

# Start WordPress
docker-compose up -d

# Verify running
docker ps | grep wordpress
curl -I http://localhost:8080

# Cleanup
docker-compose down -v
```

---

## Project Setup Workflow

### 1. Create New Project

```bash
mkdir -p ~/repos/client-project
cd ~/repos/client-project
```

### 2. Initialize with Claude Code

Open Claude Code and say:
```
I want to set up a new WordPress project for a real estate company.
Use the /wp-setup command.
```

### 3. Follow Discovery Interview

Claude will ask about:
- Business profile
- Brand assets
- Site structure
- Technical requirements

### 4. Docker Environment Created

Claude creates:
- `docker-compose.yml`
- `.env` with project settings
- Theme scaffold

### 5. Development Workflow

```
Edit theme files → See changes live →
Run visual QA → Fix issues →
Export demo content → Package theme →
Push to GitHub → Deploy via WP Pusher
```

---

## Directory Structure

After setup, your project should look like:

```
~/repos/client-project/
├── docker-compose.yml       # Docker WordPress stack
├── .env                     # Environment variables
├── uploads.ini              # PHP upload config
├── client-theme/            # WordPress theme
│   ├── style.css
│   ├── functions.php
│   ├── header.php
│   ├── footer.php
│   ├── index.php
│   ├── page-*.php           # Page templates
│   ├── single-*.php         # Single templates
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── inc/
│   │   ├── setup-wizard.php
│   │   ├── admin-dashboard.php
│   │   └── theme-demo-content.php
│   ├── tests/               # Playwright tests
│   ├── demo-content.json    # Exportable content
│   └── README.md
├── screenshots/             # Visual QA output
└── CLAUDE.md                # Project instructions
```

---

## Common Issues

### "Permission denied" on scripts

```bash
chmod +x ~/.claude/skills/*/scripts/*.sh
chmod +x ~/.claude/skills/*/scripts/*.py
```

### Playwright not installed

```bash
pip3 install playwright
playwright install chromium
playwright install-deps
```

### Docker containers won't start

```bash
# Check if ports are in use
ss -tlnp | grep 8080

# Check Docker logs
docker-compose logs

# Reset Docker
docker-compose down -v
docker-compose up -d
```

### WP-CLI not found in container

```bash
# Most Docker templates include WP-CLI
# If not, install in container:
docker exec -it wordpress bash
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
mv wp-cli.phar /usr/local/bin/wp
```

### GitHub authentication

```bash
# Authenticate with GitHub CLI
gh auth login

# Or use personal access token
git config --global credential.helper store
```

---

## Updating Skills

### Pull Latest from GitHub

```bash
cd ~/.claude/skills/wordpress-dev-skills
git pull origin main
```

### Manual Update

Replace skill folders with updated versions from the repository.

---

## Support

- **GitHub Issues**: https://github.com/CrazySwami/wordpress-dev-skills/issues
- **Documentation**: See individual skill SKILL.md files
- **Workflow Guide**: See WORKFLOW.md in wp-orchestrator

---

**Version**: 1.0
**Last Updated**: December 29, 2025
