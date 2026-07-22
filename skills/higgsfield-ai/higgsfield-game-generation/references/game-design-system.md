# GAME CREATION SYSTEM
### Plan → Build → Deliver — the compressed operating core

> **Skill integration (read first, then apply the system below):**
>
> - **Read order: this file is the FIRST reference of any game-creation run** — open it before all other references and before any code, and **read it whole, top to bottom, in one pass** — never by sections, never partially. The closing reference is `build-game.md`: read last of all, after the plan and the asset references, but strictly before generating any game code.
> - **One pipeline, one speed — and it is the floor.** Every request runs the same lean pipeline; there are no heavier or lighter modes. Feeling that it is overkill for the request never waives the plan phase (§§1–5), the STYLE FORMULA or the asset manifest; cutting a step needs the user's explicit confirmation, and a brief referencing an existing game ("like X") waives nothing — the reference only pre-fills answers. Lean means: gates and the plan are resolved **in reasoning**, not written — the only planning file is `design/assets.csv`.
> - **Three phases, merged work inside each.** PLAN (think §§1–5 through, write `assets.csv`, derive the STYLE FORMULA; `multiplayer.md` when Players ≠ solo) → BUILD (fire **all** asset generation jobs, then write the game code *while they run*, wire assets in as they land) → DELIVER (publish, hand over the URL). Inside a phase, parallelize what is genuinely independent (asset jobs run while game code is written; independent generations submit together) — and keep sequential what feeds on a prior result; don't force parallelism onto dependent steps. The phases themselves never interleave — no game code before PLAN closes. Post **1–3 plain sentences in natural language after each phase** (not after every internal step); never expose pipeline machinery — no phases/gates/modes/§-numbers, no checkmarks. Blocking points: STYLE FORMULA approval (only when the style is not explicit in the brief) and any cutting of pipeline steps.
> - **Asset manifest — the only written planning artifact, mandatory always**: planning emits `design/assets.csv` (in the game project under `design/` — it ships with the game) listing every visual/audio asset the build needs. Columns: `id`, `role` (how the build consumes it), `type`, `description`, `size/ratio`, `style line ref`, `source` (`generate` | `reference_media[i]`). It is the contract between asset generation and assembly.

The system: §0 execution → §1 profile → §2 laws → §§3–5 design → §§6–8 implementation → §§9–11 tuning → §12 determinism & debugging → §13 limits. The engine of all of it is the **iterative loop**: nothing is designed until thought through against its gate.

---

## 0. EXECUTION RULES

1. **Artifacts.** Planning is resolved in reasoning; the only written planning file is `design/assets.csv`.
2. **Each phase closes with its gate**, walked in reasoning at the transition. An unmet item blocks the move — there is no "fails, but moving on".
3. **The game tolerates hostile input by design**: spam, mid-action cancel, boundary violations, doing it "the wrong way", conflicting simultaneous inputs (opposite directions held, multi-key chords, two input methods at once, switching method mid-action), losing focus / disconnecting mid-action.
4. **Diagnose from observed behavior** (state, logs, console) — not impressions.
5. **One meaningful change at a time** when tuning or hunting a failure.
6. **Numbers before code.** Any numeric criterion (budget, window, limit) is fixed before building the thing it judges, and never softened in the same iteration that failed against it. The canonical numeric defaults live in `build-game.md`.
7. **Code permission is bound to phases** — no game code until PLAN closes (its sections thought through, `assets.csv` written, FORMULA derived). A one-paragraph "plan" followed by code is a failed run.

| Phase | Code |
|---|---|
| PLAN (§§1–5) | ❌ none |
| BUILD (§§6–8) | ✅ game code, from the `build-game.md` skeletons; §§9–11 as data/config |
| DELIVER | ❌ publish only |

---

## 1. GAME PROFILE

Think through a point on every axis — the profile decides the shape every later section takes:

| Axis | Spectrum |
|---|---|
| **Time** | real-time ↔ turn-based ↔ pause-at-will ↔ no time |
| **Space** | continuous 2D/3D ↔ discrete ↔ abstract ↔ absent |
| **Agency** | one hero ↔ squad ↔ disembodied hand |
| **Conflict** | vs system ↔ vs players ↔ vs self ↔ none (then what holds attention instead?) |
| **Content** | authored ↔ procedural ↔ emergent ↔ player-created |
| **Outcome** | win/lose ↔ endless ↔ player-set goals ↔ none |
| **Players** | solo ↔ co-op ↔ versus ↔ massive (not solo → `multiplayer.md` is mandatory) |
| **Session** | minutes ↔ hours ↔ "once a day" |
| **Engagement source** | execution ↔ calculation ↔ discovery ↔ expression ↔ story ↔ social ↔ accumulation — pick 1–2 primary; rewards (§5) and balance (§9) feed them |

