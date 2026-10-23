# Writing a Caption family

Read this when a work needs a new relationship among its spoken words, layout and motion.
[Caption craft](../playbooks/craft/captions.md) owns readability and directing judgment;
[Caption styling and coverage](caption-presentation.md) owns applying visible and hidden Styles;
[Track authoring](track-authoring.md) owns project package wiring.
[Fonts and text](fonts-and-text.md) explains exact font resources and fallbacks;
[component visuals](component-visuals.md) explains the final drawing representation.
[Component design](component-design.md) connects a new family's visual idea to useful author controls
and its fit beside the rest of the video.

## Decide what is actually new

Fine Caption already covers uniform flowing text with exact fonts, Paint, boxes, karaoke states,
placement and motion. A uniform treatment, or a treatment selected for a Role or Window, may only
require Source and Recipe changes. A persistent visual role attached to selected display words does
not: mark those words with Script attributes and let a project Caption family interpret the role.
Never put keyword search, matching or content selection in a Recipe. A keyword occupying a separate
oversized line, words playing different visual roles, or a recurring spatial relationship among
speakers can justify a new family directly.
Creating that family is normal video production. Name the family for the visual relationship it
makes reusable, and name each Style for a particular treatment within it. A project can also own a
single-use caption composition when that is what the video needs.

The result is still Caption when the displayed words correspond to speech and remain close to its
delivery. Independent slogans, summaries and titles usually belong to Typography even if they react
to a Script Moment.

## Own the visual relationship

Visual Clip presents placed footage; Visual Clips supply independent pictures. A scene component can
coordinate either with diagrams or other graphics. Fine and custom Caption families have the same relationship. Their shared input is the
authored speech and its semantic timing; the implementation owns the spatial structure and motion.

