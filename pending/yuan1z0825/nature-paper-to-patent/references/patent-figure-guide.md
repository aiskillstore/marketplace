# Patent Figure Guide

## Method Flowcharts

Build the main method flowchart from the ordered operations in the independent method claim.

Use:

- black strokes and white fills;
- rectangular process nodes;
- solid directional arrows;
- figure numbers such as `图1`;
- step identifiers such as `S1`, `S2`, and `S3`;
- concise Chinese operation labels.

Write the final node as the concrete result of the method. Examples include:

- `输出缺陷检测结果`;
- `获得故障检测结果`;
- `输出目标探测结果`;
- `获得电池健康状态估计结果`;
- `输出目标类别和目标位置`.

Keep the result name identical to the independent claim. Do not use invented umbrella terms such as `技术结果`.

## Abstract Figure

Use the main overall method flowchart as the abstract figure unless another single figure better represents the principal technical solution.

The same figure may and normally should also appear in the specification as `图1`. Reuse the same drawing file, figure number, node labels, and arrows. Do not generate separate "abstract" and "specification" versions that differ in wording or flow.

The abstract figure must:

- represent the principal independent claim;
- show the main input, core operations, and specific output;
- remain readable without equations or experimental details;
- be generated as both SVG and PNG;
- be embedded in the abstract-figure DOCX, abstract DOCX, and specification DOCX.

Avoid:

- color as the only carrier of meaning;
- gradients, shadows, decorative icons, or photographic backgrounds;
- unsupported branches or modules;
- effect-only nodes such as "提高准确率";
- vague final nodes such as `输出技术结果`, `获得处理结果`, or `输出最终结果`;
- dense equations or experimental results inside nodes;
- inconsistent terminology between the figure and claims.

## Consistency Rules

Confirm:

1. every `claim_step` appears in a method claim;
2. an overall figure marked `complete_claim_flow` covers every numbered step of its referenced claim;
3. node order follows the claimed data flow;
4. every edge connects existing nodes;
5. every node is reachable in the intended flow;
6. the figure description uses the same figure number and title;
7. the embodiment explains each node's operation;
8. optional details remain outside the main flow unless they form a disclosed branch.
9. `abstract_figure_number` points to an existing complete main figure;
10. the abstract and specification reuse the same image file.

## Figure Set

For algorithm-related inventions, consider:

- overall method flowchart;
- system or model architecture;
- core module structure;
- training flow;
- inference flow;
- data preprocessing flow.

Generate only figures supported by the source. The bundled script currently renders deterministic method flowcharts. Describe unsupported figure types as `[TO CONFIRM: figure required]` rather than fabricating them.
