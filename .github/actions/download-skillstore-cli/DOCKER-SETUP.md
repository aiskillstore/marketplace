# Self-Hosted Runner Cache Setup

## TL;DR - It Should Just Work™

**Good news:** The cache uses `/home/runner/_work/_cache/skillstore-cli` which is **already persistent** in standard Docker runner setups!

No extra configuration needed in most cases. The `_work` directory is automatically mounted as a volume by popular runner images.

## Why `_work` Directory?

According to [GitHub Actions runner documentation](https://github.com/actions/runner/issues/2708):

- ✅ **Standard persistent path** - Already mounted as volume in most Docker setups
- ✅ **No extra Docker config needed** - Works out-of-the-box
- ✅ **Automatic cleanup** - Runner cleans up old workflows but preserves `_cache`
- ✅ **Permission-safe** - Same user/group as workflow execution
- ❌ `~/.cache` - Ephemeral, reset on container restart
- ❌ `/var/lib/*` - Requires additional volume mount + permissions

## Verify Your Setup (Optional)

Check if `_work` is already mounted:

```bash
# List mounts for your runner container
docker inspect <runner-container-name> | grep -A 10 '"Mounts"'
```

You should see something like:
```json
{
  "Type": "volume",
  "Name": "runner-work",
  "Source": "/var/lib/docker/volumes/runner-work/_data",
  "Destination": "/home/runner/_work",
  "Mode": "z",
  "RW": true
}
```

## Standard Runner Setup

Most runner images (like `myoung34/github-runner`) **already configure** the `_work` volume:

### Docker Compose

```yaml
version: '3.8'

services:
  github-runner:
    image: myoung34/github-runner:latest
    environment:
      REPO_URL: https://github.com/your-org/your-repo
      ACCESS_TOKEN: ${GITHUB_TOKEN}
    volumes:
      - runner-work:/home/runner/_work  # ← Standard, already included
    restart: unless-stopped

volumes:
  runner-work:  # ← Cache persists here automatically
```

### Docker Run

```bash
docker run -d \
  --name github-runner \
  -e REPO_URL="https://github.com/your-org/your-repo" \
  -e ACCESS_TOKEN="${GITHUB_TOKEN}" \
  -v runner-work:/home/runner/_work \
  myoung34/github-runner:latest
```

### Kubernetes (actions-runner-controller)

```yaml
apiVersion: actions.summerwind.dev/v1alpha1
kind: RunnerDeployment
metadata:
  name: github-runner
spec:
  template:
    spec:
      volumes:
        - name: work
          emptyDir: {}  # For ephemeral runners
          # Or use PVC for persistent cache:
          # persistentVolumeClaim:
          #   claimName: runner-work-pvc
      containers:
        - name: runner
          volumeMounts:
            - name: work
              mountPath: /home/runner/_work
```

## How It Works

### First Run
```
📁 Cache directory doesn't exist, creating: /home/runner/_work/_cache/skillstore-cli
✅ Cache directory created successfully
❌ No cached version found for cli-v1.20.4
📦 No cached versions found (first run)
Downloading skillstore-cli (cli-v1.20.4)...
✅ Saved to local cache: /home/runner/_work/_cache/skillstore-cli/skillstore-cli-cli-v1.20.4-Linux-X64
📋 File size: 37M
🚀 Next run will use cached version (instant!)
```

### Subsequent Runs
```
✅ Found local cache: /home/runner/_work/_cache/skillstore-cli/skillstore-cli-cli-v1.20.4-Linux-X64
📋 Cache file size: 37M
✅ CLI downloaded successfully
```

**Time:** <1 second (instant!)

## Troubleshooting

### Issue: "No cached versions found" on every run

**Diagnosis:** `_work` directory is not mounted as persistent volume.

**Check:**
```bash
# Inside runner container
ls -la /home/runner/_work/_cache/skillstore-cli/

# After workflow run, check if files persist
docker exec <runner-container> ls -la /home/runner/_work/_cache/skillstore-cli/
```

**Fix:** Ensure `_work` is mounted (see setup examples above).

### Issue: Permission denied

**Diagnosis:** Cache directory has wrong ownership.

**Fix (inside container):**
```bash
# Run as part of runner setup
chown -R runner:docker /home/runner/_work/_cache
chmod -R 755 /home/runner/_work/_cache
```

### Issue: Cache grows too large

The `_work` directory accumulates workflow artifacts. According to [GitHub runner issue #2708](https://github.com/actions/runner/issues/2708), you can clean up old data:

```bash
# On Docker host or inside container
# Keep only last 7 days of cache
find /home/runner/_work/_cache -type f -mtime +7 -delete
```

Or add cleanup to your runner startup script.

## Performance Comparison

| Setup | First Run | Subsequent Runs | Daily Savings (10 runs) |
|-------|-----------|-----------------|-------------------------|
| No persistent volume | 30s | 30s | 0 (no benefit) |
| `_work` mounted ✅ | 30s | <1s | ~290s (~5min) |
| GitHub cloud cache | 25s | 25s | 0 (network every time) |

## Why Not Use Other Paths?

| Path | Issue |
|------|-------|
| `~/.cache` | Ephemeral, [HOME remapped](https://github.com/actions/runner/issues/2193) to temp dirs |
| `/tmp` | Cleaned on container restart |
| `/var/lib/*` | Requires extra volume + sudo permissions |
| `_work` ✅ | **Standard, persistent, just works** |

## Alternative: GitHub Cloud Cache

If you can't use persistent volumes (ephemeral K8s pods, etc.), remove `cache-dir` to fall back to GitHub's cloud cache:

```yaml
- name: Download skillstore CLI
  uses: ./.github/actions/download-skillstore-cli
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    # No cache-dir = uses actions/cache@v4 (cloud-based)
```

**Trade-off:** 20-30s download per run vs instant with local cache.

## References

- [Self-hosted runner cleanup bloat](https://github.com/actions/runner/issues/2708)
- [Cleaning up working directory fails](https://github.com/actions/runner/issues/3541)
- [Workspace cleanup between runs](https://github.com/orgs/community/discussions/51329)
- [Container-based action cleanup](https://devopsjournal.io/blog/2023/06/21/GitHub-container-based-Action-cleanup)
