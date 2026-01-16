import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

import { fetchGeminiAccessToken, runGeminiWebWithFallback, saveFirstGeminiImageFromOutput } from './client.js';
import { getGeminiCookieMapViaChrome } from './chrome-auth.js';
import {
  hasRequiredGeminiCookies,
  readGeminiCookieMapFromDisk,
  writeGeminiCookieMapToDisk,
} from './cookie-store.js';
import { resolveGeminiWebChromeProfileDir, resolveGeminiWebCookiePath } from './paths.js';

function printUsage(exitCode = 0): never {
  const cookiePath = resolveGeminiWebCookiePath();
  const profileDir = resolveGeminiWebChromeProfileDir();

  console.log(`Usage:
  npx -y bun skills/baoyu-gemini-web/scripts/main.ts --prompt "Hello"
  npx -y bun skills/baoyu-gemini-web/scripts/main.ts "Hello"
  npx -y bun skills/baoyu-gemini-web/scripts/main.ts --prompt "A cute cat" --image generated.png
  npx -y bun skills/baoyu-gemini-web/scripts/main.ts --promptfiles system.md content.md --image out.png

Options:
  -p, --prompt <text>       Prompt text
  --promptfiles <files...>  Read prompt from one or more files (concatenated in order)
  -m, --model <id>          gemini-3-pro | gemini-2.5-pro | gemini-2.5-flash (default: gemini-3-pro)
  --json                    Output JSON
  --image [path]            Generate an image and save it (default: ./generated.png)
  --login                   Only refresh cookies, then exit
  --cookie-path <path>      Cookie file path (default: ${cookiePath})
  --profile-dir <path>      Chrome profile dir (default: ${profileDir})
  -h, --help                Show help

Env overrides:
  GEMINI_WEB_DATA_DIR, GEMINI_WEB_COOKIE_PATH, GEMINI_WEB_CHROME_PROFILE_DIR, GEMINI_WEB_CHROME_PATH
`);

  process.exit(exitCode);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function readPromptFromStdin(): Promise<string | null> {
  if (process.stdin.isTTY) return null;
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  const text = Buffer.concat(chunks).toString('utf8').trim();
  return text ? text : null;
}

function readPromptFiles(filePaths: string[]): string {
  const contents: string[] = [];
  for (const filePath of filePaths) {
    const resolved = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
    if (!fs.existsSync(resolved)) {
      throw new Error(`Prompt file not found: ${resolved}`);
    }
    const content = fs.readFileSync(resolved, 'utf8').trim();
    contents.push(content);
  }
  return contents.join('\n\n');
}

function parseArgs(argv: string[]): {
  prompt?: string;
  promptFiles?: string[];
  model?: string;
  json?: boolean;
  imagePath?: string;
  loginOnly?: boolean;
  cookiePath?: string;
  profileDir?: string;
} {
  const out: ReturnType<typeof parseArgs> = {};
  const positional: string[] = [];

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i] ?? '';
    if (arg === '--help' || arg === '-h') printUsage(0);
    if (arg === '--json') {
      out.json = true;
      continue;
    }
    if (arg === '--image' || arg === '--generate-image') {
      const next = argv[i + 1];
      if (next && !next.startsWith('-')) {
        out.imagePath = next;
        i += 1;
      } else {
        out.imagePath = 'generated.png';
      }
      continue;
    }
    if (arg.startsWith('--image=')) {
      out.imagePath = arg.slice('--image='.length);
      continue;
    }
    if (arg.startsWith('--generate-image=')) {
      out.imagePath = arg.slice('--generate-image='.length);
      continue;
    }
    if (arg === '--login') {
      out.loginOnly = true;
      continue;
    }
    if (arg === '--prompt' || arg === '-p') {
      out.prompt = argv[i + 1] ?? '';
      i += 1;
      continue;
    }
    if (arg.startsWith('--prompt=')) {
      out.prompt = arg.slice('--prompt='.length);
      continue;
    }
    if (arg === '--promptfiles') {
      out.promptFiles = [];
      while (i + 1 < argv.length) {
        const next = argv[i + 1];
        if (next && !next.startsWith('-')) {
          out.promptFiles.push(next);
          i += 1;
        } else {
          break;
        }
      }
      continue;
    }
    if (arg === '--model' || arg === '-m') {
      out.model = argv[i + 1] ?? '';
      i += 1;
      continue;
    }
    if (arg.startsWith('--model=')) {
      out.model = arg.slice('--model='.length);
      continue;
    }
    if (arg === '--cookie-path') {
      out.cookiePath = argv[i + 1] ?? '';
      i += 1;
      continue;
    }
    if (arg.startsWith('--cookie-path=')) {
      out.cookiePath = arg.slice('--cookie-path='.length);
      continue;
    }
    if (arg === '--profile-dir') {
      out.profileDir = argv[i + 1] ?? '';
      i += 1;
      continue;
    }
    if (arg.startsWith('--profile-dir=')) {
      out.profileDir = arg.slice('--profile-dir='.length);
      continue;
    }

    if (arg.startsWith('-')) {
      throw new Error(`Unknown option: ${arg}`);
    }
    positional.push(arg);
  }

  if (!out.prompt && positional.length > 0) {
    out.prompt = positional.join(' ').trim();
  }

  if (out.prompt != null) out.prompt = out.prompt.trim();
  if (out.model != null) out.model = out.model.trim();
  if (out.imagePath != null) out.imagePath = out.imagePath.trim();
  if (out.cookiePath != null) out.cookiePath = out.cookiePath.trim();
  if (out.profileDir != null) out.profileDir = out.profileDir.trim();

  if (out.imagePath === '') delete out.imagePath;
  if (out.cookiePath === '') delete out.cookiePath;
  if (out.profileDir === '') delete out.profileDir;
  if (out.promptFiles?.length === 0) delete out.promptFiles;

  return out;
}

