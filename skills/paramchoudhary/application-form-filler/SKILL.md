---
name: application-form-filler
description: Fill out job application form fields with context-aware, tailored answers drawn from the candidate's CV and the job description
---

# Application Form Filler

## When to Use This Skill

Use this skill when the user wants to:
- Answer specific questions on a job application form
- Fill out text fields on Greenhouse, Lever, Ashby, Workday, or any ATS
- Write responses to "tell us about yourself" or "why do you want to work here" prompts
- Get clean, copy-pasteable answers to application questions
- Mentions: "fill this out", "what do I write here", "answer this question", "application form", "form field"

## Core Principle

Application form answers should be direct and specific — not a cover letter crammed into a text box. Each field has a purpose. Answer that purpose clearly, then stop.

**The answer should feel like:** A real person typed it, not a template was filled in.

## Before Answering

Always read:
1. **The job description** — mirror its language and priorities
2. **The candidate's CV/profile** — pull real projects, roles, and metrics
3. **The specific question** — answer exactly what was asked, not what you wish was asked

If the user hasn't provided a CV or JD, ask for them before writing.

## Question Types and How to Handle Each

---

### Type 1: Experience/Background Questions

**Examples:**
- "How many years of experience do you have with [technology]?"
- "Describe your experience with [domain]"
- "What backend frameworks have you used?"

**Format:**
```
[Technology/skill] — [X years]. [One sentence on what you used it for, with a
specific project or context]. [Optional: secondary tools in the same category].
```

**Rules:**
- Lead with the most used/relevant technology
- Give years honestly — don't inflate
- Anchor every claim to a real project or role
- For "describe experience" questions: 2-4 sentences max, one project per sentence
- If experience is indirect (adjacent domain), say so and pivot to what is relevant

---

### Type 2: Why This Company / What Interests You

**Examples:**
- "Why do you want to work at [Company]?"
- "What interests you about this role?"
- "Why are you a good fit?"

**Format:**
```
[Specific thing about the company/role that's genuinely interesting — not generic].
[How that connects to something the candidate has actually worked on].
[Optional: one line on why this domain, not just this company].
```

**Rules:**
- Must be specific to this company — no boilerplate
- Research the company before answering if needed
- Connect to real work, not aspirations
- Keep it under 150 words for a form field
- Don't repeat the JD back to them

---

### Type 3: Portfolio / Work Samples

**Examples:**
- "Include any other samples of work you're proud of"
- "Link to relevant projects or repositories"
- "Describe a project you've built end-to-end"

**Format:**
List projects with one-line descriptions and links. Lead with the most relevant.

```
[Project Name] ([live URL] | [github URL]) — [one line: what it is and one
proof point]. [Stack if relevant].
```

**Rules:**
- Only include projects relevant to the role
- Always include links (live demo > GitHub > nothing)
- If the project has paying users or measurable usage, say so — once
- Don't pad with irrelevant projects to look prolific

---

### Type 4: Technical Skill Questions

**Examples:**
- "Which frontend frameworks have you used most extensively?"
- "Rate your proficiency in Python"
- "Describe your experience with cloud infrastructure"

**Format:**
For open-text fields:
```
[Primary skill] — [X years]. [Specific use: what you built with it, in what context].
[Secondary skill] — [X years]. [Same].
[Note any relevant gaps honestly].
```

For rating/dropdown fields: pick the honest level — don't optimize for the highest rating if it's not accurate.

**Rules:**
- Years + context beats years alone
- Acknowledge gaps rather than hiding them
- If asked to rate, rate honestly — inflated ratings create problems in technical interviews
- For stacks you've used but not recently, note it

---

### Type 5: Open-Ended / "Tell Us About Yourself"

**Examples:**
- "Tell us about yourself"
- "Describe your professional background"
- "What are you looking for in your next role?"

**Format:**
```
Current role + what you do there (1 sentence).
Relevant prior experience, briefly (1 sentence).
What you're looking for / why this role (1-2 sentences — specific to the company).
Optional: one project or side work that's relevant (1 sentence).
```

**Rules:**
- Start with current role, not education
- Keep to 100-200 words for most form fields
- End on the forward-looking note (what you want, not where you've been)
- No trait statements ("I'm passionate about...") — just facts and projects

---

### Type 6: Situational / Behavioral Questions

**Examples:**
- "Describe a time you solved a complex technical problem"
- "Tell us about a project you led end-to-end"
- "How do you handle working across multiple teams?"

**Format:** Condensed STAR (no labels, just flow)

```
[Context in one sentence]. [What you specifically did — 2 sentences]. [Outcome
with a metric if possible — 1 sentence].
```

**Rules:**
- Be specific — name the project, the tech, the team size
- Don't generalize ("I always approach problems by...")
- Keep to 150-250 words
- First-person, active voice throughout
- End with the result, not the lesson learned (save that for interviews)

---

### Type 7: Opinion / Vision Questions

**Examples:**
- "Which technologies do you think are most important for the future?"
- "What would you learn if you had unlimited time?"
- "Where do you see AI/[domain] in 5 years?"

**Format:**
Answer with a genuine opinion. Pick one or two things and explain the reasoning briefly.

**Rules:**
- Have an actual point of view — vague answers are forgettable
- Ground opinions in domain knowledge or real experience
- Keep to 100-150 words
- Don't hedge everything — commit to a view, acknowledge it's one perspective

---

## Output Format

Always wrap the answer in a plain code block so it's clean to copy-paste:

```
[Answer text here]
```

If providing multiple answers (one per field), use separate code blocks with a label above each:

**Years of React experience:**
```
4 years. Used it across Screenr (agentic hiring SaaS), a Tauri-based POS
system, and several client projects. Also used Next.js where SSR was needed.
```

**Describe your backend experience:**
```
...
```

## Length Calibration

| Field type | Target length |
|------------|---------------|
| Single-line text | 1 sentence |
| Short answer | 2-4 sentences |
| Long answer / textarea | 100-250 words |
| "Describe your experience" | 150-300 words |
| "Tell us about yourself" | 100-200 words |
| Portfolio / links section | List format, no prose |

When in doubt, shorter is better. Recruiters skim form answers. The goal is to be clear and memorable, not comprehensive.

## Common Mistakes to Avoid

**Repeating the JD:**
❌ "I am interested in this role because you are looking for someone to build scalable backend systems..."
✅ "What caught my attention was the real-time constraint — healthcare data at milliseconds latency is a different class of problem than most backend work."

**Generic trait claims:**
❌ "I am a fast learner who thrives in collaborative environments"
✅ [Just describe the actual work — the traits come through]

**Over-qualifying:**
❌ "While I may not have exactly 5 years, I believe my experience..."
✅ "The role mentions 5 years — I'm at 3, but the systems I've shipped are production-facing."

**Listing without context:**
❌ "React, Vue, Angular, Next.js, TypeScript, Node.js..."
✅ "React is my primary frontend framework — 4 years across Screenr and several client projects. Vue and Angular for about 3 years each, mostly dashboards and admin tooling."

**Padding to fill space:**
❌ Adding projects or experience that aren't relevant just to look prolific
✅ Include only what's relevant to this specific role
