# CI recipes

All of these run `liarjs` version-pinned. Node 22 or newer, and a Chromium the launcher can find.
`liarjs` finds Chrome, Chromium or Edge at the usual paths; set `LIARJS_CHROME=/path/to/binary` when
it is somewhere else.

Keep Chrome's sandbox enabled in every one of these. The two things a CI container actually needs are
enough shared memory and the capabilities the sandbox requires; both are properties of how the
container is started, and both are shown below.

## GitLab CI

```yaml
fingerprint:
  image: node:22
  variables:
    LIARJS_CHROME: /usr/bin/chromium
    KUBERNETES_MEMORY_REQUEST: 2Gi
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends chromium
  script:
    - npx liarjs@0.3 --headless --json scan.json --min-score 60
    - npx liarjs@0.3 diff baseline.json scan.json
  artifacts:
    when: always
    paths: [scan.json]
```

## Docker

Chrome needs more shared memory than the 64 MB Docker gives `/dev/shm` by default, and it needs its
sandbox to be permitted rather than turned off. Both are flags on `docker run`, so the image stays
clean:

```dockerfile
FROM node:22-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium ca-certificates fonts-liberation \
 && rm -rf /var/lib/apt/lists/*
ENV LIARJS_CHROME=/usr/bin/chromium
USER node
```

```bash
docker run --rm \
  --shm-size=1g \
  --security-opt seccomp=chrome.json \
  -v "$PWD:/w" -w /w node-liarjs \
  npx liarjs@0.3 --headless --min-score 60
```

`chrome.json` is the seccomp profile the Chromium project publishes for exactly this case. It lets
the sandbox initialise inside a container without granting the whole container extra privilege.

Run the browser as a non-root user (`USER node` above). Chrome's sandbox declines to initialise as
root, and that is the actual reason most container guides reach for a sandbox flag.

## Inside a Playwright or Puppeteer suite

Asserting on the harness that the rest of the suite uses is stricter than scanning a separately
launched browser, because the launch flags, plugins and proxy under test are the ones measured.

```ts
import { test, expect } from '@playwright/test';
import { checkPage } from 'liarjs';

test('harness fingerprint stays coherent', async ({ page }) => {
  const result = await checkPage(page);

  // Assert on ids, not only on the total, so an unrelated drift does not mask a real one.
  const failed = result.checks.filter((c) => c.status === 'bad').map((c) => c.id);
  expect(failed, JSON.stringify(result.checks.filter((c) => c.status === 'bad'), null, 2)).toEqual([]);
  expect(result.score).toBeGreaterThanOrEqual(85);
});
```

```bash
npm install --save-dev liarjs
```

## Ignoring checks that cannot hold in your environment

Filter in the library API rather than lowering the floor for everything:

```ts
const IGNORED = new Set(['tz', 'conn-rtt']);   // datacenter IP, synthetic network info
const failed = result.checks.filter((c) => c.status === 'bad' && !IGNORED.has(c.id));
```

Every ignored id deserves a comment saying why. An ignore list without reasons becomes the place
real regressions go to hide.

## Refreshing a baseline

Do it deliberately, in its own commit:

```bash
npx liarjs@0.3 --headless --json baseline.json
npx liarjs@0.3 diff baseline.json.bak baseline.json > baseline-change.txt
```

Put the diff output in the commit message. A baseline that moves without an explanation is the same
as having no baseline.

Take the baseline in the same mode the job runs in. A headed baseline compared against a headless run
reports the headless tells as regressions on the first comparison.

## Exit codes

| code | meaning |
|---|---|
| 0 | scan completed, score at or above `--min-score` if given |
| 1 | score below `--min-score` |
| 2 | error, for example no browser found or a CDP endpoint that did not answer |

## Keeping traffic internal

`--offline` makes no outbound request and skips the 8 cross-layer checks. To keep those checks while
keeping the traffic inside your own infrastructure, deploy the endpoint yourself: it is a small
Cloudflare Worker in the open-source repo, and `--endpoint <url>` points the scan at it.
