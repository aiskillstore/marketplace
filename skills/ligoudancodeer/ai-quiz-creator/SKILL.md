---
name: ai-quiz-creator
description: Help users create and share a personalized 10-question friendship quiz on Block You Test Me. Collect their real choices, prepare an answer key, and return a public challenge link and private score page. Use for friend quizzes and social guessing games, not arbitrary-topic exams or personality assessments.
---

# AI Quiz Creator

An AI-assisted workflow for creating a friendship quiz with [Block You Test Me](https://blockyoutestme.fun/). The assistant guides the creator; the website hosts the quiz, scores friends' guesses, and provides share cards.

## Website and documentation

- Website: https://blockyoutestme.fun/
- Playing guide: https://blockyoutestme.fun/how-to-play/
- Machine-readable guide: https://blockyoutestme.fun/how-to-play/index.md
- About and contact: https://blockyoutestme.fun/about/
- Privacy: https://blockyoutestme.fun/privacy
- Updates: https://blockyoutestme.fun/updates/

## Create a quiz

1. Read [the current question set](references/questions.json). Every quiz has these 10 preset questions, in this exact order, with four options each. Explain this if the user requests custom questions or a themed quiz.
2. Ask for a nickname the user is comfortable making public and collect one choice per question. Ask in small batches when helpful. Never invent personal preferences or substitute an AI guess for a missing answer. Options are numbered 1–4 for the user; the stored answer indices are 0–3.
3. Prepare a JSON payload with `name`, ten `answers`, and optional `lang`. Show the user the choices if any mapping is ambiguous. Default to a local draft when they only ask for ideas. Creating a hosted quiz sends their nickname and selected answers to Block You Test Me; do it when the user requests hosting there, otherwise ask before sending.
4. If Node.js 18+ and network access are available, use the bundled helper. It previews locally unless `--publish` is provided:

   ```text
   node scripts/create-quiz.mjs --input /absolute/path/to/quiz.json
   node scripts/create-quiz.mjs --input /absolute/path/to/quiz.json --publish
   ```

   The helper posts only to `https://blockyoutestme.fun/api/quizzes`. It needs no account or API key. Do not automatically retry a failed or timed-out creation request: the first request may already have created a quiz.
5. If the network request is blocked or the helper is unavailable, give the user [the homepage](https://blockyoutestme.fun/) and their prepared choices to enter manually. Do not fabricate links or claim a quiz was created.
6. On success, give the creator two clearly separated links:
   - **Friend link:** share this publicly to invite players.
   - **Friend Score Page:** bookmark this privately. Anyone holding it can see submitted nicknames/scores and delete the quiz. Never put this link in invitations, screenshots, public repositories, examples, or directory listings.
7. Draft a friendly invitation containing only the public friend link. Do not send messages to friends unless the user explicitly asks. Explain that friends get one point for each matching answer, up to 10; they can save a score-card image after completing the quiz.

## Supported website features

Free browser play without sign-up; 10 preset friendship questions; creator-selected answer keys; public invitations; scores out of 10; private scoreboard and deletion; downloadable sharing cards; 25 display languages with a `lang` parameter and remembered browser preference.

Use only language codes listed by the helper. Keep nicknames, IDs and numeric answer indices unchanged when switching languages. Translate the conversational guidance when appropriate, not the underlying scoring rules.

The website does not generate arbitrary-topic questions, edit questions, assess personality, provide classroom testing, or detect social-media blocks. The AI assistance comes from the assistant running this skill, not an AI generation engine on the website. A low score is just a game result.

See [example interactions](examples/conversations.md). Treat live guide/schema differences as a reason to recheck the workflow before publishing; the question snapshot was checked against the website source on October 13, 2026.
