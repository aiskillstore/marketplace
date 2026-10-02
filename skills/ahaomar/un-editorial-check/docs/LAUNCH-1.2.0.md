# un-editorial-check 1.2.0

The leftover release. Three new opt-in capabilities, one new P0 detection, and four
honesty fixes where the tool could claim more than it had actually done.

```sh
npx -y un-editorial-check statement.md --report review.html
```

## What is new

**An HTML report.** `--report review.html` writes a self-contained page beside
the existing PDF: the same five lanes, the same six fields on every finding, the
same framing disclaimer, and byte-identical output for identical input so two
runs can be diffed. No external stylesheet, script or font.

**Your own house terminology.** `--glossary house.json` reports where a draft
disagrees with the words your organisation insists on — a term on your
`forbiddenTerms` list that appears in the copy, and a term on your
`requiredTerms` list that appears nowhere in a file. Those results are labelled
as yours throughout, never as a United Nations rule, and they never change the
exit code.

**A watch loop.** `--watch` re-checks whenever you save, until you stop it. It
is deliberately not a CI facility and resolves no exit code.

**Duplicated paragraphs are caught.** A long paragraph copied word for word
inside one file is now reported, with the line where the first copy was. A whole
paragraph is compared, not the pieces the markup cut it into, so a word in
italics or a link in one copy cannot hide the repeat.

## What was fixed

Four places where the tool could say "clean" more confidently than its own
evidence allowed:

- Naming a file inside the skill root was silently dropped, and the run still
  printed the clean sentence. It is now scanned.
- A file whose bytes are not decodable text is skipped, counted out of the
  scanned total and named in the header. A run that read nothing is a refusal
  with exit `2`, not a clean `0`.
- The PDF now discloses when it has replaced a character it cannot draw, instead
  of leaving a bare `?` on the page.
- The PDF now states the framing disclaimer that the claim table promises for
  "the report".

Four false-positive classes were removed from the hate-speech comparatives, and
JSX/TSX copy is now extracted by markup shape rather than by file extension.

## Unchanged, deliberately

The five lanes, the exact clean-run wording, the `--fix` allow-list, the
exit-code contract, heuristics as review severity by default, audits that never
move the exit code, and zero npm dependencies. No rule changed without a
sourced fixture, and every lock added in this release was shown to fail when
its guarantee is removed.

## Try it

```sh
# the five lanes, as a self-contained page
npx -y un-editorial-check statement.md --report review.html

# your own terminology
printf '{"glossaryVersion":1,"forbiddenTerms":["beneficiaries"]}' > house.json
npx -y un-editorial-check statement.md --glossary house.json

# re-check as you edit
npx -y un-editorial-check statement.md --watch
```

Full notes: [CHANGELOG.md](../CHANGELOG.md) ·
[docs/GLOSSARY-AND-WATCH.md](GLOSSARY-AND-WATCH.md) ·
[docs/demo/README.md](demo/README.md) ·
[README.md](../README.md)
