---
id: "object-storage-lifecycle"
title: "Object retention and deletion lifecycle"
category: "data"
summary: "Express how object versions are retained, restored and ultimately removed."
aliases: ["object storage retention","lifecycle policy","version expiration","delete marker","data retention","nesne deposu sürüm saklama","dosya sürümlerinin süresi dolması","silme işaretçisi"]
decisions: [{"when":"Normal recovery and cost control dominate","use":"Use versioned buckets with explicit current, noncurrent and incomplete-upload lifecycle rules.","tradeoff":"Lifecycle changes are asynchronous and need monitoring."},{"when":"Some objects must remain immutable for a stated period","use":"Use appropriate retention locks or holds and audit authorized transitions separately.","tradeoff":"Irreversibility and storage cost need deliberate ownership."}]
checks: ["Verify expected state for current and noncurrent versions after logical deletion.","Test restore and expiry with representative lifecycle settings and hold states."]
sources: [{"title":"Amazon S3 lifecycle expiration","url":"https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html"},{"title":"Amazon S3 Object Lock","url":"https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html"}]
---

<!-- Generated record title. -->
# Object retention and deletion lifecycle

## Scenario

A company allows trash recovery for a week and must delete expired objects while retaining legal holds when they apply.

## Failure modes

Deleting a current key can leave earlier versions recoverable. Expiration rules may be asynchronous and retention policies may override cleanup.

## Explain it simply

Define how long copies stay recoverable and verify which copies actually disappear at the end of that period.

## Implementation guidance

Design separate policies for the current object, earlier versions, delete markers and incomplete multipart uploads. Keep a way to verify that a marked deletion actually converges to storage expiry within the allowed window. Model restore and legal hold explicitly, including which actor can release a regulation-driven hold. Prove with a versioned test object that a delete marker hides the current name while older version retention follows policy.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Normal recovery and cost control dominate** Use versioned buckets with explicit current, noncurrent and incomplete-upload lifecycle rules. Lifecycle changes are asynchronous and need monitoring.
- **Some objects must remain immutable for a stated period** Use appropriate retention locks or holds and audit authorized transitions separately. Irreversibility and storage cost need deliberate ownership.

## Verification

- Verify expected state for current and noncurrent versions after logical deletion.
- Test restore and expiry with representative lifecycle settings and hold states.

## Sources

- [Amazon S3 lifecycle expiration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html)
- [Amazon S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)

<!-- End generated record details. -->
