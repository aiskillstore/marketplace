# Choose an editor and replace tools

The shared workflow produces a catalogue, confirmed context, scene plan, source ranges, voiceover, feedback and project preferences. These are portable. A native editable project is editor-specific: changing a brand name is not an adapter.

| Route | Without driving the editor UI? | Status in this package |
|---|---|---|
| FFmpeg | Yes: command-line trim and render | Bundled `render_preview.py`; silent straight-cut MP4 from validated same-rate media. No editable multi-track editor project |
| DaVinci Resolve | XML interchange; external Python scripting where the installed edition supports it | Bundled video-only FCP 7 XML and guarded bridge. Live native import/playback/export not yet validated. Studio is the target for the external bridge; planning and XML generation do not need it |
| Shotcut / MLT | Text MLT XML; command-line export with melt | Recommended open-source adapter candidate. No generator or round-trip validation bundled |
| Kdenlive | MLT rendering and generated render scripts | Candidate. A renderable MLT file is not automatically a fully editable Kdenlive project; native metadata must be tested |
| OpenShot / libopenshot | Video-editing library with Python bindings | Candidate. Library rendering and desktop project interchange need separate implementation and validation |
| iMovie / CapCut | No native automation adapter verified here | Use plans, shot lists, narration and timecoded feedback, then assemble in the UI. Do not promise unattended editing or modify undocumented project internals as if they were a stable API |

For a first session, ask which editor the user already uses and whether they want planning, a silent rough-cut preview, or an editable timeline. Do not require a paid editor to start. When a requested adapter is missing, deliver the portable plan and explain the remaining assembly step. Do not silently substitute a flattened MP4 for an editable project.

For any new adapter, first prove a small round trip: clips → source ranges → native project → reopen → render. Check frame count, cut positions, audio, relinking and preservation of unrelated material. Test in a separate project. Record editor version and platform. FCP 7 XML (`xmeml`) is not modern Final Cut Pro FCPXML, and neither is a universal iMovie/CapCut interchange format.

## Replace a service by its job

- Photos/GPS → selected photo metadata or the author's memory; retain confidence and provenance.
- Gmail/bookings → chosen travel records or answers; never assume new account access.
- Replay → versioned timecoded text, another review tool or an issue list.
- Transcription/audio models → any available ASR and listening tools with stated limits. Transcription alone does not judge music or stereo quality.
- Optional editorial second opinion → another available reviewer or human review. Optional, not a prerequisite for starting.
- YouTube → another delivery destination, with explicit publication instructions and verified output.

## Official references

Checked 27 October 2026; these establish tool capabilities, not compatibility testing of this package.

- [Shotcut command-line options and MLT inputs](https://www.shotcut.org/notes/command-line-options/)
- [Shotcut: export at the command line](https://forum.shotcut.org/t/export-at-the-command-line/44067)
- [Kdenlive rendering and command-line scripts](https://docs.kdenlive.org/en/exporting/render.html)
- [OpenShot video-editing library and language bindings](https://www.openshot.org/libopenshot/)
- [Blackmagic support and installed-version documentation](https://www.blackmagicdesign.com/support)

For Resolve scripting requirements, consult the Developer/Scripting documentation shipped with your installed version. Free and Studio capabilities differ; do not infer external scripting availability from successful manual XML import.
