---
name: floor-plan-cad
description: Turn a brief or a sketch into a measured floor plan as a CAD drawing (DXF, DWG, PDF). Use for floor plan drawings, sketch to CAD and image to DWG.
---

# Floor plan as CAD

Hands a floor plan brief to the Plan Chat CAD studio of AI Architectures, where it is drawn as a layered CAD plan with DXF, DWG and PDF.

## Setup (once)

The tool comes from the AI Architectures connector. If `prepare_cad_drawing_link` is not available, add it:
`claude mcp add --transport http ai-architectures https://mcp.ai-architectures.com/mcp`

## Steps

1. Collect the brief in the user's words: building type, rooms, sizes, storeys, plot. Ask at most one question if the type or size is missing.
2. Call `prepare_cad_drawing_link` with the brief. Nothing is drawn or charged until the user presses send on the site.
3. Give the user the returned link, with this tag appended to the address: `&utm_source=agent-skills&utm_medium=probe`. Tell them they can attach a sketch there before sending.
4. Optional: example drawings https://cad.ai-architectures.com/community?utm_source=agent-skills&utm_medium=probe

Drawings are concepts, not permit or construction documents. Check dimensions and local rules with a licensed professional before building.
