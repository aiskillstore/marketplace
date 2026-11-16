# Guidance budget

Load this reference when developing or auditing prompt assembly, not during an ordinary edit. `scripts/budget.py` is a local, standard-library helper. It makes no model calls, network requests, file changes, or additional writing passes.

## What is counted

`measure_guidance(text, encoding="o200k_base", token_counter=None)` measures exactly the supplied text, including headings and separators. `characters` counts Python Unicode code points, not visual graphemes; `utf8_bytes` counts its UTF-8 encoding. No whitespace is stripped or Unicode normalized.

Without a tokenizer, `tokens` is `null`, `token_measurement` is `estimate`, and `estimated_tokens` is `ceil(utf8_bytes / 4)`. That heuristic is neither an exact count nor an upper bound. `encoding` labels the intended encoding; the default path does not load or run that tokenizer.

For development, an already installed exact local tokenizer can supply `token_counter(text) -> int`. For example, with an available `tiktoken` installation, pass `lambda text: len(encoder.encode(text, disallowed_special=()))`. Use the encoder matching the declared encoding. The helper does not install a package or download encoding data. A counter failure propagates rather than quietly switching to an estimate.

The report covers only the provided guidance string. Source text, samples, task data, message framing, tool schemas, and output are excluded unless explicitly passed to the helper. Measure those separately when evaluating a whole request. A guidance token count is not provider-reported input, cached, output, or reasoning usage and cannot establish API cost.

## Assembly contract

`assemble_guidance(required_parts, examples=(), ...)` joins required strings verbatim with two newlines. Pass the kernel, selected destination card, compact author card, and any explicit preferences or locks carried in guidance as required parts. Keep source text and sample data outside guidance; never shorten them to satisfy this budget.

Defaults are 4,000 characters for all guidance, at most two optional examples, and 900 characters for joined examples. The 1,000-token default is a target when only character measurements are available; it becomes an enforced limit when an exact tokenizer is supplied. A 4,000-character cap does not guarantee 1,000 tokens. Both character and exact-token checks include separators.

The helper first checks required material, then fits whole optional examples in priority order. An oversized example may be skipped so a later, smaller example fits. If exact token counting reveals overflow, it removes selected examples from the end. It never paraphrases, truncates, or removes a required part. Required overflow raises `GuidanceBudgetError` with its measurement; preserve the requirements and resolve the budget explicitly. Do not silently convert an explicit author preference into optional material.

The result contains `text`, `measurement`, `examples_used`, `examples_omitted`, and `limits`. `fit_examples(examples, remaining_chars=...)` can be used independently; its allowance includes separators between examples. Its caller must reserve the separator before the first example. Neither function changes the input sequences.

```python
from budget import assemble_guidance

assembled = assemble_guidance([kernel, destination_card, author_card], examples)
request = {"instructions": assembled["text"], "input": {"text": source}}
# Keep assembled["measurement"] as evaluation metadata, outside the prompt.
```

Measure a UTF-8 guidance file with `python3 scripts/budget.py guidance.txt`. Use `-` or omit the file to read stdin. Exit `0` means the character cap passed, `1` means overflow, and `2` means invalid input. The CLI always labels token estimates; it does not claim to enforce an exact token limit.

## Evaluation metadata

Save the measurement beside each benchmark variant, identifying which guidance text was counted. Record provider token usage and actual cost only when those values were supplied by the execution provider. Leave unobserved values `null` or explicitly unreported; do not substitute guidance estimates or zeroes. Any calculated price estimate needs declared rates, units, currency, and an estimate label. No extra model passes are required to collect this local metadata.
