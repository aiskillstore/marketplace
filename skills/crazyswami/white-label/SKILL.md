---
name: white-label
description: Complete WordPress white-labeling using FREE plugins only - ASE, Branda, White Label CMS, Admin Menu Editor. Covers login page branding, admin cleanup, security hardening, and client handoff preparation.
allowed-tools: Read, Write, Edit, Bash, WebFetch
---

# White-Label Skill (FREE Plugins Only)

Complete WordPress white-labeling system using free plugins to create a professional, branded admin experience without any paid elements.

## Plugin Stack

| Plugin | Purpose | Key Features |
|--------|---------|--------------|
| **ASE (Admin and Site Enhancements)** | Security, admin cleanup | Custom login URL, disable XML-RPC, hide notices, obfuscate authors |
| **White Label CMS** | Dashboard & menu branding | Setup wizard, custom welcome panel, hide menus by role, import/export |
| **Branda (White Labeling)** | Login page branding | Custom logo, colors, backgrounds, admin bar logo |
| **Admin Menu Editor** (optional) | Advanced menu control | Reorder, rename, custom icons, granular permissions |

## Recommended Approach

1. **ASE** - Security first (login URL, XML-RPC, author slugs)
2. **White Label CMS** - Use setup wizard for quick branding + menu hiding
3. **Branda** - Fine-tune login page if White Label CMS isn't enough

---

## White Label CMS Quick Setup

**Access**: WordPress Admin → Settings → White Label CMS

### Setup Wizard
White Label CMS has a built-in wizard that walks you through:
1. Your company logo (admin bar, login page)
2. Client details
3. Dashboard welcome panel
4. Menu visibility

### Key Features
- **Custom Welcome Dashboard**: Add your own panel with Elementor/Beaver Builder support
- **Hide Menus by Role**: Built-in, no extra plugin needed
- **CMS Profiles**: Choose Website, Blog, or Custom preset
- **Import/Export**: Save and reuse settings across sites
- **Login Page**: Customize logo and use `/login` as URL alias

## What We Can Configure (100% FREE)

| Feature | Plugin | How |
|---------|--------|-----|
| Custom login page logo | Branda | Upload via Media Library |
| Login background color/image | Branda | Color picker or image upload |
| Login form styling | Branda | Colors, borders, shadows |
| Admin footer text | ASE or Branda | Custom HTML text |
| Admin bar cleanup | ASE | Toggle visibility of items |
| Hide "Howdy" greeting | Branda | Replace with custom text |
| Dashboard widget removal | ASE | Checkbox per widget |
| Custom login URL | ASE | Slug like `/client-login` |
| Menu organization | Admin Menu Editor | Drag-and-drop |
| WordPress version hiding | ASE | Toggle on/off |
| Admin color scheme | Branda | Custom palette |
| Disable admin notices | ASE | Move to panel or hide |

---

## Phase 1: Security First (ASE)

### 1.1 Change Login URL
- **Plugin**: ASE → Login/Logout → Change Login URL
- **Setting**: Custom URL like `/client-login` or `/secure-access`
- **Why**: Prevents automated attacks on `/wp-login.php`

**Recommended slugs:**
```
/client-login
/company-access
/portal
/secure-login
```

**Avoid:** `/login`, `/admin`, `/signin` (too common)

### 1.2 Login ID Type
- **Plugin**: ASE → Login/Logout → Login ID Type
- **Setting**: Restrict to "Username only" or "Email only"
- **Reduces attack surface**

### 1.3 Obfuscate Author Slugs
- **Plugin**: ASE → Security → Obfuscate Author Slugs
- **Hides usernames from author archive URLs**

### 1.4 Disable XML-RPC
- **Plugin**: ASE → Security → Disable XML-RPC
- **Prevents brute force and DDoS attacks**

### 1.5 Email Address Obfuscation
- **Plugin**: ASE → Security → Email Address Obfuscation
- **Protects displayed emails from scrapers**

---

## Phase 2: Branding (Branda)

### 2.1 Login Page Customization

**Access**: Branda → Login Screen

**Customize:**
- **Logo**: Upload client's logo (recommended: 200-400px wide, PNG or SVG)
- **Logo Link**: Change from wordpress.org to client's site
- **Background**: Solid color or image
- **Form Box**: Background color, border radius, shadow
- **Button**: Background color, text color, hover state
- **Links**: "Lost password" and "Back to site" colors

