# Example conversations

## Create a friendship challenge

**User:** Help me make a friendship quiz on Block You Test Me.

**Assistant:** This uses ten preset questions about your preferences. What nickname should friends see? For the first question, what is your ideal weekend: a slow day at home, a food adventure, a spontaneous trip, or seeing friends?

The assistant collects all ten choices without guessing and maps them to the fixed option order. If the user wants to host the quiz on the linked website, the assistant publishes through the helper or assists with the browser workflow. It returns only real API or browser-generated links.

**Successful handoff format:**

- Friend invitation: the returned public `quizUrl`.
- Friend Score Page: the returned private `manageUrl`; bookmark and keep it private.
- Invitation copy: “Think you know me? Try my friendship quiz: [public friend link].”

The placeholders above explain the format; they are not real quiz links.

## Unsupported topic

**User:** Create a Harry Potter quiz on this website.

**Assistant:** Block You Test Me currently hosts ten preset friendship questions, so it cannot host a custom Harry Potter quiz. I can help you create the supported friendship challenge, or draft custom questions in this chat without claiming the website hosts them.

## Hindi invitation

**User:** I want my friends to open the quiz in Hindi.

Set `lang` to `hi`. Preserve the creator's nickname and answer indices. The public invitation link can include `?lang=hi`; keep the private management link out of the invitation. The actual link must come from successful quiz creation.

## Website unavailable

**User:** The helper returned 403.

**Assistant:** I could not verify quiz creation. Here is the homepage and your prepared answer key for manual entry: https://blockyoutestme.fun/. If a request timed out, first check whether you already received a result before creating another quiz.
