# Platform status and implementation

State of the world as of the M3 guidelines and the Google I/O 2026 "Material Android is Compose-first"
announcement. **Check this before promising a user that an expressive feature is available on their
platform** — availability is uneven, and this is where confident-sounding answers go wrong.

## Library status

| Platform | Status | Gets Material updates |
|---|---|---|
| **Jetpack Compose (Material Compose)** | **Recommended for Android.** Built in-house, receives the latest Material updates first. | first |
| **Flutter** | Actively maintained by the Flutter team | periodic |
| **Android Views (MDC-Android)** | **Maintenance mode.** 1.14.0 is the **final stable release**. Critical bug fixes only, no new features. | no |
| **Web** | **Maintenance mode.** Still usable, no feature updates from Material. | no |

The Figma Design Kit and the design guidelines track **the Material Compose library**.

## What M3 Expressive support actually exists

### Jetpack Compose

- **21 Material components use the motion physics system by default.**
- `MotionScheme` API — `MotionScheme.expressive()` / `MotionScheme.standard()`, custom schemes, and
  per-element override via `CompositionLocal`.
- `MaterialShapes` — the 35-shape library plus shape morphing.
- Emphasized typography via the emphasized `Typography` tokens.
- **M3 Expressive APIs are experimental.** Later in 2026, Material Compose **1.5.0** will promote them
  to stable. Treat them as an **opt-in "expansion pack" to M3**, not the default surface.
- Ongoing: **Compose Styles API** integration (customization without a recomposition pass). Already
  shipped: **Material Adaptive + Navigation3** integration for adaptive navigation.

### Android Views (MDC-Android) — 1.14.0, final stable

M3 Expressive **did** land in Views before the freeze:

- Expressive themes
- Expressive **list** component
- **Emphasized type scale**
- Expressive styles for **11 existing components** (buttons, sliders, progress indicators, and more)
- Spring tokens for the motion physics system are **available but not wired into components** — apply
  them yourself.

New Views work should be considered migration debt. Migrate screen-by-screen to Compose.

### Web

- Motion: **compatible with Compose springs.** Use real springs where possible; otherwise use the
  spring→cubic-bezier conversion table in `tokens.md`. Curves cannot handle interruptions or gestures,
  so reserve them for animations that have neither.
- Emphasized typography: **unavailable** as a library feature — implement from the token values in
  `tokens.md`.
- Shape library / shape morph: **not currently available.**

### Flutter

- Typography (`Typography.material2021`) available.
- Dynamic color via the `dynamic_color` package.
- **Motion physics system: unavailable.**

## Per-feature availability summary

| Feature | Compose | Views (MDC) | Flutter | Web |
|---|---|---|---|---|
| Motion physics (springs) | ✅ in components | ⚠️ tokens only | ❌ | ⚠️ compatible, convert |
| Shape library (35 shapes) | ✅ `MaterialShapes` | ✅ shape theming | — | ❌ |
| Shape morph | ✅ | — | — | ❌ |
| Emphasized type scale | ✅ | ✅ | — | ❌ (build from tokens) |
| Dynamic color | ✅ | ✅ | ✅ | — |

Blank = not stated in the guidelines. Do not upgrade a blank to a ✅.

## Tools

- **Figma Design Kit** — https://www.figma.com/community/file/1035203688168086460 (also the shape library)
- **Material Theme Builder** — https://www.figma.com/community/plugin/1034969338659738588
- **Material Color Utilities** — https://github.com/material-foundation/material-color-utilities
- **Compose `MotionScheme`** — https://developer.android.com/reference/kotlin/androidx/compose/material3/MotionScheme
- **Compose `MaterialShapes`** — https://developer.android.com/reference/kotlin/androidx/compose/material3/MaterialShapes
- **MDC-Android theming docs** — https://github.com/material-components/material-components-android/tree/master/docs/theming
- **Views → Compose migration skill** — https://github.com/android/skills

## Applying expressive motion outside Material components

For custom or non-Material components, use the spring tokens rather than hand-authored durations:

```
md.sys.motion.spring.{default|fast|slow}.{spatial|effects}
```

The scheme (`expressive` / `standard`) is applied at the product level and is deliberately **not** part
of the token name, so you can swap schemes without touching a single assignment.
