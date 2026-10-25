# Local review tools

These original Python standard-library scripts offer read-only review prompts for Persian, English, and mixed text. They run offline with Python 3.9 or later. They do not rewrite input, create runtime bytecode, install packages, call a service, assign an authorship score, verify facts, or establish meaning equivalence. A clean report means only that these particular checks found nothing.

Run commands from the installed skill directory. Keep all three `.py` files together in `scripts/`.

```bash
python3 scripts/audit_text.py draft.txt
python3 scripts/audit_text.py draft.txt --lang auto --profile academic --json
python3 scripts/audit_text.py - --lang fa --json
python3 scripts/compare_revisions.py original.txt revised.txt --json
python3 scripts/compare_revisions.py original.txt revised.txt --invariants invariants.json --json --strict
```

The `-` input reads UTF-8 from stdin for `audit_text.py` only. Comparison and its invariants require file paths. UTF-8 BOM input is accepted; invalid UTF-8 is rejected rather than replaced. Unicode input remains unchanged, including Persian ZWNJ. Both programs use the same exit contract:

| Exit | Meaning |
|---|---|
| `0` | Run completed; without `--strict`, advisory findings can still be present. |
| `1` | With `--strict`, one or more advisory findings occurred. |
| `2` | Usage, file-reading, encoding, or invariants-schema error. |

`--json` writes one JSON object to stdout on completed runs, including strict exit `1`. Errors write a concise argparse diagnostic to stderr and leave stdout empty. The normal text report includes a scope reminder. Findings remain advisory under every exit code; `--strict` is a workflow signal, not a factual verdict.

## Audit one draft

`--lang` accepts `auto`, `fa`, `en`, or `mixed`. Automatic selection counts Persian/Arabic-script and Latin letters outside recognized protected spans. It is not a language classifier: Arabic passages may be routed as `fa`, and a Latin technical term can make Persian prose `mixed`. Choose an explicit language when the automatic route does not suit the text.

`--profile` accepts `general`, `academic`, `web`, or `copy`. It records the review context in the report. It does not change thresholds or penalize a genre through a word blacklist. Route genre decisions through the writing instructions and human review.

The audit reports:

- A small transparent set of English and Persian stock-framing prompts (`LEXICAL_REVIEW`). Review each phrase in context; a necessary qualification or deliberate voice can be kept.
- Arabic `ي/ك` in Persian-routed prose (`FA_ARABIC_LETTER`). Intentional Arabic, names, and source forms may be correct.
- A narrow set of space-separated `می/نمی` verb constructions (`FA_PREFIX_SPACING`). Correct ZWNJ forms are left alone; this is not morphological analysis or a complete spelling check.
- Exact sentence repetition and matching first three paragraph words (`REPEATED_SENTENCE`, `REPEATED_PARAGRAPH_START`). Parallel structure and deliberate repetition can be justified.
- Descriptive counts and sentence-length statistics. These are not naturalness, quality, predictability, or detector scores. Abbreviations, headings, lists, and unusual punctuation can distort segmentation.

Code fences, indented code, inline code, Markdown destinations, URLs, common literal quotation forms (`«…»`, `“…”`, `"…"`), and blockquote lines are excluded from prose checks. A quotation containing a URL or inline code remains protected as a whole. Link labels remain prose. The helper is a conservative text recognizer, not a complete Markdown parser; escaped quotes, nested constructs, multiline inline quotations, HTML, and unusual source formats may need manual review.

## Compare a revision

Comparison checks both inputs and uses counts, so deleting one of two identical protected spans or quantities is visible. It prompts review for:

- Removed, changed, and added exact code, destinations, URLs, quotations, and common numeric/author-year/footnote citation shapes (`PROTECTED_SPAN_REVIEW`, `PROTECTED_SPAN_ADDED_REVIEW`). A changed span can produce both a removal and an addition. The script cannot establish whether a citation is real, correctly attributed, or supports the claim.
- Removed and added normalized numeric claims, and same-magnitude changes to sign, percentage form, or a recognized unit (`NUMERIC_CLAIM_*_REVIEW`, `NUMERIC_ATTRIBUTE_REVIEW`).
- Changed, removed, and added endpoint/range patterns (`RANGE_REVIEW`, `RANGE_ADDED_REVIEW`).
- Fewer or more exact occurrences of a short list of negation, uncertainty, and qualification markers (`NEGATION_*_REVIEW`, `UNCERTAINTY_*_REVIEW`, `QUALIFICATION_*_REVIEW`).
- Violations of an optional explicit invariants contract.

