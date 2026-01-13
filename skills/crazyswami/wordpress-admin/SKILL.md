---
name: wordpress-admin
description: Full WordPress site management - create pages/posts, configure SEO (Yoast), upload media, manage settings. Use when creating content, setting up SEO, or managing any WordPress site.
allowed-tools: Read, Write, Edit, Bash(docker *), Bash(curl *), Bash(python3 *), Bash(lftp *)
---

# WordPress Admin Skill

Complete WordPress site management via WP-CLI (local Docker) and REST API (production sites).

## When to Use This Skill

Invoke this skill when you need to:
- Create pages or posts in WordPress
- Set up SEO (focus keyword, meta description, title)
- Upload and manage media/images
- Configure WordPress settings
- Check or recommend plugins
- Manage the local WordPress Docker environment

## Available Sites

### CSR Development (Production)
- **Site URL:** https://csrdevelopment.com
- **REST API:** https://csrdevelopment.com/wp-json/wp/v2
- **FTP Host:** ftp.csrdevelopment.com
- **FTP User:** alfonso@csrdevelopment.com
- **Theme Path:** /wp-content/themes/csr-theme
- **Local Files:** /root/csrdevelopment.com/csrdevelopment.com/public_html

### Local WordPress (Docker)
- **Site URL:** https://local2.hustletogether.com
- **Container:** wordpress-local-wordpress-1
- **WP-CLI:** `docker exec wordpress-local-wordpress-1 wp <command> --allow-root`
- **Admin:** https://local2.hustletogether.com/wp-admin
- **Credentials:** admin / admin123

## Workflows

### Create a Page

**Local (Docker):**
```bash
docker exec wordpress-local-wordpress-1 wp post create \
  --post_type=page \
  --post_title="Privacy Policy" \
  --post_name="privacy-policy" \
  --post_status="publish" \
  --allow-root
```

**Production (REST API):**
```bash
curl -X POST "https://csrdevelopment.com/wp-json/wp/v2/pages" \
  -H "Authorization: Basic BASE64_CREDENTIALS" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Privacy Policy",
    "slug": "privacy-policy",
    "status": "publish",
    "template": "page-privacy-policy.php"
  }'
```

### Set Page Template

```bash
docker exec wordpress-local-wordpress-1 wp post meta update <POST_ID> _wp_page_template "page-privacy-policy.php" --allow-root
```

### Configure SEO (Yoast)

**Requirements:** Theme must have Yoast meta fields registered (see functions.php snippet below)

```bash
# Set focus keyphrase
docker exec wordpress-local-wordpress-1 wp post meta update <POST_ID> _yoast_wpseo_focuskw "privacy policy miami real estate" --allow-root

# Set meta description (155 chars max, include focus keyword)
docker exec wordpress-local-wordpress-1 wp post meta update <POST_ID> _yoast_wpseo_metadesc "Learn how CSR Real Estate protects your privacy and handles personal information on our Miami real estate development website." --allow-root

# Set SEO title
docker exec wordpress-local-wordpress-1 wp post meta update <POST_ID> _yoast_wpseo_title "Privacy Policy | CSR Real Estate" --allow-root
```

### Upload Media

**From URL:**
```bash
docker exec wordpress-local-wordpress-1 wp media import "https://images.pexels.com/photos/123456/image.jpg" --title="Privacy Header" --allow-root
```

**Set Featured Image:**
```bash
docker exec wordpress-local-wordpress-1 wp post meta update <POST_ID> _thumbnail_id <MEDIA_ID> --allow-root
```

### List Pages/Posts

```bash
docker exec wordpress-local-wordpress-1 wp post list --post_type=page --allow-root
docker exec wordpress-local-wordpress-1 wp post list --post_type=post --allow-root
docker exec wordpress-local-wordpress-1 wp post list --post_type=property --allow-root
```

### Check/Install Plugins

```bash
# List installed plugins
docker exec wordpress-local-wordpress-1 wp plugin list --allow-root

# Install and activate a plugin
docker exec wordpress-local-wordpress-1 wp plugin install wordpress-seo --activate --allow-root
```

## SEO Best Practices

### Focus Keyphrase
- 2-4 words that describe the page content
- Should appear in title, meta description, and content
- Use naturally, don't keyword stuff

### Meta Description
- 150-155 characters max
- Include focus keyphrase
- Compelling call to action
- Unique for each page

