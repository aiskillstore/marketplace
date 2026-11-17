export interface AnyvizTheme {
  name: string;
  version: string;
  description: string;
  color: Record<string, unknown>;
  typography: Record<string, unknown>;
  layout: Record<string, unknown>;
  [key: string]: unknown;
}

export interface AnyvizPackage {
  root: string;
  version: string;
  skillPath: string;
  resolve: (subpath: string) => string;
  guides: {
    chartSelection: string;
    colorGuide: string;
    academicPublication: string;
    consistencyRules: string;
    customizationGuide: string;
    legendLayout: string;
    accessibility: string;
  };
  defaultTheme: () => AnyvizTheme;
  themes: {
    modern: () => AnyvizTheme;
    analytics: () => AnyvizTheme;
    dashboard: () => AnyvizTheme;
    academic: () => AnyvizTheme;
  };
}

declare const anyviz: AnyvizPackage;
export = anyviz;