**Example Configuration:**
```
Logo: /wp-content/uploads/client-logo.png
Logo Width: 300px
Background Color: #1a1a2e
Form Background: #ffffff
Form Border Radius: 8px
Button Color: #e94560
Button Hover: #c73e54
```

### 2.2 Admin Bar Branding

**Access**: Branda → Admin Area → Admin Bar

**Options:**
- Replace WordPress logo with custom logo
- Hide WordPress logo entirely
- Custom admin bar background color
- Custom menu item colors

### 2.3 Replace "Howdy" Greeting

**Access**: Branda → Admin Area → Howdy Message

**Replace with:**
- "Welcome, {username}"
- "Hello, {display_name}"
- "{display_name}" (just the name)

### 2.4 Admin Footer

**Access**: Branda → Admin Area → Admin Footer

**Custom footer text (HTML supported):**
```html
&copy; 2025 [Client Name]. Powered by <a href="https://youragency.com">Your Agency</a>.
```

### 2.5 Dashboard Widget Branding

**Access**: Branda → Dashboard → Welcome Widget

**Create custom welcome widget with:**
- Client logo
- Quick links to common tasks
- Support contact information

---

## Phase 3: Admin Cleanup (ASE)

### 3.1 Clean Up Admin Bar
- **Plugin**: ASE → Admin Interface → Clean Up Admin Bar
- **Hide**: WordPress logo, comments, new content, updates, help tab
- **Keep**: Site name, user menu, essentials only

### 3.2 Hide Admin Notices
- **Plugin**: ASE → Admin Interface → Hide Admin Notices
- **Moves notices to separate panel** (accessible via admin bar icon)
- Keeps interface clean for clients

### 3.3 Disable Dashboard Widgets
- **Plugin**: ASE → Admin Interface → Disable Dashboard Widgets
- **Disable**:
  - WordPress News
  - Quick Draft
  - At a Glance (optional)
  - Activity (optional)
- **Keep**: Custom widgets, Site Health (maybe)

### 3.4 Wider Admin Menu
- **Plugin**: ASE → Admin Interface → Wider Admin Menu
- **Better readability** for long menu items

---

## Phase 4: Menu Organization (Admin Menu Editor)

### 4.1 Reorder Menu Items

**Recommended Order for Clients:**
1. Dashboard
2. Pages
3. Posts (or custom CPT name)
4. Media
5. *(separator)*
6. Comments (if enabled)
7. *(separator)*
8. Appearance (hide for editors)
9. Plugins (hide for editors)
10. Users
11. Tools (hide for editors)
12. Settings (hide for editors)

### 4.2 Rename Confusing Items

| Original | Rename To |
|----------|-----------|
| Posts | News / Blog / Articles |
| Media | Files / Images |
| Pages | Website Pages |
| Comments | Feedback / Reviews |

### 4.3 Hide Advanced Items

**Hide from Editors:**
- Plugins
- Appearance → Editor
- Tools → all except Export
- Settings → all

**Hide from Authors:**
- Everything in Editor list
- Plus: Users, Comments settings

### 4.4 Add Custom Menu Items

Admin Menu Editor allows adding links to:
- External resources
- Custom admin pages
- Help documentation

---

## Phase 5: Performance & Cleanup (ASE)

### 5.1 Heartbeat Control
- **Dashboard**: Disable or reduce to 60s
- **Post Editor**: Reduce to 30s (for autosave)
- **Frontend**: Disable

### 5.2 Revisions Control
- **Limit to 5-10 revisions** per post
- Prevents database bloat

### 5.3 Image Upload Control
- **Max dimensions**: 2560x2560px
- **Convert BMP to JPG**: Enable
- **Convert PNG to JPG**: Enable (non-transparent only)

### 5.4 Disable Bloat
- **Embeds**: Disable if not using oEmbed
- **Emoji**: Disable (system emojis work fine)
- **Dashicons on frontend**: Disable
- **jQuery Migrate**: Disable if not needed

---

## Automated White-Labeling (Claude Can Do This!)

This skill includes automation scripts that allow Claude to configure ALL white-label settings programmatically based on brand information you provide.

### Quick Start

```bash
# Apply white-label config from JSON file
/root/.claude/skills/white-label/scripts/apply-white-label.sh config.json container-name

# Example for CSR Development:
/root/.claude/skills/white-label/scripts/apply-white-label.sh \
  /root/csrdevelopment.com/white-label-config.json \
  wordpress-local-wordpress-1
```

### Configuration File Format

