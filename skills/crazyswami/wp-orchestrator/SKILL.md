---
name: wp-orchestrator
description: Master WordPress project orchestrator - coordinates all WordPress skills for complete site setup, audit, and optimization. Use for new project setup, site audits, or comprehensive reviews. Runs interview phases and manages todo lists.
allowed-tools: Read, Write, Edit, Bash, Task, Glob, Grep, WebFetch, AskUserQuestion, TodoWrite
---

# WordPress Project Orchestrator

Master skill that coordinates all WordPress development skills for comprehensive project management.

**See Also:** [WORKFLOW.md](./WORKFLOW.md) - Complete end-to-end development workflow documentation

## Quick Start Slash Commands

| Command | Purpose |
|---------|---------|
| `/wp-setup` | Set up a new WordPress site with Docker, plugins, white-labeling |
| `/wp-audit` | Run comprehensive site audit (SEO, visual, performance, security) |
| `/wp-launch` | Pre-launch checklist and handoff documentation |

## Complete Development Lifecycle

```
1. Discovery & Branding → 2. Environment Setup → 3. Theme Development
       ↓                        ↓                       ↓
   brand-guide              wp-docker              wordpress-dev
                                                   gsap-animations
       ↓                        ↓                       ↓
4. Content & SEO → 5. Testing & QA → 6. Packaging & Deploy
       ↓                 ↓                    ↓
  wordpress-admin    visual-qa           GitHub + WP Pusher
  seo-optimizer      form-testing        demo-content.json
                     E2E tests           theme zip
       ↓                 ↓                    ↓
7. White-Label → 8. Client Handoff
       ↓                 ↓
  white-label       Documentation
  ASE + Branda      Training
```

## Environment Detection

The orchestrator automatically detects your WordPress environment:

### Docker Environment
```bash
# Check for docker-compose.yml with WordPress
if [ -f docker-compose.yml ] && grep -q wordpress docker-compose.yml; then
    echo "Docker WordPress detected"
fi

# Check running containers
docker ps | grep wordpress
```

### WordPress Playground
```bash
# Check for Playground blueprints
if [ -f blueprint.json ] || [ -d blueprints/ ]; then
    echo "Playground environment detected"
fi

# Run Playground with blueprint
npx @wp-playground/cli server --blueprint=./blueprint.json
```

### Standard WordPress
```bash
# Check for wp-config.php
if [ -f wp-config.php ]; then
    echo "Standard WordPress installation detected"
fi
```

## Available Skills

| Skill | Purpose | Use When |
|-------|---------|----------|
| **wordpress-dev** | Coding standards, CPT, security, performance | Writing WordPress code |
| **wordpress-admin** | Site management, WP-CLI, REST API | Managing content, settings |
| **seo-optimizer** | Yoast/Rank Math audit, keywords, meta | SEO review and fixes |
| **visual-qa** | Screenshot testing, responsive QA | After CSS/template changes |
| **brand-guide** | Brand documentation | Starting new project |
| **white-label** | Admin branding with ASE + Branda | Client site setup |
| **gsap-animations** | GSAP best practices, accessibility | Implementing animations |
| **wp-performance** | Speed optimization, Core Web Vitals | Performance issues |
| **wp-docker** | Docker Compose environment | Local development |
| **wp-playground** | WordPress Playground blueprints | Testing and demos |

---

## Project Phases

### Phase 1: Discovery Interview

Ask the user these questions to understand the project:

```markdown
## Project Discovery

1. **Project Type**
   - New site build?
   - Existing site optimization?
   - Site audit?
   - Specific feature implementation?

2. **Site Information**
   - URL (staging/production)
   - WordPress version
   - Theme (custom, child, builder?)
   - Hosting environment (Docker local, shared, VPS, managed?)

3. **Requirements**
   - What pages are needed?
   - Custom post types?
   - Forms (contact, inquiry)?
   - E-commerce?
   - Multilingual?

4. **Brand**
   - Do you have brand guidelines?
   - Logo files available?
   - Color palette defined?
   - Typography chosen?

5. **SEO Requirements**
   - Focus keywords identified?
   - Existing content to optimize?
   - Google Analytics/Search Console connected?

6. **Performance Goals**
   - Target PageSpeed score?
   - Core Web Vitals requirements?
   - CDN preferences?

7. **Client Handoff**
   - Need white-labeled admin?
   - Training documentation needed?
   - Which admin features to expose?
```

### Phase 2: Initial Audit

Run these checks on existing sites:

#### Plugin Check
```bash
# Via WP-CLI in Docker
docker exec wordpress-container wp plugin list --format=table

# Check for required plugins
REQUIRED="admin-site-enhancements litespeed-cache wordpress-seo ewww-image-optimizer"
```

