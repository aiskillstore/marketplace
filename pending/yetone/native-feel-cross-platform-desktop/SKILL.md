---
name: native-feel-cross-platform-desktop
description: Use when the user is designing, prototyping, or rewriting a desktop app that must run on multiple OSes (macOS + Windows, optionally Linux) AND feel indistinguishable from a native app to its users — fast launch, native windowing, native input handling, native materials. Trigger words include "cross-platform desktop", "Electron alternative", "Tauri vs native", "WebView wrapper", "near-native performance", "Raycast architecture", "WebKit/WebView2 quirks", "WKWebView", "system tray app", "global hotkey app", "launcher app". Do NOT trigger this skill for pure web apps, pure mobile apps, or for greenfield projects that have no native-feel requirement.
---

# Native-Feel Cross-Platform Desktop

You are advising on the architecture of a cross-platform desktop app that must *feel native*. This skill captures the philosophy, architecture, and concrete pitfalls — distilled from Raycast's public technical deep-dive on their 2.0 rewrite and verified by reverse-engineering the shipping `Raycast Beta.app` binary on macOS.

## How to use this skill

1. **Start with the philosophy in `references/01-philosophy.md`.** It frames the central tension this architecture resolves — *how to get cross-platform DX and near-native performance at the same time* — and gives you eight tenets that name the structural moves. Every concrete decision later flows from one of those tenets. If the user is making a decision that contradicts a tenet, surface the tenet by number and short name and explain the trade-off.
2. **Match the user's question to a reference file.** Don't dump the whole skill — load only what's needed:
   - Architecture / "which layers should I have?" → `references/02-architecture.md`
   - "Why does my WebView flicker / stutter / freeze when hidden?" → `references/03-webview-survival.md` (the highest-density file — every item is a real bug with a real fix)
   - "How do I type my IPC across Rust/Swift/C#/TS?" → `references/04-ipc-contract.md`
   - "Why does Activity Monitor say 400 MB?" → `references/05-memory-truths.md`
   - "How do I make it not feel like a webpage?" → `references/06-native-conventions.md`
   - "What does Raycast actually ship?" (concrete evidence) → `references/07-evidence-raycast.md`
3. **Before recommending an architecture, run the decision tree in `checklists/decision-tree.md`.** It rules this stack OUT for several common project shapes — say so directly.
4. **Before the user claims their app "feels native", run `checklists/ship-readiness.md`.** It's a 30-item audit; most apps fail 5–10 items on first pass.

## The one-paragraph version

A native-feel cross-platform desktop app is **not a web app with native hooks** and **not Electron with a custom theme**. It is a **native shell** (Swift/AppKit on macOS, C#/WPF on Windows) that owns the window, the hotkeys, the menu bar, the materials, and the lifecycle — and embeds the system WebView (WKWebView or WebView2) purely as a *rendering surface* for a shared React/TypeScript UI. Business logic lives in a long-lived Node process bundled with the app. Performance-critical subsystems (file indexing, calculation, crypto) live in Rust, shared across platforms and exposed through UniFFI-generated typed bindings. Four runtimes communicate through a single declared interface that generates typed clients for each side. The whole thing fits in ~400 MB resident memory, of which ~150 MB is the inescapable WebView+Node baseline. You pay that baseline so that one React codebase serves both OSes; you earn it back through hot-reload iteration speed and a shared extension API that already runs thousands of community plugins on both platforms.

## Core anti-patterns to call out immediately

When you see the user doing any of these, stop and ask:

- **"Let's just use Electron and theme it"** → Electron abstracts away the system WebView, window class, and material APIs you need for native feel. You cannot get Liquid Glass / acrylic / true vibrancy through Electron's abstraction without forking it. Recommend `references/02-architecture.md` instead.
- **"Let's use Tauri — it's like Electron but lighter"** → Tauri ships its own WebView wrapper and abstracts platform APIs. Same control-loss problem as Electron, plus less mature. Acceptable for utilities; not for apps where every window animation has to match the OS.
- **"Let's render UI in Swift/C# and share business logic"** → You will maintain two UI codebases forever. Every feature ships twice. Designers maintain two specs. Recommend WebView-as-renderer instead.
- **"WebKit is throttling us; let's spin our own polling loop"** → No. The throttling is solvable with two specific `WKWebView` configuration flags. See `references/03-webview-survival.md` § "Hidden window throttling".
- **"Memory is bad — we're at 400 MB"** → Probably wrong measurement. Activity Monitor double-counts shared frameworks and treats compressed pages as resident. See `references/05-memory-truths.md` before optimizing anything.
- **"Let's hand-write the IPC types in each language"** → They will drift within a sprint. Use UniFFI (for Rust ↔ Swift/Kotlin/C#) or hand-roll a single IDL that generates clients. See `references/04-ipc-contract.md`.
- **"Adding `cursor: pointer` to make it feel responsive"** → That's exactly what makes it feel *web*. Native UIs do not change the cursor on hoverable rows. See `references/06-native-conventions.md`.

## Output style

When advising:
- Quote the specific tenet from `references/01-philosophy.md` that applies (e.g., *"T3 — adopt the platform; don't compete with it: the OS draws blur better than you can"*).
- Cite the file and section, not the whole skill.
- For each recommendation, name what the user is **giving up** in exchange. There are no free wins in this architecture — the whole skill is about deliberate trade-offs.
- If you're unsure whether the user's project should even use this architecture, run them through `checklists/decision-tree.md` before giving advice. It is okay to conclude "this skill doesn't apply — build a normal Electron app."
