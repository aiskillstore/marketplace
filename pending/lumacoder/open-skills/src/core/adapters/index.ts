import { EditorPreset } from '../../types/index.js';
import { BaseAdapter } from './base-adapter.js';
import { ClaudeAdapter } from './claude-adapter.js';
import { HermesAdapter } from './hermes-adapter.js';
import { CursorAdapter } from './cursor-adapter.js';
import { WindsurfAdapter } from './windsurf-adapter.js';
import { ClineAdapter } from './cline-adapter.js';
import { RooClineAdapter } from './roo-cline-adapter.js';
import { AntigravityAdapter } from './antigravity-adapter.js';
import { CursorSkillsAdapter } from './cursor-skills-adapter.js';

export function createAdapter(preset: EditorPreset): BaseAdapter {
  switch (preset.id) {
    case 'claude-code':
      return new ClaudeAdapter(preset);
    case 'hermes':
      return new HermesAdapter(preset);
    case 'cursor':
      return new CursorAdapter(preset);
    case 'windsurf':
      return new WindsurfAdapter(preset);
    case 'cline':
      return new ClineAdapter(preset);
    case 'cursor-skills':
      return new CursorSkillsAdapter(preset);
    case 'roo-cline':
      return new RooClineAdapter(preset);
    case 'antigravity':
      return new AntigravityAdapter(preset);
    case 'github-copilot':
      return new ClaudeAdapter(preset);
    default:
      throw new Error(`Unknown editor preset: ${preset.id}`);
  }
}

export * from './base-adapter.js';
export * from './claude-adapter.js';
export * from './hermes-adapter.js';
export * from './cursor-adapter.js';
export * from './windsurf-adapter.js';
export * from './cline-adapter.js';
export * from './roo-cline-adapter.js';
export * from './antigravity-adapter.js';
export * from './cursor-skills-adapter.js';
