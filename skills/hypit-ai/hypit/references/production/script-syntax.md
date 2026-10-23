# Script syntax

Read this when writing or correcting `<script>`, including display spelling, pronunciation,
spaces, Caption grouping and semantic markers. [Script and semantic time](../creation/script-and-time.md)
owns the creative decisions; [Source syntax](source-syntax.md) owns imports and graph references;
[Timing](timing.md) explains how components use the resulting identities.

These are the author forms owned by the installed Script package. Package releases and logical Module
ABIs are different: `@hypit/script@1` is the logical import. Correct a syntax error in the Source
rather than changing authored wording or spaces. The installed package owns the parser and exact
diagnostics.

## Keep the languages distinct

| Where you are writing | Form | Meaning |
| --- | --- | --- |
| Structured Source attribute | `narrative={story}` | A whole-value graph reference. |
| Script prose | `@{reveal!}` | A semantic Moment; contributes no displayed or spoken text. |
| Script prose | `clear{emphasis}` | An attribute on the preceding display word. |
| A model's prompt text | `@image1` | That model's reference notation, when its Kit declares it. |
| An absolute-time declaration | `<time:Instant id="cue" timeline={film.timeline} at={claim}/>` | A named Instant produced from an already resolved value. |

Braces and at-signs have no global substitution rule. The receiving Surface owns its body's grammar.

## Structure, grouping and display attributes

The author-facing forms are:

| Form | Meaning |
| --- | --- |
| `<opening>...</opening>` | A Segment named `opening`; all spoken prose belongs inside a Segment. |
| `<pause/>` | A self-closing Segment with identity and boundaries but no words. |
| `<HOST>` | A Role Cue inside the current Segment; it applies until another Role Cue or the Segment end. |
| `<display text \| spoken text>` | One Dual Text unit with separate visible and pronounced wording. |
| `<display text\|>` | One complete display/speech unit using the same wording for both; individual spoken word times remain available. |
| `< \| spoken text>` | Spoken words that keep semantic timing while contributing no visible Caption words. |
| `\|\|` | A Caption Cue handoff between complete Alignment Units. |
| `word{emphasis,keyword}` | Boolean attributes on one complete display word for a Caption family to interpret. |
| `word{importance=2,tone=warm}` | Named string, number or boolean attribute values on that display word. |
| `@{proof} ... @{/proof}` | A Selection: one named semantic range. |
| `@{claim!}` | A Moment: one named semantic point. |

A Script contains one or more uniquely named Segments matching `[a-z][a-z0-9_-]{0,63}`;
`script` is reserved. A paired Segment can carry prose or be wordless; the self-closing form also
carries a wordless passage. A Role Cue is a bare turn marker: the next Role Cue begins the next turn,
and closing the Segment ends the final turn
and resets its Role. When a Segment uses Roles, place the first Role before that Segment's first
spoken text. One Segment can contain several Role turns without requiring several generated clips. A bare tag
inside a Segment is a Role Cue by context, not by capitalization: `<host>`, `<主持人>` and
`<진행자>` can name speakers. The label directs the request through dialogue; it selects no voice
or character asset by itself.

Dual Text can contain several visible or spoken words on either side; its display side feeds Caption
and its spoken side feeds pronunciation. An empty display side intentionally omits those spoken words
from Caption while keeping them in the Narrative and semantic timing. Selections and Moments can be
placed on the spoken side because that side owns the speech anchors. End a Cue before or after the
complete Dual Text unit, not inside it. Attributes for a displayed Dual Text word belong on the
display side before the pipe. Inside that display side, use `\@` when the visible text itself needs an
at-sign.

The three Dual forms serve distinct author choices:

| Script fragment | Display | Speech | Use |
| --- | --- | --- | --- |
| `<S\|ess>` | `S` | `ess` | Keep the spelling while specifying the letter's spoken name. |
| `<New York\|>` | `New York` | `New York` | Keep the same words and internal space in one complete correspondence. |
| `<\|再见>` | No Caption words | `再见` | Retain speech and its semantic anchors without displaying it. |

