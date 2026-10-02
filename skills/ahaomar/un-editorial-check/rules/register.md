# Register

- **UE-RE001** *(warning)* — Avoid loaded or informal phrases including “boom”, “appetite”, “furthest behind”, “on the line” and “as donors retreat”. Use a neutral factual construction.
- **UE-RE004** *(warning, heuristic)* — Do not use rhetorical questions in UN editorial copy; state the finding. The rule matches sentence-initial question openers only, and a genuine information question can match the same openers — the finding is routed to review, never declared a defect.
- **UE-RE005** *(error)* — No exclamation marks in formal copy. Deterministic and report-only: `--fix` never rewrites it, because deleting the mark can leave a sentence that still needs rewriting.

## Agent review required

- **UE-RE002** *(warning)* — A superlative, ranking or ratio written into a JavaScript string needs a source or neutral wording. Derive it from the same data shown to the user and test the result; comparisons must use aligned reporting years. The fixed economic term *leading indicator* (and *leading indicators*) names an indicator rather than a ranking and is exempt.

Register findings are guards against tone drift, not a substitute for reading the claim in context. Report them separately from the deterministic rules.

## Aggressive and undiplomatic tone

- **UE-RE006** *(warning, heuristic)* — No insults, name-calling or contempt appellations such as “a clown”, “idiots” or “losers”. The rule matches appellation wording only — an article-led singular or a bare plural — and cannot judge the target or context: criticism of a policy may use the same wording, so every finding is routed to review. Quoted copy and block quotations are outside the copy span; a paraphrase in the writer's own voice still matches.
- **UE-RE007** *(warning, heuristic)* — No threat or intimidation posture: fixed phrases such as “will regret”, “should be afraid” or “no choice but to crush”. The phrases cannot be separated from idiom — “the squad will regret the missed penalty” matches as well — while “crush expectations” and “crush records” are deliberately excluded by pattern. Every finding is routed to review; the rule never proves a threat.
- **UE-RE008** *(warning, deterministic)* — No all-caps word of five letters or more in running prose. Digits, adjacent punctuation and a file-name extension disqualify the token, and a finite exemption list covers short initialisms plus the longer ones and reference words (UN, NATO, WHO, ASEAN, UNHCR, ECOSOC, SARIF, README, USAGE); an initialism or heading word missing from that list is reported.
