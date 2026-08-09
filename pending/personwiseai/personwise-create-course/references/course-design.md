# Design a high-quality PersonWise course

## Build the blueprint before creation

Write a concise, secret-free blueprint:

- learner and prerequisite knowledge;
- observable learner outcome;
- course class: `concrete-object`, `open-ended`, or an explicitly partitioned hybrid;
- dominant teaching archetype from `course-archetypes.md`;
- factual authority: open research, strict supplied materials, or source-assisted research;
- language and earned page count;
- page-by-page teaching arc;
- examples, comparisons, diagrams, tables, illustrations, and guided practice that earn their
  space;
- visual system and prohibited motifs;
- spoken style and Voice-delivery brief;
- presenter brief covering the teaching job, warmth/authority, energy, formality, framing, and
  language compatibility;
- final target: draft, private, link, or separately authorized Topics review.

Choose page count from the learner promise:

- 4–8 pages for one bounded workflow or interpretive lens;
- 8–16 for a focused lesson;
- 16–26 for mechanisms, examples, counterarguments, practice, and synthesis;
- 26–30 only when the depth is real.

Do not pad. Each page needs one primary teaching job and a reason for its visual form.

## Understand the creation fields

| Field | Public meaning |
|---|---|
| `name` | Visible course title, at most 200 characters. |
| `topic` | Compact course constitution, at most 200 characters. It strongly guides Outline, metadata, style, and—when `content` is absent—Narration. |
| `description` | Learner-facing summary, at most 500 characters. |
| `target_audience` | Audience, prerequisites, context, and success criterion, at most 500 characters. |
| `content` | Aligned long-form generation input, at most 8000 characters. It does not replace uploaded strict sources. |
| `language` | Course language/locale; also constrains presenter Voice compatibility. |
| `desired_slide_count` | Fixed page count from 1–30. Count/order cannot be changed through this public workflow after creation. |
| `style_instruction` | Global visual system, at most 2000 characters: palette, medium, typography character, composition rhythm, and constraints. |
| `script_style` | Spoken teaching behavior, at most 2000 characters: tone, pacing, explanation structure, analogy policy, and narration exclusions. |
| `voice_render_style_instruction` | TTS delivery direction, at most 300 characters; no factual content. |
| `avatar_id` | Optional known compatible presenter UUID. Prefer later catalog review rather than guessing. |
| `voice_id` / `voice_plane_voice_id` | Optional known compatible Voice lane UUID. Never invent or mix an unrelated presenter/Voice pair. |
| `knowledge_source_mode` | `open` or `materials_only`; fixes the factual acquisition boundary. |
| `declared_sources` | Exact retained document count expected before deferred project creation. |
| `visual_review_capability` | Declare `multimodal` only when this Agent can truly inspect downloaded review images; otherwise `none`. |
| `distribution_target` | `draft`, `private`, `link`, or `topics_review`, bounded by OAuth consent and advertised capabilities. Always set it explicitly: when omitted it resolves to the OAuth grant's publication ceiling, which can be `link`; use `private` unless the user asked for broader access. |

At least one of `topic`, `content`, or a declared source is required. `materials_only` requires at
least one declared source.

## Respect `topic` and `content` precedence

The generation pipeline uses `topic` before `content` for the Outline and project initializers, but
uses `content` before `topic` for Page text and Narration. Therefore:

- Use `topic` alone for one compact instruction that must propagate consistently.
- When long `content` is needed, make it semantically identical to the `topic` constitution.
- Put audience, visual style, script behavior, and Voice delivery in their dedicated fields.
- Never place conflicting instructions in `topic` and `content`.
- Uploaded strict materials govern facts; `topic`/`content` still govern selection, organization,
  teaching intent, and exclusions.

A useful compact topic contains:

```text
subject + learner promise + arc + required visual grammar + exclusions
```

Example:

```text
Forces that shape Earth's surface (internal forces → external forces → landform evidence →
human consequences; use cross-sections, process diagrams, and comparisons; one causal relationship
per page; avoid tourism-poster scenery)
```

## Choose the knowledge boundary

### Open research

Use `knowledge_source_mode=open` when the model may select and synthesize generally available
knowledge. Sources may be absent.

Review concrete claims for accuracy and currency. Open mode is not permission to invent exact
metrics, quotations, product interfaces, chronology, or attribution.

### Strict supplied materials

Use `materials_only` when correctness means staying within the supplied PDF, PPTX, DOCX, Markdown,
or TXT files.

Before creation:

1. Retain only authoritative files.
2. Set `declared_sources` to their exact count.
3. Build a source map:

   ```text
   source -> authoritative sections/claims -> intended pages -> claims that must not be added
   ```

4. Request and complete one document upload ticket per source.
5. Wait until every retained source reaches canonical complete state.

