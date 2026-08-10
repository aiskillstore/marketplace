# Kickoff — research lab (SPARSE input)

Tests Phase 0 sparse-input *prediction* and the "lean root, don't over-scaffold" rule. There are no
input files; the builder gets only the prompt below, verbatim, as its domain input.

> I'm starting a small machine-learning research lab — just me plus two collaborators. I want a
> workspace to run the whole research lifecycle: tracking the open research questions we're chasing,
> the literature we've read, the experiments we're running, and writing results up into papers. Set it
> up as a self-managing system that stays organized and gets smarter as we go.

**What a strong build looks like here:** infers the *research* archetype (questions → lit-review →
experiment → analysis → writeup), predicts entities like `studies/` (or `experiments/`), seeds
starter `library/` instruments (an experiment log template, a paper outline, a lit-review note
template) and `knowledge/` stubs — all marked "draft — confirm" — **without** sprouting a row of empty
optional top-level folders. The whole plugin (6 organs + a domain skill or two) is authored and valid.
