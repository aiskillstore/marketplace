# Deduplication and Conflict Resolution

## Deduplication Strategies

- keep_first: Keep the first occurring record
- keep_last: Keep the last occurring record
- keep_longest: Keep the record with the most complete field information
- keep_all: No deduplication, only output and mark the source

## Conflict Determination

A conflict is identified when multiple non-null and different values appear for the same field under the same primary key.

## Handling Methods

- report_only: Only output conflict reports; merged results are retained according to the deduplication strategy
- manual: Require the user to specify conflict resolution rules
- prefer_source: Select values based on priority source files (e.g., the most recent file)

## When to Prompt the User

- Primary keys are not unique or have a high missing rate
- Conflict fields involve key business fields (e.g., price, contract status)
- Composite keys are required but the user has not provided rules