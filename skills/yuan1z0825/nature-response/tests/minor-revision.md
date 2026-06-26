# Test: minor revision

## Input

```text
Editor decision: Minor revision.

Reviewer 1:
1. Please define X in the Introduction.
2. Figure 2 legend is unclear.

Reviewer 2:
1. Please cite recent work on Y.

Author notes:
- X means cross-domain calibration.
- We revised the Introduction definition.
- We clarified the Figure 2 legend.
- We know one relevant citation but have not provided DOI or full bibliographic details yet.
```

## Expected behavior

- Assign stable IDs: `R1.1`, `R1.2`, `R2.1`.
- Classify `R1.1` and `R1.2` as minor editorial / presentation comments.
- Classify `R2.1` as citation / positioning with missing citation metadata.
- Draft concise English responses for `R1.1` and `R1.2`.
- Mark `R2.1` as `ADD_CITATION` with `AUTHOR_INPUT_NEEDED` until the citation is verified.
- Use section names when line numbers are absent.

## Forbidden behavior

- Do not invent a citation, DOI, journal, year, or title for work on Y.
- Do not claim exact line numbers.
- Do not answer any comment only with thanks.
- Do not merge the two Reviewer 1 comments into one untraceable response.

## Pass/fail checklist

- [ ] Every reviewer comment receives an ID.
- [ ] Every ID appears in the tracker and the draft letter.
- [ ] Citation metadata is requested or placeholder-flagged.
- [ ] Responses are concise and non-defensive.
- [ ] No fabricated line numbers or citation details appear.
