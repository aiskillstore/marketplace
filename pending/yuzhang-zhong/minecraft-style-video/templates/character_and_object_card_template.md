# Character & Voxel Object DNA Card: {{NAME}}

| Field | Locked Value |
| --- | --- |
| **Character / Mob Archetype** | `{{ARCHETYPE}}` |
| **Rig & Arm Width** | `{{RIG}}` (`8x8x8` head, `8x12x4` torso, `4x12x4` Steve or `3x12x4` Alex limbs) |
| **3D Outer Skin Shell** | `+0.5px` Hat/Hair layer + `+0.25px` Jacket/Sleeve/Pants overlay |
| **Hand Lock** | Fingerless & clawless flat `4x4` / `3x4` square pixel-block ends |
| **Face Grid** | `8x8` nearest-neighbor pixel face (`2x1` sliding pixel eyes + `2x1` floating brows) |
| **Featured Voxel Object / Block** | `{{OBJECT}}` (`16x16x16` block or `14x14x14` chest) |
| **Extruded Held Item** | `{{HELD_ITEM}}` (`16x16x1` stepped pixel-art thickness) |
| **Shader & Lighting** | `{{SHADER}}` |

## 3-View Character Turnaround Prompt

```text
{{TURNAROUND_PROMPT}}
```

## Isometric Voxel Object / Block Reference Prompt

```text
{{OBJECT_PROMPT}}
```

## Anti-Drift Negative Prompt

```text
{{NEGATIVE_PROMPT}}
```
