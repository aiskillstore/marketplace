# Parametric Scribe: Time Travel for AI Coding

**Most AI coding is destructive.** You paint over the canvas. If you realize your foundation was wrong, you have to scrape it off or start over.

**Parametric Scribe changes this.** It treats your coding session like a CAD Timeline or a Non-Linear Editor.
*   **Record:** Every task you complete is saved as a discrete "Step" with an **Intent** (Prompt) and **Outcome** (Files).
*   **Replay:** Want to change Step 1 from "Flask" to "Django"? The Scribe doesn't just change the text; it **replays the subsequent steps**, intelligently adapting them to the new foundation.

## The Problem
In CAD, if you change a Sketch from a Square to a Circle, the Extrude feature updates automatically.
In Code, if you change `app.py` to `index.js`, your subsequent "Add Login" prompt fails because it's looking for Python code.

## The Solution
Parametric Scribe uses the LLM as an **Intelligent Compiler**. During replay, it looks at the *original intent* of the subsequent steps ("Add Login") and applies it to the *new reality* (the Node.js app), effectively "healing" the broken references.

## Usage
This is a **Superpower Skill**.
1.  Add this folder to your Agent's workspace.
2.  Tell the Agent: "Read `parametric-scribe/SKILL.md`."
3.  Start coding.

## The Recipe File
Your history is saved in `docs/recipe.yaml`. This is your Source of Truth.