#### SEO Audit
```bash
# Run SEO optimizer
python3 /root/.claude/skills/seo-optimizer/audit.py --base-url https://site.com --json
```

#### Visual QA
```bash
# Take screenshots of all pages
python3 /root/.claude/skills/visual-qa/screenshot.py --all --base-url https://site.com
```

#### Performance Check
```bash
# Check PageSpeed (requires API key or use web tool)
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://site.com&strategy=mobile"
```

### Phase 3: Todo List Generation

Based on audit results, generate comprehensive todo list:

```markdown
## Site Setup Checklist

### Foundation
- [ ] WordPress core updated
- [ ] Theme installed and configured
- [ ] Child theme created (if needed)
- [ ] Required plugins installed

### Plugins to Install
- [ ] Admin and Site Enhancements (ASE) - Admin cleanup, security
- [ ] Branda - White labeling, login customization
- [ ] LiteSpeed Cache - Performance
- [ ] Yoast SEO - SEO optimization
- [ ] WP Mail SMTP - Email delivery
- [ ] Solid Security - Additional security
- [ ] EWWW Image Optimizer - Image compression
- [ ] WP Activity Log - Audit logging
- [ ] Site Kit by Google - Analytics integration
- [ ] ManageWP Worker - Remote management
- [ ] Instant Images - Stock photos
- [ ] Admin Menu Editor - Menu organization (optional)

### Pages to Create
- [ ] Home
- [ ] About
- [ ] Services/Portfolio
- [ ] Contact
- [ ] Privacy Policy
- [ ] Terms of Service

### SEO Setup
- [ ] Focus keyword for each page
- [ ] Meta descriptions (120-160 chars)
- [ ] Featured images with ALT text
- [ ] XML sitemap generated
- [ ] Robots.txt configured
- [ ] Google Search Console connected

### Performance
- [ ] Image optimization configured
- [ ] Caching enabled
- [ ] CDN configured
- [ ] Lazy loading enabled
- [ ] Minification enabled
- [ ] PageSpeed score >80

### Security
- [ ] Login URL changed
- [ ] XML-RPC disabled
- [ ] 2FA enabled for admins
- [ ] Automatic updates configured
- [ ] Backup solution in place

### White Label (Client Sites) - Using white-label skill
- [ ] Login page customized (Branda: logo, colors, background)
- [ ] Admin bar branded (Branda: hide WP logo, custom logo)
- [ ] "Howdy" replaced (Branda: custom greeting)
- [ ] Admin footer customized (ASE or Branda)
- [ ] Dashboard widgets hidden (ASE)
- [ ] Admin menu organized (Admin Menu Editor)
- [ ] Custom login URL set (ASE: /client-login)
- [ ] XML-RPC disabled (ASE)
- [ ] Author slugs obfuscated (ASE)

### Visual QA
- [ ] Desktop screenshots reviewed
- [ ] Tablet screenshots reviewed
- [ ] Mobile screenshots reviewed
- [ ] Animations working
- [ ] No layout issues
- [ ] Forms functional

### Pre-Launch
- [ ] All pages have content
- [ ] Forms tested
- [ ] 404 page configured
- [ ] Favicon uploaded
- [ ] Social sharing images set
- [ ] Analytics tracking verified
```

---

## Orchestration Commands

### New Project Setup

When user says: "Set up a new WordPress project"

1. **Run Discovery Interview**
   - Use AskUserQuestion tool for project requirements
   - Document brand, pages, features needed

2. **Create Todo List**
   - Generate comprehensive TodoWrite list
   - Break into phases (Foundation → Content → SEO → Performance → Launch)

3. **Plugin Installation Guidance**
   - List plugins from recommended-plugins.md
   - Provide installation order

4. **Theme Setup**
   - Guide through theme installation
   - Configure initial settings

5. **ASE Configuration**
   - Apply security settings
   - Configure white labeling

### Site Audit

When user says: "Audit this WordPress site"

1. **Run All Audits in Parallel** (using Task tool with Haiku agents)
   - SEO audit agent
   - Visual QA agent
   - Performance check agent
   - Security review agent

2. **Compile Results**
   - Aggregate findings
   - Prioritize issues

3. **Generate Action Plan**
   - Create TodoWrite list of fixes
   - Estimate effort (simple/moderate/complex)

### Performance Optimization

When user says: "Optimize site performance"

1. **Baseline Measurement**
   - Run PageSpeed test
   - Record current scores

2. **Image Audit**
   - Check image sizes
   - Identify unoptimized images

3. **Caching Configuration**
   - Configure LiteSpeed Cache
   - Set up browser caching

