# 06 — Native Conventions: The Audit

T3 (*adopt the platform; don't compete with it*) and T4 (*performance is a property of perception*) converge here. This file is a list of behaviors that, when wrong, telegraph "web app." Each is independent. Each is cheap to fix once you know about it. None changes a benchmark; all change what the user feels.

The goal: a skeptical user should examine the app for 30 seconds and conclude "this is a regular Mac/Windows app." Every item below is something that skeptic notices unconsciously.

---

## Input & cursor

- [ ] **No `cursor: pointer` on hoverable rows.** Native list rows don't change the cursor.
- [ ] **No text selection on chrome.** Labels, button text, headings should not be selectable. Only content areas (editable text, message bodies) allow selection.
- [ ] **Caret-style text cursor on inputs only.** Don't show I-beam on non-editable areas.
- [ ] **Native context menu, not WebKit's.** Override `willOpenMenu` (Mac) or intercept `CoreWebView2.ContextMenuRequested` (Win). Either remove the menu or populate with native items.
- [ ] **No link previews on force-touch / long-press.** Disable `-webkit-touch-callout`.
- [ ] **No spellcheck red underlines on chrome.** Only on user-entered text in editable fields.
- [ ] **No dictionary lookup popup on force-tap.** Override or suppress.
- [ ] **IME composition window appears at the caret, not above the WebView.** Test with Pinyin / Japanese kana.

## Windowing & focus

- [ ] **Windows behave like native windows.** ⌘W closes (Mac), Alt-F4 closes (Win). ⌘M minimizes (Mac), Win+Down minimizes (Win).
- [ ] **Window restoration on app re-focus.** Clicking the Dock/Taskbar icon re-shows the last-active window, doesn't open a new one (unless your app's identity demands a new window per click).
- [ ] **Settings open in a native window**, not a modal inside the main window. Standard ⌘, opens it on Mac.
- [ ] **No modal overlays with backdrop blur for "dialogs"**. Use native `NSAlert` / `MessageBox` for confirmations.
- [ ] **No web-style "toast" notifications**. Use the OS notification center.
- [ ] **The window has a real title bar (or a real chromeless region)**, not a hand-painted div pretending to be one. Drag must work on the full title bar, not just a centered handle.
- [ ] **Traffic lights / window controls match platform.** Mac: red/yellow/green on the left. Windows: minimize/maximize/close on the right.
- [ ] **Maximizing on Mac uses Green = zoom (window-sized), not fullscreen unless user holds Option.** Most web-wrappers get this wrong.
- [ ] **The window remembers its size and position across launches**, per-screen if multi-monitor.

## Materials & visual

- [ ] **Window background uses platform material**, not a static color.
  - Mac: `NSVisualEffectView` with appropriate material, or `NSGlassEffectView` (Liquid Glass) on macOS 26+.
  - Win: `DwmSetWindowAttribute(DWMWA_SYSTEMBACKDROP_TYPE, DWMSBT_MAINWINDOW)` for mica, or `DWMSBT_TRANSIENTWINDOW` for acrylic.
