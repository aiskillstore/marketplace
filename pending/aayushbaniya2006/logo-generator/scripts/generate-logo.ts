import Replicate from "replicate";
import fs from "node:fs";
import path from "node:path";
import sharp from "sharp";

// Check for REPLICATE_API_TOKEN
if (!process.env.REPLICATE_API_TOKEN) {
  console.error(
    "❌ Error: REPLICATE_API_TOKEN is not set in environment variables.",
  );
  console.error(
    "Please set REPLICATE_API_TOKEN in your .env, .env.local, or .env.production file.",
  );
  process.exit(1);
}

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN,
});

async function pollPrediction(
  predictionId: string,
  interval: number = 2000,
): Promise<unknown> {
  let prediction = await replicate.predictions.get(predictionId);
  
  while (
    prediction.status !== "succeeded" &&
    prediction.status !== "failed" &&
    prediction.status !== "canceled"
  ) {
    await new Promise((resolve) => setTimeout(resolve, interval));
    prediction = await replicate.predictions.get(predictionId);
    
    if (prediction.status === "processing" || prediction.status === "starting") {
      process.stdout.write(".");
    }
  }
  
  if (prediction.status === "failed") {
    throw new Error(`Prediction failed: ${prediction.error || "Unknown error"}`);
  }
  
  if (prediction.status === "canceled") {
    throw new Error("Prediction was canceled");
  }
  
  return prediction.output;
}

async function main() {
  // Parse arguments
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error(
      "Usage: pnpm run script .claude/skills/logo-generator/scripts/generate-logo.ts <prompt> [company-name]",
    );
    process.exit(1);
  }

  const [prompt, companyName] = args;
  const finalPrompt = companyName ? `${prompt} for ${companyName}` : prompt;

  console.log(`🎨 Generating logo with prompt: "${finalPrompt}"...`);

  try {
    // Step 1: Generate logo
    console.log("📝 Step 1: Generating logo");
    const logoPrediction = await replicate.predictions.create({
      version: "67ed00e8999fecd32035074fa0f2e9a31ee03b57a8415e6a5e2f93a242ddd8d2",
      input: {
        width: 1024,
        height: 1024,
        prompt: finalPrompt,
        refine: "no_refiner",
        scheduler: "K_EULER",
        lora_scale: 0.6,
        num_outputs: 1,
        guidance_scale: 7.5,
        apply_watermark: true,
        high_noise_frac: 0.8,
        negative_prompt: "",
        prompt_strength: 0.8,
        num_inference_steps: 50,
      },
    });

    console.log(`   Prediction ID: ${logoPrediction.id}`);
    const logoOutput = await pollPrediction(logoPrediction.id);
    const logoUrl = Array.isArray(logoOutput) ? logoOutput[0] : logoOutput;
    const logoFileUrl =
      typeof logoUrl === "string"
        ? logoUrl
        : logoUrl.url?.() || logoUrl.toString();

    console.log(`\n✅ Logo generated: ${logoFileUrl}`);

    // Step 2: Remove background
    console.log("🔄 Step 2: Removing background");
    const transparentPrediction = await replicate.predictions.create({
      model: "bria/remove-background",
      input: {
        image: logoFileUrl,
        preserve_alpha: true,
        content_moderation: false,
        preserve_partial_alpha: true,
      },
    });

    console.log(`   Prediction ID: ${transparentPrediction.id}`);

    const transparentOutput = await pollPrediction(transparentPrediction.id);

    // Handle different output formats from Replicate
    let transparentUrl: string;
    if (typeof transparentOutput === "string") {
      transparentUrl = transparentOutput;
    } else if (transparentOutput && typeof transparentOutput === "object") {
      // Check if it's a FileOutput with url method
      if (
        "url" in transparentOutput &&
        typeof transparentOutput.url === "function"
      ) {
        transparentUrl = transparentOutput.url();
      } else if (
        "url" in transparentOutput &&
        typeof transparentOutput.url === "string"
      ) {
        transparentUrl = transparentOutput.url;
      } else {
        // Fallback: try to convert to string
        transparentUrl = String(transparentOutput);
      }
    } else {
      transparentUrl = String(transparentOutput);
    }

    console.log(`\n✅ Background removed: ${transparentUrl}`);

    // Step 3: Download image
    console.log("⬇️  Step 3: Downloading image...");

    // Check if it's a data URL (for small files <= 256kb)
    let imageBuffer: Buffer;
    if (transparentUrl.startsWith("data:")) {
      // Handle data URL
      const base64Data = transparentUrl.split(",")[1];
      imageBuffer = Buffer.from(base64Data, "base64");
    } else {
      // Download from URL
      const response = await fetch(transparentUrl);
      if (!response.ok) {
        throw new Error(`Failed to download image: ${response.statusText}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      imageBuffer = Buffer.from(arrayBuffer);
    }

    // Step 4: Trim transparent padding and add 5px padding
    console.log("✂️  Step 4: Trimming transparent edges and adding padding...");
    
    const processedImage = await sharp(imageBuffer)
      .trim({ threshold: 0 }) // Remove all transparent edges
      .extend({
        top: 5,
        bottom: 5,
        left: 5,
        right: 5,
        background: { r: 0, g: 0, b: 0, alpha: 0 }, // Transparent padding
      })
      .png({
        compressionLevel: 9, // Maximum compression (0-9)
        quality: 100, // Maximum quality
        palette: true, // Use palette if possible for smaller files
        effort: 7, // Compression effort (0-10, higher = better compression but slower)
      })
      .toBuffer();

    // Ensure directory exists
    const assetsDir = path.join(process.cwd(), "public", "assets");
    if (!fs.existsSync(assetsDir)) {
      fs.mkdirSync(assetsDir, { recursive: true });
    }

    // Save file
    const logoPath = path.join(assetsDir, "logo.png");
    fs.writeFileSync(logoPath, processedImage);

    console.log(`✅ Logo saved to: public/assets/logo.png`);
    console.log(`📊 File size: ${(processedImage.length / 1024).toFixed(2)} KB`);
  } catch (error) {
    console.error("❌ Failed to generate logo:", error);
    if (error instanceof Error) {
      console.error("Error details:", error.message);
    }
    process.exit(1);
  }
}

main();