4. **Asset Optimization**
   - Review CSS/JS loading
   - Implement deferring

5. **Re-test**
   - Run PageSpeed again
   - Compare results

---

## Parallel Agent Patterns

### Multi-Page Audit

```python
# Launch parallel Haiku agents for page audits
agents = [
    Task(subagent_type="Explore", prompt="Audit home page SEO and visual state"),
    Task(subagent_type="Explore", prompt="Audit about page SEO and visual state"),
    Task(subagent_type="Explore", prompt="Audit portfolio page SEO and visual state"),
    Task(subagent_type="Explore", prompt="Audit contact page SEO and visual state"),
]
# Run all in parallel using model="haiku"
```

### Full Site Review

```python
# Parallel skill execution
agents = [
    Task(prompt="Run SEO audit using seo-optimizer skill", model="haiku"),
    Task(prompt="Take visual QA screenshots using visual-qa skill", model="haiku"),
    Task(prompt="Check performance using wp-performance skill", model="haiku"),
    Task(prompt="Review security using ase-config skill", model="haiku"),
]
```

---

## Interview Templates

### Client Kickoff Interview

```markdown
# Project Kickoff Questions

## Business Understanding
1. What does your business do?
2. Who is your target audience?
3. What are your main competitors?
4. What makes you different?

## Website Goals
1. What is the primary goal of this website?
   - Lead generation
   - E-commerce sales
   - Information/portfolio
   - Brand awareness

2. What actions should visitors take?
3. How will you measure success?

## Content
1. Do you have existing content to migrate?
2. Will you provide content or need copywriting?
3. Do you have professional photos?
4. What pages do you need?

## Design Preferences
1. Any websites you like the look of?
2. Brand colors and fonts established?
3. Logo files available?
4. Design style preference?
   - Minimal
   - Bold
   - Corporate
   - Creative

## Technical Requirements
1. Need any integrations?
   - CRM
   - Email marketing
   - Booking system
   - Payment processing

2. Expected traffic volume?
3. Need multilingual support?
4. Special functionality needed?

## Timeline & Budget
1. Deadline for launch?
2. Ongoing maintenance needed?
3. Budget constraints?
```

### Site Audit Interview

```markdown
# Site Audit Questions

1. What issues are you experiencing?
2. When did you last update WordPress/plugins?
3. Have you noticed performance problems?
4. Any specific pages with issues?
5. Are you tracking analytics currently?
6. What is your current hosting?
7. Do you have backups configured?
8. Who has admin access?
```

---

## Reporting Templates

### Audit Report

```markdown
# WordPress Site Audit Report

**Site**: [URL]
**Date**: [Date]
**Auditor**: Claude Code

## Executive Summary
[2-3 sentence overview]

## Scores
| Category | Score | Target |
|----------|-------|--------|
| SEO | X/100 | 80+ |
| Performance | X/100 | 80+ |
| Accessibility | X/100 | 90+ |
| Security | X/10 | 10/10 |

## Critical Issues
1. [Issue 1]
2. [Issue 2]

## Recommendations

### High Priority
- [ ] Fix [issue]
- [ ] Implement [feature]

### Medium Priority
- [ ] Optimize [aspect]
- [ ] Configure [setting]

### Low Priority
- [ ] Consider [improvement]

## Next Steps
1. [Action 1]
2. [Action 2]
```

### Handoff Documentation

```markdown
# Website Handoff Documentation

## Login Information
- **Admin URL**: [URL]/secure-login
- **Username**: [provided separately]
- **Password**: [provided separately]

## How to Edit Content

### Editing Pages
1. Log in to the admin area
2. Click "Pages" in the left menu
3. Find the page you want to edit
4. Click "Edit"
5. Make your changes
6. Click "Update" to save

### Adding Blog Posts
1. Click "Posts" → "Add New"
2. Enter title and content
3. Set featured image
4. Add categories/tags
5. Click "Publish"

### Uploading Images
1. Click "Media" → "Add New"
2. Drop files or click to upload
3. Images are automatically optimized

## SEO Guidelines
- Each page should have a focus keyword
- Meta descriptions should be 120-160 characters
- Featured images should have ALT text

## Support
Contact [Your Agency] at [email] for assistance.
```

---

## Workflow Integration

### With Hooks

The orchestrator can trigger other skills automatically:

```yaml
# Example workflow configuration
on_new_project:
  - run: discovery_interview
  - run: wordpress-dev/scaffold_theme
  - run: ase-config/apply_defaults
  - run: seo-optimizer/initial_setup

on_pre_launch:
  - run: seo-optimizer/audit
  - run: visual-qa/full_site
  - run: wp-performance/speed_test
  - run: generate_report
```

