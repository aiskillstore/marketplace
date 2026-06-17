# Security Policy

This skill performs network calls and writes files locally. We disclose the full data flow upfront so that auditors and users can make informed decisions.

## 1. Data flow at a glance

| Item | Direction | Destination | Sensitive? |
|---|---|---|---|
| User-supplied image | **outbound** | `https://scan-business.quark.cn` | depends on content |
| `SCAN_WEBSERVICE_KEY` | outbound (HTTP header) | same as above | yes — credential |
| Enhanced image | local write | system temp dir (`/tmp/imgs` or `%TEMP%`) | depends on content |
| Conversation context, other local files | not transmitted | — | n/a |

Full details: [references/privacy.md](references/privacy.md).

## 2. Known risks (already disclosed)

| Risk | Status | Mitigation |
|---|---|---|
| User images sent to third-party API | **disclosed**, required by skill purpose | User must opt in; data flow documented in SKILL.md & privacy.md |
| API key stored in plaintext at `~/.yescan_env` | **disclosed**, standard practice | Recommend `chmod 600`; documented rotation procedure |
| Output images written to `/tmp/imgs` and not auto-cleaned | **disclosed** | Cleanup commands provided in privacy.md |
| Network calls to `scan-business.quark.cn` | **disclosed** | Single, documented domain; no other external hosts |
| Package imports in `scripts/common/__init__.py` | **disclosed** | Standard Python package pattern; all imports are static and resolved at load time |
| Magic-byte detection in `scripts/common/file_saver.py` | **disclosed** | Used to validate decoded file format before save; not obfuscation |

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
- Modify files in place — output is always written to a fresh temp file
