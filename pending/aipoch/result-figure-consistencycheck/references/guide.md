# Figure Legend Consistency Check Reference List

## Input List

- Figure legend text
- Results description in the main text
- Figure numbers and citation locations

## Output List

- Inconsistency list CSV (Figure No./Location/Issue/Suggestion/Priority)
- Explanatory report Markdown (Summary and revision suggestions)

## Output Format

- The inconsistency list should be output separately as a CSV (UTF-8 encoding), where "Location/Citation" should only be filled as `Page XX`.
- The list should be detailed down to the panel/sub-figure level; issue descriptions must be verifiable, and suggestions must be actionable.
- The explanatory report should be in Markdown (UTF-8 encoding).

## Quality Check

- Consistency in values, units, and directions.
- Consistency between figure legends and the core conclusions described in the main text.

## Scope Description

- Only compare figure legend text with the results description in the main text; do not read image content.

## Common Issues

- Checking only text without verifying numerical values.
- Missing figure citations within the main text.