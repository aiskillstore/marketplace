# Source-by-source analysis

## How to read this ledger

All 112 input records have an explicit disposition. Analysis below is original editorial synthesis, not wholesale reproduction of source instructions. The machine-readable source-reviews.json retains detailed locators, scope and access notes. A rejected or contextual finding is accounted for but is not promoted into a binding rule. Source counts are records, not independent studies.

## D01: DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature

Source: https://arxiv.org/abs/2301.11305

Read scope: Selected full-text methods, evaluation design/results, and discussion/limitations; full paper, proofs, and appendix tables not claimed.

Role: primary method research

- **adapt** · skill-build-work/modules/detection/.research/D01.txt:L43-68 (local extraction; sha256:9240f3c6f0221234f5bd83e22d038672e69f75b6cb7ff103a97046349f81b287) · The criterion compares original log probability with nearby perturbations and applies a threshold. It is a model-conditioned statistic, not an absolute human-writing property. · Rules: DP01, DP02, DE02
- **adapt** · skill-build-work/modules/detection/.research/D01.txt:L241-250 (local extraction; sha256:9240f3c6f0221234f5bd83e22d038672e69f75b6cb7ff103a97046349f81b287) · Evaluation balances classes and spans specified datasets; AUROC measures ranking. Original success does not certify a new language or deployment. · Rules: DE04, DE06, DE09
- **adapt** · skill-build-work/modules/detection/.research/D01.txt:L347-349 (local extraction; sha256:9240f3c6f0221234f5bd83e22d038672e69f75b6cb7ff103a97046349f81b287) · Scoring access and meaningful perturbations are required, with compute and domain limits. Do not install or run it as a prerequisite for editing. · Rules: DP02, DE02

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: 2023-era generators and selected domains; no direct Persian validation established in reviewed ranges.

Access: Saved original source; no detector or research code was executed.

## D02: Fast-DetectGPT

Source: https://arxiv.org/html/2310.05130v3

Read scope: Selected full-text introduction, task/method setup, experimental design, usability results, and limitations; formulas and appendices not fully reviewed.

Role: primary method research

- **adapt** · skill-build-work/modules/detection/.research/D02.txt:L54-61 (local extraction; sha256:4816fadc6d19a744b27052771eee24d03d9e70f6a045a261cafa145ec26715d8) · Conditional sampling/scoring reduces perturbation cost; white-box and surrogate-model access are different settings. Zero-shot still requires pretrained models. · Rules: DP02, DE02
- **adapt** · skill-build-work/modules/detection/.research/D02.txt:L356-378 (local extraction; sha256:4816fadc6d19a744b27052771eee24d03d9e70f6a045a261cafa145ec26715d8) · Low-FPR recall, length, domain, and language affect usefulness; the authors acknowledge no single pretrained model covers every language and domain. · Rules: DP03, DE06, DE09

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Reported improvements are relative to tested baselines and settings, not a current universal accuracy estimate.

Access: Saved original source; no detector or research code was executed.

## D03: Fast-DetectGPT official code

Source: https://github.com/baoguangsheng/fast-detect-gpt

Read scope: Complete extracted README body, plus selected local inference implementation; other code files and experiments not reviewed or run.

Role: primary implementation documentation

- **adapt** · skill-build-work/modules/detection/.research/D03.txt:L61-90 (local extraction; sha256:ae998899b126759d102108b222586c7dd837cce49df6bb56e8616d8a8632e35d) · The README announces a changed model pair, while its demo description still names an older default. Method name, demo, and implementation version must be distinguished. · Rules: DP11, DE02
- **adapt** · skill-build-work/modules/detection/.research/D03-infer.txt:L18-52 (local extraction; sha256:4cbe06cdb456df729ce9eede14505757775bc388f4c17d762a6b28f57b169cb0) · Displayed probability uses fitted normal distributions and a balanced-class assumption. It is not an externally calibrated authorship probability for arbitrary populations. · Rules: DE07, DE09
- **adopt** · skill-build-work/modules/detection/.research/D03-infer.txt:L55-67 (local extraction; sha256:4cbe06cdb456df729ce9eede14505757775bc388f4c17d762a6b28f57b169cb0) · Inference truncates tokenized input and checks tokenizer agreement. Record tested text extent and the model/tokenizer pair. · Rules: DE02

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Maintainer claims are not independent reproduction; repository snapshot was inspected, not executed.

Access: Saved original source; no detector or research code was executed.

## D04: Spotting LLMs With Binoculars

Source: https://arxiv.org/html/2401.12070v3

Read scope: Selected main-body mechanism, datasets/metrics, multilingual reliability, prompting experiments, and limitations; full appendix not reviewed.

Role: primary method research

- **adapt** · skill-build-work/modules/detection/.research/D04.txt:L121-152 (local extraction; sha256:2284ba0c74e3febf6cc34e53d4dc6d923a27e1c7933d7f2f7841589f2407065d) · The score contrasts model perplexity and cross-perplexity; the paper prioritizes recall at low FPR because AUROC can conceal operating-point failures. · Rules: DP02, DE08, DE09
- **adapt** · skill-build-work/modules/detection/.research/D04.txt:L179-190 (local extraction; sha256:2284ba0c74e3febf6cc34e53d4dc6d923a27e1c7933d7f2f7841589f2407065d) · Low-resource-language recall can be poor despite low false positives; a favorable ESL check does not establish coverage of other populations. · Rules: DP06, DE05
- **adapt** · skill-build-work/modules/detection/.research/D04.txt:L223-234 (local extraction; sha256:2284ba0c74e3febf6cc34e53d4dc6d923a27e1c7933d7f2f7841589f2407065d) · Random strings may score human, while explicit bypass efforts and code are outside the main study. A human-like score is not a writing-quality objective. · Rules: DP06, DP08, DE06

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Specific Falcon pair, datasets, and tested versions; no general Persian guarantee.

Access: Saved original source; no detector or research code was executed.

## D05: A Practical Examination of AI-Generated Text Detectors for Large Language Models

Source: https://aclanthology.org/2025.findings-naacl.271/

Read scope: Substantial selected main-body sections: background, task/data/model design, metrics, generation pipeline, results, and discussion. Full PDF and appendices not claimed.

Role: independent primary benchmark research

- **adopt** · skill-build-work/modules/detection/.research/D05.txt:L236-252 (local extraction; sha256:9eed6b32b11b6c0859b5bedf025f9caec106b9c94c3c5ba77f88073aa7db23da) · The study gives an example of strong AUROC with poor recall at 1% FPR. Report the intended operating point rather than substituting a ranking metric. · Rules: DE08, DE09
- **adapt** · skill-build-work/modules/detection/.research/D05.txt:L346-378 (local extraction; sha256:9eed6b32b11b6c0859b5bedf025f9caec106b9c94c3c5ba77f88073aa7db23da) · Task/language shifts and rewriting change detection; different detectors return probabilities or raw criteria. Do not merge score units or generalize English results. · Rules: DP03, DP08, DE05, DE07
- **adapt** · skill-build-work/modules/detection/.research/D05.txt:L453-480 (local extraction; sha256:9eed6b32b11b6c0859b5bedf025f9caec106b9c94c3c5ba77f88073aa7db23da) · Rewriting shifts scores, while the quality analysis is limited. A detector change cannot substitute for fidelity and reader-quality assessment. · Rules: DE11, DE12

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Specified models and four multilingual subsets; neither all services nor Persian were validated.

Access: Saved original source; no detector or research code was executed.

## D06: RAID: A Shared Benchmark for Robust Evaluation of Machine-Generated Text Detectors

Source: https://arxiv.org/html/2405.07940v2

Read scope: Selected main narrative: corpus creation, decoding, statistics/release design, detectors, thresholds, principal findings, limitations, and per-domain calibration discussion; numerical tables/appendices only partially inspected.

Role: independent primary benchmark research

- **adapt** · skill-build-work/modules/detection/.research/D06.txt:L223-249 (local extraction; sha256:39fca5c060eaaf2917381fb39f21dc22bc0e375a1e58d8d8bd80a1d709f0ec3f) · RAID separates benchmark-trained systems and includes a hidden test. Detector comparisons depend on declared calibration and benchmark exposure. · Rules: DE04, DE06, DE08
- **adapt** · skill-build-work/modules/detection/.research/D06.txt:L514-520 (local extraction; sha256:39fca5c060eaaf2917381fb39f21dc22bc0e375a1e58d8d8bd80a1d709f0ec3f) · Decoding and repetition settings materially affect performance. Treat them as robustness factors, not prescriptions for changing a draft to evade tools. · Rules: DP08, DE06, DE12
- **adapt** · skill-build-work/modules/detection/.research/D06.txt:L590-593 (local extraction; sha256:39fca5c060eaaf2917381fb39f21dc22bc0e375a1e58d8d8bd80a1d709f0ec3f) · Limited multilingual domains, evolving generators, and benchmark overfitting limit generalization; preserve dates and out-of-domain tests. · Rules: DE05, DE10, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Historical tested versions; multilingual extras are narrow and do not establish Persian performance.

Access: Saved original source; no detector or research code was executed.

## D07: GPT detectors are biased against non-native English writers

Source: https://arxiv.org/html/2304.02819v3

Read scope: Complete main article narrative L21-L48, plus selected materials/methods; bibliography and full supplementary figures not reviewed.

Role: primary fairness study

- **adapt** · skill-build-work/modules/detection/.research/D07.txt:L30-37 (local extraction; sha256:2280104c79a620e601d1da352fe1fc2180688a6b328e9664e471213fb69922f5) · Seven tested tools misclassified many sampled TOEFL essays. Audit non-native writing separately; do not infer origin from constrained vocabulary. · Rules: DP06, DP09, DE05
- **adapt** · skill-build-work/modules/detection/.research/D07.txt:L47-48 (local extraction; sha256:2280104c79a620e601d1da352fe1fc2180688a6b328e9664e471213fb69922f5) · The authors identify small samples and older detector backbones as limits. Their intervention results do not justify a universal lexical trick or current error rate. · Rules: DP06, DE06
- **adopt** · skill-build-work/modules/detection/.research/D07.txt:L323-339 (local extraction; sha256:2280104c79a620e601d1da352fe1fc2180688a6b328e9664e471213fb69922f5) · The tools were accessed in March 2023. Preserve that historical scope rather than attributing results to current products. · Rules: DE02, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: English samples and 2023 services; not a Persian or current-product benchmark.

Access: Saved original source; no detector or research code was executed.

## D08: Different Time, Different Language: Revisiting the Bias Against Non-Native Speakers in GPT Detectors

Source: https://arxiv.org/html/2602.05769v1

Read scope: Selected full-text questions, dataset construction, results/discussion, correlation analysis, and limitations; intermediate tables and all appendices not fully reviewed.

Role: primary preprint fairness study

- **adapt** · skill-build-work/modules/detection/.research/D08.txt:L163-169 (local extraction; sha256:880b60c819c1282afda8eb91fcc223ea10c448383b13ad6f14c8da917bff6f90) · Native/non-native controls are matched with explicit proficiency and length constraints; the advanced non-native sample is small. Fairness conclusions require population-specific controls. · Rules: DE04, DE05, DE10
- **adapt** · skill-build-work/modules/detection/.research/D08.txt:L565-585 (local extraction; sha256:880b60c819c1282afda8eb91fcc223ea10c448383b13ad6f14c8da917bff6f90) · This Czech follow-up finds different bias and weak entropy-output correlation. Reject a timeless rule linking non-native writing, low perplexity, and flags. · Rules: DP06, DE05, DE06
- **adapt** · skill-build-work/modules/detection/.research/D08.txt:L491-491 (local extraction; sha256:880b60c819c1282afda8eb91fcc223ea10c448383b13ad6f14c8da917bff6f90) · A nonbreaking-space artifact affected one result. Inspect source/encoding shortcuts; do not adopt character manipulation as writing guidance. · Rules: DP07, DE04

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Preprint; limited generators and small proficient-writer subset; black-box commercial analysis.

Access: Saved original source; no detector or research code was executed.

## D09: AI detectors rarely flag human writing, but sometimes miss AI text imitating real authors

Source: https://epoch.ai/data-insights/ai-detectors-false-negatives

Read scope: Complete extracted article, methods, results tables, assumptions, and limitations; linked raw corpus/code not independently audited.

Role: independent primary benchmark article

- **adopt** · skill-build-work/modules/detection/.research/D09.txt:L17-23 (local extraction; sha256:05365d46b41db25489976d1987e2ea5a07b7e7ceae4d6c2bb5bef3fb04c25d9e) · The benchmark fixes default verdicts, versions, roughly 500-word passages, and author-derived controls. These design choices define the claim. · Rules: DE01, DE02, DE04
- **adopt** · skill-build-work/modules/detection/.research/D09.txt:L47-50 (local extraction; sha256:05365d46b41db25489976d1987e2ea5a07b7e7ceae4d6c2bb5bef3fb04c25d9e) · Mixed-label mapping changes reported misses, human excerpts cluster by author, and tested versions are pinned to June 2026. Report mappings, dependence, and dates. · Rules: DE07, DE10, DE14
- **adapt** · skill-build-work/modules/detection/.research/D09.txt:L5-14 (local extraction; sha256:05365d46b41db25489976d1987e2ea5a07b7e7ceae4d6c2bb5bef3fb04c25d9e) · Zero observed false positives for two systems and nonzero errors for another are sample results, not proof that all tools fail or never err. · Rules: DP03, DE06

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Only three services, three genres, one imitation condition, and the stated sample; no Persian evaluation.

Access: Saved original source; no detector or research code was executed.

## D10: Why AI Detection Fails for Academic Integrity

Source: https://arxiv.org/html/2608.11256v3

Read scope: Selected methods, proxy-label definitions, key results and correlates, discussion, and limitations. Full tables/appendices not reviewed.

Role: primary empirical preprint/research report

- **adopt** · skill-build-work/modules/detection/.research/D10.txt:L47-68 (local extraction; sha256:65074e41b00f660cc599a4c8abf61e5d33d959058f0a688fad14b24422c655ce) · Recent originals have unknown AI-use history; refine prompts are generative rewriting rather than verified grammar-only edits. Separate flag rates, proxy FPR, and policy labels. · Rules: DP04, DP09, DE01
- **adopt** · skill-build-work/modules/detection/.research/D10.txt:L291-297 (local extraction; sha256:65074e41b00f660cc599a4c8abf61e5d33d959058f0a688fad14b24422c655ce) · The study did not verify semantic preservation or actual sanctions and used English abstracts. Detector-score decreases cannot establish better writing or quantify human contribution. · Rules: DP08, DE11, DE14
- **adapt** · skill-build-work/modules/detection/.research/D10.txt:L224-243 (local extraction; sha256:65074e41b00f660cc599a4c8abf61e5d33d959058f0a688fad14b24422c655ce) · Feature-score correlations pool originals and rewrites and are not causal. Do not turn long-word or vocabulary associations into mandatory substitutions. · Rules: DP06, DE06

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: 642 abstracts, one rewrite generator, two commercial detectors and one humanizer setup; proxy labels and correlational features.

