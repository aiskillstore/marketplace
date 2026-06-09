---
name: frontend-guardrails
description: "Professional frontend standards for building, scaffolding, extending, or reviewing any UI or frontend project — new or existing — even when standards aren't explicitly asked for. Keeps generated code consistent, reusable, secure, and production-quality. Framework-agnostic: React, Vue, Angular, Svelte, plain JS."
---

# Frontend Guardrails

Without explicit standards, frontend code drifts: the same logic in three places (so one bug needs three fixes), inconsistent colors and fonts, backend concerns leaking into the UI, secrets and user data ending up in the browser. This skill is the standing instruction set that prevents that, so professional output is the *default* and requires no extra prompting.

**Compose, don't reinvent.** This skill is opinionated policy, not a re-implementation of existing tools. Where a mature linter, formatter, auditor, MCP, or companion skill already enforces one of these standards, prefer wiring it in over duplicating its work — see `references/ecosystem.md` for the recommended ecosystem and how each principle maps to it.

## How to use this skill

1. **Detect the stack first.** Identify the framework, styling approach, and state library from `package.json`, config files, and existing components. Never impose a stack the project does not use.
2. **Read the matching framework reference** for syntax-level guidance:
   - React / Next.js → `references/react.md`
   - Vue / Nuxt → `references/vue.md`
   - Angular → `references/angular.md`
   - Svelte / SvelteKit → `references/svelte.md`
   - Anything else (plain JS, SolidJS, etc.) → apply the principles below; the framework files show how the same principles map to syntax.
3. **Apply the universal principles** (below) to every task.
4. **Read the topic reference when the task touches that area** — these hold the deep detail:
   - Security-sensitive work (auth, user data, env vars, tokens) → `references/security.md`
   - Notifications, toasts, or user feedback → `references/notifications.md`
   - Accessibility → `references/accessibility.md`
5. **Run the self-audit** (final section) before declaring any task done.

---

## Scale rigor to the project (read first)

Match the depth of these standards to the project's size and maturity. Imposing enterprise rigor on a small or beginner project is itself a violation of principle 16 — over-engineering.

- **Always apply the fundamentals, at any size:** reusability/DRY, consistent design tokens, responsiveness, the security basics, professional polish, not shipping broken code, and not over-engineering.
- **Don't impose heavyweight infrastructure on projects that don't use it.** Do not introduce CI pipelines, test suites, TypeScript, build tooling, design-system infrastructure, or supply-chain scanning into a project that doesn't already have them unless the user asks or the project clearly warrants it. Detect what exists, match it, and grow rigor only as the project grows.
- **For beginners and non-developers, prefer sensible defaults over interrogation.** When a technical choice arises (state approach, folder structure, library), pick a reasonable default and explain it in one line rather than quizzing someone on jargon they may not know. Ask only when a choice genuinely cannot be made for them.
- **Keep ecosystem recommendations opt-in and needs-gated.** Offer tools (CI, hooks, CodeRabbit, scanners, Context7) when they actually fit the project — never as a checklist the user must satisfy or feel they've failed.

---

## Precedence — these are baselines, not mandates

The user's explicit instructions and the project's existing conventions always win over this skill's defaults. These principles are a portable baseline to fall back on, not commandments to impose.

- When a principle conflicts with an established project choice or a clear user instruction, follow the project/user — and if the trade-off is genuinely risky, flag it in one line rather than silently overriding either direction.
- Engineering is trade-offs. A deliberate, reasoned exception — accepted duplication, a test skipped on a throwaway spike, `any` at an untyped boundary — is not a violation. Don't "correct" intentional decisions.
- This skill governs the *AI's* defaults so output stays disciplined and consistent across sessions and teammates; it is not here to override an experienced developer's judgment.

## Hard rules vs sensible defaults

Not everything below carries equal weight. Distinguish the two:

- **Non-negotiable (don't bend without explicit, informed sign-off):** the security fundamentals — no secrets in client code, the backend enforces authorization, no unsanitized HTML, least data exposure — and not shipping broken code (it builds and typechecks locally with no errors).
- **Sensible defaults (defer to the project when it differs):** everything stylistic or architectural — toast placement, font count, when design tokens are worth it, SSR vs SSG/ISR, `any` usage, state-management and folder choices. Apply these when the project has no opinion; yield when it does.

This is a deliberately tight baseline, not an exhaustive checklist — it omits topics like i18n, error monitoring, and visual-regression testing on purpose, to stay lean and composable. Add them per project when needed.

---

## Surface the trade-off, then let the user decide

When following the user's request would conflict with a fundamental or steer toward a likely downstream problem, don't silently comply and don't silently override. Make the trade-off visible, then defer to their choice:

1. **Name the risk concretely** — what specifically could go wrong, and how it could grow into a real problem later. Be concrete, not vague: e.g. "storing the auth token in `localStorage` means any XSS bug anywhere in the app becomes full account takeover," or "this duplicated logic in three files means a future fix has to be made in all three — easy to miss one."
2. **State the cleaner approach in a sentence** — what you'd do instead and why.
3. **Ask whether to apply it or continue as requested — and honor the answer.** The user always decides; your job is to surface the choice before it gets baked in, not to insist.

Calibrate so this helps rather than nags:
- Only interrupt for genuine fundamentals or real downstream risks (security, data exposure, code that won't build, an architectural choice that's costly to unwind later). For stylistic or architectural defaults the project hasn't decided, just pick a sensible option and mention it in one line — don't turn every small choice into a question.
- After completing work, briefly note which standards shaped the result (one line, skipped for trivial tasks) — so the user can see what was applied without reading a lecture.
- If the user has already chosen to proceed their way, respect it and move on; don't re-litigate the same point.

---

## Universal principles

**1. Reusability / DRY — "one fix, not five."** If you would write the same markup, logic, or value twice, extract it once (a component, a hook/function, a token). Before building new UI, search for an existing component to reuse or extend. Duplication means fixing the same bug in many places.

**2. Component architecture & separation of concerns.** Build small, single-responsibility components that compose. Keep presentation, logic, and data access in separate layers — data fetching belongs in a clear layer, not inside presentational components. Name files consistently with one convention.

**3. Consistency through design tokens.** Never hardcode raw colors, font sizes, spacing, or radii. Reference named tokens (CSS variables, a theme object, or config) so every value has one source of truth. Inconsistent values are the hallmark of unpolished work.

**4. Responsiveness.** Design mobile-first against the project's defined breakpoints; never assume a single screen size. Prefer fluid units and flex/grid over fixed pixel widths. Verify nothing overflows, overlaps, or becomes unreadable at narrow, medium, and wide widths.

**5. Professional polish.** Every page needs a meaningful `<title>`, the favicon/logo in the tab, and viewport + description meta (Open Graph for shareable pages). Always handle loading and empty states — never show a blank or broken screen. (Accessibility basics are covered in principle 11.)

**6. State & navigation discipline.** Keep state at the right level — local for local concerns, a shared store only for genuinely shared state; avoid deep prop-drilling and avoid dumping everything into global state. Derive values instead of storing duplicates that fall out of sync. Centralize routing in one consistent setup.

**7. Frontend/backend boundary.** This is a frontend project: no direct DB access, no server-side business rules, no secret-bearing operations. Talk to the backend **only through a defined API layer**; components call that layer, never raw network logic scattered around.

**8. Security — assume everything in the browser is public.** No secrets in frontend code; the frontend reflects authorization but the backend enforces it; fetch and render only the data you display; never inject unsanitized HTML; prefer httpOnly cookies for tokens; always HTTPS. **Full detail and framework specifics: `references/security.md` — read it for any auth, user-data, or env-var work.**

**9. Dependencies — current and supported, not bleeding edge.** Install the latest *stable*, actively-maintained version (LTS where the ecosystem offers it); avoid pre-release tags (`beta`/`rc`/`canary`/`alpha`/`0.x`) and avoid abandoned or outdated packages that no longer get security patches. Before adding a dependency, vet it (reputation, maintenance, adoption) and scan for known vulnerabilities (`npm audit` or a supply-chain scanner like Socket/Snyk); don't add packages casually. Commit a lockfile. Bleeding-edge breaks; abandoned ships vulnerabilities.

**10. Performance.** Code-split and lazy-load; optimize images (modern formats, responsive sizes, lazy below the fold); avoid needless re-renders and re-fetches; paginate or virtualize long lists; watch bundle size. Speed directly affects bounce rate, conversions, and search ranking (Core Web Vitals).

**11. Accessibility.** Use semantic HTML first and reach for ARIA only to fill gaps; make everything keyboard-operable with visible focus; keep sufficient contrast and never convey meaning by color alone; label fields and associate errors with their inputs. **Full detail: `references/accessibility.md`.**

**12. Error handling, resilience & feedback.** Handle the unhappy paths (failed, empty, slow, offline) with clear messages and a retry where sensible; use error boundaries so one broken component doesn't crash the app; validate forms inline next to the relevant field. For notifications, match the message to the right vehicle (inline vs toast vs banner) and design toasts into the system. **Full detail: `references/notifications.md`.**

**13. Type safety.** In TypeScript projects, type props, function signatures, and especially API responses; treat external data as untyped until validated; avoid `any` (prefer precise types or `unknown` with narrowing). Types catch bugs before runtime and document intent.

**14. SEO & discoverability.** Per-route titles and meta descriptions, semantic headings, structured data (schema.org) for rich content like listings, and crawlable content via server-side rendering or pre-rendering; provide a sitemap and clean URLs. For content and listing sites, organic discovery is often the primary growth channel.

**15. Documentation & project context — keep it current.** Maintain a human-facing **README** and, for Claude Code projects, a **CLAUDE.md** briefing (stack, build/test/lint commands, architecture, conventions). Update both as part of finishing any meaningful change — new feature, dependency, structural change, or convention — not as an afterthought, and commit them. Stale docs mislead both new contributors and the AI.

**16. Behavioral discipline — the AI-specific failure modes.** Check assumptions before charging ahead; if requirements are ambiguous, ask rather than guess. Don't over-engineer — build what was asked and abstract only on genuine repetition (the rule of three), not speculatively. Touch only the code relevant to the task; leave unrelated code alone. Use real, current APIs and packages — don't invent methods, props, or libraries. **Before declaring done, verify the code actually works — it builds and typechecks locally with no errors — and remove debug artifacts (stray `console.log`s, stubs, mock data, dead/commented-out code, TODOs).** Don't hand over code that won't compile. Several of these behaviors are also encoded by mature standalone skills (see `references/ecosystem.md`). Deployment, CI/CD, and server/database concerns are intentionally out of scope — this skill stays client-side.

---

## Self-audit checklist (run before finishing any task)

Verify each item and fix anything that fails before reporting the task complete:

- [ ] No duplicated markup/logic/values — repeated things were extracted.
- [ ] New UI reuses or extends existing components where possible.
- [ ] No hardcoded colors, fonts, or spacing — all reference tokens.
- [ ] Layout works mobile, tablet, and desktop; nothing overflows or overlaps.
- [ ] Page has a meaningful title, favicon, and viewport meta tag.
- [ ] Loading and empty states are handled.
- [ ] State lives at the appropriate level; no redundant/duplicated state.
- [ ] No backend logic, DB access, or secrets in frontend code; all calls go through the API layer.
- [ ] No secrets/keys shipped to the browser; only necessary data fetched/rendered; no unsanitized HTML; auth enforced by the backend. (See references/security.md.)
- [ ] Dependencies are stable, supported (LTS where available), not pre-release or abandoned; new deps vetted and vulnerability-scanned (`npm audit`/Socket/Snyk); a lockfile is committed.
- [ ] Code split/lazy-loaded where heavy; images optimized; long lists paginated or virtualized.
- [ ] Semantic HTML; keyboard-operable; sufficient contrast; meaning never by color alone. (See references/accessibility.md.)
- [ ] Failure paths handled; error boundaries in place; form errors inline. Notifications use the right vehicle and match the design system. (See references/notifications.md.)
- [ ] TypeScript: props and API responses typed; no `any`; external data validated.
- [ ] SEO: per-route titles/meta, structured data where relevant, crawlable content.
- [ ] README and CLAUDE.md reflect the current state after meaningful changes.
- [ ] Scope kept to the task; unrelated code untouched; no speculative over-engineering; real (not invented) APIs/packages used.
- [ ] Verified the code builds and typechecks locally with no errors (don't ship code that won't compile); no debug artifacts, stubs, mock data, or dead code left behind.
- [ ] Checked for an existing component/utility/tool/skill before building something new. (See references/ecosystem.md.)

Briefly note to the user which standards were applied — a short mention, not a lecture, and skip it entirely for trivial tasks.
