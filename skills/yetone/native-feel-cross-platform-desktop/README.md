<div align="center">

# native-feel.skill

> *"Cross-platform development AND near-native performance — refuse the trade-off."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7c3aed)](https://github.com/yetone/native-feel-skill)

<br>

**An Agent Skill for designing cross-platform desktop apps that feel native** — distilled from Raycast's 2.0 technical deep-dive and grounded in reverse-engineering of the shipping `Raycast Beta.app` binary.

Two goals usually pull against each other: convenient cross-platform development, and near-native performance. This skill captures the structural choices — eight architectural tenets, a four-layer architecture, a WebKit/WebView2 survival guide, a 75-item ship audit — that let an app have both.

<br>

**Install** — paste this to your AI agent:

</div>

```
Install the native-feel skill for me:

1. Clone https://github.com/yetone/native-feel-skill into your
   user-level skills directory as `native-feel-cross-platform-desktop/`
   (whatever path your agent reads skills from on this machine — e.g.
   `~/.claude/skills/` for Claude Code).
2. Verify that SKILL.md plus the references/ and checklists/ subdirs
   are present.
3. Confirm the install path when done.
```

<div align="center">

[Use cases](#use-cases) · [What this is](#what-this-is) · [Philosophy](#philosophy) · [Layout](#layout) · [Sources](#sources)

</div>

---

## Use cases

Once installed, the skill activates automatically whenever the conversation touches cross-platform desktop architecture, WebView quirks, or making a UI feel native. Two common ways to use it:

### Case 1 — Refactor an existing app to feel more native

You have an Electron / Tauri / web-wrapped app, and a designer (or your own eye) tells you it feels web-y. You want to know where to start and how far you can take it without a full rewrite.

```
You    ❯ My Electron app feels web-y on macOS — the designer says it
         doesn't pass for a real Mac app. Where do I start?

Agent  ❯ Quickest path is the 75-item native-feel audit
         (checklists/ship-readiness.md). Most Electron apps fail
         the same 6–8 items:
           - cursor:pointer on rows (item 21)
           - web-style modal overlays instead of native sheets (19)
           - hardcoded brand accent instead of system accent (33)
           - page fade-transitions (40)
           - opaque window background instead of platform material (31)
           - WebKit context menu still firing (23)
         Each is a 5-to-30-minute fix; together they move you most
         of the way to "passes the 30-second skeptical user test."

         Bigger question first: how far do you need to go? If "good
         enough" means passing that 30-second test, Electron + this
         audit gets you 80% there without rewriting. If you want
         "indistinguishable from a Mac app" — Liquid Glass materials,
         native popovers, sub-200ms launch — Electron has a ceiling
         you'll hit. Want me to run the decision tree first?
```

### Case 2 — Build a cross-platform native-feel app from scratch

Greenfield project, must run on macOS + Windows, and the native feel is the *point* — a launcher, a productivity tool, an AI workspace your users live in all day.

```
You    ❯ Starting a new desktop app — macOS + Windows, native feel
         is the whole pitch. What architecture should I use?

Agent  ❯ Before architecture, the decision tree
         (checklists/decision-tree.md) rules this stack out for
         several common shapes — quick check first:
           - Cold-start budget?  (<100ms → build native instead)
           - Memory floor?       (<150MB → build native instead)
           - Extension ecosystem? (yes → need the Node layer)
           - Runway?             (<3mo → start on Electron)

         If you pass, the four-layer architecture is:

           ┌──────────────────────────────────────────────────┐
           │ Native shell      Swift/AppKit  +  C#/WPF        │
           │       ↕   one IPC schema, codegen for all sides  │
           │ System WebView    WKWebView    +  WebView2       │
           │   running React + TypeScript, shared 1:1         │
           │       ↕                                          │
           │ Node backend      single long-lived process      │
           │       ↕                                          │
           │ Rust core         UniFFI-bridged, sharable       │
           │                   with iOS and server            │
           └──────────────────────────────────────────────────┘

         The expensive-to-get-wrong decisions, in order:
           1. The IPC contract (one schema, codegen). Get this wrong
              and you rebuild it later under duress.
           2. WebView survival flags (occlusion off, alpha-prewarm,
              _doAfterNextPresentationUpdate, font prewarming).
           3. Memory hygiene (lazy-load extensions, tear down
              secondary windows aggressively).

         Want to start with the seam — where to draw the cross-
         platform line — or with the IPC contract, since that's the
         load-bearing piece?
```

### Other things the skill is good for

- **"Why is my WKWebView flickering when I hide and re-show it?"** → walks you through `references/03-webview-survival.md` (most likely A.1 throttling or A.2 startup flicker).
- **"How should typed IPC work across Rust, Swift, and TypeScript?"** → the UniFFI-based pattern in `references/04-ipc-contract.md`, with the exact `Coordinator`/`EventHandler` shape Raycast Beta ships.
- **"My app is at 450 MB resident, is that bad?"** → the six common Activity-Monitor mistakes and what to actually measure, in `references/05-memory-truths.md`.
- **"Is my designer's spec ‘native enough’?"** → the 70+ item conventions audit in `references/06-native-conventions.md`.

---

> *"We're not a web app with some native hooks sprinkled on top. We're a native app that uses web for its UI."* — Raycast

## What this is

A reference for architects, tech leads, and engineers who must build a desktop app that:

- runs on **macOS + Windows** (optionally Linux) from a single UI codebase,
- launches in under 500 ms and stays under 500 MB resident,
- is **indistinguishable from a native app** to its users (no `cursor: pointer` tell-tales, no white-flash on launch, no WebKit context menu, no smooth-scroll JS),
- supports a **plugin/extension ecosystem** in TypeScript,
- can share performance-critical code with iOS and a server backend.

This is the four-layer architecture: **native shell → system WebView (WKWebView/WebView2) → Node backend → Rust core**, wired together with a single typed IPC schema that generates clients for every runtime.

## What this is not

- Not for single-OS apps (just build native).
- Not for Electron-style "good enough" apps (the polish budget here is 5–10× higher).
- Not for apps with strict <150 MB or <100 ms cold-start budgets (the floor is real).
- Not for games, document editors, or media players.

Run [`checklists/decision-tree.md`](checklists/decision-tree.md) to find out if this architecture is even right for your project. It rules itself out for several common cases — saying so directly is more useful than over-fitting advice.

## Layout

```
native-feel-skill/
├── SKILL.md                                # entry point for the agent
├── references/
│   ├── 01-philosophy.md                    # 8 tenets that drive every decision
│   ├── 02-architecture.md                  # the four-layer architecture
│   ├── 03-webview-survival.md              # WebKit/WebView2 quirks + fixes (the goldmine)
│   ├── 04-ipc-contract.md                  # typed IPC across Rust/Swift/C#/TS
│   ├── 05-memory-truths.md                 # why Activity Monitor lies
│   ├── 06-native-conventions.md            # 70+ items the native-feel audit checks
│   └── 07-evidence-raycast.md              # what a reverse-eng. of Raycast Beta shows
└── checklists/
    ├── decision-tree.md                    # should you use this architecture?
    └── ship-readiness.md                   # 75-item launch audit
```

## Philosophy

The central tension this architecture resolves: **how can a desktop app deliver convenient cross-platform development AND near-native performance, when those goals usually pull against each other?** Eight tenets name the structural moves:

1. **Place the seam at the rendering surface** — share above the WebView, diverge below it; this is the only altitude where both DX and native feel survive.
2. **One schema, many languages** — pay the polyglot tax once at the declaration, never at the call site.
3. **Adopt the platform; don't compete with it** — the OS draws blur, scrolling, materials, and dark mode better than you can.
4. **Performance is a property of perception** — what the user feels, not what Activity Monitor reports.
5. **The short iteration loop is the product** — 200 ms hot reload vs 30 s native rebuild is a 150× compounding advantage.
6. **Cross boundaries intentionally** — IPC has a cost; design every crossing as async, batched, schema-typed.
7. **Identity is muscle memory** — the hotkey, the rank order, the verbs are the app; everything else is implementation.
8. **Separate baseline from margin** — the WebView+Node floor is rented; only your dirty pages are yours to optimize.

Read [`references/01-philosophy.md`](references/01-philosophy.md) first. Everything else is consequence.

## About Agent Skills

Agent Skills are the emerging standard for packaging domain knowledge that any compatible agent (Claude Code, the Claude Agent SDK, or other Agent-Skill-aware runtimes) can discover and load. Once installed via the prompt at the top of this README, the skill activates automatically when the agent's conversation touches cross-platform desktop architecture, WebView quirks, or Raycast-style apps — the trigger conditions are declared in `SKILL.md`'s frontmatter.

## Sources

- Raycast's public technical post: [A Technical Deep Dive into the New Raycast](https://www.raycast.com/blog/a-technical-deep-dive-into-the-new-raycast)
- Reverse engineering of `Raycast Beta.app` v0.60.0 (macOS 26+ build, Xcode 17, arm64) — see [`references/07-evidence-raycast.md`](references/07-evidence-raycast.md) for what was found and how.

## License

MIT — see [`LICENSE`](LICENSE).

## Credits

Authored as an Agent Skill. The architecture this skill describes is Raycast's; the philosophy is the author's synthesis; the evidence is from the shipping app.