Arabic-Indic, Persian, and Latin decimal digits normalize to the same magnitude; valid comma/Arabic-thousands groups and `.`/`٫` decimal marks are recognized. `۱٬۲۰۰٫۵۰ mg` matches `1,200.5 milligrams`, and `1.0` matches `۱`. A period ending a sentence does not hide the preceding number. Known adjacent units such as `5mg` are accepted. `$`, `€`, and `£` map to USD, EUR, and GBP conventions; these symbols do not establish the actual currency intended in an ambiguous source.

English `%`, `percent`, `percentage points`, Persian `٪`, `درصد`, and `واحد درصد` are distinguished where appropriate: `5 percent` changing to `5 percentage points` requires review. The finite unit table includes common mass, volume, distance, time, currency, and temperature names. Units are canonicalized by spelling only; the tool does not convert `1 g` to `1000 mg`, recognize every domain unit, parse scientific notation, infer ratios, or interpret local decimal conventions. Unknown attached identifiers and dotted software versions are skipped. Numbers inside recognized protected material use the exact-span check instead of numeric normalization.

Ranges recognize hyphens/dashes, `to`, `through`, `تا`, and `الی`, with a trailing unit or percent applying to both endpoints. ASCII `10 -20` is treated as the compact range `10–20`; use unambiguous punctuation when the source means separate signed values. Unicode minus `−` remains a sign. Explicit negative ranges such as `-5--2 mg` are supported. These recognizers cannot prove that the bounds refer to the same subject or that a range is mathematically appropriate.

Marker checks are case-insensitive lexical prompts. Equivalent paraphrases can trigger them, and words such as “about” or “May” can have a different grammatical role. Conversely, unlisted negations, hedges, implicit scope changes, and changed relations can be missed. The tool does not understand whether “activates” changing to “destroys” reverses a claim. Reordering matching numbers among subjects can also pass. Read the full original and revision, check sources, and preserve the intended uncertainty yourself.

## Set explicit invariants

Create a UTF-8 JSON file using only these optional keys:

```json
{
  "protected_strings": ["approval pending", "DOI:10.0000/example"],
  "required_terms": ["RNA", "سلول"]
}
```

`protected_strings` preserves exact case-sensitive occurrences: the revision must contain at least as many as the original, and at least one. An absent baseline string is also reported so a mistaken contract stays visible. This is appropriate for a quotation, citation, approved claim, product name, or any literal passage whose syntax the recognizer cannot protect reliably. It does not forbid additional occurrences.

`required_terms` requires each exact case-sensitive term to appear somewhere in the revision, including protected content. A term beginning or ending with a word character is bounded at that edge: `cat` is not satisfied by `concatenate`, and `سلول` is not satisfied by `سلولی`. ZWNJ is treated as part of a Persian word at a boundary. This does not check a term's definition, role, frequency, correct usage, or semantic substitution. If a passage must remain in its original context, review the passage directly.

Unknown or duplicate keys, non-object JSON, non-list values, duplicate entries, and non-string, empty, or whitespace-only entries fail with exit `2`. There is no silent typo fallback. Both arrays may be omitted or empty.

## Read findings and verify the installation

JSON includes `schema_version: 1`, the tool name, a `scope` reminder, language information, metrics, and a `findings` array. Every finding has a stable category code, `severity: "advisory"`, a message, a short original excerpt, and 1-based line/column coordinates. Columns count Unicode code points in the unchanged input, not bytes, display cells, or grapheme clusters. Tabs count as one code point. Comparison adds `source: "original"` or `"revised"`; use that file to interpret its coordinates. A missing-term finding points to the first position because no missing span has an actual location.

When tests are included in the installed package, run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The tests exercise the real CLI, valid and invalid UTF-8, all exit modes, JSON parsing, positive and negative controls, byte-for-byte input preservation, absence of runtime bytecode writes, protected material, Persian ZWNJ, quantities, ranges, markers, and explicit contracts. Python 3.9 grammar compatibility is checked; the recorded execution environment is specified in the integration results, not assumed to cover every supported interpreter or operating system.