async function isCookieMapValid(cookieMap: Record<string, string>): Promise<boolean> {
  if (!hasRequiredGeminiCookies(cookieMap)) return false;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10_000);
  try {
    await fetchGeminiAccessToken(cookieMap, controller.signal);
    return true;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

async function ensureGeminiCookieMap(options: {
  cookiePath: string;
  profileDir: string;
}): Promise<Record<string, string>> {
  const log = (msg: string) => console.log(msg);

  let cookieMap = await readGeminiCookieMapFromDisk({ cookiePath: options.cookiePath, log });
  if (await isCookieMapValid(cookieMap)) return cookieMap;

  log('[gemini-web] No valid cookies found. Opening browser to sync Gemini cookies...');
  cookieMap = await getGeminiCookieMapViaChrome({ userDataDir: options.profileDir, log });
  await writeGeminiCookieMapToDisk(cookieMap, { cookiePath: options.cookiePath, log });
  return cookieMap;
}

function resolveModel(value: string): 'gemini-3-pro' | 'gemini-2.5-pro' | 'gemini-2.5-flash' {
  const desired = value.trim();
  if (!desired) return 'gemini-3-pro';
  switch (desired) {
    case 'gemini-3-pro':
    case 'gemini-3.0-pro':
      return 'gemini-3-pro';
    case 'gemini-2.5-pro':
      return 'gemini-2.5-pro';
    case 'gemini-2.5-flash':
      return 'gemini-2.5-flash';
    default:
      console.error(`[gemini-web] Unsupported model "${desired}", falling back to gemini-3-pro.`);
      return 'gemini-3-pro';
  }
}

function resolveImageOutputPath(value: string | undefined): string | null {
  if (value == null) return null;
  const trimmed = value.trim();
  const raw = trimmed || 'generated.png';
  const resolved = path.isAbsolute(raw) ? raw : path.resolve(process.cwd(), raw);

  if (resolved.endsWith(path.sep)) return path.join(resolved, 'generated.png');
  try {
    if (fs.existsSync(resolved) && fs.statSync(resolved).isDirectory()) {
      return path.join(resolved, 'generated.png');
    }
  } catch {
    // ignore
  }
  return resolved;
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  const cookiePath = args.cookiePath ?? resolveGeminiWebCookiePath();
  const profileDir = args.profileDir ?? resolveGeminiWebChromeProfileDir();

  if (args.loginOnly) {
    await ensureGeminiCookieMap({ cookiePath, profileDir });
    return;
  }

  const promptFromStdin = await readPromptFromStdin();
  const promptFromFiles = args.promptFiles ? readPromptFiles(args.promptFiles) : null;
  const prompt = promptFromFiles || args.prompt || promptFromStdin;
  if (!prompt) printUsage(1);

  let cookieMap = await ensureGeminiCookieMap({ cookiePath, profileDir });

  const desiredModel = resolveModel(args.model || 'gemini-3-pro');
  const imagePath = resolveImageOutputPath(args.imagePath);

  try {
    const effectivePrompt = imagePath ? `Generate an image: ${prompt}` : prompt;
    const out = await runGeminiWebWithFallback({
      prompt: effectivePrompt,
      files: [],
      model: desiredModel,
      cookieMap,
      chatMetadata: null,
    });

    let imageSaved = false;
    let imageCount = 0;
    if (imagePath) {
      const save = await saveFirstGeminiImageFromOutput(out, cookieMap, imagePath);
      imageSaved = save.saved;
      imageCount = save.imageCount;
      if (!imageSaved) {
        throw new Error(`No images generated. Response text:\n${out.text || '(empty response)'}`);
      }
    }

    if (args.json) {
      process.stdout.write(
        `${JSON.stringify(
          imagePath ? { ...out, imageSaved, imageCount, imagePath } : out,
          null,
          2,
        )}\n`,
      );
      if (out.errorMessage) process.exit(1);
      return;
    }

    if (out.errorMessage) {
      throw new Error(out.errorMessage);
    }

    process.stdout.write(out.text ?? '');
    if (!out.text?.endsWith('\n')) process.stdout.write('\n');
    if (imagePath) {
      process.stdout.write(`Saved image (${imageCount || 1}) to: ${imagePath}\n`);
    }
    return;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);

    if (message.includes('Unable to locate Gemini access token')) {
      console.error('[gemini-web] Cookies may be expired. Re-opening browser to refresh cookies...');
      await sleep(500);
      cookieMap = await getGeminiCookieMapViaChrome({ userDataDir: profileDir, log: (m) => console.log(m) });
      await writeGeminiCookieMapToDisk(cookieMap, { cookiePath, log: (m) => console.log(m) });

      const out = await runGeminiWebWithFallback({
        prompt: imagePath ? `Generate an image: ${prompt}` : prompt,
        files: [],
        model: desiredModel,
        cookieMap,
        chatMetadata: null,
      });

      let imageSaved = false;
      let imageCount = 0;
      if (imagePath) {
        const save = await saveFirstGeminiImageFromOutput(out, cookieMap, imagePath);
        imageSaved = save.saved;
        imageCount = save.imageCount;
        if (!imageSaved) {
          throw new Error(`No images generated. Response text:\n${out.text || '(empty response)'}`);
        }
      }

      if (args.json) {
        process.stdout.write(
          `${JSON.stringify(
            imagePath ? { ...out, imageSaved, imageCount, imagePath } : out,
            null,
            2,
          )}\n`,
        );
        if (out.errorMessage) process.exit(1);
        return;
      }

      if (out.errorMessage) {
        throw new Error(out.errorMessage);
      }

      process.stdout.write(out.text ?? '');
      if (!out.text?.endsWith('\n')) process.stdout.write('\n');
      if (imagePath) {
        process.stdout.write(`Saved image (${imageCount || 1}) to: ${imagePath}\n`);
      }
      return;
    }

    throw error;
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
