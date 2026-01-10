# Logo Generator Reference

## Configuration
Ensure `REPLICATE_API_TOKEN` is set in your environment (`.env`, `.env.local`, or `.env.production`).

## Models Used

### Logo Generation
- **Model**: `mejiabrayan/logoai:67ed00e8999fecd32035074fa0f2e9a31ee03b57a8415e6a5e2f93a242ddd8d2`
- **Output Size**: 1024x1024
- **Default Settings**:
  - `refine`: "no_refiner"
  - `scheduler`: "K_EULER"
  - `lora_scale`: 0.6
  - `guidance_scale`: 7.5
  - `num_inference_steps`: 50
  - `apply_watermark`: true

### Background Removal
- **Model**: `bria/remove-background`
- **Settings**:
  - `preserve_alpha`: true
  - `preserve_partial_alpha`: true
  - `content_moderation`: false

## Prompt Engineering Tips

For best logo results:
- Be specific about style: "Minimalistic", "Modern", "Vintage", etc.
- Include company/brand name in the prompt
- Specify color preferences if needed
- Mention any specific elements or symbols

## File Handling

The script uses data URLs for images <= 256KB to avoid unnecessary uploads. For larger files, it downloads from the URL provided by Replicate.

## Output

- **Location**: `public/assets/logo.png`
- **Format**: PNG with transparency
- **Size**: 1024x1024 pixels (configurable in script)

## Error Handling

The script will:
- Check for `REPLICATE_API_TOKEN` before running
- Handle API errors gracefully
- Provide clear error messages

