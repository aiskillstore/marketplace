---
name: wp-performance
description: WordPress performance optimization - Core Web Vitals, image/video compression, caching, asset optimization, and speed testing. Use when optimizing site speed or diagnosing performance issues.
allowed-tools: Read, Write, Edit, Bash, WebFetch, WebSearch
---

# WordPress Performance Optimization

Complete guide for optimizing WordPress site performance, Core Web Vitals, and passing speed tests.

## Core Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | 2.5-4s | >4s |
| **INP** (Interaction to Next Paint) | ≤200ms | 200-500ms | >500ms |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 |

---

## Image Optimization

### Plugin Stack

1. **EWWW Image Optimizer** - Best all-around
   - Lossless & lossy compression
   - WebP conversion
   - Lazy loading
   - CDN option (ExactDN)

2. **ShortPixel** - Alternative with more formats
   - AVIF support
   - Glossy/lossy/lossless modes
   - Bulk optimization

3. **Imagify** - Simple and effective
   - Three compression levels
   - WebP conversion
   - Resize on upload

### EWWW Configuration

```php
// Recommended EWWW settings via wp-config.php or plugin settings

// Enable WebP conversion
define('EWWW_IMAGE_OPTIMIZER_WEBP', true);

// Set maximum dimensions
define('EWWW_IMAGE_OPTIMIZER_MAX_WIDTH', 2560);
define('EWWW_IMAGE_OPTIMIZER_MAX_HEIGHT', 2560);

// Enable lazy loading
define('EWWW_IMAGE_OPTIMIZER_LAZY_LOAD', true);
```

### Manual Image Guidelines

| Use Case | Format | Max Width | Quality |
|----------|--------|-----------|---------|
| Hero images | WebP (fallback JPG) | 1920px | 80-85% |
| Content images | WebP (fallback JPG) | 1200px | 80% |
| Thumbnails | WebP | 600px | 75% |
| Icons/logos | SVG or PNG | As needed | Lossless |
| Photos with transparency | WebP or PNG | As needed | 85% |

### Responsive Images

WordPress generates srcset automatically. Ensure proper sizes:

```php
// Add custom image sizes
function theme_custom_image_sizes() {
    add_image_size('hero', 1920, 1080, true);
    add_image_size('hero-tablet', 1024, 768, true);
    add_image_size('hero-mobile', 768, 1024, true);
    add_image_size('card', 600, 400, true);
    add_image_size('thumb-square', 300, 300, true);
}
add_action('after_setup_theme', 'theme_custom_image_sizes');
```

### Preload Critical Images

```php
// Preload LCP image
function theme_preload_hero() {
    if (is_front_page()) {
        $hero_url = get_theme_file_uri('/assets/images/hero.webp');
        echo '<link rel="preload" as="image" href="' . esc_url($hero_url) . '">';
    }
}
add_action('wp_head', 'theme_preload_hero', 1);
```

---

## Video Optimization

### Self-Hosted Video

1. **Compress before upload**
   - Use HandBrake or FFmpeg
   - Target: 1-2 MB per minute for web
   - Resolution: 1080p max (720p for backgrounds)
   - Codec: H.264 (MP4) for compatibility, H.265 for smaller size

2. **FFmpeg commands**

```bash
# Compress video for web (H.264, CRF 23 = good quality)
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset slow -c:a aac -b:a 128k output.mp4

# Create WebM version (smaller, modern browsers)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm

# Extract poster image
ffmpeg -i input.mp4 -ss 00:00:01 -vframes 1 poster.jpg

# Resize to 720p
ffmpeg -i input.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 output-720p.mp4
```

3. **HTML with fallbacks**

```html
<video autoplay muted loop playsinline poster="poster.jpg">
    <source src="video.webm" type="video/webm">
    <source src="video.mp4" type="video/mp4">
</video>
```

### External Video Hosting

For longer videos, use:
- **YouTube** - Free, good performance, ads
- **Vimeo** - Ad-free, professional
- **Bunny Stream** - Cheap, fast CDN
- **Cloudflare Stream** - Good for high traffic

### Lazy Load Videos

```javascript
// Lazy load video on scroll
const videoObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const video = entry.target;
            video.src = video.dataset.src;
            video.load();
            videoObserver.unobserve(video);
        }
    });
});

document.querySelectorAll('video[data-src]').forEach(video => {
    videoObserver.observe(video);
});
```

---

## Caching

### LiteSpeed Cache Configuration

```php
// wp-config.php settings
define('LITESPEED_ON', true);
define('LITESPEED_CACHE_DIR', WP_CONTENT_DIR . '/cache/litespeed/');
```

**Recommended LiteSpeed Settings:**

