# LUT Format Notes

## .cube Defaults

Use `.cube` as the default deliverable because it is broadly accepted by video, photo, and game tools.

Default header:

```text
TITLE "Look Name"
LUT_3D_SIZE 33
DOMAIN_MIN 0.0 0.0 0.0
DOMAIN_MAX 1.0 1.0 1.0
```

Write RGB triplets as floats in `0..1`. For 3D LUT data, use red fastest, then green, then blue:

```text
for b in range(size):
  for g in range(size):
    for r in range(size):
      write transform(r, g, b)
```

This yields the identity sequence for size 2:

```text
0 0 0
1 0 0
0 1 0
1 1 0
0 0 1
1 0 1
0 1 1
1 1 1
```

## Size Selection

Use `17` for fast drafts or realtime constrained contexts, `33` for normal creative delivery, and `65` for smoother high-end grading. Avoid very large LUTs unless the destination tool supports them.

## Compatibility

Many editors ignore comments but accept them safely. Keep headers simple. Avoid negative domains or non-`0..1` output unless targeting a known technical workflow.

## Validation

Check that:

- `LUT_3D_SIZE` exists and matches the entry count.
- Every RGB value is finite and usually in `0..1`.
- The LUT does not have unexpected interior clipping.
- Neutral grey drift is intentional and not accidental.
- The generated preview matches the described style.

## Shared normalized reader (v5)

`cube_io.read_cube` is shared by previews and validation (and therefore by strength mixing and chain loading). It accepts sizes 2..128, UTF-8 BOMs, inline comments, and optional default domain headers. It rejects unsupported/duplicate headers, 1D or combined LUTs, non-default or non-finite domains, malformed/extra/missing rows, and non-finite or non-0..1 outputs. Values are never silently clipped or remapped. Extended-range .cube files may be valid in other workflows; they are outside this reader, not universally invalid.
