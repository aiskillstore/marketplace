---
id: "safe-file-ingest"
title: "Defensive file ingest for user uploads"
category: "security"
summary: "Treat uploaded files as untrusted data throughout storage, validation and serving."
aliases: ["file upload validation","upload content type","object isolation","file processing limits","quarantine","yüklenen dosya türünü doğrulama","dosya işleme karantinası","yükleme boyut sınırı"]
decisions: [{"when":"Only a narrow set of file types is required","use":"Allowlist supported formats and bound stored and decoded size; serve from a separate controlled origin.","tradeoff":"Validation and content transformation can add latency and cost."},{"when":"High-risk documents require isolated processing","use":"Use an isolated worker with constrained permissions, quarantine and explicit result states.","tradeoff":"Users must see processing status and recoverable failures."}]
checks: ["Verify type mismatches, decoded-size limits and failed processing leave objects private.","Confirm approved files are served with the expected origin and response headers."]
sources: [{"title":"OWASP File Upload Cheat Sheet","url":"https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html"},{"title":"Amazon S3 multipart checksums","url":"https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html"}]
---

<!-- Generated record title. -->
# Defensive file ingest for user uploads

## Scenario

A portfolio service accepts images and previews them after processing in a background worker.

## Failure modes

Name and MIME hints are user controlled. Very large decoded images can exhaust resources, and serving uploads from an application origin can create unwanted trust.

## Explain it simply

Place incoming files in a restricted area and make them public only after checking they are the kind and size expected.

## Architecture notes

Establish an allowed content policy and limits on uploaded and decoded size. Generate the storage name independently of supplied names and parse in a constrained worker. Publish only after a successful recorded result, using a response or origin policy for untrusted content. Exercise oversized, mislabeled and interrupted inputs and prove that each remains quarantined.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Only a narrow set of file types is required** Allowlist supported formats and bound stored and decoded size; serve from a separate controlled origin. Validation and content transformation can add latency and cost.
- **High-risk documents require isolated processing** Use an isolated worker with constrained permissions, quarantine and explicit result states. Users must see processing status and recoverable failures.

## Verification

- Verify type mismatches, decoded-size limits and failed processing leave objects private.
- Confirm approved files are served with the expected origin and response headers.

## Sources

- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [Amazon S3 multipart checksums](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity-upload.html)

<!-- End generated record details. -->
