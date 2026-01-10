export type PageSnapshot = {
  url: string;
  title: string;
  description: string;
  headings: string[];
  wordCount: number;
  images: { alt: string | null; src: string }[];
  links: { href: string; text: string }[];
};

export type AnalysisRequest = {
  type: 'analyze-page';
  payload: PageSnapshot;
};

export type AnalysisResponse = {
  type: 'analysis-result';
  payload: {
    score: number;
    issues: string[];
    recommendations: string[];
    aiSummary: string;
  };
};

export type SaveApiKeyRequest = {
  type: 'save-api-key';
  payload: {
    apiKey: string;
  };
};

export type GetApiKeyRequest = {
  type: 'get-api-key';
};

export type RequestPageSnapshot = {
  type: 'request-page-snapshot';
};

export type PageSnapshotResponse = {
  type: 'page-snapshot';
  payload: PageSnapshot;
};

export type OffscreenParseRequest = {
  type: 'offscreen-parse';
  payload: {
    html: string;
  };
};

export type OffscreenParseResponse = {
  type: 'offscreen-parse-result';
  payload: {
    links: number;
    images: number;
  };
};

export type RuntimeMessage =
  | AnalysisRequest
  | AnalysisResponse
  | SaveApiKeyRequest
  | GetApiKeyRequest
  | RequestPageSnapshot
  | PageSnapshotResponse
  | OffscreenParseRequest
  | OffscreenParseResponse;
