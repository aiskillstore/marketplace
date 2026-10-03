---
name: lifecycle-email
description: "Draft a lifecycle email as a welcome, delivery of the bargain, then nurture tied to the pain they showed. Use when someone already opted in and the sequence must not be a generic drip or a cold email."
models: ""
---

# Lifecycle email

Someone raised a hand. The sequence has three parts, in this order. Welcome them. Hand over the thing they opted in for. Then keep writing about the pain they already showed.

The build guide teaches a human. This pack teaches an agent.

## The three parts

1. Welcome. The first note after the opt-in. It names that they asked, and it starts the relationship. It is not an introduction to a stranger.
2. Bargain. Delivery of the thing they were promised: the checklist, the sample, the access. The bargain is the exchange, handed over.
3. Nurture. Later notes that stay on the pain they showed on the form or in the reply. The pain is in the words. A calendar of tips is not nurture.

## What the scorer refuses

The scorer refuses a generic drip and a cold email. A generic drip is a day-1, day-3, day-7 tip series, or a note that calls itself a generic drip. A cold email speaks to someone who never opted in, introduces a product to a stranger, or is labeled a cold email.

A welcome can be short. It still has to be for a person who opted in, and the nurture still has to name their pain.

## Checklist

Copy this list and tick it in order.

- [ ] 1. Name the pain they showed.
- [ ] 2. Fill the sequence shell: welcome, bargain, nurture.
- [ ] 3. Run `python3 scripts/score.py --file draft.json`.

Check again until the script exits 0.

Go back to step 2 if step 3 fails.

## Run

```bash
python3 scripts/score.py --file examples/lifecycle-good.json
python3 scripts/score.py --file examples/lifecycle-refused.json
```

The good file exits 0 and prints the welcome, the bargain, and the nurture. The refused file exits 1.

The JSON object has four strings: `pain`, `welcome`, `bargain`, and `nurture`. A broken JSON exits non-zero and does not echo the raw input.

Python 3 standard library only. No network. No send.

## Shell

```json
{
  "pain": "the trial dies after the first login",
  "welcome": "You asked for the trial checklist. This note starts there.",
  "bargain": "The checklist is the bargain. It is attached, the thing you opted in to receive.",
  "nurture": "The next note stays on the pain you showed: the trial dies after the first login."
}
```
