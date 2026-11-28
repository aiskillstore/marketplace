---
id: "atomic-file-replacement"
title: "Atomic file replacement and recovery"
category: "concurrency"
summary: "Publish complete local files while accounting for concurrency, durability and platform semantics."
aliases: ["atomic rename","atomic file write","temp file fsync","crash safe configuration","replace file","dosyayı atomik değiştirme","yarım yazılan ayar dosyası","geçici dosya kullanarak güvenli kayıt"]
decisions: [{"when":"Readers need either the old or the new complete file","use":"Write and validate a temp file in the same directory, then rename with documented durability settings.","tradeoff":"Writer coordination and filesystem behavior still need evaluation."},{"when":"Several writers merge state or transactional history is required","use":"Use a database or a durable versioned journal with an explicit commit boundary.","tradeoff":"A heavier dependency brings recovery and concurrency capabilities."}]
checks: ["Interrupt before and after replacement and confirm readers see a complete supported version.","Race writers and test permission, disk-space and same-volume assumptions."]
sources: [{"title":"The Open Group rename specification","url":"https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html"},{"title":"SQLite atomic commit","url":"https://sqlite.org/atomiccommit.html"}]
---

<!-- Generated record title. -->
# Atomic file replacement and recovery

## Scenario

A local CLI writes a settings snapshot read by other processes. The machine can crash mid-save.

## Failure modes

In-place writes expose truncated data. Atomic rename and durable persistence are distinct, and moving across filesystems can fail.

## Explain it simply

Write the replacement next to the old file and switch names only after the new contents are complete.

## Implementation guidance

Write a temporary file in the target directory, set any required permissions, finish and validate it, then replace the target using the platform API. Where crash durability is a requirement, explicitly account for flushing the file and, when supported, the containing directory. Clean up abandoned temporary files after verified crashes. Inject failures before rename and just after it and check that a reader always observes a whole old or new snapshot.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Readers need either the old or the new complete file** Write and validate a temp file in the same directory, then rename with documented durability settings. Writer coordination and filesystem behavior still need evaluation.
- **Several writers merge state or transactional history is required** Use a database or a durable versioned journal with an explicit commit boundary. A heavier dependency brings recovery and concurrency capabilities.

## Verification

- Interrupt before and after replacement and confirm readers see a complete supported version.
- Race writers and test permission, disk-space and same-volume assumptions.

## Sources

- [The Open Group rename specification](https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html)
- [SQLite atomic commit](https://sqlite.org/atomiccommit.html)

<!-- End generated record details. -->
