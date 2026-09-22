export type ConstraintRole = 'frontend' | 'backend' | 'cache' | 'database' | 'queue' | 'security' | 'generic';
export type RuleApplicability = 'applicable' | 'conditional' | 'superseded' | 'conflict' | 'uncertain';
export type FreshnessStatus = 'unchanged' | 'changed' | 'missing' | 'unverified';
export interface ConstraintFreshness {
  checkedAt: string;
  head: string;
  rules: Record<string, {
    status: FreshnessStatus;
    baselineCommit?: string;
    reason?: 'no-baseline' | 'unavailable-baseline';
    files: Array<{ path: string; role: 'source' | 'code'; status: FreshnessStatus }>;
  }>;
}

export interface SourceHistory {
  complete: boolean;
  version: number | null;
  lastEdited: string | null;
  commit: string | null;
}

export interface SourceSection { id: string; title: string; level: number; line: number; endLine: number; text: string }
export interface ConstraintSource {
  id: string;
  path: string;
  kind: 'instruction' | 'skill' | 'reference';
  scope: string | null;
  discoveredFrom: string | null;
  applicability: string;
  text: string;
  sections: SourceSection[];
  history: SourceHistory;
}

export interface HistoryCommit { commit: string; date: string }
export interface TrackedRuleHistory {
  status: 'tracked';
  method: 'git-line-history';
  snapshot: string;
  sourcePath: string;
  line: number;
  endLine: number;
  version: number;
  lastEdited: string;
  commits: HistoryCommit[];
}
export interface UntrackedRuleHistory { status: 'untracked'; reason: string; snapshot: string }
export type RuleHistory = TrackedRuleHistory | UntrackedRuleHistory;

export interface ConstraintRule {
  id: string;
  name: string;
  sourcePath: string;
  line: number;
  endLine: number;
  category: string;
  topic?: { id: string; name: string };
  applicability: RuleApplicability;
  condition: string;
  explanation: string;
  verification: string;
  targetRole?: ConstraintRole;
  roleReason?: string;
  modules?: string[];
  history?: RuleHistory;
}

export interface ConstraintCatalog {
  schema: 'birdview.constraint-catalog/v1';
  project: { name: string; revision: string };
  coverage: {
    checkedAt: string;
    snapshot: string;
    shallow: boolean;
    entries: string[];
    checkedPaths: string[];
    excluded: Array<{ path: string; reason: string; target?: string }>;
    unresolved: Array<{ from: string; target: string; reason: string }>;
    uninspectedPaths: string[];
    semanticReview: string;
    limitations: string[];
  };
  references: Array<{ from: string; to: string; target: string }>;
  sources: ConstraintSource[];
  rules?: ConstraintRule[];
  architectureBinding?: { mapId: string; mapRevision: number; sourceRevision: string };
  ruleReview?: { scope: string; sourcePaths: string[]; reviewedAt: string; implementationVerification: 'unverified' };
}

export interface ReviewedConstraintCatalog extends ConstraintCatalog {
  rules: ConstraintRule[];
  ruleReview: NonNullable<ConstraintCatalog['ruleReview']>;
}

export interface ReviewedSelection {
  revision: string;
  scope: string;
  architectureBinding?: ConstraintCatalog['architectureBinding'];
  groups: Array<{
    sourcePath: string;
    category: string;
    topic?: { id: string; name: string };
    rules: Array<Omit<ConstraintRule, 'sourcePath' | 'line' | 'endLine' | 'category' | 'applicability'> & {
      anchor: string;
      applicability?: RuleApplicability;
      history?: RuleHistory;
    }>;
  }>;
}

export interface ConstraintGraphNode {
  id: string;
  parent: string | null;
  title: string;
  desc: string;
  role: ConstraintRole;
  label: string;
  kind: 'group' | 'rule' | 'source';
  modules?: string[];
  ordinal?: number;
  applicability?: RuleApplicability;
  version?: number;
  lastEdited?: string;
}
export interface ConstraintGraph {
  schema: 'birdview.constraint-view/v1';
  mode: 'rules' | 'sources';
  title: string;
  revision: string;
  scope: string;
  sourceHref?: string;
  roles?: Record<ConstraintRole, { name: string; dark: string[]; light: string[] }>;
  nodes: ConstraintGraphNode[];
  directoryNodes?: ConstraintGraphNode[];
  documents: Record<string, { body: string }>;
}
