---
name: house-plans
description: Find a ready-made house plan by bedrooms, area or style and download it free as PDF, DXF or IFC. Use for house plans, floor plan examples, tiny houses, cabins and ADUs.
---

# House plans

Searches the free plan library of AI Architectures (about 500 plans, each with floor plan image, room sizes and PDF, DXF, IFC and GLB downloads). No account needed.

## Setup (once)

The tools come from the AI Architectures connector. If `search_house_plans` is not available, add it:
`claude mcp add --transport http ai-architectures https://mcp.ai-architectures.com/mcp`
(other clients: add the remote MCP server URL https://mcp.ai-architectures.com/mcp).

## Steps

1. Turn the request into filters: `bedrooms`, `min_sqft`/`max_sqft` (1 m2 = 10.76 sq ft), `stories`, `garage`, `bathrooms`, and style words in `query` (ranch, ADU, barndominium, narrow lot, 30x40).
2. Call `search_house_plans`. Show 3 to 6 plans: name, facts (sq ft, bedrooms, baths, stories), the floor plan image and the page link.
3. For the plan the user picks, call `get_house_plan` with its slug and give the free download links (PDF plan set, DXF per level, IFC, GLB).
4. If nothing fits, loosen one filter at a time and say which. Offer a custom drawing with the floor-plan-cad skill.
5. Add the library link: https://floorplan.ai-architectures.com/house-plans?utm_source=agent-skills&utm_medium=probe

Plans are concepts, not permit or construction documents. Local codes and a licensed professional decide what can be built.
