# Security policy

## Public-content boundary

ShareXtract is designed for public HTTP(S) resources. The core client blocks localhost and non-public IP ranges and revalidates redirects.

The project does not accept features whose primary purpose is to bypass authentication, CAPTCHAs, paywalls, WAF challenges, private sharing controls, or other access controls.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting if it is available for this repository. Otherwise, open an issue only when the report contains no exploit secrets or sensitive user data and ask a maintainer for a private contact channel.

Useful reports include SSRF bypasses, unsafe redirects, command injection, credential leakage, unbounded resource consumption, or a platform adapter exposing data not intended to be public.

## Supported versions

Until the project reaches 1.0, security fixes are applied to the latest main branch and newest release.
