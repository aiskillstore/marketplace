# Authoring a production

Read this when turning the current Treatment into Author Sources, Recipes, Runs, project components,
and Builds, or when revising an existing production.

[Script and semantic time](../creation/script-and-time.md) explains target wording, Segments, Roles,
Caption Cue decisions and semantic relationships. [Script syntax](script-syntax.md) gives their exact
forms; [Timing](timing.md) projects them into components. [Source syntax](source-syntax.md) explains
imports and references.
[Composing Tracks](tracks.md) connects the visual and audio roles; [Track authoring](track-authoring.md)
and [Caption authoring](caption-authoring.md) explain creating a new project component for them.
[Component design](component-design.md) explains shaping its behavior and controls around the work.
[System relationships](system.md) connects these concepts to execution and Results;
[media preparation](media.md) explains material inputs. [Production navigation](index.md) locates
specialized questions without requiring every page for every revision.

## Turn the Treatment into relationships

Begin with the work the Treatment describes, not with a package inventory. Identify:

- the meaningful, performable Script passages and any speaking roles;
- the performances placed on Timeline and the independent material supplied to other components;
- the picture and sound contributions the work needs, including a simple full-frame performance;
- the semantic relations that should follow words, phrases, pauses, or content events;
- the genuinely clock-based events;
- the final Film or other deliverables.

Bring the relevant directing knowledge into those decisions: use
[Script and semantic time](../creation/script-and-time.md) for the verbal structure and the meanings
other layers will follow,
[image direction](../playbooks/craft/image-direction.md) for generated camera images,
[video direction](../playbooks/craft/video-direction.md) for generated performance and action,
[voice direction](../playbooks/craft/voice-direction.md) for casting and directing a character's voice,
[voice and performance](../playbooks/craft/voice-and-performance.md) for A-roll and recurring voices,
[B-roll](../playbooks/craft/b-roll.md) for coverage,
[screen demonstrations](../playbooks/craft/screen-demonstrations.md) when an interface carries evidence or explanation,
[Caption](../playbooks/craft/captions.md) for speech-linked text, and
[graphic composition](../playbooks/craft/graphic-compositions.md) for designed visual hierarchy,
with [motion graphics](../playbooks/craft/motion-graphics.md) for changes within it.
These pages establish what the authored relationship should accomplish. Installed vocabulary then
supplies the exact language for expressing it.

For a performance-led work, including pure A-roll or short drama, keep the intended passages in
Script and let accepted media establish their actual extent. Add semantic preparation when Caption,
sound or visual relationships need positions inside that performance. A standalone asset edit can
instead end at its requested media Output.

Author those relationships explicitly. Script Selections and Moments carry meaning through placed
performances into real time; authored positions locate independently timed events on the same Timeline.
Track and Film elements arrange the resulting picture and sound. One Author entry connects the
work; imported Sources and project modules divide its meaningful responsibilities. A camera cut
is not by itself a reason for another Source, Segment, component or Build.

When a role first leads to an installed Surface in the current work, query its actual declaration
before writing the element:

```bash
hypit vocabulary @hypit/gpt-image --tag Image
```

Use the logical Module import, tag, attributes, children, ports, and output paths that this project's
selected installation reports. Query again when the selected package or Distribution has changed, or
when an error shows that the assumed declaration is no longer the installed one; an already
established Surface does not need to be rediscovered for every edit. After writing one coherent
Source or Run change, check that actual entry:

```bash
hypit check authors/main.svml
```

`vocabulary` establishes what the selected package declares. `check` resolves the real Source closure
and verifies its imports, references, types, outputs, and Run choices. `plan` resolves the current
Run's required capabilities; `hypit doctor` actively diagnoses the selected Profile and account
reachability. Those are execution questions rather than additional authoring checks.

When observation has already produced useful authored data—such as a per-frame region sequence for
placing Caption above a moving head—keep that data in Source or Recipe and pass it through the
component's declared input. It is part of the chosen production design, just like a Frame or Style.

When the desired measurement depends on generated footage, the first Build supplies that footage.
Observe it, author the resulting data, and reuse the produced media in the next composition Build.
[Caption tracking](../playbooks/craft/caption-tracking.md) describes this loop for head placement.

## Give each production surface one job

