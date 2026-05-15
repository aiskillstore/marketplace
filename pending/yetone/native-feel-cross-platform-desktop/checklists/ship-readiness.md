# Ship-Readiness Audit

Before claiming the app "feels native," walk through this list. Most apps fail 5–10 items on first pass. Each failure costs cheap-to-fix engineering, but compounds.

Score: green ✓ if observably correct, red ✗ if not, gray ◯ if N/A.

---

## A. Cold launch (10 items)

1. ◯  App launches from hotkey to visible window in < 200 ms (warm) / < 600 ms (cold).
2. ◯  No white/black flash before content appears. (`_doAfterNextPresentationUpdate` on Mac, `DefaultBackgroundColor` + `NavigationCompleted` on Win.)
3. ◯  Window appears at the correct screen and position (last position remembered, multi-monitor aware).
4. ◯  Initial focus is in the most likely input control. User can type immediately.
5. ◯  No "loading…" placeholder visible to the user during normal launch.
6. ◯  Dock/Taskbar icon shows correct app icon, not a generic Electron-style icon.
7. ◯  Menu bar / system tray icon is monochrome (Mac convention) or follows system theme.
8. ◯  ⌘-Space / global hotkey works on first launch without re-registration.
9. ◯  App registers with Login Items (Mac) / Startup (Win) on user opt-in, not silently.
10. ◯  Quitting the app actually quits — no hidden zombie processes.

## B. Window & focus (10 items)

11. ◯  ⌘W (Mac) / Ctrl-W (Win) closes the window.
12. ◯  ⌘M (Mac) / Win-Down (Win) minimizes.
13. ◯  Green button (Mac) zooms to content size, doesn't fullscreen unless Option held.
14. ◯  Clicking outside the launcher window dismisses it (if that's the design).
15. ◯  Window remembers size and position across launches.
16. ◯  Multi-monitor: window opens on the active screen, not always screen 0.
17. ◯  Fullscreen mode (if applicable) uses native fullscreen, not a maximized window.
18. ◯  Settings opens in a separate native window (⌘, on Mac, Ctrl-, on Win).
19. ◯  No modal "dialogs" implemented as DOM overlays. Use NSAlert / MessageBox or native sheets.
20. ◯  When the app loses focus, the launcher hides (or follows the configured behavior — but predictably).

## C. Input & cursor (10 items)

21. ◯  No `cursor: pointer` on rows, buttons, or tabs.
22. ◯  Text selection disabled on labels, headings, button text.
23. ◯  Native context menu (or removed entirely), not WebKit's.
24. ◯  No link previews on force-touch / long-press.
25. ◯  No spellcheck red underlines on chrome.
26. ◯  IME composition works correctly (test with Pinyin specifically; Japanese kana; Korean Hangul).
27. ◯  Full keyboard navigation: every action reachable via Tab + Enter.
28. ◯  Focus rings visible and platform-styled.
29. ◯  Escape always does something meaningful — close popover, cancel action, dismiss.
30. ◯  Type-ahead in lists: typing letters jumps to matching items.

## D. Visual & material (10 items)

31. ◯  Window background uses platform material (NSVisualEffectView / Liquid Glass / mica / acrylic).
32. ◯  Dark mode follows system, switches without flicker.
33. ◯  Accent color matches system accent (not a hardcoded brand color).
34. ◯  System font in use; no web font for chrome.
35. ◯  No CSS `box-shadow` for window shadow (OS draws it).
36. ◯  No CSS `border-radius` for window corners (OS draws them, matching platform radius).
37. ◯  Translucency works correctly: blur visible through transparent regions.
38. ◯  No `cursor: pointer` (yes, again — most common offender).
39. ◯  Animations honor `prefers-reduced-motion`.
40. ◯  No page transitions / route fades.

## E. Scrolling (5 items)

41. ◯  Overlay scrollbars on Mac (fade out).
42. ◯  Thin scrollbars on Win 11; classic if user opted out.
43. ◯  No `behavior: 'smooth'` on programmatic scroll.
44. ◯  Scroll inertia feels native, not document-style.
45. ◯  Scroll position preserved across navigation within a window.

## F. Performance (10 items)

46. ◯  Resident memory under 500 MB at idle.
47. ◯  No noticeable hitch when expanding/collapsing the search results.
48. ◯  No frame drops when typing fast into a search field with live results.
49. ◯  Background CPU < 0.5% when window hidden (Mac) / window minimized (Win).
50. ◯  Battery impact rated "low" by Activity Monitor (Mac) after 1 hour of idle.
51. ◯  Hidden window doesn't get WebKit-throttled (test: scheduled UI updates fire promptly when window re-shown).
52. ◯  File indexer doesn't pin a core (off-loaded to Rust subprocess, niced appropriately).
53. ◯  Extension/plugin crash doesn't take down the app.
54. ◯  Network call timeouts surface as user-visible errors within 10 seconds, not 60.
55. ◯  Loading state for any operation > 200 ms; nothing for under.

## G. System integration (10 items)

56. ◯  URL scheme registered and works system-wide.
57. ◯  File associations work; double-clicking an associated file opens the app.
58. ◯  Drag-and-drop with real file URLs, accepted by Finder/Explorer correctly.
59. ◯  Copy to clipboard writes all expected pasteboard types (text, RTF, HTML for rich content).
60. ◯  Save dialogs are native (NSSavePanel / IFileSaveDialog).
61. ◯  Native notifications via NSUserNotification / Windows Toast.
62. ◯  Auto-update is real (Sparkle / MSIX / custom). User isn't prompted to "download a new version."
63. ◯  Crash reports go to a real crash reporter with symbolicated stack traces.
64. ◯  Single-instance on Windows (second launch focuses existing instance).
65. ◯  Bundle/manifest correct: identifier, version, icon, document types.

## H. Accessibility (5 items)

66. ◯  VoiceOver / Narrator can navigate the entire interface.
67. ◯  Focus is announced when it moves.
68. ◯  Color contrast meets WCAG AA.
69. ◯  Works with system font size bumped to large.
70. ◯  All actions reachable without a mouse.

## I. Cross-platform parity (5 items)

71. ◯  Mac and Windows ship the same feature set (no "this feature only on Mac").
72. ◯  Both shell binaries hit the same IPC schema version after an update.
73. ◯  Extensions written by third parties work identically on both OSes.
74. ◯  Visual differences between OSes match platform conventions, not arbitrary.
75. ◯  Bug fixes propagate to both OSes from a single codebase change in most cases.

---

## How to use this list

For a v1.0 launch: aim for 90% green. The 10% red should all be in section H (accessibility) or I (cross-platform parity) where some lag is acceptable. Reds in A–G are launch blockers.

For a code review: pick the 5–10 items most relevant to the PR's surface area and check them explicitly.

For a regression audit after a refactor: walk the whole list. Refactors tend to silently undo native-feel work.

---

## The single most diagnostic test

Hand the app to a designer who uses native Mac/Windows apps daily but has never seen yours. Don't tell them anything. Watch for the first time they say "wait, this feels weird." That moment is one of the items above. Find it, fix it, ship.