Create a JSON file with your brand settings:

```json
{
  "brand": {
    "company_name": "Your Company",
    "logo_url": "https://example.com/logo.png",
    "website": "https://yourcompany.com",
    "colors": {
      "primary": "#2271b1",
      "primary_dark": "#135e96",
      "background": "#1a1a2e"
    }
  },
  "login": {
    "background_color": "#1a1a2e",
    "form_background": "#ffffff",
    "button_color": "#2271b1",
    "logo_width": 300
  },
  "security": {
    "login_url": "secure-login",
    "disable_xmlrpc": true,
    "obfuscate_authors": true
  },
  "dashboard": {
    "hide_news": true,
    "hide_quick_draft": true,
    "welcome_title": "Welcome",
    "welcome_message": "<p>Your custom dashboard message</p>"
  },
  "greeting": "Welcome,"
}
```

### What Gets Configured

The automation script configures:

| Plugin | Settings Applied |
|--------|-----------------|
| **White Label CMS** | Admin bar logo, greeting, side menu, footer, dashboard widgets, welcome panel |
| **ASE** | Custom login URL, XML-RPC, author obfuscation, email obfuscation, heartbeat, revisions |
| **Branda** | Login page styling, admin bar, howdy message, footer |

### Asking Claude to White-Label

Just say:
- "White-label this site for [Company Name]"
- "Apply branding with primary color #e94560"
- "Set up client handoff for [Company]"

Claude will:
1. Create or use existing config JSON
2. Run the automation script
3. Verify all settings applied
4. Report completion

### Scripts Location

```
/root/.claude/skills/white-label/scripts/
├── apply-white-label.sh           # Main runner script
├── configure-white-label.php      # WP-CLI configuration script
└── white-label-config.example.json # Example config file
```

---

## Programmatic Configuration

All three plugins store settings in `wp_options`:

| Plugin | Option Name | Format |
|--------|-------------|--------|
| ASE | `admin_site_enhancements` | Serialized array |
| Branda | `ub_settings` (and others) | Serialized array |
| Admin Menu Editor | `acp_custom_menu`, `acp_custom_menu_data` | Serialized array |

### Reading Current Settings

```bash
# ASE settings
docker exec wordpress wp option get admin_site_enhancements --format=json

# Branda settings
docker exec wordpress wp option get ub_settings --format=json

# Admin Menu Editor
docker exec wordpress wp option get acp_custom_menu --format=json
```

### Updating Settings via WP-CLI

**ASE Configuration:**
```bash
docker exec wordpress wp option update admin_site_enhancements '{
  "change_login_url": {"enabled": true, "slug": "secure-login"},
  "hide_admin_notices": true,
  "disable_xmlrpc": true,
  "obfuscate_author_slugs": true,
  "heartbeat_control": {
    "dashboard": "disable",
    "post_editor": 30,
    "frontend": "disable"
  },
  "revisions_control": 5
}' --format=json
```

**Branda Login Customization:**
```bash
# Upload logo first
docker exec wordpress wp media import /path/to/logo.png --title="Client Logo"

# Get attachment ID
LOGO_ID=$(docker exec wordpress wp post list --post_type=attachment --name=logo --field=ID)

# Update Branda settings
docker exec wordpress wp option update ub_login_image "$LOGO_ID"
docker exec wordpress wp option update ub_login_background_color "#1a1a2e"
```

---

## Automation Script

Complete white-label setup script:

```bash
#!/bin/bash
# white-label-setup.sh - Apply complete white-labeling

CLIENT_NAME="${1:-Client Name}"
LOGIN_URL="${2:-client-login}"
LOGO_PATH="${3:-}"
PRIMARY_COLOR="${4:-#2271b1}"
BACKGROUND_COLOR="${5:-#1a1a2e}"

# Configure ASE
docker-compose exec -T wpcli wp option update admin_site_enhancements "$(cat <<EOF
{
  "change_login_url": {"enabled": true, "slug": "$LOGIN_URL"},
  "hide_admin_notices": true,
  "disable_xmlrpc": true,
  "obfuscate_author_slugs": true,
  "email_address_obfuscation": true,
  "clean_up_admin_bar": {
    "enabled": true,
    "hide_wp_logo": true,
    "hide_comments": true,
    "hide_new_content": true
  },
  "disable_dashboard_widgets": {
    "welcome": true,
    "quick_draft": true,
    "wordpress_news": true
  },
  "heartbeat_control": {
    "dashboard": "disable",
    "post_editor": 30,
    "frontend": "disable"
  },
  "revisions_control": 5
}
EOF
)" --format=json

# Upload logo if provided
if [ -n "$LOGO_PATH" ] && [ -f "$LOGO_PATH" ]; then
    docker cp "$LOGO_PATH" wordpress:/tmp/logo.png
    docker-compose exec -T wpcli wp media import /tmp/logo.png --title="$CLIENT_NAME Logo"
fi

# Configure admin footer
docker-compose exec -T wpcli wp option update ub_admin_footer_text \
  "&copy; $(date +%Y) $CLIENT_NAME. All rights reserved."

echo "White-labeling complete for: $CLIENT_NAME"
echo "Login URL: /wp-login.php → /$LOGIN_URL"
```

