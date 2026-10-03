---
name: indexability
description: "Record an indexability pass for one URL. Use when a page must be fetchable before anyone asks whether it can be cited."
models: ""
---

# Indexability

An indexability pass says whether one URL can be fetched and listed. It is not a site grade.

## Checklist

Copy this list and tick it in order.

- [ ] 1. Name the one URL.
- [ ] 2. Record status, robots, and sitemap in the draft.
- [ ] 3. Run `python3 scripts/score.py --file draft.json`.

Check again until the script exits 0.

Go back to step 2 if step 3 fails.
