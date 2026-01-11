# Recommended WordPress Plugins

Essential plugins to install on every WordPress project for optimal performance, security, SEO, and client experience.

## Core Stack (Always Install)

### 1. Admin and Site Enhancements (ASE)
**Purpose**: All-in-one admin optimization, white labeling, security, and performance

| Feature | Description |
|---------|-------------|
| White Label | Custom admin logo, footer text, login page branding |
| Login Security | Custom login URL, CAPTCHA, login attempt limits |
| Admin Cleanup | Hide notices, disable widgets, organize menus |
| Performance | Heartbeat control, revision limits, image optimization |
| Security | Disable XML-RPC, obfuscate author slugs, email protection |

**Why**: Replaces 10+ single-purpose plugins. Essential for professional client delivery.

```
Plugin: Admin and Site Enhancements (ASE)
Author: Bowo
URL: https://wordpress.org/plugins/admin-site-enhancements/
Pro: https://www.wpase.com/
```

### 2. LiteSpeed Cache
**Purpose**: Page caching, CDN integration, image optimization

| Feature | Description |
|---------|-------------|
| Page Cache | Full page caching with ESI support |
| Object Cache | Database query caching |
| Image Optimization | WebP conversion, lazy loading |
| CDN | Built-in CDN (QUIC.cloud) or custom CDN |
| Database Optimization | Clean up transients, revisions |

**Why**: Best performance plugin for LiteSpeed servers. Works on any server with reduced features.

```
Plugin: LiteSpeed Cache
Author: LiteSpeed Technologies
URL: https://wordpress.org/plugins/litespeed-cache/
Active Installs: 7 million
```

### 3. Yoast SEO
**Purpose**: On-page SEO, sitemaps, schema markup

| Feature | Description |
|---------|-------------|
| Content Analysis | Readability and SEO scoring |
| Meta Tags | Title, description, OG tags |
| Sitemaps | XML sitemap generation |
| Schema | Structured data markup |
| Breadcrumbs | Navigation breadcrumbs |

**Why**: Industry standard for SEO. Comprehensive and well-maintained.

```
Plugin: Yoast SEO
Author: Yoast
URL: https://wordpress.org/plugins/wordpress-seo/
Active Installs: 10 million
```

### 4. WP Mail SMTP
**Purpose**: Reliable email delivery via SMTP

| Feature | Description |
|---------|-------------|
| SMTP Setup | Configure external mail server |
| Email Logging | Track sent emails |
| Multiple Providers | SendGrid, Mailgun, Amazon SES, etc. |
| Debugging | Test email configuration |

**Why**: WordPress default mail often fails. SMTP ensures delivery.

```
Plugin: WP Mail SMTP
Author: WPForms
URL: https://wordpress.org/plugins/wp-mail-smtp/
Active Installs: 4 million
```

### 5. Solid Security (formerly iThemes Security)
**Purpose**: Comprehensive security hardening

| Feature | Description |
|---------|-------------|
| Brute Force Protection | Login attempt limits |
| Two-Factor Auth | 2FA for admin accounts |
| File Change Detection | Monitor for malware |
| Security Hardening | Hide login, disable file editing |
| Database Backups | Scheduled backups |

**Why**: Enterprise-grade security. Covers all attack vectors.

```
Plugin: Solid Security
Author: StellarWP
URL: https://wordpress.org/plugins/better-wp-security/
Active Installs: 800,000
```

### 6. EWWW Image Optimizer
**Purpose**: Image compression and WebP conversion

| Feature | Description |
|---------|-------------|
| Lossless Compression | Reduce file size without quality loss |
| WebP Conversion | Modern format for faster loading |
| Lazy Loading | Defer off-screen images |
| Bulk Optimization | Optimize existing media library |
| CDN Integration | ExactDN CDN option |

**Why**: Images are often the largest page weight. Critical for Core Web Vitals.

```
Plugin: EWWW Image Optimizer
Author: nosilver4u
URL: https://wordpress.org/plugins/ewww-image-optimizer/
Active Installs: 1 million
```

---

## Management & Workflow

### 7. ManageWP Worker
**Purpose**: Remote site management from ManageWP dashboard

| Feature | Description |
|---------|-------------|
| Centralized Updates | Manage all sites from one dashboard |
| Backups | Cloud backup to Dropbox, S3, etc. |
| Uptime Monitoring | Get notified of downtime |
| Performance Checks | PageSpeed insights |
| Client Reports | White-label reports |

**Why**: Essential for agencies managing multiple sites.

```
Plugin: ManageWP Worker
Author: GoDaddy
URL: https://wordpress.org/plugins/worker/
Active Installs: 1 million
```

### 8. Site Kit by Google
**Purpose**: Connect Google services (Analytics, Search Console, AdSense)

| Feature | Description |
|---------|-------------|
| Analytics Dashboard | View stats in WordPress |
| Search Console | Monitor search performance |
| PageSpeed Insights | Core Web Vitals |
| AdSense | Ad performance (if applicable) |

**Why**: Single plugin for all Google integrations. Easy setup with OAuth.

