# Ecosystem map

ShareXtract is an orchestration and normalization layer. It should reuse strong upstream projects instead of cloning their internals.

## AI conversation exporters

### Timed text standards

WebVTT, SubRip/SRT, and TTML are handled as public timed-text documents before generic HTML extraction. The core path uses only Python standard-library parsing. HTML track elements are discovered as metadata rather than eagerly fetched, preserving ShareXtract's bounded/network-explicit behavior.

### RSS / Atom standards

RSS 2.0, RSS 1.0/RDF, and Atom are normalized directly with Python standard-library XML parsing after the existing SafeHttpClient fetch. ShareXtract does not guess feed URLs by suffix and does not require a third-party parser for the core path. Standard enclosure/media references and webpage feed-discovery links are preserved. DTD/entity declarations are rejected before parsing.

### ChatGPT React Router turbo-stream

Current public ChatGPT `/share/` and `/s/` pages serialize structured shared content into first-party React Router turbo-stream script chunks. ShareXtract hydrates the public serialization directly over ordinary HTTP and keeps the older backend share JSON only as a compatibility fallback.

### X / YouTube / Vimeo oEmbed

X, YouTube, and Vimeo expose public oEmbed routes suitable for metadata and embed extraction without account tokens. These adapters sit ahead of yt-dlp so open/documented provider interfaces win over heavier media tooling.

### Bilibili public view metadata

Bilibili's public `/x/web-interface/view` JSON route exposes video metadata including title, owner, description, timestamps, duration, pages, public statistics, and thumbnails. ShareXtract treats it as first-party but undocumented rather than as a promised external API contract.

### chat2md

hao0xffff/chat2md focuses on exporting AI sharing links to Markdown. Its README describes ChatGPT and Gemini as enabled and Doubao as a registered but disabled skeleton, plus API/MCP/UI surfaces.

It is a useful architectural reference for the AI-share niche. At the time ShareXtract was created, the GitHub repository metadata did not declare a license, so ShareXtract does not copy its code.

Repository: https://github.com/hao0xffff/chat2md

### Doubao embedded router JSON

Doubao public thread/share pages currently embed first-party Modern Router loader data in HTML attributes. The decoded payload contains share_info and message_snapshot.message_list. ShareXtract reads that public embedded JSON directly, avoiding browser rendering and authenticated chat APIs. Normal media variants are retained; raw/no-watermark-specific image fields are intentionally not selected.

### Qwen public share JSON

Qwen public chat shares expose an anonymous first-party GET /api/v2/chats/share/{id} JSON route. The payload can include final answers, model/file metadata, message-tree relationships, and internal reasoning-related fields. ShareXtract exports only public final answer content and intentionally omits internal reasoning/thinking fields.

### Kimi public GetChatShare

Kimi formerly exposed share content through server-rendered hydration state. The current public frontend loads the snapshot through an anonymous first-party POST /apiv2/kimi.gateway.chat.v1.ChatService/GetChatShare request whose body contains only the public share_id. ShareXtract follows the current structured route rather than relying on stale SSR markers.

### Grok public share transport

Grok exposes a first-party share-data route under grok.com/rest/app-chat, but Cloudflare may challenge standard HTTP clients. ShareXtract does not bypass that challenge. Its optional fallback opens the public x.com/i/grok/share page with a fresh anonymous browser context and extracts the structured GrokShare GraphQL response already requested by that public page.

### Claude public chat snapshots

Claude public share pages can be protected by Cloudflare and may fail under ordinary automated page fetches, but the public frontend currently exposes an anonymous first-party GET /api/chat_snapshots/{uuid} JSON route for public snapshots. ShareXtract targets that structured route directly and does not require a logged-in Claude browser session.

### Gemini public share RPC

Gemini public share pages are snapshots readable by anyone with the link. The current public frontend retrieves the snapshot through an unauthenticated first-party BardChatUi batchexecute RPC. ShareXtract calls that RPC directly after resolving supported short links, avoiding browser automation while clearly labeling the route undocumented and unstable.

