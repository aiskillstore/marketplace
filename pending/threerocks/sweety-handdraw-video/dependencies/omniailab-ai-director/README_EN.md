<h1 align="center">OmniAiLab AI Film &amp; TV Director</h1>

<p align="center">
  <b>A film-industry-grade, end-to-end AI director Skill — and a creative system that guides your decisions</b><br>
  Live-action realism &amp; animation&nbsp;&nbsp;|&nbsp;&nbsp;30-second short → 100+ scene feature&nbsp;&nbsp;|&nbsp;&nbsp;Script breakdown to final delivery
</p>

<p align="center">
  <a href="https://github.com/tomatoparkdao/omniailab-ai-director"><img src="https://img.shields.io/badge/Version-2.3.0-1f6feb?style=flat-square" alt="Version 2.3.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2ea043?style=flat-square" alt="License MIT"></a>
  <a href="https://www.omniailabx.com/"><img src="https://img.shields.io/badge/Platform-OmniAiLab-8957e5?style=flat-square" alt="Platform OmniAiLab"></a>
  <img src="https://img.shields.io/badge/Medium-Live_action_%2B_Animation-db6d28?style=flat-square" alt="Medium: Live action and Animation">
  <img src="https://img.shields.io/badge/Works_with-Codex_%7C_Claude_%7C_WorkBuddy_%7C_OmniAiLab-0969da?style=flat-square" alt="Works with Codex / Claude / WorkBuddy / OmniAiLab">
</p>

<p align="center">
  <a href="README.md">简体中文</a>&nbsp;&nbsp;|&nbsp;&nbsp;<b>English</b>
</p>

