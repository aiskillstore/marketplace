---
name: wp-playground
description: WordPress Playground for instant browser-based WordPress testing. Use for quick demos, plugin testing, or ephemeral development environments without Docker.
allowed-tools: Bash, Read, Write, WebFetch
---

# WordPress Playground Skill

Instant WordPress environments in the browser using WebAssembly. Zero setup, no server required.

## Quick Start

### Browser Access

Visit: https://playground.wordpress.net/

### CLI (Node.js)

```bash
# Start local Playground server
npx @wp-playground/cli server

# With custom blueprint
npx @wp-playground/cli server --blueprint=./blueprint.json

# Specify versions
npx @wp-playground/cli server --wp=6.8 --php=8.3
```

---

## Blueprints

Blueprints are JSON files that define the WordPress environment setup.

### Blueprint Structure

```json
{
  "$schema": "https://playground.wordpress.net/blueprint-schema.json",
  "landingPage": "/wp-admin/",
  "login": true,
  "preferredVersions": {
    "php": "8.3",
    "wp": "latest"
  },
  "phpExtensionBundles": ["kitchen-sink"],
  "features": {
    "networking": true
  },
  "steps": []
}
```

### Available Steps

| Step | Purpose | Example |
|------|---------|---------|
| `installPlugin` | Install plugin from wp.org | `{"step":"installPlugin","pluginData":{"resource":"wordpress.org/plugins","slug":"yoast-seo"}}` |
| `installTheme` | Install theme from wp.org | `{"step":"installTheme","themeData":{"resource":"wordpress.org/themes","slug":"astra"}}` |
| `setSiteOptions` | Update wp_options | `{"step":"setSiteOptions","options":{"blogname":"Test"}}` |
| `login` | Login as user | `{"step":"login","username":"admin","password":"password"}` |
| `runPHP` | Execute PHP code | `{"step":"runPHP","code":"<?php echo 'Hello'; ?>"}` |
| `wp-cli` | Run WP-CLI command | `{"step":"wp-cli","command":"plugin list"}` |
| `writeFile` | Create/modify file | `{"step":"writeFile","path":"/index.html","data":"content"}` |
| `mkdir` | Create directory | `{"step":"mkdir","path":"/wp-content/uploads/test"}` |

---

## Pre-Built Blueprints

### Base Development Blueprint

Full development environment with essential plugins:

```json
{
  "$schema": "https://playground.wordpress.net/blueprint-schema.json",
  "landingPage": "/wp-admin/",
  "login": true,
  "preferredVersions": {
    "php": "8.3",
    "wp": "latest"
  },
  "steps": [
    {
      "step": "installPlugin",
      "pluginData": { "resource": "wordpress.org/plugins", "slug": "admin-site-enhancements" },
      "options": { "activate": true }
    },
    {
      "step": "installPlugin",
      "pluginData": { "resource": "wordpress.org/plugins", "slug": "branda-white-labeling" },
      "options": { "activate": true }
    },
    {
      "step": "installPlugin",
      "pluginData": { "resource": "wordpress.org/plugins", "slug": "wordpress-seo" },
      "options": { "activate": true }
    },
    {
      "step": "installPlugin",
      "pluginData": { "resource": "wordpress.org/plugins", "slug": "instant-images" },
      "options": { "activate": true }
    },
    {
      "step": "setSiteOptions",
      "options": {
        "blogname": "Development Site",
        "blogdescription": "WordPress Playground Environment",
        "permalink_structure": "/%postname%/"
      }
    }
  ]
}
```

### WooCommerce Testing Blueprint

```json
{
  "$schema": "https://playground.wordpress.net/blueprint-schema.json",
  "landingPage": "/wp-admin/admin.php?page=wc-admin",
  "login": true,
  "preferredVersions": {
    "php": "8.3",
    "wp": "latest"
  },
  "steps": [
    {
      "step": "installPlugin",
      "pluginData": { "resource": "wordpress.org/plugins", "slug": "woocommerce" },
      "options": { "activate": true }
    },
    {
      "step": "installTheme",
      "themeData": { "resource": "wordpress.org/themes", "slug": "storefront" },
      "options": { "activate": true }
    }
  ]
}
```

### Theme Development Blueprint

