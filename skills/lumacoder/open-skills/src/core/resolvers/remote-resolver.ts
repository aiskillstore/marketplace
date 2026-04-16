import type { SkillMetaV3 } from '../../types/index.js';

export interface RemoteResolver {
  provider: string;
  resolve(ref: string): Promise<Partial<SkillMetaV3>>;
}
