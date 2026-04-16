export type InstallScope = 'global' | 'local';

// V2 legacy types
export type LegacySourceType = 'git' | 'curl' | 'local';

export interface LegacySkillSource {
  type: LegacySourceType;
  url: string;
  path?: string;
  ref?: string;
}

export interface LegacySkillBundle {
  path: string;
}

export interface SkillTransformRule {
  remove_frontmatter?: string[];
  map_tools?: Record<string, string>;
  inject_header?: string;
  strip_bash_preamble?: boolean;
}

// V2 legacy SkillMeta (kept for migration)
export interface LegacySkillMeta {
  name: string;
  display_name: string;
  description: string;
  category: string;
  tags: string[];
  source?: LegacySkillSource;
  bundle?: LegacySkillBundle;
  author?: string;
  version?: string;
  license?: string;
  agent?: string;
  transform?: Record<string, SkillTransformRule>;
}

// V3 types
export type OriginType = 'bundle' | 'git' | 'github' | 'clawhub' | 'skillstore';

export interface SkillOrigin {
  type: OriginType;
  /** Remote reference like owner/repo or repo-name (for github/clawhub/skillstore) */
  ref?: string;
  /** Local path for bundle, or sub-path inside git repo */
  path?: string;
  /** Full git URL (for git type) */
  url?: string;
  /** Git branch/tag (default: main) */
  refName?: string;
}

export interface SkillMetaV3 {
  name: string;
  displayName: string;
  description: string;
  category: string;
  tags: string[];
  origin: SkillOrigin;
  author?: string;
  version?: string;
  license?: string;
  agent?: string;
  transform?: Record<string, SkillTransformRule>;
}

// Unified SkillMeta used by Engine (backward-compatible shape)
export interface SkillMeta {
  name: string;
  display_name: string;
  description: string;
  category: string;
  tags: string[];
  source?: LegacySkillSource;
  bundle?: LegacySkillBundle;
  author?: string;
  version?: string;
  license?: string;
  agent?: string;
  transform?: Record<string, SkillTransformRule>;
}

export interface CategoryGroupV3 {
  id: string;
  displayName: string;
  order: number;
}

export interface RegistryV3 {
  version: string;
  updatedAt: string;
  categories: CategoryGroupV3[];
  skills: SkillMetaV3[];
}

export interface CategoryGroup {
  id: string;
  displayName: string;
  skills: SkillMeta[];
}

export interface InstallResult {
  skill: SkillMeta;
  success: boolean;
  message: string;
  targetPath: string;
}

export interface EditorPreset {
  id: string;
  name: string;
  filePath: string;
  type: 'file' | 'directory';
  defaultEnabled: boolean;
  isSkillType: boolean;
}

export interface MarkerBlock {
  type: 'source' | 'rule' | 'user' | 'file';
  source?: string;
  id?: string;
  priority?: string;
  count?: number;
  content: string;
  raw: string;
}
