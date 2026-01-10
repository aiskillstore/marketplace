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
    throw new Error(
      `Prediction failed: ${prediction.error || "Unknown error"}`,
    );
  }

  if (prediction.status === "canceled") {
    throw new Error("Prediction was canceled");
  }

  return prediction.output;
}

function generateFilename(prompt: string): string {
  return prompt
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .substring(0, 50);
}

function enhancePrompt(
  basePrompt: string,
  assetType: "hero" | "feature" | "transformation" | "foreground" | "other",
  needsTransparent: boolean = false,
): string {
  // Theme-inspired enhancements based on globals.css
  const themeElements = [
    "modern minimalist design",
    "subtle gradients",
    "soft shadows",
    "rounded corners",
    "clean lines",
  ];

  // Background patterns
  const backgroundPatterns = [
    "subtle dot pattern",
    "geometric grid pattern",
    "triangle pattern",
    "star pattern",
    "gradient background",
    "radial gradient",
    "linear gradient",
  ];

  // UI elements
  const uiElements = [
    "modern UI elements",
    "playful interface components",
    "smooth animations",
    "glassmorphism effects",
    "neomorphic design elements",
  ];

  // Decorative elements for larger images
  const decorativeElements = [
    "subtle stars",
    "geometric dots",
    "elegant lines",
    "floating shapes",
    "particle effects",
  ];

  let enhancedPrompt = basePrompt;

  // Add UI style
  enhancedPrompt += `, ${themeElements.join(", ")}`;

  // Add background preferences
  if (!needsTransparent) {
    const randomPattern =
      backgroundPatterns[Math.floor(Math.random() * backgroundPatterns.length)];
    enhancedPrompt += `, ${randomPattern}`;
  } else {
    enhancedPrompt += ", transparent background";
  }

  // Add UI elements
  if (assetType === "hero" || assetType === "feature") {
    enhancedPrompt += `, ${uiElements.join(", ")}`;
  }

  // Add decorative elements for larger images
  if (assetType === "hero" || assetType === "transformation") {
    const randomDecorative =
      decorativeElements[Math.floor(Math.random() * decorativeElements.length)];
    enhancedPrompt += `, ${randomDecorative}`;
  }

  // Add style modifiers
  enhancedPrompt +=
    ", professional, high quality, subtle, elegant, contemporary design";

  return enhancedPrompt;
}

async function getImageDimensions(
  imagePath: string,
): Promise<{ width: number; height: number } | null> {
  try {
    if (!fs.existsSync(imagePath)) {
      return null;
    }
    const metadata = await sharp(imagePath).metadata();
    return {
      width: metadata.width || 1920,
      height: metadata.height || 1080,
    };
  } catch {
    return null;
  }
}

function calculateAspectRatio(width: number, height: number): string {
  const ratio = width / height;
  const commonRatios: { [key: number]: string } = {
    1.0: "1:1",
    1.33: "4:3",
    1.5: "3:2",
    1.77: "16:9",
    2.33: "21:9",
    0.56: "9:16",
    0.75: "3:4",
  };

  // Find closest match
  let closestRatio = "16:9";
  let minDiff = Infinity;

  for (const [ratioValue, ratioString] of Object.entries(commonRatios)) {
    const diff = Math.abs(ratio - parseFloat(ratioValue));
    if (diff < minDiff) {
      minDiff = diff;
      closestRatio = ratioString;
    }
  }

  return closestRatio;
}

