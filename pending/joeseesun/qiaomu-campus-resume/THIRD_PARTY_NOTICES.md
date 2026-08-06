# Third-Party Notices

## Grill Me / Interview dialogue references

- Matt Pocock, `grill-me`: https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me — MIT License.
- Addy Osmani, `interview-me`: https://github.com/addyosmani/agent-skills/tree/main/skills/interview-me — MIT License.
- alirezarezvani, `grill-me`: https://github.com/alirezarezvani/claude-skills/tree/main/engineering/grill-me/skills/grill-me — MIT License; derived upstream from Matt Pocock.

This skill adopts high-level interview mechanisms—one question per turn, a correctable recommendation or hypothesis, depth-first branch resolution, periodic restatement and explicit confirmation. It does not redistribute their scripts, documentation, examples or branding.

## Kami

This skill's borderless editorial visual language is adapted from [tw93/kami](https://github.com/tw93/kami), inspected at commit `fbdb54f59b7f224db55322357e5739b9ef9687f4` on 2026-08-04.

Kami is licensed under the MIT License:

```text
MIT License

Copyright (c) 2026 Tw93

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Adapted mechanisms: parchment `#f5f4ed`, ink-blue `#1B365D`, serif-led hierarchy, A4 resume margins, restrained emphasis, editorial spacing, and quiet warm-gray separators. The implementation is rewritten for this skill's evidence-bound student-resume schema and forbids rounded boxes or card outlines.

## TsangerJinKai02

Kami documents that TsangerJinKai02 is a commercial font and requires an appropriate license for commercial use. This skill does not copy or redistribute the font files. It requires a user-installed W04 face, uses W05 for headings when available, and validates the resulting PDF font embedding.

## ResumeCollection

The optional `rc-*` reference presets were researched from [mmmlllnnn/ResumeCollection](https://github.com/mmmlllnnn/ResumeCollection), inspected at commit `56a18c26dd8d6ecd60df80b7dd8261b78dd70998` on 2026-08-04. The repository declares the MIT License with `Copyright (c) 2024 mln`.

The repository README describes the templates as collected from across the Internet. To avoid extending an unclear asset provenance chain, this skill does not copy or redistribute upstream DOCX files, preview images, photos, icons, fonts, or embedded media. It only records source links and reimplements general layout mechanisms as original single-column HTML/CSS under this skill's stricter ATS and no-border rules.

## Design and workflow references

The six-style system was researched against RenderCV, Reactive Resume, OpenResume, Jake's Resume, Awesome-CV, AltaCV, MIT CAPD resume guidance and Europass guidance. No source templates, font files, application code or private assets were copied into this package. Only general mechanisms—structured content separated from theme defaults, single-column text order, scenario-based template choice and deterministic PDF checks—were reimplemented locally. Source links and adoption/rejection notes are recorded in `reports/prior-art-research.md`.
