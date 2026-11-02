---
name: nl-humanizer-ai-smell-detector
description: 'Detect and remove "AI smell" from Dutch text with a diagnostic scoring system and human-centric rewriting. Use when: Audit Dutch marketing copy for robotic linguistic patterns; Convert formal Netherlands-Dutch into conversational Belgian-Dutch; Reduce AI detection scores through targeted linguistic rewriting.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: nl-humanizer-ai-smell-detector
compatibility: Compatible with SKILL.md-compatible agents including Claude Code and CLI tools.
---

# NL Humanizer AI Smell Detector

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/nl-humanizer-ai-smell-detector). Scripts, extension source, and templates from the original package are not in this folder.

## Deep Analysis and Humanization for Dutch Content

Most AI-generated Dutch text suffers from a distinct "AI smell"—it is overly formal, repetitive, and uses specific transition words that native speakers rarely use. This skill provides a deterministic diagnostic tool and a specialized rewriting engine to transform stiff, robotic Dutch into natural, conversational Belgian-Dutch (Vlaams) or standard Dutch.

## What it does

The skill operates in two phases: detection and transformation. First, it performs a linguistic audit of your text, identifying "tells" like excessive use of *uiteraard*, *desalniettemin*, passive constructions, and repetitive tricolon structures. It provides a transparent 0-5 "AI Smell Score." Second, it applies specific linguistic rules to break these patterns, shortening sentences, switching to active voice, and localizing the register without losing the original intent.

## Why use this skill

- **Transparency:** Unlike black-box AI detectors, this provides a clear count of specific linguistic signals.
- **Localization:** Moves beyond Google Translate-style Dutch toward a natural Belgian-Dutch register.
- **Consistency:** Ensures your brand voice doesn't sound like a generic LLM output.
- **Efficiency:** Automates the tedious process of stripping out robotic filler words and fixing sentence rhythms.

## When to use

- Audit Dutch marketing copy for robotic linguistic patterns
- Convert formal Netherlands-Dutch into conversational Belgian-Dutch
- Reduce AI detection scores through targeted linguistic rewriting
- Eliminate overused transition words like 'desalniettemin' and 'uiteraard'

## Known limitations

- Focuses on linguistic patterns rather than semantic truth.
- Best for business/web Dutch: creative literature may trigger false positives.

## Example

**Request**

Scan deze tekst op AI-geur en herschrijf het naar een natuurlijke toon: "Uiteraard is het belangrijk om te vermelden dat deze software, desalniettemin de kosten, tevens efficiënt is."

**Result**

Score: 4/5 (Zwaar AI-geurend)
Signalen: 'Uiteraard', 'desalniettemin', 'tevens', 'het is belangrijk om'.

Herschrijving:
Deze software is efficiënt, ook al hangt er een prijskaartje aan. We leggen je graag uit waarom dit een goede investering is.

## Questions

### What specific problems does the 'nl-humanizer-ai-smell-detector' solve?

This skill identifies and removes "AI smell"—linguistic patterns like overused transition words and passive voice typical of LLMs—and replaces them with natural, human-centric Dutch or Belgian-Dutch phrasing.

### How does the 0-5 'AI Smell Score' actually work?

The score is a diagnostic 0-5 rating based on a linguistic audit of 'tells' like repetitive structures and formal filler words, giving you a clear objective measure of how robotic your text appears.

### Can I choose between standard Dutch and Belgian-Dutch (Vlaams) for the rewritten text?

Yes, the tool is designed to localize text into both standard Dutch and the specific Belgian-Dutch (Vlaams) register, ensuring your content resonates with local audiences.

### What exactly is included in my purchase of this skill?

You receive the full diagnostic scoring system and the specialized rewriting engine, designed to integrate seamlessly with your existing AI agent workflows.

### How are updates and new versions of the detection logic handled?

The skill is updated periodically to stay ahead of evolving AI writing patterns, ensuring the detector remains effective against the latest versions of major LLMs.

### Is this skill compatible with my existing AI agent or platform?

This skill is a modular linguistic layer that can be integrated into most major AI platforms and custom agents that support Dutch language processing.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
