# Where to put the Asyntai snippet, by stack

`SNIPPET` below means the official snippet from SKILL.md, with the real widget
ID in place of `YOUR_WIDGET_ID`. Add it once, in the layout that every page
shares.

Some stacks cannot hold an inline script easily (JSX, for example). For those,
use the short form below. It loads the same widget and reads the same ID:

```html
<script async src="https://widget.asyntai.com/static/js/chat-widget.js" data-asyntai-id="YOUR_WIDGET_ID"></script>
```

## Asyntai packages (use these first)

For these tools, an Asyntai package does the install. Its guide has the exact
config.

| Stack | Package | Guide |
| --- | --- | --- |
| Astro | `astro-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/astro/ |
| Astro Starlight | `starlight-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/starlight/ |
| Nuxt | `nuxt-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/nuxt/ |
| Gatsby | `gatsby-plugin-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/gatsby/ |
| Docusaurus | `docusaurus-plugin-asyntai` (npm) | https://asyntai.com/documentation/integrations/docusaurus/ |
| Eleventy (11ty) | `eleventy-plugin-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/eleventy/ |
| VuePress | `vuepress-plugin-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/vuepress/ |
| docsify | `docsify-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/docsify/ |
| Hexo | `hexo-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/hexo/ |
| TypeDoc | `typedoc-plugin-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/typedoc/ |
| Slidev | `slidev-addon-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/slidev/ |
| Storybook | `storybook-addon-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/storybook/ |
| Ember | `ember-ai-chatbot` (npm) | https://asyntai.com/documentation/integrations/ember/ |
| MkDocs | `mkdocs-ai-chatbot` (PyPI) | https://asyntai.com/documentation/integrations/mkdocs/ |
| Lektor | `lektor-ai-chatbot` (PyPI) | https://asyntai.com/documentation/integrations/lektor/ |
| Wagtail | `wagtail-ai-chatbot` (PyPI) | https://asyntai.com/documentation/integrations/wagtail/ |
| Quarto | `quarto add asyntai/quarto-asyntai-ai-chatbot` | https://asyntai.com/documentation/integrations/quarto/ |
| Bridgetown | `bridgetown-ai-chatbot` (RubyGems) | https://asyntai.com/documentation/integrations/bridgetown/ |
| Laravel Filament | `asyntai/filament-ai-chatbot` (Composer) | https://asyntai.com/documentation/integrations/filament/ |
| Neos CMS | `asyntai/neos-ai-chatbot` (Composer) | https://asyntai.com/documentation/integrations/neos/ |
| Payload CMS | see guide | https://asyntai.com/documentation/integrations/payload/ |
| Halo | see guide | https://asyntai.com/documentation/integrations/halo/ |
| Thelia | see guide | https://asyntai.com/documentation/integrations/thelia/ |

If the user prefers no new dependency, the snippet in the shared layout also
works for all of these.

## Plain HTML

Paste `SNIPPET` just before `</body>` in every page, or in the shared header or
footer include if the site has one.

## Vite apps (React, Vue, Svelte, Solid, Preact, vanilla)

Edit `index.html` in the project root. Paste `SNIPPET` just before `</body>`.

## Create React App

Edit `public/index.html`. Paste `SNIPPET` just before `</body>`.

## Angular

Edit `src/index.html`. Paste `SNIPPET` just before `</body>`.

## Next.js (App Router)

Edit `app/layout.tsx` (or `app/layout.js`). Use `next/script`:

```tsx
import Script from "next/script";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Script
          src="https://widget.asyntai.com/static/js/chat-widget.js"
          data-asyntai-id="YOUR_WIDGET_ID"
          strategy="lazyOnload"
        />
      </body>
    </html>
  );
}
```

Keep the rest of the existing layout. Add only the import and the `<Script>`.

## Next.js (Pages Router)

Edit `pages/_app.tsx` (or `pages/_app.js`). Add the same `<Script>` element
after `<Component {...pageProps} />`, inside a fragment.

## SvelteKit

Edit `src/app.html`. Paste `SNIPPET` just before `</body>`.

## Remix and React Router (framework mode)

Edit `app/root.tsx`. In the `Layout` (or the root component), add the short
form inside `<body>`, after `<Scripts />`:

```tsx
<script async src="https://widget.asyntai.com/static/js/chat-widget.js" data-asyntai-id="YOUR_WIDGET_ID" />
```

## Astro without the package

In the base layout (often `src/layouts/Layout.astro`), paste `SNIPPET` before
`</body>` and add `is:inline` to the opening tag: `<script is:inline>`.
Without `is:inline`, Astro bundles the script and changes it.

## Server templates

Paste `SNIPPET` before `</body>` in the base template:

- Laravel: `resources/views/layouts/app.blade.php` (or the main layout)
- Django: `templates/base.html`
- Flask or Jinja: `templates/base.html`
- Ruby on Rails: `app/views/layouts/application.html.erb`
- Express with EJS, Pug or Handlebars: the shared layout or footer partial
- Plain PHP: the shared `footer.php`
- Hugo: `layouts/_default/baseof.html` or the footer partial
- Jekyll: `_layouts/default.html` or `_includes/footer.html`

## A site on a hosted platform

Use the platform guide in [platforms.md](platforms.md). For WordPress,
Shopify, Wix and most builders, the user installs the widget in the admin, not
in code.
