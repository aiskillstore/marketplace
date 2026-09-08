# Contributing to ShareXtract

Thanks for helping make public shared content easier for agents and tools to consume.

## What we want

The highest-value contributions are new public platform adapters, fixes for platform changes, sanitized regression fixtures, better generic oEmbed/JSON-LD/readability handling, normalized metadata improvements, security hardening, and documentation about endpoint stability and limitations.

## Adapter requirements

A platform adapter must:

1. target public content;
2. avoid credentials, copied browser sessions and private cookies in tests or fixtures;
3. not bypass authentication, CAPTCHAs, paywalls, WAF challenges, signing/access controls, or platform privacy settings;
4. narrowly match supported URL patterns;
5. identify the extraction method and its stability honestly;
6. fail closed rather than fabricate missing content;
7. include tests using static/fake responses.

Undocumented provider-owned endpoints are allowed only when they are publicly reachable without authentication and the adapter clearly labels them unstable/undocumented and retains a public-page fallback.

## Development

    python -m unittest discover -s tests -v
    python -m compileall -q sharextract
    python -m sharextract --help

Optional dependencies:

    python -m pip install -e ".[all]"

## Pull requests

Keep each PR focused. For a new platform, include the adapter, tests, and a platform-matrix update in the same PR.

Explain which public URL patterns are covered, which protocol/source is used, whether that source is documented or undocumented, what fallback exists, and what was tested.

Do not include real private conversations or personal data in fixtures. Use synthetic payloads.

By contributing, you agree that your contribution is licensed under the repository's Apache-2.0 license.
