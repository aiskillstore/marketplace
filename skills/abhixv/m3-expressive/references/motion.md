# Motion physics system

Introduced with M3 Expressive (May 2025). **Replaces** the previous easing-and-duration system.
Numeric spring values: see `tokens.md`.

## The two schemes

The scheme you choose defines how the product feels. Most motion in a product should use **one**
scheme.

| Scheme | Feel | Use for |
|---|---|---|
| **Expressive** | overshoots final values to add bounce | Material's recommendation for **most situations**, particularly hero moments and key interactions |
| **Standard** | eases into final values, minimal bounce | utilitarian / functional products |

Custom schemes are supported and are a first-class path, not a hack.

## Spatial vs effects — the load-bearing distinction

| | Animates | Behavior |
|---|---|---|
| **Spatial** | x/y position, rotation, size, corner radius | overshoots the final value and bounces into place |
| **Effects** | color, opacity | **no overshoot**, ever (damping is 1.0 in both schemes) |

Getting this wrong is the most common motion error: a bouncing opacity fade reads as a glitch.
If the property is not geometric, it takes an effects spring.

## Speed selection

Three speeds per style. **Most motion should use default.**

| Speed | Spatial example | Effects example |
|---|---|---|
| Default | animations that partially cover the screen — bottom sheet, expanded navigation rail | opacity of content within a navigation rail |
| Fast | small components — switches, buttons | color change of a switch handle |
| Slow | full-screen animations | full-screen content refresh |

Rule of thumb: **smaller element → faster; larger element → slower.**

Spring tokens are device-aware. `fast` is always faster than `default` on any device, but the
absolute values differ for wearable vs phone vs tablet so the motion feels fast *in context*.

## Why springs rather than curves

- **Versatile** — one spring covers transitions, button effects, and gestures, so expression stays
  consistent product-wide.
- **Natural** — predictable, like real objects.
- **Interruptible** — springs handle gestures, interruptions, and retargeting seamlessly. Curves
  with fixed durations do not. This is the reason to prefer springs on web too.

## Three levels of application

**Level 1 — use a default scheme.** Expressive and standard cover all motion needs. On Jetpack
Compose, components use these schemes by default; 21 Material components use the physics system out
of the box.

**Level 2 — create a custom scheme.** Build a custom `MotionScheme` object returning a different
`AnimationSpec` per property. Changes every component and transition at once.

**Level 3 — swap scheme per element.** Run expressive product-wide but override the
`CompositionLocal` for a specific composable, screen, or element to use standard (or vice versa).
This is the sanctioned way to make one moment feel different.

## Platform availability

| Platform | Status | How to apply |
|---|---|---|
| Jetpack Compose | Available | built-in components + spring tokens; `MotionScheme` API |
| Android Views (MDC-Android) | Available, **not wired into components** | use spring tokens directly |
| Web | Compatible with Compose springs | real springs where possible; otherwise the curve conversion table in `tokens.md` |
| Flutter | Unavailable | — |

## Applying it to custom components

Components outside Material — including your own — get the physics system by using the spring
tokens. Do not hand-author durations for expressive motion; reach for
`md.sys.motion.spring.{speed}.{spatial|effects}` and let the product-level scheme decide the feel.

## Shape morph uses this system

Shape morphing runs on the **expressive** scheme by default and can be switched to standard. Morph
is a geometry change, so it is spatial.

## What not to invent

There are no official stagger values, no official per-component choreography timings, and no
official "reduce motion" scheme-swap rule in the motion guidance. If you need those, they are your
design decisions — label them as such rather than presenting them as M3 spec.
