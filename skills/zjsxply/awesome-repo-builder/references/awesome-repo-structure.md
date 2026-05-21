# Awesome Repository Structure

Use this as the structural model for generated awesome repositories.

## Root Files

- `README.md`: primary artifact. Contains a centered header, badges, a short topic definition, contents, categorized sections, optional templates, related awesome lists, and contributing section.
- `CONTRIBUTING.md`: concise criteria, exclusions, contribution steps, update guidance, and template contribution guidance.
- `AGENTS.md`: repository-specific instructions for AI agents. Describes what the repo is, README conventions, what belongs, what does not belong, template guidance, and verification checks.
- `LICENSE`: default to CC0 1.0 Universal unless the user asks for another license.
- `.gitignore`: small repository housekeeping file.
- `verify_urls.py`: standalone URL checker for links in `README.md`.

## Directories

- `assets/`: optional visual assets such as a banner image. Do not create a fake banner if none is provided.
- `templates/`: reusable Markdown templates relevant to the topic. Include `AGENTS.md`, `PLAN.md`, `IMPLEMENT.md`, and `CHECKLIST.md` by default.

## README Pattern

1. Centered title block:
   - optional banner image
   - `<h1>Awesome ...</h1>`
   - one-sentence tagline
   - awesome badge, license badge, and optional GitHub repository badges
2. Short definition paragraph explaining the topic.
3. `Contents` with links to top-level sections and subsections.
4. Curated sections organized by problem, use case, or resource role, not by vendor.
5. Resource entries formatted as a Markdown link plus a concise note explaining why the resource matters.
6. `Templates`, when the topic naturally has reusable artifact templates.
7. `Related Awesome Lists`, when relevant.
8. `Contributing`.

## Contribution Pattern

Keep contribution rules short:

- Define what belongs.
- Define what does not belong.
- Tell contributors to add resources to the appropriate README section.
- Use a simple entry format with a short explanatory note.
- Allow updates for dead links or better successors.
- Allow template contributions when the repo includes reusable templates.

## Agent Instruction Pattern

The generated `AGENTS.md` should tell AI agents:

- The primary artifact is `README.md`.
- Keep all content in the repository's chosen language.
- Every resource entry needs a note explaining why it is included.
- Organize sections by the problem being solved or the resource role rather than vendor or model.
- Verify reachable URLs and Markdown rendering before finishing.

## Avoid Adding Unrequested Scope

Do not invent advanced governance unless requested. The default scaffold should not include batch PR review automation, scheduled link cleanup, complex ranking rules, or a full maintenance program.
