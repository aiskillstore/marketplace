---
name: cold-offer
description: "Draft a cold offer as a leak, a prototype, and email one. Use when the first outbound email should hand over a finding and a short trial, and when email one must not sell the paid product."
models: ""
---

# Cold offer

A cold offer is not the main service. Email one hands over work already done: a finding the buyer did not request, and a short trial of the solution. The full report is offered only if they want it. There is no meeting ask, no demo, and no pitch.

The build guide teaches a human. This pack teaches an agent.

## The three parts

1. Leak. The finding, in words the reader already uses. One concrete miss on their public page or product. They did not ask for it.
2. Prototype. The short trial. One page, one sample, or one worked slice of the fix. It shows the system works. It is not the core retainer.
3. Email one. States that offer in words the reader understands. It delivers the finding. It names the prototype. It offers the full report only if they want it.

## What email one refuses

The scorer refuses email one that sells the paid product. Selling means the letter asks the reader to buy, book, or start the paid thing: retainer, demo, purchase, subscribe, checkout, or pricing of the core service.

A letter can name the finding and the short trial. It does not sell the retainer in the same breath.

A recruiter note that asks for coffee is a different letter. It is not this gate. This gate is selling the paid product.

## Checklist

Copy this list and tick it in order.

- [ ] 1. Choose the finding the buyer did not request.
- [ ] 2. Fill the offer shell: leak, prototype, email one.
- [ ] 3. Run `python3 scripts/score.py --file draft.json`.

Check again until the script exits 0.

Go back to step 2 if step 3 fails.

## Run

```bash
python3 scripts/score.py --file examples/offer-good.json
python3 scripts/score.py --file examples/offer-sells.json
```

The good file exits 0 and prints the leak, the prototype, and email one. The sell file exits 1.

The JSON object has three strings: `leak`, `prototype`, and `email_one`. A broken JSON exits non-zero and does not echo the raw input.

Python 3 standard library only. No network. No send.

## Shell

```json
{
  "leak": "The homepage asks for a meeting before it shows any work.",
  "prototype": "A one-page sample that leads with one finding and the short trial, and stops there.",
  "email_one": "Your homepage asks for a meeting before it shows any work. I wrote one page that leads with that finding. The full report is yours if you want it."
}
```
