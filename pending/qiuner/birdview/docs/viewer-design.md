# Birdview viewer design

[中文](viewer-design.zh.md)

Status: the single demo entry is examples/harness-activity.html. The shared viewer
supports architecture, changes and comparison modes, collapsible activity details,
linked pane navigation, a closable inspector and single-level groups. Activity is
an agent-declared file snapshot; live integration remains future work.

## Objective

Make the system and the agent's intended change readable at a glance. The canvas
is the primary surface. Module evidence supports inspection without dominating
the initial view. Keep the standalone HTML delivery and existing language support.

## Architecture meaning

Birdview's existing local/external kind describes code ownership. An external
database can still be inside a product's deployment. Do not derive a system or
trust boundary from kind, directory names or screen position alone.

Propose optional authored groups with stable IDs, names, member module IDs and
source evidence. Begin with one grouping level for systems or subsystems. Keep
deployment/trust boundaries out until supported by an actual use case. Translate
group labels using the same language convention as modules. Without groups,
render the original flat map; do not invent membership for visual appeal.

## Composition

- Compact header: Birdview, project name, language and theme. Move map revision
  into secondary metadata and remove the large duplicate project title band.
- Canvas toolbar: architecture/changes/comparison views, fit, zoom and flow toggle.
  Without activity records, present architecture only; no inactive view controls.
- Give the diagram the available width. Initially keep the inspector closed.
  Clicking a node opens a 300-340 px inspector; closing it restores canvas width.
  On mobile, details expand below the graph. Refit only in automatic fit mode.
- Fit the complete map with readable authored spacing; preserve original-size
  zoom for close inspection. More modules must not mean larger empty margins.
- Use group frames with a quiet tint, clear heading and reserved heading space.
  Keep external dependencies outside only when membership data says so.

## Visual language

- Retain black/white themes. Use neutral canvas and panel surfaces with restrained
  cyan, green and amber accents; avoid giving every node the same green cast.
- Nodes retain centered name, short responsibility and 8 px corners. Use role
  icons or small accents only when role data exists; do not infer database roles
  merely from external ownership. Complete descriptions stay in the inspector.
- A group frame means membership. It must not resemble a task scope outline.
- Hover highlights adjacent relationships and previews their direction. Click
  selects details. Neither interaction may imply that a node is being modified.
- Reserve the strongest glow for the current AI modification target. Planned
  scope uses an outline; unrelated modules dim only in an explicit activity view.
- Show relationship labels on inspection, with selected labels readable on the
  canvas where space permits. Keep direction arrows and reduced-motion support.

## Delivery sequence

The architecture viewer routes connections through obstacle-free orthogonal
corridors with 10 px module clearance and up to 6 px corner rounding. Shared
ports are spread along the chosen side. Route cost favors shorter paths and
fewer bends, with penalties for crossing or overlapping earlier routes. This
is a local heuristic, not a guarantee of crossing-free layout. Diagonal connections
prefer perpendicular endpoint sides with fewer occupied ports. Extra lanes sit
8 px beyond obstacle corridors; parallel proximity is penalized by overlap length
to discourage crowding without making costs depend on grid subdivision. This can
trade some route length for separation and does not enforce a hard minimum gap.
Group borders
and group headings are not routing obstacles. Routing preserves authored node
positions and uses no network assets or additional runtime dependencies.

Grid track order is preserved, but screen spacing adapts to authored edge density.
Each internal track boundary adds 12 px per crossing relationship beyond two,
capped at 96 px. Grouped maps measure each group's internal relationships;
ungrouped maps measure the full graph. All relationships count, including detail
edges, so hover and visibility changes do not relayout the map. Routing can use
mid-corridor tracks and two bottom perimeter lanes; these are candidates, not
forced paths. The larger canvas may require zooming on narrow viewports.

1. Implement the compact header and closable inspector against current data.
2. Add optional groups to schema, validation, authoring instructions and renderer
   together. Reject unknown/duplicate membership and overlapping sibling groups.
   Arrange groups without enclosing unrelated nodes or covering node text.
3. Build a representative 8-12 node fixture with an application group and explicit
   external dependencies. Keep the two-node bilingual fixture for language tests,
   not as the primary visual benchmark.
4. Render declared planned/current activity on the same map, with a full overview
   alongside it in comparison mode. Use the same positions and shared navigation.

## Acceptance

The header contains the project name without a separate module total. There is no standalone footer; the existing graph legend retains scale and relationship visibility information.

Relationship, flow and zoom controls are directly available in the map toolbar; there is no secondary tools menu.

In Changes, keep the selected step's full reason visible beside the history controls, with an expandable file/check section below and an explicit simulation or agent-declared source label. The summary must remain accessible with the inspector closed. On narrow screens, wrap the controls and scroll long expanded details within the activity panel. Architecture and comparison views hide these history controls and details.

Check dark/light themes and Chinese/English at 1440x900, 1280x720 and 390x844.
Verify group containment, no label collisions, inspector open/close, fit/manual
zoom preservation, hover restoration and keyboard selection. Render legacy maps
without groups. All graph text remains escaped; the HTML has no network assets.
Long evidence remains accessible without forcing a permanently tall empty canvas.
