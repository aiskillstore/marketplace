#!/usr/bin/env python3
"""
Deployment settings for the yescan-transoffice-universal skill.

Security audit notes
--------------------
- ``API_URL`` is the ONLY outbound network destination this skill ever
  contacts. It is hard-coded (no env-var override, no redirect chain into
  user-controlled hosts) and points to the Quark Scan King public service.
- The full data-flow disclosure (which fields are sent to this endpoint,
  retention policy, etc.) lives in ``../../SECURITY.md`` and
  ``../../references/privacy.md``.
- ``PLATFORM`` / ``VERSION`` / ``SKILL_NAME`` are non-sensitive client
  identifiers attached as request headers for telemetry only.
"""

# Single, hard-coded outbound endpoint. See SECURITY.md for the full data flow.
API_URL = "https://scan-business.quark.cn/vision"
PLATFORM = "community"
VERSION = "1.1.4"
SKILL_NAME = "yescan-transoffice-universal"
