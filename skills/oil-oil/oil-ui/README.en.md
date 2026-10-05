[中文](README.md) · English

<p align="center">
  <img src="./assets/readme/hero.webp" width="100%" alt="oil-ui: push AI UI design to its limits. A person pins a yellow pushpin to the middle of three previews in different styles">
</p>

<p align="center">
  <a href="https://ui.oiloil.org"><img src="./assets/readme/showcase.webp" width="100%" alt="Gallery highlights: an English learning app, a music year in review, hardware and component library websites, a project management tool, a ride-hailing app, a voice assistant, a checkout flow, and a film camera"></a>
</p>

See more designs at [ui.oiloil.org](https://ui.oiloil.org).

## Method

1. **Identify the category and study its best examples.** Name the product category, find two or three peers with distinctive styles, and examine their choices and reasoning. Decide what to keep and what to change.
2. **Set the tone first.** Use the subject, audience, and brand voice to set five scales: energy, polish, density, visual weight, and seriousness. Turn words like “premium” or “clean” into visible choices: type, spacing, and how much of the page uses color.
3. **Start with something concrete.** Give each direction a specific starting point: a material in a setting, a scene, a character, or the visual language of another field. Draw from the product itself rather than adjectives like “minimal” or “bold.”
4. **Decide what the opening screen is for.** For browsing, shopping, or getting work done, lead with the content itself. For pages meant to persuade, choose the opening layout, wireframe it, then write the copy. Each direction needs a different layout; use a left/right split at most once per round.
5. **Check that the directions differ.** Any two directions may share at most one of four things: layout, typography, color, and key imagery. Place the previews side by side and squint at the opening screens. If their light and dark shapes look too similar, choose a different layout.
6. **Create a memorable moment.** Focus on one or two details: the response to a tap, a successful payment, AI at work, or a 404 page. Keep the rest quiet.
7. **You decide what looks right.** Compare previews on one page, choose a direction, and say exactly what you like and dislike.
8. **Judge the actual screens.** Open the page at desktop and mobile sizes and check screenshots. An independent reviewer who has not seen the work in progress can review it. Finish by simplifying: give each page one focal point and remove unnecessary copy, repeated lines, and extra containers.

Interactions, states, layout, existing project redesigns, and effects such as light trails and dot patterns are covered in [Oil UI Pro](https://ui.oiloil.org/en/pro/).

## Installation

Send this to an agent that can install skills:

```text
Install this skill for me: https://github.com/oil-oil/oil-ui
```

Or install it from your terminal:

```bash
npx skills add oil-oil/oil-ui
```

The design workflow is ready to use after installation, with no extra configuration or other skills. Installing with the command requires Node.js 18 or later. If you already have Oil UI Pro, you don't need Oil UI (open source); installing both makes them compete for the same requests.

Using this skill triggers a version check, at most once every 10 minutes. If the server takes longer than 2 seconds, the check is skipped so it never slows down your task. Failed checks retry later when you use the skill again. The check only reads the public version list on ui.oiloil.org and does not upload project content. Offline checks cannot discover new versions, so they produce no reminder.

Automatic updates need Python 3 and Node.js 18 or later. When a new version is found, the skill tries to update itself. If dependencies are missing, the agent ends its reply with recovery steps and a command containing the current installation's absolute path: `npx github:oil-oil/oil-cli update oil-ui --path "<installation path>"`. Network errors stay silent and retry later. Set `OIL_NO_AUTO_UPDATE=1` for reminders without automatic updates, or `OIL_NO_UPDATE_CHECK=1` to disable checks entirely.

Python 3 can run as `python3` or `python`, or as `py -3` on Windows. If Python 3 is missing, the agent reminds you once and continues the design task.

## Usage

Tell your agent what you need, for example:

- “Use oil-ui to explore a few design directions for this course booking product and build pages I can preview.”
- “Create three designs with different typography, colors, and compositions. Put them on a comparison page so I can choose.”
- “Polish this page using the project’s existing design guidelines.”
- “Review this homepage and explain what to change and how. Leave the files untouched.”
- “Recreate this page from the screenshot and add a mobile layout too.”

Share any brand assets, screenshots, or existing project you have. It can start without references and only asks questions when the deliverable is unclear.

## Built-in style comparison page

<p align="center">
  <img src="./assets/readme/proof-mona-lisa.webp" width="100%" alt="Style comparison page: three directions for the same Mona Lisa exhibition page, titled Thirty Centimeters, Extra! 1911, and Sfumato">
</p>

Compare designs side by side as HTML files, images, or running development pages. Put the current version first as a baseline. Switch between desktop and mobile sizes, open previews at actual size, and browse with arrow keys. Click “Select” on your choice, then paste the copied sentence into your agent to continue.

## Open-source and full versions

<p align="center">
  <img src="./assets/readme/proof-van-gogh.webp" width="100%" alt="Full version style comparison page: three directions for a Van Gogh exhibition page, titled To Theo, Brushstrokes, and East Window">
</p>

| | Oil UI (open source) | Oil UI Pro |
| --- | :---: | :---: |
| Set the tone, explore distinct directions, define layouts first, and check their differences | ✓ | ✓ |
| Style comparison page | ✓ | ✓ |
| Visual hierarchy, typography, color, and spacing | ✓ | ✓ |
| Memorable moments and scroll storytelling (parallax and continuous shots) | ✓ | ✓ |
| Imagery, assets, and motion | ✓ | ✓ |
| Screenshot recreation, icon library selection, and sample data | ✓ | ✓ |
| Review polished interfaces against the project’s design guidelines | ✓ | ✓ |
| Independent review | One round per stage | Aim for 9/10, with up to three rounds of review and revision |
| Check for overlapping directions and have the reviewer complete real tasks | | ✓ |
| Fix common first-draft issues, check AI design defaults, refine details, and simplify | | ✓ |
| Dashboard and tool layouts, with a consistent style throughout the page | | ✓ |
| Interactions, states, layout, and responsive behavior | | ✓ |
| Polish a single component to the extreme: a visual anchor, one chosen sketch, every state, a tactile main interaction, and review rounds | | ✓ |
| SVG and shader effects: light trails, dot patterns, and flowing gradients | | ✓ |
| In existing projects, first tell apart a UI refresh, a flow fix, and a new feature | ✓ | ✓ |
| Existing project methods: check whether the current design system deserves to be the standard, offer options by how far they depart from it, walk the real flow to find root causes, and propose options that solve the task in genuinely different ways | | ✓ |

Oil UI Pro costs $9.99: a one-time purchase with lifetime updates. Purchase it at [ui.oiloil.org/pro](https://ui.oiloil.org/en/pro/).

## Use with

- [draw-ui](https://github.com/oil-oil/draw-ui): Generate design images first, choose one, then build from it. Try this when code-based iterations keep falling short and your agent can generate images.
- [oil-motion](https://github.com/oil-oil/oil-motion): Turn generated videos or frame sequences into web animation controlled by scrolling or dragging, such as product teardowns or camera fly-throughs. Use it for a striking opening animation.

## License

[MIT](LICENSE)
