# Pencil To Code Handoff Checklist

Use this checklist while implementing or debugging visual fidelity.

## Pencil Extraction

- Read every requested artboard node with `batch_get`.
- Read handoff/spec nodes at enough depth to capture responsive rules.
- Use `get_variables` and map core variables into CSS/theme tokens.
- Take Pencil screenshots for each artboard with `get_screenshot`.
- For repeated components, inspect direct children rather than relying on screenshots alone.

## Facts To Capture

- Artboard: width, height, fill, clip behavior.
- Foreground stack: width, x/y, gap, padding, min height, spacer heights.
- Cards/buttons/rows: width, height, padding, gap, radius, stroke, fill, blur, shadow.
- Typography: text, font family, size, weight, line-height, letter-spacing, color, text growth/fixed width.
- Icons/images: source file, mode (`fill`, `fit`, etc.), size, crop/object position.
- Background layers: image dimensions, fill mode, veil gradient, vignette ellipse size/position, mist size/position, wire line positions and colors.

## Code Mapping

- Make reusable components for repeated visual units before fine-tuning CSS.
- Use CSS variables for design tokens: colors, foreground width, top offset, spacer, radii, blur, shadow.
- Keep foreground as a single flex/grid stack when the design is single-column.
- Put background scene layers in a dedicated component with `aria-hidden="true"` and `pointer-events: none`.
- Prefer real exported assets from the `.pen` folder over recreating logos or photos.

## Background Rules

- Match Pencil image fill semantics:
  - `mode: fill` usually maps to `object-fit: cover` or CSS `background-size: cover`.
  - If the designer scaled the image within a larger artboard, preserve aspect ratio and adjust `background-size`, `background-position`, or `transform: scale(...)`.
  - Avoid `background-size: 100% 100%` unless the design intentionally distorts the image.
- Keep overlay layers separate from the image layer.
- Compare desktop crops carefully; a fix for mobile can break the wide artboard.

## Typography Rules

- Load the exact family used in Pencil when possible.
- If using `next/font`, ensure font CSS variables are in scope where they are consumed.
- Verify important labels with `getComputedStyle`, especially when text looks too bold or too generic.
- Match visual weight over nominal weight when browser rendering differs from Pencil.
- Preserve letter spacing exactly for labels and handles.

Useful browser check:

```js
Array.from(document.querySelectorAll(".selector")).map((el) => {
  const s = getComputedStyle(el);
  return {
    text: el.textContent,
    fontFamily: s.fontFamily,
    fontSize: s.fontSize,
    fontWeight: s.fontWeight,
    lineHeight: s.lineHeight,
    letterSpacing: s.letterSpacing,
  };
});
```

## Responsive Verification

- Test every provided artboard size, not just generic breakpoints.
- Confirm fixed foreground columns do not expand on tablet/desktop.
- Confirm footer/actions remain in the required layout at every breakpoint.
- Confirm minimum touch targets are at least 40-44px.
- Check for horizontal overflow after matching fixed-width designs.

## Final Checks

- Run the repository's required formatter/lint/type/build command.
- Capture browser screenshots at all artboard sizes.
- Compare against Pencil screenshots and name any intentional deviations in the final summary.
- Remove temporary screenshots or debug artifacts before finishing.
