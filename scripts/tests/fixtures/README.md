# Pack production cross-repository contract fixture

`pack-production-evaluation-v4.golden.json` is the exact JSON emitted by
Marketplace's trusted reconstruction and accepted by Skillstore's
`parsePackProductionEvaluation` plus `verifyPackProductionEvidenceDigest`.

This is a two-repository update point. Any change to the v4 producer, parser,
canonical JSON rules, DAG digest rules, best-single tournament, ablation,
evaluation-suite evidence, or usage provenance must update this fixture and
the copied parser test in `aiskillstore/skillstore` in the same rollout. A
Marketplace-only fixture update is a release blocker, not backward
compatibility.

The Generate Pack workflow remains pinned to CLI 2.12.0 and therefore fails
closed before Persist until the binding-aware CLI 2.13.0 release is available.
