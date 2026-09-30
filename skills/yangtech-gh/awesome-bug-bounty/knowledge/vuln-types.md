# Vulnerability Types — Hunt Focus & Patterns

Distilled from Awesome-Bugbounty-Writeups, bug-bounty-reference, hackerone-reports tops, and PayloadsAllTheThings.

## XSS (reflected / stored / DOM / blind / XSSI)

- Hunt: user input reflected in HTML/JS/attributes/URLs; JSONP callbacks; postMessage; SVG/file uploads; markdown renderers; admin panels (blind XSS); cookie/localStorage sinks.
- Escalation paths: self-XSS → CSRF → stored; XSS → session/token theft → ATO; XSS → RCE (Electron/SVG/PhantomJS renderers).
- Bypasses: CSP bypass via script gadgets/JSONP/trusted CDNs; WAF vendor-specific filters (Cloudflare/Akamai/Incapsula); encoding chains; mutation XSS.
- Fallback: Awesome-Bugbounty-Writeups#xss, PayloadsAllTheThings/XSS Injection.

## SQL injection

- Hunt: order-by/limit/WHERE params; search, sort, filter, pagination; headers (User-Agent, Referer, X-Forwarded-For); second-order injection via stored data.
- Techniques: union, boolean/time blind, error-based, out-of-band, stacked; DBMS-specific (MySQL, MSSQL, PostgreSQL, Oracle, SQLite, MongoDB→NoSQL).
- Fallback: PayloadsAllTheThings/SQL Injection; hackerone-reports TOPSQLI.

## SSRF

- Hunt: URL/webhook/fetch/avatar/image-proxy params; PDF generators; headless browsers; OpenGraph fetchers.
- Impact: cloud metadata (169.254.169.254 AWS/GCP/Azure/Alibaba/DigitalOcean/Oracle), internal admin panels, port scan, Redis/Gopher RCE chains, DNS rebinding.
- Fallback: PayloadsAllTheThings/Server Side Request Forgery; hackerone-reports TOPSSRF.

## IDOR / BOLA

- Hunt: sequential/GUID object IDs in path/query/body; UUID v1 (timestamp leaks); change owner/tenant param; horizontal (same role, other object) vs vertical (elevated role).
- Testing: capture low-priv and high-priv sessions; replay with swapped IDs (AutorizePro/BurpAPISecuritySuite Auth Replay); check GraphQL node IDs, mass assignment of user_id/role.
- ORM leaks: Django filter chains, Prisma include abuse, Ransack — see hack-skills idor-broken-object-authorization.
- Fallback: bug-bounty-reference#IDOR, hackerone-reports TOPIDOR.

## Authentication bypass / ATO / 2FA

- Password reset: token predictability, host-header poisoning, token reuse, no rate limit.
- 2FA: response manipulation (status=valid), backup codes, SIM swap/session fixation, OTP brute force, "remember device" abuse.
- OAuth: redirect_uri manipulation (path traversal / subdomain), code injection, token leakage via referer, state bypass.
- JWT: alg=none, RS256→HS256 key confusion, claim tampering (role/admin), JWKS kid injection, weak secrets.
- SAML: signature wrapping, comment injection in NameID, XXE in assertion parsing.
- Fallback: bug-bounty-reference#Authentication-Bypass, hack-skills auth-sec.

## Race condition

- Hunt: single-use coupons/tickets, balance transfers, voting/likes, stock limits, "first N users", file generation.
- Method: HTTP/1.1 last-byte sync (Turbo Intruder), HTTP/2 single-packet attack; bypass with connection: keep-alive + interleaved requests.
- Fallback: hackerone-reports TOPRACECONDITION, knowledge/business-logic.md.

## Business logic

See `knowledge/business-logic.md`. Quick hits: negative quantities/price, step skipping in wizards, coupon stacking, limit bypass via parallel requests, client-side-only validation.

## CSRF

- Hunt: state-changing requests without anti-CSRF token (logout, email change, password change, JSON endpoints with content-type trust); SameSite cookie gaps.
- Escalation: CSRF → stored XSS; CSRF → 2FA disable → ATO; JSON CSRF via text/plain.
- Fallback: Awesome-Bugbounty-Writeups#CSRF, hackerone-reports TOPCSRF.

