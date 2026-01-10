import type {
  AnalysisRequest,
  AnalysisResponse,
  GetApiKeyRequest,
  PageSnapshotResponse,
  RequestPageSnapshot,
  SaveApiKeyRequest,
} from '../shared/contracts.js';

function setStatus(text: string): void {
  const status = document.getElementById('status');
  if (status) {
    status.textContent = text;
  }
}

async function loadApiKey(): Promise<void> {
  const response = await chrome.runtime.sendMessage<GetApiKeyRequest>({ type: 'get-api-key' });
  const input = document.getElementById('apiKey') as HTMLInputElement | null;
  const apiKey = (response as { payload?: { apiKey?: string } })?.payload?.apiKey ?? '';
  if (input) {
    input.value = apiKey;
  }
}

async function saveApiKey(): Promise<void> {
  const input = document.getElementById('apiKey') as HTMLInputElement | null;
  if (!input) return;
  await chrome.runtime.sendMessage<SaveApiKeyRequest>({
    type: 'save-api-key',
    payload: { apiKey: input.value.trim() },
  });
  setStatus('API key gespeichert (Session).');
}

async function getActiveTabId(): Promise<number | undefined> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.id;
}

async function requestSnapshotFromTab(tabId: number): Promise<PageSnapshotResponse['payload']> {
  const response = (await chrome.tabs.sendMessage(tabId, {
    type: 'request-page-snapshot',
  } as RequestPageSnapshot)) as PageSnapshotResponse;
  return response.payload;
}

function renderResult(result: AnalysisResponse['payload']): void {
  const container = document.getElementById('result');
  if (!container) return;
  container.innerHTML = '';

  const score = document.createElement('div');
  score.className = 'score';
  score.textContent = `SEO Score: ${result.score}/100`;

  const summary = document.createElement('p');
  summary.textContent = result.aiSummary;

  const issuesTitle = document.createElement('h4');
  issuesTitle.textContent = 'Issues';
  const issuesList = document.createElement('ul');
  result.issues.forEach((issue) => {
    const li = document.createElement('li');
    li.textContent = issue;
    issuesList.appendChild(li);
  });

  const recTitle = document.createElement('h4');
  recTitle.textContent = 'Recommendations';
  const recList = document.createElement('ul');
  result.recommendations.forEach((rec) => {
    const li = document.createElement('li');
    li.textContent = rec;
    recList.appendChild(li);
  });

  container.append(score, summary, issuesTitle, issuesList, recTitle, recList);
}

async function analyzeCurrentTab(): Promise<void> {
  setStatus('Collecting page data...');
  const tabId = await getActiveTabId();
  if (!tabId) {
    setStatus('Kein aktiver Tab gefunden.');
    return;
  }

  const snapshot = await requestSnapshotFromTab(tabId);
  setStatus('Running analysis...');
  const response = await chrome.runtime.sendMessage<AnalysisRequest, AnalysisResponse>({
    type: 'analyze-page',
    payload: snapshot,
  });

  renderResult(response.payload);
  setStatus('Analysis complete.');
}

function wireUi(): void {
  const saveButton = document.getElementById('saveApiKey');
  const analyzeButton = document.getElementById('analyze');

  saveButton?.addEventListener('click', saveApiKey);
  analyzeButton?.addEventListener('click', () => {
    analyzeCurrentTab().catch((error) => setStatus(String(error)));
  });
}

document.addEventListener('DOMContentLoaded', () => {
  wireUi();
  loadApiKey();
});
