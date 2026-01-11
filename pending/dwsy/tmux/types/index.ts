export type SessionCategory = 'task' | 'service' | 'agent';
export type SessionStatus = 'running' | 'idle' | 'exited';

export interface TmuxSession {
  id: string;
  name: string;
  category: SessionCategory;
  socket: string;
  target: string;
  command: string;
  status: SessionStatus;
  createdAt: string;
  lastActivityAt: string;
}

export interface TmuxConfig {
  socketDir: string;
  defaultSocket: string;
  sessionStore: string;
  autoCleanup: boolean;
  cleanupAge: number;
}

export interface WaitForTextOptions {
  timeout?: number;
  interval?: number;
  lines?: number;
}