Start from what the viewer should understand or feel. A supporting phrase might establish the
thought while its key word takes the emphasis. Design how they enter, share space, respond to speech
and hand off to the next thought. That relationship suggests useful controls: the word's authored
role, fonts, relative sizes, placement and motion. Put the choices the production actually needs to direct in its Style/Recipe and the arrangement
in the renderer. A qualitative mode and a numeric field need the same justification; fixed decorative
details can remain local. [Component design](component-design.md#expose-the-choices-the-work-needs)
owns that interface decision.

The output remains an ordinary VisualTrack. Its Presents can own trees of text, boxes, images and
other visual elements. When words and graphics share layout or motion, they can live in the same
component. [Component visuals](component-visuals.md#compose-video-and-graphics-in-one-html-visual)
also describes HTML/CSS HTML visuals with typed media and text children. That drawing freedom
applies to captions too: give the program the resolved caption schedule and explicit resources,
and evaluate its state at the requested frame. Keep separately useful overlays as peers.

## Keep the existing text and timing chain

```text
Script → CaptionDocument (displayed Words, correspondence Units, authored Cues and word attributes)
NarrativeCaptionBinding + NarrativeProjection → CaptionTiming
Track Uses → resolved time windows, Styles and optional speaker filters
CaptionDocument + complete unit Timing + Uses + family parameters
  → family-owned schedule for the authored Cues → VisualTrack
```

Consume each display word's `separatorBefore` with its `text`; never rebuild wording by joining
speech Tokens with spaces or guessing from a writing system. Suppress a separator at the start of
a displayed Cue/line. Use the same authored boundaries in base glyphs, active layers and backgrounds.
Separators are display content, not timed Tokens.

Use `@hypit/caption` for content timing and Use coverage, and `@hypit/narrative` for
Script document types. A family Track accepts `document`, resolved `timing`, `timeline` and ordered
`Use` children:

```svml
<keyword:Track id="captions" document={story.caption} timing={story-captions} timeline={program.timeline}>
  <keyword:Use style={base-style}/>
  <keyword:Use role="GUEST" style={guest-style}/>
  <keyword:Use during={punchline} style={punchline-style}/>
</keyword:Track>
```

These names assume the project family and its Styles have been declared. `during` references a named
absolute Window declared upstream. A Use has the same meaning regardless of the family. `role`
filters whose content it presents within that window.

For a keyword layout, Script can mark `useful{emphasis}`. The family reads that attribute from the
CaptionDocument and gives it a visual role within the complete Cue. The word role and the time
window answer different questions; an emphasis attribute does not invent another time language.

## Design a family-specific schedule

Separate measured speech time from visible time. Preserve each alignment unit's measured boundaries
and identity; resolve lead, tail, stagger, hold and handoff into an explicit schedule before rendering.
The renderer draws that schedule. Preserve a Cue's original animation origin and apply the
winning Use window as a separate visibility mask. A window starting midway through a Cue still
receives the complete Cue and original word times. It can change appearance without restarting
karaoke or text reveal.

For a “large keyword plus supporting phrase” family, the schedule might identify each Cue's display
words, its emphasized word ids, their measured units and the visible interval of the two groups.
Its layout then computes the two groups together. Decide what happens with no keyword, several
keywords, long text and an N:M pronunciation span. Make author correction possible through word
attributes, `||` and Style configuration instead of inventing missing text or dropping words.

The projection publishes every complete Unit's absolute boundaries and does not form Cues. The
CaptionDocument already partitions complete Units into authored Cues. A family schedule joins those
Cues to Unit timing and may derive lines, pages, cards or local states, but it does not split or merge
Cues. Visual line wrapping is a separate operation. A narrow width must not silently rewrite the
Script into new Cues. Preserve the original Cue, Unit and Word associations in the schedule.

Display Words reflect Script's lexical units: a Han character is normally one Word, while an
English word is normally one Word. Keep that timing granularity separate from visual grouping.
Use each word's authored `separatorBefore` and `text`, including attached punctuation; derive no gaps
from the writing system. Measure with the selected fonts' actual widths. Exercise Chinese with an
intentional space, Korean word spaces, and mixed numeric/Latin spellings when the family carries them.

For speech-following emphasis, activate each complete unit from its projected start and end.
A Cue-wide left-to-right progress bar follows elapsed time and text width, which is a different
effect from following spoken characters. Keep within-glyph wiping an explicit visual choice.
Use uneven unit durations and a pause in a short example to check that the chosen effect follows
the intended clock.

`caption:Hidden` supplies a Style with `rendering: null`. It takes part in later-Use precedence,
clearing this Track's presentation in its window; a later visible Use can restore a smaller window.
Use `captionUseVisibility` to resolve that coverage for each Cue's speaker. The content projection
retains all Cues regardless of Style. Empty or uncovered time naturally produces no drawing.

## Give Style, layout and rendering clear owners

The Style Surface validates a Recipe and exact font references, then emits the common Caption Style
shape with the new family's name and parameters. The Caption Surface accepts the document,
Timeline and timed Use children; its Fragment assembles the Uses, performs the common timing join,
and runs its own schedule and render operations. Register the new family's Producers and any new schedule Type in its own package.

The renderer owns typography, structural relationships, stacking and motion. Use the existing text
shaping and Visual IR facilities with explicit font resources, including selected local font files,
so the same faces reach the rendering machine.
Read `@hypit/caption-fine`'s `surface.ts`, `schedule.ts` and `render.ts` as separate implementation
examples. Reuse the common parts and replace the actual family behavior, including its parameter
validation; renaming Fine while retaining its uniform-word assumption will not implement a structural
keyword treatment.

The chosen family interprets its own Styles. Fine handles its uniform-flow Styles; a structural
family handles its own layouts. Each Track is independent, so multiple Tracks can intentionally
show captions together or use complementary coverage. Mixed-family rendering, if useful, belongs
to the component that implements it.

If this family supports spatial tracking, take an explicit Region Evidence and map it into the actual
composition. Define subject matching and absent-region behavior. Detection belongs to the measurement
step described in [Caption tracking](../playbooks/craft/caption-tracking.md), not to this renderer.

## Check the relationships that matter

Use a short Script with a normal phrase, the new structural treatment, a Role change and a Dual Text
unit. Verify displayed words and their association with measured speech, then inspect the new layout
at the intended frame size and around its handoffs. Check long words, overflow and direct seeking
where relevant. A still can show typography; only the configured timeline establishes timing.

Expose the family with useful vocabulary and a designed preview. Keep wording, font choices, palette
and authored word roles editable in the project. The package adds its rendering language while
consuming the existing Script, Caption and semantic-time owners.

For live Cue Items and Inspector editing, add a [Studio Companion](studio.md#give-a-project-component-a-useful-companion)
that presents complete Cue content on the Timeline and authored Uses as Inspector objects. Read the
Track's resolved Use collection, retain each Use's Source range and temporal lineage, and expose the
referenced Style on that Use. Caption Fine's
Companion is a useful example of these relationships; the new family's layout stays in its renderer.
