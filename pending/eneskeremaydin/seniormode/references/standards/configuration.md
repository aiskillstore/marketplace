# Configuration

Separate deploy-time parameters such as addresses, timeouts, and credentials from business invariants and feature policy. Validate configuration once at startup with useful, redacted errors. Give explicit units and stable names to values copied into docs or deployment files.

Provide safe defaults for optional settings. Require the operator to supply environment-specific credentials and identities. Keep examples synthetic. Centralize the source of configuration when multiple entry points must agree and avoid reading process state from pure policy functions.

Test missing required settings, invalid units and types, and configuration overrides that are part of the public contract.
