# Decision Tree: Should You Build This Architecture?

Run the user's project through this tree *before* recommending the four-layer architecture. It excludes the architecture for many common project shapes, and saying so directly is more useful than over-fitting advice.

---

## Question 1: How many OS targets?

- **Just one (macOS only, or Windows only):**
  → **Don't use this architecture.** Build native (Swift/AppKit, or C#/WinUI/WPF). The cross-platform tax is not worth it. The whole point of this stack is to share a UI codebase across OSes; with one OS, you have nothing to share.

- **Two (macOS + Windows):**
  → Proceed.

- **Three (+ Linux):**
  → Proceed, but warn: this skill is grounded in macOS+Windows evidence. Linux + WebKitGTK works but has its own quirks not documented here. WebView2 doesn't exist on Linux; you'll likely use WebKitGTK or fall back to bundling. Budget for it.

- **Mobile too (iOS / Android):**
  → Proceed for desktop, *and* extract the Rust core to share with mobile (this is exactly the Layer-4-sharing benefit). Don't try to share the React UI with mobile via React Native; that's a different stack with different trade-offs.

---

## Question 2: Is "native feel" actually a hard requirement?

- **Yes, the app must be indistinguishable from native** (e.g., a launcher, a system utility, a productivity tool the user lives in all day):
  → Proceed.

- **"It should be nice but Electron is fine":**
  → **Don't use this architecture.** Use Electron. The polish budget here is 5–10× higher than Electron, and you only earn that back if native-feel is a competitive differentiator. If "nice" is sufficient, the cheapest path is Electron + a good designer.

- **No, it's an internal tool, no end-user polish needed:**
  → **Don't use this architecture.** Web app in a browser tab. Or Electron. Or a Mac app for the one OS your team uses.

---

## Question 3: Do you have a plugin/extension ecosystem?

- **Yes, third parties will build extensions:**
  → JS/TS plugins are the only practical choice (1000× more authors than native plugins). You need Layer 3 (Node backend). Proceed.

- **No, but the app has very rich business logic / network code:**
  → Layer 3 (Node) is still likely correct, because the alternative is duplicating business logic in Swift and C#. Proceed.

- **No, and the app is mostly UI + a small amount of native work:**
  → Consider skipping Layer 3. A native shell + WebView + small Rust core may be enough. Lighter, simpler.

---

## Question 4: How tight is your launch budget?

- **Cold start must be < 100 ms:**
  → **Don't use this architecture.** The WebView + Node boot floor is ~150–300 ms even with prewarming. Build native.

- **Cold start < 500 ms acceptable, warm start < 50 ms required:**
  → Proceed. Prewarm a hidden launcher window at app start. Warm activation is essentially free.

- **Cold start tolerance is generous (< 2s):**
  → Proceed comfortably.

---

## Question 5: What's your memory budget?

- **Under 150 MB resident:**
  → **Don't use this architecture.** The floor is ~150 MB on Windows for an empty WebView + Node. Build native.

- **300–800 MB acceptable:**
  → Proceed.

- **1 GB+ fine (e.g., a heavy AI app):**
  → Proceed, but consider memory hygiene from day one — see `references/05-memory-truths.md`. Going over 1 GB sustained will cost you reviews from users who don't understand memory accounting.

---

## Question 6: How experienced is your team?

- **Strong in one of Swift OR C#, plus React/TS:**
  → Proceed. You'll need to hire/learn the other native side, but the centroid of work is in TS where the team is fluent. This is a near-ideal fit.

- **Strong in React/TS, no native experience:**
  → Proceed with caution. The two native shells (Layers 1 + 1 again) are real work. Budget 2–3 months per shell for an experienced TS engineer to get competent. Or hire one native specialist per OS.

- **Strong in native (Swift or C#), no React experience:**
  → Proceed with caution. React/TS is easier to ramp on than the reverse, but design-system maturity in React takes longer than people expect. Budget 3 months for the UI baseline before shipping.

- **Two-person team, no Rust experience:**
  → Skip Layer 4 initially. Start with shell + WebView + Node. Add Rust only when a specific need arises (file indexer, crypto, etc.). UniFFI is great but ramping on Rust + UniFFI + cross-toolchain builds *while shipping* is a lot.

---

## Question 7: How long is the runway?

- **Short (need to ship in < 3 months):**
  → **Don't use this architecture.** Use Electron or Tauri. You can rewrite to native-feel later if the product takes off. (Raycast itself started as a pure Mac native app — they rewrote *after* they had product-market fit.)

- **Medium (6–12 months):**
  → Proceed if you have native experience on the team. Skip Layer 4 to start.

- **Long (12+ months to v1):**
  → Proceed comfortably. All four layers.

---

## Decision matrix

After all seven questions, score yourself:

| Score | Recommendation |
|---|---|
| All "Proceed" | Four-layer architecture. Read `references/02-architecture.md`. |
| One or two "Skip Layer X" | Three-layer architecture (omit the skipped layer). Read `references/02-architecture.md` and note the per-layer rationale to confirm what you're losing. |
| Any "Don't use this architecture" | Use the alternative named in that question (native / Electron / different stack). This skill doesn't apply. |
| "Proceed with caution" anywhere | Proceed but front-load risk: prototype the riskiest layer first (e.g., the native shell + WebView wiring), not the easiest. |

---

## Common false positives (apps that *seem* like a fit but aren't)

- **A "fast" web app** — i.e., a SaaS dashboard the team wants to "make feel native." Almost always: just ship it as a web app. Adding a native shell for "feel" rarely pays back the engineering cost.
- **A small utility** — e.g., a clipboard manager. Probably wants pure native; the cross-platform value isn't there at this size.
- **A game or graphics-heavy app** — use a game engine or native graphics framework, not a WebView.
- **A document editor** — depends. Notion/Obsidian-class? Maybe. Microsoft Word-class? Native.
- **A media player** — native, because media frameworks (AVFoundation, Media Foundation) are platform-specific anyway.

---

## When this architecture is *clearly* right

- A productivity launcher (Raycast, Alfred-style).
- A note-taking app with rich extensions (Obsidian-class).
- A team communication app with deep OS integration (Slack-class, *if* willing to invest more than Slack did).
- A developer tool that needs to embed editors, terminals, and rich panels (Linear desktop, Warp-ish).
- An AI app where the UI needs to render rich markdown/code and the backend needs to manage long-lived AI sessions across windows.

If the user's project resembles one of these and they passed Q1–Q7, recommend with confidence.