Official sharing behavior: https://support.google.com/gemini/answer/13743730

## Media

### yt-dlp

A mature extractor/downloader with a very large platform adapter set plus generic/embed extraction. ShareXtract uses it only as an optional metadata extractor by default.

Repository: https://github.com/yt-dlp/yt-dlp

### cobalt

A multi-platform media retrieval service/API. It is useful when a deployment wants a separate media service boundary rather than embedding platform logic.

Repository: https://github.com/imputnet/cobalt

## Readable web content

### Trafilatura

Focused on main-text and metadata extraction, with plain text, JSON, Markdown, HTML/XML-family outputs and configurable precision/recall tradeoffs. It is the preferred optional article-quality dependency in ShareXtract.

Project: https://trafilatura.readthedocs.io/

### Crawl4AI

An open-source crawler designed to produce LLM-friendly Markdown and structured extraction. It is a candidate optional service/browser integration for larger crawling deployments.

Repository: https://github.com/unclecode/crawl4ai

### Microlink

A hosted API/tooling ecosystem for extracting URL metadata/content and media-related information. It can be a deployment adapter when users prefer a managed external service instead of local extraction.

Project: https://microlink.io/

## Open social protocols

### Bluesky / AT Protocol

AT Protocol exposes documented Lexicon/XRPC endpoints and a public Bluesky AppView for unauthenticated public reads. ShareXtract should prefer these documented protocol APIs over parsing the JavaScript application shell.

Docs: https://docs.bsky.app/ and https://atproto.com/

### Mastodon / ActivityPub-compatible servers

Mastodon exposes documented anonymous REST reads for public statuses. ShareXtract probes the status API on the source instance and falls back to generic web extraction if the host is not Mastodon-compatible or the public API is unavailable.

Docs: https://docs.joinmastodon.org/

## Chinese social platforms

### MediaCrawler

A broad social crawler with implementations for Xiaohongshu, Douyin, Kuaishou, Bilibili, Weibo, Baidu Tieba and Zhihu. Some modes involve logged-in browser state and anti-crawler techniques; those are outside ShareXtract core policy. Only public, permitted integration modes should be considered.

Repository: https://github.com/NanmiCoder/MediaCrawler

### F2

A Python multi-platform downloader/API-processing project covering Douyin, TikTok, Twitter and Weibo among others. It can inform or power optional public-content adapters where its operation and license are compatible.

Repository: https://github.com/Johnserf-Seed/f2

## Principle

Upstream tools solve different layers. ShareXtract's value is to choose among them and return one stable output contract with provenance, not to pretend every site exposes the same kind of API.

### Zhihu public SSR and hydration

Zhihu answers and Zhuanlan articles expose different anonymous public structures. Answer extraction uses the first-party Tardis zm/ans/{id} SSR reader rather than the anonymous-403 API/signing path. Zhuanlan extraction prefers the public page's embedded initial-state article entity, with the Tardis zm/art/{id} reader as fallback. ShareXtract deliberately does not implement private x-zse signing, d_c0 cookie acquisition, or logged-in session reuse.

### Weibo mobile public PWA JSON

Public Weibo status URLs are normalized through the anonymous m.weibo.cn mobile PWA JSON surface. The core status route is statuses/show?id={bid}; statuses marked isLongText may additionally use the public statuses/extend?id={bid} response. The adapter sends only anonymous PWA request headers and does not use account cookies, OAuth tokens, browser session state, or authenticated APIs.

### TikTok documented oEmbed

Direct public TikTok video URLs are normalized through TikTok's documented /oembed endpoint. This route is separate from TikTok Display API authorization and needs no user login or access token for public embed metadata. ShareXtract preserves the returned standard oEmbed metadata and does not use authenticated account data.

### Douyin Jingxuan public metadata reader

Douyin's ordinary web-detail JSON surface currently may return an empty body even for public videos. ShareXtract instead uses the anonymous first-party Jingxuan mobile video reader, which embeds SSR state and schema.org VideoObject metadata for public IDs. The adapter consumes only metadata fields and deliberately excludes temporary playback/download URLs contained in nested video_model data. A standard anonymous mobile-browser User-Agent is used for content negotiation; no cookies, private signatures or account state are imported.