| Setting | Value |
|---------|-------|
| Enable Cache | On |
| Cache Logged-in Users | Off (unless needed) |
| Cache Mobile | On |
| TTL | 604800 (7 days) |
| Browser Cache | On |
| Browser Cache TTL | 31557600 (1 year) |
| Minify CSS | On |
| Minify JS | On |
| Combine CSS | Test carefully |
| Combine JS | Test carefully |
| HTTP/2 Push | CSS, JS |
| Lazy Load Images | On |
| WebP Replacement | On (if EWWW handles it, disable here) |

### Object Cache (Redis)

```php
// wp-config.php
define('WP_REDIS_HOST', '127.0.0.1');
define('WP_REDIS_PORT', 6379);
define('WP_REDIS_DATABASE', 0);
define('WP_CACHE', true);

// Install Redis Object Cache plugin
```

### Transient Caching

```php
// Cache expensive queries
function get_featured_properties() {
    $cache_key = 'featured_properties';
    $properties = get_transient($cache_key);

    if (false === $properties) {
        $properties = new WP_Query([
            'post_type' => 'property',
            'posts_per_page' => 6,
            'meta_key' => '_featured',
            'meta_value' => '1'
        ]);

        set_transient($cache_key, $properties, HOUR_IN_SECONDS);
    }

    return $properties;
}

// Clear cache on update
function clear_property_cache($post_id) {
    if ('property' === get_post_type($post_id)) {
        delete_transient('featured_properties');
    }
}
add_action('save_post', 'clear_property_cache');
```

---

## Asset Optimization

### CSS Optimization

```php
// Remove unused block styles
function theme_remove_block_styles() {
    wp_dequeue_style('wp-block-library');
    wp_dequeue_style('wp-block-library-theme');
    wp_dequeue_style('global-styles');
}
add_action('wp_enqueue_scripts', 'theme_remove_block_styles', 100);

// Defer non-critical CSS
function theme_defer_styles($html, $handle, $href, $media) {
    $defer_handles = ['theme-animations', 'font-awesome'];

    if (in_array($handle, $defer_handles)) {
        return '<link rel="preload" as="style" href="' . $href . '" onload="this.onload=null;this.rel=\'stylesheet\'">' .
               '<noscript><link rel="stylesheet" href="' . $href . '"></noscript>';
    }

    return $html;
}
add_filter('style_loader_tag', 'theme_defer_styles', 10, 4);
```

### JavaScript Optimization

```php
// Defer scripts
function theme_defer_scripts($tag, $handle, $src) {
    $defer_scripts = ['theme-main', 'gsap', 'gsap-scrolltrigger'];

    if (in_array($handle, $defer_scripts)) {
        return str_replace(' src', ' defer src', $tag);
    }

    return $tag;
}
add_filter('script_loader_tag', 'theme_defer_scripts', 10, 3);

// Remove jQuery if not needed
function theme_remove_jquery() {
    if (!is_admin()) {
        wp_deregister_script('jquery');
        wp_deregister_script('jquery-migrate');
    }
}
add_action('wp_enqueue_scripts', 'theme_remove_jquery');
```

### Font Optimization

```php
// Preload fonts
function theme_preload_fonts() {
    $fonts = [
        '/assets/fonts/inter-var.woff2',
        '/assets/fonts/playfair-display.woff2'
    ];

    foreach ($fonts as $font) {
        echo '<link rel="preload" href="' . get_theme_file_uri($font) . '" as="font" type="font/woff2" crossorigin>';
    }
}
add_action('wp_head', 'theme_preload_fonts', 1);
```

```css
/* Use font-display: swap */
@font-face {
    font-family: 'Inter';
    src: url('fonts/inter-var.woff2') format('woff2');
    font-weight: 100 900;
    font-display: swap;
}
```

---

## Database Optimization

### Regular Maintenance

```sql
-- Delete old revisions (keep last 5)
DELETE FROM wp_posts WHERE post_type = 'revision'
AND ID NOT IN (
    SELECT * FROM (
        SELECT ID FROM wp_posts WHERE post_type = 'revision'
        ORDER BY post_date DESC LIMIT 5
    ) AS t
);

-- Delete expired transients
DELETE FROM wp_options WHERE option_name LIKE '%_transient_%'
AND option_value < UNIX_TIMESTAMP();

-- Delete orphaned postmeta
DELETE pm FROM wp_postmeta pm
LEFT JOIN wp_posts p ON pm.post_id = p.ID
WHERE p.ID IS NULL;

-- Optimize tables
OPTIMIZE TABLE wp_posts, wp_postmeta, wp_options, wp_comments, wp_commentmeta;
```

### WP-CLI Commands

