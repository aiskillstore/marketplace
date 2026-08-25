# Ecommerce Story-Ad Replication Framework

## Contents

1. Evidence hierarchy
2. Story grammar
3. Product integration
4. Category adaptation
5. Prompt specificity
6. Common failures

## Evidence Hierarchy

Use evidence in this order:

1. visible action and object state;
2. native or burned-in subtitles;
3. verified transcript;
4. post caption or description;
5. inference, explicitly labeled.

Do not treat comments, reactions, engagement numbers, or platform controls as part of the produced scene unless the user explicitly asks to recreate a social-media screen recording.

## Story Grammar

Map the source into seven beats:

| Beat | Question | Typical duration in a 30-60s ad |
|---|---|---|
| Hook | What visible event stops the scroll? | 0-3s |
| Escalation | What makes viewers need the outcome? | 3-15s |
| Reversal | What unexpected action changes the situation? | 10-25s |
| Product bridge | Why does the product enter now? | 20-30s |
| Proof | What can viewers directly see it accomplish? | 25-40s |
| Payoff | What emotional or practical state improves? | 35-55s |
| CTA | Why act now? | final 2-5s |

Timing is descriptive, not mandatory. Preserve the source's actual rhythm when it differs.

## Product Integration

Prefer one of these bridges:

- **Consequence solver:** the hook creates a mess, discomfort, delay, or risk that the product resolves.
- **Hidden helper:** a character reveals the product as the reason an outcome became easy.
- **Demonstration challenge:** the conflict becomes a test that the product visibly passes.
- **Care gesture:** using the product is how one character helps another.
- **Transformation:** the product produces a visible before/after state that completes the plot.

Delay explicit sales language until after the viewer has seen a benefit. Let the product occupy the proof beat, then add the offer at the end.

Every claim must have one of three statuses:

- `verified`: supplied by the user or official product material;
- `observed`: directly visible in the reference or product demonstration;
- `placeholder`: requires the user to replace or confirm it.

## Category Adaptation

### Home cleaning and appliances

Show the problem state, cleaning path, edge/corner behavior, pickup result, and residual state. Keep liquid, debris, device geometry, and floor state physically continuous.

### Food and kitchen

Use craving, failed preparation, surprise guest, time pressure, or care as the story bridge. Show ingredient state, process, texture, serving result, and a credible consumption reaction.

### Beauty and personal care

Avoid unsupported medical claims. Use routine friction, confidence, sensory texture, application, finish, and time-bounded appearance claims. Preserve skin texture and realistic lighting.

### Apparel and accessories

Use an occasion, fit problem, weather change, styling conflict, or social reveal. Show full-body fit, movement, fabric behavior, detail, and at least one stable comparison.

### Digital products and services

Use a visible task failure or time cost. Show the workflow, input, action, and result. Do not fabricate third-party interfaces, metrics, or testimonials.

## Prompt Specificity

A production-ready prompt defines:

- duration, aspect ratio, target texture, and camera behavior;
- stable character identity, wardrobe, room, props, and product appearance;
- timestamped actions and reactions;
- exact dialogue only when supported;
- sound cues and music arc;
- product proof with physical continuity;
- text reserved for post-production;
- negative constraints tailored to likely model failures.

For generations longer than 15 seconds, also provide 2-4 independently generatable segments with overlap frames or reference-image guidance.

## Common Failures

- **Ad arrives too early:** move branding after the plot problem is understood.
- **Product is decorative:** make a visible outcome depend on its use.
- **Instant cleanup or transformation:** specify path, contact, intermediate state, and residual state.
- **Dialogue without reaction time:** add pauses and expression changes.
- **Cinematic drift:** restate fixed-camera or phone-video grammar and prohibit unmotivated close-ups.
- **Character or product mutation:** repeat identity anchors and use the same reference images for every segment.
- **Unreadable generated Chinese:** generate clean footage and add exact typography in post.
- **Copied platform chrome:** omit UI, comments, watermarks, usernames, and engagement numbers.
