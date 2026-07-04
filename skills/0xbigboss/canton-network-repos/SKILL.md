---
name: canton-network-repos
description: Use when working with Canton Network participants, DAML smart contracts, Splice applications, or debugging LF version and package ID issues.
---

# Canton Network Repositories

## Repository Hierarchy

```
Splice (e.g., 0.5.4)     github.com/digital-asset/decentralized-canton-sync
  └─ depends on
Canton (e.g., 3.4.9)     github.com/digital-asset/canton
  └─ depends on
DAML SDK (e.g., 3.4.9)   github.com/digital-asset/daml
```

## Version Mapping

| Splice | Canton | DAML SDK | Protocol | LF Default | LF Available |
|--------|--------|----------|----------|------------|--------------|
| 0.5.4  | 3.4.9  | 3.4.9    | PV34     | 2.1*       | 2.2 (verified) |
| 0.5.3  | 3.4.8  | 3.4.8    | PV34     | 2.1*       | 2.2 |
| 0.4.x  | 3.3.x  | 3.3.x    | PV33     | 2.1        | 2.1 |

*Open-source Splice 0.5.4 ships with SDK snapshot `3.3.0-snapshot.20250502` (pre-dates LF 2.2). LF 2.2 was added to the SDK on 2025-10-03. Updating to SDK 3.4.9 enables LF 2.2 builds.

## Key Configuration Files

| Purpose | Repo | File |
|---------|------|------|
| LF version definitions | daml | `sdk/daml-lf/language/.../LanguageVersion.scala` |
| damlc target validation | daml | `sdk/compiler/damlc/lib/DA/Cli/Options.hs` |
| Canton version | canton | `VERSION` |
| Built-in DARs | canton | `community/common/src/main/daml/` |
| Splice LF config | splice | `project/CantonDependencies.scala` |
| Package targets | splice | `daml/*/daml.yaml` |
| Docker builds | splice | `cluster/images/*/Dockerfile` |

**Splice LF config** (`project/CantonDependencies.scala`):
```scala
val daml_language_versions = Seq("2.1")  // ← LF target; change to "2.2" for upgrade
val daml_compiler_version = sys.env("DAML_COMPILER_VERSION")
```

## Package ID Derivation

Package IDs are cryptographic hashes of: source content + LF version (`--target`) + SDK/stdlib version + dependency package IDs.

**Changing LF version = different package IDs = incompatible packages.** Canton validates that upgraded packages use equal or newer LF version; mixing LF versions on the same ledger causes validation failures.

## Enterprise vs Community Canton

| Feature | Enterprise | Community |
|---------|------------|-----------|
| Transaction processing | Parallel | Sequential |
| Database | PostgreSQL, Oracle | PostgreSQL only |
| HA Domain | Supported | Embedded only |
| Pruning | Full | Limited |

## Build Commands

```bash
# Community Canton participant
cd canton && sbt "community/app/assembly"
# Output: community/app/target/scala-2.13/canton-community.jar

# Splice applications (requires DAML_COMPILER_VERSION env var)
cd decentralized-canton-sync && sbt compile
```

## Upgrading to LF 2.2 (Verified with SDK 3.4.9)

1. `project/CantonDependencies.scala`: `val daml_language_versions = Seq("2.2")`
2. `nix/daml-compiler-sources.json`: `{ "version": "3.4.9" }`
3. All `daml/*/daml.yaml`: set `sdk-version: 3.4.9` and `--target=2.2`
4. Remove `-Wno-ledger-time-is-alpha` from all `daml.yaml` files (not in SDK 3.4.9)
5. Build: `daml build -p daml/splice-util && daml build -p daml/splice-amulet`

Community-built DARs have identical package IDs to enterprise at the same LF version (verified 2025-12-24).

## Troubleshooting

**"Unknown Daml-LF version: 2.2"**: damlc binary doesn't support 2.2. Check `daml damlc --help` for supported targets; upgrade to SDK 3.4.9.

**Package ID mismatch**: different `--target` values between builds. Check: `unzip -p package.dar META-INF/MANIFEST.MF | grep Sdk-Version`

**Upgrade validation failed**: swapping enterprise (LF 2.2) with community (LF 2.1) packages. Use DAR injection to maintain LF 2.2 compatibility.

## References

- [DAML SDK Releases](https://github.com/digital-asset/daml/releases)
- [Canton Releases](https://github.com/digital-asset/canton/releases)
- [Splice Docs](https://docs.dev.sync.global/)
- [DAML-LF Governance](https://github.com/digital-asset/daml/blob/main/daml-lf/governance.rst)
