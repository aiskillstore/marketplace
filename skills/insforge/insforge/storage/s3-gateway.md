# S3-Compatible Storage Gateway

> **Default to the SDK.** `@insforge/sdk` (see [sdk-integration.md](./sdk-integration.md)) is the recommended path for storage work — it is the supported default for app code, handles auth/session scoping, and avoids shipping long-lived project-admin credentials. Use the S3 gateway only when the consumer is existing S3 tooling (CI, `rclone`, Terraform, backup/log shippers) and adopting the SDK would be impractical.

InsForge Storage speaks the **AWS S3 protocol** at `/storage/v1/s3`. Any SigV4-signing client — `aws` CLI, AWS SDKs, `rclone`, Terraform, custom scripts — can read and write the same buckets exposed through the `@insforge/sdk`, REST API, and Dashboard.

> **Requires InsForge 2.0.9 or later.** The S3 gateway was introduced in 2.0.9; earlier versions do not expose `/storage/v1/s3` and the admin endpoints under `/api/storage/s3/*` return 404. Confirm the project's server version before configuring any S3 client — on Cloud, check the Dashboard footer or `GET /api/health`; self-hosted, check your deployment's image tag.
>
> **Cloud only.** The S3 gateway is available on InsForge Cloud projects. Self-hosted deployments can achieve the same capability by running the platform against a MinIO or AWS S3 bucket and exposing `/storage/v1/s3` behind their own ingress.

## When to use the S3 gateway (vs. the SDK)

Pick the S3 gateway when the consumer is **server-side tooling that already speaks S3**:

- CI/CD pipelines pushing build artifacts (`aws s3 cp`, `aws s3 sync`, `rclone sync`).
- Migrating existing S3-based automation (Terraform `aws_s3_object`, backup scripts, log shippers) without rewriting it.
- Server/worker uploads where embedding `@insforge/sdk` is overkill.

Prefer the [InsForge SDK](./sdk-integration.md) for browser direct uploads, public download URLs, bucket visibility management, and typed helpers — the SDK is built for app code and does not require handing out long-lived S3 credentials.

## Setup

### Endpoint and region

Both values are shown in the Dashboard under **Storage → Settings → S3 Configuration**, or fetched via `GET /api/storage/s3/config`.

| Field | Value |
| --- | --- |
| Endpoint | `https://{app-key}.{region}.insforge.app/storage/v1/s3` |
| Region | `us-east-2` (or the value set via `AWS_REGION`) |

Clients **must** use path-style URLs (`forcePathStyle: true` / `addressing_style = path` / `force_path_style = true`). Virtual-hosted style (`{bucket}.endpoint/...`) is not supported — configurations that omit path-style will fail with signature or DNS errors.

### Access keys

#### Create a key

Generate credentials from **Storage → Settings → S3 Configuration → New access key** in the Dashboard, or via the admin API:

```bash
curl -X POST "$API_BASE/api/storage/s3/access-keys" \
  -H "x-api-key: $ACCESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"description":"backup-script"}'
```

Response:

```json
{
  "data": {
    "id": "11111111-1111-1111-1111-111111111111",
    "accessKeyId": "INSFABC123DEF456GH78",
    "secretAccessKey": "x7K2-a_pL9qRs4N8vYzWcE1fH5gJ3mUtBoD6ViXk",
    "description": "backup-script",
    "createdAt": "2026-04-22T00:00:00Z",
    "lastUsedAt": null
  }
}
```

> **The `secretAccessKey` is returned exactly once.** It is encrypted at rest and cannot be recovered later. Capture it immediately on create; if lost, revoke and recreate the key.

#### Revoke a key

```bash
curl -X DELETE -H "x-api-key: $ACCESS_API_KEY" \
  "$API_BASE/api/storage/s3/access-keys/$KEY_ID"
```

Revocation invalidates the server-side LRU cache immediately, so clients still holding the credentials start seeing `InvalidAccessKeyId` at once.

## Usage Examples

All examples assume:

- `endpoint` = `https://your-appkey.your-region.insforge.app/storage/v1/s3`
- `region` = `us-east-2`
- Path-style addressing enabled

### AWS SDK for JavaScript v3

```ts
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';

const client = new S3Client({
  forcePathStyle: true,
  region: 'us-east-2',
  endpoint: 'https://your-appkey.your-region.insforge.app/storage/v1/s3',
  credentials: {
    accessKeyId: 'your_access_key_id',
    secretAccessKey: 'your_secret_access_key',
  },
});

await client.send(
  new PutObjectCommand({
    Bucket: 'my-bucket',
    Key: 'hello.txt',
    Body: 'hello from node',
    ContentType: 'text/plain',
  })
);
```

### AWS CLI (shared credentials file)

```ini
# ~/.aws/credentials
[insforge]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key

# ~/.aws/config
[profile insforge]
region = us-east-2
endpoint_url = https://your-appkey.your-region.insforge.app/storage/v1/s3
s3 =
  addressing_style = path
```

```bash
aws --profile insforge s3 ls
aws --profile insforge s3 cp ./photo.jpg s3://my-bucket/photo.jpg
aws --profile insforge s3 sync ./dist s3://my-bucket/dist
```

