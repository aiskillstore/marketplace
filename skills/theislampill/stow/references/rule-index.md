# STOW rule index

Generated from `skills/stow/rules/registry.yaml` by `tools/gen_rule_index.py`. Do not edit by hand.

Primary records: 65

For a single-rule lookup, prefer `python runtime/query_rules.py <ID>` when execution is available. Otherwise search this index for the id, then search `registry.yaml` for the sentinel line `# === <ID> ===` and read only that record block up to the next sentinel, then open the cited corpus module and read only the anchored section. A `corpus_ref` fragment (`#STOW-XXX-NNN`) is a section anchor, not a file: drop the fragment to open the module, then read from the matching `## STOW-` heading to the next heading. A host with search or offset reads locates each span and reads only it. Full-registry ingestion is for complete audits only.

| id | title | category | precedence |
| --- | --- | --- | --- |
| STOW-WRD-001 | Use dictionary-approved words; admit technical nouns and technical verbs only under a defined category supplied by project authority, and prefer an approved dictionary verb when one exists. | words | profile |
| STOW-WRD-002 | Use each approved word only in its dictionary-specified part of speech and listed forms; a listed past participle can act as an adjective. | words | profile |
| STOW-WRD-003 | Use approved words only with their dictionary-approved, often restricted, meanings. | words | profile |
| STOW-WRD-007 | Do not use a technical noun as a verb; keep it a noun or adjectival modifier. | words | profile |
| STOW-WRD-008 | Prefer the technical noun already approved by your company, industry, or subject field. | words | profile |
| STOW-WRD-010 | Do not use regional, slang, or jargon words as technical nouns. | words | profile |
| STOW-WRD-011 | Use one technical noun consistently for one item, preserve key words and key phrases that organize the logic, and reuse recurring wording for the same context. | words | profile |
| STOW-WRD-014 | Use American English spelling unless another official directive overrides; do not change quoted-text spelling. | words | profile |
| STOW-MWN-001 | Keep multi-word nouns to a maximum of three words and keep coined terms short and easy; for a longer approved noun, write it in full first, then restructure it or use a declared short form, approved abbreviation, or clear hyphenation while you preserve enough identity-bearing words to refer to the same item. | multiword-nouns | profile |
| STOW-VRB-002 | Use only the infinitive, imperative, simple present, simple past, simple future, and listed past participle; do not use perfect, progressive, or other complex constructions. | verbs | profile |
| STOW-VRB-005 | Use an -ing word only as a technical noun or as a modifier inside a technical noun. | verbs | profile |
| STOW-VRB-006 | Use active voice; passive is allowed only in descriptive writing when the agent is unknown. | verbs | profile |
| STOW-VRB-007 | Describe an action with an approved verb, not a nominalization; technical verbs stay verbs, except that a listed past participle can act as an adjective. | verbs | profile |
| STOW-SEN-002 | Do not omit words or use contractions; write every word in full. | sentences | profile |
| STOW-SEN-003 | Break complex text into a vertical list with the prescribed layout. | sentences | profile |
| STOW-SEN-004 | Use approved connecting words and phrases to link related sentences. | sentences | profile |
| STOW-SEN-005 | Use articles and demonstratives before nouns where grammatically correct. | sentences | profile |
| STOW-PRC-001 | Limit each procedural sentence to a maximum of twenty words. | procedures | profile |
| STOW-PRC-002 | Write only one instruction per sentence unless actions occur at the same time. | procedures | profile |
| STOW-PRC-003 | Write instructions in the imperative command form. | procedures | profile |
| STOW-PRC-004 | State a required condition first and separate it from the command with a comma. | procedures | profile |
| STOW-PRC-005 | A note in a controlled procedure gives information and does not introduce an action. | procedures | profile |
| STOW-DSC-001 | Introduce information gradually, one subject per sentence. | descriptions | profile |
| STOW-DSC-003 | Limit each descriptive sentence to a maximum of twenty-five words. | descriptions | profile |
| STOW-DSC-004 | Group related information into paragraphs, each led by a topic sentence. | descriptions | profile |
| STOW-DSC-006 | Keep every paragraph to a maximum of six sentences. | descriptions | profile |
| STOW-SAF-001 | Label each safety instruction with a word that identifies the level of risk. | safety | system |
| STOW-SAF-002 | Begin a safety instruction with a clear, accurate command or condition. | safety | system |
| STOW-SAF-003 | State the risk or the possible result of not obeying the safety instruction. | safety | system |
| STOW-PCT-001 | Do not use the semicolon; write two separate sentences instead. | punctuation | profile |
| STOW-PCT-003 | Use parentheses only for references, item identifiers, step identifiers, abbreviations, singular/plural forms, explanations, or alternatives. | punctuation | profile |
| STOW-PCT-004 | In a vertical list, a colon counts as a period for word count and ends a sentence. | punctuation | profile |
| STOW-PCT-005 | Parenthetical text counts as one word in the host sentence. | punctuation | profile |
| STOW-PCT-006 | Count a number, number with unit, abbreviation, identifier, quoted text, title or label, or proper name as one word. | punctuation | profile |
| STOW-PCT-007 | Use hyphens only between directly related words that operate as one unit; a hyphenated group counts as one word. | punctuation | profile |
| STOW-STY-001 | When a word-for-word replacement is insufficient, rewrite the sentence while preserving the meaning. | style | profile |
| STOW-STY-003 | Do not combine approved words into unlisted phrasal verbs. | style | profile |
| STOW-GEN-002 | Rewrite a with phrase only when it has two plausible attachments. | general | profile |
| STOW-GEN-003 | Use only approved pronouns; replace an ambiguous pronoun with its noun. | general | profile |
| STOW-GEN-005 | Confirm a possible false friend against a supplied source-language meaning. | general | profile |
| STOW-GEN-006 | Avoid Latin abbreviations; use English words instead. | general | profile |
| STOW-GEN-007 | When gender is unknown or irrelevant, name the role or use an inclusive reference. | general | profile |
| STOW-ACT-001 | Action-first response opening | action-shaping | presentation |
| STOW-ACT-002 | Number ordered multi-step work as bounded, task-complete actions | action-shaping | presentation |
| STOW-ACT-004 | Defer secondary issues without dropping them | action-shaping | presentation |
| STOW-ACT-005 | Surface changed progress and remaining state | action-shaping | presentation |
| STOW-ACT-006 | Concrete effort estimates | action-shaping | presentation |
| STOW-ACT-007 | Surface completed outcomes | action-shaping | presentation |
| STOW-ACT-008 | Neutral error reporting | action-shaping | presentation |
| STOW-ACT-011 | Lists, not tables, for action sequences | action-shaping | presentation |
| STOW-PRO-001 | Use em dashes only under an explicit style contract | prose-integrity | presentation |
| STOW-PRO-002 | Require attributable numbers | prose-integrity | presentation |
| STOW-PRO-005 | End claims on a concrete detail | prose-integrity | presentation |
| STOW-PRO-006 | Functionless semantic repetition | prose-integrity | presentation |
| STOW-PRO-007 | Avoid mechanical repetition that obscures function. | prose-integrity | presentation |
| STOW-PRO-009 | Use urgency or intensified emphasis only when a decision-relevant reason is stated. | prose-integrity | presentation |
| STOW-PRO-011 | Remove framing or process language only when it adds no information or decision value. | prose-integrity | presentation |
| STOW-PRO-013 | Evidence-grounded requested voice | prose-integrity | presentation |
| STOW-PRO-015 | Grounded uncertainty | prose-integrity | presentation |
| STOW-PRO-016 | Concrete, descriptive headings | prose-integrity | presentation |
| STOW-PRO-017 | No fabricated scenarios | prose-integrity | presentation |
| STOW-PRO-018 | No fabricated history | prose-integrity | presentation |
| STOW-PRO-019 | No fabricated attributions | prose-integrity | presentation |
| STOW-PRO-020 | Review formulaic lexical patterns | prose-integrity | presentation |
| STOW-PRO-023 | Quote sources accurately | prose-integrity | presentation |
