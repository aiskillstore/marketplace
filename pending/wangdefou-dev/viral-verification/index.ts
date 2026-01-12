import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import Anthropic from '@anthropic-ai/sdk';
import pLimit from 'p-limit';

// 1. Load Environment Variables
const projectRoot = path.resolve(__dirname, '../../');
const envPath = path.join(projectRoot, '.env');

console.log(`Loading .env from: ${envPath}`);
if (fs.existsSync(envPath)) {
  console.log('✅ .env file found');
} else {
  console.error('❌ .env file NOT found');
}

dotenv.config({ path: envPath, override: true });

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const ANTHROPIC_BASE_URL = process.env.ANTHROPIC_BASE_URL;

// 2. Define Paths
const OUTPUT_DIR = path.join(projectRoot, 'outputs');
const SOURCE_DIR = path.join(OUTPUT_DIR, 'defou-stanley-posts');
const TARGET_DIR = path.join(OUTPUT_DIR, 'viral-verified-posts');

// Ensure target directory exists
if (!fs.existsSync(TARGET_DIR)) {
  fs.mkdirSync(TARGET_DIR, { recursive: true });
}

// 3. Initialize Anthropic Client
const anthropic = new Anthropic({
  apiKey: ANTHROPIC_API_KEY || 'dummy',
  baseURL: ANTHROPIC_BASE_URL,
});

/**
 * Load prompt from SKILL.md
 */
function loadPromptFromSkill(): string {
  try {
    const skillPath = path.join(__dirname, 'SKILL.md');
    const content = fs.readFileSync(skillPath, 'utf-8');
    
    // Regex to capture content inside the first markdown code block
    const match = content.match(/```markdown\n([\s\S]*?)\n```/);
    if (match && match[1]) {
      return match[1];
    }
    
    throw new Error('Could not find markdown code block in SKILL.md');
  } catch (error) {
    console.error('❌ Failed to load prompt from SKILL.md:', error);
    process.exit(1);
  }
}

/**
 * Check if a file has already been verified
 */
function isVerified(filename: string, verifiedFiles: string[]): boolean {
  // Verified files format: verified_TIMESTAMP_ORIGINALFILENAME
  // We check if any verified file ends with "_" + filename
  return verifiedFiles.some(vf => vf.includes(`_${filename}`));
}

/**
 * Get pending files to verify
 */
function getPendingFiles(limitCount: number = 10): string[] {
  if (!fs.existsSync(SOURCE_DIR)) return [];
  
  // Get all source files sorted by newest first
  const sourceFiles = fs.readdirSync(SOURCE_DIR)
    .filter(file => file.endsWith('.md'))
    .map(file => ({
      name: file,
      path: path.join(SOURCE_DIR, file),
      time: fs.statSync(path.join(SOURCE_DIR, file)).mtime.getTime()
    }))
    .sort((a, b) => b.time - a.time);

  // Get all verified files
  const verifiedFiles = fs.existsSync(TARGET_DIR) 
    ? fs.readdirSync(TARGET_DIR) 
    : [];

  // Filter out already verified files
  const pendingFiles = sourceFiles
    .filter(file => !isVerified(file.name, verifiedFiles))
    .map(file => file.path); // Return full paths

  console.log(`Found ${sourceFiles.length} total files, ${sourceFiles.length - pendingFiles.length} already verified.`);
  
  return pendingFiles.slice(0, limitCount);
}

/**
 * Verify content using Claude
 */
async function verifyContent(content: string, filename: string) {
  const promptTemplate = loadPromptFromSkill();
  const prompt = promptTemplate.replace('{{CONTENT}}', content);

  console.log(`🤖 Verifying content for: "${filename}"...`);

  const msg = await anthropic.messages.create({
    model: "anthropic/claude-sonnet-4",
    max_tokens: 4000,
    temperature: 0.7,
    system: "You are a Viral Content Validator.",
    messages: [
      { role: "user", content: prompt }
    ]
  });

  return (msg.content[0] as any).text;
}

/**
 * Process a single file
 */
async function processFile(filePath: string) {
    const filename = path.basename(filePath);
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const verificationResult = await verifyContent(content, filename);

        const dateStr = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const outputFilename = `verified_${dateStr}_${filename}`;
        const outputPath = path.join(TARGET_DIR, outputFilename);

        const finalContent = `
<!--
Original File: ${filename}
Verification Date: ${new Date().toLocaleString()}
-->

${verificationResult}
`;

        fs.writeFileSync(outputPath, finalContent);
        console.log(`✅ Verified content saved to: ${outputPath}`);
    } catch (error) {
        console.error(`❌ Error verifying ${filename}:`, error);
    }
}

/**
 * Main execution
 */
async function run() {
  try {
    // 1. Determine input files
    const args = process.argv.slice(2);
    let filesToProcess: string[] = [];

    if (args.length > 0) {
      // User provided specific file(s)
      const inputFile = args[0];
      if (!path.isAbsolute(inputFile)) {
        filesToProcess.push(path.resolve(process.cwd(), inputFile));
      } else {
        filesToProcess.push(inputFile);
      }
      console.log(`Processing specified file: ${filesToProcess[0]}`);
    } else {
      // Auto-detect pending files
      console.log('No input file provided. Looking for unverified files (limit 10)...');
      filesToProcess = getPendingFiles(10);
      
      if (filesToProcess.length === 0) {
        console.log('✨ All files are already verified! Nothing to do.');
        return;
      }
      
      console.log(`🎯 Found ${filesToProcess.length} pending files to verify.`);
    }

    // 2. Process files with concurrency limit
    const limit = pLimit(2); // Verify 2 files at a time
    const tasks = filesToProcess.map(file => limit(() => processFile(file)));

    await Promise.all(tasks);
    console.log('🎉 All verification tasks completed!');

  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  run();
}
