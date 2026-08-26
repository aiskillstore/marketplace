# Character profile schema

Create one profile per recurring lead character. The schema supports humans, animals, robots, and hybrids. Treat `must_keep` and `forbidden_drift` as hard visual constraints; treat `may_vary` as explicitly permitted variation.

Do not begin image generation or editing until `rights_confirmation.confirmed` is `true`. Use only references the user owns, created, licensed, or otherwise has permission to use.

## Contents

- [Profile template](#profile-template)
- [Authoring rules](#authoring-rules)
- [Minimum acceptance check](#minimum-acceptance-check)
- [Production reference gate](#production-reference-gate)

## Profile template

```yaml
schema_version: 1
character_id: "<stable-lowercase-id>"
display_name: "<character name>"
kind: "<human | animal | robot | hybrid>"

rights_confirmation:
  confirmed: false
  confirmed_by: "<user or rights holder>"
  basis: "<owned | licensed | public-domain | generated-original | other>"
  allowed_uses:
    - "<for example: generation, editing, publication>"
  restrictions:
    - "<territory, platform, attribution, or other limit; use [] if none>"
  notes: "<optional provenance note; do not include sensitive personal data>"

identity:
  summary: "<one-sentence recognition description>"
  species_or_model: "<human type, animal species, robot model, or hybrid description>"
  age_or_life_stage: "<optional observable age band or life stage>"
  silhouette: "<recognizable outer shape and posture>"
  head_and_face: "<head shape, facial structure, eyes, ears, sensors, or display>"
  surface_and_palette: "<skin, fur, feathers, shell, material, and stable colors>"
  scale: "<relative height or size when useful>"

identity_references:
  - id: "<reference-id>"
    source: "<workspace-relative path or approved URL>"
    role: "<primary-identity | turnaround | expression | palette | anatomy | mark>"
    priority: "<primary | supporting>"
    rights_basis: "<must agree with rights_confirmation>"
    notes: "<what to read from this reference>"

must_keep:
  - "<one observable invariant per item>"

may_vary:
  - "<one permitted change per item, with limits when needed>"

anatomy:
  body_plan: "<biped, quadruped, wheeled robot, floating body, etc.>"
  proportions: "<head-to-body ratio, torso length, limb length, or chassis proportions>"
  countable_parts:
    - part: "<hands, paws, wings, wheels, antennae, panels, etc.>"
      count: "<expected count or conditional rule>"
      structure: "<digits, joints, segments, attachment, and motion limits>"
  joints_and_range: "<important articulation and impossible poses>"
  locomotion: "<walk, fly, roll, hover, or other movement rules>"
  interaction_rules: "<how limbs or tools plausibly grip and operate objects>"

wardrobe:
  default: "<default clothing, accessories, shell panels, or none>"
  placement_rules:
    - "<where each stable item sits and how it is oriented>"
  allowed_variants:
    - "<approved outfit, accessory, or shell variant>"
  prohibited_substitutions:
    - "<items or colors that must not replace the approved design>"

signature_mark:
  enabled: false
  reference: "<approved asset path, or empty when disabled>"
  description: "<shape and visual construction>"
  placement: "<exact body, garment, accessory, or shell location>"
  color_rules: "<approved colors by rendering mode>"
  transform_rules: "<whether rotation, mirroring, cropping, or simplification is allowed>"
  visibility_rule: "<when it should appear or be naturally occluded>"

voice:
  language: "<primary language>"
  register: "<plainspoken, formal, playful, reserved, etc.>"
  sentence_shape: "<typical length and rhythm>"
  humor_or_emotion: "<emotional range and comic tendency>"
  recurring_phrases:
    - "<optional approved phrase; use [] when none>"
  avoid:
    - "<tones, vocabulary, claims, or mannerisms that do not belong>"

forbidden_drift:
  - "<identity, anatomy, wardrobe, palette, voice, or mark failure that invalidates the result>"
```

## Authoring rules

- Write observable, testable constraints. Prefer “two rounded antennae attached symmetrically to the head” over “keep the character cute.”
- Give every reference a role and priority. When references conflict, follow the primary reference, then the written `must_keep` rules; never average incompatible designs.
- Describe anatomy by body plan and countable parts, not by assuming human anatomy. Include digit counts only when digits are visible or narratively important.
- Use `wardrobe` for clothing, collars, harnesses, removable accessories, robot shells, or panels. Set `default: none` when the character has no wardrobe.
- Keep `signature_mark.enabled: false` unless the user explicitly supplies an authorized mark. Never invent, infer, mirror, or approximate a mark.
- Put flexible styling, poses, expressions, and scene-dependent clothing in `may_vary`; do not weaken identity-critical invariants to increase variety.
- Add every known model failure to `forbidden_drift` as a checkable rejection condition.

## Minimum acceptance check

Reject the profile as incomplete when any of these is true:

- Rights are unconfirmed or the allowed use does not cover the requested output.
- No usable identity description or authorized identity reference exists.
- `must_keep`, anatomy, or `forbidden_drift` is empty.
- A required signature mark lacks an authorized standalone reference and exact placement rules.
- Two hard constraints contradict each other.

## Production reference gate

Inspect every identity or anatomy reference before using it for episode generation. Mark each referenced field as `pass`, `fail`, or `not-verified`.

- Do not use a failed reference for any panel that must preserve its failing field. Visual evidence usually outweighs a prose instruction to ignore the visible defect.
- Do not relabel a failed primary reference as `supporting` to bypass this gate.
- Supply only the relevant accepted view or crop for a panel when a multi-view sheet would create side, pose, or identity ambiguity.
- If no reference passes the fields needed by the episode within the bounded reference-attempt budget, stop before comic generation and report the missing evidence.
- Record the accepted reference identifier and hash in the visual task contract so later panel regeneration uses the same evidence.
