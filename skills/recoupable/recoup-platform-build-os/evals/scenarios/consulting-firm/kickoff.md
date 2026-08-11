# Kickoff — boutique consulting firm (RICH input)

Tests extraction: turning a real input packet into entities, a staged pipeline, and seeded
`knowledge/` + `library/`. The builder's domain input is the **packet in `./kickoff/`** next to this
file:

- `kickoff/discovery-call-acme.md` — transcript of a discovery call with a prospect (Acme Corp).
- `kickoff/clients.csv` — the current pipeline (clients, stages, value, owner, next action).
- `kickoff/notes.md` — loose notes: recurring questions, a standing decision, a one-off idea, a
  reusable proposal structure.

The builder reads all three fully, then builds the OS for this boutique strategy-consulting practice.

**What a strong build looks like:** archetype = consulting (leads → qualifying → discovery → proposal
→ negotiation → won/lost); a `clients/` entity folder with a record per CSV row (each with a README
dashboard); the pipeline `_board.md` reflecting the CSV; `knowledge/faqs/` + `knowledge/decisions/`
populated from `notes.md` (standard discovery deliverable, value-based-pricing decision, guarantee
policy); a proposal template in `library/` mined from the notes; the one-off "pricing calculator idea"
parked in `work/` (NOT a top-level folder). Inferred facts marked "draft — confirm".