Access: Saved original source; no detector or research code was executed.

## D11: Base Models Look Human To AI Detectors

Source: https://arxiv.org/abs/2605.19516

Read scope: Selected introduction, method/algorithm, evaluation design, principal results, and limitations; related work, qualitative examples, and appendices partly reviewed only.

Role: primary diagnostic preprint; evasion method not adopted

- **context_only** · skill-build-work/modules/detection/.research/D11.txt:L106-130 (local extraction; sha256:fdf39bff2193c2a2859ee7a55b2bced843c99e2a1a32d8885c6e5bc1ab5938df) · The base/instruct comparison uses selected RAID/MAGE categories and specific continuation controls. It diagnoses a tested failure mode, not every machine-text distribution. · Rules: DP03, DE06
- **reject** · skill-build-work/modules/detection/.research/D11.txt:L155-175 (local extraction; sha256:fdf39bff2193c2a2859ee7a55b2bced843c99e2a1a32d8885c6e5bc1ab5938df) · Repeated paraphrasing raises detector human scores while semantic fidelity declines, and services can adapt. Reject iteration-for-evasion as the skill objective. · Rules: DP08, DE11, DE12

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Preprint; selected model families and commercial systems; semantic scoring is automated, not a full factual audit.

Access: Saved original source; no detector or research code was executed.

## D12: Detecting the Machine: A Comprehensive Benchmark of AI-Generated Text Detectors Across Architectures, Domains, and Adversarial Conditions

Source: https://arxiv.org/abs/2603.17522

Read scope: Selected substantive dataset/preprocessing and discussion/conclusion/limitations; lengthy detector implementations, stage-by-stage tables, and appendices not fully reviewed.

Role: primary benchmark preprint; bounded contextual use

- **adapt** · skill-build-work/modules/detection/.research/D12.txt:L215-247 (local extraction; sha256:ffb386f78cc621f235b241b6c8f27b1cf689ed4327f55a19702e1dca8930e798) · Length matching addresses a shortcut, but the two English Q&A datasets use different generators. Domain and generator shifts must be distinguished. · Rules: DE04, DE05
- **context_only** · skill-build-work/modules/detection/.research/D12.txt:L2380-2409 (local extraction; sha256:ffb386f78cc621f235b241b6c8f27b1cf689ed4327f55a19702e1dca8930e798) · The paper reports cross-domain degradation and generator-detector identity effects, with only two sources and small prompted-detector subsets. Keep the conclusion within those limits. · Rules: DP01, DE06, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Preprint with narrow English Q&A coverage; broad architecture claims are not independently reproduced or generalized to Persian.

Access: Saved original source; no detector or research code was executed.

## D13: Crafting Tomorrow’s Headlines: Neural News Generation and Detection in English, Turkish, Hungarian, and Persian

Source: https://arxiv.org/html/2408.10724v3

Read scope: Selected full-text rationale, corpus/model design, results, and limitations; appendix model listings inspected, full tables and example corpus not audited.

Role: primary multilingual workshop benchmark

- **adapt** · skill-build-work/modules/detection/.research/D13.txt:L74-89 (local extraction; sha256:c3277c30238c73e49a56ef0ee0df31162c022f01d3f5408d11721597cc6536fe) · The benchmark directly includes Persian news with specified source and generation setup. It is relevant evidence for that genre, not all Persian writing. · Rules: DE04, DE05
- **adapt** · skill-build-work/modules/detection/.research/D13.txt:L973-988 (local extraction; sha256:c3277c30238c73e49a56ef0ee0df31162c022f01d3f5408d11721597cc6536fe) · Out-of-domain behavior varies; truthfulness and cross-language transfer were not evaluated. Detection performance cannot establish factual quality or general Persian support. · Rules: DP07, DE05, DE11

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Older generators and news domain; full generated-record quality/encoding not independently inspected.

Access: Saved original source; no detector or research code was executed.

## D14: Persian AI-Text Corpus

Source: https://github.com/asrinvakili/persian-ai-text-corpus

Read scope: Selected repository README, full motivation/composition/collection portion of datasheet, and licensing/maintenance sections; no complete record-level data audit.

Role: community dataset author documentation

- **adopt** · skill-build-work/modules/detection/.research/D14-datasheet.txt:L31-41 (local extraction; sha256:4e3f0509826cf1be0ecbb864b3b045c2f37a38044cffd7a0d7cb4da5e76d10d7) · Topic-linked versions remain in one split to prevent leakage. Group related human/generated variants before calibration and final testing. · Rules: DE04
- **adapt** · skill-build-work/modules/detection/.research/D14.txt:L181-190 (local extraction; sha256:4d470d6dc13cf85cf4a418205603886626a251d04cf01f653c4a2278de08401c) · The corpus is encyclopedic, uses three June 2026 generators, and has different human/AI licensing. It is a limited resource, not a general Persian certification set. · Rules: DP07, DE05
- **adapt** · skill-build-work/modules/detection/.research/D14-datasheet.txt:L47-67 (local extraction; sha256:4e3f0509826cf1be0ecbb864b3b045c2f37a38044cffd7a0d7cb4da5e76d10d7) · Pre-2020 revisions and topic anchors are author-reported provenance procedures. Verify records before treating those procedures as established dataset quality. · Rules: DE04, DE06

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Author documentation only; data/model identities and licensing compatibility require verification for intended reuse.

Access: Saved original source; no detector or research code was executed.

## D15: Persian AI-Generated Text Dataset

Source: https://huggingface.co/datasets/ehsantorabi/persian-ai-generated-text

Read scope: Complete public dataset card; gated data files were not accessed or accepted.

Role: community dataset card; no empirical performance evidence

- **context_only** · skill-build-work/modules/detection/.research/D15.txt:L1-25 (local extraction; sha256:b7237e290760b7e82ebd808d6006b89519e79eb531061be867c43c3c0569ebb0) · The public card reports its count and model diversity but conditions file access. Treat these as card assertions rather than audited data. · Rules: DE06, DE14
- **adapt** · skill-build-work/modules/detection/.research/D15.txt:L108-116 (local extraction; sha256:b7237e290760b7e82ebd808d6006b89519e79eb531061be867c43c3c0569ebb0) · The corpus is AI-only and may contain non-Persian artifacts. It cannot estimate FPR without matched human controls, and artifacts can create shortcuts. · Rules: DP07, DE04, DE05
- **adapt** · skill-build-work/modules/detection/.research/D15.txt:L84-110 (local extraction; sha256:b7237e290760b7e82ebd808d6006b89519e79eb531061be867c43c3c0569ebb0) · The card says 70 models in its model section but 58 in a use-case sentence. Verify the actual inventory before quoting exact diversity. · Rules: DE06, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: No records downloaded; counts, licensing, model identities, and quality are unverified author assertions.

Access: Saved original source; no detector or research code was executed.

## D16: MULTITuDE: Large-Scale Multilingual Machine-Generated Text Detection Benchmark

Source: https://arxiv.org/abs/2310.13606

Read scope: Selected abstract, language/generator inventory, split construction, discussion, and limitations; full evaluation tables/appendices not read.

Role: primary multilingual benchmark

- **reject** · skill-build-work/modules/detection/.research/D16.txt:L18-44 (local extraction; sha256:495c5422cef82d667449af379e9f29925f758035d6c38ad6ee737d6d6b8e8814) · The eleven named languages exclude Persian. Multilingual in the title is not evidence for Persian accuracy. · Rules: DE05
- **adopt** · skill-build-work/modules/detection/.research/D16.txt:L200-202 (local extraction; sha256:495c5422cef82d667449af379e9f29925f758035d6c38ad6ee737d6d6b8e8814) · Human/machine versions sharing a headline are kept together across splits. Preserve grouped splits when evaluating generalization. · Rules: DE04
- **adapt** · skill-build-work/modules/detection/.research/D16.txt:L793-807 (local extraction; sha256:495c5422cef82d667449af379e9f29925f758035d6c38ad6ee737d6d6b8e8814) · Script/language similarity affects transfer and English is not a universal default. Limits include language selection, corpus size, and generator coverage. · Rules: DP07, DE05, DE06

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: News data and selected languages/models from the paper; no direct Persian validation.

Access: Saved original source; no detector or research code was executed.

## D17: AbjadGenEval shared-task announcement

Source: https://ezzini.github.io/AbjadGenEval/

Read scope: Complete extracted official task page, including tentative timeline and later announcement; no linked competition files audited.

Role: official task announcement; contextual only

- **context_only** · skill-build-work/modules/detection/.research/D17.txt:L5-30 (local extraction; sha256:5137fd03d60c5927a5f6bee39b2ec9784fba5fcff90b5ef4cea793089fa5a477) · The page announces Arabic, Urdu, and Persian tracks. This is a planned scope, not evidence that Persian results were completed. · Rules: DE05, DE14
- **adapt** · skill-build-work/modules/detection/.research/D17.txt:L33-43 (local extraction; sha256:5137fd03d60c5927a5f6bee39b2ec9784fba5fcff90b5ef4cea793089fa5a477) · The announced evaluation emphasizes macro-F1/accuracy and labels its schedule tentative. Read the final report before treating plans as outcomes. · Rules: DE06, DE14

Integration: references/detector-evaluation.md

Limits: Announcement differs from the reviewed final two-language report D18; no Persian performance inferred.

Access: Saved original source; no detector or research code was executed.

## D18: AbjadGenEval final shared-task overview

Source: https://aclanthology.org/2026.abjadnlp-1.68.pdf

Read scope: Selected full-text abstract/introduction, actual task/data/evaluation description, leaderboard excerpt, and limitations; detailed system table and full paper not claimed.

Role: primary final shared-task overview

- **reject** · skill-build-work/modules/detection/.research/D18.txt:L194-225 (local extraction; sha256:6a549b4dbe67d1d693db5cfa706cef42c6f51d3a1017d783269076502e895ef5) · The completed tasks and evaluation cover Arabic and Urdu news with held-out predictions and macro-F1. They do not report a Persian test. · Rules: DE05, DE14
- **adapt** · skill-build-work/modules/detection/.research/D18.txt:L367-385 (local extraction; sha256:6a549b4dbe67d1d693db5cfa706cef42c6f51d3a1017d783269076502e895ef5) · News structure, fixed generator coverage, and blind-test generalization gaps constrain deployment claims; suitable operating thresholds remain relevant. · Rules: DE06, DE08

Integration: references/detector-evaluation.md

Limits: Final workshop overview is news-specific; do not transfer its Arabic/Urdu results to Persian.

Access: Saved original source; no detector or research code was executed.

## D19: Turnitin: File requirements for an AI Writing Report

Source: https://guides.turnitin.com/hc/en-us/articles/28234943089933-File-requirements-for-an-AI-Writing-Report

Read scope: Complete meaningful official documentation body; unrelated navigation excluded.

Role: official vendor input/support documentation

- **adopt** · skill-build-work/modules/detection/.research/D19.txt:L6-12 (local extraction; sha256:bd90ae14c438fe00847ddf9c24ff2071def9208e07842f229afb65ade3422e50) · The report requires long-form prose within stated size/length/file constraints. An unsupported input cannot yield an interpretable comparison. · Rules: DE02, DE03
- **adapt** · skill-build-work/modules/detection/.research/D19.txt:L11-13 (local extraction; sha256:bd90ae14c438fe00847ddf9c24ff2071def9208e07842f229afb65ade3422e50) · The listed languages exclude Persian, and consistent file format is recommended. Treat this as dated product support, not an empirical Persian failure rate. · Rules: DP11, DE05

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Live vendor documentation snapshot, not an independent accuracy study.

Access: Saved original source; no detector or research code was executed.

## D20: Turnitin: Using the AI Writing Report

Source: https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report

Read scope: Complete meaningful documentation body; navigation excluded.

Role: official vendor score/limitations documentation

- **adopt** · skill-build-work/modules/detection/.research/D20.txt:L13-22 (local extraction; sha256:8991bbcad9a17ce8bc99871967de9d4bb94cf01adfaffc262fb7ffc46a021f84) · The vendor distinguishes AI qualifying-text percentage from similarity and warns against sole reliance for adverse action; features vary by language. · Rules: DP01, DP09, DE01, DE03
- **adopt** · skill-build-work/modules/detection/.research/D20.txt:L25-35 (local extraction; sha256:8991bbcad9a17ce8bc99871967de9d4bb94cf01adfaffc262fb7ffc46a021f84) · Low scores can be suppressed with an asterisk because of false positives. Do not reinterpret an unavailable percentage as zero or certainty. · Rules: DE07
- **adopt** · skill-build-work/modules/detection/.research/D20.txt:L44-53 (local extraction; sha256:8991bbcad9a17ce8bc99871967de9d4bb94cf01adfaffc262fb7ffc46a021f84) · Qualifying prose excludes several short/non-prose forms from reliable detection. Interpret highlights and denominators using documented eligibility. · Rules: DE02, DE07

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Current vendor definitions; the article does not independently establish accuracy for every supported language.

Access: Saved original source; no detector or research code was executed.

## D21: Introducing GPTZero 4o

Source: https://gptzero.me/news/introducing-gptzero-4o

Read scope: Complete extracted release article and tables; linked raw benchmarks not audited.

Role: vendor release and self-evaluation

- **adapt** · skill-build-work/modules/detection/.research/D21.txt:L75-91 (local extraction; sha256:fb83bebef89491698f7459cedef762fe616c19bc22b75182bd08961492a58eef) · The vendor reports demographic testing and says punctuation edits do not determine its result. Reject universal dash/semicolon removal as a detection strategy. · Rules: DP05, DP06, DE06
- **adapt** · skill-build-work/modules/detection/.research/D21.txt:L94-117 (local extraction; sha256:fb83bebef89491698f7459cedef762fe616c19bc22b75182bd08961492a58eef) · New-version and default-access claims are vendor statements; internal release timing differs from the page publication cue. Pin actual run versions rather than infer them from a headline. · Rules: DP11, DE02, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Vendor self-evaluation/retests; independent validation of the new version was not performed here.

Access: Saved original source; no detector or research code was executed.

## D22: GPTZero multilingual detection

Source: https://gptzero.me/news/what-is-the-best-ai-detector-for-multilingual-detection

