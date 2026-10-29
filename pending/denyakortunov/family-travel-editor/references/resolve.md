# Resolve operations

Release status: native import was not validated during v0.1.0 preparation because the live Resolve connection was unavailable. The XML-generation helper was tested separately.

Use the scripting documentation installed with the user's Resolve version. On macOS it is normally under `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/`. Studio and external scripting access may be needed; enable local scripting in the user's Resolve settings only as part of setup. Do not expose network scripting unnecessarily.

`python3 scripts/resolve_bridge.py probe` reads version and current project only. `--modules PATH` can point to the directory containing DaVinciResolveScript.py; `RESOLVE_SCRIPT_LIB` follows Resolve's own loader. A missing connection is a capability failure, not permission to modify another project.

For the included video-only interchange example, create a NEW empty project in Resolve yourself, name it `Family Travel Editor Demo`, then:

```sh
python3 scripts/resolve_bridge.py import-xml /absolute/path/to/timeline.xml --project 'Family Travel Editor Demo'
```

The importer requires that exact currently open project, zero timelines, zero media and zero subfolders. It refuses a populated project and never creates, switches or deletes projects. Importing and saving is a mutation requested by this command. Media needs to remain where the XML points. On failure, inspect the new project; the command does not claim rollback.

For real editing, duplicate a timeline, snapshot source IN/OUT and all video/audio/title tracks, and define what may change. Verify frame-rate and source-boundary semantics with a short probe on the current version; do not assume every API uses the same inclusive end. Check Fusion duration/keys after duplication. Activate the timeline being inspected before interpreting enabled-state or audio properties.

After editing, verify all preserved tracks and corresponding rendered output, save a versioned project export and hash it. A .drp contains project data, not original media. Never change paths or library storage merely to match the example. The bundled XML helper supports only integer 24/25/30 fps, same-rate video, straight cuts and no audio/effects/titles. Other timelines require a native workflow, not silent frame rounding.
