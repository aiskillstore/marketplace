---
id: "accessibility-keyboard"
title: "Keyboard navigation and focus management"
category: "frontend"
summary: "Keep interactive interfaces usable with keyboard input and sensible focus restoration."
aliases: ["keyboard navigation","accessibility focus","modal focus","accessible dialog","tab order","klavye ile pencereyi kullanma","odak yönetimi","pencere kapanınca odağı geri ver"]
decisions: [{"when":"Native HTML elements match the intended behavior","use":"Use semantic controls and manage focus only at clear transitions.","tradeoff":"Native defaults reduce complexity but design and browser behavior need testing."},{"when":"A composite or modal widget needs custom focus behavior","use":"Follow the relevant ARIA authoring pattern and test actual interaction with keyboard and assistive technology.","tradeoff":"Custom keyboard handling introduces more states and maintenance."}]
checks: ["Open, navigate, dismiss and reopen using only a keyboard.","Verify focus after deleting the invoking row or replacing a focused control."]
sources: [{"title":"WAI-ARIA modal dialog pattern","url":"https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/"},{"title":"W3C Web Content Accessibility Guidelines 2.2","url":"https://www.w3.org/TR/WCAG22/"}]
---

<!-- Generated record title. -->
# Keyboard navigation and focus management

## Scenario

A document viewer opens a confirmation dialog from a row's action button. Keyboard users must be able to complete it and continue from the right row.

## Failure modes

Hidden or removed elements can retain focus. Custom widget keys may conflict with text entry, and focus can be lost when a list refreshes.

## Explain it simply

Let people reach every action from the keyboard and return them to the place they were working.

## Implementation guidance

Use a real button to open the dialog, choose a meaningful initial focus target, and keep modal keyboard focus in the dialog until it closes. Restore focus to the triggering row control or a logical replacement if that row is gone. Test the full sequence with Tab, Shift+Tab and Escape where supported, as well as another interaction following a refreshed list. Keyboard behavior and an accessibility tree inspection complement automated checks.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Native HTML elements match the intended behavior** Use semantic controls and manage focus only at clear transitions. Native defaults reduce complexity but design and browser behavior need testing.
- **A composite or modal widget needs custom focus behavior** Follow the relevant ARIA authoring pattern and test actual interaction with keyboard and assistive technology. Custom keyboard handling introduces more states and maintenance.

## Verification

- Open, navigate, dismiss and reopen using only a keyboard.
- Verify focus after deleting the invoking row or replacing a focused control.

## Sources

- [WAI-ARIA modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
- [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)

<!-- End generated record details. -->
