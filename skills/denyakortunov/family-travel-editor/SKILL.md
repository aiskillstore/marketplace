---
name: family-travel-editor
description: Plan and edit travel videos and family films from camera or drone footage with AI assistance and the user’s preferred editor. Use for footage cataloguing, trip storytelling, scene planning, personal voiceover and timecoded review revisions while preserving an editable project.
---

# Family Travel Editor

This is a skill for an AI agent, not a standalone video editor. Help the filmmaker turn clips into a coherent film using their chosen editor. Work on one named scene or revision at a time; keep an editable timeline and evidence of what was checked. This skill needs local file access for media operations. Planning is editor-independent; native editing requires a supported editor adapter. Installing it does not install an editor, grant account access, or supply audio models.

## First use and continuing work

On a first invocation or setup request, read [first run](references/first-run.md). Explain what this installation can do, check it, and produce one concrete next step. Resolve scripts and templates relative to this SKILL.md, not the user’s working directory. Film files belong in a separate workspace. On later sessions, resume from that workspace’s current status and selected feedback instead of repeating onboarding.

## Start from the actual project

Find the user's workspace, current project/version, footage and preferences. Continue existing work when present. For a new project, use `scripts/project.py init WORKSPACE` to create empty planning files. Do not initialize over an existing project. Select a short representative scene before scaling to a whole trip.

Ask which editor the user already uses. Read [editor choices](references/editors.md) when selecting tools or replacing a service. Use `scripts/project.py doctor` for task-specific tool availability. Read [setup](references/setup.md) for the bundled commands and [Resolve operations](references/resolve.md) before touching Resolve. If the chosen editor has no available adapter, complete the catalogue, questions and scene plan; offer manual assembly or the explicitly silent FFmpeg preview without claiming native support. A generated XML file is not evidence of an imported or working Resolve timeline.

## Reconstruct the story

Read [story and context](references/story.md). Catalogue all footage, including non-speech clips. Separate observed facts, metadata, author memories and assumptions. Treat file timestamps, photo GPS and travel bookings as clues that can conflict. Use photos or selected emails only within the user's authorized sources; without them, ask focused questions and continue with known context.

View candidate ranges in motion and with surrounding context. A transcript or contact sheet alone cannot establish a good cut. Build a visual coverage map before selecting dialogue; include silent footage and reasons for excluding meaningful events. Map place → action → reaction/result → ending. Ask for memories where they change the story; never invent a remembered event or causal connection between different days.

## Edit a bounded scene

Read [editing principles](references/editing.md) and the user's preferences. Describe the intended change and protected material, then duplicate the timeline or create a new named version. Track source ranges, frame rates and each shot’s role, including beauty, atmosphere and spatial context. Before a helper export, derive a technical shot plan from the narrative scene using [plan formats](references/plan-formats.md); do not pass the narrative template directly to a timeline helper. Preserve complete selected thoughts, real reactions and meaningful motion. Adapt pacing to the scene, not a fixed shot length. Read [camera motion](references/camera-motion.md) for selected ranges and [preservation](references/preservation.md) before revising a timeline or rebuilding a mix.

Draft voiceover from confirmed memories. Let the author record it; do not fabricate missing family dialogue. Optional music, sound effects and models are choices, not required subscriptions. Record their provenance and check the actual resulting mix. Read [scene music](references/scene-music.md) when choosing music or shaping the balance of montage and live speech.

## Verify, review and learn

Read [checks](references/checks.md) for each new export or sound change. Compare the native timeline and actual rendered file. Identify the reviewed version by hash; distinguish measured, transcribed, model-reviewed, watched/listened and accepted by the author. Report untested intervals and unavailable checks. A command returning success is not artistic approval.

Apply feedback with [review and memory](references/review.md). Keep the original comment, timecode/version, concrete change and verification evidence. Reusable taste belongs in preferences; one-off cuts belong in the scene's feedback. Previous approval of an idea does not accept its execution.

Deliver the editable project plus a clearly labelled review export, remaining limitations and a short project status. Upload to Replay or publish on YouTube only within an explicit publishing instruction; preserve earlier versions and verify the actual delivered file. Save selected delivery metadata locally, not in the reusable skill.

## Bundled resources

- `scripts/self_test.py`: installation check using temporary metadata fixtures; no footage, editor, models or network required. It does not render or assess a film.
- `scripts/project.py`: workspace initialization, read-only catalogue, tool discovery, export measurement.
- `scripts/timeline.py`: validated, video-only straight-cut FCP 7 XML from an explicit shot plan. It is a technical interchange helper, not an automatic story editor or complete audio conform.
- `scripts/render_preview.py`: FFmpeg video-only preview from the same shot plan; requires ffprobe and rejects mismatched rates/dimensions/duration. No audio or editable native project.
- `scripts/resolve_bridge.py`: read-only connection probe and guarded XML import into an already open, empty, explicitly named project.
- `assets/templates/`: blank preferences, scene, feedback and status files. Copy them into the user's project; do not write personal data into the installed skill.

Paths in commands are supplied by the user or discovered locally. Helper scripts use only Python's standard library; FFmpeg/ffprobe and Resolve are separate optional executables. See the references for command arguments and limits.
