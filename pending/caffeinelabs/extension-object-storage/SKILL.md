---
name: extension-object-storage
description: General file/object storage, such as for images, videos, files, documents and other bulk data. Perfect fit for image galleries, video galleries, and other file or object management. Supports large files beyond IC limit, with browser-cached HTTP URL access.
version: 1.1.0
compatibility:
  mops:
    caffeineai-object-storage: "~1.1.0"
caffeineai-subscription: [none]
---

# Object Storage
Object storage extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds off-chain file/object storage with on-chain references. The `MixinObjectStorage` mixin provides infrastructure for file operations; you track uploaded files in your own data structures using `Storage.ExternalBlob`.

## Required Setup Checklist

All four steps are mandatory. Skipping any one causes `403 Forbidden: Invalid payload` at upload time.

1. **mops dependency** — add `caffeineai-object-storage` to `mops.toml` under `[dependencies]`.
2. **Mixin invocation** — `include MixinObjectStorage()` in `main.mo` (imported from `"mo:caffeineai-object-storage/Mixin"`).
3. **Storage.ExternalBlob types** — every data field that represents a file MUST use `Storage.ExternalBlob`, never `Text`.
4. **Frontend npm package** — `@caffeineai/object-storage` installed and `ExternalBlob.fromBytes(bytes, file.type, file.name)` used at the call site.

CRITICAL: The frontend package (`@caffeineai/object-storage`) does NOT work without the backend mops package (`caffeineai-object-storage`). Installing only the npm package and not the mops package causes silent upload failures (403 from the storage gateway). You MUST install both together.

# Backend

File content is stored off-chain. The backend manages references to external files using the `Storage.ExternalBlob` type from `mo:caffeineai-object-storage/Storage`. The frontend handles the actual upload/download; the backend only stores the reference.

CRITICAL: ANY data field that represents a file, image, photo, document, or media MUST use `Storage.ExternalBlob` as its type -- NEVER `Text`. Using `Text` breaks the upload/download proxy. Method parameters that accept file uploads MUST also use `Storage.ExternalBlob`, not `Text`.

Correct:
```
blob : Storage.ExternalBlob
```

Wrong:
```
blobId : Text
imageUrl : Text
fileRef : Text
```

## Module API

The only type you use from `mo:caffeineai-object-storage/Storage` is `ExternalBlob` (which is `Blob`). All other functions in `Storage.mo` are internal infrastructure used by `MixinObjectStorage` -- do not call them directly.

## Setup in main.mo

`include MixinObjectStorage()` MUST be placed in `main.mo`, not in a custom mixin file. Your own file-tracking logic goes in a separate mixin.

```motoko filepath=src/backend/main.mo
import MixinObjectStorage "mo:caffeineai-object-storage/Mixin";
import Storage "mo:caffeineai-object-storage/Storage";

actor {
  include MixinObjectStorage();

   // Track file references
  type Data = {
        id: Text;
        blob: Storage.ExternalBlob;
        name: Text;
        // other metadata
    };
};
```

## Wrong: Do NOT Implement Storage Methods Yourself

NEVER create your own implementation of `_immutableObjectStorageCreateCertificate` or any other `_immutableObjectStorage*` method. These are platform-reserved method names provided exclusively by the `MixinObjectStorage` mixin from the mops package. Hand-written implementations produce wrong return types and cause `403 Forbidden: Invalid payload` at upload time.

Wrong — inline stub in main.mo:
```motoko filepath=wrong.mo
// WRONG: Do not write this yourself
public shared func _immutableObjectStorageCreateCertificate(fileHash : Text) : async Blob {
  CertifiedData.set(Blob.fromArray(hashBytes));
  Blob.fromArray([])
};
```

Wrong — custom mixin file mimicking the platform shape:
```motoko filepath=wrong-mixin.mo
// WRONG: Do not create src/backend/mixins/object-storage-api.mo
import ObjectStorageMixin "mixins/object-storage-api";
include ObjectStorageMixin();
```

The correct import path is ALWAYS `"mo:caffeineai-object-storage/Mixin"` — a mops package, never a relative path. Any relative import like `"mixins/object-storage-api"` or `"./ObjectStorage"` is wrong.

The correct signature produced by the platform mixin is:
```
_immutableObjectStorageCreateCertificate : (blobHash : Text) -> async record { method : Text; blob_hash : Text }
```