Do not silently switch to open mode when a source fails. Strict mode is a generation constraint,
not a compliance certificate: inspect every claim, remove unsupported additions, distinguish
source statements from implications, and surface source disagreement instead of merging it into
false certainty.

### Source-assisted open research

Use `open` with documents when supplied facts should anchor the lesson but relevant outside context
is allowed. Label this honestly; do not describe it as strict source compliance.

## Apply the editorial-authority boundary

Read `course-archetypes.md` before correcting model-authored content.

For a `concrete-object` course, verify the external object's facts, claims, chronology, UI,
capabilities, relationships, outputs, metrics, and source imagery. Plausible specificity is still
unsupported until evidence establishes it.

For an `open-ended` course, the model legitimately chooses structure, examples, analogies, and
interpretive emphasis within the brief. Preserve coherent authorship. Correct only:

- demonstrable factual or source error;
- copyright or attribution error;
- internal contradiction;
- clear pedagogical failure;
- approved-brief violation;
- material safety problem.

For a hybrid, mark which pages or claims use each authority boundary. An original film-analysis
arc may be valid while release facts, credits, quotations, and scene details remain externally
verifiable.

Before editing, record the objective category and evidence. “I prefer another example” is not a
correction reason.

## Design and review the Outline

Every page should:

- perform one teaching job;
- build on the previous page or create a deliberate contrast;
- contribute a distinct concept, example, practice, counterargument, or synthesis;
- contain enough factual support for its title and Key points;
- offer a meaningful visual job.

Review the full Outline, including every generated title. Hunt for:

- repeated claims in different words;
- a sequence that requires unexplained prerequisites;
- decorative pages with no learning function;
- a conclusion that introduces new core content;
- unsupported specificity or false certainty;
- plot summary, feature catalogues, or trivia replacing explanation;
- a page title that promises more than its Key points deliver.

Keep slide IDs stable. Do not add, delete, or reorder pages. Batch the smallest sufficient title and
`key_points` corrections, then fetch a fresh revision.

## Align Title, Key points, Page text, and Narration

Treat the four fields as an aligned contract:

### Title

Name the page's teaching job. Prefer a claim, question, mechanism, decision, or contrast over a
generic section label.

### Key points

Define what the page must teach. Use distinct, supportable claims. Key points are not a pile of
keywords and should not duplicate each other.

### Page text

Define what the learner sees and what primarily controls the generated slide image. Keep it concise,
hierarchical, and layout-ready. State diagram labels, comparison dimensions, table headings, and
critical caveats explicitly. Avoid transcript paragraphs.

### Narration `script`

Explain the page: context, causal links, transitions, nuance, evidence limits, and examples. Do not
merely read visible text. Keep the spoken claim set aligned with the page and source boundary.

### Change-impact matrix

| Changed field | Recheck |
|---|---|
| Title | Key points, Page text, Narration, visual job |
| Key points | Title, Page text, Narration, learner-outcome alignment |
| Page text | Key points, Narration, generated image |
| Narration | Key points, Page text, factual/source alignment |

When one conceptual correction affects several fields, update them in one atomic revision-checked
batch. After every accepted batch, fetch a fresh snapshot before the next mutation.

## Design useful visuals

Specify the information job, not only a style adjective:

- process -> numbered flow, state diagram, or causal chain;
- mechanism -> labeled schematic or cross-section;
- comparison -> consistent columns with meaningful dimensions;
- chronology -> scaled or explicitly non-scaled timeline;
- hierarchy -> nested structure or dependency tree;
- evidence -> source-grounded annotated artifact or claim/evidence table;
- interpretation -> juxtaposed details, motifs, or competing readings;
- practice -> scenario, decision point, and feedback path.

Treat visual semantics as claims. A green check implies success; a rising chart implies growth; a
padlock implies security; a polished dashboard implies an observed interface or dataset. Ban these
when evidence does not support them. Avoid invented percentages, counts, scores, durations,
customers, logos, maps, quotations, and pseudo-screenshots.

Use Reference images for subject, palette, composition, or visual grammar. Use Pin only when the
exact supplied image should remain the hero visual. A Pin provider contract is not proof of
pixel-perfect preservation.

## Define publish quality

Before finishing, require:

- full Outline and Page text/Narration review;
- every retained strict source complete and mapped;
- no unresolved factual, source, safety, or internal-consistency finding;
- all slide images canonically complete;
- visual review recorded honestly as `completed`, `partial`, or `not_performed`;
- one exact language-compatible presenter/Voice pair;
- requested layout persisted;
- successful first publish when authorized;
- link visibility only when requested/resolved;
- `playable=true` before reporting public or embed URLs;
- private delivery gives the login-required `editor_url` and never calls it a share link;
- Topics state described as a pending/reviewed submission, never as automatic distribution.