Read scope: Complete meaningful multilingual article, language table, and benchmark method; related-post navigation excluded.

Role: vendor multilingual self-evaluation

- **adapt** · skill-build-work/modules/detection/.research/D22.txt:L7-75 (local extraction; sha256:cd9c911d84416a43219f4d226b7efe4d37947e9023216a3b7cd253103f33e2b1) · Language-aware pipelines and per-language results are described, but Persian is absent from the reviewed table. Do not infer Persian validation from multilingual branding. · Rules: DE05
- **context_only** · skill-build-work/modules/detection/.research/D22.txt:L76-100 (local extraction; sha256:cd9c911d84416a43219f4d226b7efe4d37947e9023216a3b7cd253103f33e2b1) · Competitor results use a cost-limited subsample of an internal benchmark. Public figures remain vendor evaluation with a specific sampling design. · Rules: DE06, DE10

Integration: references/detector-evaluation.md

Limits: Internal benchmark and stated snapshot; no independent Persian evidence.

Access: Saved original source; no detector or research code was executed.

## D23: Introducing Originality.ai 5.0 and 5.0 Max

Source: https://originality.ai/blog/introducing-originality-5-0-and-max

Read scope: Selected release body, benchmark methodology/table excerpt, feature descriptions, and score semantics; full article tables not reviewed.

Role: vendor release and self-evaluation

- **adapt** · skill-build-work/modules/detection/.research/D23.txt:L32-72 (local extraction; sha256:ac78e2bc93c43646329f9c5a214dfa1cac186704981bc431dfefbd09624cdecb) · Models are retired/replaced and benchmark rows use differing samples and scoring rules. Public datasets do not make a vendor retest independent or a matched comparison. · Rules: DP11, DE06
- **adopt** · skill-build-work/modules/detection/.research/D23.txt:L224-245 (local extraction; sha256:ac78e2bc93c43646329f9c5a214dfa1cac186704981bc431dfefbd09624cdecb) · The vendor changes score semantics from older confidence scores to estimated involvement classes/fractions and still warns results are review signals. Preserve version-specific meaning. · Rules: DE01, DE07

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Vendor claims about new models and estimated fractions are not independently verified authorship measures.

Access: Saved original source; no detector or research code was executed.

## D24: Originality.ai: Multiple Languages

Source: https://help.originality.ai/en/article/multiple-languages-how-to-use-multi-language-ai-detection-13e5plo/

Read scope: Complete official support page and date; feedback/navigation excluded.

Role: official vendor language-support statement

- **context_only** · skill-build-work/modules/detection/.research/D24.txt:L14-35 (local extraction; sha256:5ebf8c6f78ad94e90e368ee60677ae7d7b41ffdea14057d269ba7c4b8d9f1c79) · Persian is explicitly named in the language list. This supports a dated support claim, not an independent accuracy claim. · Rules: DP11, DE03, DE05
- **adopt** · skill-build-work/modules/detection/.research/D24.txt:L49-50 (local extraction; sha256:5ebf8c6f78ad94e90e368ee60677ae7d7b41ffdea14057d269ba7c4b8d9f1c79) · Instructions and an October 20 update date tie the list to a live product workflow. Recheck it for current operational advice. · Rules: DP11, DE02

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Language support documentation supplies no Persian sample size or external validation.

Access: Saved original source; no detector or research code was executed.

## D25: Scalable watermarking for identifying large language model outputs

Source: https://www.nature.com/articles/s41586-024-08025-4

Read scope: Selected full-text background, main evaluation/discussion, limitations, and beginning of formal method. Remaining methods, supplements, and detailed figures not fully reviewed.

Role: primary peer-reviewed watermark research

- **adapt** · skill-build-work/modules/detection/.research/D25.txt:L31-35 (local extraction; sha256:8d4f522358ced29595b8a37b8f368a1ed8d9bc52cde11f5ae4e7569801ceeb43) · Post-hoc classification, retrieval, and generation-time watermarking are distinct and potentially complementary. Do not collapse their provenance claims. · Rules: DP01, DP10
- **adapt** · skill-build-work/modules/detection/.research/D25.txt:L90-105 (local extraction; sha256:8d4f522358ced29595b8a37b8f368a1ed8d9bc52cde11f5ae4e7569801ceeb43) · Generative watermarking uses a sampling/scoring configuration and requires generator participation; unmarked actors and edits limit coverage. A negative result is not human proof. · Rules: DP10, DE13

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Selected paper sections only; production results and technical guarantees belong to the studied configurations.

Access: Saved original source; no detector or research code was executed.

## D26: SynthID Text official reference implementation

Source: https://github.com/google-deepmind/synthid-text

Read scope: Selected complete README mechanism/caveat sections plus selected actual frequentist detector code; remaining implementation and tests not fully reviewed or run.

Role: primary reference implementation and documentation

- **adopt** · skill-build-work/modules/detection/.research/D26.txt:L43-85 (local extraction; sha256:d4114b36d31d4597c18cba433a4073e75ba3395a5a324dfec72833dfa0296e66) · The repository is a research reference, distinguishes trained Bayesian and frequentist detectors, and disclaims production/cryptographic guarantees. Do not present it as a universal deployed detector. · Rules: DP11, DE13
- **adopt** · skill-build-work/modules/detection/.research/D26-detector.txt:L28-64 (local extraction; sha256:a8a8092b2f741307579be4c82aeaa96a8c6712a0b8f254eddb0be8a344600ec7) · The null concerns the given watermark key; context masking supports an independence assumption that can fail with long repeated contexts. A p-value is not authorship probability. · Rules: DE07, DE13

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Code read without execution; matching configuration required; no production certification inferred.

Access: Saved original source; no detector or research code was executed.

## D27: Our approach to EU text provenance rules

Source: https://openai.com/index/eu-text-provenance/

Read scope: Complete meaningful supplier announcement, limitations, and rollout scope; linked technical report not read.

Role: official supplier provenance announcement

- **adapt** · skill-build-work/modules/detection/.research/D27.txt:L9-23 (local extraction; sha256:bca7431d92d0d362256c5c932092eb132ce00e1edfd9ec6ae278c4fe26b8e155) · The announcement describes opt-in API coverage, staged EU rollout, restricted detector access, and length/domain-sensitive performance. Do not infer global universal marking. · Rules: DP11, DE13
- **adopt** · skill-build-work/modules/detection/.research/D27.txt:L53-69 (local extraction; sha256:bca7431d92d0d362256c5c932092eb132ce00e1edfd9ec6ae278c4fe26b8e155) · A watermark signals possible system involvement without identifying a user, measuring human contribution, or verifying accuracy. Absence is inconclusive. · Rules: DP10, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Supplier announcement dated October 5; no independent deployment or benchmark verification here.

Access: Saved original source; no detector or research code was executed.

## D28: How Claude’s text watermark works

Source: https://www.anthropic.com/news/claude-text-watermark

Read scope: Complete extracted technical explainer and caveats; linked external technical material not separately reviewed beyond D25/D26.

Role: official supplier technical explainer

- **adapt** · skill-build-work/modules/detection/.research/D28.txt:L9-30 (local extraction; sha256:4c6888ae3a5887ff3278f0978da7968b07f8f3235acde3c9c5d668f33a15db30) · The described watermark changes token-choice randomness and adds no hidden characters. It needs a compatible key and weakens in small/constrained samples. · Rules: DP10, DE13
- **adopt** · skill-build-work/modules/detection/.research/D28.txt:L43-59 (local extraction; sha256:4c6888ae3a5887ff3278f0978da7968b07f8f3235acde3c9c5d668f33a15db30) · Text detector access, signed file metadata, translated outputs, older-model rollout, and authorship claims differ. Producer involvement is not proof of original authorship. · Rules: DP10, DP11

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Supplier technical explanation; current model coverage should be checked against D39/current docs.

Access: Saved original source; no detector or research code was executed.

## D29: Does ChatGPT tell the truth?

Source: https://help.openai.com/en/articles/8313428-does-chatgpt-tell-the-truth

Read scope: Complete meaningful official help article; feedback excluded.

Role: official supplier limitations documentation

- **adopt** · skill-build-work/modules/detection/.research/D29.txt:L27-28 (local extraction; sha256:854b5c547c3bc939c778618c6a8abdf129af12f343295bdab842547ff13a0037) · ChatGPT cannot reliably attribute a text to AI or itself and may invent self-attribution answers. Do not treat prompted self-recognition as origin evidence. · Rules: DP01, DP09
- **adopt** · skill-build-work/modules/detection/.research/D29.txt:L5-11 (local extraction; sha256:854b5c547c3bc939c778618c6a8abdf129af12f343295bdab842547ff13a0037) · Confident prose can contain fabricated facts and citations. A natural revision still needs a claims/source check. · Rules: DP04, DE11

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Official product guidance rather than an experimental detector benchmark.

Access: Saved original source; no detector or research code was executed.

## D30: Can AI-Generated Text be Reliably Detected?

Source: https://arxiv.org/abs/2303.11156

Read scope: Selected abstract, theoretical main section, and surrounding interpretation. Full attack experiments, proofs, and appendices not reviewed.

Role: primary theory and robustness research

- **adapt** · skill-build-work/modules/detection/.research/D30-full.txt:L305-319 (local extraction; sha256:10a33f643a36e148df8e9b53d6dd214b01a6f3b465a0befc1f083a48233f705d) · The AUROC bound depends on total-variation distance between specified distributions; watermarked distributions can differ substantially. Reject universal mathematical-impossibility claims. · Rules: DP12, DE06
- **context_only** · skill-build-work/modules/detection/.research/D30-full.txt:L26-41 (local extraction; sha256:10a33f643a36e148df8e9b53d6dd214b01a6f3b465a0befc1f083a48233f705d) · Attack robustness and text quality are distinct measurements. Do not adopt paraphrasing or spoofing as editing procedures or infer future undetectability. · Rules: DP03, DE11, DE12
- **adapt** · skill-build-work/modules/detection/.research/D30-full.txt:L320-322 (local extraction; sha256:10a33f643a36e148df8e9b53d6dd214b01a6f3b465a0befc1f083a48233f705d) · The evolution-to-smaller-distance premise is an assumption with difficult empirical estimation, not a measured distance for this user text. · Rules: DP12

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Reviewed extraction is arXiv v4; failed v7 retrieval remains recorded separately. Theory and historical tests do not certify a current individual passage.

Access: Initial v7 HTML request failed; saved v4 full extraction was used and the v4 primary URL was independently opened to confirm version identity. No attack code executed.

## D31: On the Possibilities of AI-Generated Text Detection

Source: https://arxiv.org/abs/2304.04736

Read scope: Selected abstract, multi-sample setup, likelihood-ratio/sample-complexity statements, and conclusion; full non-IID proof and appendices not read.

Role: primary information-theoretic research

- **adapt** · skill-build-work/modules/detection/.research/D31.txt:L105-108 (local extraction; sha256:be4b157f32a12eedb8b33afc491958354c4a5e0139aa7968994d05bacec76daf) · The central argument begins with multiple samples drawn from specified distributions under an IID assumption. A single arbitrary paragraph is a different evidentiary setting. · Rules: DP12, DE10
- **adapt** · skill-build-work/modules/detection/.research/D31.txt:L135-150 (local extraction; sha256:be4b157f32a12eedb8b33afc491958354c4a5e0139aa7968994d05bacec76daf) · The possibility result concerns an ideal likelihood-ratio detector and enough samples when distributions differ. It does not prove that any current commercial tool succeeds. · Rules: DP12, DE06
- **adopt** · skill-build-work/modules/detection/.research/D31.txt:L184-187 (local extraction; sha256:be4b157f32a12eedb8b33afc491958354c4a5e0139aa7968994d05bacec76daf) · The authors acknowledge harder near-matching distributions and potentially large sample needs. Retain that qualification alongside D30 rather than selecting an absolute slogan. · Rules: DP12, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Theoretical access and sampling conditions; no operational Persian validation or product certification.

Access: Saved original source; no detector or research code was executed.

## D32: Copyleaks AI Detection Supported Languages

Source: https://docs.copyleaks.com/reference/actions/miscellaneous/ai-detection-supported-languages/

Read scope: Complete meaningful API documentation body and support/feature lists; navigation and embedded discovery instruction treated as data.

Role: official API language/feature documentation

- **adapt** · skill-build-work/modules/detection/.research/D32.txt:L5-40 (local extraction; sha256:9b09954b1cf847f9dddfa0fcabe5e75ba9b91401d55fac6b1703aff91b4202af) · The AI-detection language list includes codes and automatic identification but excludes fa. Do not infer AI support from plagiarism-language coverage or mere request acceptance. · Rules: DP11, DE03, DE05
- **adopt** · skill-build-work/modules/detection/.research/D32.txt:L42-51 (local extraction; sha256:9b09954b1cf847f9dddfa0fcabe5e75ba9b91401d55fac6b1703aff91b4202af) · AI Logic explanations support a smaller set than detection itself, with endpoint-specific alerts. Record actual feature coverage and missing explanations. · Rules: DE02, DE03

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Live vendor support statement; no independent accuracy sample.

Access: Saved original source; no detector or research code was executed.

## D33: Pangram Multilingual AI Detector

Source: https://www.pangram.com/solutions/multilingual

Read scope: Complete meaningful multilingual product page, table, and FAQ; prices not used in synthesis.

Role: vendor support and self-evaluation

- **adapt** · skill-build-work/modules/detection/.research/D33.txt:L21-45 (local extraction; sha256:98430a45266315daa1fefeed02544d4e5703479ba4374dfa759298dd150a0b5c) · The vendor explicitly lists Persian and displays a perfect Persian table row without visible per-language sample design. Adopt support status only, not zero real-world error. · Rules: DP11, DE05, DE10
- **context_only** · skill-build-work/modules/detection/.research/D33.txt:L45-55 (local extraction; sha256:98430a45266315daa1fefeed02544d4e5703479ba4374dfa759298dd150a0b5c) · Tokenizer/active-learning explanations and guarantees are promotional self-description. Do not turn them into independently established architecture or fairness conclusions. · Rules: DP02, DE06

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Vendor table and testimonial framing; sample sizes and independent Persian validation unavailable in the page.

Access: Saved original source; no detector or research code was executed.

## D34: Winston AI official product page

Source: https://gowinston.ai/

Read scope: Complete extracted official product page, validation summaries, and FAQs; linked papers not newly audited.

Role: official vendor product documentation