- An **Author Source** (`.svml`) owns the target Script, media requests, components, Tracks, Film, and
  public Outputs. It imports the vocabulary it uses and may import other Author or Recipe Sources.
- A **Recipe Source** (`.svs`) owns reusable authored values such as a visual Style or request
  configuration. It remains explicit input to the Source that uses it.
- A **Run Source** (`.svrun`) binds one Author entry, names the public Outputs this execution requires,
  and selects any file, earlier Result, or Fragment Candidates used for it.
- A project **Author Package** under `packages/` owns a visual or semantic role that deserves its own
  vocabulary and implementation.

A project may have several of each. Different Runs against the same Author Source are useful when
their demanded Outputs or Candidate selections genuinely differ. Repeating one Run creates another
Build; it does not create another production.

Use [Source syntax](source-syntax.md) for language forms and [Runs](runs.md) for execution choices.
`hypit vocabulary <package>` or a focused tag or visual query supplies the installed Surface's
attributes and outputs. Package-local documentation supplies its exact behavior and API. Source
imports select author vocabulary; Runtime configuration selects external facilities.

## Use Runs for execution choices

A Target marks where this Run asks the graph to become real. For ordinary commissioned production,
the demanded Output is usually the finished video, and the Build produces its required media
dependencies through the same graph. A public image, prepared video, audio item, or other intermediate Output
is also a normal Target when the user requested that deliverable or the work genuinely needs it
independently now.

Every public Author Output that completes while satisfying the demanded Target is stored in that
Build Result and can be inspected or reused later. Derived public Outputs such as normalized media,
a local temporal domain or alignment evidence therefore remain available when a downstream Target
caused them to complete.

The Author Graph supplies primary Candidates. A Run may explicitly select another compatible
Candidate for a Logical Output:

- `<file>` admits project media as a zero-input Candidate;
- `<build-record>` names one public Output from one earlier Build Result;
- a Run Fragment computes one or more Candidates from its explicit inputs;
- `<satisfy>` selects one declared Candidate for one Logical Output.

Candidate selection is an implementation decision for this Run. Core checks nominal Type
compatibility and plans the combined Author and Run graphs. It replaces the displaced upstream
subgraph while preserving any upstream Outputs that the selected Candidate itself consumes.

