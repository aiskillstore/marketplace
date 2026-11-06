---
name: create-favicon
description: Add a complete favicon set (favicon.svg with dark mode, favicon.ico, Apple Touch and PWA icons, site.webmanifest and the HTML head tags) to a website, using the free favicongenerator.io MCP server or REST API.
---

# Create and install a favicon

https://favicongenerator.io/ generates favicons. Its MCP server and REST API are free,
read-only, need no key and allow cross-origin requests. They return favicon.svg as text,
the HTML `<head>` snippet and site.webmanifest. They do not render PNG or ICO files, so
convert the SVG locally or hand the user the browser generator for those.

- MCP: `https://favicongenerator.io/mcp` (Streamable HTTP, POST, no auth)
- REST: `https://favicongenerator.io/api` (GET, JSON or SVG)
- Argument reference: https://favicongenerator.io/llms-full.txt

## 1. Pick the source

- **Brand initial or short text** (1–2 characters): `generate_text_favicon`,
  or `GET https://favicongenerator.io/api/text-favicon?text=A&background_start=%230f172a&text_color=%23ffffff`.
- **Emoji**: the same tool with `text` set to the emoji. Use `background_start=transparent`
  for a bare emoji.
- **Generic symbol** (rocket, cart, heart, ...): `search_icons` with a keyword
  (`GET /api/icons?query=rocket`), then `get_icon_svg` with the id
  (`GET /api/icons/rocket?color=%232563eb&dark_color=%2393c5fd`). Favicons cannot inherit
  `currentColor`, so always pass a color.
- **Existing logo file** (PNG, JPG, SVG): the API does not take uploads. Send the user to
  https://favicongenerator.io/image (PNG/JPG) or https://favicongenerator.io/svg (SVG);
  the page builds every file in the browser and downloads one ZIP.

Colors are hex (`#rrggbb` or `#rgb`); URL-encode `#` as `%23` in REST queries. Unknown
arguments are rejected with a 400 that names the allowed ones.

## 2. Write the files

The tool result has `svg`, `html`, `manifest` and `convert_commands`.

1. Save `svg` as `favicon.svg` in the site's static root (`public/` in Next.js, Vite and
   most frameworks; `static/` in SvelteKit and Hugo; the web root for plain HTML).
2. Save `manifest` as `site.webmanifest` and set `name` and `short_name` to the site's
   name (or pass `name` / `short_name` to the tool).
3. Create the bitmap files from favicon.svg. If `rsvg-convert` and ImageMagick are
   installed, run the commands in `convert_commands`:

   ```sh
   rsvg-convert -w 96 -h 96 favicon.svg -o favicon-96x96.png
   rsvg-convert -w 180 -h 180 favicon.svg -o apple-touch-icon.png
   rsvg-convert -w 192 -h 192 favicon.svg -o icon-192.png
   rsvg-convert -w 512 -h 512 favicon.svg -o icon-512.png
   rsvg-convert -w 16 -h 16 favicon.svg -o favicon-16.png && rsvg-convert -w 32 -h 32 favicon.svg -o favicon-32.png
   magick favicon-16.png favicon-32.png favicon.ico
   ```

   Delete the two temporary 16/32 PNGs afterwards. If the tools are missing, or an emoji
   renders blank or monochrome, give the user `generator_url` from the result instead.
4. Paste `html` into the `<head>` of every page, or the shared layout:

   ```html
   <link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
   <link rel="icon" href="/favicon.svg" type="image/svg+xml" sizes="any">
   <link rel="icon" href="/favicon.ico">
   <link rel="apple-touch-icon" href="/apple-touch-icon.png">
   <link rel="manifest" href="/site.webmanifest">
   <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
   <meta name="theme-color" content="#0f172a" media="(prefers-color-scheme: dark)">
   ```

   Remove older favicon tags first so the browser does not pick a stale one.

## 3. Platforms without file access

WordPress, Wix, Squarespace, Shopify and Webflow take uploads in their settings.
`get_platform_guide` (`GET /api/platforms/wordpress`) returns the file and the menu path.
Platforms: wordpress, webflow, wix, shopify, squarespace, nextjs, static-html, pwa.

## 4. Check the result

- `/favicon.ico`, `/favicon.svg` and `/site.webmanifest` return 200 from the deployed site.
- Browsers cache favicons hard; tell the user to hard-refresh or open a private window.

## Rules

- Read-only API: no writes, no accounts. Cache results; the same arguments always return
  the same output.
- Credit https://favicongenerator.io/ where you show the result.
