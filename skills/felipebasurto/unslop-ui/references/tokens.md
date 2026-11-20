# Surface values

Fix targets for U17 to U20, and nothing else: there is no rule here for type sizes, radii or the palette, so leave those as they are. When the project already has a token system (Tailwind theme, CSS variables, a design-system package), use its values and only fix where the code bypasses them. These numbers are the fallback, not a house style.

## Contents
- Gradients, glows and depth (U17)
- Spacing (U18)
- Weight (U19)
- Motion (U20)

## Gradients, glows and depth (U17)

- A gradient is allowed only as a tone shift inside one neutral. A gradient from one hue to another, gradient text, colored glows and blurred color blobs go.
- The replacement surface is solid and comes from the neutral the screen already uses. The replacement text color is the one its siblings use.
- Depth is a surface step plus a hairline border: the text color at 6 to 10% opacity.
- Where a shadow earns its place, keep it neutral and small: `0 1px 2px rgb(0 0 0 / 0.05)`, or `0 8px 24px rgb(0 0 0 / 0.06)` for something floating.
- Text on the new surface keeps a contrast of at least 4.5:1.

## Spacing (U18)

Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64. Inside a control, 2, 6, 10 and 14 are also steps (Tailwind's `0.5`, `1.5`, `2.5`, `3.5`).

| Where | Value |
|---|---|
| Inside a control | 2 to 12 |
| Between rows in a list | 2 to 8 |
| Between groups (a label and its list, two cards) | 12 to 24 |
| Between sections | 32 to 64 |
| Card padding | 16 to 24, one value for sibling cards |

Space inside a group is smaller than space between groups. An off-scale value moves to the nearest step, written as the scale class when one exists (`mt-[13px]` becomes `mt-3`, `py-[10px]` becomes `py-2.5`). An odd value that exactly centers something can stay.

## Weight (U19)

Weights 400 to 600. 800 and 900 become 600, or 500 where siblings already use it. Hierarchy comes from size and color, which this rule does not change.

## Motion (U20)

| Use | Duration |
|---|---|
| Hover, press, toggle | 120 to 180ms |
| Menu, popover, tooltip | 160 to 220ms |
| Entrance, layout change | 300 to 400ms |

One easing curve for the screen: `cubic-bezier(0.22, 1, 0.36, 1)` or the framework's ease-out. Transition named properties (`transition-colors`, `transition-[opacity,transform]`), never `all`. A press scales to 0.97 to 0.98. A card does not scale on hover. Keep motion that explains something (a menu rising a few pixels, a number tweening) and drop loops and bounces.
