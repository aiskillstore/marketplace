# WordPress Development Workflow

Complete end-to-end workflow for WordPress theme development, from initial branding through deployment.

---

## Table of Contents

1. [Project Setup](#1-project-setup)
2. [Branding & Discovery](#2-branding--discovery)
3. [Theme Development](#3-theme-development)
4. [Content Management](#4-content-management)
5. [SEO Configuration](#5-seo-configuration)
6. [Visual QA & Testing](#6-visual-qa--testing)
7. [Theme Packaging](#7-theme-packaging)
8. [GitHub Deployment](#8-github-deployment)
9. [Production Sync](#9-production-sync)
10. [Client Handoff](#10-client-handoff)

---

## 1. Project Setup

### Docker Environment Setup

```bash
# Create project directory
mkdir -p /root/repos/client-project
cd /root/repos/client-project

# Copy Docker templates from wp-docker skill
cp /root/.claude/skills/wp-docker/templates/docker-compose.yml .
cp /root/.claude/skills/wp-docker/templates/uploads.ini .
cp /root/.claude/skills/wp-docker/templates/.env.example .env

# Edit .env with project details
nano .env
# Set: PROJECT_NAME, WORDPRESS_PORT, DB credentials

# Start environment
docker-compose up -d

# Verify running
docker ps | grep wordpress
```

### Theme Scaffold

```bash
# Create theme directory
mkdir -p client-theme/{assets/{css,js,images},inc,tests/e2e}

# Essential files
touch client-theme/{style.css,functions.php,header.php,footer.php,index.php}
touch client-theme/inc/{setup-wizard.php,admin-dashboard.php,theme-demo-content.php}
```

### Required Theme Files

| File | Purpose |
|------|---------|
| `style.css` | Theme metadata + custom styles |
| `functions.php` | Theme setup, CPT, enqueues |
| `header.php` | Site header, navigation |
| `footer.php` | Site footer, scripts |
| `index.php` | Main template |
| `inc/setup-wizard.php` | First-run configuration |
| `inc/theme-demo-content.php` | Export/import system |
| `inc/admin-dashboard.php` | Custom admin interface |
| `demo-content.json` | Portable content package |

---

## 2. Branding & Discovery

### Client Discovery Interview

Before writing any code, gather this information:

```markdown
## Business Profile
- Company name:
- Industry:
- Target audience:
- Competitors:
- Unique value proposition:

## Brand Assets
- Logo files (SVG preferred):
- Color palette:
  - Primary:
  - Secondary:
  - Accent:
  - Background:
  - Text:
- Typography:
  - Headings font:
  - Body font:
- Photography style:

## Site Requirements
- Pages needed:
- Custom post types:
- Forms (contact, inquiry):
- Integrations:
- Special features:

## SEO Goals
- Target keywords:
- Competitor sites to outrank:
- Local SEO needed?
```

### Extract Brand from Existing Site

```bash
# Use brand-guide skill to extract colors/fonts
python3 /root/.claude/skills/brand-guide/extract-brand.py \
  --theme-path /path/to/theme \
  --output /path/to/brand-guide.md
```

### Brand Configuration in Theme

Store brand variables in `style.css` or Tailwind config:

```css
:root {
  /* Primary Brand Colors */
  --color-primary: #07254B;
  --color-secondary: #B4C1D1;
  --color-accent: #C9A227;
  --color-background: #EDEAE3;
  --color-text: #07254B;

  /* Typography */
  --font-heading: 'Playfair Display', serif;
  --font-body: 'Inter', sans-serif;
}
```

---

## 3. Theme Development

### Theme Structure Best Practices

```
client-theme/
├── style.css                 # Theme header + custom CSS
├── functions.php             # All PHP functionality
├── header.php                # <head> through <body> open
├── footer.php                # Footer through </body>
├── index.php                 # Home/fallback template
├── page-{slug}.php           # Custom page templates
├── single-{cpt}.php          # Custom post type singles
├── assets/
│   ├── css/
│   │   └── admin-style.css   # Admin customizations
│   ├── js/
│   │   └── animations.js     # GSAP/frontend JS
│   ├── images/
│   │   ├── logo.svg
│   │   └── logo-white.svg
│   └── video/                # Hero videos if needed
├── inc/
│   ├── setup-wizard.php      # First-run wizard
│   ├── admin-dashboard.php   # Custom dashboard
│   ├── admin-pages.php       # Settings pages
│   ├── theme-demo-content.php # Export/import
│   ├── required-plugins.php  # TGM plugin activation
│   └── class-tgm-plugin-activation.php
├── tests/
│   ├── playwright.config.ts
│   ├── run-tests.sh
│   └── e2e/*.spec.ts
├── demo-content.json         # Exportable content
├── screenshot.png            # Theme thumbnail (1200x900)
└── README.md                 # Theme documentation
```

### functions.php Essentials

```php
<?php
// Theme setup
function theme_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', ['search-form', 'gallery', 'caption']);

    register_nav_menus([
        'primary' => 'Primary Menu',
        'footer' => 'Footer Menu',
    ]);

    // Image sizes
    add_image_size('hero', 1920, 1080, true);
    add_image_size('card', 600, 400, true);
}
add_action('after_setup_theme', 'theme_setup');

// Enqueue assets
function theme_assets() {
    // Tailwind CSS (CDN for dev, compiled for prod)
    wp_enqueue_script('tailwind', 'https://cdn.tailwindcss.com', [], null);

    // GSAP for animations
    wp_enqueue_script('gsap', 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js', [], null, true);
    wp_enqueue_script('gsap-st', 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js', ['gsap'], null, true);

    // Theme scripts
    wp_enqueue_script('theme-animations', get_template_directory_uri() . '/assets/js/animations.js', ['gsap', 'gsap-st'], null, true);
}
add_action('wp_enqueue_scripts', 'theme_assets');

// Include additional files
require_once get_template_directory() . '/inc/setup-wizard.php';
require_once get_template_directory() . '/inc/admin-dashboard.php';
require_once get_template_directory() . '/inc/theme-demo-content.php';
```

### Custom Post Types

```php
// Register Property CPT
function register_property_cpt() {
    register_post_type('property', [
        'labels' => [
            'name' => 'Properties',
            'singular_name' => 'Property',
        ],
        'public' => true,
        'has_archive' => true,
        'menu_icon' => 'dashicons-building',
        'supports' => ['title', 'editor', 'thumbnail', 'excerpt'],
        'rewrite' => ['slug' => 'property'],
    ]);
}
add_action('init', 'register_property_cpt');
```

---

## 4. Content Management

### Demo Content Export

The theme includes a built-in export system at **CSR Theme → Demo Content**:

**What Gets Exported:**
- All pages with templates
- Custom post types with meta fields
- Yoast SEO data (focus keywords, meta descriptions)
- Featured image URLs
- Theme settings
- Reading settings (front page configuration)

**Export Process:**
1. Go to WordPress Admin → CSR Theme → Demo Content
2. Click "Export Demo Content"
3. File saved to `theme/demo-content.json`

**Export via WP-CLI:**
```bash
# In Docker container
docker exec -it wordpress-container bash

# Manual export trigger
wp eval "csr_export_demo_content();" --allow-root
```

### Demo Content Import

**On Fresh Installation:**
1. Activate theme
2. Setup Wizard offers demo import option
3. Or: CSR Theme → Demo Content → Import

**What Gets Imported:**
- Creates pages if slug doesn't exist
- Downloads featured images from URLs
- Sets Yoast SEO meta fields
- Configures front page settings

### Content via WP-CLI

```bash
# Create page
docker exec wordpress wp post create \
  --post_type=page \
  --post_title="About Us" \
  --post_name="about" \
  --post_status=publish \
  --allow-root

# Set page template
docker exec wordpress wp post meta update <ID> _wp_page_template page-about.php --allow-root

# Create property
docker exec wordpress wp post create \
  --post_type=property \
  --post_title="Downtown Tower" \
  --post_status=publish \
  --allow-root

# Set property meta
docker exec wordpress wp post meta update <ID> _property_status "active" --allow-root
docker exec wordpress wp post meta update <ID> _property_location "Miami, FL" --allow-root
```

---

## 5. SEO Configuration

### Yoast SEO Fields

| Meta Key | Purpose | Target |
|----------|---------|--------|
| `_yoast_wpseo_focuskw` | Focus keyword | Required for every page |
| `_yoast_wpseo_metadesc` | Meta description | 120-160 characters |
| `_yoast_wpseo_title` | SEO title | 50-60 characters |

### Set SEO via WP-CLI

```bash
# Set focus keyword
docker exec wordpress wp post meta update <ID> _yoast_wpseo_focuskw "miami real estate" --allow-root

# Set meta description (must contain focus keyword)
docker exec wordpress wp post meta update <ID> _yoast_wpseo_metadesc "Premier miami real estate development company specializing in luxury residential and commercial properties." --allow-root

# Set SEO title
docker exec wordpress wp post meta update <ID> _yoast_wpseo_title "About Us | Miami Real Estate Development" --allow-root
```

### SEO Audit

```bash
# Run full SEO audit
python3 /root/.claude/skills/seo-optimizer/audit.py \
  --base-url https://local2.hustletogether.com

# JSON output for processing
python3 /root/.claude/skills/seo-optimizer/audit.py \
  --base-url https://local2.hustletogether.com \
  --json

# Single page audit
python3 /root/.claude/skills/seo-optimizer/audit.py \
  --base-url https://local2.hustletogether.com \
  --page about
```

### SEO Checklist Per Page

- [ ] Focus keyword set
- [ ] Focus keyword appears in meta description
- [ ] Meta description is 120-160 characters
- [ ] SEO title is 50-60 characters
- [ ] Featured image has ALT text with keyword
- [ ] H1 contains focus keyword
- [ ] URL slug is keyword-friendly

---

## 6. Visual QA & Testing

### Screenshot Testing

```bash
# All pages, all viewports (10 sizes)
python3 /root/.claude/skills/visual-qa/screenshot.py \
  --all \
  --base-url https://local2.hustletogether.com \
  --output /root/screenshots

# Single page
python3 /root/.claude/skills/visual-qa/screenshot.py \
  --url https://local2.hustletogether.com/about/ \
  --output /root/screenshots
```

### Viewport Sizes Tested

| Category | Name | Resolution |
|----------|------|------------|
| Desktop | desktop-1920 | 1920×1080 |
| Desktop | desktop-1440 | 1440×900 |
| Desktop | desktop-1280 | 1280×800 |
| Tablet | tablet-portrait | 768×1024 |
| Tablet | tablet-landscape | 1024×768 |
| Tablet | tablet-mini | 744×1133 |
| Mobile | mobile-iphone14 | 390×844 |
| Mobile | mobile-iphone14pro | 393×852 |
| Mobile | mobile-iphoneSE | 375×667 |
| Mobile | mobile-android | 412×915 |

### E2E Testing (Playwright)

```bash
cd /path/to/theme/tests

# Install dependencies
npm install

# Run all tests
./run-tests.sh

# Run specific suite
./run-tests.sh home
./run-tests.sh contact
./run-tests.sh responsive

# UI mode (interactive)
./run-tests.sh ui

# View report
./run-tests.sh report
```

### Test Suites

| File | Tests |
|------|-------|
| `navigation.spec.ts` | Header, footer, menu links |
| `home.spec.ts` | Hero, animations, featured content |
| `about.spec.ts` | Team section, company info |
| `portfolio.spec.ts` | Property grid, filtering |
| `contact.spec.ts` | Form validation, submission |
| `property.spec.ts` | Property details, inquiry form |
| `legal.spec.ts` | Privacy, Terms pages |
| `responsive.spec.ts` | Layout at all breakpoints |

---

## 7. Theme Packaging

### Create Distribution Zip

```bash
cd /root/repos/client-project

# Remove old zips
rm -f client-theme-*.zip

# Create versioned zip (exclude dev files)
zip -r client-theme-1.0.0.zip client-theme \
  -x "*.git*" \
  -x "*node_modules*" \
  -x "*.DS_Store" \
  -x "*tests/*" \
  -x "*.env*"

# Verify contents
unzip -l client-theme-1.0.0.zip
```

### Version Numbering

Update `style.css` header:
```css
/*
Theme Name: Client Theme
Version: 1.0.0
*/
```

**Versioning Convention:**
- `1.0.0` - Initial release
- `1.0.1` - Bug fixes
- `1.1.0` - New features
- `2.0.0` - Major redesign

### Pre-Package Checklist

- [ ] Version number updated in style.css
- [ ] All PHP files have no syntax errors (`php -l *.php`)
- [ ] demo-content.json is current
- [ ] Screenshot.png is 1200×900
- [ ] README.md is complete
- [ ] No debug code or console.logs
- [ ] No hardcoded URLs
- [ ] .htaccess included if needed

---

## 8. GitHub Deployment

### Initial Repository Setup

```bash
cd /root/repos/client-project/client-theme

# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
node_modules/
.DS_Store
*.log
tests/test-results/
tests/playwright-report/
.env
*.zip
EOF

# Initial commit
git add .
git commit -m "Initial theme release v1.0.0"

# Create GitHub repo
gh repo create client-theme --public --source=. --push

# Or add existing remote
git remote add origin https://github.com/username/client-theme.git
git push -u origin main
```

### Push Updates

```bash
# Stage changes
git add .

# Commit with version
git commit -m "feat: add contact form validation v1.0.1"

# Push to GitHub
git push origin main
```

### WP Pusher Setup (Production)

**On Production WordPress:**

1. **Install WP Pusher**
   - Plugins → Add New → Search "WP Pusher"
   - Install and Activate

2. **Connect Repository**
   - WP Pusher → Install Theme
   - Repository: `username/client-theme`
   - Branch: `main`
   - Click "Install Theme"

3. **Update Theme**
   - WP Pusher → Themes
   - Find theme → Click "Update Theme"

4. **Enable Auto-Deploy (Optional)**
   - WP Pusher → Themes → theme settings
   - Enable "Push-to-Deploy"
   - Copy webhook URL
   - Add to GitHub: Settings → Webhooks → Add webhook
   - Paste URL, content type: application/json
   - Select "Just the push event"

### Manual Git Update (SSH Access)

```bash
# SSH to production server
ssh user@production-server

# Navigate to theme
cd /var/www/html/wp-content/themes/client-theme

# Pull latest
git pull origin main

# Clear cache if needed
wp cache flush --allow-root
```

---

## 9. Production Sync

### Theme File Sync

For sites without Git access, use SFTP sync:

```bash
# Using rsync
rsync -avz --delete \
  /root/repos/client-project/client-theme/ \
  user@production:/var/www/html/wp-content/themes/client-theme/ \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='tests'

# Using SFTP
sftp user@production << EOF
cd /var/www/html/wp-content/themes
put -r client-theme
EOF
```

### Database Sync

```bash
# Export from local Docker
docker exec wordpress wp db export /tmp/local-db.sql --allow-root
docker cp wordpress:/tmp/local-db.sql ./local-db.sql

# Search-replace URLs
docker exec wordpress wp search-replace \
  'https://local.domain.com' \
  'https://production.com' \
  --all-tables \
  --allow-root

# Import to production
wp db import local-db.sql --allow-root
```

### Media Sync

```bash
# Export media from Docker
docker cp wordpress:/var/www/html/wp-content/uploads ./uploads

# Upload to production
rsync -avz ./uploads/ user@production:/var/www/html/wp-content/uploads/
```

---

## 10. Client Handoff

### White-Label Admin

Use the white-label skill to prepare admin for clients:

```bash
# Apply white-label configuration
/root/.claude/skills/white-label/scripts/apply-white-label.sh \
  config.json \
  wordpress-container
```

**Customizations Applied:**
- Custom login URL (`/client-login`)
- Branded login page (logo, colors)
- Custom admin footer
- Hidden dashboard widgets
- Organized admin menu
- Disabled XML-RPC
- Obfuscated author slugs

### Client Documentation

Generate handoff documentation:

```markdown
# Website Admin Guide

## Login
- URL: https://yoursite.com/client-login
- Username: [provided separately]
- Password: [provided separately]

## Editing Pages
1. Log in to admin
2. Click "Pages" in left menu
3. Click page to edit
4. Make changes
5. Click "Update"

## Adding Properties
1. Click "Properties" → "Add New"
2. Enter title and details
3. Set featured image
4. Fill in property fields
5. Click "Publish"

## SEO Guidelines
- Every page needs a focus keyword
- Meta descriptions: 120-160 characters
- Include focus keyword in meta description
- Set featured image with descriptive ALT text

## Support
Contact support@agency.com for assistance.
```

### Pre-Launch Checklist

Run `/wp-launch` command or manually verify:

- [ ] All pages have content
- [ ] All forms tested and working
- [ ] Email delivery configured (WP Mail SMTP)
- [ ] SEO configured for all pages
- [ ] Featured images set
- [ ] Favicon uploaded
- [ ] Social sharing images set
- [ ] 404 page configured
- [ ] Analytics installed
- [ ] SSL certificate active
- [ ] Caching enabled
- [ ] Backups configured
- [ ] Security hardened
- [ ] Admin white-labeled
- [ ] Client documentation provided

---

## Quick Reference Commands

### Docker

```bash
docker-compose up -d          # Start
docker-compose down           # Stop
docker-compose logs -f        # View logs
docker exec -it wordpress bash # Shell access
```

### WP-CLI (in Docker)

```bash
docker exec wordpress wp plugin list --allow-root
docker exec wordpress wp post list --post_type=page --allow-root
docker exec wordpress wp cache flush --allow-root
```

### Git

```bash
git status                    # Check changes
git add .                     # Stage all
git commit -m "message"       # Commit
git push origin main          # Push to GitHub
```

### Testing

```bash
python3 /root/.claude/skills/visual-qa/screenshot.py --all --base-url URL
python3 /root/.claude/skills/seo-optimizer/audit.py --base-url URL
./run-tests.sh                # E2E tests
```

### Packaging

```bash
zip -r theme-1.0.0.zip theme -x "*.git*" -x "*node_modules*" -x "*tests/*"
```

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `wp-docker` | Docker environment setup |
| `wordpress-dev` | Coding standards, CPT, security |
| `wordpress-admin` | WP-CLI, content management |
| `seo-optimizer` | SEO auditing and fixes |
| `visual-qa` | Screenshot testing |
| `brand-guide` | Brand documentation |
| `white-label` | Admin customization |
| `gsap-animations` | Animation best practices |
| `wp-performance` | Speed optimization |
| `form-testing` | Form and email testing |

---

**Version**: 1.0
**Last Updated**: December 29, 2025
