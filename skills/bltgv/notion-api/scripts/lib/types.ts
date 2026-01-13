// Response types for script output
export type ScriptResponse<T> =
  | { status: "success"; data: T }
  | { status: "auth_required"; message: string; setupUrl: string }
  | { status: "error"; error: string };

// Notion API types
export interface NotionUser {
  object: "user";
  id: string;
  name?: string;
  avatar_url?: string;
  type?: "person" | "bot";
  person?: {
    email?: string;
  };
}

export interface NotionRichText {
  type: "text" | "mention" | "equation";
  text?: {
    content: string;
    link?: { url: string } | null;
  };
  mention?: {
    type: string;
    [key: string]: unknown;
  };
  equation?: {
    expression: string;
  };
  annotations?: {
    bold: boolean;
    italic: boolean;
    strikethrough: boolean;
    underline: boolean;
    code: boolean;
    color: string;
  };
  plain_text: string;
  href?: string | null;
}

export interface NotionPropertyValue {
  id: string;
  type: string;
  title?: NotionRichText[];
  rich_text?: NotionRichText[];
  number?: number | null;
  select?: { id: string; name: string; color: string } | null;
  multi_select?: Array<{ id: string; name: string; color: string }>;
  date?: { start: string; end?: string | null; time_zone?: string | null } | null;
  formula?: { type: string; [key: string]: unknown };
  relation?: Array<{ id: string }>;
  rollup?: { type: string; [key: string]: unknown };
  people?: NotionUser[];
  files?: Array<{ name: string; type: string; [key: string]: unknown }>;
  checkbox?: boolean;
  url?: string | null;
  email?: string | null;
  phone_number?: string | null;
  created_time?: string;
  created_by?: NotionUser;
  last_edited_time?: string;
  last_edited_by?: NotionUser;
  status?: { id: string; name: string; color: string } | null;
  unique_id?: { prefix?: string | null; number: number };
}

export interface NotionPage {
  object: "page";
  id: string;
  created_time: string;
  last_edited_time: string;
  created_by: NotionUser;
  last_edited_by: NotionUser;
  cover?: { type: string; [key: string]: unknown } | null;
  icon?: { type: string; [key: string]: unknown } | null;
  parent:
    | { type: "database_id"; database_id: string }
    | { type: "page_id"; page_id: string }
    | { type: "workspace"; workspace: true };
  archived: boolean;
  in_trash: boolean;
  properties: Record<string, NotionPropertyValue>;
  url: string;
}

export interface NotionDatabaseProperty {
  id: string;
  name: string;
  type: string;
  [key: string]: unknown;
}

export interface NotionDatabase {
  object: "database";
  id: string;
  created_time: string;
  last_edited_time: string;
  created_by: NotionUser;
  last_edited_by: NotionUser;
  title: NotionRichText[];
  description: NotionRichText[];
  icon?: { type: string; [key: string]: unknown } | null;
  cover?: { type: string; [key: string]: unknown } | null;
  properties: Record<string, NotionDatabaseProperty>;
  parent:
    | { type: "database_id"; database_id: string }
    | { type: "page_id"; page_id: string }
    | { type: "workspace"; workspace: true };
  url: string;
  archived: boolean;
  in_trash: boolean;
  is_inline: boolean;
}

export interface NotionBlock {
  object: "block";
  id: string;
  parent:
    | { type: "database_id"; database_id: string }
    | { type: "page_id"; page_id: string }
    | { type: "block_id"; block_id: string }
    | { type: "workspace"; workspace: true };
  created_time: string;
  last_edited_time: string;
  created_by: NotionUser;
  last_edited_by: NotionUser;
  has_children: boolean;
  archived: boolean;
  in_trash: boolean;
  type: string;
  [key: string]: unknown;
}

export interface NotionSearchResult {
  object: "list";
  results: Array<NotionPage | NotionDatabase>;
  next_cursor: string | null;
  has_more: boolean;
  type: "page_or_database";
}

export interface NotionBlockList {
  object: "list";
  results: NotionBlock[];
  next_cursor: string | null;
  has_more: boolean;
  type: "block";
}

export interface NotionDatabaseQueryResult {
  object: "list";
  results: NotionPage[];
  next_cursor: string | null;
  has_more: boolean;
  type: "page_or_database";
}

// Filter types for database queries
export interface NotionFilter {
  property?: string;
  [key: string]: unknown;
}

export interface NotionSort {
  property?: string;
  timestamp?: "created_time" | "last_edited_time";
  direction: "ascending" | "descending";
}
