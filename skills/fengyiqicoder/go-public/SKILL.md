---
name: go-public
description: Turn a workflow you just ran with the AI (a prompt, or a few prompts in a row, that take some input and produce a result) into a single web page anyone can open and use, with no account and no API key on their side, and publish it to a public link. Use when the user says "go public", "share this", "make this a page/tool/app others can use", "publish this workflow", "send this to my team/clients/friends", or wants a link to a prompt-based tool. Not for static pages without AI, multi-tool automations (Zapier/n8n style), or anything that needs a login, payment, or a database.
---

# Go Public

Goal: the workflow the user just ran with you becomes a link that works for anyone: they open it, fill in the input, press Run, and get the same kind of result. Visitors need no account. The page runs on a small free daily AI allowance that the page carries with it.

Everything happens through `share.py` in this skill's folder (Python 3, standard library). `<skill>` below means this skill's folder.

## 1. Pin down the workflow (ask, don't guess)

From the conversation, write down in 3–6 lines and show the user:
- **Visitor gives**: each input (a text box, a one-line field, or a pick from a list).
- **Steps**: each AI call in order, and what it does. Most workflows are 1–3 steps. Use the prompts that actually worked in this conversation, written so they make sense with no conversation around them.
- **Visitor gets**: which step results are shown.
- **Title** and a one-sentence description a stranger understands.

Ask the user to confirm or correct. Also ask what language the page should be in if it is not obvious.

Do not build pages that ask for passwords, payment or card details, one-time codes, or pretend to be another company or person. Do not put private data from the conversation (names, emails, internal numbers) into prompts or examples; use made-up examples.

## 2. Write workflow.json

In the user's current folder. Shape:

```json
{
  "title": "Meeting notes → follow-up email",
  "description": "Paste rough notes from a meeting. Get the decisions, owners, and a short follow-up email.",
  "inputs": [
    {"id": "notes", "label": "Your meeting notes", "type": "textarea", "placeholder": "Messy is fine…"},
    {"id": "tone", "label": "Tone", "type": "select", "options": ["Friendly", "Formal"]}
  ],
  "steps": [
    {"id": "facts", "prompt": "List the decisions, action items (owner — task — due date) and open questions. Use only what the notes say. Plain text, no Markdown.", "input": "{{notes}}", "show": true, "label": "What was decided"},
    {"id": "email", "prompt": "Write a follow-up email in a {{tone}} tone, under 150 words. Plain text, no Markdown.", "input": "{{facts}}", "show": true, "label": "Follow-up email"}
  ],
  "examples": [{"label": "Product sync", "values": {"notes": "launch moved to dec 2 bc payments bug. raj fixes bug by fri…", "tone": "Friendly"}}]
}
```

Rules:
- `type`: `textarea` (default), `text`, or `select` (needs `options`). Inputs are required unless `"required": false`.
- `{{id}}` in `prompt`, `system` or `input` is replaced by an input or an earlier step's answer. Put the visitor's text in `input`, the instruction in `prompt`; an optional `system` sets role and rules.
- `show: true` prints that step. Hidden steps are fine for intermediate work. The last shown step streams.
- `maxTokens` per step, default 800 (the page's limit too).
- Always give at least one example: visitors click it to see the page work before typing.
- Answers are shown as plain text, so `**bold**` shows up as asterisks. End every shown step's prompt with "Plain text, no Markdown." and use simple dashes for lists.

## 3. Check and try it for real

```bash
python3 <skill>/share.py check workflow.json
python3 <skill>/share.py try workflow.json      # runs example 1 through the real AI, prints every step
```

Read the output as a stranger would. If a step is vague, wrong, or too long, fix the prompt and run `try` again. Show the user the final output of the example before publishing.

## 4. Build and publish

```bash
python3 <skill>/share.py build workflow.json page.html
python3 <skill>/share.py publish page.html
```

`publish` prints the public link. It saves the page id and a private edit token in `.go-public.json` (and adds it to `.gitignore` in a git repo). Tell the user:
- the link, ready to send to anyone;
- that `.go-public.json` is what lets them change or remove the page later, so keep it and do not share it.

Do not hand-edit page.html: change workflow.json and build again.

## 5. Change or remove it later

Edit workflow.json, then `build` and `publish` again in the same folder: same link, new content. `python3 <skill>/share.py delete` takes it down.

## Limits to state honestly when they come up

- Each page has a free AI allowance per day and a per-visitor rate limit (printed by `publish`). When a busy page runs out, it says so and works again the next day.
- If the user asks how to raise the limit or see usage: the `claim_url` in `.go-public.json` lets them claim the page. They enter an email, confirm it from their inbox, and the page then runs on that account's own allowance. Mention this only when they ask or the allowance runs out. The small "Made with OneTag · Report" mark stays on every page.
- Visitors can report a page; a page several people report is taken offline for review.
- The page cannot load outside images, fonts or libraries, and has no storage or login: it is a form, AI steps, and results.