```
Plugin: Site Kit by Google
Author: Google
URL: https://wordpress.org/plugins/google-site-kit/
Active Installs: 5 million
```

### 9. WP Activity Log
**Purpose**: Audit trail of all user and system activity

| Feature | Description |
|---------|-------------|
| User Activity | Track logins, content changes |
| System Changes | Plugin/theme updates, settings changes |
| Security Monitoring | Failed logins, user enumeration attempts |
| Reports | Generate activity reports |

**Why**: Essential for security audits and troubleshooting. Know who changed what.

```
Plugin: WP Activity Log
Author: Melapress
URL: https://wordpress.org/plugins/wp-security-audit-log/
Active Installs: 300,000
```

---

## Content & Media

### 10. Classic Editor
**Purpose**: Restore the classic TinyMCE editor

| Feature | Description |
|---------|-------------|
| Classic Editor | Traditional WYSIWYG editing |
| Per-User Setting | Allow users to choose editor |
| Disable Block Editor | Completely remove Gutenberg |

**Why**: Many clients prefer the classic editor. Some themes require it.

```
Plugin: Classic Editor
Author: WordPress Contributors
URL: https://wordpress.org/plugins/classic-editor/
Active Installs: 9 million
```

### 11. Yoast Duplicate Post
**Purpose**: Clone posts, pages, and custom post types

| Feature | Description |
|---------|-------------|
| One-Click Clone | Duplicate any post type |
| Rewrite & Republish | Edit published content safely |
| Custom Settings | Control what gets copied |

**Why**: Huge time saver for creating similar content.

```
Plugin: Yoast Duplicate Post
Author: Yoast
URL: https://wordpress.org/plugins/duplicate-post/
Active Installs: 4 million
```

### 12. Instant Images
**Purpose**: One-click stock photos from Unsplash, Pexels, Pixabay

| Feature | Description |
|---------|-------------|
| Multiple Sources | Unsplash, Pexels, Pixabay, Openverse, Giphy |
| Direct Upload | Download straight to Media Library |
| In-Editor Search | Find images while writing |
| Attribution | Automatic photographer credit |

**Why**: Fast access to free, high-quality stock photos without leaving WordPress.

```
Plugin: Instant Images
Author: Suspended Theme
URL: https://wordpress.org/plugins/instant-images/
Active Installs: 200,000
```

---

## Optional / Situational

### For Elementor Sites
**Style Kits for Elementor** - Advanced theme styles and design system management.

### For E-commerce
**WooCommerce** - Standard e-commerce solution.
**Stripe/PayPal** - Payment processing.

### For Forms
**WPForms** or **Gravity Forms** - Advanced form building.
**Contact Form 7** - Simple, free forms.

### For Multilingual
**WPML** or **Polylang** - Multi-language support.

### For Membership
**MemberPress** or **Restrict Content Pro** - Membership and access control.

---

## Plugin Installation Order

For optimal setup, install in this order:

1. **Solid Security** - Secure the site first
2. **LiteSpeed Cache** - Enable caching early
3. **EWWW Image Optimizer** - Before uploading media
4. **Admin and Site Enhancements** - Configure admin experience
5. **Yoast SEO** - SEO foundation
6. **WP Mail SMTP** - Ensure email works
7. **WP Activity Log** - Start logging activity
8. **Site Kit by Google** - Connect analytics
9. **ManageWP Worker** - Enable remote management
10. **Content plugins** - Classic Editor, Instant Images, etc.

---

## Configuration Checklist

### After Installing All Plugins

#### Security
- [ ] Change login URL (ASE or Solid Security)
- [ ] Enable 2FA for admin accounts
- [ ] Set login attempt limits
- [ ] Disable XML-RPC
- [ ] Hide WordPress version

#### Performance
- [ ] Enable page caching
- [ ] Enable browser caching
- [ ] Configure image optimization
- [ ] Enable lazy loading
- [ ] Minify CSS/JS

#### SEO
- [ ] Configure Yoast settings
- [ ] Submit sitemap to Google Search Console
- [ ] Set up breadcrumbs
- [ ] Configure schema markup

#### Admin Experience
- [ ] White label admin (ASE)
- [ ] Customize login page
- [ ] Hide unnecessary menu items
- [ ] Disable dashboard widgets
- [ ] Configure admin footer text

#### Email
- [ ] Configure SMTP settings
- [ ] Test email delivery
- [ ] Set sender name/email

#### Monitoring
- [ ] Connect Google Analytics
- [ ] Set up uptime monitoring
- [ ] Configure activity log retention

---

## Sources

- [Admin and Site Enhancements (ASE)](https://wordpress.org/plugins/admin-site-enhancements/)
- [ASE Features](https://www.wpase.com/features/)
- [LiteSpeed Cache](https://wordpress.org/plugins/litespeed-cache/)
- [Yoast SEO](https://wordpress.org/plugins/wordpress-seo/)
- [WP Mail SMTP](https://wordpress.org/plugins/wp-mail-smtp/)
- [Solid Security](https://wordpress.org/plugins/better-wp-security/)
- [EWWW Image Optimizer](https://wordpress.org/plugins/ewww-image-optimizer/)
