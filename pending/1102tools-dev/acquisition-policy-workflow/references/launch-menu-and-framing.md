# Launch menu and framing

## Complete menu

Use this menu for a vague request, an invocation without a defined task, or when the user asks what the workflow can do:

```text
What would you like to do?

1. Explain the current codified FAR, DFARS, or agency-supplement rule
2. Determine the documented policy status for an agency and FAR part
3. Compare codified text, RFO model text, and an agency deviation
4. Compare regulatory versions or explain what changed
5. Trace a FAR, DFARS, or agency rulemaking
6. Find open procurement rulemakings and comment deadlines
7. Analyze public comments and stakeholder positions
8. Prepare an Acquisition Policy Impact Brief
9. Refresh an earlier policy analysis
10. Help me choose

Which option would you like? You can reply with the number, label, or your own wording.
```

The menu is the complete response. Do not perform capability preflight or retrieval first.

## Direct routing

Route a clear request without forcing the menu:

- A current section or definition request routes to mode 1.
- A named agency plus FAR part and words such as applies, current policy, deviation, or RFO routes to mode 2.
- A request to compare FAR/eCFR, model text, and an agency deviation routes to mode 3.
- Before-and-after or change requests route to mode 4.
- A FAR/DFARS case, RIN, rule history, proposed rule, final rule, or withdrawal request routes to mode 5.
- A command or assertion that a proposed rule, withdrawn rule, future-effective final rule, or model deviation is already current or operative routes directly to the relevant status boundary. Correct the classification and state the missing effective-date or agency-adoption evidence; do not show the menu merely because the request is phrased as an instruction.
- Open comment periods or deadlines route to mode 6.
- Comment themes, associations, stakeholder positions, or docket comments route to mode 7.
- A formal brief routes to mode 8.
- A supplied prior record or brief with a refresh request routes to mode 9.

If two routes are equally plausible, show the menu and mark the likely choices `Recommended` without hiding any option.

## Minimum framing by mode

| Mode | Required before retrieval |
|---|---|
| Current codified rule | Citation or part; as-of date defaults to today if user accepts current |
| Agency policy status | Agency; FAR part or citation; as-of date; relevant procurement date when timing may change treatment |
| Three-layer comparison | Agency; FAR part or citation; as-of date |
| Version comparison | Citation; before and after dates or a described period |
| Rulemaking history | Case number, RIN, docket ID, document number, or sufficiently specific topic |
| Open rulemakings | Topic or procurement scope; as-of date; optional agency |
| Comment analysis | Docket or proposed-rule document; sampling purpose; audience lens |
| Impact brief | Exact policy question; scope; as-of date; agency when relevant; audience lens |
| Refresh | Prior record or brief; new as-of date; changed scope if any |

Use `government`, `industry`, or `neutral` as the audience-lens values. Neutral presents both operational perspectives without advocating for either.
