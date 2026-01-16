import path from 'node:path';
import type { BrowserRunOptions, BrowserRunResult, BrowserLogger, CookieParam } from '../browser/types.js';
import { runGeminiWebWithFallback, saveFirstGeminiImageFromOutput } from './client.js';
import type { GeminiWebModelId } from './client.js';
import {
  buildGeminiCookieMap,
  hasRequiredGeminiCookies,
  readGeminiCookieMapFromDisk,
} from './cookie-store.js';
import type { GeminiWebOptions, GeminiWebResponse } from './types.js';

export { hasRequiredGeminiCookies } from './cookie-store.js';

function estimateTokenCount(text: string): number {
  return Math.ceil(text.length / 4);
}

function resolveInvocationPath(value: string | undefined): string | undefined {
  if (!value) return undefined;
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  return path.isAbsolute(trimmed) ? trimmed : path.resolve(process.cwd(), trimmed);
}

function resolveGeminiWebModel(
  desiredModel: string | null | undefined,
  log?: BrowserLogger,
): GeminiWebModelId {
  const desired = typeof desiredModel === 'string' ? desiredModel.trim() : '';
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
      if (desired.startsWith('gemini-')) {
        log?.(
          `[gemini-web] Unsupported Gemini web model "${desired}". Falling back to gemini-3-pro.`,
        );
      }
      return 'gemini-3-pro';
  }
}

function buildInlineCookiesFromEnv(): CookieParam[] {
  const cookies: CookieParam[] = [];
  const psid = process.env.GEMINI_SECURE_1PSID?.trim();
  const psidts = process.env.GEMINI_SECURE_1PSIDTS?.trim();

  if (psid) {
    cookies.push({ name: '__Secure-1PSID', value: psid, domain: 'google.com', path: '/' });
  }
  if (psidts) {
    cookies.push({ name: '__Secure-1PSIDTS', value: psidts, domain: 'google.com', path: '/' });
  }

  return cookies;
}

async function loadGeminiCookiesFromInline(
  browserConfig: BrowserRunOptions['config'],
  log?: BrowserLogger,
): Promise<Record<string, string>> {
  const inline = browserConfig?.inlineCookies;
  if (!inline || inline.length === 0) return {};

  const cookieMap = buildGeminiCookieMap(
    inline.filter((cookie): cookie is CookieParam => Boolean(cookie?.name && typeof cookie.value === 'string')),
  );

  if (Object.keys(cookieMap).length > 0) {
    const source = browserConfig?.inlineCookiesSource ?? 'inline';
    log?.(`[gemini-web] Loaded Gemini cookies from inline payload (${source}): ${Object.keys(cookieMap).length} cookie(s).`);
  } else {
    log?.('[gemini-web] Inline cookie payload provided but no Gemini cookies matched.');
  }

  return cookieMap;
}

export async function loadGeminiCookies(
  browserConfig: BrowserRunOptions['config'],
  log?: BrowserLogger,
): Promise<Record<string, string>> {
  const inlineMap = await loadGeminiCookiesFromInline(browserConfig, log);
  if (hasRequiredGeminiCookies(inlineMap)) return inlineMap;

  const diskMap = await readGeminiCookieMapFromDisk({ log });
  const merged = { ...diskMap, ...inlineMap };
  if (hasRequiredGeminiCookies(merged)) return merged;

  if (browserConfig?.cookieSync === false) {
    log?.('[gemini-web] Cookie sync disabled and inline cookies missing Gemini auth tokens.');
    return merged;
  }

  log?.(
    '[gemini-web] Missing Gemini auth cookies. Run `npx -y bun skills/baoyu-gemini-web/scripts/main.ts --login` to sign in and refresh cookies.',
  );
  return merged;
}

export async function loadGeminiCookieMap(log?: BrowserLogger): Promise<Record<string, string>> {
  const diskMap = await readGeminiCookieMapFromDisk({ log });
  const inlineCookies = buildInlineCookiesFromEnv();
  const envMap = buildGeminiCookieMap(inlineCookies);
  return { ...diskMap, ...envMap };
}

