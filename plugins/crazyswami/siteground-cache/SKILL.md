# SiteGround Cache Buster Skill

Bypass SiteGround caching (SG CachePress + LiteSpeed) for WordPress development. Adds cache-busting code to child themes for real-time development testing.

---

## ⛔ CRITICAL: STAGING ONLY - NEVER PRODUCTION

**Claude is FORBIDDEN from deploying to production sites.**

| Action | Allowed? |
|--------|----------|
| Deploy to staging | ✅ YES |
| Deploy to production | ❌ **ABSOLUTELY NEVER** |
| Read from production | ✅ YES (read-only) |
| Write to production | ❌ **ABSOLUTELY NEVER** |

**If user asks to deploy to production:**
1. **REFUSE** the request
2. Explain that production deployments must be done manually by the user
3. Offer to deploy to staging instead

**Production paths are BLOCKED.** Any path that does NOT contain "staging" is off-limits for writes.

---

## Required Information

Before using this skill, Claude will ask for:

1. **FTP/SFTP Credentials**
   - Hostname (e.g., `ftp.example.com`)
   - Username
   - Password
   - Port (usually 21 for FTP, 22 for SFTP)

2. **Site URLs**
   - Staging URL (e.g., `https://staging.example.com`)
   - ~~Production URL~~ (NOT needed - Claude won't deploy there)

3. **Theme Path**
   - Child theme folder name (e.g., `theme-child`)

**Store credentials in project's `CLAUDE.local.md`** (gitignored) for future sessions.

---

## Staging-Only Workflow

```
Local Development → Staging Site → [USER MANUALLY] → Production
        ↑              ↑                   ↑
    Claude edits   Claude deploys     USER deploys
```

Claude handles: Local editing + Staging deployment
User handles: Production deployment (via SiteGround, FTP client, or manually)

---

## What It Does

1. **Disables server-side caching for admins** - LiteSpeed Cache + SG CachePress
2. **Adds no-cache headers** - Prevents CDN/proxy caching
3. **Busts browser cache** - Adds timestamp to CSS/JS URLs
4. **Shows version banner** - Visual confirmation theme is loading (admin only)

---

## The Code

### PHP Snippet (add to functions.php)

```php
/**
 * SiteGround Cache Buster for Development
 * Disables caching for logged-in administrators
 * REMOVE OR DISABLE IN PRODUCTION when done testing
 */

// Development mode banner (shows version to confirm theme is active)
add_action('wp_head', 'sg_dev_mode_banner');
function sg_dev_mode_banner() {
    if (current_user_can('administrator')) {
        $theme = wp_get_theme();
        $version = $theme->get('Version');
        $name = $theme->get('Name');
        echo '<style>
            .sg-dev-banner {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #34889A;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 12px;
                z-index: 999999;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
        </style>
        <div class="sg-dev-banner">
            ' . esc_html($name) . ' v' . esc_html($version) . ' - ' . date('M j, H:i') . '
        </div>';
    }
}

// Disable all caching for administrators
add_action('init', 'sg_disable_cache_for_dev');
function sg_disable_cache_for_dev() {
    if (current_user_can('administrator')) {
        // Disable LiteSpeed Cache
        if (!defined('LSCACHE_NO_CACHE')) {
            define('LSCACHE_NO_CACHE', true);
        }

        // Disable SG Optimizer/CachePress
        if (!defined('SG_CACHEPRESS_NO_CACHE')) {
            define('SG_CACHEPRESS_NO_CACHE', true);
        }

        // Send no-cache headers
        nocache_headers();

        // Additional headers for CDN bypass
        header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
        header('Pragma: no-cache');
        header('Expires: Thu, 01 Jan 1970 00:00:00 GMT');
    }
}

// Bust browser cache by adding timestamp to theme CSS/JS
add_filter('style_loader_src', 'sg_bust_asset_cache', 999);
add_filter('script_loader_src', 'sg_bust_asset_cache', 999);
function sg_bust_asset_cache($src) {
    if (current_user_can('administrator')) {
        // Only bust cache for theme assets
        $theme_uri = get_stylesheet_directory_uri();
        $parent_uri = get_template_directory_uri();

        if (strpos($src, $theme_uri) !== false || strpos($src, $parent_uri) !== false) {
            $src = add_query_arg('v', time(), $src);
        }
    }
    return $src;
}
```

---

## Usage

### Method 1: Auto-inject via Script

```bash
# Navigate to your project
cd /path/to/wordpress-project

# Run the injector script
/root/.claude/skills/siteground-cache/add-cache-buster.sh ./wp-content/themes/your-child-theme
```

### Method 2: Manual Copy

1. Copy the PHP code above
2. Paste at the end of your child theme's `functions.php`
3. Upload via FTP **TO STAGING ONLY**
4. Visit staging site as admin - you should see the version banner

### Method 3: Via Claude

Just ask:
- "Add SiteGround cache busting to this theme"
- "Enable dev mode for SiteGround"
- "Add cache buster to functions.php"

**Claude will only deploy to staging.**

---

## Deployment Workflow (STAGING ONLY)

### Step 1: Get Credentials (Ask User)

Before deploying, ask the user:
```
I need FTP credentials to deploy to STAGING. Please provide:
1. FTP Host (e.g., ftp.yourdomain.com)
2. FTP Username
3. FTP Password
4. Staging site path (e.g., staging.yourdomain.com/public_html)
```

### Step 2: Deploy to Staging

```bash
# STAGING ONLY - Never production!
lftp -u "user,password" -e "
    set ssl:verify-certificate no
    mirror -R ./child-theme staging.example.com/public_html/wp-content/themes/child-theme
    bye
" ftp://ftp.example.com
```

### Step 3: Verify on Staging

1. Visit staging site as admin
2. Confirm dev banner appears (bottom-right)
3. Test CSS/JS changes are visible
4. Check for PHP errors

### Step 4: User Deploys to Production

**Claude does NOT do this step.** Tell the user:

```
The changes are ready on staging. To deploy to production:

Option 1: SiteGround Site Tools
  - Go to Site Tools > WordPress > Staging
  - Click "Push to Live"

Option 2: FTP Client (FileZilla, Cyberduck, etc.)
  - Download from staging
  - Upload to production

Option 3: Manual file copy via FTP
```

---

## How Each Part Works

### 1. LiteSpeed Cache Bypass
```php
define('LSCACHE_NO_CACHE', true);
```
LiteSpeed Cache plugin checks for this constant and skips caching when set.

### 2. SG CachePress Bypass
```php
define('SG_CACHEPRESS_NO_CACHE', true);
```
SiteGround's caching plugin respects this constant.

### 3. HTTP Headers
```php
nocache_headers();
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
```
Tells browsers and CDNs not to cache the response.

### 4. Asset Cache Busting
```php
add_query_arg('v', time(), $src);
```
Adds `?v=1704567890` to CSS/JS URLs. Since the timestamp changes every second, browsers always fetch fresh files.

---

## Troubleshooting

### Banner not showing?
- Make sure you're logged in as Administrator
- Check if child theme is activated (Appearance > Themes)
- Check for PHP errors in the error log

### Still seeing cached content?
1. Try incognito/private browser window
2. Clear browser cache manually
3. Check SiteGround Site Tools > Speed > Caching > Purge Cache
4. Check if Cloudflare is in front (need to purge there too)

### CSS changes not appearing?
- View page source and check if `?v=` timestamp is on CSS URLs
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

---

## Files in This Skill

```
/root/.claude/skills/siteground-cache/
├── SKILL.md                 # This documentation
├── add-cache-buster.sh      # Auto-inject script
├── cache-buster.php         # Standalone PHP snippet
└── remove-cache-buster.sh   # Removal script
```

---

## Example CLAUDE.local.md Template

Store this in your project (gitignored):

```markdown
# SiteGround Credentials (DO NOT COMMIT)

## FTP Access
- Host: ftp.example.com
- User: user@example.com
- Pass: your-password
- Port: 21

## Site URLs
- Staging: https://staging.example.com
- Production: https://example.com (READ-ONLY for Claude)

## Theme Paths
- Staging: staging.example.com/public_html/wp-content/themes/theme-child
- Production: OFF-LIMITS (user deploys manually)
```

---

## Related

- **wp-docker** - Local WordPress development
- **wp-performance** - Production caching optimization
- **visual-qa** - Screenshot testing after changes
