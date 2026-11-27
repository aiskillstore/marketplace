# Findings from Disclosed AI Social Content

## Scope

Use these observations when reviewing social-media text. They come from disclosed bot communities, verified LLM-Bot datasets, controlled experiments, and platform investigations—not from accusing ordinary accounts based on appearance.

## Sample groups reviewed

- Reddit's `r/SubSimulatorGPT2`, where all ordinary posts and comments are disclosed as fine-tuned GPT-2 output: https://www.reddit.com/r/SubSimulatorGPT2/comments/btfhks/what_is_rsubsimulatorgpt2/
- TweepFake, 25,572 real tweets split evenly between disclosed generation bots and the human accounts they imitated: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0251415
- A 463,382-comment Weibo dataset built from verified LLM-Bot and human interactions: https://aclanthology.org/2025.ccl-1.64/
- OpenAI investigations where generated comments, articles, account bios, translations, and replies were posted across X, Telegram, Facebook, Instagram, Medium, 9GAG, and other sites: https://openai.com/index/disrupting-deceptive-uses-of-ai-by-covert-influence-operations/
- A 680-participant controlled social discussion experiment comparing unassisted and AI-assisted participation: https://www.nature.com/articles/s41598-026-40110-8

## Recurring patterns

### Older or weak generators

- Local fluency with global incoherence: adjacent sentences sound plausible while entities, roles, chronology, or causal relationships drift.
- Circular restatement: the same noun phrase or conclusion returns with little added information.
- Contradictory action chains: a character repeatedly reverses what they did or wanted without narrative motivation.
- Broken references: generated links, titles, named entities, or metadata do not match the surrounding claim.

Treat these as strong style anomalies only when the contradiction is present in the supplied text. Humor, surreal fiction, dreams, and word games are major confounds.

### Modern Chinese social comments

The verified Weibo comparison found group-level tendencies, not universal rules:

- AI comments were generally longer, while both groups remained short-form.
- AI comments used more stop words and more consistently normative syntax.
- AI comments had lower and less variable spelling/grammar error rates.
- Their punctuation frequency was more regular; human comments clustered around no punctuation, ordinary punctuation, and excessive punctuation.
- AI comments overused affection-related language and showed important happiness/surprise signals.
- Human comments used more platform interaction elements such as user mentions and emoji.
- AI comments favored assertive verbs and absolute adverbs such as “think,” “absolutely,” “definitely,” and “certainly.”
- Prompt-triggered bot replies were more structurally uniform than voluntary bot comments; personalized blogger assistants were harder to detect.

Do not turn an individual post's clean grammar, missing emoji, or positive tone into a verdict. Combine several features and explain platform and genre alternatives.

### Modern long-form and expert review

Experienced LLM users reviewing 300 English non-fiction articles relied on vocabulary plus higher-level formality, originality, and clarity. This supports holistic review rather than keyword counting: https://aclanthology.org/2025.acl-long.267/

For social posts, inspect:

- whether every paragraph performs the same setup-development-summary function;
- whether examples are specific but strangely interchangeable;
- whether the post explains an obvious metaphor, joke, or conclusion after it has landed;
- whether emotional language is polished but detached from concrete stakes;
- whether the text responds to the actual thread or merely restates the topic safely;
- whether a supposed personal experience contains sensory, temporal, relational, or decision details that remain mutually consistent.

These remain style observations. A prompt can request irregularity, and a human editor can add or remove any of them.

## Account and campaign context

Platform investigations show that AI material is commonly mixed with manual posts, copied memes, translation, and human editing. Do not classify an entire account from one asset.

Higher-value contextual signals include:

- pasted refusal or assistant-interface language;
- many near-simultaneous replies with the same rhetorical function;
- self-replies used to manufacture engagement;
- repeated cross-language or cross-platform variants;
- visible author disclosure, bot labeling, or generation provenance.

These signals require page or account context. They are not available from pasted text alone.

## Human reception

In the controlled social experiment, AI tools increased participation volume but several conditions reduced perceived informativeness, quality, and authenticity and increased dislikes. Participants described some content as generic, impersonal, or overly formal. However, a control-group false-suspicion baseline remained: 13.8% of unassisted participants were believed by others to have used AI.

Therefore:

- genericness can create real reader friction;
- reader suspicion is not authorship evidence;
- disclosure and platform context affect trust;
- suggestions or light editing may be received differently from wholesale generated comments.

## Detector cautions

- TweepFake found transformer-generated short tweets harder to identify than older RNN output.
- A 2026 large-scale social-web audit found considerable false positives and political-distribution bias in current detectors: https://ojs.aaai.org/index.php/ICWSM/article/view/42660
- Cross-platform and cross-model generalization remains a central weakness; use corroboration and retain uncertainty.