### Xiaohongshu tokenized public SSR

Xiaohongshu's note-detail APIs require signed X-s/X-t style headers and are intentionally outside ShareXtract's core boundary. Public official share links already carry a transient xsec_token; when present, the anonymous note page exposes Vue SSR window.__INITIAL_STATE__ with the public note payload. ShareXtract consumes that existing share token only, strips unrelated tracking parameters, and never creates or refreshes tokens. Because share tokens expire, no fixed live-health sample is stored. Video/subtitle stream URLs present inside SSR state are deliberately excluded from normalized output.

### Kuaishou public Apollo SSR

Kuaishou PC public video pages can embed window.__APOLLO_STATE__ with a normalized visionVideoDetail relation linking the exact photo, author and tags. Bare direct pages may omit detail, while current official share links can carry the public context needed by the same anonymous page response. ShareXtract consumes that context only in the original public request, never exports it, and does not use did device cookies or private GraphQL detail calls. Playback URLs/manifests present in Apollo state are intentionally excluded.


### Kuaishou atlas/image shares

Current Kuaishou image-share HTML exposes an empty static INIT_STATE and renders the actual work client-side. ShareXtract uses its existing isolated public-browser boundary for this case: a fresh context with no imported account state, scoped to the active work DOM. The page may naturally create ephemeral visitor state while running, but ShareXtract does not export or persist it and does not replay protected internal requests. Public /ufile/atlas/ images may be normalized; audio/video streams and protected request URLs are excluded.


### Reddit oEmbed + Atom threads

Reddit's anonymous .json post surface can now return 403 for public threads. ShareXtract does not bypass that policy. The documented www.reddit.com/oembed endpoint is used as the primary public contract, while the thread's standard .rss Atom feed is used only as a best-effort content enhancement. Atom entry zero supplies the post body and later entries normalize to comment messages. If RSS is rate-limited, the oEmbed result remains valid. No OAuth, copied account cookie, blocked JSON endpoint, or browser session is required.


### Telegram Post Widget

Telegram officially supports embedding messages from public channels and groups through its Post Widget. ShareXtract fetches the anonymous t.me embed representation and parses only the already-public widget HTML. This exposes message text, author/channel, timestamp, views, reactions, link-preview metadata and public photos without Bot Tokens, login cookies, OAuth, or browser automation. Widget auth/upload configuration and temporary audio/video stream details are intentionally excluded.


### Pinterest Open Graph Pin surface

Pinterest public Pin pages expose standard Open Graph title, description, image, dimensions, updated time, source link and Pin type in anonymous static HTML. ShareXtract intentionally ignores internal PWS bootstrap state and undocumented pidgets APIs. Pinterest may declare a canonical/og:url Pin ID that differs from the requested Pin and can resolve to different content; therefore the requested Pin ID remains ShareXtract's stable identity while declared canonical metadata is recorded separately with a mismatch flag.


### Meta tokenless embeds

Meta's official Meta Embeds for WordPress project documents tokenless oEmbed providers for Threads, Instagram and Facebook. ShareXtract combines those official embed surfaces with standard Open Graph from the anonymous public post page. Open Graph remains the content layer; tokenless oEmbed is an enhancement and may fail without invalidating already-public OG content. No access token, developer app, login cookie or browser is required. Threads profile-image OG data is not exported as post media; Instagram video streams are not exported; Facebook canonical identifier changes are recorded separately from requested identity.


### LinkedIn public Embed

LinkedIn documents off-LinkedIn embedding for eligible Public/Anyone posts. ShareXtract derives the activity ID from normal LinkedIn post/feed URLs and consumes the anonymous public Embed page. The Embed DOM provides actor, commentary, relative publication display, reaction/comment counts, explicit feed images and article/link attachments. No OAuth, access token, li_at cookie or browser is required. Non-embeddable posts are treated as unavailable rather than authenticated or bypassed.
