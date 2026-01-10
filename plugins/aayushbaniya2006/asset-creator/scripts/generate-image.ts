import fs from 'fs';
import path from 'path';
import OpenAI from 'openai';
import { z } from 'zod';

// Validation schema for arguments
const argsSchema = z.object({
  prompt: z.string().min(1, "Prompt is required"),
  filename: z.string().min(1, "Filename is required"),
  folder: z.string().default("assets/images"),
  style: z.enum(["natural", "vivid"]).default("vivid"),
});

async function main() {
  // Parse arguments
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error("Usage: tsx .claude/skills/asset-creator/scripts/generate-image.ts <prompt> <filename> [folder] [style]");
    process.exit(1);
  }

  const [prompt, filename, folder = "assets/images", style = "vivid"] = args;

  // Validate
  const validation = argsSchema.safeParse({ prompt, filename, folder, style });
  if (!validation.success) {
    console.error("Invalid arguments:", validation.error.format());
    process.exit(1);
  }

  const config = validation.data;

  // Initialize OpenAI
  if (!process.env.OPENAI_API_KEY) {
    console.error("Error: OPENAI_API_KEY is not set in environment variables.");
    process.exit(1);
  }

  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });

  console.log(`🎨 Generating image for: "${config.prompt}"...`);

  try {
    const response = await openai.images.generate({
      model: "dall-e-3",
      prompt: `${config.prompt}. Minimalist, flat, modern SaaS style, high quality, transparent background if possible (though DALL-E 3 outputs jpg/png often, we request white background for easy removal or specific style).`,
      n: 1,
      size: "1024x1024",
      quality: "hd",
      style: config.style as "vivid" | "natural",
      response_format: "b64_json",
    });

    const image = response.data?.[0];
    if (!image?.b64_json) {
      throw new Error("No image data received.");
    }

    // Ensure directory exists
    const publicDir = path.join(process.cwd(), 'public', config.folder);
    if (!fs.existsSync(publicDir)) {
      fs.mkdirSync(publicDir, { recursive: true });
    }

    // Save file
    const fullPath = path.join(publicDir, config.filename.endsWith('.png') ? config.filename : `${config.filename}.png`);
    const buffer = Buffer.from(image.b64_json, 'base64');
    fs.writeFileSync(fullPath, buffer);

    console.log(`✅ Image saved to: public/${config.folder}/${path.basename(fullPath)}`);
    
  } catch (error) {
    console.error("Failed to generate image:", error);
    process.exit(1);
  }
}

main();

