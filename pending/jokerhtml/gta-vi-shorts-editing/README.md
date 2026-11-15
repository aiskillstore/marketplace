# GTA 6 Shorts Editing Skill

Free Claude Code skill for editing GTA 6 (Grand Theft Auto VI) YouTube Shorts to a professional standard: fact-checked scripts, voiceover, exact subtitles, colour grade, thumbnails, and an upload checklist — built on the real workflow behind three GTA VI news Shorts.

## Install

```bash
npx skills add JokerHTML/gta-vi-shorts-editing
```

Manual copy fallback: copy this folder into `.claude/skills/` in your project, or into `~/.claude/skills/` to use it in every project.

Note: the GitHub repo must be named `gta-vi-shorts-editing` so the skill name matches the directory, as the Agent Skills frontmatter rule requires.

## What is this?

This skill is the working method behind the Joker Gaming GTA 6 news Shorts: short, premium, zero-fake English Shorts built from official Rockstar material only. It covers the full path from topic research to a scheduled upload: fact ledger, ChatGPT script and SEO, voiceover, subtitles, stills and motion, cards, mix, render, grade, loudness, builder QC, red-team gate, and scheduling.

It teaches you to edit your own GTA 6 gameplay — not to re-upload someone else's footage, not to auto-cut with one click, and not to chase leak screenshots. Every viewer-facing word traces back to a fact ledger row.

## Who is this for?

An editor or agent making GTA 6 Shorts who wants a repeatable, checkable method instead of guessing. It assumes you have ffmpeg, Python, Node with Remotion, Kokoro TTS, and faster-whisper available (see Tools in SKILL.md). It does not contain any Rockstar footage, logo files, trailer files, or music. You supply your own official source material.

## How to edit GTA 6 Shorts with this skill

Invoke this skill when you are planning, scripting, editing, checking, or uploading a GTA 6 Short.

Quickstart:

1. Research the topic and write a fact ledger with a banned list.
2. Get the script, SEO, and thumbnail brief from ChatGPT, then hand-count the script to 90-105 words.
3. Run the M20 pool gate before any voiceover work.
4. Synthesise Kokoro VO, check it with faster-whisper, cut stills and motion from the measured active picture, and build the mix.
5. Render in Remotion, apply the grade plus the M36 colour fix plus loudnorm, run builder QC, and pass the red-team gate before scheduling.

The full method — all 36 rules, verified commands, upload checklist, thumbnail method, and red-team rubric — is in `SKILL.md`.

## Proof

Three Shorts were built with this method on November 15, 2026, on the Joker Gaming channel, and all three were scheduled the same day. No earnings or subscriber counts are claimed here.

### Verified views — channel proof (checked Nov 15, 2026, evening PKT, on the public YouTube pages)

The channel's five most-viewed Shorts, all built with the same editing system:

| Short | Views | Likes | Published |
|---|---|---|---|
| [SPOTTED: Jason's GTA 6 Launch Trailer Shirt Names a Base From the 1997 Game](https://youtube.com/shorts/8uBbUEWNCag) | 1,140 | 7 | Nov 10, 2026 |
| [NEW: How Big Is GTA VI's Map? Rockstar Already Answered It](https://youtube.com/shorts/C4Sr6Emcxiw) | 1,028 | 9 | Nov 10, 2026 |
| [NEW: GTA VI's Weapon Wheel Is Back — But You Can't Carry Everything](https://youtube.com/shorts/DP4sJFn5ql4) | 1,010 | 8 | Nov 10, 2026 |
| [PlayStation AND Xbox Agree: GTA 6 Broke Both Records](https://youtube.com/shorts/aoM0939hZ7s) | 874 | 5 | Nov 12, 2026 |
| [Your 13-Year-Old Xbox Plays GTA VI on Launch Day](https://youtube.com/shorts/_RcbKgTRgTA) | 804 | 12 | Nov 12, 2026 |

Channel total: **10,013 public views across the 37 most recent Shorts** on [@jokergaminglive](https://www.youtube.com/@jokergaminglive) (same check). Watch hours are not public — no watch-hours figure is claimed here. No other view numbers are used in this README.

- GTA VI Built a Whole Cartoon Inside the Game - https://youtube.com/shorts/OC5KczRGYSQ - 40.00s - 96/100 + 60/60 PASS
- New Zealand Plays GTA VI First. Here's Your Unlock Time - https://youtube.com/shorts/aF6RgIg_mHI - 45.9s - 90/100 + 53/60 PRE-FIX verdict, a FAIL (MAJOR-1 colour). The shipped file is the MAJOR-fixed file, technically re-verified, expected approx 94/100, not a measured re-score
- Burger Shot Is Real Now. You Can Eat It in Florida - https://youtube.com/shorts/74I0MXC-aIQ - 40.8s - 97/100 + 57/60 PASS, per RUN-NOTES.md only; no standalone red-team report file exists for this video

Full worked examples with scripts, SEO, shot plans, and scores are in `examples/`.

## Free vs Pro

| Free (this repo) | Pro pack ($49 one-time, Gumroad) |
| Complete SKILL.md: all 36 rules, full workflow, verified commands, upload checklist, thumbnail method, red-team rubric | Remotion project template with the colour-safe pipeline (M36 fix script included) |
| 3 worked examples with full scripts, SEO, shot plans, scores | Colour LUT (.cube) + grade pipeline for the locked v3 recipe |
| Tools table with exact versions + gotchas | Thumbnail prompt pack (7 adapted prompts + layout templates + safe-zone guide) |
| Rockstar IP + honesty rules | Subtitle style presets (ASS files, both documented caption styles) |
| | Full M1-M36 + advanced checklists (printable) |
| | 3 worked-example project breakdowns with frame-accurate timelines |
| | Launch-week updates included |

Get the Pro Pack here: https://needcraftco.gumroad.com/l/zqnhg — $49 one-time.

## FAQ

**Is this official?**
No. This skill is unofficial and independent. It is not affiliated with, endorsed by, or sponsored by Rockstar Games or Take-Two Interactive. See the Disclaimer below.

**Does it contain any GTA 6 footage, logos, or music?**
No. It contains techniques, commands, and checklists only. You supply your own official source material.

**Which platforms does GTA 6 launch on?**
PlayStation 5 and Xbox Series X|S on November 19, 2026. There is no PC version announced and no PC date — this skill does not claim one, and its capture guidance is console-first.

**Will this make my Shorts go viral or earn money?**
No promise is made about views, earnings, subscribers, or any result. The skill documents a workflow that was used on real videos. Your results depend on your material, your topics, and your execution.

**Can I use it with agents other than Claude Code?**
The skill is written to the Agent Skills standard (`SKILL.md` + frontmatter), so any agent that loads skills can use it. The install command targets Claude Code; the manual copy fallback works anywhere.

## Repo layout

```text
gta-vi-shorts-editing/
  SKILL.md            The skill: workflow, all 36 rules, commands, rubric, thumbnail method, tools
  README.md           This file
  LICENSE             MIT licence
  examples/
    v1-macca-friends.md
    v2-unlock-times.md
    v3-burger-shot.md
```

## License

MIT. See `LICENSE`. Copyright 2026 Muhammad Saad Ranjha.

## Disclaimer

This skill is unofficial and independent. It is not affiliated with, endorsed by, or sponsored by Rockstar Games or Take-Two Interactive. It contains techniques, commands, and checklists only. It contains no Rockstar footage, trailer files, logo files, game music, or leaked material. Monetised GTA gameplay videos are common in practice, but that practice is tolerated, not licensed, and Take-Two can request removal at any time.