- **adapt** · skill-build-work/modules/detection/.research/D34.txt:L37-74 (local extraction; sha256:9dd248823cdea06e978d6345ecf16e562b28e20af4e7458ada2d3c9e3f90b6c8) · The page describes a human/AI odds scale and benchmark claims. Keep score definition, operating point, and provenance of evaluation separate. · Rules: DE02, DE06, DE07
- **adapt** · skill-build-work/modules/detection/.research/D34.txt:L49-50 (local extraction; sha256:9dd248823cdea06e978d6345ecf16e562b28e20af4e7458ada2d3c9e3f90b6c8) · A language section lists fourteen languages while the FAQ elsewhere lists eleven; neither includes Persian. Do not silently resolve the discrepancy into a definitive current list. · Rules: DP11, DE03, DE14
- **adopt** · skill-build-work/modules/detection/.research/D34.txt:L91-94 (local extraction; sha256:9dd248823cdea06e978d6345ecf16e562b28e20af4e7458ada2d3c9e3f90b6c8) · The vendor says algorithms update weekly. Historical performance requires version/date identification. · Rules: DE02

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Product claims, inconsistent support lists, and linked-study summaries are not independent verification of the deployed version.

Access: Saved original source; no detector or research code was executed.

## D35: Sapling AI Detector

Source: https://sapling.ai/ai-content-detector

Read scope: Complete extracted meaningful detector page, instructions, changelog, and FAQs; linked whitepaper not accessed.

Role: official vendor limitations and product documentation

- **adopt** · skill-build-work/modules/detection/.research/D35.txt:L47-55 (local extraction; sha256:943b7b3aa5e714b3aae923edd9b1fd690059205f568030d93322c7784d554450) · The vendor warns against standalone authorship conclusions, specifies score behavior and approximate length sensitivity, and lists supported languages. · Rules: DP09, DE03, DE07
- **adopt** · skill-build-work/modules/detection/.research/D35.txt:L113-126 (local extraction; sha256:943b7b3aa5e714b3aae923edd9b1fd690059205f568030d93322c7784d554450) · Accuracy depends on input/threshold; unsupported languages use an English model and are less reliable. Distinguish accepted input from validated Persian support. · Rules: DE05, DE09
- **adopt** · skill-build-work/modules/detection/.research/D35.txt:L130-135 (local extraction; sha256:943b7b3aa5e714b3aae923edd9b1fd690059205f568030d93322c7784d554450) · The vendor reports false scan-pass claims by third-party tools. Never claim a successful scan without an actual identified run. · Rules: DP03, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Vendor documentation/self-evaluation, with changing feature support; no independent Persian benchmark.

Access: Saved original source; no detector or research code was executed.

## D36: Reddit r/Professors: AI Detectors

Source: https://www.reddit.com/r/Professors/comments/1wdo1zg/ai_detectors/

Read scope: Selected original thread comments exposed by web retrieval after direct HTTP 403; complete thread and linked studies not read.

Role: original user discussion; contextual only

- **context_only** · skill-build-work/modules/detection/.research/D36-web.txt:L131-143 (local extraction; sha256:5c20ceebfcd7a02b089c262786083c59487aa0d7a4bce2f4f1f8a5d90fa73ec2) · One commenter reports perfect personal testing while another reports old writing falsely flagged. Neither supplies a reproducible denominator/version design. · Rules: DP09, DE06
- **adapt** · skill-build-work/modules/detection/.research/D36-web.txt:L136-167 (local extraction; sha256:5c20ceebfcd7a02b089c262786083c59487aa0d7a4bce2f4f1f8a5d90fa73ec2) · Even a favorable commenter separates a detector ping from an accusation. Treat anecdotes as review questions, not measured error rates or verified policy. · Rules: DP09, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Unverified users, selected comments, self-selection, missing controls, and no representative Persian sample.

Access: Direct retrieval returned HTTP 403; original Reddit page was accessible through web retrieval. D36-web.txt preserves returned text with web line labels; all cited L numbers here are LOCAL file lines, not publisher pagination.

## D37: Reddit r/academia: AI detection software is junk science

Source: https://www.reddit.com/r/academia/comments/1rjlea0/ai_detection_software_is_junk_science_and_we_need/

Read scope: Selected original-thread passages found by targeted web retrieval after direct HTTP 403; complete discussion and linked studies not fully reviewed.

Role: original user discussion; contextual only

- **context_only** · skill-build-work/modules/detection/.research/D37-web.txt:L43-61 (local extraction; sha256:29fba48d4d6ff69eb96a87bcec13c07967661764521a6975fbb446d0ab57741e) · An unverified account claims study authorship and possible contamination of two human labels. This cannot amend the paper or establish the true error rate. · Rules: DP09, DE01, DE06
- **adapt** · skill-build-work/modules/detection/.research/D37-web.txt:L79-81 (local extraction; sha256:29fba48d4d6ff69eb96a87bcec13c07967661764521a6975fbb446d0ab57741e) · A claimed perfect outcome follows preselecting suspicious writing. Such selection cannot estimate error rates on an unselected population. · Rules: DE04, DE10
- **adapt** · skill-build-work/modules/detection/.research/D37-web.txt:L86-97 (local extraction; sha256:29fba48d4d6ff69eb96a87bcec13c07967661764521a6975fbb446d0ab57741e) · The discussion distinguishes older and newer evidence but mixes quotations and claims. Verify underlying sources rather than promote thread statistics. · Rules: DE06, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Selected comments and unverifiable identity; no independent ground-truth correction or product endorsement.

Access: Direct retrieval returned HTTP 403; targeted find on the accessible original web page supplied selected passages. D37-web.txt includes repeated web excerpts; cited L numbers are LOCAL extraction lines.

## D38: People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text

Source: https://arxiv.org/html/2501.15654v2

Read scope: Selected abstract, controlled task/selection design, reader-experience comparison, stylistic explanations, conclusion, and limitations; full appendix/annotation corpus not reviewed.

Role: primary human-evaluation study

- **adapt** · skill-build-work/modules/detection/.research/D38.txt:L45-68 (local extraction; sha256:9c8795eccaae5a3a33f05c3f29947e28b51d169367721eb8f09c8829320092fa) · The study randomizes matched English nonfiction articles and asks for explanations. Adapt blinded, relevant-reader comparisons when evaluating revisions. · Rules: DE04, DE11
- **adapt** · skill-build-work/modules/detection/.research/D38.txt:L378-392 (local extraction; sha256:9c8795eccaae5a3a33f05c3f29947e28b51d169367721eb8f09c8829320092fa) · Readers cite repeated sentence molds, formulaic structure, and lack of surprise. Use these as contextual editorial questions, not universal origin tests or instructions to insert mistakes. · Rules: DP05, DP06
- **adapt** · skill-build-work/modules/detection/.research/D38.txt:L491-498 (local extraction; sha256:9c8795eccaae5a3a33f05c3f29947e28b51d169367721eb8f09c8829320092fa) · The domain is professionally edited American-English articles and some origin contamination remains possible. Do not generalize expert accuracy to Persian or all readers. · Rules: DP09, DE06, DE10

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Five experts, bounded nonfiction domain and historical generators; factual accuracy was not evaluated.

Access: Saved original source; no detector or research code was executed.

## D39: How Claude marks AI-generated content

Source: https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content

Read scope: Complete meaningful current support article, model coverage table, detection access, and limitations; related-article navigation excluded.

Role: official supplier provenance/support documentation

- **adopt** · skill-build-work/modules/detection/.research/D39.txt:L18-32 (local extraction; sha256:b70e74eec276fcd45eb78e1b9c5791bb844e3678e4c1debd24bb748b95e73633) · Support varies by model/surface while older-model marking is in progress and text detection remains restricted. Preserve the dated coverage rather than assume all outputs are marked. · Rules: DP11, DE13
- **adopt** · skill-build-work/modules/detection/.research/D39.txt:L90-111 (local extraction; sha256:b70e74eec276fcd45eb78e1b9c5791bb844e3678e4c1debd24bb748b95e73633) · Text marks and signed file credentials differ; a mark can signal processing rather than original authorship, while absence has several explanations. · Rules: DP01, DP10, DE14

Integration: references/detection-and-provenance.md, references/detector-evaluation.md

Limits: Supplier support snapshot; no independent deployment or current detector validation was run.

Access: Saved original source; no detector or research code was executed.

## D40: GPTZero AI Detection Benchmarking

Source: https://gptzero.me/news/gptzero-ai-detection-benchmarking-the-industry-standard-in-accuracy-transparency-and-fairness/

Read scope: Selected meaningful benchmark methodology, versions, mappings, metrics, and test descriptions; not every result row or complete page reviewed.

Role: vendor benchmark methodology and self-evaluation

- **adopt** · skill-build-work/modules/detection/.research/D40.txt:L38-58 (local extraction; sha256:03230c43b772de2db309052131d717923477a61e2b5a3d8c820b72289f81b8a2) · The vendor describes held-out construction, version tags, and excluding failed requests. Record versions and failures rather than compare only successful scans. · Rules: DE02, DE04, DE10
- **adopt** · skill-build-work/modules/detection/.research/D40.txt:L59-94 (local extraction; sha256:03230c43b772de2db309052131d717923477a61e2b5a3d8c820b72289f81b8a2) · Mixed is mapped to AI here, unlike the strict verdict in D09. Class mapping changes metrics; declare it before comparison. · Rules: DE01, DE07, DE09
- **context_only** · skill-build-work/modules/detection/.research/D40.txt:L278-281 (local extraction; sha256:03230c43b772de2db309052131d717923477a61e2b5a3d8c820b72289f81b8a2) · Bypasser testing is vendor-designed and evolving. Public benchmarking rhetoric does not establish independent evaluation or future guarantees. · Rules: DE06, DE12, DE14

Integration: references/detector-evaluation.md

Limits: Vendor-controlled benchmark, changing versions and selected sections; original raw predictions were not audited.

Access: Saved original source; no detector or research code was executed.

## A01: Wikipedia: Signs of AI writing

Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: community editorial field guide, not policy or empirical validation

- **context_only** · A01.txt:L6-L32 · The page describes observations for Wikipedia and warns against authorship judgments from style or detectors alone. · Rules: AS00, VS10
- **adapt** · A01.txt:L39-L207 · Inflation, superficial interpretation, and vague attribution can conceal missing subject-specific information. · Rules: AS01, AS02, AS03, AS04
- **adapt** · A01.txt:L270-L367;L975-L1000 · Simple copulas, formal grammar, ordinary transitions, and deliberate rhetorical shapes can be appropriate human choices. · Rules: AS05, AS08, VS06
- **adapt** · A01.txt:L750-L834;L1037-L1079 · Citation failures need verification; punctuation and synonym variation depend on context and time. · Rules: AS07, AS10, AS11

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Wikipedia-specific descriptive guide; cited studies and recent model-era assertions were not all independently checked. Its observations do not establish authorship.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A02: blader/humanizer — SKILL.md

Source: https://github.com/blader/humanizer/blob/main/SKILL.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A02.txt:L34-L53 · The workflow protects supplied claims and non-prose; a readable author sample outranks generic patterns. · Rules: AS00, VS02, VS03
- **adapt** · A02.txt:L59-L158;L225-L272 · It distinguishes empty contrast, repeated closers, and vague relations from informative uses of those structures. · Rules: AS05, AS06, AS07
- **reject** · A02.txt:L160-L181;L383-L393 · The blanket dash restriction conflicts with its contextual voice guidance; preserve useful punctuation without a numerical quota. · Rules: AS10, VS06
- **adapt** · A02.txt:L366-L381 · Replies can bury a decision under context the reader already has. · Rules: AS12

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A03: hardikpandya/stop-slop — SKILL.md

Source: https://raw.githubusercontent.com/hardikpandya/stop-slop/main/SKILL.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A03.txt:L15-L29 · Specificity and removable staging are actionable editorial concerns; directness must retain necessary content. · Rules: AS01, AS06, AS08
- **reject** · A03.txt:L19-L25;L35-L43 · Universal human-subject, passive, adverb, triad and dash bans erase valid language and relations. · Rules: AS09, VS06
- **context_only** · A03.txt:L48-L60;A03-examples.txt:L15-L35 · Its self-rating is uncalibrated; examples remove qualifiers or change claims while compressing. · Rules: AS13, VS03, VS04

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A04: stop-slop — references/phrases.md

Source: https://github.com/hardikpandya/stop-slop/blob/main/references/phrases.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A04.txt:L3-L51;L85-L128 · Phrase families organize previews, business jargon, and empty importance claims for contextual review. · Rules: AS06, AS08
- **reject** · A04.txt:L53-L83 · The complete adverb ban would remove real manner, frequency, uncertainty, and emphasis. · Rules: AS09, VS04

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A05: stop-slop — references/structures.md

Source: https://github.com/hardikpandya/stop-slop/blob/main/references/structures.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A05.txt:L3-L57 · Contrasts, negative lists, fragments and staged questions can supply empty rhetorical buildup. · Rules: AS05, AS06
- **reject** · A05.txt:L66-L106 · Its agency and passive rules demand a human actor even when source information or topical focus does not justify one. · Rules: AS09
- **reject** · A05.txt:L108-L134 · Blanket opening and item-count bans confuse deliberate parallelism and real inventories with formulaic use. · Rules: AS07, VS06

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A06: petergyang/no-ai-slop — SKILL.md

Source: https://github.com/petergyang/no-ai-slop/blob/main/skills/no-ai-slop/SKILL.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A06.txt:L10-L42;A06-eval.txt:L9-L19 · Inspection leaves text unchanged and avoids authorship guesses; minimal editing protects voice and useful long sentences. · Rules: AS00, VS02, VS09, VS10
- **adapt** · A06.txt:L35-L39;L62-L72 · Portability, concrete mechanisms and stable referents support diagnosis; specificity must already be grounded. · Rules: AS01, AS07, AS08
- **reject** · A06.txt:L44-L50;L84-L88 · Absolute vocabulary bans and fixed dash allowances are taste constraints, not general evidence of bad writing. · Rules: AS08, AS10, VS06

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A07: obra/the-elements-of-style — writing-clearly-and-concisely

Source: https://github.com/obra/the-elements-of-style/blob/main/skills/writing-clearly-and-concisely/SKILL.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A07-elements.txt:L251-L333;L467-L554 · The underlying text links paragraphing to reader comprehension and preserves informative parallel structure. · Rules: AS07, AS10, VS05
- **adapt** · A07-elements.txt:L335-L357;L556-L597 · It expressly permits passive voice for topical focus and uses word placement to clarify relations. · Rules: AS09, VS04
- **reject** · A07-elements.txt:L679-L710;L762-L770;L907-L934 · Historical usage prescriptions include obsolete restrictions and generic masculine pronouns; they are not modern bilingual defaults. · Rules: VS07

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A08: manavmishra/ZeroSlop — SKILL.md

