# Testing and verification

Start from an observable contract. Use small unit tests for pure rules, integration tests for storage and boundary contracts, end-to-end tests for important user flows, and targeted regression tests that reproduce the reported failure.

Select failure cases based on actual behavior. A reservation race needs independent transactions. A lost payment response needs a repeated logical request and an independently observable count. Shuffle tests can enumerate a tiny uniform input and include empty, skewed, and duplicate-ID scenarios. Control randomness, time, or asynchronous coordination as needed.

Use real dependencies at the lowest affordable boundary where their semantics matter. Use doubles for inaccessible components with a documented contract. Report commands and checks that ran, and state what was inferred or skipped.