Any other return type (`Blob`, `()`, `Text`, etc.) will fail gateway validation.

# Frontend

Backend `Blob` fields are represented as `ExternalBlob` on the frontend.


```typescript
import { ExternalBlob } from "@caffeineai/object-storage";
import type { FileRecord } from "@caffeineai/object-storage";
```

## ExternalBlob API

```typescript
class ExternalBlob {
  getBytes(): Promise<Uint8Array<ArrayBuffer>>;
  getDirectURL(): string;
  static fromURL(url: string): ExternalBlob;
  static fromBytes(
    blob: Uint8Array<ArrayBuffer>,
    contentType?: string,
    filename?: string,
  ): ExternalBlob;
  withUploadProgress(onProgress: (percentage: number) => void): ExternalBlob;
}
```

## Uploading Files

Pass the browser `File` type and name into `fromBytes` so the gateway blob tree stores `Content-Type` and `Content-Disposition` (original filename). Also pass `file.name` to the backend so app records keep the filename for lists and UI.

```typescript
const handleUpload = async (file: File) => {
  const bytes = new Uint8Array(await file.arrayBuffer());
  const blob = ExternalBlob.fromBytes(bytes, file.type, file.name).withUploadProgress((pct) => {
    setProgress(pct);
  });

  await actor.uploadFile(file.name, blob);
};
```

Gateway GET/HEAD responses echo the stored filename via `Content-Disposition`. Keep the backend `filename` field for queries and display without hitting the gateway.

## Displaying Files

Use `getDirectURL()` for inline display (images, videos). This returns an opaque proxy URL -- it has no file extension, so never inspect the URL to determine file type.

```typescript
<img src={record.blob.getDirectURL()} alt={record.filename} />
```

## File Type Detection

CRITICAL: Never detect file types by inspecting the URL from `getDirectURL()`. These are opaque proxy URLs with no extension. Instead use the `filename` field from the backend record:

```typescript
const isImage = (filename: string) =>
  /\.(jpg|jpeg|png|gif|webp|svg|bmp|ico)$/i.test(filename);

// Conditional rendering
{isImage(record.filename) ? (
  <img src={record.blob.getDirectURL()} alt={record.filename} />
) : (
  <div>{record.filename}</div>
)}
```

If the backend also returns a `mimeType` field, prefer that:

```typescript
const isImage = (mimeType?: string) => mimeType?.startsWith("image/");
```

## Downloading Files

For downloads with the original filename, use `getBytes()` to create a downloadable link:

```typescript
const handleDownload = async (record: FileRecord) => {
  const bytes = await record.blob.getBytes();
  const blob = new Blob([bytes]);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = record.filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
```

Use `getDirectURL()` for inline display, `getBytes()` for save-as downloads.

## Summary

| Use case | Method | Notes |
|---|---|---|
| Display image/video | `blob.getDirectURL()` | Streaming, cached |
| Download with filename | `blob.getBytes()` | Wrap in Blob + anchor |
| Upload from browser | `ExternalBlob.fromBytes(bytes, file.type, file.name)` | MIME + filename in gateway headers |
| Detect file type | `filename` or `mimeType` field | NEVER inspect the URL |

# Verifying the Setup

Confirm the backend has the mops dependency installed. Check `src/backend/mops.toml`:

```toml
[dependencies]
caffeineai-object-storage = "0.1.2"
```

If `caffeineai-object-storage` is missing from `[dependencies]`, object storage will not work regardless of what the frontend does. Add it, run `mops install`, and rebuild.

# Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `403 Forbidden: Invalid payload` on `PUT /v1/blob-tree/` | Backend canister missing `_immutableObjectStorageCreateCertificate` or returning wrong type | Install `caffeineai-object-storage` in mops.toml, add `include MixinObjectStorage()` in main.mo, redeploy |
| `403 Forbidden: Invalid payload` (all files) | `@caffeineai/object-storage` npm installed but `caffeineai-object-storage` mops NOT installed | Add the mops dependency and rebuild backend |
| Method exists but still 403 | Hand-written stub returns wrong type (e.g. `Blob` or `()` instead of `record { method; blob_hash }`) | Remove the custom implementation, use the platform mixin instead |
| `Forbidden: Owner does not have an account with the cashier` | Cashier registration issue (unrelated to this skill) | Redeploy the backend canister to trigger self-healing registration |
