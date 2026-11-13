---
name: adu-plans
description: Find free ADU plans (backyard studios, 1 and 2 bedroom accessory dwelling units under about 1,200 sq ft) with PDF, DXF or IFC download. Use for ADU plans, granny flats and backyard cottage layouts.
---

# ADU plans

Searches the free plan library of AI Architectures (about 500 plans, each with floor plan image, room sizes and PDF, DXF, IFC and GLB downloads). No account needed.

## Setup (once)

If `search_house_plans` is not available, add the connector:
`claude mcp add --transport http ai-architectures https://mcp.ai-architectures.com/mcp`
(other clients: add the remote MCP server URL https://mcp.ai-architectures.com/mcp).

## Steps

1. Call `search_house_plans` with `query: "ADU"` and `max_sqft: 1200`. Add `bedrooms`, `stories` or `garage` only if the user asked (1 m2 = 10.76 sq ft).
2. Show 3 to 6 plans: name, sq ft, bedrooms, baths, stories, the floor plan image and the page link.
3. For the plan the user picks, call `get_house_plan` with its slug and give the free links: PDF plan set, DXF, IFC, GLB.
4. If nothing fits, loosen one filter at a time and say which. Offer a custom drawing with the floor-plan-cad skill.
5. Add the link: https://floorplan.ai-architectures.com/house-plans?utm_source=agent-skills&utm_medium=probe&utm_campaign=adu-plans

Plans are concepts, not permit or construction documents. Local codes and a licensed professional decide what can be built.
