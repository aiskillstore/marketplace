# Platform matrix and extraction policy

This matrix describes the preferred path, not a promise that every link will always be extractable.

| Platform / content | Preferred route | Fallback | Core status |
| --- | --- | --- | --- |
| DeepSeek share | first-party public JSON | generic public page | native |
| ChatGPT share / shared content | first-party React Router turbo-stream; legacy share JSON compatibility fallback | generic public page | native, undocumented |
| Bluesky post | documented public AT Protocol AppView + handle resolution | generic public page | native |
| Mastodon status | documented public instance REST API | generic public page | native |
| Gemini share | first-party anonymous public share RPC | generic public page | native, undocumented |
| Qwen share | first-party anonymous share JSON; final answer blocks only | generic public page | native, undocumented |
| Kimi share | first-party anonymous GetChatShare JSON | generic public page | native, undocumented |
| Claude share | first-party anonymous chat snapshot JSON | generic public page | native, undocumented |
| Grok share | standard public share-data JSON; anonymous X GrokShare browser transport when challenged | generic public page | native + optional browser |
| Doubao share | first-party Modern Router JSON embedded in public HTML | generic public page | native, undocumented |
| YouTube video | documented public oEmbed | yt-dlp / generic public page | native |
| Vimeo video | documented public oEmbed | yt-dlp / generic public page | native |
| X / Twitter post | documented public oEmbed | generic public page | native |
| Reddit post/thread | documented public oEmbed | standard Atom thread RSS enhancement; oEmbed survives RSS rate limits | native + built-in standard |
| Telegram public post | official anonymous Post Widget HTML | generic public page | native, documented |
| Pinterest public Pin | standard Open Graph on anonymous public Pin HTML | generic public page | native, standard metadata |
| Threads public post | standard Open Graph + Meta tokenless oEmbed enhancement | generic public page | native, documented + standard |
| Instagram public post/Reel | standard Open Graph + Meta tokenless oEmbed enhancement | generic public page | native, documented + standard |
| Facebook public post | standard Open Graph + Meta tokenless oEmbed enhancement | generic public page | native, documented + standard |
| LinkedIn public post | official anonymous public Embed page keyed by activity ID | generic public page | native, documented product surface |
| Bilibili video | first-party public view metadata JSON | yt-dlp / generic public page | native, undocumented |
| Xiaohongshu note | current official share token/short link → first-party SSR initial state | fresh official share link required when token expires | native, page-structure |
| Kuaishou video | current official share context → anonymous first-party PC Apollo SSR | fresh official share link when bare detail omits Apollo data | native metadata-only, page-structure |
| Kuaishou atlas/image post | current official public share page → isolated anonymous browser-rendered active-work DOM | generic public page when browser extra is unavailable | native route + optional browser, page-structure |
| TikTok video | documented public oEmbed | yt-dlp / generic public page | native |
| Douyin video | anonymous first-party Jingxuan SSR metadata; schema.org fallback | generic public page | native metadata-only, undocumented |
| Weibo status | anonymous first-party mobile PWA JSON; public extend for long text | generic public page | native, undocumented |
| Zhihu answer | anonymous first-party Tardis SSR reader | generic public page | native, undocumented |
| Zhihu Zhuanlan article | embedded first-party initial state | anonymous Tardis SSR / generic public page | native, undocumented |
| News/blog/article | oEmbed + JSON-LD + OG + article HTML | Trafilatura | generic |
| RSS / Atom feed | open-standard XML feed normalization | none | built-in standard |
| WebVTT / SRT / TTML | open timed-text document normalization | generic page metadata for track discovery | built-in standard |
| Arbitrary JSON endpoint | public JSON | none | generic |

## Stability labels

Use one of these concepts in adapter metadata/warnings:

- documented: provider documents the endpoint or protocol for this use.
- standard: open standard such as oEmbed, JSON-LD, OpenGraph, RSS/Atom.
- first_party_undocumented: provider-owned endpoint visible to a public page but not promised as a stable external API.
- page_structure: HTML/hydration parsing that may change with frontend deployments.
- third_party_adapter: extracted through another maintained open-source project.

Never describe an undocumented web endpoint as an “official public API”. “First-party public endpoint” is more precise.

## Decision rules

Prefer a direct public protocol when it returns the full shared object without executing JavaScript. Prefer oEmbed/JSON-LD over brittle CSS selectors. Use readable-content extraction for article-like pages. Use specialized media extractors only for metadata needed from public media URLs. Browser rendering is a last resort for genuinely public JavaScript-only pages.

If a route requires authentication, cookies, a CAPTCHA, bypassing a WAF, reverse-engineering a private signing mechanism, or impersonating a logged-in user, stop and report that the public-only policy cannot extract it.

## Health contract

The machine-readable registry, packaged route-contract fixture corpus, offline CI validation, and optional live verification are documented in [adapter-health.md](adapter-health.md). Platform rows in this matrix are descriptive; the registry is the executable source of truth for adapter health metadata.
