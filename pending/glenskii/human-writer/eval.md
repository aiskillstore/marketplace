# human-writer eval

Run this against the edited draft before returning it. Answer each check pass or fail. If anything fails, fix the draft and run the checks again. Don't return output until every check passes.

For Detect requests: skip this file entirely. The eval below applies only to Edit-mode output, since Detect never rewrites anything to check.

## Fidelity (the one rule that overrides everything else)

1. Does the edit preserve the writer's actual point, with no new claims, examples, stats, or opinions added?
2. Is every FIX a minimal correction (word swap, punctuation change, clause deletion), not a rewritten sentence?
3. Do the three to five voice signals noted in Workflow step 2 survive in the edited draft? Would the writer recognize it as their own writing, not a smoothed-over version?
4. Did any FLAG item accidentally get auto-fixed? Every FLAG-tier hit must remain untouched in the draft and only appear in the notes.
5. Were factual claims left alone unless the writer confirmed a change (ASK tier)?

## Checklist items didn't reintroduce themselves

6. Did any banned-vocabulary swap (#1) introduce a different banned word, or a synonym just as inflated as the one it replaced?
7. Does any repaired sentence now end in a superficial -ing tail clause (#4) that wasn't there before?
8. Is the long-dash count zero? Check the whole draft again, not just the lines that were flagged, a fix elsewhere can introduce one reflexively (#8).
9. Did a copulative fix (#5) accidentally weaken a real technical claim, especially in documentation register?
10. Are colon-reveal (#21) or fake-profound-kicker (#23) fixes deletions, not rewrites into a different metaphor or a different dramatic device?

## Structure and rhythm

11. Does the draft avoid uniform paragraph length and repeated sentence shape beyond what was already flagged (#18, #24), without the editor restructuring anything to force variation?
12. Does the piece end on a real concrete point, takeaway, or next action, not a restated summary (#14) or an un-deleted fake-profound kicker (#23)?
13. Is formatting proportionate: no emoji-as-decoration in professional/doc register (#15), no bolded-header bullet lists where prose reads better (#11), no stray Markdown in a plain-text destination (#16)?

## Register match

14. Does the register-calibration match what was applied: lightest touch for social/chat, full checklist for documentation and correspondence, full checklist plus the prohibited-term check for public-facing copy?
15. For public-facing copy specifically: was every prohibited term flagged with a suggested substitute, not silently swapped?

## Final read

16. Was this eval run directly against the actual edited draft, not assumed to pass?
17. Would the edited draft sound like the writer if read aloud to someone who knows their work?
18. Does the output include the corrected draft, plus a compact summary line (long pieces) or nothing extra (short pieces), plus any FLAG/ASK notes as a short bulleted list?