Source: https://github.com/manavmishra/ZeroSlop/blob/main/SKILL.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A08.txt:L34-L83;L94-L105 · Fidelity includes interior claims and limits; missing substance must not be replaced with invented detail. · Rules: AS01, VS02, VS03
- **adapt** · A08.txt:L341-L439;A08-overcorrection.txt:L7-L57 · Contextual diagnosis and overcorrection review catch staged voice that lexical scoring misses. · Rules: AS00, AS05, VS08
- **reject** · A08.txt:L506-L527;L547-L594 · Fixed cadence and rhetorical budgets are project heuristics; no supplied independent bilingual validation justifies adopting them. · Rules: AS10, AS13, VS06
- **adapt** · A08.txt:L636-L722;A08-eval.txt:L223-L291 · Entity checks cannot certify agency, implication, emphasis, or qualification; exact-final comparison remains necessary. · Rules: VS03, VS04, VS09
- **context_only** · A08.txt:L881-L993;A08-evidence.txt:L324-L348 · Private pattern learning and model cloze probes differ from weight training and calibrated probability methods. · Rules: AS13, AS14, VS10

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.; Maintainer score, cloze-probe and benchmark claims are not independent validation. No private learning, remote service, source scripts or corpus was executed.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A09: seyedehsanhadi/sloptrim — SKILL.md

Source: https://github.com/seyedehsanhadi/sloptrim/blob/main/SKILL.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A09.txt:L94-L116;A09-patterns.txt:L537-L555 · Attribution, quantity-to-noun relations, scope and merge fields require semantic preservation beyond entity lists. · Rules: AS03, AS09, AS11, VS03
- **adapt** · A09.txt:L209-L227;A09-ethics.txt:L12-L46 · The documented score is heuristic; character cleaning has protected-span and format limits and cannot establish authorship. · Rules: AS11, AS13, VS10
- **reject** · A09-patterns.txt:L28-L82;L407-L457 · Worked examples add unsupplied details; rhythm targets and a length ceiling do not prove fidelity or naturalness. · Rules: VS03, VS06
- **adapt** · A09.txt:L36-L88;A09-patterns.txt:L529-L535 · Genre routing recognizes that factual prose and personal prose permit different interventions. · Rules: VS01, VS08

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.; No detector executed; worked examples are illustrative, and missing facts in before/after pairs cannot be imported into live edits.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A10: ali2000hos/persian-writing — SKILL.md

Source: https://github.com/ali2000hos/persian-writing/blob/main/SKILL.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A10.txt:L40-L55;L80-L98 · Routing separates register, orthography, genre and layout; destination can require formality despite a casual request. · Rules: VS01, VS07
- **adapt** · A10-orthography.txt:L23-L112;L191-L268 · Functional Persian joining and mixed-direction text need language-aware treatment rather than indiscriminate Unicode removal. · Rules: AS11, VS07
- **adapt** · A10-academic.txt:L122-L209;A10-content-structures.txt:L70-L96 · Source-based paraphrase preserves qualifications, quantities and attribution; inferred links must remain distinct. · Rules: VS03, VS04
- **reject** · A10-seo-copywriting.txt:L150-L180;A10-social-channels.txt:L76-L87 · Ranking guarantees, word-count floors and screen-length claims lack independent primary substantiation in these instructions. · Rules: VS08
- **context_only** · A10.txt:L207-L265 · Renderer-specific absolute technical claims were not verified from standards or code and are not adopted. · Rules: VS07

Integration: references/voice-and-structure.md, references/anti-slop.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.; No renderer-specific technical claims or SEO ranking assertions were independently validated.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A11: persian-writing — references/writing-style.md

Source: https://github.com/ali2000hos/persian-writing/blob/main/references/writing-style.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A11.txt:L23-L61;L97-L140;L246-L258 · Audience and destination guide register; appropriate politeness, loanwords and literary language deserve protection. · Rules: VS01, VS07
- **reject** · A11.txt:L148-L184 · Some examples strengthen ranking or add business results; those rewrites cannot justify invented specificity. · Rules: AS02, VS03
- **adapt** · A11.txt:L200-L244;L295-L299 · Translationese, repeated transitions and terminology cycling need contextual review; real detail should drive variation. · Rules: AS07, AS08, VS06
- **context_only** · A11.txt:L301-L338 · Its detector statistics are secondary claims, not direct Persian validation. · Rules: AS13, VS10

Integration: references/voice-and-structure.md, references/anti-slop.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A12: Anthropic — internal-comms skill

Source: https://github.com/anthropics/skills/blob/main/skills/internal-comms/SKILL.md

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read. Dedicated license inspected only in the two listed excerpt ranges.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A12.txt:L17-L29;A12-general-comms.txt:L5-L16 · The architecture selects task-specific guidance before drafting and identifies audience, purpose, tone and format. · Rules: VS01, VS05
- **adapt** · A12-3p-updates.txt:L2-L9;L38-L47;A12-faq-answers.txt:L16-L30 · Status and FAQ formats legitimately use repeated structure; uncertain answers should remain qualified and attributable. · Rules: AS10, VS01, VS08
- **context_only** · A12-company-newsletter.txt:L1-L21 · Its newsletter length, emoji and organizational assumptions are company-specific examples. · Rules: AS10, VS08

Integration: references/voice-and-structure.md, references/anti-slop.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A13: Vale prose linter

Source: https://github.com/errata-ai/vale

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A13.txt:L46-L74 · Vale separates an extensible rule system from a chosen style and can scope markup separately from prose. · Rules: AS00, AS13
- **context_only** · A13.txt:L76-L127 · The shown benchmarks concern tooling and named corpora, not independent semantic quality or Persian validation. · Rules: AS13, VS10

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Read documentation and listed companion material, not every implementation file. No installation, benchmark reproduction, or Persian performance evaluation.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A14: Proselint

Source: https://github.com/amperser/proselint

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A14.txt:L132-L186;L218-L296 · Diagnostics carry locations and check identities, with granular and per-file configuration. · Rules: AS13, VS09
- **adapt** · A14.txt:L300-L379 · Its English advice mixes mechanics with preferences such as suppressing hedging; those require genre review. · Rules: AS09, AS13, VS08

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Read documentation and listed companion material, not every implementation file. No installation, benchmark reproduction, or Persian performance evaluation.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A15: write-good

Source: https://github.com/btford/write-good

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A15.txt:L15-L69;L168-L197 · Local suggestions expose spans and reasons; checks and exceptions are configurable. · Rules: AS08, AS13
- **context_only** · A15.txt:L35-L57;L199-L208 · A non-English extension is separate from the default English linter; configurability is not Persian validation. · Rules: AS13, VS10

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Read documentation and listed companion material, not every implementation file. No installation, benchmark reproduction, or Persian performance evaluation.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A16: alex

Source: https://alexjs.com/

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A16.txt:L5-L14;A16-readme.txt:L75-L99 · The tool targets considerate phrasing, a distinct goal from authorship or generic quality classification. · Rules: AS13, VS07
- **adapt** · A16-readme.txt:L141-L175;L568-L607 · Its own guidance acknowledges false positives and identity-specific language preferences; literal matching cannot decide all context. · Rules: VS07, VS10

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Read documentation and listed companion material, not every implementation file. No installation, benchmark reproduction, or Persian performance evaluation.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A17: LanguageTool — supported languages

Source: https://dev.languagetool.org/languages

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Dedicated license inspected only in the two listed excerpt ranges.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **context_only** · A17.txt:L3-L8;L59-L62 · The page describes unequal language support and dates its table to LanguageTool 6.6 in March 2025. · Rules: AS13, VS10
- **adapt** · A17.txt:L30-L43 · English and Persian rows differ substantially; counts do not establish equal quality or current deployed capabilities. · Rules: AS13, VS07

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Read documentation and listed companion material, not every implementation file. No installation, benchmark reproduction, or Persian performance evaluation.; Historical table is explicitly version 6.6 dated 2025-03-27; current deployment capabilities not established.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A18: Stop Slop issue 42 — losing logical connectors

Source: https://github.com/hardikpandya/stop-slop/issues/42

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: anecdotal primary user critique

- **adapt** · A18.txt:L7-L11 · The reporter shows how removing staging also removes an explicit causal connection or contrast. · Rules: VS04
- **adapt** · A18.txt:L13-L17 · Words can carry logic or narrator stance without introducing a factual proposition; deletion needs a functional test. · Rules: AS01, AS09, VS04

Integration: references/voice-and-structure.md, references/anti-slop.md

Limits: Single user report; no controlled experiment or local reproduction. Saved comments endpoints contain an empty array.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A19: Stop Slop issue 46 — missing references on installation

Source: https://github.com/hardikpandya/stop-slop/issues/46

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: anecdotal primary packaging report

- **context_only** · A19.txt:L1-L5 · A user reports an installation that omitted referenced files; the report was not reproduced here. · Rules: AS15
- **adapt** · A19.txt:L7-L11 · The proposed package layout groups core and references, motivating extracted-package link checks. · Rules: AS15

Integration: references/anti-slop.md

Limits: Single user report; no controlled experiment or local reproduction. Saved comments endpoints contain an empty array.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A20: bheijden/slop

Source: https://github.com/bheijden/slop

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Listed substantive companion texts were also read in full; scripts and unlisted repository files were not read.

Role: primary maintainer/editorial instructions, not independent effectiveness evidence

- **adapt** · A20.txt:L70-L97;A20-docs-rules.txt:L349-L387 · Rule sets distinguish worn phrases from authorship, identify English-only coverage, and leave semantic dimensions unmeasured. · Rules: AS08, AS13, VS10
- **adapt** · A20-docs-styles.txt:L11-L37;L135-L183 · Register bands and defect findings answer different questions; documented tension calls for editorial arbitration. · Rules: AS10, VS01, VS08
- **context_only** · A20-research-audit.txt:L12-L57;L307-L321;L453-L474 · Its small maintainer audit reports overlapping cadence distributions and false positives; results are narrow and unreproduced. · Rules: AS13, VS06
- **adapt** · A20-research-k-and-window.txt:L62-L123;A20-notice.txt:L4-L15 · Corpus baselines can drift, and component provenance and licenses differ from the engine license. · Rules: AS14, AS15

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Read documentation and listed companion material, not every implementation file. No installation, benchmark reproduction, or Persian performance evaluation.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A21: Measuring AI Slop in Text — v3

Source: https://arxiv.org/html/2509.19163v3

Read scope: Complete meaningful main text and appendices read in bounded chunks within the listed ranges; bibliography outside those ranges not claimed read; figures reviewed only through extracted captions/text.

Role: primary English-language empirical research with construct and transfer limits

- **adapt** · A21.txt:L19-L45;L152-L159 · Slop is analyzed across utility, information quality, and style; origin and quality are distinct questions. · Rules: AS00, VS08
- **adapt** · A21.txt:L160-L230;L242-L262 · Annotation judgments vary and salient dimensions change between news and short answers. · Rules: VS01, VS08
- **adapt** · A21.txt:L266-L406;L1768-L1778 · Automatic metrics and prompted judges only partially align with human labels; clean self-review cannot certify quality. · Rules: AS13, VS09, VS10
- **context_only** · A21.txt:L407-L413;L996-L999 · The study uses English texts and selected North American editors, leaving Persian transfer unverified. · Rules: AS13, VS07

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Main meaningful text and appendices read as saved HTML text; bibliography only partly inspected. Embedded figure images were not visually inspected; extracted equations/tables can contain HTML duplication. No experiment reproduced. Persian transfer unverified.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A22: Antislop: A Comprehensive Framework — v2

Source: https://arxiv.org/html/2510.15061v2

Read scope: Complete meaningful main text and appendices read in bounded chunks within the listed ranges; bibliography outside those ranges not claimed read; figures reviewed only through extracted captions/text.

Role: primary method paper with model/domain/judge limits

- **adapt** · A22.txt:L39-L44;L729-L735 · Pattern overrepresentation is relative to a human baseline and creative-writing domain, not raw frequency alone. · Rules: AS08, AS14
- **context_only** · A22.txt:L70-L132;L499-L523 · Backtracking and FTPO require distinct inference and training machinery; suppression has throughput and intervention trade-offs. · Rules: AS14
- **context_only** · A22.txt:L133-L165;L261-L274 · Reported quality uses particular models, prompts and automated judges; it does not establish this skill’s effect or Persian transfer. · Rules: AS13, AS14, VS10

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: Main meaningful text and appendices read as saved HTML text; bibliography only partly inspected. Embedded figure images were not visually inspected; extracted equations/tables can contain HTML duplication. No experiment reproduced. Persian transfer unverified.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A23: Antislop Sampler

Source: https://github.com/sam-paech/antislop-sampler

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers. Dedicated license inspected only in the two listed excerpt ranges.

Role: primary maintainer method documentation, no execution

- **context_only** · A23.txt:L172-L194 · The sampler requires cached generation state, continuation access and probability intervention; Markdown instructions are not equivalent. · Rules: AS14
- **adapt** · A23.txt:L71-L89;L176-L182 · The maintainer calls the default list incompletely curated and the implementation research grade; context-specific vetting matters. · Rules: AS08, AS14

Integration: references/anti-slop.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A24: Auto-Antislop

Source: https://github.com/sam-paech/auto-antislop

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: primary maintainer pipeline documentation, no execution

- **context_only** · A24.txt:L3-L8;L164-L214 · The pipeline generates a baseline, compares patterns, makes preference pairs and optionally trains weights. · Rules: AS14
- **adapt** · A24.txt:L98-L124;L267-L290 · Prompt selection determines the targeted domain; saved configuration and results support traceable experiments, not prompt-level guarantees. · Rules: AS14, VS10

Integration: references/anti-slop.md, references/voice-and-structure.md

Limits: No independent Persian effectiveness evaluation or tool execution was performed for this source.; All submodule code and licenses were not audited.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## A25: Hacker News — repeated rewriting of approved marketing copy

Source: https://news.ycombinator.com/item?id=48983839

Read scope: Complete saved primary text read in bounded untruncated chunks; locators identify the exact saved extraction, not remote web line numbers.

Role: anecdotal user discussion

- **adapt** · A25.txt:L12-L24 · A participant reports repeated unwanted rewrites of authored marketing copy while an agent worked on other tasks. · Rules: VS03
- **context_only** · A25.txt:L18-L28 · Suggestions and reactions in the thread are anecdotes, not comparative evidence of a skill’s effectiveness. · Rules: AS13, VS10

Integration: references/voice-and-structure.md, references/anti-slop.md

Limits: Visible comment thread only; self-reports are not representative data. Relative dates were not converted to exact dates.

