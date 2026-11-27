# Dependencies

Reuse a shipped dependency or runtime primitive if it covers the behavior and supports the declared runtime floor. For new dependencies, check the actual package version, security and maintenance history, license, platform support, and lockfile impact. Separate development and runtime dependencies. Inspect transitive changes before upgrading.

Add a mature library when the alternative is duplicating a security-sensitive protocol or maintaining substantial edge cases. Prefer a local implementation for small well-understood logic with a straightforward test. Give new external infrastructure a measurable reason.

Keep manifest, lockfile, package contents, runtime engines, and CI aligned. Verify a clean installation and normal feature entry point. Use a fake connection at test boundaries when the feature relies on an external service.
