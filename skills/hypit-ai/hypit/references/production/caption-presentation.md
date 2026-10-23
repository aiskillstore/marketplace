# Caption presentation

Read this to apply subtitle treatments, change them during a passage, or hide them temporarily.
[Caption craft](../playbooks/craft/captions.md) owns visual direction;
[Caption authoring](caption-authoring.md) explains creating a new family.

**Script authors Words, Units and Cues; the family presents those Cues; Use organizes presentation
in time.** `||` ends the current authored Cue. An upstream adapter resolves every document Unit's timing once; the
Track consumes that flat `CaptionTiming` without knowing whether it came from Narrative, SRT/VTT or
authored absolute time. Each Use selects a complete Style inside an already resolved time window.

```svml
<caption:Hidden id="hidden"/>
<narrative-caption:Timing id="story-captions" document={story.caption}
  binding={story.caption-binding} projection={story-time}/>
<time:Window id="impact-window" timeline={program.timeline} from="12s" for="2s"/>
<caption-fine:Caption id="captions" document={story.caption} timing={story-captions} timeline={program.timeline} within={canvas.bounds}>
  <caption-fine:Use style={base-style}/>
  <caption-fine:Use role="GUEST" style={guest-style}/>
  <caption-fine:Use during={answer-window} style={answer-style}/>
  <caption-fine:Use during={demonstration-window} style={hidden}/>
  <caption-fine:Use during={impact-window} style={impact-style}/>
</caption-fine:Caption>
```

Styles are declared by the chosen family. Fine Styles take a Recipe and exact fonts. A new structural
caption can use a project family with its own layout and behavior.

## One time language

| Intent | Use |
| --- | --- |
| A treatment across the whole Timeline | `style={base}` with no time attributes |
| Follow a semantic passage | Project it once, then `during={answer-window}` |
| Follow a placed Segment | Project it once, then `during={answer-window}` |
| Start at a meaningful word, for a fixed duration | Project it once, then use the resolved Window |
| End at a meaningful event | Declare a named Window from that event, then consume it |
| Explicit window | Declare it once with `time:Window`, then `during={named-window}` |
| A particular speaker | Add `role="GUEST"` to any of these |

[Timing](timing.md) owns the shared expressions and semantic references.
Use semantic boundaries when the treatment follows what is being said. Absolute times remain useful
for an explicitly timed presentation. A Role filters whose content is presented, independently of the
window: it can cover several turns and does not change the Window shown in Studio.

The last matching Use in Source order wins locally. Each match replaces the whole Style; properties
are not merged. A hidden Use clears this Track's subtitle presentation throughout that window,
including neighboring Cue lead/tail. Later Uses can restore a smaller interval. Audio and content
stay unchanged. With no matching Use, nothing is drawn. With no subtitle content, a Use has nothing
to draw. Independent Caption components can intentionally show multiple presentations at the same time.

## A style change can happen inside a Cue

```text
test1 || test2 @{select} test3 || test4 @{/select}
```

This contains three Cues: `test1`, `test2 test3`, and `test4`. The Selection starts before `test3`;
it does not split `test2 test3`. With a broad ordinary Use and a later emphasized Use during `select`,
the complete second Cue changes Style at that boundary, then the third Cue uses the same emphasis.

Word times remain the original times. Karaoke or text reveal therefore continues at the appropriate
word when the Style changes or returns after a hidden interval. The Window limits visibility; it does
not restart the Cue's animation clock. Changing only one word's visual role is a different design
choice: Fine provides current/trail unit emphasis, while a custom family can interpret authored word
attributes for structural layouts. Display/pronunciation units remain complete.

In Studio, Caption's timeline row shows Cue Items. Presentation Uses remain Inspector objects rather
than draggable timeline ranges: their referenced Style or Recipe can be edited there, while their
Scope and Role explain which Cues they affect. Changing `||` changes Cue structure; changing a Use
does not. Inspect the resulting placement, handoffs and emphasis alongside the other visuals while
reusing the existing media.