```json
{
  "$schema": "https://playground.wordpress.net/blueprint-schema.json",
  "landingPage": "/",
  "login": true,
  "preferredVersions": {
    "php": "8.3",
    "wp": "latest"
  },
  "steps": [
    {
      "step": "installTheme",
      "themeData": { "resource": "wordpress.org/themes", "slug": "developer" },
      "options": { "activate": true }
    },
    {
      "step": "installPlugin",
      "pluginData": { "resource": "wordpress.org/plugins", "slug": "theme-check" },
      "options": { "activate": true }
    },
    {
      "step": "installPlugin",
      "pluginData": { "resource": "wordpress.org/plugins", "slug": "developer" },
      "options": { "activate": true }
    }
  ]
}
```

---

## CLI Commands

### Basic Usage

```bash
# Start with defaults
npx @wp-playground/cli server

# Custom port
npx @wp-playground/cli server --port=3000

# Specific WordPress version
npx @wp-playground/cli server --wp=6.7

# PHP version
npx @wp-playground/cli server --php=8.2

# Blueprint file
npx @wp-playground/cli server --blueprint=./my-blueprint.json

# Auto-mount current directory as plugin/theme
npx @wp-playground/cli server --auto-mount
```

### Building Snapshots

```bash
# Build ZIP snapshot from blueprint
npx @wp-playground/cli build-snapshot blueprint.json output.zip

# Use snapshot
npx @wp-playground/cli server --mount=./output.zip
```

### Directory Mounting

```bash
# Mount local plugin
npx @wp-playground/cli server \
  --mount=/local/plugin:/var/www/html/wp-content/plugins/my-plugin

# Mount local theme
npx @wp-playground/cli server \
  --mount=/local/theme:/var/www/html/wp-content/themes/my-theme
```

---

## URL Parameters

For quick browser-based testing, use URL parameters:

```
# Install plugin
https://playground.wordpress.net/?plugin=woocommerce

# Install multiple plugins
https://playground.wordpress.net/?plugin=woocommerce&plugin=yoast-seo

# Install theme
https://playground.wordpress.net/?theme=astra

# Specific versions
https://playground.wordpress.net/?wp=6.7&php=8.3

# Go to admin
https://playground.wordpress.net/?mode=seamless&login=yes

# Use blueprint URL
https://playground.wordpress.net/?blueprint-url=https://example.com/blueprint.json
```

---

## JavaScript API

For programmatic control:

```javascript
import { startPlayground } from '@wp-playground/client';

const playground = await startPlayground({
  iframe: document.getElementById('wp-frame'),
  blueprint: {
    landingPage: '/wp-admin/',
    login: true,
    steps: [
      {
        step: 'installPlugin',
        pluginData: { resource: 'wordpress.org/plugins', slug: 'woocommerce' },
        options: { activate: true }
      }
    ]
  }
});

// Run WP-CLI commands
const result = await playground.run({
  step: 'wp-cli',
  command: 'plugin list'
});
console.log(result);
```

---

## Use Cases

### Quick Plugin Testing

1. Write blueprint with plugin to test
2. Run `npx @wp-playground/cli server --blueprint=./test-blueprint.json`
3. Test in browser
4. Close when done (no cleanup needed)

### Theme Preview

1. Mount local theme directory
2. Make changes
3. See instant updates in browser
4. No server restart needed

### Client Demos

1. Create blueprint with client's preferred setup
2. Share URL with blueprint parameter
3. Client sees instant demo
4. No hosting required

### Plugin Development

1. Use `--auto-mount` to mount current directory
2. Changes reflect immediately
3. Debug with browser tools
4. Export snapshot for sharing

---

## Limitations

- **Ephemeral**: Data lost when browser closes (unless exported)
- **Performance**: Slower than native PHP (runs in WebAssembly)
- **Networking**: Limited external HTTP requests
- **File Storage**: Browser storage limits apply
- **No Email**: Email sending not supported
- **No Cron**: WP-Cron runs on page load only

---

## Playground vs Docker

| Feature | Playground | Docker |
|---------|------------|--------|
| Setup time | Instant | 2-5 min |
| Persistence | Temporary | Permanent |
| Performance | Slower | Faster |
| Server required | No | Yes |
| Use case | Testing, demos | Development |
| Networking | Limited | Full |
| Email | No | Yes (with SMTP) |
| WP-CLI | Limited | Full |

**Use Playground for**: Quick testing, demos, client previews, plugin trials

**Use Docker for**: Full development, production-like testing, persistent data

---

## Templates Location

Blueprints are in: `~/.claude/skills/wp-playground/blueprints/`

- `base.json` - Standard development setup
- `woocommerce.json` - E-commerce testing
- `theme-dev.json` - Theme development

---

## Related Skills

- **wp-docker**: Full Docker development environment
- **white-label**: Plugin configuration for branding
- **wordpress-admin**: Content and settings management
