import type { RemoteResolver } from './remote-resolver.js';
import type { SkillMetaV3 } from '../../types/index.js';

export class ClawHubResolver implements RemoteResolver {
  provider = 'clawhub';

  async resolve(ref: string): Promise<Partial<SkillMetaV3>> {
    // Placeholder for ClawHub API integration
    throw new Error('ClawHub resolver not implemented yet');
  }
}
