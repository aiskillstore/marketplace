# Camera movement and shot boundaries

Review every selected range, its source handles and its appearance in the actual export, including upper video layers, nested clips and retiming. A full-source classification does not validate a particular IN/OUT. Reuse a review only when the range, processing and visible result match.

Identify phases: starting movement, purposeful pan/zoom/follow, slowing, stopping, reframing and a late new movement. Inspect possible reversals, zoom-in then zoom-out, or a sideways correction after a retreat. Keep purposeful reframing and following people; zero movement is not the objective. Select a complete useful gesture and allow time to read the subject, even after speech ends. Do not freeze or stretch video merely to hide searching.

Review the selected range and both cuts at playback speed. Direction, axis, eye line, subject position and action phase must work across adjacent shots; a different crop alone does not create development. After repeated feedback about searching, recheck all shots in the affected scene, including earlier selections.

If available, use frame-to-frame motion measurements and a locally tested motion classifier to flag intervals for review. Optical flow measures image movement, not certain physical camera motion: foreground objects, parallax, reflections and rolling shutter can mislead it. Test the classifier against known examples on representative footage; preserve disagreement and low confidence. These models and optical-flow helpers are not bundled in this release. Do not invent a machine PASS when they are absent; record the viewing coverage and missing analysis.

Record source file/range, motion phases, flagged intervals, retain/trim decision, evidence/method and export version. Contact sheets and classifications can locate a concern; neither proves smooth playback or editorial value.
