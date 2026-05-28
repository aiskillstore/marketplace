---
name: poster-designer
description: Generate professional poster design concepts and optimized image-generation prompts, then automatically run a drawing script to produce the final poster image when a user needs a poster.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Poster Designer (Auto-Gen Edition)

This skill turns a user’s poster requirements into (1) structured design elements, (2) an optimized image-generation prompt, and (3) an automatically generated poster image by running a Python script.

It relies on the prompt templates in: [`references/design_prompts.md`](references/design_prompts.md)

## When to Use

Use this skill when the user wants to:

1. Design a professional poster for an academic event, conference, or research announcement.
2. Create a marketing poster for a product launch, promotion, or brand campaign.
3. Generate a holiday/festival poster concept and produce the final image automatically.
4. Produce multiple poster concepts quickly by changing style, palette, or layout constraints.
5. Convert a text brief (title/body/call-to-action) into a visually consistent poster image.

## Key Features

- Requirements intake with missing-field detection and follow-up questions.
- Design element analysis using a dedicated “Design Analysis Prompt”.
- High-quality image prompt synthesis using an “Image Prompt Generation Prompt”.
- Automatic image generation by executing a Python script with the generated prompt.
- Style consistency enforcement (the prompt must match the requested style).
- Optional asset placement guidance (logo/QR code) embedded into the prompt.

## Dependencies

- Python 3.10+  
- Python package: `zhipuai` (install via `pip install zhipuai`)
- Environment variable: `ZHIPUAI_API_KEY` (required for image generation)
- Prompt templates: `references/design_prompts.md`
- Script: `scripts/generate_image.py`

## Example Usage

### 1) Collect requirements (ask if missing)

**User input example**
- Scenario/type: Product promotion
- Style: Cyberpunk illustration
- Title (optional): “NEON SALE”
- Body text: “Up to 50% off smart wearables. This weekend only.”
- Primary color: Neon magenta + deep blue
- Layout preference (optional): Left-right split, bold title on left
- Assets (optional): Brand logo top-left, QR code bottom-right

If any of the above fields are missing, ask targeted questions until you have enough to proceed.

### 2) Analyze design elements (from `references/design_prompts.md`)

Use the **Design Analysis Prompt** in `references/design_prompts.md`:

- Fill the collected info into **`[Poster Design Requirements]`**
- Generate:
  - **Mandatory Modules**
  - **Recommended Layout**
  - **Style Details**

### 3) Generate the final image prompt (from `references/design_prompts.md`)

Use the **Image Prompt Generation Prompt** in `references/design_prompts.md`:

- Fill user info into **`[Basic Requirements]`**
- Fill Step 2 output into **`[Design Elements]`**
- Produce the optimized image-generation prompt string (the “generated_prompt”).

### 4) Run the script to generate the image (must be attempted)

1. Ensure `ZHIPUAI_API_KEY` is set.

   **Windows PowerShell**
   ```powershell
   $env:ZHIPUAI_API_KEY="your_key"
   ```

2. Run:
   ```bash
   python scripts/generate_image.py "<generated_prompt>"
   ```

3. On success, the script prints an output image path. Inform the user that the image is generated and provide the path.

4. If the script fails (e.g., missing key), clearly instruct the user to set `ZHIPUAI_API_KEY` and rerun the command.

## Implementation Details

### Workflow (must follow)

1. **Requirements Collection**
   - Required: scenario/type, style, body text, primary color
   - Optional: title, layout preference, assets (logo/QR code)
   - If any required field is missing, ask follow-up questions before continuing.

2. **Design Analysis**
   - Use `references/design_prompts.md` → **Design Analysis Prompt**
   - Populate `[Poster Design Requirements]`
   - Output must include:
     - Mandatory Modules (e.g., title block, body copy block, CTA, brand area)
     - Recommended Layout (e.g., grid, symmetry, left-right split)
     - Style Details (e.g., typography, texture, lighting, composition cues)

3. **Image Prompt Generation**
   - Use `references/design_prompts.md` → **Image Prompt Generation Prompt**
   - Combine:
     - `[Basic Requirements]` (user brief)
     - `[Design Elements]` (analysis output)
   - Enforce **style consistency**: the final prompt must strictly match the requested style and palette.

4. **Asset Placement Rules**
   - If the user provides a logo/QR code, the prompt must explicitly specify placement (e.g., “logo at top-left”, “QR code at bottom-right”) and reserve visual space accordingly.

5. **Automatic Execution Requirement**
   - After producing the final prompt, you **must** attempt to run `scripts/generate_image.py` with that prompt (not only return the prompt).
   - If execution cannot proceed due to missing configuration (e.g., `ZHIPUAI_API_KEY`), return actionable setup instructions and the exact command to rerun.