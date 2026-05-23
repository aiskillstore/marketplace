# Scenario: Group Presentation — Before & After

A student group needs a 7-slide English presentation about Lu Hong. They have a `tips.txt` with content, but no photos, no group member list, and no design.

## Without pptx-prep (Bad)

See [bad-output.md](bad-output.md):
- AI invents group member names
- Uses wrong stock photo for Lu Hong
- Stretches a 1:1 photo into a 4:3 slot
- Hallucinates award names and dates
- 30 minutes of fixes needed

## With pptx-prep (Good)

1. **Structure confirmed**: 7 slides — Cover → Early Life → Career → Achievements → Awards → Team → Contact
2. **Materials collected**: User drops `tips.txt` + `lu_hong.jpg` + group names
3. **Photo aspect ratio caught**: Lu Hong photo is 1:1, slide slot is 4:3 — user chooses "cover" before generation
4. **Content overflow flagged**: Achievement list is long — warned, user accepts auto-adjust
5. **Missing items handled**: Award photo → user chooses placeholder. Group project info → AI drafts, marked needs-review.
6. **One-shot generation**: All materials resolved → pptx generates complete deck, zero rework.

See [manifest.yml](manifest.yml) for the final material manifest. All items are `ready` or `placeholder` — no unresolved `ai-fill` or `missing`.