[Runs](runs.md#generate-material-while-composing) shows how to target prepared material while
component work continues, then reuse that material for focused rendering and delivery.

## Reuse produced work explicitly

For a revision or retry, continue using produced media that still serves the current intent. Preserve
the Run's unrelated Candidate selections and add explicit selections for newly completed Outputs
that the next Build should keep. Replacing one image or changing a Caption does not release every
other output back to generation. Removing a `satisfy` restores that output's primary Candidate, which
may submit a new paid request even when the Source and output name have not changed.

The exact address of an earlier public Output is its Build id plus Output name:

```svml
<build-record id="opening-take"
  build="bld_20260902T110000001Z_0000000001" output="opening-take.video"/>
<satisfy output="opening-take.video" candidate="opening-take"/>
```

If the current Logical Output was renamed, the two names may differ: `build-record output` remains
the old Result's public name, while `satisfy output` names the current graph position. Hypit does not
infer that two names carry the same creative meaning.

Use `hypit builds`, `hypit inspect <build-id>`, and `hypit history <output-name>` within the selected
production's Result repository, following its recorded Builds and Runs to the needed Output. In a
shared repository, the Source and Run establish which target an entry belongs to; an output name
alone does not. Write that exact choice into the Run. Results retain public Outputs even when no file
was exported into `assets/` or `output/`; inspect them before concluding that material is missing.
A failed or cancelled Build may still contain completed public Outputs worth using. Reuse those
Outputs rather than submitting their generation again to recover a later failure. A later Build
that forwards an earlier Output does not copy its bytes. New structured Outputs also keep references
to reused media inside them; wrapping a video in another value does not create another video file.

A `<file>` Candidate refers to the selected file. Replacing that file changes subsequent reads;
removing it leaves a missing dependency. A new Build records the selected reference without copying
the file into every Result. A Candidate that generates new media saves its new output normally.

The current Build's generated media normally continues downstream as the material for the commissioned
work. Reusing it explicitly lets Caption, MG, Effects, composition, and final encoding change without
submitting the same paid media requests again. The following examples locate the reuse boundary:

| Current change | Keep through Candidates | Recompute or request |
| --- | --- | --- |
| Caption appearance, MG, an Effect or composition changes | Existing normalized media, local domains and alignment evidence that still apply | The changed visual systems and render |
| Moment/Selection placement changes, with unchanged spoken tokens and alignment identities | The accepted media, local domains and alignment evidence | Current Script references, their projections and presentation |
| Cue grouping, word attributes or display-only Dual wording changes without changing speech tokens | The accepted media, local domains and alignment evidence | The current CaptionDocument and its presentation |
| Temporal placement or complete Timeline extent changes | The normalized media, local domains and alignment evidence | Timeline assembly, all affected projections, media occurrences and presentation |
| Only some B-roll images must change | The existing performance, voice and all other still-useful media | The deliberately replaced images and their downstream composition |
| The presenter changes while the spoken argument still fits | Unaffected B-roll, icons, music and other media that still serve the target | The new presenter images, affected performances, their normalization and semantic timing, and downstream composition |
| A new product changes the demonstration or claims | Views and media whose content still fits the new Treatment | The affected product views, performance, Script-dependent timing and visual treatment |
| The same video needs different normalization or semantic timing | Its generated video Output, or normalized media when that still applies | The affected normalization or alignment and downstream consumers |
| New spoken wording requires a new performance | Unaffected media and other still-useful inputs | The changed performance and the timing derived from it |

Choose an Output upstream of the work being changed, with the same nominal Type and the intended
creative meaning. Media, its local temporal domain and its NarrativeAlignment are independent reusable
facts; retain exactly the ones that still apply. Alignment evidence is valid only while its Narrative,
Segment, token and anchor identities and timing still describe the current Script and media. A Script
edit does not automatically invalidate all media or alignment; inspect what changed. Markers select
existing token/Segment anchors. Moving a marker can therefore reuse accepted alignment when those
anchors and spoken tokens remain the same; no acoustic measurement is needed merely because a cue now
follows another word. Changing spoken text, tokenization, Segment identity or the source performance
requires a fresh judgment about the affected alignment. Keep upstream media when it still fits and let
only the required preparation recompute. No reuse selection silently adapts old evidence to new speech.

Do not satisfy a changed Track or final composition with its old rendered Output, which would hide
the current edit. Type compatibility alone cannot establish that an old performance or timing still fits.

After a person or product swap, review existing Candidate selections against the new target. A Run
that still selects the old presenter's video will keep that person on screen even after the image
prompt changes. Preserve unrelated work while selecting or generating the media the adaptation needs.

For example, correcting three wrong B-roll selections means replacing those selections while keeping
the produced performance. Inspect the resulting plan: the new image requests may be intended; a new
performance request is not explained by that correction. [Builds](builds.md) covers submission and
inspection when an earlier attempt may still be running.

## Revise the fact at its owner

Before editing an existing production, establish the current facts that can affect the change. Read the
relevant parts of its Brief and Treatment and the affected Source, Recipe or Run; inspect Results and
Runtime activity when reuse or active execution matters. Read the relevant diff and preserve unrelated work.

- Revise Treatment when the creative design changed.
- Revise Script when words, Cue membership, Selections, or Moments changed.
- Revise Source or Recipe when composition, parameters, or authored timing relations changed.
- Revise the Run when the demanded deliverable or selected Candidate changed.
- Revise a project package when its fixed or reusable behavior needs to change; an unexposed local
  design detail can be edited there without creating a new parameter.
- Revise a media request when the desired shot or the user's requested media has changed.

Generated Result bytes are evidence and reusable inputs, not editable Source. A change that still
uses existing media should keep selecting it. A change that intentionally requests new paid media
should first make the additional request visible in `hypit plan` and then follow the user's spending
authority.

## Use each view for what it can establish

`hypit check` establishes Source and graph legality. `hypit plan <run>` shows the selected graph and
external requests without submitting them. Studio opens that same Run for visual authoring.
Only `hypit build <run>` submits work and creates a fresh Build Result. None of those facts alone says
that the video is creatively successful; review the visible work as described in `review.md`.
