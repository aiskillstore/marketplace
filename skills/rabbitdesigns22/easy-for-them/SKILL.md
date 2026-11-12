---
name: easy-for-them
description: >-
  Load whenever the agent writes instructions, a message or a request that a person (the user, or the user's client, customer or teammate) will have to follow: setup steps, "please send me...", "go to... and click...", onboarding messages, payment or access requests. It makes every human step as easy as possible: direct links that land on the exact screen, values already filled in, ready-to-forward messages in plain words, one action per line, phone-friendly, and nothing asked that the agent could find or do itself. Triggers on "explain to my client how to...", "write the message for X", "give me the steps", and on users who say "make it easy", "pass them the link", "ponérsela fácil a la gente".
license: MIT
---

# Easy for them

Every extra click, unclear word or "find the Settings menu" loses people, especially busy clients on a phone. When a human has to do something, the agent's job is to make it almost effortless. Use together with `hands-on`: first do everything you can yourself; this skill is for the part that only a person can do.

## 1. Remove every step you can

Before writing any instruction:
- Can I do this step myself? Then do it (see `hands-on`).
- Can I read this value myself (an ID, an email, a URL)? Then don't ask for it.
- Can the system do it automatically (a generated PIN, a pre-filled form)? Propose that.

What remains is the minimum. Count the steps; if there are more than 5, look again.

## 2. Direct links, not directions

- Give the link that opens the **exact screen**, with the IDs already in the URL. Not "go to Settings > Billing > Accounts".
- Before sending a link, build it from a real URL you observed (or open it yourself) so you know it lands where you say. If you could not verify it, say what the person should see when it opens.
- For messaging apps, use links with the text already written (for example a `wa.me/<number>?text=...` link).
- One link per action, right next to the action.

## 3. Write for a person on a phone

- Plain words. No jargon: "the account where you pay" instead of "the billing hub of the WABA".
- One action per line, numbered, starting with a verb: "Tap...", "Write...", "Send me...".
- Say what they will see when it worked: "You'll see your card under 'How you'll pay'".
- Put copy-ready values in their own line or code block (amounts, names, codes they must type).
- Tell them what NOT to touch, in one line, if there is a real risk.
- Short. If it doesn't fit on one phone screen, cut.

## 4. Ready to forward

When the instructions are for the user's client, write the message **as the user would send it**: their voice, greeting, the links inside, nothing addressed to the user ("tell her to..."). The user should be able to copy and paste it without editing.

## 5. Ask once, everything together

If you need something from them (a code, an email, a photo), ask for all of it in one message, with the reason in a few words, and tell them the easiest way to send it (reply with a screenshot, forward the email).

## 6. Close the loop

Say how they confirm it's done ("send me a screenshot") and check it yourself when it arrives. Never leave them guessing whether it worked.

## Checklist before sending

- [ ] Did I remove every step I could do or read myself?
- [ ] Does every action have a direct link that I built from a real URL?
- [ ] One action per line, plain words, phone-sized?
- [ ] Ready to forward as-is, in the user's voice?
- [ ] Do they know what "done" looks like?
