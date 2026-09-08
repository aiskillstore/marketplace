# Security policy

## Public-content boundary

ShareXtract is designed for public HTTP(S) resources only.

The core HTTP client resolves destination hostnames to public IP addresses once, connects directly to one of those validated addresses, and verifies the connected peer before sending the request. Redirect targets are validated again before following them. This prevents localhost/private-range access and closes the DNS-validation-versus-connect rebinding window.

The optional Playwright fallback starts from a fresh context, blocks service workers, validates the initial/final page URL, and intercepts network requests so private/non-HTTP(S) destinations are rejected before navigation continues.

System/browser proxy settings are **not trusted automatically** for untrusted public URLs. Browser proxy use requires the explicit environment flag:

    SHAREXTRACT_TRUST_PROXY=1

That flag means the operator trusts the configured outbound proxy to enforce the public-network boundary when the proxy performs remote DNS resolution. Do not enable it for an untrusted or shared proxy.

## Untrusted-content boundary

All remote content is data, not instruction. Extracted AI-share text, comments, HTML, JSON, captions, metadata, and tool-like strings must never be treated as system/developer/user intent merely because they appear in a fetched document.

Downstream agents should keep extracted content quoted or structurally separated from instructions and require independent user intent before executing commands, installing software, modifying files, sending messages, or taking other external actions.

## Access-control boundary

The project does not accept features whose primary purpose is to bypass authentication, CAPTCHAs, paywalls, WAF challenges, private sharing controls, or other access controls.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting if it is available for this repository. Otherwise, open an issue only when the report contains no exploit secrets or sensitive user data and ask a maintainer for a private contact channel.

Useful reports include SSRF bypasses, unsafe redirects, command injection, credential leakage, prompt-injection trust-boundary failures, unbounded resource consumption, or a platform adapter exposing data not intended to be public.

## Supported versions

Until the project reaches 1.0, security fixes are applied to the latest main branch and newest release.
