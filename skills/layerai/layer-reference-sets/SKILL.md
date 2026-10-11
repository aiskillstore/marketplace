---
name: layer-reference-sets
description: "Use when a look must hold across many Layer generations: training a custom style or LoRA on a studio's own artwork, curating the images that go into a reference set, choosing its training category, tuning reference-set weight on a run, or deciding whether to train at all rather than attach a style reference. Also when a trained style produces weak, inconsistent, or silently ignored results. Keywords: LoRA, custom model, trained style, reference set, consistency, on-model, art direction, dataset."
license: MIT
---

# Layer Reference Sets

## Overview

A reference set is a named group of files plus a training category. Trained, it produces a LoRA that
later runs apply by id, turning an art direction into a parameter instead of a prompt-engineering
exercise every time.

The mechanics (upload, `create_reference_set`, `estimate_training_price`, `start_training`,
`get_training_status`, `get_trained_model`, and the five categories) are covered by Layer's published
`layer-train-custom-style` skill, over both REST and MCP. This skill covers the decisions that
determine whether the trained result is any good.

If a sibling skill named here is missing from your available skills, ask the user to install it
(`npx skills add layerai/skills --skill <name>`); unattended, proceed from tool schemas and flag the
gap.

## Decide whether to train at all

Training costs Creative Units and takes time. It is the right answer less often than people expect.

| Situation                                   | Do this                                                                      |
| ------------------------------------------- | ---------------------------------------------------------------------------- |
| A handful of assets, this week              | Attach an approved image as `reference_image`, filtering for `image_editing` |
| One character across a dozen images         | An approved hero image as a reference usually suffices                       |
| A look reused for months, by several people | Train a reference set                                                        |
| A cast or prop library that keeps growing   | Train, one set per subject                                                   |
| The style exists only in the user's head    | Generate first, approve, then train on the output                            |

The last row matters. A reference set can be trained on approved generations, not only on hand-made
art, which is how a direction discovered in a session becomes reusable.

## Curate the set

Dataset quality decides the result far more than any parameter. The common failure is quantity.

- **Consistency over volume.** Fifteen images that genuinely share one look beat sixty that mostly
  do. Every off-style image teaches the model that the style is negotiable.
- **Teach one thing.** A set that mixes a character, an environment, and a UI kit trains a model that
  produces a blurred average of all three. Split them into separate sets.
- **Vary what should vary.** For a character, vary pose, angle, and expression while holding design,
  palette, and rendering constant. For a style, vary subject while holding rendering constant. A set
  that is identical throughout teaches the model to reproduce one image.
- **Clean inputs.** Exclude watermarks, UI overlays, text, heavy compression, and images where the
  subject is small in frame or occluded.
- **Match the category to the intent.** `character`, `object`, `scene`, `effect`, or `general`. The
  category shapes what the training attends to, so a character trained as `general` learns the
  background as part of the identity.

When the user offers a large folder, curating it down is the highest-value thing to do before
spending anything.

## Apply it well

Pass sets to `execute_forge` as `reference_sets: [{set_id, weight}]`, up to 10. `weight` runs 0 to 2
and defaults to 1.0.

**Prefer auto-pick.** With reference sets and no `base_model_id`, the server picks the model that
applies them best: a trained LoRA beats mapped reference images, which beat prompt-only text. The
curated ranking behind `list_base_models` is task fit, not reference-set fit, so pinning a model you
chose yourself is the usual reason a trained style arrives weaker than expected.

Weight is a dial, not a switch. Start at the default. Raise it toward 1.5 when the style is present
but too faint, and lower it toward 0.5 when the style is overwhelming the subject and every prompt
produces the same composition. Weight applies only where a LoRA applies; it is ignored for sets
applied as reference images or prompt text.

Combining a style set with a character set works. Combining two competing style sets averages them.

## Degradation is quiet

`estimate_forge_price`, `execute_forge` and `get_forge_run` all return
`reference_set_contributions`, `reference_sets_degraded`, and `reference_sets_warning`. A degraded
run still succeeds and still costs Creative Units, so nothing looks wrong except the output.

Read the contribution report on the estimate, before spending. If `reference_sets_degraded` is true,
tell the user which set did not apply and why, then either re-run without `base_model_id` so the
server picks a compatible model, or pick another one. Never describe a degraded set as applied.

## Worked example

"Everything we generate should look like our style bible."

1. Look at what they have. Twelve pieces that share a rendering style, plus eight that do not, is a
   twelve-image set.
2. Upload the twelve, then `create_reference_set` with category `general`, since this is an overall
   aesthetic rather than one subject.
3. `estimate_training_price`, present it against the balance, and confirm above 20 CUs.
4. `start_training`, then `get_training_status` at the returned interval until terminal success.
5. `estimate_forge_price` with `reference_sets: [{set_id, weight: 1.0}]` and **no** `base_model_id`,
   so the server picks a model that can apply the LoRA. The estimate carries the contribution report,
   so check `reference_sets_degraded` here, before any spend.
6. `execute_forge` with the same arguments once the estimate is clean and, above 20 CUs, confirmed.
7. Poll `get_forge_run`, then judge the output and adjust weight from there.

## Common mistakes

- Training when a style reference on an approved image would have done.
- Padding a set with off-style images to reach a number.
- Mixing characters, environments, and props into one set.
- Training a character as `general`, so the background becomes part of the identity.
- Pinning `base_model_id` alongside reference sets, then reporting the style as weak.
- Treating weight as on or off rather than tuning it.
- Missing the degradation report and reporting a set as applied when it was not.
