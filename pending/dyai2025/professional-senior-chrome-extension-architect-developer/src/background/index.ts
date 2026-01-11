import type {
  AnalysisRequest,
  AnalysisResponse,
  GetApiKeyRequest,
  OffscreenParseRequest,
  OffscreenParseResponse,
  PageSnapshotResponse,
  RequestPageSnapshot,
  SaveApiKeyRequest,
} from '../shared/contracts.js';
import { fetchWithOpenAI, requestOffscreenParse, scoreSnapshot } from '../shared/utils.js';

async function handleAnalyze(request: AnalysisRequest): Promise<AnalysisResponse['payload']> {
  const heuristics = scoreSnapshot(request.payload);
  const apiKey = await chrome.storage.session.get('openaiApiKey');
  const keyValue = apiKey.openaiApiKey as string | undefined;

  if (!keyValue) {
    return { ...heuristics, aiSummary: heuristics.aiSummary + ' (local analysis)' };
  }

  try {
    const aiSummary = await fetchWithOpenAI(keyValue, request.payload);
    return { ...heuristics, aiSummary };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown OpenAI error';
    return { ...heuristics, aiSummary: `${heuristics.aiSummary} (AI fallback: ${message})` };
  }
}

function relayToTab(
  tabId: number,
  message: RequestPageSnapshot,
): Promise<PageSnapshotResponse> {
  return chrome.tabs.sendMessage<PageSnapshotResponse>(tabId, message as unknown as PageSnapshotResponse);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    if ((message as AnalysisRequest).type === 'analyze-page') {
      const result = await handleAnalyze(message as AnalysisRequest);
      sendResponse({ type: 'analysis-result', payload: result } satisfies AnalysisResponse);
      return;
    }

    if ((message as SaveApiKeyRequest).type === 'save-api-key') {
      const { apiKey } = (message as SaveApiKeyRequest).payload;
      await chrome.storage.session.set({ openaiApiKey: apiKey });
      sendResponse({ type: 'ack' });
      return;
    }

    if ((message as GetApiKeyRequest).type === 'get-api-key') {
      const { openaiApiKey } = await chrome.storage.session.get('openaiApiKey');
      sendResponse({ type: 'api-key', payload: { apiKey: openaiApiKey ?? '' } });
      return;
    }

    if ((message as RequestPageSnapshot).type === 'request-page-snapshot' && sender.tab?.id) {
      const response = await relayToTab(sender.tab.id, { type: 'request-page-snapshot' });
      sendResponse(response);
      return;
    }

    if ((message as OffscreenParseRequest).type === 'offscreen-parse') {
      const { html } = (message as OffscreenParseRequest).payload;
      const payload = await requestOffscreenParse(html);
      sendResponse({ type: 'offscreen-parse-result', payload } satisfies OffscreenParseResponse);
      return;
    }
  })();

  return true;
});

chrome.runtime.onInstalled.addListener(() => {
  console.info('AI SEO Analyzer installed');
});
