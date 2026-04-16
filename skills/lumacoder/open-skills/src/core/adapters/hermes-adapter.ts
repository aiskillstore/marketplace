import { ClaudeAdapter } from './claude-adapter.js';

export class HermesAdapter extends ClaudeAdapter {
  override transformSkillContent(content: string): string {
    return content;
  }

  override shouldGenerateIndex(): boolean {
    return true;
  }
}
