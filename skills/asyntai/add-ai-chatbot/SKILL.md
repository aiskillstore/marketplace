---
name: add-ai-chatbot
description: Add an AI chatbot (AI customer support agent and live chat widget) to a website or web app with Asyntai. Use when the user asks to add a chatbot, AI assistant, support chat, live chat or chat widget to a site, store, docs site or app, on any stack (HTML, React, Next.js, Vue, Nuxt, SvelteKit, Angular, Astro, Laravel, Django, Rails) or platform (WordPress, Shopify, Wix, Webflow, Squarespace and 100 more).
---

# Add an AI chatbot with Asyntai

[Asyntai](https://asyntai.com) adds an AI support agent to a website. It
answers visitors from the site's own content, in more than 80 languages, and
hands over to a human when needed. The chat runs from one script tag, so the
install is one small edit.

## Step 1: get the widget ID

Every install needs the site's widget ID. It looks like `asyntai_` followed by
12 letters and digits, for example `asyntai_1a2b3c4d5e6f`.

1. Look for an ID that the user already gave you, or that the project already
   has (search the code for `data-asyntai-id`). If the site already has the
   snippet, do not add a second one.
2. If the Asyntai MCP server is connected, call `list_websites`. Each website
   has a `widget_id`.
3. Otherwise ask the user for it. Tell them where it is: sign in at
   https://asyntai.com/dashboard, open the Install page, and copy the value of
   `data-asyntai-id` from the snippet.
4. If the user has no account, they can create one free at
   https://asyntai.com/auth/ . The Free plan is enough to try the chatbot.

Never invent a widget ID. If you have none, put the placeholder
`YOUR_WIDGET_ID` in the code and tell the user to replace it.

## Step 2: find what the site is built with

- **A hosted builder or CMS** (WordPress, Shopify, Wix, Webflow, Squarespace,
  HubSpot, Ghost, Moodle and others): the user installs the widget in that
  platform's admin, not in code. Find the platform in
  [references/platforms.md](references/platforms.md) and give the user that
  guide link and its short steps.
- **A codebase**: check `package.json`, the config files and the folder layout,
  then follow [references/frameworks.md](references/frameworks.md). It has the
  exact edit for each stack and the Asyntai packages for static site and docs
  tools.

## Step 3: add the snippet

This is the official snippet. Keep it exactly as shown and change only
`YOUR_WIDGET_ID`:

```html
<script>(function(){var l=function(){var s=document.createElement("script");s.src="https://widget.asyntai.com/static/js/chat-widget.js";s.async=true;s.setAttribute("data-asyntai-id","YOUR_WIDGET_ID");document.head.appendChild(s)};if(document.readyState==="complete"){l()}else{window.addEventListener("load",l)}})();</script>
```

It waits for the page `load` event, so it does not slow the page down. Put it
once, in the shared layout that every page uses (before `</body>` or in
`<head>`). Do not put it in one page component, or the chat shows on that page
only.

## Step 4: check the result

1. Run the site (or build it) and open a page.
2. The chat button shows in the bottom corner. The widget draws inside the
   element `#asyntai-widget-host-<widget ID>`. In the browser console,
   `document.querySelectorAll('script[data-asyntai-id]').length` must be `1`.
3. If the button does not show:
   - Check the browser console for `Asyntai Widget:` errors.
   - If the site sends a Content Security Policy, it must allow these sources:

     | Directive | Sources |
     | --- | --- |
     | `script-src` | `https://widget.asyntai.com https://asyntai.com` (and `'unsafe-inline'` for the snippet, or use the short form from references/frameworks.md) |
     | `connect-src` | `https://asyntai.com` |
     | `style-src` | `'unsafe-inline'` |
     | `img-src` | `data: https://flagcdn.com` |

## Step 5: tell the user what comes next

The widget answers from the content that the user adds in the Asyntai
dashboard (https://asyntai.com/dashboard). Tell the user to:

- add their website pages, files or text as knowledge,
- set the agent name, colors and greeting on the dashboard,
- read the full guide at https://asyntai.com/documentation/installation/ .

If the Asyntai MCP server is connected, you can do this setup for them. See the
`manage-ai-support-agent` skill.