```bash
# Delete revisions
wp post delete $(wp post list --post_type=revision --format=ids)

# Delete transients
wp transient delete --expired

# Optimize database
wp db optimize

# Search-replace for migrations
wp search-replace 'old-domain.com' 'new-domain.com' --dry-run
```

### Limit Revisions

```php
// wp-config.php
define('WP_POST_REVISIONS', 5);
// Or disable completely
define('WP_POST_REVISIONS', false);
```

---

## CDN Configuration

### Cloudflare Settings

| Setting | Value |
|---------|-------|
| SSL/TLS | Full (Strict) |
| Always Use HTTPS | On |
| Auto Minify | CSS, JS (test first) |
| Brotli | On |
| Browser Cache TTL | 4 hours to 1 year |
| Rocket Loader | Off (conflicts with GSAP) |
| Mirage | On (mobile image optimization) |
| Polish | Lossy (image optimization) |
| WebP | On |

### Origin Headers

```apache
# .htaccess - Cache headers
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType font/woff2 "access plus 1 year"
</IfModule>

# Enable Gzip/Brotli
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/css
    AddOutputFilterByType DEFLATE application/javascript application/json
    AddOutputFilterByType DEFLATE image/svg+xml
</IfModule>
```

---

## Speed Testing

### Tools

1. **PageSpeed Insights** - https://pagespeed.web.dev
2. **GTmetrix** - https://gtmetrix.com
3. **WebPageTest** - https://webpagetest.org
4. **Chrome DevTools** - Lighthouse audit

### Command Line Testing

```bash
# Using Lighthouse CLI
npm install -g lighthouse
lighthouse https://example.com --output=html --output-path=./report.html

# Using WebPageTest API
curl "https://www.webpagetest.org/runtest.php?url=https://example.com&f=json&k=YOUR_API_KEY"
```

### Automated Speed Monitoring

```python
#!/usr/bin/env python3
"""
Speed test automation using PageSpeed Insights API
"""
import requests
import json

def test_pagespeed(url, api_key=None):
    endpoint = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
    params = {
        'url': url,
        'strategy': 'mobile',
        'category': ['performance', 'accessibility', 'best-practices', 'seo']
    }
    if api_key:
        params['key'] = api_key

    response = requests.get(endpoint, params=params)
    data = response.json()

    lighthouse = data['lighthouseResult']
    categories = lighthouse['categories']

    return {
        'performance': int(categories['performance']['score'] * 100),
        'accessibility': int(categories['accessibility']['score'] * 100),
        'best_practices': int(categories['best-practices']['score'] * 100),
        'seo': int(categories['seo']['score'] * 100),
        'lcp': lighthouse['audits']['largest-contentful-paint']['displayValue'],
        'cls': lighthouse['audits']['cumulative-layout-shift']['displayValue'],
        'fcp': lighthouse['audits']['first-contentful-paint']['displayValue']
    }

if __name__ == '__main__':
    result = test_pagespeed('https://example.com')
    print(json.dumps(result, indent=2))
```

---

## Performance Checklist

### Images
- [ ] All images compressed
- [ ] WebP format with fallbacks
- [ ] Lazy loading enabled
- [ ] Responsive images (srcset)
- [ ] LCP image preloaded
- [ ] No images larger than needed

### Videos
- [ ] Compressed before upload
- [ ] Poster images set
- [ ] Lazy loaded if below fold
- [ ] Consider external hosting for long videos

### Caching
- [ ] Page caching enabled
- [ ] Browser caching configured
- [ ] Object cache (Redis) if high traffic
- [ ] CDN configured

### Assets
- [ ] CSS/JS minified
- [ ] Critical CSS inlined (optional)
- [ ] Unused CSS removed
- [ ] Scripts deferred
- [ ] Fonts preloaded with font-display: swap

### Database
- [ ] Revisions limited
- [ ] Expired transients cleaned
- [ ] Orphaned meta cleaned
- [ ] Autoload options reviewed

### Third Party
- [ ] Minimal plugins
- [ ] No render-blocking third-party scripts
- [ ] Analytics async/deferred
- [ ] Social embeds lazy loaded

---

## Quick Wins

1. **Enable caching** - Biggest impact
2. **Compress images** - Second biggest
3. **Use CDN** - Global performance
4. **Defer JS** - Improve LCP/FCP
5. **Preload fonts** - Reduce CLS
6. **Remove unused plugins** - Less bloat

---

## Resources

- [web.dev Performance](https://web.dev/performance/)
- [Core Web Vitals](https://web.dev/vitals/)
- [LiteSpeed Cache Docs](https://docs.litespeedtech.com/lscache/lscwp/)
- [Cloudflare Performance](https://developers.cloudflare.com/fundamentals/speed/)
