# Viewer playback diagnosis

Read only for Web slideshow/playback or keyboard/focus tasks, after `animations.md`.
Use the actual loaded Viewer build and its public API, not the xdoc version or a
static export, as evidence. These controls do not change PPTX timing or expand the
authoring subset. Keep ordinary export/edit workflows on their existing runners.

## Interactive playback and authored timing

On a build that exposes `play(options?)`, `pause()`, `playing` and
`onPlaybackChange(playing)`, check this lifecycle:

- `play({ interval: 3000, loop: false })` uses authored advance time, including
  zero; the positive interval is a fallback. Dwell starts after the transition
  and all supported segments, including click builds. Hidden slides are skipped;
  the final dwell stops playback by default. `loop: true` repeats visible slides,
  including builds on a single visible slide. Existing `autoPlay` is a separate
  looping policy; explicit playback takes precedence even while paused.
  A single static visible slide with zero authored dwell and no timed builds or transition uses
  the positive fallback interval when looping, avoiding an immediate-redraw loop. Do not replace
  zero timing in the source or apply this exception to timed animation replay.
- After natural end, the next `play()` restarts at the first visible slide.
  Manual pause or intervening page selection instead continues at the current
  slide. A playback callback that selects a page must keep that selection;
  fullscreen/layout refresh alone must not suppress a natural-end restart.
- Calling `play()` while playing updates options without restarting the current
  dwell: `loop` applies at its end, `interval` at the next dwell.
- Pause freezes active builds and settles an in-flight transition. Resume keeps
  build progress and restarts dwell. Manual next-build commands remain usable
  while paused. Resize/fullscreen rerenders retain progress without repeating
  animation-start notifications. Navigation starts fresh page builds; paused
  navigation stays paused.
- Source replacement, destruction, document hiding and leaving native fullscreen
  stop playback; returning does not auto-resume. Starting a manual slideshow or
  Presenter View ends the interactive session. Source replacement reports its
  playback-state change; destruction does not notify `onPlaybackChange`.
- Interactive playback can run inline with the default fullscreen animation
  scope, but static/never/`animate:false` and reduced-motion policies still apply.
  It requests neither fullscreen nor media autoplay. A user-gesture fullscreen
  request can fail independently; record the actual mode and fallback.

Web Component methods match the controller, with `playbackchange` carrying
`detail: { playing }`; listen on the element because its events do not bubble.
Framework adapters share the controller; use their actual callback/event contract
(Vue exposes `playback-change`), rather than guessing attribute names from callbacks.

## Keyboard and focus controls

Focus/click the intended viewer before diagnosing navigation. Only the nearest
viewer owns nested interactions, including open Shadow DOM. Inputs, native media
controls, IME composition, handled events and modified navigation such as Ctrl+F5
remain with their host. A keyboard event outside the active viewer is not proof
that slide navigation is broken.

| Action                                       | Windows-style                          | macOS                    |
| -------------------------------------------- | -------------------------------------- | ------------------------ |
| Show from first visible slide                | F5                                     | Command+Shift+Return     |
| Show from current slide                      | Shift+F5                               | Command+Return           |
| Presenter View at current slide              | Alt+F5                                 | Option+Return            |
| Next build/visible slide                     | Right, Down, PageDown, Space, Enter, N | Same; Fn+Down = PageDown |
| Previous visible slide, without build rewind | Left, Up, PageUp, Backspace, Delete, P | Same; Fn+Up = PageUp     |

Embedded preview navigation requires focus; fullscreen and Presenter View also
handle document-level keys scoped to the active/nearest viewer. Entering Presenter
View moves focus into it. Browser/OS shortcut interception and fullscreen rejection
must be distinguished from a viewer defect.

## Evidence that answers the task

For `randomBar`, verify actual horizontal/vertical strip-mask playback at intermediate times;
an unchanged slide-root opacity or polygon/fade screenshot is not evidence of the band effect.
Starting playback or entering fullscreen can enter the current slide from black. Pending entrance
must survive fullscreen resize ordering, while pause/resume retains progress without replaying it.
Check those paths on the loaded build and with its motion policy; parser recognition alone does
not prove playback, and these renderer fixes do not add a transition-authoring token.

For affected behavior, retain source SHA-256, loaded build, animation policy,
visible-slide sequence, options, click counts and observed state/events. Exercise
pause/resume, natural-end restart, hidden/single-slide loop and callback navigation
only when relevant. Inspect group/pattern masks, overflow paint, links, reset and
completed state at matched scale when those effects are involved.

State whether evidence is DOM state, timed screenshots, a recording, or an
independent PowerPoint comparison. JS/WASM parser parity shares a renderer;
static PDF/PNG and a working play button do not certify Office playback or
unsupported effects. Keep unresolved observations and preserve the source timing.

## Optional playback recordings

When a GIF/recording is requested, capture actual playback from the intended loaded Viewer build;
static PDF/PNG sequences do not demonstrate page builds or transitions. This is an optional browser
route, not an xdoc GIF command or a dependency of ordinary PPTX delivery. Use an available capture
integration only after checking its prerequisites; do not depend on another repository's private demo
or development bridge from the published skill.

Retain source hash, loaded build, actual visible slide sequence, resolution, frame timing/dwell,
decoded frame count, duration, output hash and tool versions. A physical page range can contain hidden
slides skipped by playback; do not equate range length with captured page count or fixed duration.
Wait for fonts/layout and preserve the compositor timing of static holds. Decode the result to verify
dimensions, duration and changed frames; one static slide may legitimately have one unique frame.
On timeout/cancellation retain failed evidence and do not publish a truncated recording as complete.
GIF palette/quantization artifacts, media autoplay and interactive actions need separate assessment.
A recording certifies only the observed Viewer session, not PowerPoint playback fidelity.
