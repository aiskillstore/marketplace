---
name: whatsapp-closer
description: >-
  Load when designing, writing, reviewing or improving a sales assistant or salesperson that sells over WhatsApp (or any chat) to people who write from an ad ("Hi, info"): its prompt, its scripts, its follow-ups, or its results. Gives evidence-ranked rules to close (book a visit or call, or get paid) while staying likeable and inside WhatsApp/Meta policy: answer in under 5 minutes, few questions before price, one recommendation, every message ends in a two-option next step, objections answered with a pause and a question, 2-3 follow-ups max, human handoff always available. Includes ready scripts (Spanish, formal and informal), what not to do, metrics, and how to apply changes to a live assistant without breaking it. Triggers on "make it sell", "close more", "the bot doesn't close", "cerrar ventas", "que venda", "objections", "follow-up messages".
license: MIT
---

# WhatsApp closer

The only goal: **close** (a booked visit or call, or a payment), while the person likes talking to you. Every rule below says how strong its evidence is: **MEASURED** (a study with data), **OFFICIAL** (Meta/WhatsApp rule), or **OPINION** (well-known sales method, not measured on WhatsApp). Most "WhatsApp converts 8x" numbers online come from vendors without method; they are left out on purpose.

## 1. The rules, strongest first

1. **Answer in under 5 minutes.** Contacting a lead within 5 minutes vs 30 made reaching them ~100x and qualifying them ~21x more likely (MEASURED: Oldroyd/MIT lead response study; HBR 2011). Only 7% of companies manage it (MEASURED: Drift 2017), so speed alone beats competitors. Chat buyers expect minutes, not hours (MEASURED: Aircall 2019 survey).
2. **Offer a call inside WhatsApp at the moment of decision.** A Brazilian company got +26% conversions and ~50% faster closing when the chat offered a WhatsApp call right where people used to drop off (MEASURED by the company, published by Meta, 2025). The call is with a human (owner or team), so offer it, don't fake it.
3. **Ask before quoting, but few questions.** In sales calls, success rises up to ~11-14 questions (MEASURED: Gong, 519k calls). In chat every message costs attention: 2-3 sharp questions, then the answer.
4. **Price after the diagnosis, not before, and not hidden.** Top sellers discuss price after understanding the case (MEASURED: Gong). If asked "how much?" first: give the confirmed "from" price or the way it's priced, then one question to make it exact. Never invent a price or range the business didn't confirm.
5. **Objection → pause → question, not a speech.** Successful sellers slow down after an objection; nervous ones speed up (MEASURED: Gong, 67k meetings). In chat: acknowledge in one line, then ask what exactly worries them.
6. **"I'll think about it" is usually fear of a wrong choice.** Lower the risk: recommend one option, offer a smaller first step, show what's included. Don't push harder (MEASURED by the authors: The JOLT Effect, 2.5M calls).
7. **Real social proof, small and specific.** The first 5 reviews raise purchase likelihood a lot, more so for expensive items (MEASURED: Spiegel Research Center). Send 1-2 real photos or testimonials of the same service, ideally the same area. Never fake ones.
8. **Follow up 2-3 times, then stop.** One follow-up raised replies from 16% to 27% in email; the fourth tripled unsubscribes (MEASURED in email, no WhatsApp data). Plan: next day, ~3 days, ~7 days.
9. **The first reply continues the ad.** Repeat the offer they clicked and ask which option they want (OPINION, Click-to-WhatsApp guides).
10. **Recommend one thing.** A concrete recommendation beats a menu of options (OPINION backed by JOLT/Challenger).
11. **Every message ends in a next step with two options.** "Tuesday 10 or Thursday 3?" (OPINION: SPIN, Fanatical Prospecting, Gong consensus).
12. **Sell the gap**: the problem and what it costs to leave it (leaks get worse, the season is coming), not the product (OPINION: Gap Selling).
13. **"No"-oriented questions to revive**: "Have you given up on the roof?" gets more answers than "Are you still interested?" (OPINION: Never Split the Difference).
14. **Always offer a human.** Automated chats must let people reach a person (OFFICIAL: WhatsApp Business policy).
15. **Use the free window.** With the Cloud API, a person who arrives from a Click-to-WhatsApp ad and gets an answer within 24 h opens a free entry-point window (up to 7 days in current pricing; the old "72 h" figure is outdated). Outside 24 h of their last message you need an approved template (OFFICIAL: Meta pricing docs; check the current page).
16. **Tell Meta who booked or bought** (Conversions API with the click ID) so ads optimize for buyers, not chatters (OFFICIAL mechanism; benefit is vendor OPINION).
17. **Voice notes**: no study measures them. Use short ones only if the customer sends audio, always with the key data in text (OPINION).