Access: Previously fetched original reused from scratch; no new network request in this resumed review. Raw original and text extraction retained for root verification.

## Q01: Creating helpful, reliable, people-first content

Source: https://developers.google.com/search/docs/fundamentals/creating-helpful-content

Read scope: Article body, local Q01.txt lines 32–232; no linked rater manual or ranking system inspected.

Role: official_documentation_or_announcement

- **adopt** · Q01.txt:44–67,74–117 · Reader usefulness and original value matter; the page explicitly disclaims a preferred word count. · Rules: WEB-01, WEB-02
- **adapt** · Q01.txt:118–141,185–221 · E-E-A-T is not one ranking factor; creator/process transparency must be accurate. · Rules: WEB-02

Integration: references/web-seo.md

Limits: Official publisher guidance, not a causal writing experiment or ranking guarantee.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q02: Google Search guidance on generative AI content

Source: https://developers.google.com/search/docs/fundamentals/using-gen-ai-content

Read scope: Complete substantive guidance, Q02.txt:32–72.

Role: official_documentation_or_announcement

- **adopt** · Q02.txt:32–45 · AI assistance can structure content, but scaled generation without user value can violate policy. · Rules: WEB-02
- **adopt** · Q02.txt:46–66 · Review accuracy also covers titles, descriptions, structured data, and alt text. · Rules: WEB-02

Integration: references/web-seo.md

Limits: Does not establish a detector threshold or guaranteed discovery. Merchant Center details were not independently expanded.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q03: Spam policies for Google web search

Source: https://developers.google.com/search/docs/essentials/spam-policies

Read scope: Selected writing-relevant policy sections: Q03.txt:106–166 and 195–229; broader site-reputation/technical policies not treated as fully reviewed.

Role: official_documentation_or_announcement

- **adopt** · Q03.txt:122–132 · Keyword stuffing includes unnatural repetitive wording. · Rules: WEB-02, WEB-06
- **adopt** · Q03.txt:203–229 · Low-value scaled content and slight transformations of scraped text can be abusive irrespective of production tool. · Rules: WEB-02

Integration: references/web-seo.md

Limits: Policy scope is narrower than all SEO implementation decisions; no complete enforcement mechanism is public.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q04: ICMJE: Use of AI by Authors

Source: https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html

Read scope: Complete author AI-use policy body, Q04.txt:3–24.

Role: professional_consensus_or_editorial_standard

- **adapt** · Q04.txt:4–16 · AI-use disclosure and human responsibility remain required in the stated biomedical framework. · Rules: ACA-05
- **adopt** · Q04.txt:17–24 · Outputs require review for errors, bias, attribution, and plagiarism; AI output is not a primary source. · Rules: ACA-05, CLM-02

Integration: references/academic.md, references/claims-and-research.md

Limits: ICMJE is an editorial framework; other institutions and journals may impose different details.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q05: CONSORT 2025 Statement

Source: https://www.equator-network.org/reporting-guidelines/consort/

Read scope: EQUATOR scope/history/extension routing Q05.txt:25–44,48–106; full accessible statement prose Q05-statement.txt:10–93. Table 1 and flow diagram images and long explanation paper not read item by item.

Role: professional_consensus_or_editorial_standard

- **adopt** · Q05-statement.txt:70–87 · CONSORT 2025 supersedes the 2010 parent statement and retains relevant extensions. · Rules: ACA-02
- **adopt** · Q05-statement.txt:88–93 · Coverage concerns reporting actual conduct; it is not a study-quality instrument or mandatory prose structure. · Rules: ACA-02

Integration: references/academic.md

Limits: Statement prose reviewed; complete checklist/diagram image contents were not inspected. No manuscript compliance is certified.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q06: PRISMA 2020 Statement

Source: https://www.equator-network.org/reporting-guidelines/prisma/

Read scope: EQUATOR scope and routes Q06.txt:25–48,61–99; statement body Q06-statement.txt:17–86. Checklist tables and flow-diagram images are excluded from read claims.

Role: professional_consensus_or_editorial_standard

- **adopt** · Q06-statement.txt:29–42 · PRISMA 2020 covers systematic review reports; protocols and special review types need their own routes. · Rules: ACA-02
- **adapt** · Q06-statement.txt:65–79 · Reporting includes search/selection methods, exclusions, certainty, and available materials; locations are flexible. · Rules: ACA-02

Integration: references/academic.md

Limits: Reporting guidance does not evaluate conduct quality. No item-level certification from extracted prose.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q07: STROBE Statement

Source: https://www.equator-network.org/reporting-guidelines/strobe/

Read scope: EQUATOR scope Q07.txt:25–56,92–111; statement main prose Q07-statement.txt:53–221. Image checklist table and lengthy explanation article not inspected.

Role: professional_consensus_or_editorial_standard

- **adopt** · Q07.txt:103–110; Q07-statement.txt:85–98 · STROBE addresses cohort, case-control, and cross-sectional reports; it does not prescribe study design. · Rules: ACA-02
- **adopt** · Q07-statement.txt:181–221 · Checklist coverage must not standardize all prose or become a research-quality score. · Rules: ACA-02, ACA-04

Integration: references/academic.md

Limits: Consensus reporting standard; an observational design or checklist cannot alone establish causality.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q08: SAGER guidelines

Source: https://www.equator-network.org/reporting-guidelines/sager-guidelines/

Read scope: EQUATOR Q08.txt:25–53; article body Q08-statement.txt:51–119, including prose reporting recommendations; correction notice body read. Unrendered table/flowchart images, appendices and reviewer reports not read.

Role: professional_consensus_or_editorial_standard

- **adopt** · Q08-statement.txt:52–53,84–100 · Sex and gender differ; reporting depends on relevance, actual ascertainment, and appropriate analyses. · Rules: ACA-02, ACA-03
- **adapt** · Q08-statement.txt:101–119; Q08-correction.txt:18–22 · Generalisability and missing analyses require explanation; the correction adds missing peer-review reports. · Rules: ACA-03

Integration: references/academic.md

Limits: 2016 guidance with acknowledged limits for gender-diverse populations; current destination terminology still matters. Correction content, not supplemental reviews, inspected.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q09: ARRIVE Guidelines 2.0

Source: https://www.equator-network.org/reporting-guidelines/improving-bioscience-research-reporting-the-arrive-guidelines-for-reporting-animal-research/

Read scope: EQUATOR route Q09.txt:25–68; official guideline overview Q09-guidelines.txt:4–13; full statement prose Q09-statement.txt:10–59. Checklist images/individual explanation pages not itemwise inspected.

Role: professional_consensus_or_editorial_standard

- **adopt** · Q09-guidelines.txt:4–13; Q09-statement.txt:35–37 · ARRIVE 2.0 distinguishes Essential 10 from additional contextual reporting. · Rules: ACA-02
- **adapt** · Q09-statement.txt:52–59 · Reporting guidance complements journal requirements; incomplete reporting limits appraisal. · Rules: ACA-02, ACA-03

Integration: references/academic.md

Limits: Statement DOI e3000410 distinguishes it from explanation DOI e3000411; landing bibliography conflates these. No complete checklist audit claimed.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q10: COPE: Authorship and AI tools

Source: https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools

Read scope: Formal COPE position text, Q10.txt:17–28; user comments and related guidance are not policy evidence.

Role: discovery_only_not_evidence

- **adopt** · Q10.txt:17–26 · AI tools cannot take authorship responsibility. · Rules: ACA-05
- **adapt** · Q10.txt:27 · Authors must disclose relevant tool use and remain responsible for manuscript content. · Rules: ACA-05

Integration: references/academic.md

Limits: Prior archive access failure is resolved; comment-thread claims do not inherit COPE authority.

Access: Direct original now accessible; formal position recovered despite prior archive 403. Body distinguished from unendorsed comments.

## Q11: Zotero: The Basics

Source: https://www.zotero.org/support/quick_start_guide

Read scope: All substantive basics sections Q11.txt:1–63; navigation excluded.

Role: official_documentation_or_announcement

- **adopt** · Q11.txt:9–14,25–42 · Items combine metadata, attachments, notes, and identifier-based capture. · Rules: TOL-01, TOL-02
- **adapt** · Q11.txt:39–40,47–55 · Automatic capture may need metadata completion; citation formatting is a separate capability. · Rules: TOL-02

Integration: references/tools-and-evidence.md

Limits: Documentation establishes functionality, not correctness of every imported record. No tool installed or executed.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q12: Purdue OWL: Toulmin Argument

Source: https://owl.purdue.edu/owl/general_writing/academic_writing/historical_perspectives_on_argumentation/toulmin_argument.html

Read scope: Original web-rendered body, turn97view0 lines 28–61; direct local HTML was a five-line challenge page and is not counted as body.

Role: professional_guidance_or_framework

- **adapt** · https://owl.purdue.edu/owl/general_writing/academic_writing/historical_perspectives_on_argumentation/toulmin_argument.html, section What is the Toulmin Method?, web lines 30–35 · Claim, evidence, and the linking assumption are distinct argument components. · Rules: CLM-03
- **adapt** · same original page, web lines 46–52 · Qualifications and rebuttals can make the argument appropriately bounded. · Rules: CLM-03

Integration: references/claims-and-research.md

Limits: Teaching framework, not a validated universal paragraph template. No local source-body hash available for the web-rendered view.

Access: Recovered actual body through web tool, not the archived summary. Local Q12.raw/txt hashes identify challenge response only and are intentionally excluded as evidence.

## Q13: Self-Refine: Iterative Refinement with Self-Feedback

Source: https://arxiv.org/html/2303.17651v2

Read scope: Paper main body Q13.txt:45–454, including methods, metrics, results, analysis, discussion/limitations, conclusion; references and appendices not read as full text.

Role: primary_research_with_scope_limits

- **adapt** · Q13.txt:111–225,297–327 · Specific actionable feedback and a stop condition are central; generic repetition is not the same procedure. · Rules: CLM-04
- **context_only** · Q13.txt:373–397,440–447 · Bad feedback can drive failures, and experiments were exclusively English. · Rules: CLM-04

Integration: references/claims-and-research.md

Limits: Historical models/tasks and evaluation choices; this skill does not reproduce the experiments or claim their effect sizes.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q14: Chain-of-Verification Reduces Hallucination in Large Language Models

Source: https://aclanthology.org/2024.findings-acl.212/

Read scope: Full accessible paper main body Q14-full.txt:1–561, including §3–5 and Limitations; appendices not comprehensively read.

Role: primary_research_with_scope_limits

- **adapt** · Q14-full.txt:96–246, sections 3.2–3.4 · Factored verification avoids conditioning answers on the original draft. · Rules: CLM-04
- **context_only** · Q14-full.txt:519–561, Limitations · CoVe reduces some directly stated errors but still hallucinates and does not evaluate every reasoning failure. · Rules: CLM-04

Integration: references/claims-and-research.md

Limits: Study did not explore external tool use; adding source checks here is an editorial adaptation, not a reproduced CoVe result.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q15: FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation

Source: https://aclanthology.org/2023.emnlp-main.741/

Read scope: Full main paper body Q15-full.txt:1–874; references and supplemental experiments not comprehensively read.

Role: primary_research_with_scope_limits

- **adapt** · Q15-full.txt:168–210, section 3.1 · Atomic support is source-relative and differs from overall quality. · Rules: CLM-01
- **adopt** · Q15-full.txt:802–872, Limitations · Precision omits recall and can miss crucial information; nuanced/conflicting domains challenge its assumptions. · Rules: CLM-01, CLM-04

Integration: references/claims-and-research.md

Limits: Experiments center biographies/Wikipedia; no general factuality percentage or Persian validation inferred. No metric implementation run.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q16: Preference Optimization for Review Question Generation Improves Writing Quality

Source: https://aclanthology.org/2026.findings-acl.1256/

Read scope: Paper main body Q16-full.txt:1–479, including training, rubric, evaluation, limitations and ethics; appendices not read as a whole.

Role: primary_research_with_scope_limits

- **adapt** · Q16-full.txt:146–188, section 3.2 · Question quality is defined through effort, specific evidence, and grounding. · Rules: CLM-04
- **context_only** · Q16-full.txt:352–460, sections 6–8 and Limitations · Reported improvements concern a preference-trained model, not a writing prompt. · Rules: CLM-04

Integration: references/claims-and-research.md

Limits: Narrow review-question corpus and limited domains; main text has dataset/model naming inconsistencies, so no quantitative result used as a binding rule.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q17: marketingskills: copywriting SKILL.md

Source: https://github.com/coreyhaines31/marketingskills/blob/main/skills/copywriting/SKILL.md

Read scope: Actual SKILL.md Q17.txt:1–339 and all three listed companion files read; no external linked source automatically accepted.

Role: primary_implementation_or_instruction

- **adapt** · Q17.txt:39–86, Diagnose the Situation First · Blank drafting, voice restoration, and point edits need different scope. · Rules: COPY-01
- **reject** · Q17.txt:115–153; Q17-frameworks.txt, Clarity Beats Cleverness (the metrics) · Large conversion and commercial lift percentages lack a verified primary experiment in these files. · Rules: COPY-06
- **adapt** · Q17.txt, Claims Must Be Supportable; Q17-tells.txt, Rewrite Rules · Support gaps can be made actionable without inventing proof. · Rules: COPY-04
- **adapt** · Q17-tells.txt, Structural Patterns and The Self-Check; Q17-transitions.txt, Best Practice Guidelines · Hard rhetorical bans and stock transition lists can themselves become rigid templates. · Rules: COPY-01

Integration: references/copy-and-sales.md

Limits: Instruction implementation, not independent effectiveness evidence. MIT file Q39 reviewed; synthesis avoids reproducing substantial skill text.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q18: marketingskills: copy-editing SKILL.md

Source: https://github.com/coreyhaines31/marketingskills/blob/main/skills/copy-editing/SKILL.md

Read scope: Complete actual SKILL Q18.txt:1–491 plus complete checklist companion; further refresh/plain-English references not read.

Role: primary_implementation_or_instruction

- **adapt** · Q18.txt:18–31; Q18-checklist.txt:5–27 · Editing mode and justified changes preserve voice and prevent unnecessary rewrites. · Rules: COPY-01
- **adapt** · Q18.txt, Sweep 4 and Sweep 5 · Specificity needs proof; example numbers are not transferable evidence. · Rules: COPY-04
- **reject** · Q18.txt, Expert Panel Scoring, Sweep 6 and Sweep 7 · Persona scores, heightened emotion, and zero-risk framing are not empirical publication gates. · Rules: COPY-06

Integration: references/copy-and-sales.md

