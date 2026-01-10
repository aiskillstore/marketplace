/**
 * TypeScript definitions for window.openai
 *
 * The ChatGPT host injects this global object into widget iframes.
 */

interface OpenAIWidgetState {
  [key: string]: unknown;
}

interface OpenAIToolOutput {
  [key: string]: unknown;
}

interface OpenAIToolInput {
  [key: string]: unknown;
}

interface OpenAIResponseMetadata {
  [key: string]: unknown;
}

interface OpenAISafeArea {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

interface OpenAIUploadResult {
  fileId: string;
}

interface OpenAIDownloadResult {
  downloadUrl: string;
}

type DisplayMode = "inline" | "expanded" | "pip" | "fullscreen";
type Theme = "light" | "dark";

interface OpenAIGlobals {
  // Data access
  toolInput: OpenAIToolInput;
  toolOutput: OpenAIToolOutput;
  toolResponseMetadata: OpenAIResponseMetadata;
  widgetState: OpenAIWidgetState | null;

  // Context signals
  theme: Theme;
  displayMode: DisplayMode;
  maxHeight: number;
  safeArea: OpenAISafeArea;
  locale: string;
  userAgent: string;

  // State management
  setWidgetState: (state: OpenAIWidgetState) => void;

  // Tool invocation
  callTool: (name: string, args: Record<string, unknown>) => Promise<void>;
  sendFollowUpMessage: (params: { prompt: string }) => Promise<void>;

  // File operations
  uploadFile: (file: File) => Promise<OpenAIUploadResult>;
  getFileDownloadUrl: (params: { fileId: string }) => Promise<OpenAIDownloadResult>;

  // Layout control
  notifyIntrinsicHeight: (height: number) => void;
  requestDisplayMode: (params: { mode: DisplayMode }) => Promise<void>;
  requestModal: (params: { title: string }) => Promise<void>;
  requestClose: () => void;
  openExternal: (params: { href: string }) => void;
}

declare global {
  interface Window {
    openai: OpenAIGlobals;
  }
}

export type {
  OpenAIWidgetState,
  OpenAIToolOutput,
  OpenAIToolInput,
  OpenAIResponseMetadata,
  OpenAISafeArea,
  OpenAIUploadResult,
  OpenAIDownloadResult,
  DisplayMode,
  Theme,
  OpenAIGlobals,
};