[Pronunciation choices](../creation/script-and-time.md#choose-the-sound-the-spelling-should-carry)
shows letter names, abbreviations, coined names and homophonic readings. The spoken side is ordinary
Text supplied to the selected model, not a separate phonetic language interpreted by Script.

When the wording is identical, `<组件化|>` is shorthand for `<组件化|组件化>`. It can group a name,
compound or phrase for Caption presentation while leaving its spoken Tokens and timing intact:
`把<动效|><组件化|>。|| 以后就能<直接复用|>。` Choose groups for the intended expression; ordinary
Chinese prose does not require word-by-word markup. The group's Style determines its visual response;
`||` still controls which reading phrases appear as separate Cues.

With speech omitted, the left side supplies both projections, so semantic markers can be placed
there and Studio writes back there: `<组@{beat!}件化|>`. Display attributes and markers are annotations,
not spoken words. Attributes still apply to the preceding display word rather than the whole group.
With an explicit spoken side, markers continue to belong on that right-hand side.
Either form needs a spoken word: `<API|...>` supplies no speech correspondence for its display.

Script comments contribute no text and do not split a word: `hel<!--note-->lo` remains `hello`.
In ordinary prose, a comment or zero-width marker also leaves a following attribute attached to its
word: `hello<!--note-->{emphasis}` and `hello@{beat!}{emphasis}` annotate `hello`.
An actual space before `{emphasis}` breaks that attachment.
A comment can also stand between passages:

```svml
<!-- This note enters no text projection. -->
<social><HOST> Follow us \@hypit.</social>
```

Reserved Script punctuation remains literal when escaped: `\@` produces `@`, `\<` produces `<`,
`\{` produces `{`, `\}` produces `}`, `\|` produces `|`, and `\\` produces `\`. A plain `>` needs
no escape in ordinary prose; inside Dual Text, `\>` keeps it from closing that unit. A single `|` in
ordinary prose is literal; `||` is the Caption Cue handoff. Inside Dual Text, the first unescaped `|`
separates display from pronunciation; write `\|` for a literal pipe and `\|\|` for two literal pipes.
These escapes belong to Script prose, while structured Source attributes and elements use the Markup
escaping described in [Source syntax](../production/source-syntax.md).

Script derives speech tokens from words and numbers. Punctuation remains attached to the displayed
word it belongs with and does not create another speech time unit. CJK prose commonly contributes
one Han, Hiragana or Katakana character per lexical unit; compounds, decimal numbers and the spoken
side of Dual Text preserve their own lexical structure. This is why Cue boundaries, word attributes and
semantic markers attach to complete authored units instead of punctuation or visual line positions.
Character-level timing does not call for character-sized Cues: use `||` for meaningful reading
phrases. [Caption craft](../playbooks/craft/captions.md#language-changes-the-reading-unit) explains
Chinese, English and mixed-script grouping, spacing and their fit in the picture.

## Preserve spelling independently of timing

Ordinary whitespace runs become one displayed/spoken space. Leading and trailing whitespace in a
Turn and padding at the edges of each Dual side are omitted. A Source newline is prose formatting;
`||` makes a Caption Cue handoff, and the Caption family controls visual line wrapping.

| Script body inside a Segment | Display text | What the author chose |
| --- | --- | --- |
| `是的 就是这样` | `是的 就是这样` | A real space in Chinese prose. |
| `是的@{answer}就是这样@{/answer}` | `是的就是这样` | Joined text with a zero-width semantic range. |
| `是的 @{answer}就是这样@{/answer}` | `是的 就是这样` | The same range after an authored space. |
| `Hello @{place}New York.@{/place}` | `Hello New York.` | English spaces and attached punctuation. |
| `이건 3개월 동안 만든 영상이에요.` | `이건 3개월 동안 만든 영상이에요.` | Korean word spaces; no space inside `3개월`. |
| `3 개월` | `3 개월` | An explicitly different spelling. |
| `3D` / `3 D` | `3D` / `3 D` | Numeric/Latin adjacency is also authored. |
| `<New York\|>` | `New York` | One Alignment Unit with an internal space. |
| `<API\|A P I>` | `API` | One correspondence to several spoken tokens. |
| `<\|只说不显示>` | *(no visible words)* | Spoken content and semantic timing remain. |

Do not insert spaces around markers for parsing, strip Chinese spaces, or infer Korean/English gaps
from speech tokens. A space is display information, not an extra timed token. Caption consumers use
`separatorBefore` together with each display word's `text`; suppress a leading separator at a displayed
line/Cue start. [Caption authoring](caption-authoring.md) explains consuming these values in a new family.

The Script source and its projections answer different needs. Source preserves the author's prose;
display and speech normalize ordinary whitespace as above. Studio moving a marker relocates only
that annotation and retains unrelated source whitespace. Explicit Script formatting may reindent
and compact whitespace while preserving the same parsed meaning.

## Use the Script's deliberate projections

One Script publishes the full Narrative and the narrow views needed by the rest of the work:

| Reference | What it carries |
| --- | --- |
| `{story}` | The complete authored Narrative. |
| `{story.segment.hook}` | The `hook` Segment as a NarrativeSegmentRef for generation, alignment or another semantic consumer. |
| `{story.segment.hook.dialogue}` | Role-aware dialogue using the spoken side of Dual Text, suitable for a speaking performance request. |
| `{story.segment.hook.speech}` | Pronunciation-only Text, suitable for `hypit estimate` or independent speech. |
| `{story.caption}` | Display Words, Alignment Units, attributes, Roles, and authored Cues for Caption. |
| `{story.selection.proof}` | The named semantic range. |
| `{story.moment.claim}` | The named semantic point. |

For example, this Segment inside `story` assigns two speaking turns:

```svml
<exchange>
  <HOST> Let me show you.
  <GUEST> That looks much easier.
</exchange>
```

`{story.segment.exchange.dialogue}` supplies:

```text
HOST: Let me show you.
GUEST: That looks much easier.
```

Pass that Text to the speaking prompt. In action direction, relate HOST and GUEST to the supplied
character views and voices. The selected [Prompt Kit](prompt-kits.md) owns its reference
order; [podcast direction](../playbooks/formats/two-person-podcast.md#direct-conversation-inside-a-generated-clip)
shows how those roles and references form one performed exchange.

These are projections of one authored Script, not copies to maintain. The performance request,
Caption system, and semantic timing therefore remain connected even when their visible and spoken
wording differ.

## Bind meaning to Script identities

Every semantic marker is enclosed in `@{...}`, with `/`, `!` and `~` inside. The marker contributes
no text or whitespace. `是的@{part}就是这样@{/part}` stays joined; `是的 @{part}就是这样@{/part}`
keeps its authored space. Do not add spaces to make a marker parse. Markers cannot split a speech
Token or its attached punctuation: write `@{beat!}“测试”`, not `“@{beat!}测试”`.
`hel@{beat!}lo` and `안@{beat!}녕` also split tokens. Grouping with Dual Text does not make these
positions legal. Attributes stay attached to their display word: `word{emphasis}@{beat!}`.
Write literal `@{part}` as `\@\{part\}`.

Selections may overlap, cross, or span Segments; they are named semantic ranges rather than nested
markup. Selection and Moment names share one namespace and match `[a-z][a-z0-9_-]{0,63}`.
Inside spoken text, each marker chooses an
adjacent semantic boundary:

| Marker | Boundary |
| --- | --- |
| `@{name}` | Open a Selection at the next word's start. |
| `@{~name}` | Open a Selection at the previous word's end. |
| `@{/name}` | Close a Selection at the previous word's end. |
| `@{/name~}` | Close a Selection at the next word's start. |
| `@{name!}` | Place a Moment at the next word's start. |
| `@{~name!}` | Place a Moment at the previous word's end. |

Markers may sit between or outside Segments when the meaning crosses structural passages. For
example, this Selection owns the complete Script program rather than borrowing the first and last
word boundaries:

```svml
@{~whole}
<opening><HOST>First thought.</opening>
<answer><HOST>Final answer.</answer>
@{/whole~}
```

At a Script or Segment edge, the corresponding structural boundary remains available even when
there is no neighboring word. Thus `@{videos} videos @{/videos}` covers exactly that word. Adjacent
visual Windows can share a boundary at either side of the pause between words. To give that pause
to the incoming picture, meet at the previous word's end:

```svml
@{coffee} my coffee @{/coffee} @{~smoothie} my smoothie @{/smoothie}
```

To give it to the outgoing picture, meet at the next word's start:

```svml
@{coffee} my coffee @{/coffee~} @{smoothie} my smoothie @{/smoothie}
```

Both Selections now meet at one instant in either example. A `||` between the phrases changes
Caption grouping, not their visual boundary. [Material-led picture craft](../playbooks/craft/b-roll.md)
owns whether the edit should meet there, leave a pause visible or let another picture continue.

The marker locates meaning, not an animation's lifetime. A reveal may leave its answer visible;
a covering picture may occupy the full Selection. [Timing](timing.md) explains those consuming forms.
