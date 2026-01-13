# UI / DOM Debugging Tips

## Common causes
- CSS specificity conflicts
- Hidden/overlapping elements (z-index)
- Pointer-events blocked
- Missing data bindings
- Incorrect responsive breakpoints

## Evidence to gather
- Element text/role in snapshot
- Computed styles (display, position, z-index)
- Box metrics (client/offset/rect)

## Typical fixes
- Simplify selectors
- Adjust z-index stacking context
- Fix layout container sizes
- Ensure data exists before render
