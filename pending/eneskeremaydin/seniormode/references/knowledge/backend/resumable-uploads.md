---
id: "resumable-uploads"
title: "Resumable uploads and content integrity"
category: "backend"
summary: "Choose an upload protocol that preserves completeness across retry, interruption and finalization."
aliases: ["resumable upload","chunk upload","multipart upload","checksums","interrupted upload","dosya yükleme yarıda kesilince","kaldığı yerden dosya yükleme","parçalı dosya yükleme","yüklemeyi baştan yapmak"]
decisions: [{"when":"Uploads are large or links are unreliable","use":"Use an existing resumable protocol with server-defined offsets and checksums, then finalize atomically.","tradeoff":"Sessions, expiry and cleanup require additional state."},{"when":"Files are small and the connection is predictable","use":"Use a bounded single upload with request limits and a whole-file integrity check.","tradeoff":"A network interruption restarts that small request."}]
checks: ["Re-send a chunk and resume at a server-reported offset.","Reject mismatches and never expose a partially assembled file as complete."]
sources: [{"title":"tus protocol for resumable uploads","url":"https://tus.io/protocols/resumable-upload"},{"title":"Amazon S3 multipart upload","url":"https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html"}]
---

<!-- Generated record title. -->
# Resumable uploads and content integrity

## Scenario

A researcher uploads a large field recording over a train connection. Retrying the whole upload wastes time and bandwidth.

## Failure modes

A repeated chunk can shift offsets without checks. Finalizing before all parts arrive creates incomplete objects. Abandoned parts incur storage costs.

## Explain it simply

Save progress as the file arrives and verify what reached storage before declaring it complete.

## Implementation guidance

Give every upload attempt a stable server-side ID and check the authoritative offset or part list before resuming. Gate final publication on completeness and integrity and make finalization safe to repeat. Stale multipart state needs a retention policy and cleanup path. Test two clients sending the same range, an interrupted acknowledgement, checksum failure, a stale upload ID and a retry of the last finalize step.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Uploads are large or links are unreliable** Use an existing resumable protocol with server-defined offsets and checksums, then finalize atomically. Sessions, expiry and cleanup require additional state.
- **Files are small and the connection is predictable** Use a bounded single upload with request limits and a whole-file integrity check. A network interruption restarts that small request.

## Verification

- Re-send a chunk and resume at a server-reported offset.
- Reject mismatches and never expose a partially assembled file as complete.

## Sources

- [tus protocol for resumable uploads](https://tus.io/protocols/resumable-upload)
- [Amazon S3 multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)

<!-- End generated record details. -->
