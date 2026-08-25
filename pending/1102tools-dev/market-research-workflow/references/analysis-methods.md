# Analysis methods

## Scope

Keep government-wide and agency-specific datasets separate. State the filter and denominator for every percentage. Do not merge scopes merely to increase counts.

## Entity resolution

Normalize names only for comparison. Use stable public identifiers when available. Document unresolved aliases and recipient records. Do not merge entities based only on a similar name.

## Amounts and time

- Preserve negative obligations; explain deobligations and closeout activity.
- Convert fiscal-year strings to integers before comparison.
- Mark the current fiscal year partial before September 30.
- Mark the first fiscal year partial when the lookback begins after October 1.
- Exclude partial years from full-year growth rates.
- Distinguish obligations, outlays, current award amount, potential ceiling, and quoted or catalog prices.

## Samples and missing data

Label top-N, keyword, value-sorted, or capped samples. Never report their median, minimum, share, or distribution as a population result. Report null competition, set-aside, contract-type, or recipient fields and state denominator coverage.

For thin or zero results, show the exact query and then propose one controlled broadening step at a time: agency to government-wide, combined codes to primary code, narrower to wider dates, or exact to carefully chosen keywords. Preserve each result and obtain approval before materially changing scope.

## Reproducibility

Record the semantic operation, sanitized parameters, retrieval time, returned count, pages or coverage, transformations, exclusions, deduplication, and formulas. Independently recompute numeric tables before delivery.