- [ ] **Dark mode follows system preference**, with no per-frame flicker on toggle.
- [ ] **Accent color follows system accent color** (Mac: `NSColor.controlAccentColor`; Win: `UISettings.GetColorValue(UIColorType.Accent)`). Don't hardcode brand blue.
- [ ] **Font is the system font**, not a web font. Mac: `-apple-system, BlinkMacSystemFont`. Win: `'Segoe UI Variable', 'Segoe UI'`.
- [ ] **No `box-shadow` for window shadows**. The OS draws those.
- [ ] **No `border-radius` for window rounding**. The OS does it (and matches the rest of the system's window radius — 10 px on macOS Tahoe).

## Scrolling

- [ ] **Overlay scrollbars on Mac** that fade out, match system. WebKit does this by default if you let it.
- [ ] **No "scroll to top" rubber-band override**. Let the platform handle.
- [ ] **No smooth-scroll JS polyfills.** `behavior: 'auto'`, not `'smooth'`.
- [ ] **Scroll position doesn't reset on navigation within the same window.** Use proper scroll restoration in your router.

## Motion

- [ ] **No page transitions / route fades** by default. Native apps cut between views.
- [ ] **Animations honor `prefers-reduced-motion`.** Disable unnecessary motion when set.
- [ ] **Window resize is animated by the OS, not by JS layout animations.** Push the resize to the host shell.
- [ ] **No "loading skeletons" for fast operations.** Native apps show spinners or nothing for sub-200ms operations. Skeletons are a web idiom.
- [ ] **No spring/bounce animations on simple state changes.** Native uses tightly-controlled ease curves. Reserve spring for grab-and-drag.

## Keyboard

- [ ] **Full keyboard navigation everywhere.** Every actionable element reachable by Tab/arrow keys.
- [ ] **Focus rings match platform.** Mac: blue glow ring around focused control. Win: dotted outline or blue ring per system settings.
- [ ] **Native menu items have native shortcuts.** ⌘F opens find, not Ctrl-F on Mac. Ctrl-F on Windows.
- [ ] **Escape does something meaningful.** Close the popover, cancel the action, dismiss the window. Never nothing.
- [ ] **Tab order is logical**, not DOM order if those differ.
- [ ] **Type-ahead in lists.** Pressing letters in a list jumps to matching items. Standard native list behavior.

## File / drag-and-drop

- [ ] **Native drag-and-drop with file URLs**, not the browser's web-style drag API. Use `NSPasteboard` (Mac) / `IDataObject` (Win) under the hood.
- [ ] **Dropping files onto the dock icon opens them.** Handle `application:openFiles:`.
- [ ] **Copy operations write to all pasteboard types**, including plain text + RTF + HTML for rich content.
- [ ] **Saving uses native save panels**, not browser-style download bars.

## System integration

- [ ] **The app has a real `Info.plist` / app manifest** with proper bundle identifier, version, icon, document types.
- [ ] **URL schemes registered properly.** `appname://` works system-wide.
- [ ] **File associations work.** Double-clicking an `.appdoc` file opens your app.
- [ ] **Single-instance behavior on Windows.** Second launch focuses the existing instance, doesn't spawn a new one. (Mac handles this automatically via LSMultipleInstancesProhibited; Windows requires explicit code.)
- [ ] **Auto-update is a real process**, not a "please download a new version" link. Sparkle on Mac, MSIX or custom on Windows.
- [ ] **Crash reports go to a real crash reporter** (Sentry, Bugsnag, etc.) — verified in Raycast Beta: ships `Sentry.framework` and a `NativeSentryClient` UniFFI interface for breadcrumbs and user IDs.

## Accessibility

- [ ] **VoiceOver / Narrator can read everything.** WebView content with proper ARIA roles. Native controls auto-handle this.
- [ ] **Focus is announced** when it moves.
- [ ] **Color contrast meets WCAG AA at minimum.**
- [ ] **No fixed-pixel sizes that break when system font size is bumped.**
- [ ] **All actions reachable without a mouse.**

---

## How to use this list

For a new app: print this file, walk through with a designer, mark every item. Expect to fail 5–10 on first pass.

For a code review: when reviewing a PR that touches UI, grep for `cursor: pointer`, `user-select: text` outside of editable areas, `behavior: 'smooth'`, custom modal overlays, hardcoded `#0066cc`-type accent colors.

For a bug report ("the app feels weird"): walk the user through the list. Often a single item is the problem; the user can't articulate it but the unconscious "this is wrong" lands when they see it named.

---

## Edge cases worth special note

### Hover states (the precise rule)

The article phrases this as "no hover highlights on most controls — matching macOS button/list behavior." Unpacked:

- **List rows / sidebar items / toolbar items:** native *does* show a subtle hover background. Keep this. The visual hover is fine; only the `cursor: pointer` is the tell.
- **Plain push buttons (`NSButton.bezelStyle = .rounded`):** native does *not* show a hover effect. Don't add a background-change on hover to a normal button. Web apps reflexively do; macOS does not.
- **Borderless / "icon" buttons in toolbars:** native shows a subtle background tint on hover. Match it.
- **Hyperlinks inside content:** native AppKit shows underline on hover for `NSAttributedString` links. Match it for content links; do not add it to navigation chrome.

The unifying principle: ask "what does the equivalent native control do here?" and do exactly that. The error is not "too much hover" or "too little" — it is *uniform* hover treatment, which is a web idiom. Native varies by control kind.

### Buttons

Native buttons have a clear *pressed* state distinct from hover. Many web styles only style hover. Add a `:active` style that visually depresses the button.

### Loading

For operations < 200 ms, show nothing. Just commit the change when it arrives. For 200ms–2s, show a spinner. Beyond 2s, show progress. Never use skeleton placeholders for anything under 500ms — they make fast operations feel slow.

### Empty states

Native apps tend to have terse empty states: an icon + one line. Web apps over-explain. Lean terse.

### Onboarding

Native apps don't have multi-step onboarding tours by default. The interface should be self-explanatory. If you need to teach the user, use tooltips on first hover and never again.
