# Lexical tells (a backstop, not the main event)

The structural tells in `structures.md` matter more than any wordlist. Vocabulary
is the easy 20%: a word swap does not fix sloppy rhythm, and clean rhythm
survives the occasional flagged word. Use this list as a deterministic backstop
(the kind a Vale `reject.txt` enforces in CI), not as the definition of slop.

## Words and phrases that signal the register

Reach-for-grandeur nouns and adjectives:

- delve, tapestry, realm, landscape, ecosystem, world (as in "in today's world")
- seamless, seamlessly, effortless, robust, powerful, cutting-edge,
  state-of-the-art, best-in-class, next-generation
- game-changer, revolutionize, unlock, supercharge, elevate, empower
- bespoke, curated, crafted, meticulous, holistic

Filler intensifiers and hedges that pad without adding:

- truly, simply, easily, quickly, incredibly, remarkably, notably, ultimately
- "it is worth noting that", "it is important to remember", "needless to say"
- "at the end of the day", "when it comes to", "in order to" (usually just "to")

Connective scaffolding used on autopilot:

- moreover, furthermore, additionally, that being said, with that said
- "whether you are X or Y" (the fake-inclusive opener)
- "not only ... but also" (often a manufactured antithesis in disguise)

Closing-paragraph tells:

- "In conclusion", "In summary", "Ultimately, the key takeaway is"
- "the possibilities are endless", "the only limit is your imagination"

## Punctuation and typography

- Em dashes and en dashes, and the literal `--` used as a dash in prose. This
  project writes plain ASCII: recast with a comma, a colon, parentheses, or two
  sentences. Leave `--flag` forms inside commands and code alone.
- Curly or "smart" quotes in source text where ASCII quotes are the house style.
- The Oxford-comma rule-of-three list (see triadic parallelism in
  `structures.md`); the list is the structural tell, the commas are just where
  it shows.

## How to use this list

Flagging a word is a prompt to look, not a verdict. "Robust" in "the installer
fails closed on any checksum problem, which makes it robust" is slop (delete the
clause). "Robust" inside a quoted error message is not yours to touch. Judge the
sentence, not the token.
