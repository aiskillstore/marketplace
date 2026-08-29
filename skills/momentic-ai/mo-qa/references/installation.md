# Install or update Mo

Read this when `mo --version` fails or Mo must be updated.

## Install or update

```bash
curl -fsSL https://cli.momentic.ai/mo | sh
```

The installer writes `mo` to `$HOME/.local/bin`. Add that directory to `PATH`
if needed, then verify the installation:

```bash
mo --version
```

Rerun the same installer to update Mo.

## Authenticate after installation

After a fresh installation, read [Authentication](authentication.md) and sign
in before running an operational command.
