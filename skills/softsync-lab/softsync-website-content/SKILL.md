---
name: softsync-website-content
description: "Use the workspace as the content system of a website: read published articles and pages, add drafts, upload pictures and videos, and write the text. Use when the user builds or edits a website whose content lives in the workspace (the CMS template), or asks for a blog post, page text or a video on it."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Website content

The CMS template keeps a site's articles (`posts`) and their sections (`post_sections`) as ordinary tables. A site shows the rows whose `status` is `published`.

## Do this
1. Call `describe_workspace_schema` to see the tables and fields the workspace really has, including any extra content tables.
2. Add an article as a row of `posts` with `record_creation`, always as a draft, then its sections and questions as rows that point at it. Read before you change: use `search_records` and `get_record_by_id`, and change only what was asked with `update_record`.
3. Pictures and videos inside the text are standard Markdown: `![description](url){width=600 align=center}`, and a YouTube, Vimeo or Loom link on a line of its own is a player. Read the `using-softsync-as-cms` reference for the full syntax and for how to teach it to the AI tool building the site.

## Rules
- Never publish: leave `status` as draft for the team to review.
- Ask before replacing text a person wrote.
- Never invent facts, figures, quotes or sources.

## More detail
Read these when the task needs them:
- [using-softsync-as-cms](references/using-softsync-as-cms.md): The full guide to hand to an AI website builder: reading and writing content over the API, uploading files, Markdown pictures, sizes and video embeds, and writing clear page content.
