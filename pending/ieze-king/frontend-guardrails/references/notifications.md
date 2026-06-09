# Notifications & user feedback (detail)

Read this when building any notification, toast, alert, banner, or status message. The most common mistake is dumping every message into a generic bottom-of-screen toast. Two rules: **choose the right vehicle, and design it into the system.**

## Choose the right vehicle for the message

- **Field / validation errors → inline, next to the field.** A login failure or a bad form input belongs right beside the relevant control, not in a toast that vanishes before the user reads it.
- **Transient, non-blocking events → a toast.** "Saved", "Copied", "Listing published", a background task that finished or failed. Things the user does not need to act on.
- **Critical or blocking issues → a persistent banner or modal that does not auto-dismiss.** Session expired, payment failed, connection lost. The user must see and act on these.

Matching severity to the vehicle is what makes feedback feel intentional rather than noisy.

## When a toast is the right choice, design it properly

- **Use the design system.** Colors, typography, radius, spacing, and icons come from the design tokens — never raw library defaults that clash with the app.
- **Place it deliberately and consistently.** Top-center or top-right are conventional, visible positions. Avoid bottom-center: it is easy to miss and collides with mobile navigation and on-screen keyboards. Pick one position and use it everywhere.
- **Semantic variants.** success / error / warning / info, distinguished by both color *and* an icon — never color alone (see accessibility).
- **Accessible.** Announce to assistive tech with `aria-live` (`role="status"` for non-urgent, `role="alert"` for urgent). Never let a fleeting toast be the *only* place critical information appears.
- **Sensible timing.** Auto-dismiss success/info after a few seconds; keep errors dismissible or persistent so they are not missed. Queue or limit concurrent toasts instead of stacking many at once.
- **One system.** Route all notifications through a single shared notification component/service. Never scatter native `alert()` / `confirm()` dialogs through the app.

## Why this matters
Feedback is how users understand what just happened. Inconsistent, unstyled, or easily-missed messages make an app feel unreliable even when the underlying logic is correct.

## Quick checklist
- [ ] Message uses the right vehicle (inline / toast / banner-or-modal) for its severity.
- [ ] Toasts are styled from design tokens, not library defaults.
- [ ] Consistent, visible placement app-wide (not bottom-center).
- [ ] Variants use icon + color, not color alone.
- [ ] Announced via aria-live; critical info not toast-only.
- [ ] Timing fits severity; concurrent toasts queued/limited.
- [ ] All notifications go through one shared system; no stray native alerts.