## 2. Scripts (adapt the [ ])

**First reply after "Hi, info"** — formal: "¡Buenas! Con mucho gusto le ayudo. Soy [Nombre] de [Negocio]. ¿Es por [opción A del anuncio] o por [opción B]? Si me manda una foto, le digo de una vez cómo lo vemos." — informal: "¡Hola! Qué gusto 😊 Soy [Nombre] de [Negocio]. ¿Es para [A] o para [B]? ¿Y en qué zona estás?"

**"How much?" before qualifying** — "¡Claro! [Servicio] va desde [precio confirmado]; el monto exacto depende de [medida/material]. ¿Me manda una foto o más o menos cuántos metros?" (No confirmed price: "Se lo cotizamos exacto para no inventarle: ¿me manda una foto?")

**"I'll think about it"** — "Claro, es normal pensarlo. ¿Qué es lo que más le hace dudar: el precio, la fecha o si va a quedar bien? Así le paso justo esa info."

**"Too expensive"** — "Le entiendo. ¿Lo compara con otra cotización o con lo que tenía pensado?" Then what's included, and trade something for something (smaller first stage, different date). Never discount on the first "expensive".

**Ask for the close** — "Con lo que me cuenta, le recomiendo [opción]. Tengo visita el martes a las 10 o el jueves a las 3. ¿Cuál le queda mejor?"

**Follow-ups** — 24 h: "¡Hola [Nombre]! Le guardé el espacio del jueves. ¿Se lo confirmo?" · ~3 days (template if outside 24 h): "Terminamos un trabajo parecido en [zona], le paso la foto 👇 ¿Seguimos con lo suyo?" · ~7 days: "[Nombre], ¿ya descartó lo del [servicio]?"

**Revive (once, with a real reason)** — "Hace un tiempo me escribió por [servicio]. Esta semana [motivo real]. ¿Le sigue interesando o lo saco de mi lista?"

## 3. Never

- Free-form messages outside the 24 h window (templates only); messaging people who said stop; spam or surprises (blocks lower the number's quality).
- Frequent marketing templates to the same person (Meta caps them); low-quality templates (they get paused).
- Health claims or cure promises (supplements); asking for full card, account or ID numbers in chat.
- Bots with no way to a human; walls of text; discounting at the first objection; a 4th follow-up.
- Inventing prices, guarantees, years in business, certifications or deadlines the business didn't confirm.

## 4. Metrics (per product/ad set, weekly)

Time to first reply (<5 min) · reply rate to the first message · qualified / conversations · booked / conversations · showed / booked · paid / conversations · cost per sale (ad spend / sales), not just cost per conversation · average ticket and % sold with discount · revived / cold contacted · number quality and blocks. No trustworthy industry benchmarks exist for small LatAm businesses: measure 4 weeks as your own baseline and compare against it.

## 5. Changing a live assistant without breaking it

1. Read 20-30 real conversations first: where do people stop answering? That's where the rule goes.
2. One change at a time, with a test that fails before and passes after (the assistant's prompt and its fixed texts).
3. Keep what already works (cheapest conversations, phrases that get replies).
4. Simulate 10 conversations (price-first, "I'll think", "expensive", voice note, photo, out of area, formal/informal, "no thanks") before going live.
5. Compare the metrics of section 4 one and two weeks later. Roll back if booked/conversations drops.