> © OmniAiLab ｜ Developer: Mochiball ｜ Platform: [omniailabx.com](https://www.omniailabx.com/)

**A film-industry-grade, end-to-end AI director Skill — and a creative system that guides your decisions.** It doesn't just run a pipeline: **the first thing it does is ask what kind of piece you're making** (narrative film / short drama / animation / documentary / commercial / title sequence / music video / game PV / UI motion — each takes a different track), then lets you pin down the director, camera, lighting and aesthetics yourself or leave it to the Skill; after that it walks you from script breakdown to finished film following real production standards. **Works for both live-action realism and animation**, from a 30-second short to a feature with a hundred-plus scenes.

| Item | Value | Notes |
|---|---|---|
| Skill invocation name (unique ID) | `omniailab-ai-director` | All-lowercase with hyphens. Tools with native Skill support invoke it directly; tools without it also trigger it from a natural-language task description (implicit invocation is allowed) |
| Display name | OmniAiLab AI Film & TV Director | The name shown on the repository page and in the docs — not the invocation name |
| Version | v2.3.0 | Kept identical across the repository, the manual and this README; every update is pushed together |
| Publisher / Developer | OmniAiLab / Mochiball | — |
| License | MIT (see [LICENSE](LICENSE)) | Free to use, modify and redistribute |
| Companion manual | [Feishu doc](https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA) (Chinese) / [Notion](https://tomatopark.notion.site/3eaa28d2e378800d8b8bee090c32c34d) | How to invoke, 3-step start, stage-by-stage detail, dispatch lookup, model reference, pitfall table, FAQ, deliverables |
| Open-source repo (public) | [github.com/tomatoparkdao/omniailab-ai-director](https://github.com/tomatoparkdao/omniailab-ai-director) | Clone it to install the latest version (`git clone` into your skills folder); update with `git pull`; issues welcome |

The invocation name is **all-lowercase with hyphens** (`omniailab-ai-director`) — it is not the display name. Tools with native Skill support work best with the invocation name; tools without it will still trigger on a natural-language description (implicit invocation is allowed).

---

## In one sentence

Hand it a locked script and it takes you from script breakdown to finished film following film-industry standards. At the end of every stage you only need to reply "confirm" or "change this part."

- **Scope · any medium** — live-action photoreal pipelines, plus pure animation / 2D cartoon / 3D game-engine render style / 3D + hand-painted hybrid.
- **Scope · any length** — 30-second shorts, single-episode short dramas, brand films, narrative music-video segments, all the way up to features with dozens or hundreds of scenes, tens of minutes to two hours-plus (**features no longer need to be split into episodes**).
- **Default medium** — live-action photoreal (used when unspecified). For animation / hybrid projects, P1 first performs a **medium determination** and writes it into the "whole-film style lock"; from then on that declaration is the single source of truth for medium — modeling, brushwork, motion and lighting follow the **Animation & Hybrid Medium layer**, and motion obeys **animation principles** (squash & stretch / anticipation / follow-through & overlap / arcs / exaggeration), with physical accuracy yielding to expressive motion.

---

## What's inside

**It is not "a template that runs a pipeline" — it is a creative system that asks questions, proposes options, and translates adjectives into parameters.**

| Layer | What it gives you |
|---|---|
| **① A guided entry — you need no jargon** | It first determines the **form of work**: narrative film / short drama / animation / documentary / commercial / title sequence / music video / game PV / UI motion / creator video / education — each runs on its own track. If you can't say, it asks **only three questions** to narrow down (where it plays / are the people real or performed / what must it deliver). If three questions don't settle it, it **won't guess** — it proposes the shortest viable deliverable for you to decide. |
| **② Creative decisions on a menu — or delegated** | **20 director presets** (single or blended: one lead director sets the whole-film baseline, plus 1–2 others lending specific dimensions) · **five-dimensional camera coordinates** (6 body formats × 11 lens characters × 6 focal lengths × 3 depth-of-field tiers × 20 movements) · **33 lighting setups × 5 colour-temperature variants** · **7 film-level aesthetic recipes** (A01–A07) · **D/P/C/R/S visual-language vocabulary**. All of it is yours to pick, or you can leave it to the Skill — if you can't say, it proposes 2–3 candidates with reasons, by genre. |
| **③ Expertise lives in mechanisms, not adjectives** | **Directorial reasoning**: choosing a director loads his underlying mechanisms for space, camera, light, time and subtext; every preset states its **"counter-example"** — the *mechanism difference* from the nearest-lookalike director (e.g. Kubrick compresses people into architecture with wide lenses, Fincher cuts them out as specimens with long lenses — **the background requirements are opposite**). A **dispatch lookup** maps **16 genres / 22 scene types / 16 character functions / 18 plot beats** straight to camera and lighting choices. **A 16-block fixed prompt order + eleven iron rules** ("negation summons", "anchor geometry to the frame, not the object", "solve the hard parts in a still plate"). Plus an **asset system**: paired assets, unified naming, state management, voice lock. |
| **④ Backed by real projects** | **6 commercial-grade case studies** (live-action shorts / features / animation, with production-ready prompt blocks and "problem → fix" lists) · **49 method figures** (keyword lookup index — the hardest things are shown, not described) · **7 real finished-film samples** (verbatim source text plus breakdown) · **14 commercial-video tracks** (brand ad / title sequence / motion design / game PV / UI motion / music video / creator video / education / video deconstruction / voice cloning). When unsure how to write something, copy a finished block. |
| **⑤ Full pipeline to delivery** | P0 project intake → P0A ten-point script breakdown with a whole-film emotion curve → P1 photography, colour and sound baseline → P2 character and key-prop boards → P3 scene assets and environment colour cards → P4 shot design and first frames → P5 video prompts and canvas parameters → P6 generation, editing and export in the **OmniAiLab infinite canvas**. **One confirmation gate at the end of each stage** — you only reply "confirm" or "change item X". |
| **⑥ Promo-class briefs get a channel decision first** | The same promo / product film / launch video / feature demo has two routes: the **generative track** (imagery generated by the model — **MiniMax H3** on the OmniAiLab canvas) and the **code-rendered track** (real page screenshots + frame-by-frame rendering, 100% controllable, with an editable project handed back). They run **in parallel and can interleave**. It **gives a judgement before it gives options**: **five criteria** (is the subject live action or UI/data / does it need pixel accuracy / is there a real interface that can be captured / does it need frame-exact control / length and placement) produce a stated recommendation **with the trade-offs spelled out**; it **hints at format-selection time and only expands when information is missing**, then **formally confirms and locks the channel after assets are verified, before storyboarding**. Scenario coverage is **grouped by subject into four families** (people / objects / screens / hybrid) spanning corporate image, TVC, public service, city, recruitment, product ads, software launches, feature demos, data visualisation, TV packaging and large-screen loops, plus a **hybrid hand-off split** (anything live-action and moving goes generative; everything on a screen goes code-rendered). The code-rendered side ships **157 motion shot recipe cards**, seven rule documents, a runnable project template and **154 sound-effect assets**; **unsuitable briefs get an explicit "not this track" plus an alternative route**. |
| **⑦ Judgement with sources, not adjectives** | **Film-art knowledge layer**: a read-only **judgement and source layer** distilled from film-art literature — **15 domains** (read-and-direct playbook / story & script / casting & directing actors / visual language / staging & camera / storyboard / editing & montage / sound / lighting / production design / genre / production & on-set / master methods / genre craft / national styles) + **39 verified capability cards** (frameworks / principles / cases / counter-examples, each traceable) + an index of **118 works**. It answers **what to think about, why, and where the criteria are**: spine and fulcrum, dramatic blocks and narrative beats, **the relation line and the triangle principle** (the root cure for crossing the axis and for "I cannot follow it"), blocking motivation, cut criteria and stop points, **six sound-design frames**, genre as a contract with the audience, resource-driven planning and the limits of a director's authority, and **shot-level film analysis**. It **only produces judgements, evidence and checklists** — prompt wording still belongs to the specialized layers; it **raises its judgement proactively at P0A / P1 / P4** and closes with the release checklist at P5 — plus **three borrowing tiers for fusing classics with new ideas**. |

> **Adjectives get translated into parameters.** Say "make it classy" or "cinematic" and it first converts that into executable tiers (soft curve, 3:1 ratio, medium-telephoto compression, 6-second average shot) for you to confirm — **adjectives can't be executed; tiers can.**

---

## Quick start

### 1. Where to install it

Copy the **entire `omniailab-ai-director` folder** (including `GUIDE.md`, `VERSION`, `openai.yaml`, `references/`, `examples/`) into the matching directory below, then start a new session.

| Tool | Where to put it | How to invoke |
|---|---|---|
| **Codex** (recommended) | No native skill directory: drop the folder into your project, e.g. `<your project>/skills/omniailab-ai-director/`, then add one line to `AGENTS.md` in the project root:<br>`For film production tasks: first read skills/omniailab-ai-director/GUIDE.md and follow its workflow.` | Say "start making the film per GUIDE.md". |
| **Claude / Claude Code** | Personal: `~/.claude/skills/omniailab-ai-director/`<br><br>Project: `<your project>/.claude/skills/omniailab-ai-director/` | Type **`/omniailab-ai-director`**, or describe the task (e.g. "run the full film pipeline for this script"). |
| **WorkBuddy** | User level (global): `~/.workbuddy/skills/omniailab-ai-director/`<br><br>Project level: `<your project>/.workbuddy/skills/omniailab-ai-director/` | It appears in the skill list in a new session; just say **`$omniailab-ai-director 开始`**. |
| **OmniAiLab** (omniailabx) | [Download from the official site](https://www.omniailabx.com/plugin) (Windows local build v0.8.16), or use the [mirror link](https://pan.baidu.com/s/12Wtj8pAKmXOGgWN-M07v7A?pwd=2gff) (access code `2gff`); then put the whole folder into its **skill directory** (the client shows where that is) | It appears in the skill list in a new session; just say **`$omniailab-ai-director 开始`**. |

> **Copy the whole folder — never just `GUIDE.md`.** The four sub-skills (ACTING / EMOTION / LIRA / CINEDANCE), all specialized layers (COMBAT combat / BLOCKING blocking / AESTHETICS / PROMPT-DOCTRINE / ASSET-SYSTEM / SCENE-ENGINE / OPTICS / FEATURE-PRODUCTION / MUSIC-SCENE / ANIMATION / DOCUMENTARY / PROMO / ONBOARDING / MOTION-STUDIO), the visual-language library, the 7 ready-made prompt sets, the documentary templates, **all 14 promo directions in full detail**, **7 real promo samples**, **camera & lighting indexes** and **49 case-study figures** all live in `references/` and `examples/`. Skip one directory at runtime and the chain breaks.

**Install by cloning (recommended)**

```bash
git clone https://github.com/tomatoparkdao/omniailab-ai-director.git \
  ~/.workbuddy/skills/omniailab-ai-director
```

The repository is **public** and always tracks the latest skill version; update later with `git pull` in that folder. Issues are welcome in the repo.

### 2. Where the script comes from (pick one)

1. **You upload a locked script** — it reads it and enters P0 directly.
2. **You give nothing and just say "start"** — it first asks one question: "do you have a script, or just a one-line idea?" It will **not** auto-load the built-in script. Say "run the default project" only if you want to see the sample *Floor 17* (a 30-second suspense short).
3. **You give a one-line idea or title** (e.g. "make a space thriller short") — it first writes a locked script for you to confirm, then enters P0. Script length is kept to 30 seconds – 5 minutes.

### 3. Start command

```text
$omniailab-ai-director start
```

Just say "start" — instead of asking "what is your script?", it asks "do you have a script, or just a one-line idea?".

It will **not** run the built-in script by default. Only wording like this uses the built-in sample script (a 30-second suspense short, *Floor 17*):

```text
run the default project
do Floor 17
```

### 4. Two things to settle before you start

- **The story must be locked.** It only works with a locked script: no rewriting the story, adding characters, adding dialogue or changing the ending. Major mid-course story changes (especially adding/removing characters or scenes) invalidate every asset already generated.
- **Decide delivery specs first.** Defaults are 1080p / 16:9 / 24fps / MP4. If you need vertical or square (mobile, product packaging art, etc.), say so at P1 — changing specs after P1 also causes asset rework.

### 5. You only ever reply two ways

1. **Release the next stage** — it must be one of these four; anything else does not open the gate:

```text
confirm / pass / locked / continue
```

2. **Ask for a change by location** — it stays in the current stage and redoes it in place:

```text
change the lighting in item 3 to side-backlight
change shot 07 from a wide to a medium close-up
```

**Want only one capability?** Name it directly; the full pipeline is optional:

| What you want | Copy this and just say it | What you get back |
|---|---|---|
| Image prompts | `image only — give me the prompt for this shot` | A ready-to-feed image prompt with look tier, composition and light positions |
| Video prompts | `video prompt only — how do I shoot this shot` | A complete video prompt in the 16-block fixed order, checked against the eleven iron rules |
| Performance design | `performance only — how should this character play this scene` | A performance task block: objective / obstacle / tactic, beat by beat |
| Emotion control | `emotion only — how do I play this crying scene` | A whole-film emotion curve or a single-shot emotion engine output |
| Look selection | `give me the look menu` / `use D01 + C04 + R01 + S2` | Visual-language tiers with ready-to-use phrasing |
| Aesthetic recommendation | `which film aesthetic fits this scene` | 2–3 film-level recipe candidates, each with a one-line reason |
| Fight choreography | `how should this fight go — give me a high-energy fight prompt` | Fight frame-chain, named actions with vectors, money-shot timeline |
| Blocking / staging | `how should these people stand` / `the positions shifted again in the next shot` | A blocking baseline plus cross-shot lock — required whenever several people share the frame |
| Camera and lighting | `what lens and light for this shot` / `how do I light the whole film` | A camera and lighting plan resolved from genre / scene / character / plot lookups |
| Director style | `who should direct this` / `can I mix Wong Kar-wai with Fincher` | 2–3 director candidates with reasons, or a blend plan with the do-not-mix list |

> **The more specific the request, the less rework.** Three things matter most: ① the full locked script; ② delivery specs (aspect ratio, resolution, frame rate, duration); ③ hard constraints (what must not appear, what must appear). Give these up front and you save far more than patching later.

---

## Pipeline overview

Eight stages form one **serial chain**: **P0 → P0A → P1 → P2 characters → P2 props → P3 → P4 → P5 → P6**. Every link ends with a **confirmation gate** — until you explicitly say "confirm / pass / locked / continue", it stays locked in place.

| Stage | What it does | What you get |
|---|---|---|
| **P0 + P0A** | Receive script + ten-item breakdown + whole-film emotion curve | Project intake summary, ten-item breakdown, one 16:9 black-background emotion curve |
| **P1** | Lock whole-film cinematography, environment colour strategy, sound bible; proactively propose 2–3 aesthetic recipes | The "whole-film style lock" text — the fixed prefix for every downstream prompt |
| **P2 characters** | Character/state master-plate production list → dependency-batched 9:16 character plates → batch 16:9 character sheets | Character master plates, character sheets, performance master files |
| **P2 props** | Key-prop list → 3:4 single-item product archive shots | Prop master plates |
| **P3** | Scene list → 16:9 empty-scene master plates → 5-colour environment palettes | Scene master plates, environment palettes (with HEX), spatial direction chain |
| **P4** | Shot breakdown → full shot list → blocking baseline → 16:9 first frames for every shot | Shot list, blocking data, all first frames, per-shot performance passages |
| **P5** | Performance passage + emotion layer + spatial data → final video prompts and parameter table | Per-shot video prompts, OmniAiLab parameter table |
| **P6** | Batch generation on the OmniAiLab canvas, voice, BGM, edit, export | Finished MP4, all assets, QC report |

> **Promo-class projects pass a "channel decision" before entering this chain**: the same promo has a **generative track** (imagery generated by the model, MiniMax H3 on the OmniAiLab canvas) and a **code-rendered track** (real interface screenshots + frame-by-frame rendering); picking wrong means redoing the whole film. It **hints at format-selection time** and **formally confirms and locks before storyboarding, once assets are verified**. Criteria, timing, the full scenario table and the hybrid split are in `references/CHANNEL-SELECT GUIDE.md`.

> **Gates are hard rules.** P0 and P0A must run in the same turn — P0 is never confirmed separately. From P0A onward, each stage ends with fixed wording and only "confirm" unlocks the next step. To change something, stop and change it in place, then confirm — **do not try to make it finish several stages in one sentence.**

---

## Stage-by-stage details

### P0 + P0A | Project intake and script breakdown

Reads the whole script, outputs the P0 intake summary, and in the **same reply** completes the first 9 items of P0A (country/era, world rules, character bios, spatial chain, state chain, etc.). It then computes emotion nodes and generates item 10 — the 16:9 black-background emotion curve.

**What you do:** almost nothing; wait for it to deliver in one go. Check two things — the curve's **node count** and its **breathing zone**.

**Deliverables:** intake summary + ten-item breakdown + whole-film emotion curve.

**Its confirmation wording** (copy the whole block):

```text
[Please confirm] Do you confirm the above P0A script breakdown and creative baseline (including the whole-film emotion curve)? Point out any specific items to change.
[Next step after confirmation] Establish the P1 whole-film cinematography, environment colour strategy and sound bible.
```

**Pitfalls**

| Pitfall | Correct approach |
|---|---|
| Waiting for P0 to be confirmed separately | **It won't be** — P0 and P0A run in the same reply, confirmed once after the emotion curve is shown |
| A curve with high energy throughout, or a release point out of nowhere | **8–14 nodes (max 16)**, with at least **one genuine breathing zone**; otherwise send it back |
| Treating the emotion curve as decoration | It drives P6's BGM in/out points and P4's rhythm checks — **get it wrong and everything downstream skews** |

### P1 | Creative baseline (the single most important confirmation)

After judging the script's genre, it **proactively proposes 2–3 aesthetic recipe candidates** (ID + name + why it fits + suggested placement + trade-off). Once you pick, it delivers one complete recommendation — one primary film reference (at most one supplementary), capture medium and lens family, aspect ratio and frame rate, light sources and materials, environment colour strategy, whole-film ambience principles and music bible.

**What you do:** choose one as the primary aesthetic and at most one supplementary, or just say "no need" and it falls back to standard sourcing. Then confirm the style-lock text.

**Deliverables:** the "whole-film style lock" text — **every downstream image and video prompt must carry it verbatim at the start.**

**Its confirmation wording** (copy the whole block):

```text
[Please confirm] Do you confirm the above P1 cinematography, environment colour strategy and sound bible? Point out changes directly.
[Next step after confirmation] First list the 9:16 character/state master-plate production list; confirm scope and dependency batches before generating.
```

**Pitfalls**

| Pitfall | Correct approach |
|---|---|
| Expecting images or audio at P1 | **No images and no audio are generated at this stage** (no palette chart, no audio files, no BGM); expecting images here means you are at the wrong stage |
| Wanting to change the style after locking | The style lock is **frozen once confirmed** — changing it means going back to P1, which reworks every downstream asset; **this is the one confirmation to read carefully** |
| Forcing an aesthetic recipe | "No need" is legitimate; if the script has no recipe-grade need it says so explicitly |
| Leaving lens character, night darkness or in-frame text to the video stage | **Settle "the hard things" at plate time** — all three are solved at the **scene plate / first frame** stage and frozen into the style lock; chasing them later only makes the model drift |
| Relying on post grading, or writing "no yellow", to set the look | **Colour is tuned in the prompt**: paste the whole-film style prefix shot by shot (palette, exposure and contrast, grain, movement character); use a positive **"colour constitution sentence"**; choose film/print stock by "**which colour the shadows lean toward**", not by price; for an uncroppable bright object write "**it is switched off in this film**" |
| Generating animation/hybrid without a medium determination | P1 must do the **medium determination** (photoreal / stylised 3D / 2D / hybrid), write it into the style lock, and lock the **whole-film lighting formula** and the **style split** (moving objects get clean solid volume; heavy brushwork stays with the environment) |

### P2 character assets

First a 9:16 character/state master-plate production list (asset type, upstream dependencies, suggested batch, necessity, reason to generate). After you confirm scope, **batch 1 covers only dependency-free or base characters**; once base characters are locked, blood relatives, variants, costume changes, injuries and age states follow. After everything is confirmed, it generates 16:9 character sheets for all confirmed characters in one pass, and builds a performance master file per main character.

**What you do:** confirm or edit the list; review every batch's images carefully.

**Deliverables:** 9:16 character master plates, 16:9 character sheets, performance master files.

**Its confirmation wording** (copy the whole block):

```text
[Please confirm] Are the above character assets all locked? Point out specific characters and locations to change.
[Next step after confirmation] Extract the key-prop list and generate key-prop master plates.
```

**Pitfalls**

| Pitfall | Correct approach |
|---|---|
| Pushing for a standalone character sheet | Sheets are **not a separate item and get no second list** — generated in one pass only after all 9:16 characters are confirmed |
| Skipping batches (writing downstream before upstream is confirmed) | Unlock by dependency batch: blood relatives / variants / costume changes / injuries / age states only after base characters are locked; **change upstream and everything downstream is wasted** |
| Reviewing character images carelessly | Consistency is inherited downstream from **genuinely confirmed images** — **approve one wrong image and everything after is wrong** |

### P2 key props

First a **non-batched** table of final prop candidates (plot function, identity/continuity anchor, necessity, reason to generate). After you confirm or edit, it generates 3:4 portrait single-item product archive shots. No three-view sheets, no people or hands in frame.

**What you do:** confirm the prop list; review each master plate.

**Deliverables:** prop master plates (each with its prompt).

**Pitfalls**

| Pitfall | Correct approach |
|---|---|
| Assuming props are batched too | Props **have no batch concept** (unlike characters), but the **list must be confirmed before generating** — don't let it start drawing |
| Using an image with hands or people as a prop plate | A prop image must read as a "**product archive shot**" — clean, single item, identifiable detail; **images containing people or hands cannot serve as prop master plates** |

### P3 scene assets

Extracts scenes from the script's spatial chain and outputs a production list (scene name, plot function, lighting state, interaction points, necessity). After you confirm, it generates a 16:9 **empty-scene master plate (no people)** for each required scene, with different lighting states in the same space generated separately. After all are confirmed, it extracts a 5-colour environment palette per main scene (dominant / shadow / midtone / light-source colour / accent, labelled with HEX) and outputs the spatial direction chain and scene-character-prop interaction points.

**What you do:** confirm the scene list; review each plate and palette.

**Deliverables:** scene master plates, 5-colour environment palettes (with HEX), spatial direction chain.

**Pitfalls**

| Pitfall | Correct approach |
|---|---|
| People appearing in empty-scene plates | Must contain **no people** — that is the basis for overlaying blocking and first frames later; a plate with people has to be redone, or blocking cannot be overlaid at all |
| Only one image for a space | **Different lighting states** in the same space (day / night / rain / different sources) **need separate images**; don't expect one image to cover everything |
| Palettes without HEX | Must be **labelled with HEX** (dominant / shadow / midtone / light-source colour / accent — all five), otherwise they cannot be referenced later and the work is wasted |

### P4 | Shot design and first-frame generation

Breaks shots by dramatic beat (6–10 shots for a 30-second short; 15–30 shots for 1–3 minutes), outputs a full shot list (shot number, duration, shot size, angle, camera move, frame content, characters/props, scene, sound, emotional intensity). **Multi-person or multi-object shots first establish a "blocking baseline"**, then each shot takes values from it. It generates a 16:9 first frame per shot and rewrites character master files into per-shot performance passages with emotion propositions and beats.

**What you do:** confirm the shot list and **all** first frames.

**Deliverables:** shot list, blocking data, all first frames, per-shot performance passages, emotion beats.

**Its confirmation wording** (copy the whole block):

```text
[Please confirm] Are the above shot list and all first frames locked? Point out specific shot numbers to change.
[Next step after confirmation] Enter P5 and generate video prompts and OmniAiLab parameters for each shot.
```

**Pitfalls (this stage has the most)**

| Pitfall | Correct approach |
|---|---|
| Cross-shot blocking drift (left in one shot, right in the next) | Build a **blocking baseline** per scene; every shot reads from it and **only changes the fields that genuinely changed**, with unchanged characters inherited and frozen; **without evidence of a coordinate change, no position / facing / pose may be altered**. On drift, say `check blocking, run the cross-shot continuity protocol` |
| Writing "the two start fighting" for a fight shot | Fill in the **shot contract** first (narrative purpose → shot size → camera position / axis → A/B frame positions → primary move → trigger → end point → hand-off), then fix A/B sides and three spatial anchors, then choreograph |
| First-frame prompt missing the style prefix, or wrong reference order | Must carry the **P1 style prefix**; upload references by priority: **confirmed character plates > scene master plates > prop master plates** (max 6 per node) |
| Chinese text in frame while using the default image model | For **Chinese text** (signage, street signs, packaging, on-screen text) or a full storyboard board, switch to **image2.5** — otherwise glyphs and layout break |
| Planning to fix exposure, optics or in-frame text at the video stage | **The first frame is the final exposure and optics**: don't plan to darken later; keep **sky out of the composition** (it reliably drifts toward blue hour) and frame windows filled by the opposite wall; text is finalised here. Also: **every asset used must already be named and locked** — on-the-fly rewording breaks consistency |

### P5 | Video prompts and OmniAiLab parameters

Every shot has **two mandatory upfront layers** — ① use ACTING to rewrite the character master file into a "performance passage for this shot" (objective, obstacle, tactic, beats, listening, subtext, body and voice); ② use EMOTION to write the "emotion proposition + emotion beats + eye-line landing points + voice envelope" and complete character permission isolation and visual vocabulary purification. **Only when both layers are ready**, together with this shot's blocking / camera coordinates, reference tags and storyboard requirements, does CINEDANCE compose the final video prompt. It then outputs the parameter table.

**What you do:** confirm all video prompts and the parameter table.

**Deliverables:** per-shot video prompts + parameter table (shot number, model, duration, ratio, input method, reference list).

**Its confirmation wording** (copy the whole block):

```text
[Please confirm] Do you confirm all the above video prompts and OmniAiLab parameters? Point out specific shot numbers to change.
[Next step after confirmation] Enter P6 to batch-generate video in the OmniAiLab canvas, produce audio, and edit and export the film.
```

**Pitfalls**

| Pitfall | Correct approach |
|---|---|
| Skipping ACTING and EMOTION and writing video prompts directly; or bolting emotion on afterwards | **Hard prerequisite**: produce the per-shot performance passage (ACTING) and the emotion layer (EMOTION) first; only **when both are ready** does CINEDANCE compose. Skipping it means giving up performance and emotion control |
| Direct text-to-video | **Image-to-video is mandatory** (except pure black or text-only shots) — first frame per shot first, then the video |
| Wrong video model | Character shots → **Seedance 2.5**; VFX / transformation → **Kling O3**; prop close-ups → **Vidu**; fallback / trial → **Wan 2.6 / Seedance 2.0 Fast** |
| Putting aspect ratio, resolution, duration or model name into the prompt text | All belong in the platform UI — **never in the prompt text** |
| Incomplete action chain in fight shots | Full chain: attack intent → body and weapon motion → opponent response → contact feedback → displacement result → environmental aftermath; paired attack/defence, closed physical loop, no crossing the axis, one primary move per phase, **no ending on a posed freeze** |
| Not writing in the fixed block order, or not self-checking the iron rules | See **16-block order** and **eleven iron rules** below — dialogue goes only in the "sound and dialogue" block; the action block must contain not a single word of dialogue |
| Physics and continuity not written down | Door / window / opening geometry **repeated in full every shot**; prop scale as "**value + relationship**"; walking gets a **gait lock**, side-by-side "shoulder to shoulder on the same depth line", cross-shot **consistent camera speed**; fights use a **frame chain + single-take per-second timeline** |
| Missing the animation principles on an animation project | Add the **animation-principle five-set** per shot — **write them explicitly; the model defaults to averages**; reuse the same lighting wording verbatim shot by shot |

**16-block fixed order** (write video prompts in this sequence; copy the whole block):

```text
1  Scene context
2  Enabled references
3  Whole-film locks
4  Location map (GEO spatial map)
5  Eye-line and gaze
6  First-frame state and spatial occupancy
7  Format mode
8  Lens (optics)
9  Camera
10 Action timing
11 Performance task
12 Physics
13 Lighting
14 Sound and dialogue
15 Style and image quality
16 Positive lock
```

> **Dialogue goes only in the "sound and dialogue" block; the action block must contain not a single word of dialogue. All constraints go into the final "positive lock" block — never in negative form.**

**The eleven iron rules** (self-check every shot; copy the whole block):

```text
1  Say what is there, not what isn't (writing "no flags" summons flags)
2  Bind geometry to the frame, not to objects ("left of the gun" reads as left of frame)
3  One reaction per beat
4  Imply scale through cues, never metres (prop scale as "value + relationship")
5  Countable events need visual evidence (one flash = one rocket)
6  Write action as a physical beat chain
7  Adjacent shots must differ in size and angle
8  Check countable body parts ("only two hands, both in the same sleeve")
9  Switch off unwanted things in references
10 Never write ages (content filters tighten sharply on minors)
11 Maintain a banned-word dictionary ("dark" → "low-key", "bumpy" → "fast motion")
```

### P6 | Generation, editing and export

Guides you through creating a project on OmniAiLab (omniailabx.com) and uploading all pre-production assets to the asset library; builds the canvas as "script → images → video → audio → editing → export". **Confirm all first frames first, then batch-queue video generation**, checking and retrying shot by shot. AI voice-over (matched to character timbre), BGM (entering/exiting per the emotion curve), layered sound effects (ambience / action / accent). Assemble by shot, layer audio tracks, add subtitles. Export 1080p / 16:9 / 24fps / MP4 / H.264, then run item-by-item QC.

**What you do:** follow the guidance on the platform; confirm all first frames before batch generation.

**Deliverables:** finished MP4 + full asset pack + QC report.

**Pitfalls**

| Pitfall | Correct approach |
|---|---|
| Batch-generating before all first frames are confirmed | **Always confirm every first frame before batch generation** — one wrong frame wastes an entire generated video, **the most expensive rework there is** |
| Laying BGM by feel | In/out points must **follow the P0A emotion curve** — mark only the nodes needing push / reversal / build-up / release |
| Editing and sound not following the phases | Rough arrangement → rough cut → generation supervision → fine cut → **final cut**; no new generation after final cut except emergency fixes. Match transitions by **movement direction + sound**, leave **8 frames** of headroom and tailroom per segment, cut on the frame where the covering element **fills ≥90% of frame**; colour is **unified**, not graded shot by shot |

---

## Sub-skills and specialized layers

You don't need all of them every time. **To do just one small thing, say "only do …"** and it calls only that sub-skill, skipping the full pipeline.

### The four sub-skills

| Sub-skill | File | Responsibility |
|---|---|---|
| **ACTING** | `references/ACTING GUIDE.md` | Turns abstract emotion into camera-visible behaviour: objective, obstacle, tactic, beats, listening, physical tasks, subtext, eye-line and vocal identity |
| **EMOTION** | `references/EMOTION GUIDE.md` | Writes emotion as a character processing an event within a relationship: emotion proposition, internal/external lines, emotion beats, eye-line landing points, voice envelope; plus character permission isolation, contact boundaries, visual-vocabulary purification and generation-failure repair |
| **LIRA** | `references/LIRA GUIDE.md` | Optimises image generation / editing prompts and routes models; look comes from the visual-language library, whole-film aesthetics from the aesthetics recipe library |
| **CINEDANCE** | `references/CINEDANCE GUIDE.md` | Turns shot requirements into executable video prompts, controlling first frame, spatial staging, eye-lines, optics, lighting, physics and continuity |

### Specialized (mounted) layers — not counted as separate sub-skills

| Layer | File | One-line summary |
|---|---|---|
| **STYLE** visual-language library | `references/STYLE GUIDE.md` | **Dictionary**: D director visual languages / P general photographic styles / C capture stocks / R print stocks / S style strength |
| **AESTHETICS** recipe library | `references/AESTHETICS GUIDE.md` | **Recipe book**: A01–A07 seven whole-film aesthetics; **proactively triggered** — P1 always proposes 2–3 candidates |
| **COMBAT** | `references/COMBAT GUIDE.md` | Attack/defence choreography, closed physical loops, three spatial anchors, shot contracts |
| **BLOCKING** | `references/BLOCKING GUIDE.md` | Cross-shot blocking lock: one baseline per scene + `locked` freeze + drift diagnosis; **mandatory for multi-person shots** |
| **PROMPT-DOCTRINE** | `references/PROMPT-DOCTRINE GUIDE.md` | Fixed 16-block order + eleven iron rules + solve hard things in the still frame + how to write physics and continuity |
| **ASSET-SYSTEM** | `references/ASSET-SYSTEM GUIDE.md` | Text + image paired assets, `@char_/@loc_/@prop_/@staging_` naming, "new state = new asset", voice lock |
| **SCENE-ENGINE** | `references/SCENE-ENGINE GUIDE.md` | Five-element dramatic engine (objective / obstacle / tactic / reversal / value shift) + script stress test; **diagnose only, never rewrite** |
| **FILM-ART** film-art knowledge layer | `references/FILM-ART GUIDE.md` + `references/film-art/` (30 knowledge files) | **Read-only judgement and source layer**: 15 domains + 39 capability cards + an index of 118 works, covering what to think about and where the criteria are (spine and fulcrum / relation line and triangle principle / blocking motivation / cut criteria / six sound-design frames / genre contract / resource-driven planning / shot-level film analysis); **produces judgements, evidence and checklists only, never prompt wording**, execution criteria stay with the existing layers; raises judgement at P0A / P1 / P4 |
| **OPTICS** | `references/OPTICS GUIDE.md` | Seven field-of-view anchors (8/18/29/47/84/107°), lens decision tree, multi-shot lens consistency statement |
| **DIRECTOR-VISION** | `references/DIRECTOR-VISION GUIDE.md` + `examples/director-presets/` (20 presets) | Turns "in the style of a director" from adjectives into **reasoning**: six-axis mechanism, **counter-example discipline** (state the mechanical difference from adjacent directors), **mixing rules** (one primary + borrowed axes), **Director Style Statement** (frozen / variable / forbidden); 20 presets, recommended by genre, selectable in combination |
| **CAMERA-LIGHT** | `references/CAMERA-LIGHT GUIDE.md` | Five-axis camera coordinates (body format × lens character × focal × aperture × movement); **four-way dispatch lookup tables by genre / scene / character / story beat** (16 genres, 22 scenes, 16 character functions, 18 story beats) plus 10 quick-response cards + three-light structure and colour-temperature variants; **intent → combination lookup** (`examples/camera-light/`) and a block 9 / block 13 injection template; **hardware tiers are selection-only, prompts carry observable results** |
| **FEATURE-PRODUCTION** | `references/FEATURE-PRODUCTION GUIDE.md` | Four shot-table card groups, per-scene opening ritual, asset stress tests, iteration discipline, statute-style locks |
| **MUSIC-SCENE** | `references/MUSIC-SCENE GUIDE.md` | Sing-first-then-perform with lip sync: cut 12-second blocks, black-frame video files, disable generated audio, hard lip lock |
| **MOTION-STUDIO** | `references/MOTION-STUDIO GUIDE.md` + `references/motion/` (rules) + `examples/motion/` (assets) | **The code-rendered track** (parallel to — and interleavable with — the generative promo track): real page screenshots + 2.5D camera moves + beat-synced cuts + cinematic SFX, rendered frame by frame. Ships **157 motion shot recipe cards** (ten categories, each with intent / parameter table / known pitfalls / reference implementation), seven rule documents, a runnable project template and **154 sound-effect assets**. **It judges fitness first** — live-action drama, concept-only with no product, realistic natural scenes or very long pieces get an explicit "not this track"; **purpose decides the form** (website / app store / launch event / social feed / sales) |
| **CHANNEL-SELECT** | `references/CHANNEL-SELECT GUIDE.md` | **Deciding whether a given promo goes generative or code-rendered**: a two-track comparison, **five criteria** (subject / pixel accuracy / capturable real interface / frame-exact control / length & placement), **three reminder points** (hint at format selection / formally confirm and lock after assets, before storyboarding / re-judge the moment the user changes their mind), three copy-paste scripts, a **four-family scenario table** (including **TV promos split by format**: channel IDs, show packaging and large screens go code-rendered; programme trailers, TVCs and public-service spots go generative), the **hybrid hand-off split** ("anything live-action and moving goes generative; everything on a screen goes code-rendered") and eight efficiency-and-empathy hard rules |
| **PROMO** | `references/PROMO GUIDE.md` | Dispatch across 14 commercial-short directions (brand ad / TVC, brand short, stream MG, product film, UI motion, title sequence, motion design, game PV, music short, creator video, education, drawing timelapse, video deconstruction, voice clone) + six-step flow and commercial hard rules; **video generated with MiniMax H3 on the OmniAiLab canvas** |
| **ONBOARDING** | `references/ONBOARDING GUIDE.md` | **Settle the format first**: a routing table for film / short drama / animation / documentary / promo / title / MV / game PV / UI motion / creator video / education + a three-question convergence method |
| **DOCUMENTARY** | `references/DOCUMENTARY GUIDE.md` | Observational documentary: eight spec items, de-dramatised narration, 6–12 s shots with three-tier camera moves, natural-light logic and airborne texture, cross-shot character consistency, colour-system extraction; **enabled when the conversation is a documentary**, while generation methods stay on the existing film-grade layers |
| **ANIMATION** | `references/ANIMATION GUIDE.md` | Medium determination, previs vs generation division of labour, hybrid aesthetic split, light defines style, 360° turnaround video, animation principles first |
| **Case-study library** | `examples/case-studies/` | Finished prompt blocks from six commercial-grade AI film projects + "problem → solution" lists, **copy-paste ready** |
| **Documentary templates** | `examples/documentary/` | Seven ready-to-use documentary prompt templates: character turnaround / look board / location / prop / colour card / first frame / video |
| **Case-study figures** | `examples/images/` | 49 method diagrams (how a three-panel character sheet is laid out, how states are separated, what a staging diagram looks like, what colour drift looks like, what "a moving prop behaving like a decal" looks like) + a keyword→figure lookup in `INDEX.md`; ~2.4 MB |
| **Promo sample library** | `examples/promo-cases/` | Raw briefs and finished prompts from **7 real MiniMax H3 films**, organised by direction (brand ad ×4, visual design ×2, UI motion ×1), with a source-record → sub-skill → file mapping table |

### Dispatch quick reference

| What you want to do | What it calls |
|---|---|
| Images only (asset generation or image editing) | LIRA (look from the STYLE library) |
| Video prompts only | CINEDANCE |
| Performance design only | ACTING |
| Emotion only (crying / laughing / anger / fear / disappointment / farewell / reunion / silent reactions; or fixing dead eyes, stray tears, emotion bleed, accidental kissing, dialogue clipping, intensity jumps) | EMOTION |
| Look selection only ("give me the look menu", "D01+C04+R01+S2") | STYLE library |
| Aesthetic selection only ("what style for this scene", "give me aesthetic advice") | AESTHETICS library |
| Fight choreography only ("how should this fight go") | COMBAT layer |
| Blocking / staging only ("how should these people stand", "the positions shifted again") | BLOCKING layer |
| "How do I write this prompt so it doesn't break" | PROMPT-DOCTRINE layer |
| "How do I build / name assets so they don't drift" | ASSET-SYSTEM layer |
| Ready-made sentences / what others got wrong | Case-study library (`examples/case-studies/`) |
| Want to see what a rule actually looks like / "I don't get it" | Case-study figures (`examples/images/`; lookup table in `images/INDEX.md`) |
| Want to copy a **real, already-produced** promo sample / see how a direction is actually written | Promo sample library (`examples/promo-cases/`, organised by direction) |
| Director style selection ("who should direct this", "Wong Kar-wai + Fincher?") | DIRECTOR-VISION layer (offers 2–3 candidates by genre first) |
| Camera setup / lighting only ("what lens and light for this shot", "that clean product look", "how should the whole thriller be lit") | CAMERA-LIGHT layer (dispatch lookup first: genre → scene → character → story beat) |
| Script structure only ("does this scene work", "where is it weak") | SCENE-ENGINE layer |
| Lens choice / lens drift only ("how wide should this lens be") | OPTICS layer |
| How to organise a feature ("how to manage 100+ scenes") | FEATURE-PRODUCTION layer |
| Singing / rap sections ("lip sync is off", "how do I make it sing our song") | MUSIC-SCENE layer |
| Animation / hybrid medium ("can this be animated", "moving objects look like stickers") | ANIMATION layer |
| Documentary only ("I want to make a documentary", "how do I shoot real people", "how to use natural light") | DOCUMENTARY layer |
| "Generative or code-rendered for this one" ("MiniMax H3 or code rendering", "can it reproduce our interface", "these words keep changing", "how do I make a TV promo", "large-screen loop") | CHANNEL-SELECT layer (judgement first, locked before storyboarding) |
| Commercial short / promo only ("I need a promo", "a brand ad", "logo animation", "UI motion", "title sequence", "game PV") | PROMO line (pick a direction first) |
| "I do not know what to make" / "where do I start" | ONBOARDING layer (settle the format) |

**Full shot chain:** ACTING → EMOTION → BLOCKING (blocking first) → LIRA (+ STYLE look) → CINEDANCE. **Fight shots** route through COMBAT before CINEDANCE. **Before writing, pass the PROMPT-DOCTRINE fixed block order and iron rules; name and lock every character / scene / prop per ASSET-SYSTEM first.**

---

## Model reference

These are the whole-film's single source of truth. **Do not mix in model names from other platforms.**

| Purpose | Model | When to use it |
|---|---|---|
| Character generation / consistency | Seedream 5.0 | First choice for P2 character boards; the most stable across shots |
| Scene / environment master plates | Flux | P3 location plates, environment colour cards and empty sets |
| Prop / product master plates | Nano Banana Pro (香蕉Pro) | When physical detail and material must be reproduced exactly |
| Image editing (first choice) | Nano Banana Pro (香蕉Pro) | Strongest at local edits, state changes and detail fixes |
| Rough AI texture repair | Seedream | When a generation comes out plastic or mushy |
| Local micro-edits / location viewpoint changes | Qwen Image | Change one small area, or shift the location viewpoint without touching the style |
| Images: general generation (common) | image2 | Everyday assets — fast and cheap |
| Images: Chinese text / covers / posters / storyboards | **image2.5** | First choice whenever Chinese lettering appears in frame; stronger at Chinese than Nano Banana Pro |
| Video: characters | Seedance 2.5 | Shots with performance and dialogue |
| Video: VFX / transformation | Kling O3 | Transformations, explosions, morphing |
| Video: prop close-ups | Vidu | Small-object inserts and product showcases |
| Video: fallback / trial | Wan 2.6 / Seedance 2.0 Fast | Try a cheap version first, then decide which model to shoot the final on |

> **Hard image-model constraint:** whenever Chinese text appears in frame (signage, packaging, posters, covers, books, screens / subtitle boards, street signs) or the deliverable is itself a cover, poster or storyboard (full shot-breakdown board), **always prefer image2.5** — its Chinese glyph shapes and layout are the strongest (stronger than Nano Banana Pro), and its character consistency and storyboard continuity are best too. Use image2 for general generation. **Do not treat Nano Banana Pro as the default choice for these tasks.**

---

## Pitfall table

These **29** items are ordered by "likelihood × severity". Scan them before the P1, P4 and P5 confirmations.

| # | Pitfall | Correct approach |
|---|---|---|
| 1 | Multi-person blocking drifts across shots: on one side in the last shot, gone in the next | One blocking baseline per scene, read per shot, change only changed fields, freeze unchanged characters; no coordinate-change evidence, no blocking edits |
| 2 | Skipping performance and emotion when writing video prompts | ACTING must produce the shot's performance passage + EMOTION the emotion layer, then CINEDANCE composes |
| 3 | Chinese in frame but using the default image model | Chinese text / covers / posters / storyboards → always prefer image2.5 |
| 4 | Writing 16:9, 10 seconds or a model name into the prompt body | Ratio, resolution, duration and model name belong in the platform UI, never the body |
| 5 | Stacking "no XX" / "exclude XX" in prompts | Always express positively ("exclude digital feel" → "photochemical film texture") |
| 6 | Writing film stock as real capture ("shot on 70mm film") | Write "70mm film **simulation** texture"; don't pretend it is physical film |
| 7 | Writing a director's name in the prompt ("X's style") | Names are internal retrieval tags only; convert to concrete visual traits for delivery |
| 8 | Referencing a non-existent image (`{{Image 3}}` without uploading) | With no real reference, delete all asset numbers and inheritance wording |
| 9 | Wanting to change the look after the style lock | The lock is frozen; changing it means going back to P1 |
| 10 | Emotion curve is high-energy throughout with no breathing zone | 8–14 nodes, at least one genuine breathing zone, no invented release |
| 11 | Skipping character batches: writing downstream states before upstream confirmation | Unlock by dependency batch; blood relatives / variants / costume / injury / age only after base characters are locked |
| 12 | Writing "the two start fighting" for a fight shot | Fill the shot contract, fix A/B sides and three spatial anchors, then choreograph the spine and physical loop |
| 13 | Asking for five confirmations at once to finish in one go | Show only the step needing confirmation each round; only a genuine confirmation unlocks the next |
| 14 | Treating confirmed images as drafts and regenerating them | Confirmed means frozen and depended upon downstream; regenerating invalidates everything downstream |
| 15 | Writing "lens character" into video prompts (wanting anamorphic), then lenses drift shot to shot | Bake optical character into the **scene plate**; in video prompts you cannot even write "no flare" — naming flare summons flare |
| 16 | Night scenes won't go dark; the model keeps giving dusk | **Bake the darkness into the plate** (2–3 stops down, crushed blacks, one cold rim light) + **crop the sky out** |
| 17 | Overwriting a new state onto an old asset (costume change / injury on the same image) | **New state = new asset + new name**; keep the old asset — overwriting robs every prior shot of its reference |
| 18 | Cool footage gets pulled warm; "no yellow" does nothing | Use a positive **"colour constitution sentence"**; for uncroppable glowing objects in references write "**it is switched off in this film**"; choose stock by where the shadows lean |
| 19 | Stairs vanish and a character jumps up in one move; walking slides or floats | Write ascent as physics + **name openings as objects that must exist**; add a **gait lock**; write "shoulder to shoulder on the same depth line" for side-by-side; **consistent camera speed** across shots |
| 20 | Splitting a fight across generations always stutters; editing can't save it | **Frame chain** (segment N's last frame = N+1's first) + a hero shot that is **single-take, per-second timeline, with slow motion explicitly banned**; **name every action and give it a vector** |
| 21 | Generating without a script health check, discovering mid-way that a scene doesn't work | Run the **five-element engine** first for its **single weakest point** and three-layer fixes; hunt **inert reversals**. **Diagnose only, never rewrite** |
| 22 | Faces, voices, seating and eye-lines all drift across dozens of shots in one room | **Sound bible** (a VOICE LOCK block per character, pasted verbatim) + asset **scene suffixes** + beat timing per segment + eye-line as its own block |
| 23 | Shot size and perspective drift (wide-angle feel comes and goes) | Choose lenses by **content type** (FOV anchors 8/18/29/47/84/107°); never mix incompatible content categories in one beat; write a **lens consistency statement** |
| 24 | Heroes teleport, swap places, or the camera jumps across the room | Give every scene an **opening ritual**: a one-second fixed-blocking wide master + a **GEO spatial map** + a **compass sentence** (never cross the 180° line) |
| 25 | A shot stalls for a dozen versions and gets worse | **Ten-to-fifteen rule**: past that it isn't wording — **change the shot**; iterate **one change at a time** and **log everything** |
| 26 | Lip sync is off in sung / rap sections, or generation is blocked by copyright checks | Sing first, perform second: cut the final mix into **12-second blocks**, make **black-frame video files**, **disable generated audio in settings**; then write a **hard lip lock** and **mouth ownership** |
| 27 | Moving objects look like "stickers", surfaces go dead, brushwork looks flattened | Moving objects get **clean solid volume**; heavy brushwork is reserved for the environment; hybrid aesthetics need a **"split declaration"** |
| 28 | Hand-painted / stylised environments look flat, stuffy, volume-less; a different shot no longer looks like the same film | Switch to **golden-hour side-backlight + long, crisp shadows**; and use **one lighting wording for the whole film, reused verbatim shot by shot** |
| 29 | Static character sheets can't hold cross-generation consistency; characters get invented by the model | Animation lines use a **360° turnaround video** (turn / expression / voice) as the primary character reference; **every moving asset must pass a video test first** |

---

## Repository layout

```text
omniailab-ai-director/
├── GUIDE.md                     # Master dispatcher: P0→P6 trunk, gates, sub-skill mapping, model reference
├── VERSION                      # Version number
├── openai.yaml                  # Interface metadata (display_name / default prompt / implicit invocation)
├── LICENSE                      # MIT
├── README.md                    # Simplified Chinese
├── README_EN.md                 # This file (English)
├── references/                  # Specification layer: four sub-skills + all specialized layers + dictionaries
│   ├── ACTING GUIDE.md
│   ├── EMOTION GUIDE.md
│   ├── LIRA GUIDE.md
│   ├── CINEDANCE GUIDE.md
│   ├── STYLE GUIDE.md
│   ├── AESTHETICS GUIDE.md
│   ├── aesthetic-recipes.md
│   ├── COMBAT GUIDE.md
│   ├── BLOCKING GUIDE.md
│   ├── blocking-stage-schema.md
│   ├── blocking-weapon-library.md
│   ├── PROMPT-DOCTRINE GUIDE.md
│   ├── ASSET-SYSTEM GUIDE.md
│   ├── SCENE-ENGINE GUIDE.md
│   ├── FILM-ART GUIDE.md       # Film-art knowledge layer: a 15-domain judgement and source layer (judgement only, no prompt wording)
│   ├── OPTICS GUIDE.md
│   ├── FEATURE-PRODUCTION GUIDE.md
│   ├── MUSIC-SCENE GUIDE.md
│   ├── ANIMATION GUIDE.md
│   ├── DOCUMENTARY GUIDE.md
│   ├── CHANNEL-SELECT GUIDE.md  # Channel-select layer: generative vs code-rendered, and how to choose
│   ├── PROMO GUIDE.md
│   ├── ONBOARDING GUIDE.md
│   ├── MOTION-STUDIO GUIDE.md   # Motion-studio layer: the code-rendered track (real UI screenshots + 2.5D moves + beats + SFX)
│   ├── motion/                  # Motion-studio RULES: seven rule docs (workflow / guided co-creation /
│   │                            # aesthetic criteria / sound design / beat sync / final checklist / CapCut export)
│   ├── promo/                   # 14 promo directions (78 files, original detail folders preserved)
│   ├── film-art/                # Film-art knowledge files (30: outline / card index / glossary / digest / 15 domain handbooks / bibliography and audit trail)
│   ├── story_bible.md / emotion_curve.md / creative_baseline.md
│   ├── character_assets.md / prop_assets.md / scene_assets.md
│   ├── storyboard.md / video_prompts.md / omniailab_production.md
│   ├── director-styles.md / photo-styles.md / capture-films.md / print-films.md
│   ├── shot-emotion-engine.md / performance-palette.md
│   ├── generation-guardrails.md / seedance-production.md
│   └── (43 specification documents in total; plus 78 direction files under promo/, 7 rule docs under motion/, 30 knowledge files under film-art/)
└── examples/                    # Finished-work layer: copy-paste ready
    ├── floor17_script.md        # Sample script "Floor 17" (30-second suspense short; only on request)
    ├── aesthetics/              # Ready-made prompts for the seven A01–A07 aesthetics
    ├── case-studies/            # Six commercial-grade AI film case studies + README stage index
    ├── documentary/            # Seven ready-to-use documentary prompt templates
    ├── director-presets/        # 20 director presets (selection + genre recommendations + mixing rules + axis mapping)
    ├── camera-light/            # Camera & lighting indexes (five-axis coordinates + 33 lighting setups + dispatch tables by genre/scene/character/story beat)
    ├── motion/                  # Motion-studio ASSETS (Remotion-bound, copy-paste ready): 157 shot cards (10 categories)
    │                            # + bridge templates + runnable project template + per-card reference implementations
    │                            # + components + 154 sound-effect assets + CapCut export scripts (638 files)
    ├── promo-cases/            # Seven real promo samples + index (organised by direction)
    └── images/                  # 49 case-study figures + INDEX.md (keyword → figure lookup), ~2.4 MB
```

> **Specifications live in `references/`; copy-paste-ready finished work lives in `examples/case-studies/`; the visible look of it lives in `examples/images/`.** Whenever it's a question of "how exactly do I write this sentence", take a finished block from `examples/case-studies/` first. Whenever it's a question of "what does that actually look like", show the figure from `examples/images/` (see the keyword lookup table in its `INDEX.md`). Whenever it's a question of "how is a given commercial-short direction actually written", take a sample from `examples/promo-cases/` first. Whenever it's a question of "what camera setup and light for this shot", start from the two indexes in `examples/camera-light/`.

---

## Deliverables

After a full run you get:

1. The final MP4
2. All first frames (packaged)
3. All video segments (packaged)
4. OmniAiLab canvas project link
5. Final QC report
6. Project asset pack (character / prop / scene images + all prompt documents)

---

## FAQ

**Q: I want to change the look mid-way.**
A: Go back to P1. Downstream assets are invalidated as a consequence, so settle the look at P1.

**Q: It keeps asking for confirmation — can it just finish in one go?**
A: Gates are an anti-rework mechanism, not process decoration. Each confirmation point carries a batch of dependent deliverables — skipping it magnifies the error into the next stage.

**Q: Can I use only one part?**
A: Yes. Say "images only", "blocking only", "fight choreography only" — see the dispatch table above; it skips the full pipeline.

**Q: Must generation happen on OmniAiLab?**
A: Sub-skills handle "how to describe it" (prompt construction and model selection); actual generation runs on OmniAiLab, and model naming follows the table above. You may also generate on an external platform, but align model names with this reference.

**Q: Can I change the script mid-way?**
A: Only details that **don't change assets**. Once characters, scenes or the ending change, previously generated assets must be redone.

**Q: I don't want the aesthetic proposal — can I skip it?**
A: Yes. Reply "no need" and it continues with standard sourcing; with no match it says so rather than forcing one.

---

## Recommended tools and models

This Skill is a pure-text specification and is not bound to any one model — it runs on any tool or model. But the pipeline is long (P0→P6, dozens of generation instructions), so **the stronger the model, the less likely it is to lose context or miss a gate mid-run.**

| Tool | Best used for |
|---|---|
| **Codex** (recommended) | Running the full P0→P6: strong engineering, direct project-file access, batch asset-list processing and scripted output organisation |
| **Claude** | Script breakdown, prompt refinement, long-form documents (native Skill support, stable long-text rewriting) |
| **WorkBuddy** | Running the full P0→P6: read/write files and run scripts in-session, with each stage's output landing on disk |
| **OmniAiLab** (omniailabx) | Running the full P0→P6: a chat client in the same class as WorkBuddy, [download from the official site](https://www.omniailabx.com/plugin) (Windows local build v0.8.16; [mirror link](https://pan.baidu.com/s/12Wtj8pAKmXOGgWN-M07v7A?pwd=2gff) access code `2gff`); read/write files and run scripts in-session, generation unified in the OmniAiLab canvas |

**Model guidance**

- **Preferred:** the latest generation such as GPT-5.6 or DeepSeek V4 — steadier long-context and instruction following, less mid-run "amnesia" or missed gates.
- **Workable:** any reasoning model with ≥64K context can complete the pipeline, but double-check outputs at each gate.
- **Not recommended:** lightweight models on the full pipeline (the P0A ten-item breakdown is the easiest place to lose items).

> Which models you can actually choose depends on your account; models cycle fast and this Skill needs no change — it specifies "how", not "with whom".

---

## System requirements

This Skill is a **workflow specification and prompt system**. It deploys no local service and consumes no local compute — **all image and video generation happens inside the OmniAiLab canvas**. What matters is the client that runs the conversation and where you keep your assets.

| Item | Minimum | Recommended | Purpose |
|---|---|---|---|
| Chat client | An AI coding assistant that can read local files (any of Codex / Claude / WorkBuddy / OmniAiLab) | As above; **Codex** is the most stable on long pipelines | Loading the Skill and producing prompts and project files stage by stage |
| Local disk | 1 GB free | 5 GB or more | The Skill itself is about 3 MB; final cuts, first frames and asset images are stored per project |
| Network | Access to OmniAiLab and to your chat service | Stable broadband | Generation, asset download, repository sync |
| Browser | Chrome or Edge from the last two years | Latest version | Running generation in the OmniAiLab canvas |
| Generation compute | **No local GPU required** | — | All generation runs in the OmniAiLab cloud |
| Optional local software | — | 3D previs, compositing and motion, raster retouching, procedural and real-time visual tools | Only when a project needs them; the Skill produces specifications and prompts only |

**What you do not need**: a local model, a vector database, any API key, or a professional GPU. Generation parameters are chosen in the OmniAiLab canvas, subject to the models the platform currently offers.

---

## Companion manual

This README covers every point of the manual; **the full manual is published in both a Feishu doc and Notion, with identical content**, version-synced with the Skill:

- **Manual — Feishu (primary):** <https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA>
- **Manual — Notion (same content):** <https://tomatopark.notion.site/3eaa28d2e378800d8b8bee090c32c34d>

> **Mandatory sync:** every Skill update (version number, trunk workflow, model reference, or sub-skill wiring) must be reflected in that manual **and** in both READMEs, keeping version numbers aligned.

---

## Contributing

This repository is open source under the **MIT License** — contributions are welcome. One rule applies to everything: **submit methods, specifications and prompts only, and introduce no third-party platform dependency** — all generation happens in OmniAiLab and must match the existing conventions.

### Ways to contribute

| Area | What to submit | Where |
|---|---|---|
| New director preset | Write a new director following the six-part structure; it **must include a "counter-example: the nearest director it is confused with" section** and state the mechanical difference rather than an adjective difference | `examples/director-presets/`, plus one row in each of the index tables |
| New camera and lighting combinations | New lens-character tiers, lighting setups, intent tags and use-case tags | The two index files under `examples/camera-light/` |
| New case study | A post-mortem of a real finished project: ready-to-use prompt blocks plus a "problem → solution" list | `examples/case-studies/` |
| New commercial-short direction | Follow the structure of the existing directions and keep that direction's own `references/` | `references/promo/` |
| New aesthetic recipe | A film-level recipe plus ready-to-use prompts | `references/aesthetic-recipes.md`, `examples/aesthetics/` |
| Fixes and completion | Typos, outdated wording, broken links, inconsistent counts, tables that do not span full width on GitHub | Open a PR or an issue |

### How to submit

```bash
git clone https://github.com/tomatoparkdao/omniailab-ai-director.git
cd omniailab-ai-director

# Self-check after your change (all three are hard requirements)
# 1) every .md opens with the eight-item frontmatter and closes with the attribution footer
# 2) any new or edited table must span full width on GitHub
# 3) the version number stays aligned across GUIDE.md / VERSION / openai.yaml / both READMEs

git add -A
git commit -m "docs: what changed"
git push
```

### Code of conduct

Professional, evidence-based, reproducible. The test for any discussion is "does this make a better film": a new method must land on executable parameters — no piles of adjectives, and no verbatim reuse without attribution.

---

## License & Legal

This repository is released under the **MIT License** — see [LICENSE](LICENSE). You may freely use, modify and distribute it, including commercially, provided the copyright and permission notice is retained.

> Attribution note: every file in this Skill keeps `© OmniAiLab ｜ Developer: Mochiball` in its frontmatter and footer. That notice identifies the source and preserves brand attribution; **it does not impose any restriction beyond the MIT License.**

**By using this Skill you acknowledge and accept the following:**

- **No warranty** — no guarantee of output quality, platform availability, or fitness for any particular purpose.
- **Costs are yours** — any fees charged by OmniAiLab or any third-party tool are the user's sole responsibility.
- **Human review is mandatory** — every generated image, video, audio track and piece of copy **must be reviewed by a person before publication**; responsibility for content compliance rests with the user.
- **Third-party rights** — no license is granted for any third-party trademark, brand, likeness, music or footage; clear your own rights for real people, brand marks and copyrighted music or video material.
- **Source of materials** — the methods in the case-study library are **distilled and rewritten in Chinese** from public post-mortems; method extraction only, no verbatim reuse. Rights holders who believe something is used improperly can reach us via an issue.
- **Liability** — the author and maintainer accept no liability for any loss caused directly or indirectly by use of this Skill.

---

## Credits

- Publisher and maintainer: **OmniAiLab** ([omniailabx.com](https://www.omniailabx.com/))
- Developer: **Mochiball**
- The methods in the case-study library are **distilled and rewritten in Chinese** from public post-mortems of several commercial-grade AI film projects — method extraction only, no verbatim reuse, with attribution unified under OmniAiLab.
- This Skill uses only **OmniAiLab**'s own platform capabilities and introduces no third-party platform dependencies.

---

<div align="right">

[简体中文](README.md) ｜ **English**

</div>

> © OmniAiLab ｜ Developer: Mochiball ｜ omniailabx.com