Limits: Professional workflow, not measured conversion evidence; fixed score, word, and device caps not inherited.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q19: marketingskills: seo-audit SKILL.md

Source: https://github.com/coreyhaines31/marketingskills/blob/main/skills/seo-audit/SKILL.md

Read scope: Complete SKILL Q19.txt:1–497 and title-tags companion; other technical/localization references not read.

Role: primary_implementation_or_instruction

- **adapt** · Q19.txt, Output Format and Schema Markup Detection Limitation · Evidence-based findings should distinguish an observed extraction from rendered-site behavior. · Rules: WEB-05
- **reject** · Q19.txt, Tools Referenced; Q19-title-tags.txt, Default structure and Fixing low click-through · Retired tool listings and deterministic length/CTR diagnoses need correction. · Rules: WEB-03, WEB-05

Integration: references/web-seo.md

Limits: Technical heuristics in public skill are not primary SEO authority. Q35 resolves Mobile-Friendly Test conflict; Q31 resolves fixed-title-length conflict.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q20: ComposioHQ: content-research-writer SKILL.md

Source: https://github.com/ComposioHQ/awesome-claude-skills/blob/master/content-research-writer/SKILL.md

Read scope: Complete actual SKILL Q20.txt:1–538; linked external demonstrations and tools not executed.

Role: primary_implementation_or_instruction

- **adapt** · Q20.txt, Instructions 2, 5, 6 · Outlining, section feedback, and voice samples provide useful editorial checkpoints. · Rules: WEB-01, COPY-01
- **reject** · Q20.txt, Instructions 3 and Examples 2–4; Technical Tutorial Workflow · Illustrative statistics, quotations, and first-person hooks are not verified facts; tutorials need tested instructions. · Rules: WEB-06, TOL-05

Integration: references/web-seo.md, references/tools-and-evidence.md

Limits: Repository instruction, not independent evaluation. No substantial text reused and no license assertion made.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q21: K-Dense: scientific-writing SKILL.md

Source: https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-writing/SKILL.md

Read scope: Complete SKILL and five named essential guidance companions read; source_ledger was fetched but not read in full. Optional scripts/assets not executed or audited.

Role: primary_implementation_or_instruction

- **adapt** · Q21.txt, Evidence binding and Workflow 3–7; Q21-evidence_workflow.txt:46–110 · Source/claim records and consistency checks keep evidence separate from fluent drafting. · Rules: CLM-01, TOL-05
- **adopt** · Q21.txt, Workflow 11–12; Q21-reporting_guidelines.txt, Coverage record · A successful local audit does not certify scientific quality or official guideline adherence. · Rules: TOL-05
- **context_only** · Q21.txt, Citing Scientific Agent Skills · The source requests citation of its creators when materially used. · Rules: ACA-05

Integration: references/claims-and-research.md, references/tools-and-evidence.md, references/academic.md

Limits: Implementation’s metadata and MIT declaration do not prove effectiveness. Companion-specific human approval rules adapted to actual destination and task, not imposed universally.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q22: Research-Paper-Writing-Skills: research-paper-writing/SKILL.md

Source: https://github.com/Master-cai/Research-Paper-Writing-Skills/blob/main/research-paper-writing/SKILL.md

Read scope: Complete SKILL and four named companions read; other section/example banks not inspected.

Role: primary_implementation_or_instruction

- **adapt** · Q22.txt, Paragraph Clarity Check; Q22-does-my-writing-flow-source.txt, Reverse-outlining · Reverse outlining exposes mismatches between paragraph purpose and support. · Rules: ACA-04
- **adapt** · Q22-paper-review.txt, Critical Rule; Q22-experiments.txt, Experimental Rigor Checklist · Major claims should align with evaluation evidence and reported limitations. · Rules: ACA-03, ACA-04
- **context_only** · Q22-abstract.txt, Version templates; Q22-experiments.txt, Hard rules · Abstract templates, mandatory visuals, and layout rules target particular ML-style papers. · Rules: ACA-04

Integration: references/academic.md

Limits: ML/CV/NLP-oriented instruction; source and companion content are not universal acceptance standards. No source wording copied into modules.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q23: Copyhackers: Amazon review mining

Source: https://copyhackers.com/2014/10/amazon-review-mining/

Read scope: Complete article prose Q23.txt:5–95; linked video/books not inspected.

Role: professional_guidance_or_framework

- **adapt** · Q23.txt:18–28,47–71 · Review language can reveal concerns and alternatives for message research. · Rules: COPY-02
- **reject** · Q23.txt:24,40–44,94 · Covert recording and unattributed swiping are inappropriate defaults; case-study lift is not a universal effect. · Rules: COPY-02, COPY-06

Integration: references/copy-and-sales.md

Limits: Practitioner tutorial and anecdotal case, not representative market evidence or proof for another product.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q24: NN/G: Concise, Scannable, and Objective

Source: https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/

Read scope: Complete substantive study article Q24.txt:16–301: all three studies, methods/results, future research and conclusions; references/navigation excluded.

Role: primary_research_with_scope_limits

- **adapt** · Q24.txt:118–164 · The measurement study compares five versions using task, memory, and satisfaction measures. · Rules: WEB-01
- **context_only** · Q24.txt:230–301 · Reported percentage gains refer to a particular older usability setup, with further-study needs. · Rules: WEB-01, COPY-06

Integration: references/web-seo.md, references/copy-and-sales.md

Limits: Small 1997 website/task setting; it does not establish a universal text length or Persian effect.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q25: FTC Policy Statement Regarding Advertising Substantiation

Source: https://www.ftc.gov/legal-library/browse/ftc-policy-statement-regarding-advertising-substantiation

Read scope: Full policy body Q25.txt:33–58, including prior/post-claim evidence distinctions; footnotes read where present, no case-law expansion.

Role: official_documentation_or_announcement

- **adapt** · Q25.txt:35–40 · Objective advertising claims need a reasonable prior evidentiary basis; stated evidence strength also matters. · Rules: COPY-04
- **context_only** · Q25.txt:46–55 · Later evidence is not a simple substitute for prior substantiation in the policy. · Rules: COPY-04

Integration: references/copy-and-sales.md

Limits: US regulatory policy used as an editorial principle; no advice about Iranian law or comprehensive legal compliance.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q26: Elicit: Systematic Reviews workflow

Source: https://support.elicit.com/en/articles/14759154-systematic-reviews-in-elicit

Read scope: Complete workflow documentation Q26.txt:3–95; linked plan/usage pages not inspected.

Role: official_documentation_or_announcement

- **adapt** · Q26.txt:17–51,62–87 · Screening/extraction settings and figure access depend on workflow and plan. · Rules: TOL-01, TOL-03
- **adapt** · Q26.txt:8,55–59,84–95 · The vendor supplies source quotes and export workflows but also promotional saving/coverage claims. · Rules: TOL-03

Integration: references/tools-and-evidence.md

Limits: Documentation dated 2026-09-16; no account, paid feature, or independent accuracy test used.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q27: Scite Features

Source: https://scite.ai/features

Read scope: Complete features page Q27.txt:3–35; no account, classification model, or partner corpus audited.

Role: official_documentation_or_announcement

- **adapt** · Q27.txt:10–23 · Citation contexts are classified and searchable by supporting, contrasting, or mentioning labels. · Rules: TOL-01, TOL-04
- **context_only** · Q27.txt:5–9,15,27–31 · Vendor coverage figures and reliability wording are promotional and internally vary across the page. · Rules: TOL-04

Integration: references/tools-and-evidence.md

Limits: Feature documentation establishes claimed functions; no independent classifier accuracy or current corpus size established.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q28: Generating Attractive and Authentic Copywriting from Customer Reviews

Source: https://arxiv.org/abs/2404.13906

Read scope: Full paper main body Q28-full.txt:16–329, including methods, results, human comparison and limitations; appendices not read as a whole.

Role: primary_research_with_scope_limits

- **context_only** · Q28-full.txt:46–98,124–158 · A review-derived training pipeline separately optimizes attractiveness, fidelity, and information. · Rules: COPY-04
- **reject** · Q28-full.txt:292–306, section 6.2 · The paper uses detector probabilities to infer human-like quality. · Rules: COPY-06
- **adapt** · Q28-full.txt:326–329, Limitation and Potential Risks · The system still produces false information and requires actual reviews. · Rules: COPY-02, COPY-04

Integration: references/copy-and-sales.md

Limits: Restaurant reviews, short generated copy and subjective comparisons; no Persian validation or real purchase effect inferred.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q29: Using Elicit AI research assistant for data extraction in systematic reviews

Source: https://www.cambridge.org/core/journals/research-synthesis-methods/article/using-elicit-ai-research-assistant-for-data-extraction-in-systematic-reviews-a-feasibility-study-across-environmental-and-life-sciences/C97DAEC70C3173A260F0B12E729E7250

Read scope: Complete article main body Q29.txt:476–635, including protocol deviations, all results, discussion, limitations, declarations; supplemental data/code not executed or fully read.

Role: primary_research_with_scope_limits

- **adapt** · Q29.txt:537–555,566–588 · Prompt development and held-out tests differ; account/algorithm reruns can alter extraction. · Rules: TOL-03
- **adapt** · Q29.txt:603–618 · Ethics approval can be misread as registration; access restrictions and sample/time limits constrain conclusions. · Rules: TOL-03
- **context_only** · Q29.txt:554,608,617 · Figure limitations reflect the evaluated 2025 configuration and no direct timing comparison was available. · Rules: TOL-03

Integration: references/tools-and-evidence.md

Limits: Seven life/environmental reviews with small per-review test samples; later vendor documentation differs, and raw data reproduction was not performed.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q30: Google Search: Write high quality reviews

Source: https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews

Read scope: Complete review-writing guidance Q30.txt:32–73.

Role: official_documentation_or_announcement

- **adapt** · Q30.txt:41–58 · Reviews should explain decision criteria, original evidence, measurements, and tradeoffs. · Rules: WEB-04
- **adopt** · Q30.txt:63–73 · Best-for-purpose recommendations need grounds; usefulness is not a fixed-length target. · Rules: WEB-04

Integration: references/web-seo.md

Limits: Search publisher guidance, not proof that every review tactic improves rankings.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q31: Google Search: Influencing title links

Source: https://developers.google.com/search/docs/appearance/title-link

Read scope: Complete substantive title guidance Q31.txt:32–187.

Role: official_documentation_or_announcement

- **adopt** · Q31.txt:39–92 · Titles should be descriptive/distinct and match primary language; truncation depends on display width. · Rules: WEB-03
- **adopt** · Q31.txt:98–184 · Google can derive title links from multiple sources and repair mismatches. · Rules: WEB-03

Integration: references/web-seo.md

Limits: Current documentation checked; no query performance, ranking experiment, or exact character guarantee inferred.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q32: Google Scholar Search Help

Source: https://scholar.google.com/intl/en/scholar/help.html

Read scope: Discovery/access sections Q32.txt:20–80 and export/coverage Q32.txt:120–148; remaining account/alert sections not treated as fully reviewed.

Role: official_documentation_or_announcement

- **adopt** · Q32.txt:22–38,57–80 · Version links and citation chains help locate literature and accessible complete sources. · Rules: TOL-01, TOL-02
- **adapt** · Q32.txt:120–148 · Coverage is not guaranteed and includes preprints/abstracts; bulk export is limited. · Rules: TOL-01, TOL-02

Integration: references/tools-and-evidence.md

Limits: Tool guidance, not an appraisal system. No Scholar scraping or account operation performed.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q33: Mailchimp Content Style Guide: Voice and Tone

Source: https://styleguide.mailchimp.com/voice-and-tone/

Read scope: Complete voice/tone guide body Q33.txt:3–27.

Role: professional_guidance_or_framework

- **adapt** · Q33.txt:4–7,18–20 · Voice is relatively stable while tone adapts to situation and reader emotion. · Rules: COPY-01
- **context_only** · Q33.txt:9–17,21–27 · Dry humor and other defaults describe this brand. · Rules: COPY-01, COPY-07

Integration: references/copy-and-sales.md

Limits: Single-brand style guide, not a universal language law or effectiveness experiment.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q34: Online Experimentation at Microsoft

Source: https://www.microsoft.com/en-us/research/publication/online-experimentation-at-microsoft/

Read scope: Official Microsoft summary through web turn99view0:0–18; full exact public ThinkWeek author PDF Q34-author.txt main body:1–713 (sections 1–7); references not read as a complete corpus.

Role: primary_research_with_scope_limits

- **adapt** · Q34-author.txt, section 2 Controlled Experiments, lines 64–92 · Random assignment and a defined outcome isolate a change more credibly than preference. · Rules: COPY-06
- **adopt** · Q34-author.txt, section 5.2 Running Sequential (Uncontrolled) Experiments, lines 417–449 · Time effects can overwhelm the apparent before/after treatment difference. · Rules: COPY-06
- **context_only** · Q34-author.txt, sections 6.5–6.6 · Bots and integration defects can corrupt apparent results. · Rules: COPY-06

Integration: references/copy-and-sales.md

Limits: Historical platform case report, not a present copy formula or Persian-specific experiment. Exact original Microsoft fetch timed out; Stanford linked PDF returned 503.

Access: Original Microsoft page read via web; exact public paper legitimately recovered from author ExP site after linked Stanford PDF failed. Alternative proceedings PDF fetched separately but not counted as read.

## Q35: Google Mobile-Friendly Test retirement update

Source: https://developers.google.com/search/blog/2016/05/a-new-mobile-friendly-testing-tool

Read scope: Retirement notice and original announcement Q35.txt:31–47.

Role: official_documentation_or_announcement

- **adopt** · Q35.txt:31–34 · The notice explicitly retires Mobile-Friendly Test and Mobile Usability report in December 2023. · Rules: WEB-05
- **context_only** · Q35.txt:35–47 · The original 2016 launch description remains below the retirement update. · Rules: WEB-05

Integration: references/web-seo.md

Limits: Product-status evidence, not a general mobile-writing or ranking rule.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q36: Christensen Institute: Jobs to Be Done Theory

Source: https://www.christenseninstitute.org/theory/jobs-to-be-done/

Read scope: Definition and substantive explanatory/case/tool sections Q36.txt:3–74; linked videos/books not inspected.

Role: professional_guidance_or_framework

- **adapt** · Q36.txt:5–11,52–62 · JTBD examines progress in circumstances with practical, social, and emotional forces. · Rules: COPY-03
- **context_only** · Q36.txt:15–50 · Case narratives illustrate the framework but do not establish this product’s customers or conversion lift. · Rules: COPY-03

Integration: references/copy-and-sales.md

Limits: Originator framework and cases, not a universal causal marketing law.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q37: Strategyzer: Value Proposition Canvas

