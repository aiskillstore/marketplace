# Slop Text Humanizer Pro

**Humanize AI text, remove AI flavor, and keep your original meaning, facts, and voice.** 
Stop sounding like a robot. Turn AI-generated drafts into natural, human-sounding text with a dedicated next-gen cloud engine.

Whether you need to **humanize an essay**, **rewrite a blog post**, **remove AI tone from an email**, or **eliminate AI traces in a novel**, this skill gets the job done without breaking your content's structure.

---

## 🚀 Why Choose This? (Core Features)

Unlike basic rulebook-based tools that rely on the host AI's mood, this skill routes your text through a **purpose-tuned cloud engine**.

*   🧠 **Next-Gen Cloud Engine:** Consistent, high-quality results every time. **No template flavor** — every output feels uniquely written by a human.
*   🔗 **Golden Pair Combo Recipes:** Single mode is for beginners; combos are for pros. Combine two passes to fix stubborn, heavily AI-flavored drafts.
*   🛡️ **Seven-Keep Fidelity Promise:** Never flips viewpoints, never alters facts/numbers, never breaks attribution, never drops core information. Your meaning stays 100% intact.
*   📊 **Five-Dimension Quality Report:** See exactly what changed. Every run reports rhythm variance, vocabulary register, AI-tell density, and specificity scores before and after.
*   🌍 **Fully Language-Adaptive:** Input in any language, output in the same language. English in, English out. Chinese in, Chinese out.
*   🔒 **Stateless Privacy:** Cloud functions run statelessly — nothing is stored, no context kept, discarded after each run.

---

## 🛠️ How to Use in Your AI Agent

Works perfectly with **Claude Code, Codex, OpenClaw, WorkBuddy**, and any skill-capable AI agent.

**1. Light & Fast:**
> *"Humanize this text for me: [paste 300+ characters of text]"*

**2. Deep Rewrite (For heavy AI drafts):**
> *"Remove the AI tone and use a Golden Pair combo to rewrite this essay."*

*(💡 Pro Tip: If you don't know which mode to use, just paste your text. The agent will list all available modes and recommend the best one for your specific scenario.)*

---

## 🎯 Trigger Words
The AI agent will automatically activate this skill when you say phrases like:
`"humanize this"` · `"remove AI tone"` · `"make this sound human"` · `"sounds like ChatGPT"` · `"fix my AI draft"` · `"去AI味"` · `"降AI味"` · `"润色"` · `"洗稿"`

---

## 💻 Developer API
The engine is OpenAI-compatible, meaning you can plug it into any client, workflow, or self-built app.
```bash
POST https://1257655569-3o00dbw8fr.ap-singapore.tencentscf.com/v1/chat/completions
Authorization: Bearer sk-hai-...
{"model": "<mode-id>", "messages": [{"role": "user", "content": "..."}]}
