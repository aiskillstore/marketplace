# Design Philosophy

## Vanilla-First

Modern CSS and HTML are powerful enough that most projects don't need frameworks, preprocessors, or build tools. The web platform has evolved — use it.

## The Ponytail Ladder

Stop at the first rung that holds:

1. **Does this need to exist at all?** Speculative need = skip it. (YAGNI)
2. **Already in this codebase?** Reuse existing patterns. Look before you write.
3. **Stdlib does it?** Use native HTML elements and CSS properties.
4. **Native platform feature covers it?** `<dialog>` for modals, `<details>` for accordions, CSS over JS.
5. **Already-installed dependency solves it?** Use it.
6. **Can it be one line?** One line.
7. **Only then:** the minimum code that works.

## Why This Works

- **Faster pages:** No build step, no framework JS, no hydration.
- **Simpler debugging:** You can read the CSS. It's right there.
- **Longer lifespan:** No dependency updates, no breaking changes from upstream.
- **Better accessibility:** Semantic HTML gives you keyboard navigation and screen reader support for free.
- **Easier onboarding:** Any developer can read and understand vanilla HTML/CSS/JS.

## When to Reach for a Framework

When you have a concrete, experienced problem that vanilla can't solve elegantly:
- Complex state management across many components → consider a reactive framework
- Need for a rich component library with accessibility built in → consider a component framework
- Team of 10+ developers who need conventions → consider a CSS methodology

But start with vanilla. Add complexity only when the pain is real.
