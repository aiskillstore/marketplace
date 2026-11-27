# Research Basis

Verified on 2026-07-15. Re-check provider documentation after schema errors or endpoint changes.

## Text detection

- OpenAI retired its classifier for low accuracy. Its published evaluation reported 26% true positives, 9% false positives, and poor reliability below 1,000 characters: https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/
- Stanford HAI summarized evidence of detector bias against non-native English writers, including 61.22% of tested TOEFL essays being classified as AI-generated: https://hai.stanford.edu/news/ai-detectors-biased-against-non-native-english-writers
- Pudasaini et al. found substantial real-world unreliability under new domains, models, and evasion tactics: https://aclanthology.org/2025.genaidetect-1.4/
- GPTZero's 2026 vendor-authored paper describes a supervised hierarchical multi-task architecture: Human/AI/Mixed document classes, binary sentence predictions, large continually collected human/AI corpora, adversarial augmentation, and proprietary architecture/hyperparameters: https://arxiv.org/abs/2602.13042
- GPTZero's public methodology explains its historical use of perplexity and burstiness while stating that the current product has moved to a multilayered learned system with sentence-level classification: https://gptzero.me/news/how-ai-detectors-work/
- Chakraborty et al. analyze fundamental possibilities and limits of AI-text detection, including dependence on sample length and distributional separation: https://arxiv.org/abs/2304.04736
- Sadasivan et al. show that paraphrasing attacks can sharply erode detector performance and argue that reliable detection is fundamentally difficult: https://arxiv.org/abs/2303.11156
- RAID evaluates detectors across more than six million generations, 11 models, eight domains, and 11 adversarial attacks, showing substantial out-of-domain and attack brittleness: https://aclanthology.org/2024.acl-long.674/
- M4GT-Bench evaluates multilingual, multidomain, and mixed-source text and finds that strong results often depend on matching training domains and generators: https://aclanthology.org/2024.acl-long.218/

## Image provenance and detection

- C2PA defines signed provenance and explicitly states that Content Credentials do not make value judgments about truth: https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html
- IPTC distinguishes “Created using Generative AI” (`trainedAlgorithmicMedia`), “Edited using Generative AI” (`compositeWithTrainedAlgorithmicMedia`), and non-generative “Algorithmically-altered media” (`algorithmicallyEnhanced`): https://cv.iptc.org/newscodes/digitalsourcetype/
- The official Python SDK reads and validates C2PA manifests: https://opensource.contentauthenticity.org/docs/c2pa-python/
- Hive documents a 0.9 starting threshold for AI-generated images and advises holistic interpretation with C2PA: https://docs.thehive.ai/docs/ai-image-and-video-detection

## Human reception

- A 680-participant social-media experiment found that AI assistance can increase participation while decreasing perceived quality and authenticity in some conditions; it recommends disclosure, personalization, and context sensitivity: https://www.nature.com/articles/s41598-026-40110-8
- Other work found that AI-generated content can be perceived as similarly credible and sometimes clearer or more engaging, so algorithm aversion must not be assumed: https://arxiv.org/abs/2309.02524

## Editorial style heuristics

- Humanizer-zh catalogs 24 editorial patterns and a 50-point post-rewrite quality rubric. It is a prompt-based editing guide, not a statistical classifier and does not publish a calibrated AI probability, validation set, precision, or recall: https://github.com/op7418/Humanizer-zh
- Its pattern basis is Wikipedia's community observation guide. These observations are useful for explainable review but overlap with satire, marketing, academic, bureaucratic, and intentionally formulaic human writing: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- A verified Weibo study compared 463,382 human and LLM-Bot comments and found group-level differences in length, stop-word use, error variance, punctuation regularity, emotional vocabulary, platform markers, and assertive language. Its stylometric classifier reached F1 91.8% in-domain, but voluntary and personalized bot comments were harder: https://aclanthology.org/2025.ccl-1.64/
- A disclosed GPT-2 Reddit community and TweepFake show that older generators often expose global inconsistency and repetition, while transformer-generated short tweets can still be difficult to distinguish: https://www.reddit.com/r/SubSimulatorGPT2/comments/btfhks/what_is_rsubsimulatorgpt2/ and https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0251415

## Product interpretation

The skill therefore:

- Treats provenance as stronger than detector inference.
- Refuses strong standalone judgments on short text.
- Uses an offline Chinese predictability/rhythm proxy plus sentence/document aggregation only as a descriptive aid; it does not call GPTZero, produce an authorship likelihood, or claim GPTZero-equivalent accuracy.
- Calls document self-surprisal, compression, and repetition “proxies,” never true language-model perplexity.
- Keeps Human Reception independent from origin detection.
- Reports Chinese AI-style pattern density as a separate, non-provenance assessment.
- Uses stance-based reactions rather than demographic personas.
- Labels reader reactions as estimates requiring real-world validation.
- Requires a provenance-backed, group-leakage-controlled, frozen blind evaluation before any future local model can be promoted to a release-grade authorship classifier.
