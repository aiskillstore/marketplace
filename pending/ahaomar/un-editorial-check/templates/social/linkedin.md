# Professional-network post

Facts to keep intact: version 1.1.0, published 28 September 2026, zero npm dependencies, 43 rules. Recommended placement: a professional network feed, with the repository link as the final line. Keep the short paragraphs and the blank lines between them.

---

This month I published version 1.1.0 of `un-editorial-check`, an open-source editorial pre-screen for United Nations style English copy.

The scope is narrow on purpose. A large share of editorial review time goes on things a machine can check: a doubled word, a numeric date where the day-month-year form belongs, a bare country abbreviation, a figure with no source in its sentence, a contested territorial statement written as fact instead of attributed. Those are documented rules with recorded sources, so they can run before a reviewer opens the document.

What the 1.1.0 release added:

— Five lanes in every output format, so deterministic findings, heuristic review, harmful or discriminatory wording, diplomatic sensitivity and optional audits never read as one flat list

— One exact sentence for a clean run: "No findings under the enabled, documented local rules."

— Contested claims reported as diplomatic review rather than as verdicts, symmetrically for every party

The constraint I kept is report first. A finding identifies a review requirement; it does not establish the truth of a claim. The tool changes nothing on its own, and the automatic fixer is opt-in, previewed as a diff, and limited to deterministic corrections. Sign-off stays with the person responsible for the document.

Zero npm dependencies, MIT licence, runs offline on Node.js 18 or newer.

https://github.com/ahaomar/un-editorial-check
