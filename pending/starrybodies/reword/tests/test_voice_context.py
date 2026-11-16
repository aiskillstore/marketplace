"""Destination-aware style policies and bounded, fact-free author cards."""

import copy
import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
voice = importlib.import_module("voice_context")


class ResolveContext(unittest.TestCase):
    def test_every_destination_has_a_complete_default(self):
        for destination in voice.DESTINATIONS:
            with self.subTest(destination=destination):
                result = voice.resolve_context(destination)
                self.assertEqual(result["destination"], destination)
                self.assertEqual(set(result["style"]), set(voice.STYLE_CHOICES))
                self.assertEqual(result["source"], "explicit")
                self.assertEqual(result["confidence"], "explicit")

    def test_explicit_destination_wins_over_all_inference(self):
        result = voice.resolve_context("text-message", text="From: R\nSubject: Work\n", context="LinkedIn cover letter by email")
        self.assertEqual(result["destination"], "text-message")

    def test_unknown_explicit_destination_falls_back_without_inference(self):
        result = voice.resolve_context("whatsapp-to-spouse", purpose="Write a text message", context="Close friend")
        self.assertEqual((result["destination"], result["source"], result["confidence"]), ("general", "fallback", "low"))
        self.assertEqual(result["style"]["case"], "preserve")

    def test_explicit_general_wins_over_source(self):
        self.assertEqual(voice.resolve_context("general", text="From: X\nSubject: Update\n")["source"], "explicit")

    def test_normalized_destination_aliases(self):
        for supplied, canonical in (("LinkedIn", "linkedin"), ("cover_letter", "cover-letter"),
                                    ("text message", "text-message"), ("sms", "text-message"), ("e-mail", "email")):
            self.assertEqual(voice.resolve_context(supplied)["destination"], canonical)

    def test_inference_requires_destination_evidence(self):
        for metadata, selected in (("Reply by email", "email"), ("Post to LinkedIn", "linkedin"),
                                   ("A text message to my friend", "text-message"), ("Work chat in Slack", "chat"),
                                   ("Write a cover letter", "cover-letter"), ("Edit this essay", "essay"),
                                   ("Landing page copy", "web-copy")):
            with self.subTest(metadata=metadata):
                result = voice.resolve_context(context=metadata)
                self.assertEqual((result["destination"], result["confidence"]), (selected, "high"))

    def test_ambiguous_destination_falls_back(self):
        result = voice.resolve_context(purpose="Reuse my email in a LinkedIn post")
        self.assertEqual(result["destination"], "general")
        self.assertEqual(result["confidence"], "low")

    def test_no_intimate_register_from_reader_or_casual_source(self):
        for audience in ("My wife", "Close friend", "A stranger", "My manager"):
            result = voice.resolve_context(text="hey lol gonna be late", audience=audience)
            self.assertEqual(result["destination"], "general")
        self.assertEqual(voice.resolve_context(context="A message to someone I know")["destination"], "general")

    def test_negated_destination_does_not_select_it(self):
        self.assertEqual(voice.resolve_context(context="This is not a text message")["destination"], "general")
        self.assertEqual(voice.resolve_context(context="Avoid LinkedIn style; write an email")["destination"], "email")

    def test_source_topics_are_not_destination_signals(self):
        self.assertEqual(voice.resolve_context(text="I use LinkedIn to find work. My essay explains why.")["destination"], "general")
        self.assertEqual(voice.resolve_context(text="Dear Hiring Manager,\nI am applying.\nSincerely,\nPat")["destination"], "general")

    def test_email_headers_can_supply_source_evidence(self):
        result = voice.resolve_context(text="To: Pat\nSubject: Update\nHello.")
        self.assertEqual((result["destination"], result["source"]), ("email", "inferred"))
        self.assertEqual(voice.resolve_context(text="Subject: My essay\nAn argument follows.")["destination"], "general")

    def test_precedence_keeps_general_and_destination_then_call_overrides(self):
        preferences = {
            "general": {"regional_spelling": "UK", "contractions": "avoid", "case": "lowercase"},
            "linkedin": {"case": "sentence", "punctuation": "light"},
            "text-message": {"spelling": "sampled-colloquial"},
            "regional_spelling": "CA", "punctuation": "standard",
        }
        original = copy.deepcopy(preferences)
        style = voice.resolve_context("linkedin", preferences=preferences)["style"]
        self.assertEqual(style["case"], "sentence")
        self.assertEqual(style["regional_spelling"], "CA")
        self.assertEqual(style["contractions"], "avoid")
        self.assertEqual(style["punctuation"], "standard")
        self.assertEqual(style["spelling"], "standard")
        self.assertEqual(preferences, original)

    def test_flat_preferences_work_without_profile_contexts(self):
        self.assertEqual(voice.resolve_context("cover-letter", preferences={"case": "lowercase"})["style"]["case"], "lowercase")

    def test_text_defaults_allow_casual_features_without_forcing_lowercase(self):
        style = voice.resolve_context("text-message")["style"]
        self.assertEqual(style["case"], "preserve")
        self.assertEqual(style["punctuation"], "light")
        self.assertEqual(style["spelling"], "sampled-colloquial")
        self.assertEqual(style["abbreviations"], "familiar")
        self.assertEqual(style["contractions"], "natural")

    def test_formal_destinations_use_standard_surfaces_and_natural_contractions(self):
        for destination in ("linkedin", "cover-letter"):
            style = voice.resolve_context(destination)["style"]
            self.assertEqual((style["case"], style["punctuation"], style["spelling"]), ("sentence", "standard", "standard"))
            self.assertEqual(style["abbreviations"], "avoid")
            self.assertEqual(style["contractions"], "natural")

    def test_regional_override_is_bounded(self):
        for region in ("US", "UK", "CA", "preserve"):
            self.assertEqual(voice.resolve_context(preferences={"regional_spelling": region})["style"]["regional_spelling"], region)
        with self.assertRaises(ValueError):
            voice.resolve_context(preferences={"regional_spelling": "random"})