## CORS misconfiguration

- Danger: `Access-Control-Allow-Origin` reflecting arbitrary origin + `Access-Control-Allow-Credentials: true`; null origin; wildcard with sensitive data; subdomain trust abuse.
- Impact: cross-origin read of authenticated responses → data theft/ATO.
- Fallback: PayloadsAllTheThings/CORS Misconfiguration.

## RCE / deserialization / SSTI / CMDi

- Deserialization: Java (ysoserial), PHP (phar/unserialize gadget chains), Python (pickle/yaml), Ruby Marshal, .NET BinaryFormatter/ViewState, Node node-serialize.
- SSTI engines: Jinja2/Twig/Pug/Handlebars/EJS/Razor — detect via `{{7*7}}` vs `${7*7}` vs `<%= %>`.
- CMDi: spaceless payloads (`$IFS`), wildcards, base64/echo pipes, ImageMagick/FFmpeg component bugs, PHP disable_functions bypasses.
- Fallback: PayloadsAllTheThings/{Insecure Deserialization, Server Side Template Injection, Command Injection}.

## File upload / LFI / path traversal

- Upload: double extensions, content-type/MIME tricks, polyglot images+PHP, null byte (legacy), SVG/HTML upload → XSS, phar → deserialization.
- LFI: wrappers (`php://filter`, `phar://`, `zip://`, `data://`), log poisoning, session files, pearcmd, `/proc/self/environ`.
- Fallback: PayloadsAllTheThings/{Upload Insecure Files, File Inclusion, Directory Traversal}.

## Open redirect / clickjacking / subdomain takeover

- Open redirect: parameter abuse (`url=`, `next=`, `redirect=`), `//evil`, `@` userinfo tricks, backslash, `..%2f`; chain to OAuth token theft.
- Clickjacking: missing X-Frame-Options / weak CSP frame-ancestors; combine with CSRF.
- Subdomain takeover: dangling CNAME to GitHub Pages/S3/Heroku/Unbounce/Vercel/Shopify/Azure; NS delegation.
- Fallback: PayloadsAllTheThings/{Open Redirect, Clickjacking}, bug-bounty-reference#Subdomain-Takeover.

## Request smuggling / cache / host header

- Smuggling: CL.TE, TE.CL, TE.TE; HTTP/2 downgrade (H2.CL); poison caches → XSS/session hijack.
- Cache: web cache deception (path confusion), cache poisoning via unkeyed headers (X-Forwarded-Host, X-Original-URL).
- Host header: password reset poisoning, routing SSRF, absolute-URL override.
- Fallback: PayloadsAllTheThings/{Request Smuggling, Web Cache Deception}; hack-skills http-host-header-attacks.

## GraphQL

- Introspection leakage, batching attacks (auth bypass rate limits), field suggestion info leak, nested query DoS, IDOR via global IDs.
- Fallback: PayloadsAllTheThings/GraphQL Injection; BurpAPISecuritySuite GraphQL tab.

## API security (OWASP API Top 10 highlights)

- BOLA/BFLA (API1/API4), mass assignment (API3), excessive data exposure (API6), lack of resources/rate limiting (API9), SSRF (API10).
- Fallback: BurpAPISecuritySuite, hack-skills api-sec, knowledge/methodology.md.

## Top disclosed reports (patterns worth studying)

Index at hackerone-reports `docs/tops_by_bug_type/`: TOPXSS, TOPSQLI, TOPSSRF, TOPIDOR, TOPRACECONDITION, TOPBUSINESSLOGIC, TOPAUTH, TOPOAUTH, TOPACCOUNTTAKEOVER, TOPGRAPHQL, TOPAPI, TOPREQUESTSMUGGLING, TOPWEBCACHE, TOPMFA, TOPAUTHORIZATION, TOPSUBDOMAINTAKEOVER, and more. Program-specific tops under `docs/tops_by_program/` (Shopify, GitLab, Uber, Twitter/X, HackerOne, DoD…).