**Delivery context** (fixed here, never retrofitted): target platforms — default **desktop + mobile + gamepad**; every verb performable by every declared input method, no hover-only interactions when touch is declared, keyboard bound to **physical key codes, never typed letters**; shipping languages — all player-visible strings external from day one. Performance budgets target the **weakest** declared platform.

---

## 2. LAWS

- **L1 — Experience first.** Design the experience, not the artifact; any convention may break if the experience demands it. Every later dispute resolves against the experience formula (§3.1).
- **L2 — Meaningful interaction.** Every player action must be *discernible* (visible effect now) and *integrated* (echo later). Test per mechanic: action → visible effect → where it resurfaces. An empty slot = a dead mechanic.
- **L3 — Mastery.** Interest is pattern mastery: **one new pattern at a time**, the next after the previous one's exam (§7.3); design the sequence of mastery, not the volume of content; grind is a deliberate recorded choice or a hole.
- **L4 — Undecided outcome on every horizon** (turn, fight, session). Pick 2–3 uncertainty sources tied to actual mechanics (execution, randomness, hidden info, depth of calculation, another mind, anticipation); randomness lands **before** decisions, not after; when a source runs dry (pattern learned, meta solved), another must already be active — or the game ends there.

---

## 3. CONCEPT

- **3.1 Experience formula** — one sentence: "The player feels ___ because the game constantly ___." No genre labels. This is the compass for every decision after it.
- **3.2 Four pillars** — mechanics, story (even an abstract game has a tension arc), aesthetics, technology: each must reinforce the other three; a pillar serving nothing is ballast.
- **3.3 Formal elements** — answer each or justify its absence: players, goals, actions, rules, resources (anything scarce — time and attention count), conflict, boundaries, outcome.
- **3.4 Interest curve** — hook in the first moments, alternating peaks and breathers, maximum near the end.

---

## 4. SYSTEM

- **4.1 Verbs.** Few strong verbs beat many weak ones — strong means several object types respond differently. Plan each verb's development (new objects/contexts re-weight old verbs). Social verbs get the same rigor as combat ones.
- **4.2 Loops.** Sign every feedback loop: positive snowballs (an early lead decides the game too soon), negative dampens skill (good play stops mattering). A comeback from a deficit must exist, and good play must still win.
- **4.3 Information map.** Decide visibility per fact. A hidden fact that affects the outcome needs a discoverable trail — hidden-with-no-trail reads as cheating. In multiplayer it defines who sees what.

---

## 5. FULL WALKTHROUGH — ten subsystems, each a decision or a justified absence

1. **Representation** (camera / screen layout / text order): never hides information needed for the current decision; the player keeps control of it unless taking it is deliberate.
2. **Input**: platform/genre conventions; axes **not inverted by default** (inversion = settings option); the most frequent actions on the cheapest gestures; conflicting simultaneous inputs resolve predictably (§0.3).
3. **Agency metrics** — the numbers all content is measured by (jump length, move range, options on screen): **frozen before mass content production**; changing them later invalidates everything built on them.
4. **Resistance × verb matrix**: every source of resistance is a question some player verb answers. An unanswerable row = frustration; one verb answering everything = boredom.
5. **Peaks**: each period ends in a combined exam of the patterns it taught, with escalation.
6. **Rewards** feed the declared engagement source (§1); the strongest reward is a **new verb**; big rewards sit on interest-curve peaks.
7. **Interface**: every element serves a player decision — otherwise remove it or hide it until needed.
8. **Economy**: every resource has sources *and* sinks.
9. **Delivery of mechanics**: one new pattern at a time (L3), the next after the previous one's exam.
10. **Game entry**: a short, counted path from launch to the first meaningful action; on return, the first screen shows the current goal and next step; controls learnable on demand at any moment; accessibility options reachable before play starts.

---

## 6. CODE

Game code starts **only after PLAN closes** (§0.7), from the `build-game.md` skeletons — never from scratch.

