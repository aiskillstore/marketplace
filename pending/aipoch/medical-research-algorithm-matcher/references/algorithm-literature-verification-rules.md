# Algorithm Literature Verification Rules

This module controls whether an algorithm can be formally recommended and how its literature support is structured.

## Search order
1. Search recent algorithm papers from the last 12 months first.
2. If directly relevant recent methods are sparse, expand to 1–3 years.
3. Add canonical baselines only when required for comparison or continuity.

## Two-layer evidence rule
Every formal algorithm recommendation must be supported by: 

### Layer 1 — Primary method paper (required)
This is the paper that introduced the algorithm or clearly established the named method identity.

Required fields:
- algorithm / method name
- paper title
- first author or consortium
- year
- venue
- article type: primary method
- direct stable link
- DOI when available

### Layer 2 — Published downstream use papers (add when found)
These are later papers that explicitly cite, apply, benchmark, or adapt the algorithm in published biomedical research.

Use them to judge: 
- whether the algorithm has actually been used in projects close to the user’s direction
- whether the method is still only identity-level plausible or already directionally supported
- whether the method appears in disease, modality, or task settings similar to the current project

Required fields for each downstream paper:
- paper title
- first author
- year
- venue
- article type: application / benchmark / adaptation
- direct stable link
- DOI when available
- short fit note

If no downstream published use paper is found, say so explicitly. Do not invent one.

## Acceptable verification sources
- DOI landing page
- PubMed
- PMC
- official publisher page
- arXiv / bioRxiv / medRxiv official page for preprints only

## Unverified-name rule
If a user supplies an algorithm name and no directly verified relevant primary method paper is identified, output:
**No directly verified primary algorithm paper identified yet for this method name in the current biomedical scope.**

Do not guess the expansion or silently replace it with another algorithm.

## Published-use honesty rule
Only count a downstream paper if the paper genuinely cites, applies, benchmarks, or adapts the algorithm.
Do not label a merely related paper as an algorithm-use paper.

## Forbidden
- fabricated DOI
- fabricated PMID / PMC ID
- fabricated author list
- fabricated benchmark claim
- fabricated “state-of-the-art” claim
- fabricated downstream use paper
