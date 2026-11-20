---
name: openmotion
description: Create and edit videos with OpenMotion, recreate a reference video, or adapt an editable template. Set up the local Studio and MCP connection when missing, then continue through the matching production workflow. Use for OpenMotion installation and first use; an already-selected specialist continues directly. Repository development does not trigger video production.
---

# OpenMotion

Turn a reference, template or creative brief into an editable video project in the local OpenMotion Studio, with preview and MP4 export through the same workspace.

## Connect once

Discover the current host's OpenMotion MCP tools first. If connected, call `openmotion_get_project` to identify the workspace and resume existing work. Preserve projects, credentials, project/version identities and unrelated host settings. Do not reinstall a working connection.

If OpenMotion is missing or disconnected, read the maintained [installation guide](https://github.com/nexu-io/openmotion/blob/main/docs/install.md) and follow its current-host instructions. Source installation is the repository default; follow that same guide's published-application section only when the user explicitly chooses npm. Reuse an existing installation rather than mixing source and npm. Derive onboarding language from the user's request. Follow the guide's shared welcome, three-card and template-library procedure. Show cards whenever this host supports them; use the same three recommendations as text only when card presentation is unsupported or fails. Do not treat the host name as a capability check.

Installing this Skill with Skills CLI installs instructions only. Complete runtime, Studio, MCP and the guide's browser/media prerequisites before claiming production readiness. Use actual startup URLs and transport settings; the Studio URL is not an HTTP MCP endpoint. This version provides local stdio, not a ChatGPT cloud endpoint. Native tools must be discovered and `openmotion_get_project` must succeed in the calling host before claiming that host is connected. A standalone probe has a separate verification scope. Report the concrete blocker when host recovery is needed.

Installation alone does not request a film, project edit, export or paid generation. If the user only asked to install, finish the maintained onboarding and wait. If they already supplied a creative brief, continue with it after setup.

## Continue with the matching workflow

Read the selected installed Skill, or its full MCP resource through `resources/read`. Resources remain available when only this entry Skill was installed; do not depend on sibling files in a standalone Skills CLI copy.

| User intent | Skill | MCP resource |
| --- | --- | --- |
| Original video, narrative, motion or sound design | openmotion-director | `openmotion://workflow/director/start` |
| Browse or adapt an existing editable template | openmotion-template-to-video | `openmotion://workflow/template/start` |
| Recreate a reference video for this film | openmotion-recreate | `openmotion://workflow/recreate/start` |
| Turn a reference into a reusable template | openmotion-video-to-template | `openmotion://workflow/video-to-template/start` |
| Scoped edits under established decisions, preview, troubleshooting or export | openmotion-production | `openmotion://workflow/production/start` |
| Generate an individual image, video, speech or music asset | openmotion-media | `openmotion://workflow/media/start` |

Continue directly in that workflow, preserving the user's brief and existing decisions. These are instructions for the same Agent, not recursive tasks or a new creative intake. The selected workflow owns reference reading, revision protection, asset generation, preview and delivery. Read its conditional references as needed; do not load every workflow. Technical export validation, actual playback and human visual acceptance remain separate.
