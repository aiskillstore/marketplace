---
name: kv-design
description: Generate professional Key Visual (KV) design proposals and images; use when you have a slogan/copy and a marketing scenario but need a clear visual direction and a ready-to-generate image prompt.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- **Brand marketing campaigns** where you need a hero visual that matches brand tone and supports headline/copy overlay.
- **Event promotions** (e.g., seasonal sales, product launches) requiring a strong focal point and clear layout guidance.
- **Website/app banners** that must fit specific aspect ratios and maintain readable negative space for text.
- **Social media hero creatives** where you need fast iteration from vague requirements to a consistent visual direction.
- **Pitching multiple design directions** to stakeholders (e.g., 2–3 KV concepts with distinct styles and compositions).

## Key Features

- Converts vague KV requirements into **professional design directions** (visual focus, layout suggestions, style details).
- Produces **image-generation-ready prompts** optimized for KV composition and marketing readability.
- Encourages **negative space planning** for copy placement and **subject prominence** for attention capture.
- Supports common KV constraints: **scenario-driven style**, **main color tone**, and **size/ratio intent**.

## Dependencies

- Python **3.10+**
- Required Python packages:
  - `zhipuai`
  - `requests`
- ZhipuAI API access via environment variable:
  - `ZHIPUAI_API_KEY` (required)

## Example Usage

### 1) Collect KV Requirements

Prepare the following information:

- **Project/Brand Name**
- **Core Slogan/Copy** (the “soul” of the KV)
- **Usage Scenario** (e.g., New Product Launch, Black Friday Sale, Website Banner)
- **Style Preference** (e.g., 3D render, minimalist, illustration)
- **Main Color Tone**
- **Size/Ratio Requirements** (even if the script defaults to one, capture the user’s intent)

### 2) Analyze the Design Direction

Use the **KV Design Analysis Prompts** in:  
`references/design_prompts.md`

Process:

1. Open **KV Design Analysis Prompts**.
2. Fill in the collected information into **`[KV Design Requirements]`**.
3. Generate:
   - **Visual Focus**
   - **Layout Suggestions**
   - **Style Details**

### 3) Generate the KV Image Prompt

Use the **KV Image Prompt Generation Prompts** in:  
`references/design_prompts.md`

Process:

1. Open **KV Image Prompt Generation Prompts**.
2. Fill in:
   - **`[Basic Requirements]`**
   - **`[Design Proposal]`** (from Step 2)
3. Generate the final optimized image prompt.

### 4) Generate the KV Image (Runnable)

1. Ensure the API key is set:

   ```bash
   export ZHIPUAI_API_KEY="YOUR_KEY_HERE"
   ```

2. Run the script with the generated prompt:

   ```bash
   python scripts/generate_kv.py "<generated_prompt>"
   ```

3. After completion, return the generated image file path to the user.

## Implementation Details

- **Two-stage prompting workflow**
  1. **Design analysis stage**: transforms requirements into actionable design guidance (focus, layout, style).
  2. **Prompt generation stage**: converts the design guidance into a production-ready image prompt.

- **KV composition constraints**
  - **Negative space**: reserve clean areas for headline/subcopy overlays; avoid overly busy backgrounds.
  - **Subject prominence**: ensure the primary subject (product/concept) is visually dominant and attention-grabbing.

- **Parameters to capture early**
  - **Scenario** drives composition and tone (e.g., “sale” vs. “premium launch”).
  - **Style preference** constrains rendering approach (3D/illustration/minimal).
  - **Main color tone** ensures brand consistency.
  - **Aspect ratio/size intent** informs layout planning even if generation defaults to a preset.