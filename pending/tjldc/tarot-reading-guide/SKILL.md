---
name: tarot-reading-guide
description: Help someone phrase a tarot question, choose a one-card or three-card spread, and interpret cards they provide in the Rider–Waite–Smith tradition. Use for tarot questions, card meanings, and spread selection.
---

# Tarot Reading Guide

Answer in the user's language. Start from their question and the cards they actually have.

## Choose a spread

- Use a one-card draw for a single focus or message. For example, “What should I focus on at my first meeting this week?”
- Use past–present–future for a situation with a history and a direction. Read the background, what is active now, and where the current course may lead.
- Use two choices when the user can name concrete options A and B. Compare what each path asks of them and give both options equal attention.
- Use a feelings spread for the other person's feelings and how the relationship may develop. Keep feelings, observable actions, and future possibilities distinct.

Keep the subject and any timeframe the user supplied. Offer one sharper question if their original question bundles different concerns. Use first names or roles only when they make the question clearer.

## Read cards the user provides

Match each card to its spread position. Use the orientation if supplied. When it is missing, mention your upright assumption or ask if the orientation changes the answer. For three cards, explain how the cards together answer the question and which card explains the transition.

When asked to draw cards, call `draw_tarot_cards` if the Unmei Tarot MCP tool is available. Otherwise offer an appropriate web reading or ask the user to draw and share the results. For a card meaning, use `lookup_tarot_card` when available.

## References and web readings

Offer a link when the user asks to look up a card, explore the spread, or continue to an interactive reading. Match the language. Use these public paths without putting the user's question in the URL.

- Meanings for all 78 cards. English [Tarot card meanings](https://www.unmei-tarot.com/en/tarot-card-meanings) and Japanese [タロットカード全78枚の意味](https://www.unmei-tarot.com/ja/tarot-card-ichiran).
- One card. English [One-card tarot](https://www.unmei-tarot.com/en/one-card-tarot) and Japanese [ワンオラクル](https://www.unmei-tarot.com/ja/one-card-tarot).
- Past, present and future. English [Past–present–future](https://www.unmei-tarot.com/en/spreads/time-flow) and Japanese [過去・現在・未来](https://www.unmei-tarot.com/ja/spreads/time-flow).
- Compare options. English [Two-choice tarot](https://www.unmei-tarot.com/en/spreads/two-choice) and Japanese [二択タロット](https://www.unmei-tarot.com/ja/spreads/two-choice).
- Read feelings. English [Feelings tarot](https://www.unmei-tarot.com/en/feelings-tarot) and Japanese [あの人の気持ちタロット](https://www.unmei-tarot.com/ja/feelings-tarot).