### boto3 (Python)

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    region_name='us-east-2',
    endpoint_url='https://your-appkey.your-region.insforge.app/storage/v1/s3',
    aws_access_key_id='your_access_key_id',
    aws_secret_access_key='your_secret_access_key',
    config=Config(s3={'addressing_style': 'path'}),
)

s3.upload_file('photo.jpg', 'my-bucket', 'photo.jpg')
```

### rclone

```ini
# ~/.config/rclone/rclone.conf
[insforge]
type = s3
provider = Other
access_key_id = your_access_key_id
secret_access_key = your_secret_access_key
endpoint = https://your-appkey.your-region.insforge.app/storage/v1/s3
region = us-east-2
force_path_style = true
```

```bash
rclone copy ./dist insforge:my-bucket/dist
rclone sync insforge:my-bucket/backups ./local-backups
```

## Supported Operations

The gateway covers the operations common workloads depend on:

| Category | Operations |
| --- | --- |
| Bucket | `ListBuckets`, `CreateBucket`, `DeleteBucket`, `HeadBucket`, `ListObjectsV2` |
| Object | `PutObject`, `GetObject` (incl. `Range`), `HeadObject`, `DeleteObject`, `DeleteObjects`, `CopyObject` |
| Multipart | `CreateMultipartUpload`, `UploadPart`, `CompleteMultipartUpload`, `AbortMultipartUpload`, `ListParts` |
| Probe stubs | `GetBucketLocation`, `GetBucketVersioning` (for SDK startup checks) |

Streaming uploads (`STREAMING-AWS4-HMAC-SHA256-PAYLOAD`) are fully supported, so `aws s3 cp` with large files and `aws s3 sync` work without any client-side configuration changes.

## Shared Namespace with REST and SDK

An object uploaded via the S3 gateway appears immediately in the REST API, the SDK, and the Dashboard — and vice versa. There is no separate S3 bucket namespace to reconcile.

```bash
# Upload via S3 protocol
aws --profile insforge s3 cp photo.jpg s3://my-bucket/photo.jpg

# Same object is visible to the REST API
curl -H "x-api-key: $ACCESS_API_KEY" \
  "$API_BASE/api/storage/buckets/my-bucket/objects"
# { "data": [{ "key": "photo.jpg", ... }] }
```

This means buckets created via `npx -y @insforge/cli storage create-bucket` are reachable over S3, and objects uploaded with `aws s3 cp` can be served via the SDK's `download()` using the same key.

## Best Practices

- **Treat S3 keys like production credentials.** They grant project-admin-level access — every bucket is readable and writable regardless of the `public`/`private` flag. Never ship them to browsers, never commit them to source control.
- **Scope keys per workload.** Create distinct keys for CI, backups, and each automation tool so you can rotate or revoke them independently. Stay under the project cap of **50 keys**.
- **Rotate on schedule.** Revoking via `DELETE /api/storage/s3/access-keys/{id}` invalidates the server-side LRU cache immediately.
- **Always enable path-style addressing** on every client (`forcePathStyle: true` / `addressing_style = path` / `force_path_style = true`).
- **Capture `secretAccessKey` at creation time.** It is encrypted at rest and cannot be recovered; if lost, revoke and recreate the key.
- **Prefer the SDK for browser flows, public download URLs, bucket visibility changes, and typed helpers** — the gateway is for server-side S3 tooling, not app code.

## Common Mistakes

### Unsupported features

Reach for the matching alternative instead of trying to make these work:

- **Presigned URLs** (query-string SigV4). For browser direct uploads, use the REST helper `POST /api/storage/buckets/:bucket/upload-strategy`, or the SDK's `uploadAuto()` / `upload()`.
- **Session tokens** (`X-Amz-Security-Token`, user-JWT-scoped access). The gateway accepts only the long-lived access keys described above.
- **S3 governance features**: versioning, SSE-C / SSE-KMS, bucket policies, ACLs, object lock, tagging, lifecycle, replication, CORS config. These return `NotImplemented` (501).
- **Virtual-hosted-style URLs**. Path-style only.

### Configuration pitfalls

| Mistake | Solution |
|---------|----------|
| Using virtual-hosted style (`{bucket}.endpoint/...`) | Enable path-style addressing on every client |
| Losing the `secretAccessKey` after creation | Capture it at creation time; revoke and recreate if lost |
| Shipping access keys to a browser | Use the SDK or upload-strategy REST helper instead — S3 keys are project-admin |
| Expecting presigned URLs to work | Use `POST /api/storage/buckets/:bucket/upload-strategy` for browser direct uploads |
| Trying to set bucket policies / lifecycle / CORS via S3 | Not supported — manage visibility via the Dashboard / CLI |

## Recommended Workflow

```text
1. Generate an access key    → POST /api/storage/s3/access-keys (capture secret once)
2. Configure the client      → endpoint + region + path-style
3. Verify connectivity       → aws --profile insforge s3 ls
4. Use standard S3 tooling   → cp / sync / multipart uploads / Terraform
5. Rotate or revoke keys     → DELETE /api/storage/s3/access-keys/{id}
```