### With Claude Code Slash Commands

```bash
# Register as skill
/wp-setup       # Start new project setup
/wp-audit       # Run comprehensive audit
/wp-optimize    # Performance optimization
/wp-seo         # SEO review and fixes
/wp-visual      # Visual QA screenshots
```

---

## Theme Packaging & Distribution

### Create Theme Zip

```bash
cd /path/to/project

# Remove old zips
rm -f theme-name-*.zip

# Create versioned zip (exclude dev files)
zip -r theme-name-1.0.0.zip theme-name \
  -x "*.git*" \
  -x "*node_modules*" \
  -x "*.DS_Store" \
  -x "*tests/*" \
  -x "*.env*"
```

### Export Demo Content

Before packaging, export current content:
1. WordPress Admin → Theme Settings → Demo Content
2. Click "Export Demo Content"
3. Verify `demo-content.json` is updated in theme folder

### GitHub Repository Setup

```bash
cd /path/to/theme

# Initialize and push
git init
git add .
git commit -m "Initial theme release v1.0.0"
gh repo create theme-name --public --source=. --push

# Push updates
git add .
git commit -m "feat: description of changes v1.0.1"
git push origin main
```

### WP Pusher Deployment (Production)

**Install WP Pusher on production site:**
1. Plugins → Add New → "WP Pusher" → Install & Activate
2. WP Pusher → Install Theme
3. Enter repository: `username/theme-name`
4. Branch: `main`
5. Click "Install Theme"

**Pull Updates:**
- WP Pusher → Themes → Click "Update Theme"

**Auto-Deploy (Optional):**
1. WP Pusher → Themes → Theme Settings
2. Enable "Push-to-Deploy"
3. Copy webhook URL
4. GitHub repo → Settings → Webhooks → Add webhook
5. Paste URL, select "push" events

---

## Demo Content System

### What Gets Exported

| Data | Source |
|------|--------|
| Pages | Title, content, template, slug |
| Properties (CPT) | All fields and meta |
| Yoast SEO | Focus keyword, meta desc, SEO title |
| Featured Images | URLs for re-download |
| Theme Options | Custom settings |
| Reading Settings | Front page config |

### Import on Fresh Install

1. Activate theme
2. Setup Wizard Step 2: "Import Demo Content"
3. Or: Theme Settings → Demo Content → Import

### WP-CLI Export/Import

```bash
# Export
docker exec wordpress wp eval "print_r(csr_export_demo_content());" --allow-root

# Trigger import
docker exec wordpress wp eval "csr_import_demo_content();" --allow-root
```

---

## Quick Reference

### Common Orchestrator Commands

| User Says | Orchestrator Does |
|-----------|-------------------|
| "Set up a new WordPress site" | `/wp-setup` → Discovery interview → Docker/Playground → Install plugins |
| "Audit this site" | `/wp-audit` → Run all audit skills in parallel → Compile report |
| "Optimize performance" | Run wp-performance → Apply fixes |
| "Check SEO" | Run seo-optimizer → Show issues |
| "Take screenshots" | Run visual-qa → Analyze results |
| "White label admin" | Run white-label → Apply ASE + Branda settings |
| "Prepare for launch" | `/wp-launch` → Run all checks → Generate handoff docs |
| "Start Docker WordPress" | Copy wp-docker templates → docker-compose up |
| "Test in Playground" | Run wp-playground blueprint → Open browser |
| "Package theme for distribution" | Export demo content → Create zip → Push to GitHub |
| "Deploy to production" | Setup WP Pusher → Connect GitHub → Pull updates |

---

## Related Skills

All skills are documented at:
- `/root/.claude/skills/wordpress-dev/` - Development best practices
- `/root/.claude/skills/wordpress-admin/` - Site management
- `/root/.claude/skills/seo-optimizer/` - SEO auditing
- `/root/.claude/skills/visual-qa/` - Visual testing
- `/root/.claude/skills/brand-guide/` - Brand documentation
- `/root/.claude/skills/white-label/` - Admin white-labeling (ASE + Branda)
- `/root/.claude/skills/gsap-animations/` - Animation best practices
- `/root/.claude/skills/wp-performance/` - Performance optimization
- `/root/.claude/skills/wp-docker/` - Docker environment
- `/root/.claude/skills/wp-playground/` - WordPress Playground

Slash commands at:
- `/root/.claude/commands/wp-setup.md`
- `/root/.claude/commands/wp-audit.md`
- `/root/.claude/commands/wp-launch.md`

Plugin bundle at:
- `/root/.claude/plugins/wordpress-dev-skills/`