async function main() {
  // Parse arguments
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error(
      "Usage: pnpm run script .claude/skills/generate-assets/scripts/generate-asset.ts <prompt> [aspect-ratio] [filename] [folder] [asset-type] [transparent]",
    );
    console.error(
      "Example: pnpm run script .claude/skills/generate-assets/scripts/generate-asset.ts \"modern dashboard\" \"16:9\" \"hero-dashboard\" \"hero\" \"hero\" false",
    );
    process.exit(1);
  }

  const [
    prompt,
    aspectRatio,
    filename,
    folder = "",
    assetType = "other",
    transparent = "false",
  ] = args;

  const needsTransparent = transparent === "true";
  const finalFilename = filename || generateFilename(prompt);

  // Check if file exists to get dimensions
  const imagesDir = path.join(process.cwd(), "public", "assets", "images");
  const targetDir = folder ? path.join(imagesDir, folder) : imagesDir;
  const existingFilePath = path.join(targetDir, `${finalFilename}.webp`);

  let finalAspectRatio = aspectRatio || "16:9";
  let imageWidth = 1920;
  let imageHeight = 1080;

  const existingDimensions = await getImageDimensions(existingFilePath);
  if (existingDimensions) {
    console.log(
      `📏 Found existing image: ${existingDimensions.width}x${existingDimensions.height}`,
    );
    finalAspectRatio = calculateAspectRatio(
      existingDimensions.width,
      existingDimensions.height,
    );
    imageWidth = existingDimensions.width;
    imageHeight = existingDimensions.height;
    console.log(`   Using aspect ratio: ${finalAspectRatio}`);
  } else if (!aspectRatio) {
    // Default aspect ratios based on asset type
    const defaultRatios: { [key: string]: string } = {
      hero: "16:9",
      feature: "1:1",
      transformation: "16:9",
      foreground: "1:1",
      other: "16:9",
    };
    finalAspectRatio = defaultRatios[assetType] || "16:9";
  }

  // Enhance prompt
  const enhancedPrompt = enhancePrompt(
    prompt,
    assetType as "hero" | "feature" | "transformation" | "foreground" | "other",
    needsTransparent,
  );

  console.log(`🎨 Generating asset with enhanced prompt...`);
  console.log(`   Original: "${prompt}"`);
  console.log(`   Enhanced: "${enhancedPrompt}"`);
  console.log(`   Aspect ratio: ${finalAspectRatio}`);
  console.log(`   Size: ${imageWidth}x${imageHeight}`);
  console.log(`   Filename: ${finalFilename}.webp`);
  console.log(`   Transparent: ${needsTransparent}`);

  try {
    // Step 1: Generate image
    console.log("📝 Step 1: Generating image");
    const prediction = await replicate.predictions.create({
      model: "black-forest-labs/flux-1.1-pro",
      input: {
        prompt: enhancedPrompt,
        aspect_ratio: finalAspectRatio,
        output_format: "webp",
        output_quality: 80,
        safety_tolerance: 2,
        prompt_upsampling: true,
      },
    });

    console.log(`   Prediction ID: ${prediction.id}`);
    const output = await pollPrediction(prediction.id);

    // Handle different output formats from Replicate
    let imageUrl: string;
    if (typeof output === "string") {
      imageUrl = output;
    } else if (output && typeof output === "object") {
      if ("url" in output && typeof output.url === "function") {
        imageUrl = output.url();
      } else if ("url" in output && typeof output.url === "string") {
        imageUrl = output.url;
      } else {
        imageUrl = String(output);
      }
    } else {
      imageUrl = String(output);
    }

    console.log(`\n✅ Image generated: ${imageUrl}`);

    // Step 2: Download image
    console.log("⬇️  Step 2: Downloading image...");

    let imageBuffer: Buffer;
    if (imageUrl.startsWith("data:")) {
      const base64Data = imageUrl.split(",")[1];
      imageBuffer = Buffer.from(base64Data, "base64");
    } else {
      const response = await fetch(imageUrl);
      if (!response.ok) {
        throw new Error(`Failed to download image: ${response.statusText}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      imageBuffer = Buffer.from(arrayBuffer);
    }

    // Step 3: Remove background if needed (for smaller/foreground assets)
    if (needsTransparent || assetType === "foreground") {
      console.log("🔄 Step 3: Removing background...");
      const transparentPrediction = await replicate.predictions.create({
        model: "bria/remove-background",
        input: {
          image: imageUrl,
          preserve_alpha: true,
          content_moderation: false,
          preserve_partial_alpha: true,
        },
      });

      console.log(`   Prediction ID: ${transparentPrediction.id}`);
      const transparentOutput = await pollPrediction(transparentPrediction.id);

      let transparentUrl: string;
      if (typeof transparentOutput === "string") {
        transparentUrl = transparentOutput;
      } else if (transparentOutput && typeof transparentOutput === "object") {
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
          transparentUrl = String(transparentOutput);
        }
      } else {
        transparentUrl = String(transparentOutput);
      }

      // Download transparent version
      if (transparentUrl.startsWith("data:")) {
        const base64Data = transparentUrl.split(",")[1];
        imageBuffer = Buffer.from(base64Data, "base64");
      } else {
        const response = await fetch(transparentUrl);
        if (!response.ok) {
          throw new Error(`Failed to download transparent image: ${response.statusText}`);
        }
        const arrayBuffer = await response.arrayBuffer();
        imageBuffer = Buffer.from(arrayBuffer);
      }
      console.log(`✅ Background removed`);
    }

    // Step 4: Optimize with sharp
    console.log("⚡ Step 4: Optimizing image...");

    let sharpProcessor = sharp(imageBuffer);
    
    // Only resize if dimensions are specified and different from original
    const metadata = await sharp(imageBuffer).metadata();
    if (metadata.width && metadata.height) {
      if (metadata.width !== imageWidth || metadata.height !== imageHeight) {
        sharpProcessor = sharpProcessor.resize(imageWidth, imageHeight, {
          fit: "contain",
          background: needsTransparent ? { r: 0, g: 0, b: 0, alpha: 0 } : undefined,
        });
      }
    }

    const optimizedImage = await sharpProcessor
      .webp({
        quality: 80,
        effort: 6,
      })
      .toBuffer();

    // Ensure directory exists
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    // Save file
    const filePath = path.join(targetDir, `${finalFilename}.webp`);
    fs.writeFileSync(filePath, optimizedImage);

    const relativePath = folder
      ? `public/assets/images/${folder}/${finalFilename}.webp`
      : `public/assets/images/${finalFilename}.webp`;

    console.log(`✅ Asset saved to: ${relativePath}`);
    console.log(`📊 File size: ${(optimizedImage.length / 1024).toFixed(2)} KB`);
    console.log(
      `\n💡 Usage in component:\n   <Image src="/assets/images/${folder ? `${folder}/` : ""}${finalFilename}.webp" alt="${prompt.substring(0, 50)}" width={${imageWidth}} height={${imageHeight}} />`,
    );
  } catch (error) {
    console.error("❌ Failed to generate asset:", error);
    if (error instanceof Error) {
      console.error("Error details:", error.message);
    }
    process.exit(1);
  }
}

main();
