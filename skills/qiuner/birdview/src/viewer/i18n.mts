export const uiTranslations: Readonly<Record<string, string>> = {
  '架构标识': 'Architecture identity',
  '前端': 'Frontend', '后端': 'Backend', '缓存': 'Cache', '数据存储': 'Data store',
  '任务与队列': 'Tasks / Queue', '安全': 'Security', '通用模块': 'Generic',
  '关闭详情': 'Close details', '查看详情': 'Inspect module',
  '看见 AI 如何改变你的系统': 'See how AI changes your system',
  '架构快照': 'Architecture snapshot',
  '系统架构': 'System architecture', '项目架构': 'Project architecture',
  '缩小': 'Zoom out', '放大': 'Zoom in', '缩放比例': 'Zoom level',
  '适配全图': 'Fit diagram', '原始大小': 'Actual size', '模块关系': 'Module relationships',
  '架构快照 · 尚无修改活动': 'Architecture snapshot · No change activity',
  '模块详情': 'Module details', '文件归属': 'File ownership', '源码证据': 'Source evidence',
  '待确认': 'Uncertain', '相关连接': 'Related connections',
  '切换到深色': 'Switch to dark theme', '切换到浅色': 'Switch to light theme',
  '关系方向动画，不代表实时数据传输': 'Relationship direction, not live data transfer',
  '流向': 'Flow', '外部服务': 'External service', '本地模块': 'Local module',
  '有来源证据': 'Source-backed', '无本地文件归属': 'No local file ownership',
  '无来源证据': 'No source evidence', '无已记录的待确认项': 'No recorded open questions',
  '无已记录的关系': 'No recorded relationships'
};

export interface LanguageSource {
  translations?: Record<string, object>;
  evidence?: readonly LanguageSource[];
}
export interface LanguageMap {
  language?: string;
  project: LanguageSource;
  modules: readonly LanguageSource[];
  relationships: readonly LanguageSource[];
  groups?: readonly LanguageSource[];
  constraints?: readonly LanguageSource[];
}
export function availableLanguages(map: LanguageMap): Set<string> {
  const languages = new Set([map.language || 'zh', 'zh', 'en']);
  for (const item of [map.project, ...map.modules, ...map.relationships, ...(map.groups || []), ...(map.constraints || [])]) {
    for (const locale of Object.keys(item.translations || {})) languages.add(locale);
    for (const source of item.evidence || []) for (const locale of Object.keys(source.translations || {})) languages.add(locale);
  }
  return languages;
}
export function selectLanguage(base: string | undefined, available: ReadonlySet<string>, stored: string | null, requested: string | null): string {
  let language = base || 'zh';
  if (stored !== null && available.has(stored)) language = stored;
  if (requested !== null && available.has(requested)) language = requested;
  return language;
}
export const isChinese = (language: string): boolean => language.split('-')[0] === 'zh';
export const translate = (text: string, language: string): string => isChinese(language) ? text : (uiTranslations[text] || text);
export type TextField = 'name' | 'responsibility' | 'label' | 'note' | 'explanation' | 'verification' | 'reason' | 'summary' | 'plan' | 'evidence';
export type LocalizedText = Partial<Record<TextField, string>> & { openQuestions?: string[] };
export function localized<K extends keyof LocalizedText>(item: Partial<Pick<LocalizedText, K>> & {
  translations?: Record<string, Partial<Pick<LocalizedText, K>>>;
}, field: K, language: string) {
  return item.translations?.[language]?.[field] ?? item[field] ?? '';
}