export function createGeminiWebExecutor(
  geminiOptions: GeminiWebOptions,
): (runOptions: BrowserRunOptions) => Promise<BrowserRunResult> {
  return async (runOptions: BrowserRunOptions): Promise<BrowserRunResult> => {
    const startTime = Date.now();
    const log = runOptions.log;

    log?.('[gemini-web] Starting Gemini web executor (TypeScript)');

    const cookieMap = await loadGeminiCookies(runOptions.config, log);
    if (!hasRequiredGeminiCookies(cookieMap)) {
      throw new Error(
        'Gemini browser mode requires auth cookies (missing __Secure-1PSID/__Secure-1PSIDTS). Run `npx -y bun skills/baoyu-gemini-web/scripts/main.ts --login` to sign in and save cookies.',
      );
    }

    const configTimeout =
      typeof runOptions.config?.timeoutMs === 'number' && Number.isFinite(runOptions.config.timeoutMs)
        ? Math.max(1_000, runOptions.config.timeoutMs)
        : null;

    const defaultTimeoutMs = geminiOptions.youtube
      ? 240_000
      : geminiOptions.generateImage || geminiOptions.editImage
        ? 300_000
        : 120_000;

    const timeoutMs = Math.min(configTimeout ?? defaultTimeoutMs, 600_000);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    const generateImagePath = resolveInvocationPath(geminiOptions.generateImage);
    const editImagePath = resolveInvocationPath(geminiOptions.editImage);
    const outputPath = resolveInvocationPath(geminiOptions.outputPath);
    const attachmentPaths = (runOptions.attachments ?? []).map((attachment) => attachment.path);

    let prompt = runOptions.prompt;
    if (geminiOptions.aspectRatio && (generateImagePath || editImagePath)) {
      prompt = `${prompt} (aspect ratio: ${geminiOptions.aspectRatio})`;
    }
    if (geminiOptions.youtube) {
      prompt = `${prompt}\n\nYouTube video: ${geminiOptions.youtube}`;
    }
    if (generateImagePath && !editImagePath) {
      prompt = `Generate an image: ${prompt}`;
    }

    const model: GeminiWebModelId = resolveGeminiWebModel(runOptions.config?.desiredModel, log);
    let response: GeminiWebResponse;

    try {
      if (editImagePath) {
        const intro = await runGeminiWebWithFallback({
          prompt: 'Here is an image to edit',
          files: [editImagePath],
          model,
          cookieMap,
          chatMetadata: null,
          signal: controller.signal,
        });
        const editPrompt = `Use image generation tool to ${prompt}`;
        const out = await runGeminiWebWithFallback({
          prompt: editPrompt,
          files: attachmentPaths,
          model,
          cookieMap,
          chatMetadata: intro.metadata,
          signal: controller.signal,
        });
        response = {
          text: out.text ?? null,
          thoughts: geminiOptions.showThoughts ? out.thoughts : null,
          has_images: false,
          image_count: 0,
        };

        const resolvedOutputPath = outputPath ?? generateImagePath ?? 'generated.png';
        const imageSave = await saveFirstGeminiImageFromOutput(out, cookieMap, resolvedOutputPath, controller.signal);
        response.has_images = imageSave.saved;
        response.image_count = imageSave.imageCount;
        if (!imageSave.saved) {
          throw new Error(`No images generated. Response text:\n${out.text || '(empty response)'}`);
        }
      } else if (generateImagePath) {
        const out = await runGeminiWebWithFallback({
          prompt,
          files: attachmentPaths,
          model,
          cookieMap,
          chatMetadata: null,
          signal: controller.signal,
        });
        response = {
          text: out.text ?? null,
          thoughts: geminiOptions.showThoughts ? out.thoughts : null,
          has_images: false,
          image_count: 0,
        };
        const imageSave = await saveFirstGeminiImageFromOutput(out, cookieMap, generateImagePath, controller.signal);
        response.has_images = imageSave.saved;
        response.image_count = imageSave.imageCount;
        if (!imageSave.saved) {
          throw new Error(`No images generated. Response text:\n${out.text || '(empty response)'}`);
        }
      } else {
        const out = await runGeminiWebWithFallback({
          prompt,
          files: attachmentPaths,
          model,
          cookieMap,
          chatMetadata: null,
          signal: controller.signal,
        });
        response = {
          text: out.text ?? null,
          thoughts: geminiOptions.showThoughts ? out.thoughts : null,
          has_images: out.images.length > 0,
          image_count: out.images.length,
        };
      }
    } finally {
      clearTimeout(timeout);
    }

    const answerText = response.text ?? '';
    let answerMarkdown = answerText;

    if (geminiOptions.showThoughts && response.thoughts) {
      answerMarkdown = `## Thinking\n\n${response.thoughts}\n\n## Response\n\n${answerText}`;
    }

    if (response.has_images && response.image_count > 0) {
      const imagePath = generateImagePath || outputPath || 'generated.png';
      answerMarkdown += `\n\n*Generated ${response.image_count} image(s). Saved to: ${imagePath}*`;
    }

    const tookMs = Date.now() - startTime;
    log?.(`[gemini-web] Completed in ${tookMs}ms`);

    return {
      answerText,
      answerMarkdown,
      tookMs,
      answerTokens: estimateTokenCount(answerText),
      answerChars: answerText.length,
    };
  };
}
