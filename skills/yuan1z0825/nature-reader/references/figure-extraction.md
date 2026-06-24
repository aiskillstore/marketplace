# Figure and table extraction

Open this reference when extracting and placing figures or tables. It expands step 4 of the reading workflow.

## Placement near the relevant discussion

Do not try to recreate the PDF pixel-for-pixel. Preserve semantic proximity instead.

Default placement rule:

- crop each figure/table into `assets/` and show it near its first substantive mention in the body text
- keep the caption attached to the figure/table
- show both original caption and Chinese caption translation
- if the caption contains critical details, keep caption and figure together
- if a table is central to the claim, keep it near the paragraph that interprets it
- if a figure/table appears before the body discussion in PDF layout, still place it where it best supports the reading flow and add `Placed near: p.X SYYY`
- if a later section mentions the same figure/table again, link back to the already inserted figure/table block instead of duplicating it

If the paper has a complex multi-column layout, prefer a clean reading layout over exact visual mimicry.

## Crop figures and tables tightly

When extracting a figure or table image:

- crop only the figure or table content area, not the whole page
- use the smallest rectangle that fully contains the visual object
- exclude page headers, footers, surrounding prose, and unrelated margins
- keep the caption separate unless the caption is part of the requested visual crop
- if the crop box is uncertain, mark it as approximate instead of enlarging it

Precision matters more than convenience here. A slightly smaller but correct crop is better than a wider crop that includes unrelated page content.

## Figure/table block shape

Figure/table blocks in `paper.md` should use this shape:

```markdown
<a id="F001"></a>
### Fig. 1. [short translated title]

**Placed near:** p.3 S012
**Source:** p.4 C001

![Fig. 1](assets/fig1.png)

**Original caption:** [caption text]

**中文图注:** [caption translation]

**Reading note:** [brief explanation of what to inspect in the figure]
```
