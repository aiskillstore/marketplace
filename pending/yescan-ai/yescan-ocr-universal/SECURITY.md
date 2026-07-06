# Security Policy

This skill performs network calls to a third-party OCR service. We disclose the full data flow upfront so that auditors and users can make informed decisions.

## 1. Data flow at a glance

| Item | Direction | Destination | Sensitive? |
|---|---|---|---|
| User-supplied image | **outbound** | `https://scan-business.quark.cn` | depends on content |
| `SCAN_WEBSERVICE_KEY` | outbound (HTTP header) | same as above | yes — credential |
| OCR text result | **inbound** | returned as JSON to caller | depends on content |
| Translated image (`pic-translate` only) | **local write** | `/tmp/imgs/` | depends on content |
| Conversation context, other local files | not transmitted | — | n/a |

Full details: [references/privacy.md](references/privacy.md).

## 2. Known risks (already disclosed)

| Risk | Status | Mitigation |
|---|---|---|
| User images sent to third-party API | **disclosed**, required by skill purpose | User must opt in; data flow documented in SKILL.md & privacy.md |
| API key stored in plaintext at `~/.yescan_env` | **disclosed**, standard practice | Recommend `chmod 600`; documented rotation procedure |
| Network calls to `scan-business.quark.cn` | **disclosed** | Single, documented domain; no other external hosts |
| Package imports in `scripts/common/__init__.py` | **disclosed** | Standard Python package pattern; all imports are static and resolved at load time |

We have **not** introduced any dangerous built-in functions on user input, hidden network endpoints, credential exfiltration, prompt injection, or obfuscated code.

## 3. Reporting a vulnerability

If you find a security issue **in this skill's code** (not in the upstream Quark API):

1. Do **not** open a public GitHub issue
2. Email the maintainer at the address listed in `https://scan.quark.cn/business`
3. Provide a minimal reproduction and the affected version

We aim to acknowledge within 5 business days.

## 4. What this skill will never do

- Read files outside the user-specified path
- Access clipboard, browser cookies, or environment variables other than `SCAN_WEBSERVICE_KEY`
- Send data to any host other than `scan-business.quark.cn`
- Auto-retry failed requests (avoids quota leakage)
- Write output files to disk — except `pic-translate` scene, which saves the translated image to `/tmp/imgs/` (documented in privacy.md)
