# First run: make the next step visible

Use this for installation, “what now?”, or a new filmmaker. Resume an existing film from its status instead of running setup again.

## Establish what is installed

Read VERSION next to SKILL.md. Run `python3 scripts/project.py doctor --task plan` and `python3 scripts/self_test.py` from the skill directory (or use absolute script paths). Both work without an editor, footage or FFmpeg. Do not assume the repository root, tools/ or examples/ were installed with the skill.

Explain in the user's language: this is guidance and local helpers for an agent, not an application that starts editing when installed. State the version, actual ability to view/listen, and supported operations. READY means helper prerequisites are available; it does not mean an editor is connected or a film has been reviewed.

## Choose one useful start

Use information already supplied. Ask only for missing footage/workspace locations, the editor if relevant, and the desired first scene or result. An undecided editor is fine. If no footage is available, walk through an illustrative scene plan or run the installation check; label invented examples. The repository's optional color-bar test checks timing, not creative output.

If footage is supplied, run `project.py doctor --task catalog --source SOURCE` to check folder access. Explain separately whether you can read files, run helpers, inspect moving images, listen/transcribe, and operate the chosen editor. Mark each capability as tested, unavailable or not yet checked; installed files alone do not establish any of them.

For footage, create a separate workspace using `project.py init` only if it is new. Catalogue the selected media folder outside the originals. For a large trip, inventory the trip and choose one scene for detailed review; report what has actually been watched. Read the catalogue summary and failed/skipped entries. Exit code 2 means empty or partial results need attention; do not hide failed files or infer coverage from the included count. Build visual coverage before speech selection, then a scene plan with facts, source ranges, gaps and useful memory questions. Do not claim a finished scene from metadata alone.

## End the first step with something usable

Give the user links/paths to the catalogue, scene plan and STATUS, explain each in one sentence, and state what is ready and what remains. Example structure (fill it with observed facts):

- “Installed version …; planning check …; viewing/listening available through ….”
- “I catalogued … files. I inspected … ranges; … remains unviewed.”
- “Here is the proposed scene, the evidence behind it and the questions that affect it.”
- “Next I can assemble … in …; this route preserves … and cannot yet ….”

When the user requested only a plan, stop at that result. When editing is already authorized, continue the scoped work without demanding the same approval again. If no native adapter is available, make the manual assembly plan concrete or use the silent preview when it serves the request; do not pass it off as a dialogue/music edit.

Record accepted preferences and open feedback in the film workspace. Installing or updating this skill must not create film memory inside its own folder.

## Manual assembly and the next session

Alongside the narrative plan, provide a table with source file, IN/OUT and units, shot role, selected speech, music intention and transition. Unknown source ranges stay unknown until inspected. If no editor adapter is available, describe the concrete trim, order and audio actions the user can perform; distinguish a proposed instruction from an action already executed. Read the plan-formats reference before producing a helper shot plan.

Save STATUS with timestamp/timezone, operator role, current version, sources and export identity (or “none”), actual checks, open questions, running processes and the next action. Give a resume prompt pointing to that workspace's STATUS, scene, preferences and selected feedback. Preserve the previous entry; do not manufacture acceptance, viewing or listening evidence.

The helpers run locally, but model and connected-tool operations depend on the user's agent setup. Explain this when choosing a source-processing route; photos and email remain optional.