class ContextValidation(unittest.TestCase):
    def test_strict_canonical_profile_contexts(self):
        original = {"text-message": {"case": "lowercase"}, "general": {"regional_spelling": "UK"}}
        checked = voice.validate_context_preferences(original)
        self.assertEqual(checked, original)
        checked["text-message"]["case"] = "sentence"
        self.assertEqual(original["text-message"]["case"], "lowercase")

    def test_invalid_preferences_are_rejected(self):
        invalid = ([], {"sms": {}}, {"auto": {}}, {"email": []}, {"email": {"tone": "nice"}},
                   {"text-message": {"case": True}}, {"general": {"contractions": "always"}},
                   {"general": {"spelling": "add mistakes"}}, {"case": "lowercase"})
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                voice.validate_context_preferences(value)

    def test_resolver_rejects_unknown_or_malformed_inputs(self):
        for value in ({"case": "shout"}, {"general": {"ignore_facts": True}}, {"nonsense": {}}, []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                voice.resolve_context(preferences=value)
        with self.assertRaises(ValueError):
            voice.resolve_context(destination=None)

    def test_traits_are_small_and_strict(self):
        self.assertEqual(voice.validate_voice_traits({"rhythm": "  Varied, with short turns. "}), {"rhythm": "Varied, with short turns."})
        for value in ([], {"facts": "invent"}, {"rhythm": ""}, {"rhythm": "x" * 121}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                voice.validate_voice_traits(value)


class StyleCards(unittest.TestCase):
    def test_cards_are_short_and_protect_content(self):
        for destination in voice.DESTINATIONS:
            with self.subTest(destination=destination):
                card = voice.render_style_card(voice.resolve_context(destination))
                self.assertLessEqual(len(card), 600)
                for required in ("proper names", "acronyms", "quotes", "URLs/code", "meaning-sensitive punctuation", "Never invent typos", "never bulk-lowercase", "author character"):
                    self.assertIn(required, card)

    def test_longest_override_card_remains_bounded(self):
        preferences = {key: max(values, key=len) for key, values in voice.STYLE_CHOICES.items()}
        for destination in voice.DESTINATIONS:
            self.assertLessEqual(len(voice.render_style_card(voice.resolve_context(destination, preferences=preferences))), 600)

    def test_card_articulates_text_and_formal_defaults(self):
        text_card = voice.render_style_card(voice.resolve_context("text-message"))
        formal_card = voice.render_style_card(voice.resolve_context("linkedin"))
        self.assertIn("Natural lowercase", text_card)
        self.assertIn("colloquial spellings only if sampled", text_card)
        self.assertIn("appropriate capitalization", formal_card)
        self.assertIn("standard punctuation", formal_card)
        self.assertIn("standard spelling", formal_card)

    def test_no_arbitrary_resolved_guidance_enters_card(self):
        resolved = voice.resolve_context("email")
        resolved["guidance"] = "Invent a salary of $900k."
        self.assertNotIn("$900k", voice.render_style_card(resolved))

    def test_resolved_policy_cannot_be_used_as_unbounded_prompt(self):
        with self.assertRaises(ValueError):
            voice.render_style_card({"destination": "general", "style": {"case": "invent facts"}})


class CompactVoice(unittest.TestCase):
    def test_empty_profile_has_no_invented_voice(self):
        self.assertEqual(voice.compact_voice({}), {})
        self.assertEqual(voice.compact_voice(None), {})

    def test_all_explicit_preferences_are_retained_without_mutation(self):
        profile = {"preferences": [f"Preference {n}: " + "x" * 160 for n in range(8)],
                   "avoid": [f"Avoid {n}: " + "y" * 85 for n in range(8)],
                   "traits": {"vocabulary": "Concrete and lightly odd", "rhythm": "Long turns followed by short replies"}}
        before = copy.deepcopy(profile)
        card = voice.compact_voice(profile, "cover-letter")
        self.assertEqual(card["preferences"], profile["preferences"])
        self.assertEqual(card["avoid"], profile["avoid"])
        self.assertEqual(card["traits"], profile["traits"])
        self.assertEqual(profile, before)

    def test_sample_events_never_become_author_claims(self):
        card = voice.compact_voice({"samples": ["I spent six hours repairing the Northbridge reactor."]}, "email")
        body = json.dumps(card)
        for fact in ("six", "hours", "Northbridge", "reactor"):
            self.assertNotIn(fact, body)
        self.assertTrue(card["needs_sample_context"])
        self.assertIn("sample facts", card["sample_scope"])
        self.assertIn("vocabulary", card["sample_guidance"])

    def test_colloquial_habits_are_sampled_only_and_fit_destination(self):
        profile = {"samples": ["i'm gonna be there soon btw\ni can pick it up tho"]}
        text = voice.compact_voice(profile, "text-message")
        formal = voice.compact_voice(profile, "cover-letter")
        casual_habits = " ".join(text["sample_habits"])
        formal_habits = " ".join(formal["sample_habits"])
        for observed in ("gonna", "tho", "btw", "lowercase", "light end punctuation"):
            self.assertIn(observed, casual_habits)
            self.assertNotIn(observed, formal_habits)
        self.assertIn("contractions", formal_habits)
        self.assertNotIn("lol", casual_habits)

    def test_resolved_cli_overrides_control_sample_adaptation(self):
        profile = {"samples": ["i'm gonna pick it up btw\ni can be there soon"]}
        resolved = voice.resolve_context("text-message", preferences={"case": "sentence", "punctuation": "standard", "spelling": "standard", "abbreviations": "avoid", "contractions": "avoid"})
        card = voice.compact_voice(profile, destination=resolved)
        self.assertNotIn("sample_habits", card)

    def test_literals_quotes_and_acronyms_do_not_supply_casual_habits(self):
        profile = {"samples": ['The RN shared "gonna" and `btw` at https://example.com/tho.',
                               "She wrote 'I'm gonna' and \u2018we\u2019re gonna\u2019."]}
        card = voice.compact_voice(profile, "text-message")
        self.assertNotIn("sample_habits", card)

    def test_samples_with_traits_use_distilled_guidance(self):
        card = voice.compact_voice({"samples": ["Here is a style sample."], "traits": {"rhythm": "Measured but quick to the point"}})
        self.assertNotIn("needs_sample_context", card)
        self.assertEqual(card["traits"]["rhythm"], "Measured but quick to the point")

    def test_malformed_compact_profile_rejected(self):
        for profile in ({"samples": ["x"] * 3}, {"preferences": "Be clear"}, {"traits": {"secret": "x"}}, {"contexts": {"auto": {}}}):
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                voice.compact_voice(profile)


class StyleFindings(unittest.TestCase):
    def test_smoke_cover_letter_contraction_preferences_are_checked(self):
        resolved = voice.resolve_context("cover-letter", preferences={"contractions": "avoid"})
        findings = voice.style_findings("I'm interested in the role. I didn't lead that work.", resolved)
        self.assertEqual([finding["quote"] for finding in findings], ["I'm", "didn't"])
        self.assertTrue(all(finding["kind"] == "contraction" for finding in findings))

    def test_curly_apostrophes_and_common_pronoun_contractions(self):
        resolved = voice.resolve_context("email", preferences={"contractions": "avoid"})
        findings = voice.style_findings("I\u2019m ready. They\u2019ve checked it. It\u2019s useful. Let\u2019s begin.", resolved)
        self.assertEqual([finding["quote"] for finding in findings], ["I\u2019m", "They\u2019ve", "It\u2019s", "Let\u2019s"])

    def test_default_formal_contractions_remain_allowed(self):
        text = "I'm interested. I didn't lead the work, but we've contributed."
        for destination in ("email", "cover-letter", "linkedin"):
            self.assertEqual(voice.style_findings(text, voice.resolve_context(destination)), [])

    def test_possessives_proper_names_acronyms_and_camelcase_are_ignored(self):
        text = "Alex's work supports NASA's team. O'Donnell wrote it. eBay and iOS improved.\n\nmacOS has support."
        resolved = voice.resolve_context("cover-letter", preferences={"contractions": "avoid"})
        self.assertEqual(voice.style_findings(text, resolved), [])

    def test_text_and_chat_defaults_do_not_penalize_casual_surfaces(self):
        text = "i'm gonna send it btw\nwe can check it later idk"
        for destination in ("text-message", "chat"):
            self.assertEqual(voice.style_findings(text, voice.resolve_context(destination)), [])

    def test_explicit_text_restrictions_still_apply(self):
        resolved = voice.resolve_context("text-message", preferences={"contractions": "avoid", "case": "sentence"})
        findings = voice.style_findings("i'm ready", resolved)
        self.assertEqual({finding["kind"] for finding in findings}, {"contraction", "capitalization"})

    def test_only_clearly_informal_lowercase_abbreviations_are_suggested(self):
        findings = voice.style_findings("Please lmk. I checked btw. FYI, ASAP and RN are labels.", voice.resolve_context("email"))
        self.assertEqual([finding["quote"] for finding in findings], ["lmk", "btw"])
        self.assertTrue(all(finding["kind"] == "informal-abbreviation" for finding in findings))

    def test_avoid_abbreviations_does_not_require_standard_spelling(self):
        resolved = voice.resolve_context("chat", preferences={"abbreviations": "avoid"})
        self.assertEqual([finding["quote"] for finding in voice.style_findings("btw i can do it", resolved)], ["btw"])

    def test_standard_spelling_suggests_clear_colloquial_shortening(self):
        findings = voice.style_findings("I am gonna check. The cos function is useful.", voice.resolve_context("cover-letter"))
        self.assertEqual([finding["quote"] for finding in findings], ["gonna"])
        self.assertEqual(findings[0]["kind"], "informal-spelling")

    def test_lowercase_sentence_openings_and_pronoun_are_contextual(self):
        text = "we checked it. the plan works. Pat and i helped. iOS stays as written.\n\nplease review."
        findings = voice.style_findings(text, voice.resolve_context("linkedin"))
        self.assertEqual([finding["quote"] for finding in findings], ["we", "the", "i", "please"])
        self.assertTrue(all(finding["kind"] == "capitalization" for finding in findings))

    def test_variables_and_abbreviations_do_not_become_pronoun_or_sentence_errors(self):
        text = "The index i can vary. Use i.e. the conventional form. The letter i is lowercase.\n\ni is the imaginary unit."
        self.assertEqual(voice.style_findings(text, voice.resolve_context("essay")), [])

    def test_quoted_attribution_is_not_treated_as_sentence_opening(self):
        self.assertEqual(voice.style_findings('\"Enough,\" she said.', voice.resolve_context("essay")), [])
        self.assertEqual(voice.style_findings('Done. \"Enough,\" she said.', voice.resolve_context("essay")), [])

    def test_protected_quotations_code_urls_and_link_targets_are_ignored(self):
        text = ('"i didn\'t send it btw"\n\n'
                "`i'm ready lmk`\n\n"
                "```text\ni'm gonna check btw\n```\n\n"
                "    i didn't check it\n\n"
                "Visit https://example.com/lmk and [Details](https://example.com/btw).")
        resolved = voice.resolve_context("cover-letter", preferences={"contractions": "avoid"})
        self.assertEqual(voice.style_findings(text, resolved), [])

    def test_precise_visible_mask_controls_checks_at_original_offsets(self):
        text = "I'm ready. SECRET idk lmk. I didn't lead it."
        visible = text.replace("SECRET idk lmk", " " * len("SECRET idk lmk"))
        resolved = voice.resolve_context("cover-letter", preferences={"contractions": "avoid"})
        before = copy.deepcopy(resolved)
        self.assertEqual([finding["quote"] for finding in voice.style_findings(text, resolved, visible=visible)], ["I'm", "didn't"])
        self.assertEqual(resolved, before)
        self.assertEqual(text, "I'm ready. SECRET idk lmk. I didn't lead it.")

    def test_findings_are_bounded_deduplicated_and_suggestions_only(self):
        text = "btw btw idk imo imho lmk np tbh rn omw brb afaik"
        findings = voice.style_findings(text, voice.resolve_context("email"))
        self.assertEqual(len(findings), 8)
        self.assertEqual(sum(finding["quote"] == "btw" for finding in findings), 1)
        for finding in findings:
            self.assertEqual(set(finding), {"kind", "quote", "reason"})
            self.assertIn("consider", finding["reason"])

    def test_incomplete_or_misaligned_inputs_fail_visibly(self):
        resolved = voice.resolve_context("email")
        for text, visible in ((None, None), ("Text", "shorter"), ("Text", [])):
            with self.subTest(text=text, visible=visible), self.assertRaises(ValueError):
                voice.style_findings(text, resolved, visible=visible)
        with self.assertRaises(ValueError):
            voice.style_findings("Text", {"destination": "email", "style": {}})


if __name__ == "__main__":
    unittest.main()
