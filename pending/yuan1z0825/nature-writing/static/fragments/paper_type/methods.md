# Paper type: methods

A methods paper proposes a technique and must convince the reader it works, is reproducible, and is better than alternatives under a fair test.

## Argument chain

`task / problem -> limits of existing methods -> proposed method -> evaluation showing advantage -> reproducibility evidence -> boundary`

## Drafting order

1. Methods — the technical core, written first
2. Results — what comparisons and ablations show
3. Introduction — frames the task and gap retrospectively
4. Conclusion
5. Discussion
6. Abstract

## Results section discipline

In a methods paper, Results must answer:

- Is it more reliable?
- Is it faster / cheaper / smaller?
- Does it require fewer resources or data?
- Is the comparison fair and reproducible?

Bare "we obtain higher accuracy" without baseline + setup + statistical handling is insufficient.

## Methods section depth

Be explicit about:

- axioms, conditions, and assumptions
- hardware and software environment
- mathematical derivations
- evaluation protocol: datasets, baselines, metrics, splits, hyperparameters
- failure modes and out-of-scope conditions

When drafting a method, also open `references/method.md` for module-motivation and three-elements patterns.