- **6.1** Architecture = minimizing the cost of change: decouple what will change; don't abstract what won't.
- **6.2 By symptom**: behavior depends on frame rate → fixed-timestep simulation, render separate · class explosion ("FlyingShootingMerchant") → entity = components · need replay/undo/multi-source input → **input as command objects** (also carries the player id for multiplayer) · boolean-flag forest → state machine · gameplay pokes audio/UI directly → events/subscription · object churn eats the budget (profiler-proven) → pools / spatial index / dirty flags — never pre-emptively.
- **6.3 Instruments**: a dev overlay (fps, frame time, entity/draw counts) toggled by a query flag; readable state and logs; programmatic input feeding (N parallel streams when players > 1).
- **6.4** Logic separate from rendering; saves/serialization designed early if anything persists.
- **6.5 PERFORMANCE LAW — universal.** Performance is a frame budget set **before code**, not "optimization later"; exceeding it is a crash-grade bug. Budgets are chosen at planning for the weakest platform (numeric defaults in `build-game.md`). **Swarms of same-type entities render as one draw call, never one each** (instancing/batching — the technique varies by renderer, the rule doesn't). The hidden is neither drawn nor created. Zero allocations inside the frame loop. Measure on the dev overlay before any talk of "slow"; diagnose in fixed order: draw calls → GPU-bound → CPU-bound → spikes/GC. Anti-patterns: a mesh/material per instance, default-on shadows/post-processing, full-scene scans every frame, rendering the invisible.

---

## 7. CONTENT

- **7.1** Build content from modules calibrated by the agency metrics (§5.3) in three grades — tight / comfortable / trivial — so everything assembled is traversable by construction. **Parameter consistency:** cross-check every demand the content makes against capabilities and economy (required gap vs jump length, required resources vs obtainable, time limits vs route time, win thresholds vs reachable totals) — one mismatched number silently makes a condition unreachable, and no crash or test will say so.
- **7.2** Rhythm = alternation of compression (few options, pressure) and expansion (overview, safety); monotony either way is a defect. Guidance comes from the observable state — landmarks, salience, what characters mention; a HUD arrow is the last resort. Show a distant goal early, deny it, deliver the path later.
- **7.3 Teaching loop** for every new pattern: introduce in safety → test with a mild price → combine with the known → exam under pressure (= the §5.5 peak). Intuition over instruction: build the situation that makes the player guess — every tutorial text is a scene that failed. Once a rhythm settles, break it deliberately; a break only works against a settled rhythm.

---

## 8. RESPONSE

Every action gets an immediate acknowledgment (long operations: instant receipt + progress). Context gives weight: every significant action has an immediate reaction **and** a later echo in the world (L2 at the presentation layer). Polish parameters (shake, hit-pauses, easing) are config data, tunable live. Input is forgiving: generous tolerance windows (defaults in `build-game.md`) so honest near-misses count; the player's hitbox smaller than its sprite, the enemy's honest. Stable frame pacing matters more than a high average.

---

## 9. BALANCE

- **9.1 Options**: priced options live on one cost curve — above it = dominant, below = junk; deviations only deliberate. Keep at least one non-transitive structure (A>B>C>A) so the game can't be "solved". Asymmetric sides: equal expected strength, different style.
- **9.2** Perceived difficulty = the gap between the player-power curve and the challenge curve — steer the gap; the next progression step costs more than its reward returns (soft slowdown instead of a wall).
- **9.3 Economy**: inflation (sources outrunning sinks) kills every price — fix sinks, not prices.
- **9.4 Randomness**: tune expected value *and* variance separately; streaks read as cheating — soften them (pity counters, draw-from-deck) and re-count the odds after softening; design the extreme tails on purpose.
- **9.5** All balance numbers live in data, tuned one change at a time (§0.6).

---

## 10. PLAYER'S HEAD

- **10.1 Three limiters**: perception is subjective → critical signals use several channels at once and no two critical signals collide (including under colorblindness); attention is a bottleneck → nothing instructional under load, one message at its moment of need; memory decays → the game remembers for the player: current goal and next step visible at any return.
- **10.2** Every system state observable; every refusal explains *why* and *how to lift it*; what looks interactive is interactive (and vice versa); the cost of an error is repeating the interesting part, not the boring one; motivation needs all three: visible growth, real choices, a world that responds.
- **10.3 Accessibility & localization are data from day one**: remappable bindings (physical key codes + gamepad buttons; a binding per declared method for every command); options that actually apply (text scale, shake/flash toggles, contrast); all player-visible strings external — switching language is a data change, not a code change.

---

## 11. NARRATIVE (when the profile has story)

The hero's goal = the player's goal — divergence only as a deliberate, recorded device. Build on state variables, not scene-branching trees. Every significant choice observably fires later (L2) — a choice with no consequence is decoration. Deliver up the hierarchy: the player *did it* > saw it in the world > overheard it > read it.

---

## 12. DETERMINISM & DEBUGGING

- **12.1 Determinism**: fixed timestep + seeded RNG, logic and visual generators split — same input, same game; any bug reproduces from its inputs.
- **12.2 Debugging**: reproduce stably → hypothesis, then observe (never "patch and see") → bisect the cause space → fix the cause, not the symptom → leave a guard behind so the class of bug stays closed.

---

## 13. LIMITS — close honestly

Perceptual quality — composition, animation feel, music — and real player delight need human eyes and hands the pipeline lacks. Say so plainly at delivery instead of overclaiming.

**Freeze points:** agency metrics — before mass content (§5.3); features — once content is complete.
