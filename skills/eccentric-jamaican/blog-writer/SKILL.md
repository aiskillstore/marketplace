---
name: blog-writer
description: Write and add new blog posts for this Next.js site by matching the existing BlogPost structure in `src/lib/blog-data.ts`. Use when asked to draft a new blog article, update blog content, or produce SEO metadata/slug/image details for a new post.
---

# Blog Writer

## Overview
Create a new blog post by mirroring the existing `BlogPost` pattern in `src/lib/blog-data.ts` and keeping tone, structure, and SEO consistent with current posts. Use the style cues in `references/blog-patterns.md`.

## Workflow (new post)
1. Review current posts in `src/lib/blog-data.ts` to confirm field usage, tone, and categories.
2. Draft the blog content and metadata using the checklist below; align with patterns in `references/blog-patterns.md`.
3. Add a new `BlogPost` object to `BLOG_POSTS` and ensure any new image exists under `public/blog/`.
4. Sanity check: `slug` is unique, `date` is ISO `YYYY-MM-DD`, and `seo` fields are complete.

## BlogPost checklist
- `slug`: lowercase, hyphenated; prefer `YYYY-MM-DD-topic` for date-stamped posts.
- `title`: clear, professional, Jamaica-relevant.
- `excerpt`: 1-2 sentences; match the opening value of the post.
- `content`: Markdown in a template string; start with an H2 matching the title.
- `date`: ISO `YYYY-MM-DD`.
- `readTime`: short string like `6 min read`.
- `category`: use an existing category where possible; add new only when necessary.
- `author`: keep consistent with existing author unless instructed otherwise.
- `image`: `/blog/<filename>.png` in `public/blog/`.
- `seo`: title/description optimized for search; `keywords` 3–5 items.

## Content guidance
- Keep paragraphs short and direct; use subheadings to create a clear reading path.
- End with an action-oriented close or invitation to contact.
- If citing facts, include a brief "Sources" section with numbered entries.

## References
- Blog structure and style patterns: `skills/blog-writer/references/blog-patterns.md`