---

## Template Configuration Export

Save this as your baseline white-label configuration:

```json
{
  "ase": {
    "change_login_url": {
      "enabled": true,
      "slug": "secure-login"
    },
    "hide_admin_notices": true,
    "disable_xmlrpc": true,
    "obfuscate_author_slugs": true,
    "email_address_obfuscation": true,
    "clean_up_admin_bar": {
      "enabled": true,
      "hide_wp_logo": true,
      "hide_comments": true,
      "hide_new_content": true,
      "hide_updates": true
    },
    "disable_dashboard_widgets": {
      "welcome": true,
      "quick_draft": true,
      "wordpress_news": true,
      "activity": false
    },
    "heartbeat_control": {
      "dashboard": "disable",
      "post_editor": 30,
      "frontend": "disable"
    },
    "revisions_control": 5,
    "image_upload_control": {
      "max_width": 2560,
      "max_height": 2560
    }
  },
  "branda": {
    "login_screen": {
      "logo_enabled": true,
      "background_color": "#1a1a2e",
      "form_background": "#ffffff",
      "button_color": "#e94560"
    },
    "admin_bar": {
      "hide_wp_logo": true,
      "custom_logo_enabled": true
    },
    "howdy_message": {
      "enabled": true,
      "text": "Welcome,"
    },
    "admin_footer": {
      "enabled": true,
      "text": "&copy; {year} {client}. All rights reserved."
    }
  },
  "admin_menu_editor": {
    "hide_for_non_admins": [
      "plugins.php",
      "theme-editor.php",
      "options-general.php",
      "tools.php"
    ],
    "rename": {
      "Posts": "News",
      "Media": "Files"
    }
  }
}
```

---

## Client Handoff Checklist

Before handing off to client:

- [ ] Custom login URL set and tested
- [ ] Login page has client logo
- [ ] Login page colors match brand
- [ ] Admin bar shows client branding (not WordPress)
- [ ] "Howdy" replaced with professional greeting
- [ ] Admin footer shows client copyright
- [ ] Dashboard widgets cleaned up
- [ ] Menu items renamed and organized
- [ ] Advanced items hidden from editors
- [ ] WordPress version hidden
- [ ] XML-RPC disabled
- [ ] Author slugs obfuscated
- [ ] Email addresses obfuscated
- [ ] Heartbeat optimized
- [ ] Revisions limited
- [ ] Image upload limits set

---

## Troubleshooting

### Login URL Not Working
1. Flush permalinks: Settings → Permalinks → Save
2. Check for plugin conflicts
3. Verify .htaccess is writable
4. Clear all caches

### Logo Not Displaying on Login
1. Check image dimensions (not too large)
2. Verify image URL is accessible
3. Clear browser cache
4. Check Branda settings saved

### Admin Bar Items Still Visible
1. Clear browser cache
2. Check if other plugins are adding items
3. Verify ASE/Branda settings saved
4. Check user role (some items only for admins)

### Settings Not Saving
1. Check user capabilities (must be admin)
2. Clear cache (if using caching plugin)
3. Disable other security plugins temporarily
4. Check PHP memory limit

---

## Related Skills

- **wp-docker**: Development environment
- **wp-playground**: Testing environment
- **wordpress-admin**: Site management
- **seo-optimizer**: SEO configuration
- **brand-guide**: Brand documentation

---

## Sources

- [ASE Plugin](https://wordpress.org/plugins/admin-site-enhancements/)
- [Branda Plugin](https://wordpress.org/plugins/branda-white-labeling/)
- [Admin Menu Editor](https://wordpress.org/plugins/admin-menu-editor/)
- [White-Labeling Best Practices](https://developer.wordpress.org/themes/customize-api/)
