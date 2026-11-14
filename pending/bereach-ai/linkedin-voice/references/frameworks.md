# Reference frameworks for the voice card

How to use this library:
1. No framework is proven better than another. What is measured is the parts of a message: about them, their problem, short, one easy ask. Here, what is measured is how a person's style is carried (function words, length, punctuation) and copied (from real samples).
2. A framework orders the parts or names what to count. "Nothing is proven better" never justifies keeping a slot that fails the type's framework: each slot earns its place by what it does for the reader.

Evidence levels: **Measured** (a study with a method and a sample), **Survey** (self-reported), **Practice** (recognised practitioners or style guides, nobody measured it), **Vendor claim** (a seller's own numbers), **Untraced** (repeated, no source found).

Every example below uses one invented seller: field calibration software for water networks, writing to the persona "network manager".

## Summary

| Framework | Author | Feeds | Evidence |
|---|---|---|---|
| Voice and tone | Mailchimp Content Style Guide | Card split: voice (constant) vs tone per message type | Practice |
| Four dimensions of tone | Kate Moran, Nielsen Norman Group, 2016 | Tone per message type line | Measured (small effects) |
| Style lives in function words | Chung and Pennebaker 2007; Pennebaker 2011 | What the card counts (pronouns, punctuation) | Measured |
| Write from samples, not adjectives | Wang et al. 2025; Patel, Andrews, Callison-Burch 2022 | Step 1: 3 to 5 real messages, verbatim, varied | Measured |
| The reference message | Ghostwriting practice; Anthropic on canonical examples | Steps 2b and 3: their best message upgraded; the test message copies its voice, never a failing slot | Practice |
| Counting, not judging (stylometry) | Biber 1988; Eder 2015 and 2017 | Step 5: the countable draft check | Measured |
| Linguistic style matching | Niederhoffer and Pennebaker 2002; Ireland et al. 2011 | Reply tone; mirror the prospect once they answer | Measured (correlational) |
| Mirroring and accommodation | Chartrand and Bargh 1999; van Baaren et al. 2003; Giles | Switching to the prospect's address form and register | Measured (face to face) |
| Plain language | plainlanguage.gov (2011); ISO 24495-1:2023 | Never list (jargon), full sentences, one idea per sentence | Practice |
| Readability formulas | Flesch 1948; Kandel and Moles 1958 (French) | Plain, whole sentences; never a length target | Measured (readability of long text); Vendor claim (any reply lift) |
| Processing fluency | Oppenheimer 2006 | Short, common words over impressive ones | Measured (one study) |
| T/V distinction (tu/vous) | Brown and Gilman 1960; Clyne, Norrby, Warren 2009 | Address form field | Measured (sociolinguistic, not replies) |
| Formal address for competence | Lenoir 2015 (doctoral thesis) | Default formal form for a first contact | Measured (consumers) |

## The frameworks

### Voice and tone (Mailchimp, Content Style Guide, voice and tone section)
- What it says: "You have the same voice all the time, but your tone changes" with the message and the reader's state.
- On LinkedIn: the card's split (SKILL, top). Size and the opening line are craft, from the type's framework.
- Example: voice "short, plain, no exclamation mark"; tone of a follow-up "lighter, the way out offered".
- Use when / not when: always for the card's layout; not as a reason to invent a tone the samples do not show.
- Evidence: Practice. A style guide, nothing measured. (Often credited to Nielsen Norman Group; the split is Mailchimp's.)

### Four dimensions of tone (Kate Moran, Nielsen Norman Group, "The Four Dimensions of Tone of Voice", 2016)
- What it says: tone varies on four scales: formal/casual, serious/funny, respectful/irreverent, matter-of-fact/enthusiastic.
- On LinkedIn: the words for the "Tone per message type" line; place each type on the scales the samples show.
- Example: "First message: formal, serious, respectful, matter-of-fact. Reply to a network manager who wrote casually: one step more casual."
- Use when / not when: to name a tone the samples show.
- Evidence: Measured, in Moran's companion article "The Impact of Tone of Voice on Users' Brand Perception" (NN/g, 2016): 100 raters, differences of 0.3 to 0.7 on a 5-point scale (small). The four dimensions article only defines the scales.

### Style lives in function words (Chung and Pennebaker, "The Psychological Functions of Function Words", 2007; Pennebaker, *The Secret Life of Pronouns*, 2011)
- What it says: a person's style shows in small words (pronouns, articles, prepositions), sentence length and punctuation, not in topic words.
- On LinkedIn: every field on the card is countable (I / we / you habit, contractions, ! and ?). Nothing about what they sell.
- Example: "Pronoun habit: you-first ('your network', 'your meters'), I only in the trade clause."
- Use when / not when: when filling the card.
- Evidence: Measured. Decades of word-count studies; not proof of authorship alone.

### Write from samples, not adjectives (Wang, Tripto, Park, Li, Zhou, "Catch Me If You Can? Not Yet", EMNLP Findings 2025; Patel, Andrews, Callison-Burch, "Low-Resource Authorship Style Transfer", 2022)
- What it says: a model imitates an everyday writer best from a few real examples; 5 samples worked, 2 to 10 changed little; samples picked for the same topic made imitation worse.
- On LinkedIn: Step 1's samples, verbatim on the card.
- Example: three messages to a network manager, a water utility director and a former colleague, rather than three on leak detection.
- Use when / not when: always.
- Evidence: Measured. 400+ authors; email imitated far better than blogs.

### The reference message (ghostwriting practice; Anthropic, "Effective context engineering for AI agents", on diverse canonical examples)
- What it says: people recognise their voice better than they describe it; one real example the writer copies beats a list of rules.
- On LinkedIn: the reference message (SKILL Step 1): their words and identity wherever a slot passes, every failing slot rewritten.
- Example: theirs "Hi Anne, thanks for connecting. Your team recalibrates the sector meters each spring. Hope we get to work together." Reference after the upgrade: "Hi Anne, your team recalibrates the sector meters each spring. I build the software for that. Is it still done by hand?" (no offer made yet: a question on her fact, never an invented one).
- Use when / not when: always.
- Evidence: Practice. Practitioners and model-vendor guidance, not a controlled test.

### Counting, not judging (stylometry: Douglas Biber, *Variation across Speech and Writing*, 1988; Eder, "Does size matter?", 2015, and "Short Samples in Authorship Attribution", 2017)
- What it says: style is measured by counted features; identifying a writer needs thousands of words, imitating needs far fewer.
- On LinkedIn: Step 5's check.
- Use when / not when: every draft; never replace it with a model's "sounds like them" opinion.
- Evidence: Measured. Stylometry research; model judges over-call differences.

### Linguistic style matching (Niederhoffer and Pennebaker, "Linguistic Style Matching in Social Interaction", Journal of Language and Social Psychology, 2002; Ireland et al., "Language Style Matching Predicts Relationship Initiation and Stability", Psychological Science, 2011)
- What it says: people in conversation converge on each other's function words; pairs that match more were more likely to want to meet again and to stay together.
- On LinkedIn: once a prospect answers, the Reply tone follows their length, register and address form, inside the user's voice.
- Example: the network manager answers in two short lines, no greeting: the reply drops to two lines too.
- Use when / not when: replies and later messages; not a first message (there is nothing to match yet).
- Evidence: Measured. Correlational, dating and couples, not sales.

### Mirroring and accommodation (Chartrand and Bargh, "The Chameleon Effect", 1999; van Baaren et al., "Mimicry for Money", 2003; Howard Giles, communication accommodation theory, from the 1970s)
- What it says: people like and reward those who match them (a waitress repeating orders got larger tips); speakers shift toward the person they want to be close to.
- On LinkedIn: the address form switches to the prospect's once they write (tu after their tu); a tu in a thread stays.
- Example: the network manager writes "tu" first: the reply and every follow-up use tu.
- Use when / not when: after they answer; never copy their words back as a trick, never mirror a register the user would never use.
- Evidence: Measured. Face-to-face studies; not tested in written outreach.

### Plain language (plainlanguage.gov, Federal Plain Language Guidelines, 2011, under the Plain Writing Act of 2010; ISO 24495-1:2023, Plain language, governing principles)
- What it says: readers find what they need, understand it and can use it: short sentences, everyday words, the reader first.
- On LinkedIn: jargon goes on the Never list; the check keeps full sentences, one idea each; a doubt in the language is rewritten.
- Example: "We optimise hydraulic asset performance" becomes "Your meters drift. I build the software that recalibrates them in the field."
- Use when / not when: every message; it never overrides a technical word the user's own samples use with their peers.
- Evidence: Practice. Government guidance and an ISO standard, not reply data.

### Readability formulas (Rudolf Flesch, "A New Readability Yardstick", Journal of Applied Psychology, 1948; Kandel and Moles, French adaptation, 1958)
- What it says: shorter sentences and shorter words read more easily; scores built on those two counts.
- On LinkedIn: plain words in whole sentences; never a reason to clip a sentence or drop its verb. No score is shown to the user.
- Example: two whole sentences of 12 words each rather than one run-on of 24.
- Use when / not when: as a count, never a target score (built on long text).
- Evidence: Measured (readability of long text); Vendor claim (any reply lift). The formula was validated on long text; reply lifts for low reading level come from vendor data.

### Processing fluency (Daniel Oppenheimer, "Consequences of Erudite Vernacular Utilized Irrespective of Necessity", 2006)
- What it says: needlessly complex words made writers seem less intelligent, not more.
- On LinkedIn: common words over impressive ones; "use" over "leverage", in every language.
- Use when / not when: every draft.
- Evidence: Measured. One paper, no replication found.

### T/V distinction, tu and vous (Brown and Gilman, "The Pronouns of Power and Solidarity", 1960; Clyne, Norrby, Warren, *Language and Human Relations*, Cambridge University Press, 2009)
- What it says: the formal and informal "you" mark power and solidarity; in French workplaces vous is the default with strangers and in hierarchy, tu spreads with informality.
- On LinkedIn: the address form field (SKILL Step 2).
- Use when / not when: every language with a formal "you" (French, German, Spanish, Italian); not English.
- Evidence: Measured (sociolinguistic surveys). No study measures replies by tu against vous.
- French defaults by reader, when the samples do not decide (Practice: OQLF, the Swiss business guide, Waalaxy, Overloop, Origami; nobody measured it):
  - Start-ups, tech and SaaS teams, agencies, creative trades: vous + first name; tu if the reader writes tu or the user always does.
  - Corporate tech, industry, construction, finance, legal, accounting, consulting partners, real estate investors: vous.
  - Real estate agents and brokers: vous in message 1, then mirror.
  - Public sector, hospitals, education, health professionals: vous, always.
  - Quebec: vous in message 1, switch at the first tu. Belgium and Romandie: vous, wait for them to offer tu.
  - Across all: mirror their tu, and go back to vous at once if they answer vous; "Bonjour Prénom, ... vous" is the normal form; never "Salut ... vous"; tu never licenses hype; a tu in a sequence is permanent.
  - Native French (Practice): the reason in sentence one, never "J'espère que vous allez bien" or "Je me permets"; a space before ? ! : ;; "12 000", "3,5 %". The card's own greeting and sign-off still win.

### Formal address signals competence (Anne-Sophie Lenoir, *Are You Talking to Me? Addressing Consumers in a Globalised World*, ERIM doctoral thesis, 2015)
- What it says: in six consumer experiments, informal address suited "warm" brands and formal address suited "competent" ones.
- On LinkedIn: a stranger selling expertise is the "competent" case: the formal form stays the default when the samples are silent.
- Example: calibration software sold to a public water utility: vous, "Bonjour" capitalised.
- Use when / not when: when the samples do not decide; never over the user's own habit.
- Evidence: Measured. Consumer experiments, not B2B messages.

## Further reading

- Mailchimp, *Content Style Guide*, Voice and tone. https://styleguide.mailchimp.com/voice-and-tone/
- Kate Moran, "The Four Dimensions of Tone of Voice", Nielsen Norman Group, 2016. https://www.nngroup.com/articles/tone-of-voice-dimensions/
- Kate Moran, "The Impact of Tone of Voice on Users' Brand Perception", Nielsen Norman Group, 2016. https://www.nngroup.com/articles/tone-voice-users/
- James W. Pennebaker, *The Secret Life of Pronouns*, Bloomsbury, 2011.
- Cindy Chung and James W. Pennebaker, "The Psychological Functions of Function Words", 2007.
- Wang, Tripto, Park, Li, Zhou, "Catch Me If You Can? Not Yet: LLMs Still Struggle to Imitate the Implicit Writing Styles of Everyday Authors", EMNLP Findings, 2025. https://arxiv.org/abs/2509.14543
- Patel, Andrews, Callison-Burch, "Low-Resource Authorship Style Transfer: Can Non-Famous Authors Be Imitated?", 2022. https://arxiv.org/abs/2212.08986
- Anthropic, "Effective context engineering for AI agents". https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Maciej Eder, "Does size matter? Authorship attribution, small samples, big problem", Digital Scholarship in the Humanities, 2015.
- Maciej Eder, "Short Samples in Authorship Attribution: A New Approach", Digital Humanities, 2017.
- Douglas Biber, *Variation across Speech and Writing*, Cambridge University Press, 1988.
- Kate Niederhoffer and James W. Pennebaker, "Linguistic Style Matching in Social Interaction", Journal of Language and Social Psychology, 2002.
- Ireland, Slatcher, Eastwick, Scissors, Finkel, Pennebaker, "Language Style Matching Predicts Relationship Initiation and Stability", Psychological Science, 2011.
- Tanya Chartrand and John Bargh, "The Chameleon Effect", Journal of Personality and Social Psychology, 1999.
- van Baaren, Holland, Steenaert, van Knippenberg, "Mimicry for Money: Behavioral Consequences of Imitation", Journal of Experimental Social Psychology, 2003.
- Federal Plain Language Guidelines, 2011. https://www.plainlanguage.gov/guidelines/
- ISO 24495-1:2023, *Plain language, Part 1: Governing principles and guidelines*. https://www.iso.org/standard/78907.html
- Rudolf Flesch, "A New Readability Yardstick", Journal of Applied Psychology, 1948.
- Daniel Oppenheimer, "Consequences of Erudite Vernacular Utilized Irrespective of Necessity", Applied Cognitive Psychology, 2006.
- Roger Brown and Albert Gilman, "The Pronouns of Power and Solidarity", 1960.
- Michael Clyne, Catrin Norrby, Jane Warren, *Language and Human Relations: Styles of Address in Contemporary Language*, Cambridge University Press, 2009.
- Office québécois de la langue française (OQLF), Banque de dépannage linguistique, vouvoiement et tutoiement.
- Anne-Sophie Lenoir, *Are You Talking to Me? Addressing Consumers in a Globalised World*, Erasmus Research Institute of Management (ERIM), 2015. https://repub.eur.nl/pub/79036/Resume-en-francais.pdf
