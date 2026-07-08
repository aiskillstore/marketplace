#!/usr/bin/env bun
/**
 * TUI Configuration Manager
 * Manages TUI settings and preferences
 */

export interface TUIConfig {
  language: 'bilingual' | 'zh' | 'en';
  refreshInterval: number;
  showTimestamps: boolean;
  colorTheme: 'default' | 'dark' | 'light';
  maxOutputLines: number;
  autoCleanupHours: number;
  confirmKill: boolean;
  showFullCommand: boolean;
}

const DEFAULT_CONFIG: TUIConfig = {
  language: 'bilingual',
  refreshInterval: 5,
  showTimestamps: true,
  colorTheme: 'default',
  maxOutputLines: 200,
  autoCleanupHours: 24,
  confirmKill: true,
  showFullCommand: false,
};

class TUIConfigManager {
  private config: TUIConfig;
  private configPath: string;

  constructor(configPath?: string) {
    this.configPath = configPath || `${process.env.HOME}/.pi-tmux-tui-config.json`;
    this.config = { ...DEFAULT_CONFIG };
    this.load();
  }

  async load(): Promise<void> {
    try {
      const { readFile } = await import('fs/promises');
      const content = await readFile(this.configPath, 'utf-8');
      const loaded = JSON.parse(content);
      this.config = { ...DEFAULT_CONFIG, ...loaded };
    } catch (error) {
      // Config file doesn't exist, use defaults
      this.config = { ...DEFAULT_CONFIG };
    }
  }

  async save(): Promise<void> {
    try {
      const { writeFile } = await import('fs/promises');
      await writeFile(this.configPath, JSON.stringify(this.config, null, 2));
    } catch (error) {
      console.error('Failed to save config:', error);
    }
  }

  get<K extends keyof TUIConfig>(key: K): TUIConfig[K] {
    return this.config[key];
  }

  set<K extends keyof TUIConfig>(key: K, value: TUIConfig[K]): void {
    this.config[key] = value;
  }

  getAll(): TUIConfig {
    return { ...this.config };
  }

  reset(): void {
    this.config = { ...DEFAULT_CONFIG };
  }

  async resetAndSave(): Promise<void> {
    this.reset();
    await this.save();
  }
}

export { TUIConfigManager, DEFAULT_CONFIG };