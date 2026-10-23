# Caption craft

Caption displays the speech as it is being delivered. Its verbal identity and contemporaneous
relationship to that speech matter more than its size, decoration or placement. A striking animated
word can be Caption; a title held long after the phrase to label a section can be Typography even
when those words were also spoken. Their role in the work decides the distinction.

Script's Dual Text permits intentional display/pronunciation differences: “2012” and “twenty twelve”
remain one authored verbal unit. Caption does not require literal equality to a raw transcript.
Independent titles, lower thirds, labels and editorial paraphrases belong to their own Text or MG role.

For a coined name or letter-name reading, use
[Script pronunciation](../../creation/script-and-time.md#choose-the-sound-the-spelling-should-carry):
`<CSS|see ess ess>` keeps `CSS` on screen while supplying its chosen reading to the performance.
`<New York|>` instead keeps identical display/speech wording in one complete correspondence;
`<|再见>` retains the spoken words and their anchors while omitting them from Caption. These forms
choose content and correspondence; the Caption family decides their visual treatment. Place `||`
between complete units when another reading handoff is wanted.

For implementation of a new visual family, read
[Caption authoring](../../production/caption-authoring.md). That guide keeps the common text/timing
chain and shows where the new family owns scheduling and rendering.
For choosing Chinese, Latin or mixed-script faces, using a local font or finding a new one, read
[Fonts and text](../../production/fonts-and-text.md).

## Direct captions for this video

Use the reference to understand what its captions contribute: how they group speech, emphasize an
idea, establish a speaker or fit around the picture. Carry those relationships into the new work
when they serve its Brief. A new language, performer, product or tone can call for a different face,
grouping, placement or motion. Direct that treatment from the new Script's meaning and the video's
vibe, and record the choice in Treatment and its Recipe.

A short handoff can land a punchline; a longer phrase can let an explanation breathe. Both are useful
when the viewer can read the thought and follow the picture. The reference, language and intended
energy inform that judgment rather than prescribing a fixed Cue length or one caption look.

Choose the reading phrase, its layout and its emphasis together while keeping their responsibilities
clear. A meaningful phrase may wrap over two lines; one line may stay fully visible while its spoken
word changes color. Hiding a caption for a demonstration changes presentation, not the Script or the
performed speech. The following sections connect these decisions to the actual picture.

## Keep wording and timing in their owners

Script owns display words, speaking Roles, Dual Text units, attributes and authored Cues; `||` ends
the current Cue. Its CaptionDocument contains no seconds or frames. A source-domain adapter produces
complete, flat Unit CaptionTiming on the actual Timeline; a visual family joins that timing to the
authored Cues and presents them. Reuse those units rather than retyping spoken words into independent Typography merely
because it can draw the desired shape.

Use the produced performance's normalized and aligned audio. A change to that audio, its speed or
its cuts can change word timing and requires corresponding alignment. A visual-only restyle can
reuse the same semantic and media outputs through the Run.

## Design Cue rhythm with the Caption system

A Cue is one timed block of displayed speech. Its family and Recipe determine what that block looks
like; Script's `||` determines an additional handoff between blocks inside the same Segment and
speaking turn. Segment and turn boundaries already form new Cues. A Style Use can change presentation
partway through a Cue while retaining its complete content and original word times. A visual line is
different: Fine may wrap one Cue over several lines without another `||`.

Choose the grouping from language and picture together. Let one Cue carry a coherent phrase or
thought that the viewer can grasp while still watching the performance. Preserve words whose meaning
depends on each other, and give a payoff or contrast its own handoff when the visual treatment makes
that separation useful. Keep a name, negation, article and noun, preposition and object, phrasal verb,
or quantity and unit together when separating them would make either screen state harder to read.

### Language changes the reading unit

English commonly uses a word as its smallest timed display unit; Chinese uses individual Han
characters. That gives Chinese precise character highlighting, while a Cue still holds a meaningful
phrase. A Chinese Cue can comfortably contain more characters than an English Cue contains words.
Choose its length from meaning, reading time and the space the actual font occupies. A fixed word
or character count cannot make that choice. Count the display side of Dual Text when judging fit.

| Writing | Grouping and presentation |
| --- | --- |
| English | Keep a useful phrase together, including its articles, negation and name or quantity. Word lengths vary, so the chosen face and width matter more than a word count. |
| Chinese | Keep compounds, names, modifiers and their objects together. Let a complete short clause share a Cue when it fits; repeated tiny character groups fragment both meaning and the screen. |
| Korean | Preserve the authored word spaces and keep grammatical phrases readable together. `3개월` and `3 개월` are different authored spellings; the Caption layout follows the chosen one. |
| Mixed Chinese and English | Read the phrase as a whole. A Latin brand name or number can occupy several Han characters' width; its lexical unit count does not predict that width. |

Fine preserves authored display separators in every writing system. Its `word-gap` sizes those
separators; a Chinese/Latin or number/letter boundary does not create one. Write `是的 就是这样`
when that space is intended, and `3D` or `3개월` when the text should stay joined. `letter-spacing`
adjusts glyph tracking. `<expression|>` groups an expression for caption behavior; it is not needed
to preserve spelling or spaces.

### Choose emphasis independently of grouping

The same timing supports a stable complete Cue, current-word or current-character color, or a trail.
A stable phrase can let the viewer follow a detailed demonstration while still reading the speech.
An active-word response can draw attention to its delivery; a whole-expression response can give a
name or punchline one visual accent. Choose from the intended viewing rhythm. Character-level timing
remains available even when the design keeps the whole phrase steady.

For whole-character highlighting, use `karaoke: current` with `karaoke-transition: step`.
Choose `trail` instead of `current` when the already spoken characters should stay highlighted.
`step` activates the complete timed unit at its start; `wipe` is a different visual choice that
sweeps inside its glyphs. Both follow each unit's own speech time, including uneven delivery and
pauses. Making a Cue longer changes its reading group, not its character timing.

When a compound, name or short phrase should respond together, author it as `<组件化|>` in Script.
The omitted spoken side inherits the same words. Fine's existing whole-unit `step` highlighting,
underline and active box then follow that group's first-to-last speech interval, while each spoken
character keeps its own Timeline anchors. A Cue can mix these groups with ordinary characters.
Use this for deliberate whole-expression treatment, not as a requirement to annotate every Chinese
word. `||` remains the reading handoff; group markup does not create another Cue.

Text appearing and text changing color are separate choices. `atom-reveal: all` keeps the complete
Cue available to read while Karaoke supplies emphasis; `on-start` reveals whole spoken units, and
`typewriter` reveals whole graphemes within them. A pronunciation span such as `<API|A P I>`
remains one shared timing unit. Scope it to the expression needing a pronunciation hint so the
surrounding Chinese characters retain their own timing.

### Choose line layout for the picture

A single-line treatment can give successive short Cues a stable reading position. Direct it through
the phrase grouping, font size, usable width and spacing together. When a complete thought needs
more room, Fine can wrap the same Cue over several lines. An independently arranged oversized keyword
with supporting text can instead belong to a new Caption family. Choose the structure for the
picture and meaning; a visual line break alone is not a reason to add another `||`.

For example, these groupings preserve short ideas in each language:

```svml
<explanation><HOST>
  One reference can rebuild ||
  the shots and pacing, ||
  the captions and effects, ||
  around your product.
</explanation>

<explanation-zh><HOST>
  一张参考图 || 就能重新设计镜头和节奏，||
  让字幕和特效 || 为你的产品服务。
</explanation-zh>

<explanation-ko><HOST>
  참고 영상 하나로 || 촬영과 편집의 리듬을 바꾸고, ||
  자막과 효과를 || 제품에 맞출 수 있어요.
</explanation-ko>
```

These are alternative Script excerpts, not a bilingual performance. Another width or delivery can
justify a different handoff. The sentence supplies semantic structure; the presentation says how
much of that structure should share one screen state.

Fine's optional `max-words-per-line` inserts visual line breaks by display-unit count. In Chinese,
that count is usually characters. Leave it unset for ordinary width-based flow; choose it when a
deliberate counted row serves the design. `max-lines` checks those counted rows and requires that
setting; it does not make a long Cue fit one physical line. The package README owns these controls.

## Give captions a place in the visual language

Choose font, size, width, line height, contrast and motion together. If a Cue overflows, inspect both
its authored grouping and its actual Style; do not assume every overflow has the same cause. Lead,
tail and handoff shape visibility while karaoke follows semantic word timing.

Judge weight, outline and shadow from the actual glyphs against the moving picture at delivery size.
A bold outline can give an energetic caption its shape and separation; a compact shadow can separate
a quieter treatment. Keep the internal spaces of dense glyphs legible as the weight grows. The useful
strength depends on font, size, background and intended style, including when changing languages.

Lettering and decoration can share a palette without coloring each word differently. A two-color
accent beneath a steady phrase, a shaped background or an offset shadow can connect Caption to the
film's visual language. Use an existing Style when it expresses that relationship, or author the
coordinated text and decoration in a project Caption family. Let the decoration's extent, position
and movement answer the text it supports.

Treat Caption, icons, flashes and other graphics as a composition. A guest color and answer accents
can work together without coloring every system identically. Check readability across
light and dark frames, avoid hiding the important face or product, and allow enough space above a
tracked head for the whole Cue rather than only its anchor.

Ordinary Caption placement belongs to the chosen family's layout and Style: it can hold a stable
reading area or respond to the composition without face boxes. When the user's reference visibly
uses head-following Caption, or the user asks for that treatment, use the optional
[Caption tracking](caption-tracking.md) relationship. A visible face alone does not choose it.

## Caption families, Styles and parameters

Script publishes one `CaptionDocument`: ordered display words, complete Alignment Units, speaking
Roles, word attributes and authored Cue handoffs. Caption joins it to the real Timeline. That
common typed relationship is what makes the result Caption; an official renderer is not the
definition. A project package can provide another Caption family while keeping the same Script words
and measured speech evidence.

Direct the presentation through three related layers:

| Choice | What it decides |
| --- | --- |
| **Family** | The structural visual language and scheduling behavior the Caption can express: uniform flowing words, independently arranged phrases, speaker-attached shapes, or another authored relationship. |
| **Recipe and resolved Style** | One coherent treatment within that family. An SVS Recipe gathers a useful combination; the family's Style Surface resolves it with fonts or other explicit resources. Role or Selection applications can choose among those Styles. |
| **Parameters** | The individual decisions inside that treatment: placement and anchors, usable width, wrapping, typography, Paint and boxes, active-word response, Cue motion, reveal, lead, tail and handoff. |

The installed family vocabulary owns exact parameter names and accepted values. Craft owns how the
combination serves this picture and this reading rhythm. Keep a proven production treatment in its
project `.svs`; a set that has earned reuse across works can become an ordinary versioned data package
under its owner's scope. Such a collection preserves the family, Recipe and intended use together
rather than turning isolated parameter values into universal defaults.

Caption Uses choose when those Styles apply, optionally filtered by speaker. Cue content
stays complete when presentation changes midway through a phrase. [Caption styling and coverage](../../production/caption-presentation.md) explains
overrides, Segment-wide selections, word attributes and hiding selected captions with a Hidden Style.

## Reuse Fine or author a new family

UGC, podcast and interview work can use `@hypit/caption-fine`. Fine supports exact fonts,
placement and anchors, wrapping, Cue boxes, active-word treatment, lead/tail and motion through
explicit Style Recipes. Role overrides can distinguish podcast hosts; a tracked head can supply a
moving placement point without changing the verbal pipeline.

```svml
<caption-fine:Caption id="captions" document={story.caption} timing={story-captions}
  timeline={speech.timeline} within={vertical.bounds}>
    <caption-fine:Use style={primary-caption}/>
    <caption-fine:Use role="GUEST" style={guest-caption}/>
  </caption-fine:Caption>
```

This excerpt assumes the imported Surfaces, fonts and Styles already declared in the Source.
Use the owning package README and `hypit vocabulary @hypit/caption-fine` for current Recipe fields.
Keep one coherent interpretation of the Script across speakers and styles; different colors do not
require unrelated transcripts or separately invented timing.

Fine is to Caption what Media is to ordinary picture presentation: a broadly useful reusable
component. A new visual relationship can become a project component directly. A Caption family can
arrange a phrase around its keyword, place speakers' phrases in a shared composition, or coordinate
words and graphics as one visual event. Word attributes and Selections carry the authored meaning;
the family owns how that meaning appears and moves. This is ordinary video authorship, including for
a treatment used in only one work.

Apply the same freedom to component boundaries. Independently behaving captions can remain a peer
Track. Words and graphics whose layout or motion belongs together can share a component, consuming
the common Caption document and semantic timing. Caption names the relationship between displayed
speech and its performance; it does not prescribe a separate visual layer or the Fine renderer.
[Caption authoring](../../production/caption-authoring.md) explains building that family or scene.

## Review in the current composition

Use [snapshots](../../production/snapshots.md) from Studio or the existing HTML to inspect the actual
glyphs, spaces, outline, decoration, wrapping and neighboring visual states. Play the passage in
Studio to judge reading rhythm, emphasis, Role assignment, cut transitions and tracked movement with
speech. The current composition supplies this evidence while the Run retains its accepted media and
semantic Outputs. Inspect the encoded file too when delivering an export.

Repeated tiny handoffs can ask the viewer to reacquire text too often; an overfull block can ask one
visual state to carry too much. Change `||` when the reading unit needs another handoff. Change the
Style when the reading unit works but its size, wrap, placement or motion does not. A different
structural relationship can become a project Caption family. Check that the resulting treatment
works with the actual spoken pace and picture, including its entrances and exits.
