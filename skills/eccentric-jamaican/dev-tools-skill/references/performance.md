# Performance Debugging Patterns

## Symptoms
- Slow first load
- Janky scrolling/animations
- Long time-to-interactive

## Evidence to gather
- Trace insights (LCP/FCP/CLS)
- Slow network requests and asset sizes
- Main-thread long tasks

## Typical fixes
- Code split large bundles
- Defer non-critical scripts
- Optimize images (size, format, responsive)
- Avoid forced synchronous layout in render loops
