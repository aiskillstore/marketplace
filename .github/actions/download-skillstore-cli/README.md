# Skillstore CLI Download Action

Downloads and caches the skillstore-cli binary for GitHub Actions workflows.

## Quick Start

### For Docker-based Self-Hosted Runners (⚠️ READ THIS FIRST)

**IMPORTANT:** If your self-hosted runner runs in Docker, you **MUST** mount a persistent volume or the cache won't persist between runs!

```yaml
# In your workflow:
- name: Download skillstore CLI
  uses: ./.github/actions/download-skillstore-cli
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    cache-dir: /var/lib/github-runner-cache/skillstore-cli
```

**See [DOCKER-SETUP.md](./DOCKER-SETUP.md) for complete Docker volume configuration!**

### For GitHub-Hosted Runners

```yaml
- name: Download skillstore CLI
  uses: ./.github/actions/download-skillstore-cli
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    # No cache-dir = uses GitHub's cache automatically
```

## Features

- ✅ **Automatic version resolution**: Defaults to latest release
- ✅ **Smart caching**: GitHub-hosted (cloud) vs self-hosted (local)
- ✅ **Zero manual setup**: Auto-creates cache directories
- ✅ **Version tracking**: Auto-downloads new versions when available
- ✅ **Cross-platform**: Linux, macOS, Windows

## Inputs

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `version` | No | `latest` | CLI version (e.g., "1.20.4" or "latest") |
| `token` | Yes | - | GitHub token with repo access |
| `cache-dir` | No | `''` | Local cache path for self-hosted runners |

## Outputs

| Name | Description |
|------|-------------|
| `cli-path` | Absolute path to the CLI binary |

## How Caching Works

### GitHub-Hosted Runners (Default)

```yaml
# Automatically uses actions/cache@v4
cache-dir: ""  # or omit this parameter
```

- Cache stored in GitHub's cloud (~37 MB)
- Download speed: ~20-30 seconds per run
- Works everywhere, no setup required

### Self-Hosted Runners (Persistent Filesystem)

```yaml
# Uses local filesystem for instant cache
cache-dir: /var/lib/github-runner-cache/skillstore-cli
```

- **First run**: Download + save to cache (~30s)
- **Subsequent runs**: Instant copy from local disk (<1s!)
- **Requires**: Persistent directory (see below)

#### ⚠️ CRITICAL for Docker Runners

Docker containers are **ephemeral by default**. Without a mounted volume, the cache directory is recreated on every run and **you get NO performance benefit**.

**Required:** Mount `/var/lib/github-runner-cache` as a Docker volume.

**See [DOCKER-SETUP.md](./DOCKER-SETUP.md) for step-by-step instructions.**

## Usage Examples

### Example 1: Docker Self-Hosted with Persistent Cache

```yaml
jobs:
  validate:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4

      - name: Download skillstore CLI
        uses: ./.github/actions/download-skillstore-cli
        with:
          version: latest
          token: ${{ secrets.GITHUB_TOKEN }}
          cache-dir: /var/lib/github-runner-cache/skillstore-cli

      - name: Run validation
        run: |
          ./skillstore-cli skill validate ./skills
```

### Example 2: GitHub-Hosted Runners

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download skillstore CLI
        uses: ./.github/actions/download-skillstore-cli
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          # No cache-dir needed

      - name: Run tests
        run: |
          ./skillstore-cli skill test
```

### Example 3: Specific Version

```yaml
- name: Download skillstore CLI v1.20.4
  uses: ./.github/actions/download-skillstore-cli
  with:
    version: "1.20.4"
    token: ${{ secrets.GITHUB_TOKEN }}
```

## Troubleshooting

### "No cached versions found" on every run (Docker)

**Problem:** Cache isn't persisting between workflow runs.

**Cause:** Your Docker container is ephemeral and doesn't have a persistent volume mounted.

**Solution:** See [DOCKER-SETUP.md](./DOCKER-SETUP.md) to mount `/var/lib/github-runner-cache` as a volume.

### Permission denied creating cache directory

**Problem:** `mkdir: cannot create directory: Permission denied`

**Solution 1 (Recommended):** Use a user-writable path in your Docker setup:
```yaml
cache-dir: /home/runner/cache/skillstore-cli
```

**Solution 2:** Pre-create the directory with correct permissions on the Docker host:
```bash
sudo mkdir -p /var/lib/github-runner-cache
sudo chown -R 1001:1001 /var/lib/github-runner-cache
```

### Cache still slow on self-hosted runners

**Problem:** Still taking 20-30 seconds even with `cache-dir` set.

**Diagnosis:** Check if the "Save to local cache" step runs:
- ✅ **Should see**: "✅ Saved to local cache: /var/lib/..."
- ❌ **If missing**: Volume not mounted or directory not writable

**Solution:** Verify Docker volume mount (see [DOCKER-SETUP.md](./DOCKER-SETUP.md))

## Cache Behavior Logs

### First Run (Cache Miss)
```
📁 Cache directory doesn't exist, creating: /var/lib/github-runner-cache/skillstore-cli
✅ Cache directory created successfully
❌ No cached version found for cli-v1.20.4
📂 Cache directory: /var/lib/github-runner-cache/skillstore-cli
📦 No cached versions found (first run)
Downloading skillstore-cli (cli-v1.20.4)...
✅ Saved to local cache: /var/lib/github-runner-cache/skillstore-cli/skillstore-cli-cli-v1.20.4-Linux-X64
📋 File size: 37M
🚀 Next run will use cached version (instant!)
```

### Second Run (Cache Hit)
```
✅ Found local cache: /var/lib/github-runner-cache/skillstore-cli/skillstore-cli-cli-v1.20.4-Linux-X64
📋 Cache file size: 37M
✅ CLI downloaded successfully
```

### New Version Released
```
Fetching latest release tag...
Latest release: cli-v1.21.0
❌ No cached version found for cli-v1.21.0
📦 Existing cached versions:
  - skillstore-cli-cli-v1.20.4-Linux-X64 (37M)
Downloading skillstore-cli (cli-v1.21.0)...
✅ Saved to local cache: ...
```

## Performance Comparison

| Runner Type | First Run | Subsequent Runs | Savings |
|-------------|-----------|-----------------|---------|
| GitHub-hosted | ~25s | ~25s | 0s |
| Self-hosted (no volume) | ~25s | ~25s | 0s |
| Self-hosted (with volume) | ~30s | **<1s** | ~25s/run |

**Example savings:** 10 workflows/day × 25s = **4+ minutes saved daily!**

## Cache Invalidation

Cache automatically updates when:
- CLI version changes (e.g., "latest" points to new release)
- OS or architecture changes

Manual cleanup:
```bash
# Remove all cached versions
rm -rf /var/lib/github-runner-cache/skillstore-cli/*

# Remove specific version
rm /var/lib/github-runner-cache/skillstore-cli/skillstore-cli-cli-v1.20.4-Linux-X64
```

## References

- [Docker Setup Guide](./DOCKER-SETUP.md) - **Required for Docker runners**
- [Caching on self-hosted runners](https://github.com/orgs/community/discussions/18549)
- [GitHub Actions runner issues](https://github.com/actions/runner/issues/2193)