### Page Title (SEO Title)
- 50-60 characters max
- Focus keyphrase near the beginning
- Brand name at the end (e.g., "Title | CSR Real Estate")

### Featured Image
- Every page/post should have one
- Optimized file size (< 200KB)
- Descriptive alt text with keyphrase

## Required Theme Modification

Add to theme's `functions.php` to enable Yoast fields via REST API:

```php
// Enable Yoast SEO fields in REST API
function enable_yoast_rest_api() {
    $post_types = ['post', 'page', 'property'];
    foreach ($post_types as $type) {
        register_post_meta($type, '_yoast_wpseo_focuskw', [
            'show_in_rest' => true,
            'single' => true,
            'type' => 'string'
        ]);
        register_post_meta($type, '_yoast_wpseo_metadesc', [
            'show_in_rest' => true,
            'single' => true,
            'type' => 'string'
        ]);
        register_post_meta($type, '_yoast_wpseo_title', [
            'show_in_rest' => true,
            'single' => true,
            'type' => 'string'
        ]);
    }
}
add_action('init', 'enable_yoast_rest_api');
```

## Stock Photo Integration

### Pexels API
- **API Key:** Store in `/root/.pexels-api-key`
- **Search:** `curl -H "Authorization: API_KEY" "https://api.pexels.com/v1/search?query=TERM&per_page=5"`
- **Download:** Use the `src.large` or `src.original` URL from response

### Unsplash API
- **API Key:** Store in `/root/.unsplash-api-key`
- **Search:** `curl "https://api.unsplash.com/search/photos?query=TERM&client_id=API_KEY"`

## Scripts

### wp-page.py
Creates a WordPress page with optional SEO and featured image.

**Usage:**
```bash
python3 /root/.claude/skills/wordpress-admin/scripts/wp-page.py \
  --site local \
  --title "Privacy Policy" \
  --slug "privacy-policy" \
  --template "page-privacy-policy.php" \
  --focus-kw "privacy policy" \
  --meta-desc "Description here"
```

### wp-seo.py
Sets Yoast SEO fields for existing posts/pages.

**Usage:**
```bash
python3 /root/.claude/skills/wordpress-admin/scripts/wp-seo.py \
  --site local \
  --post-id 123 \
  --focus-kw "keyword" \
  --meta-desc "Description" \
  --seo-title "SEO Title"
```

### wp-media.py
Downloads stock photo and uploads to WordPress.

**Usage:**
```bash
python3 /root/.claude/skills/wordpress-admin/scripts/wp-media.py \
  --site local \
  --search "miami skyline" \
  --set-featured 123
```

## Docker Management

### Start Local WordPress
```bash
cd /root/csrdevelopment.com/wordpress-local && docker-compose up -d
```

### Stop Local WordPress
```bash
cd /root/csrdevelopment.com/wordpress-local && docker-compose down
```

### View Logs
```bash
docker logs wordpress-local-wordpress-1 -f
```

### Reset Database
```bash
cd /root/csrdevelopment.com/wordpress-local && docker-compose down -v && docker-compose up -d
```

## FTP Sync (Production)

### Sync Theme Files
```bash
/root/csrdevelopment.com/sync-to-remote.sh
```

### Upload Single File
```bash
lftp -u "alfonso@csrdevelopment.com",'@#s;v1#%1M$+' ftp.csrdevelopment.com << 'EOF'
set ssl:verify-certificate no
cd /public_html/wp-content/themes/csr-theme
put /root/csrdevelopment.com/csrdevelopment.com/public_html/wp-content/themes/csr-theme/FILE.php
bye
EOF
```

## Common Tasks

### Create Privacy Policy Page
1. Create page with slug `privacy-policy`
2. Set template to `page-privacy-policy.php`
3. Set focus keyphrase: "CSR privacy policy"
4. Set meta description (~155 chars with keyphrase)
5. Upload relevant featured image

### Create Terms of Service Page
1. Create page with slug `terms`
2. Set template to `page-terms.php`
3. Set focus keyphrase: "CSR terms of service"
4. Set meta description (~155 chars with keyphrase)
5. Upload relevant featured image

## Reference

- **WordPress REST API:** https://developer.wordpress.org/rest-api/
- **WP-CLI Commands:** https://developer.wordpress.org/cli/commands/
- **Yoast SEO API:** https://developer.yoast.com/customization/apis/
- **Pexels API:** https://www.pexels.com/api/documentation/
