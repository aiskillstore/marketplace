# Docker Self-Hosted Runner Setup for Cache Persistence

## The Problem

GitHub Actions self-hosted runners running in Docker containers face a critical caching challenge:

- **Ephemeral containers**: Each workflow run may use a fresh container
- **No filesystem persistence**: Files created during one run are lost when the container is destroyed
- **Cache doesn't work**: Local cache directories like `~/.cache` are reset on every run

## The Solution

Mount a **persistent volume** from the Docker host into the container at a fixed path.

## Setup Instructions

### Option 1: Docker Compose (Recommended)

Create or update your `docker-compose.yml`:

```yaml
version: '3.8'

services:
  github-runner:
    image: myoung34/github-runner:latest
    environment:
      REPO_URL: https://github.com/your-org/your-repo
      RUNNER_NAME: self-hosted-runner
      ACCESS_TOKEN: ${GITHUB_TOKEN}
    volumes:
      # Persistent cache volume - THIS IS CRITICAL
      - /var/lib/github-runner-cache:/var/lib/github-runner-cache
      # Runner work directory
      - runner-work:/home/runner/_work
    restart: unless-stopped

volumes:
  runner-work:
```

### Option 2: Docker Run Command

```bash
docker run -d \
  --name github-runner \
  -e REPO_URL="https://github.com/your-org/your-repo" \
  -e RUNNER_NAME="self-hosted-runner" \
  -e ACCESS_TOKEN="${GITHUB_TOKEN}" \
  -v /var/lib/github-runner-cache:/var/lib/github-runner-cache \
  -v runner-work:/home/runner/_work \
  myoung34/github-runner:latest
```

### Option 3: Kubernetes (actions-runner-controller)

```yaml
apiVersion: actions.summerwind.dev/v1alpha1
kind: RunnerDeployment
metadata:
  name: github-runner
spec:
  template:
    spec:
      volumes:
        - name: cache
          hostPath:
            path: /var/lib/github-runner-cache
            type: DirectoryOrCreate
      containers:
        - name: runner
          volumeMounts:
            - name: cache
              mountPath: /var/lib/github-runner-cache
```

## Verifying the Setup

After starting your runner, check that the volume is mounted:

```bash
# Enter the container
docker exec -it github-runner bash

# Check if the directory exists and is writable
mkdir -p /var/lib/github-runner-cache/test
echo "test" > /var/lib/github-runner-cache/test/file.txt
cat /var/lib/github-runner-cache/test/file.txt
rm -rf /var/lib/github-runner-cache/test

# Exit container
exit
```

## How It Works

1. **First workflow run**:
   - Action creates `/var/lib/github-runner-cache/skillstore-cli/`
   - Downloads CLI (~37 MB, ~30s)
   - Saves to cache: `/var/lib/github-runner-cache/skillstore-cli/skillstore-cli-cli-vX.X.X-Linux-X64`
   - Shows: "🚀 Next run will use cached version (instant!)"

2. **Subsequent runs** (with volume mounted):
   - Finds cached file immediately
   - Copies from cache (<1s, no download!)
   - Shows: "✅ Found local cache: ..."

3. **Without volume mounted**:
   - Each run creates directory fresh
   - Downloads CLI every time (~30s per run)
   - No performance benefit

## Troubleshooting

### Cache still not persisting

**Check volume mount:**
```bash
docker inspect github-runner | grep -A 10 Mounts
```

You should see:
```json
"Mounts": [
    {
        "Type": "bind",
        "Source": "/var/lib/github-runner-cache",
        "Destination": "/var/lib/github-runner-cache",
        ...
    }
]
```

### Permission denied errors

The container user needs write access:

```bash
# On Docker host
sudo mkdir -p /var/lib/github-runner-cache
sudo chown -R 1001:1001 /var/lib/github-runner-cache  # Adjust UID/GID as needed
sudo chmod -R 755 /var/lib/github-runner-cache
```

### Still downloading every time

**Check the logs** for "Save to local cache" step:

```bash
# You should see this after first download:
✅ Saved to local cache: /var/lib/github-runner-cache/skillstore-cli/skillstore-cli-cli-v1.20.4-Linux-X64
📋 File size: 37M
🚀 Next run will use cached version (instant!)
```

If you don't see this, check:
1. Is `cache-dir` parameter set in the workflow?
2. Is the directory writable?
3. Is the volume actually mounted?

## Alternative: Use GitHub Hosted Cache

If persistent volumes are difficult to set up, fall back to GitHub's cache service by **removing** the `cache-dir` parameter:

```yaml
# Uses GitHub's cache service (slower but works anywhere)
- name: Download skillstore CLI
  uses: ./.github/actions/download-skillstore-cli
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    # No cache-dir = uses actions/cache@v4
```

## References

- [Caching on self-hosted runners](https://github.com/orgs/community/discussions/18549)
- [HOME dir shared between jobs](https://github.com/actions/runner/issues/2193)
- [Containerize GitHub Actions runner](https://baccini-al.medium.com/how-to-containerize-a-github-actions-self-hosted-runner-5994cc08b9fb)
- [Local Cache on Self-hosted Runner](https://github.com/marketplace/actions/local-cache-on-self-hosted-runner)
