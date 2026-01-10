/**
 * TypeScript definitions for window.openai
 *
 * Copy of the definitions from the server template.
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

interface OpenAIView {
  [key: string]: unknown;
}

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
  view: OpenAIView;

  setWidgetState: (state: OpenAIWidgetState) => void;
  callTool: (name: string, args: Record<string, unknown>) => Promise<void>;
  sendFollowUpMessage: (params: { prompt: string }) => Promise<void>;
  uploadFile: (file: File) => Promise<OpenAIUploadResult>;
  getFileDownloadUrl: (params: { fileId: string }) => Promise<OpenAIDownloadResult>;
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

export {};
