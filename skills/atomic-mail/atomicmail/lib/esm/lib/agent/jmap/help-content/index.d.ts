export declare const HELP_TOPICS: Record<string, string>;
export declare const HELP_TOPIC_LIST: string[];
export declare function normalizeHelpTopic(topic: string): string;
export type HelpRuntime = "mcp" | "skill";
export declare function getHelp(topic?: string, runtime?: HelpRuntime): Promise<string>;
//# sourceMappingURL=index.d.ts.map