Source: https://www.strategyzer.com/library/the-value-proposition-canvas

Read scope: Complete substantive offer/canvas description Q37.txt:9–79; paid playbooks/templates not downloaded or read.

Role: professional_guidance_or_framework

- **adapt** · Q37.txt:40–48 · The canvas relates customer jobs/pains/gains to actual offer capabilities and calls for evidence-based testing. · Rules: COPY-03
- **context_only** · Q37.txt:26–38,64–68 · A template or AI-filled profile is only a starting point. · Rules: COPY-03

Integration: references/copy-and-sales.md

Limits: Framework creator’s product page; commercial claims and subscription benefits are not independent outcome evidence.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q38: Copyhackers: 7 copywriting research techniques

Source: https://copyhackers.com/2022/06/copywriting-research/

Read scope: Complete article prose Q38.txt:5–123; linked training/videos not inspected.

Role: professional_guidance_or_framework

- **adapt** · Q38.txt:23–65 · Interviews, surveys and reviews provide different views of customer language and objections. · Rules: COPY-02
- **adapt** · Q38.txt:66–119 · Analytics, behavioral observations, and competitor research need interpretation and organization. · Rules: COPY-02, COPY-06

Integration: references/copy-and-sales.md

Limits: Practitioner instruction, not proof all seven methods outperform alternatives in every market.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q39: marketingskills LICENSE

Source: https://github.com/coreyhaines31/marketingskills/blob/main/LICENSE

Read scope: Complete original MIT LICENSE Q39.txt:1–21.

Role: license_primary_document

- **adopt** · Q39.txt:1–14 · MIT grants reuse subject to retaining specified notices in substantial copies. · Rules: TOL-05
- **context_only** · Q39.txt:16–21 · The license disclaims warranties. · Rules: TOL-05

Integration: references/tools-and-evidence.md

Limits: License applies to that repository; it does not establish rights for unrelated sources. Original synthesis avoids substantial reproduction.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## Q40: ICMJE: Preparing a Manuscript

Source: https://www.icmje.org/recommendations/browse/manuscript-preparation/preparing-for-submission.html

Read scope: Complete substantive manuscript-preparation page Q40.txt:19–90; linked specialty policies and external guidelines not all read.

Role: professional_consensus_or_editorial_standard

- **adopt** · Q40.txt:19–23,35–38 · IMRaD suits many original reports; article type and venue control structure and abstract form. · Rules: ACA-04
- **adapt** · Q40.txt:41–58,59–70 · Methods/results, uncertainty, direct source support and reference verification are distinct responsibilities. · Rules: ACA-03, CLM-02, TOL-02

Integration: references/academic.md, references/claims-and-research.md

Limits: Biomedical editorial recommendations; not every reference style, format or requirement transfers to all fields.

Access: Original source retrieved anew; archived summary was used only to locate the source.

## R01: Style Over Substance: Evaluation Biases for Large Language Models

Source: https://aclanthology.org/2025.coling-main.21/

Read scope: Complete meaningful main paper body, including methods, results, discussion and limitations; text-extracted appendices A–D and figure captions. Bibliography not treated as substantive evidence; interface images were not visually inspected. Local evidence: skill-build-work/root-retrievals/R01-pdf.txt; SHA256 c4af2bc62f976aa0ff0ae69fec6cc067d637c048fa613687ad16f3bf04cd05a5; read line ranges 1-572, 774-961.

Role: primary_research_with_scope_limits; limited empirical motivation; operational procedures are original synthesis, not source-authored or efficacy-validated rules.

- **adapt** · skill-build-work/root-retrievals/R01-pdf.txt:L322-L374 (sha256 c4af2bc62f976aa0ff0ae69fec6cc067d637c048fa613687ad16f3bf04cd05a5) · Longer or fluent answers could outrank factually better alternatives in the controlled comparisons. · Rules: XQ-01, XQ-02
- **adapt** · skill-build-work/root-retrievals/R01-pdf.txt:L425-L538 (sha256 c4af2bc62f976aa0ff0ae69fec6cc067d637c048fa613687ad16f3bf04cd05a5) · Dimension-separated GPT-4 factuality judgments improved relative to compound judgments; crowd evaluation did not become reliably accurate. · Rules: XQ-01

Integration: references/quality-gates.md

Limits: Forty English question prompts; creative writing tasks were excluded. Older evaluated models and sampled expert judgments limit transfer to other genres, current models and Persian.

Access: Parent retrieval supplied actual ACL PDF and text. Reviewed substantive paper text, not only the landing abstract.

## R02: Help Me Write a Story: Evaluating LLMs’ Ability to Generate Writing Feedback

Source: https://aclanthology.org/2025.acl-long.1254/

Read scope: Complete meaningful main body including limitations and ethical considerations; extracted appendices A–G, prompts, annotation instructions, results tables and examples. Bibliography excluded from the substantive review; figures reviewed through extracted labels/captions. Local evidence: skill-build-work/root-retrievals/R02-pdf.txt; SHA256 27c283ed26539bca331e6f12978b5507db4aad5f8ae2ddda5b6b2bbc0e5b46da; read line ranges 1-687, 824-1416.

Role: primary_research_with_scope_limits; limited empirical motivation; operational procedures are original synthesis, not source-authored or efficacy-validated rules.

- **adapt** · skill-build-work/root-retrievals/R02-pdf.txt:L445-L486 (sha256 27c283ed26539bca331e6f12978b5507db4aad5f8ae2ddda5b6b2bbc0e5b46da) · Specific, plausible feedback often missed the issue judged most important. · Rules: XQ-03
- **adapt** · skill-build-work/root-retrievals/R02-pdf.txt:L528-L557 (sha256 27c283ed26539bca331e6f12978b5507db4aad5f8ae2ddda5b6b2bbc0e5b46da) · The direct spot-the-problem prompt underperformed list-based review; examples could bias feedback toward repetition. · Rules: XQ-03, XC-04

Integration: references/creative-and-editorial.md, references/quality-gates.md

Limits: Controlled short English stories with induced corruptions and single-turn feedback. Does not validate iterative critique or Persian performance.

Access: Parent retrieval supplied actual ACL PDF and text. Reviewed substantive paper text and extracted appendices.

## R03: Generative AI enhances individual creativity but reduces the collective diversity of novel content

Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC11244532/

Read scope: Complete meaningful main paper body including methods, results, discussion, limitations and ethics. Two-column PDF extraction interleaves some bibliography lines with closing methods; those references are not evidence. Separate supplementary file S1–S9 not retrieved or reviewed. Local evidence: skill-build-work/root-retrievals/R03-pdf.txt; SHA256 b988eb802ae667c608cd2498a08538587c80c6d11a82ad6f583b8b7fb243ec75; read line ranges 1-432.

Role: primary_research_with_scope_limits; limited empirical motivation; operational procedures are original synthesis, not source-authored or efficacy-validated rules.

- **context_only** · skill-build-work/root-retrievals/R03-pdf.txt:L119-L150 (sha256 b988eb802ae667c608cd2498a08538587c80c6d11a82ad6f583b8b7fb243ec75) · Third-party novelty and usefulness ratings improved in assisted conditions; writer self-ratings did not show corresponding differences. · Rules: XQ-04
- **adapt** · skill-build-work/root-retrievals/R03-pdf.txt:L170-L227 (sha256 b988eb802ae667c608cd2498a08538587c80c6d11a82ad6f583b8b7fb243ec75) · Assisted stories were more similar within condition and closer to supplied AI ideas. · Rules: XC-03

Integration: references/creative-and-editorial.md, references/quality-gates.md

Limits: Eight-sentence English fiction by ordinary recruited writers; fixed idea prompts and no free dialogue. Not a professional-writing or general creativity test.

Access: PMC browser check and science.org DOI were blocked; UCL /id/eprint PDF returned 403 natively. Legitimate UCL alternate /10195027/1 PDF downloaded successfully; its extracted body was read locally.

## R04: AI Suggestions Homogenize Writing Toward Western Styles and Diminish Cultural Nuances

Source: https://arxiv.org/abs/2409.11360

Read scope: Complete meaningful main paper body including methodology, findings, discussion and limitations; additional cultural-expression examples in appendix C. Bibliography and raw participant lists excluded from substantive review. HTML repeats some mathematical numbers; do not interpret duplicated digits as actual sample sizes. Local evidence: skill-build-work/root-retrievals/R04.txt; SHA256 f80134a5e1642806547f1d8c36d31a91b0cb66b887cac0369fe0dca19c449d9a; read line ranges 63-433, 971-1058.

Role: primary_research_with_scope_limits; limited empirical motivation; operational procedures are original synthesis, not source-authored or efficacy-validated rules.

- **adapt** · skill-build-work/root-retrievals/R04.txt:L341-L349 (sha256 f80134a5e1642806547f1d8c36d31a91b0cb66b887cac0369fe0dca19c449d9a) · Increased lexical variety coexisted with convergence toward the comparison cohort; more unique words did not mean more cultural range. · Rules: XC-03
- **adapt** · skill-build-work/root-retrievals/R04.txt:L395-L427 (sha256 f80134a5e1642806547f1d8c36d31a91b0cb66b887cac0369fe0dca19c449d9a) · Group-level cultural examples lost some specific practices; national labels and between-subject design limit individual or cross-language conclusions. · Rules: XC-01, XC-02

Integration: references/creative-and-editorial.md

Limits: English tasks with Indian and US groups; between-subject comparisons and broad national proxies. Cultural-preference shifts are tentative; no Persian measurement.

Access: Parent retrieval supplied author arXiv v3 HTML and text. Review used the saved actual paper body.

## R05: Introducing AI to an Online Petition Platform Changed Outputs but not Outcomes

Source: https://arxiv.org/abs/2511.13949

Read scope: Complete meaningful main paper body and complete supplementary methods narrative; selected supplementary captions 1–13. Remaining supplementary numeric tables and figure captions were not reviewed exhaustively. Main findings supported by body and method narrative, not an independent data reanalysis. Local evidence: skill-build-work/root-retrievals/R05.txt; SHA256 0db57f3c47b2487c46974f288a36a401eac4e3e2d1e15b314d0b27a815dc0b99; read line ranges 37-465, 971-1050, 1714-2067.

Role: primary_preprint_research; limited empirical motivation; operational procedures are original synthesis, not source-authored or efficacy-validated rules.

- **adapt** · skill-build-work/root-retrievals/R05.txt:L165-L193 (sha256 0db57f3c47b2487c46974f288a36a401eac4e3e2d1e15b314d0b27a815dc0b99) · Measured engagement did not improve despite higher independent text-quality and persuasiveness ratings. · Rules: XQ-04
- **context_only** · skill-build-work/root-retrievals/R05.txt:L261-L312 (sha256 0db57f3c47b2487c46974f288a36a401eac4e3e2d1e15b314d0b27a815dc0b99) · Substance, suspicion and ownership explanations were hypotheses; the design estimated platform access effects rather than individual use effects. · Rules: XQ-04

Integration: references/quality-gates.md

Limits: Preprint; platform-level access effect under quasi-experimental assumptions. Individual usage, amplification and causal mechanisms remain incompletely observed. Petition engagement is not sales.

Access: Parent retrieval supplied author arXiv v5 dated 2026-09-26. Full main text plus supplementary methods read from saved text; preprint status retained.

## R06: Does AI Homogenize Student Thinking? A Multi-Dimensional Analysis of Structural Convergence in AI-Augmented Essays

Source: https://arxiv.org/abs/2603.21228

Read scope: Complete meaningful main paper body, including construction prompts, measurement, all results, limitations and declarations. Bibliography excluded from substantive review; charts inspected through extracted text/captions, not visual rendering. Local evidence: skill-build-work/root-retrievals/R06.txt; SHA256 3abb1bc10ca5ffbedc0027080dc804fc136fa572f4e4c050f30df4d2ac7bc4b0; read line ranges 48-536.

Role: primary_preprint_research; limited empirical motivation; operational procedures are original synthesis, not source-authored or efficacy-validated rules.

- **adapt** · skill-build-work/root-retrievals/R06.txt:L310-L379 (sha256 3abb1bc10ca5ffbedc0027080dc804fc136fa572f4e4c050f30df4d2ac7bc4b0) · Structural variance changes differed by dimension; some pooled dimensions diversified while others converged. · Rules: XC-03
- **adapt** · skill-build-work/root-retrievals/R06.txt:L445-L528 (sha256 3abb1bc10ca5ffbedc0027080dc804fc136fa572f4e4c050f30df4d2ac7bc4b0) · Argument-depth variation depended on prompt condition, but augmentation was computational and scoring lacked reported human validation. · Rules: XC-04

Integration: references/creative-and-editorial.md

Limits: Preprint; simulated one-turn augmentation of two-topic English essays, with LLM-generated scores and no reported human validation of this scoring. Not direct evidence about cognition.

Access: Parent retrieval supplied author arXiv v1. Journal field is metadata, not independent evidence of publication or peer review; treated as preprint.

## R07: Delving into LLM-assisted writing in biomedical publications through excess vocabulary

Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12219543/

Read scope: Complete meaningful main paper body in author arXiv v5 alternate, including dataset, preprocessing, statistical analysis, results and limitations. Bibliography excluded. Published PMC page unavailable; exact text identity with the publisher version not independently compared. Local evidence: skill-build-work/root-retrievals/R07.txt; SHA256 9e91b6732354ede7580efcf5f039d093326b9b051f8e5fccfca79d64c213faa0; read line ranges 37-140.

Role: primary_research_with_scope_limits; limited empirical motivation; operational procedures are original synthesis, not source-authored or efficacy-validated rules.

- **context_only** · skill-build-work/root-retrievals/R07.txt:L62-L78 (sha256 9e91b6732354ede7580efcf5f039d093326b9b051f8e5fccfca79d64c213faa0) · Excess style-word frequencies supported aggregate lower-bound estimates, not exact total adoption rates. · Rules: XC-05
- **adapt** · skill-build-work/root-retrievals/R07.txt:L88-L100 (sha256 9e91b6732354ede7580efcf5f039d093326b9b051f8e5fccfca79d64c213faa0) · The method cannot identify individual abstracts or separate direct AI use from human adoption of preferred words. · Rules: XC-05

Integration: references/creative-and-editorial.md

Limits: Biomedical English corpus and counterfactual vocabulary assumptions. Indirect stylistic adoption, publication lags and editing differences complicate adoption interpretation; no individual attribution or Persian validation.

Access: PMC retrieval hit a browser-check wall; author arXiv v5 was accessible and supplied by parent retrieval. Reviewed actual alternate main text, not the blocked page.
