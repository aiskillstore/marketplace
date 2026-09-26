---
name: camel-matrix
description: Generates a Markdown compatibility matrix for Apache Camel Spring Boot, Spring Boot, and Apache CXF versions by running the camel-springboot-matrix.sh script. Use when the user asks to generate or update the Camel compatibility matrix, check Camel Spring Boot version compatibility, or run the camel-springboot-matrix script. Supports optional version range arguments (min max).
---

# Camel Spring Boot Compatibility Matrix

Run `scripts/camel-springboot-matrix.sh` (bundled in this skill) to generate `target/camel-springboot-matrix.md` relative to the current project directory. The `target/` directory is created automatically if it does not exist.

## Arguments

The user may provide an optional version range: `$ARGUMENTS`

- No arguments: use the default range `4.14.0` to latest (see below)
- Two arguments (e.g. `4.0.0 4.15.0`): only versions in that range are processed

## Steps

1. Run the script. If no version range is given by the user, default to `4.14.0` as minimum and omit the max argument (so the script fetches up to the latest available version):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/camel-springboot-matrix.sh" ${ARGUMENTS:-4.14.0}
```

2. After completion, report:
   - How many Camel versions were processed
   - That `target/camel-springboot-matrix.md` was created/updated in the current project directory
   - The last 5 rows of the generated table so the user can verify the output
