/// <reference types="node" />
import { fileURLToPath } from "url";
import path from "path";
import dotenv from "dotenv";

// 自动加载 .env 文件（从脚本目录向上查找）
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 尝试多个位置加载 .env
const envPaths = [
  path.resolve(__dirname, "../../../../.env"),  // deepresearch/.env
  path.resolve(__dirname, "../../../.env"),     // skills/.env
  path.resolve(process.cwd(), ".env"),          // 当前工作目录
];

for (const envPath of envPaths) {
  const result = dotenv.config({ path: envPath });
  if (!result.error) {
    console.error(`[Dify Client] Loaded env from: ${envPath}`);
    break;
  }
}

/**
 * Dify Code Research Workflow Client
 *
 * 调用 Dify 平台上的 Code Research Skill 工作流
 * 工作流结构:
 *   Start → Background Search → Task Analysis → Research Loop → Implementation Guide → End
 *
 * 输入参数:
 *   - coding_task: 编码任务描述 (必填)
 *   - tech_stack: 技术栈上下文 (可选)
 *   - max_iterations: 研究深度 1-5 (可选, 默认 3)
 *
 * 输出:
 *   - analysis: 任务分析 JSON (来自 Task Analysis 节点)
 *   - guide: 实现指南 Markdown (来自 Implementation Guide 节点)
 */

interface DifyConfig {
  apiKey: string;
  baseUrl: string;
  workflowId?: string;
}

interface ResearchRequest {
  codingTask: string;
  techStack?: string;
  depth?: number; // 1-5, 默认 3
}

interface TaskAnalysis {
  task_summary: string;
  task_type: "bug_fix" | "feature" | "refactor" | "optimization" | "integration" | "architecture";
  tech_requirements: {
    languages: string[];
    frameworks: string[];
    libraries: string[];
    apis: string[];
  };
  implementation_scope: {
    files_to_create: string[];
    files_to_modify: string[];
    estimated_complexity: "low" | "medium" | "high";
  };
  knowledge_gaps: Array<{
    topic: string;
    priority: number;
    search_focus: "docs" | "examples" | "stackoverflow" | "github";
  }>;
  critical_decisions: string[];
  search_queries: string[];
}

interface ResearchResponse {
  success: boolean;
  data?: {
    analysis: string; // Task Analysis JSON string
    guide: string;    // Implementation Guide Markdown
  };
  metadata?: {
    duration_ms: number;
    workflow_run_id: string;
  };
  error?: string;
}

export class DifyResearchClient {
  private config: DifyConfig;

  constructor(config: Partial<DifyConfig> = {}) {
    this.config = {
      baseUrl: config.baseUrl || process.env.DIFY_BASE_URL || "https://api.dify.ai/v1",
      apiKey: config.apiKey || process.env.DIFY_API_KEY || "",
      workflowId: config.workflowId || process.env.DIFY_WORKFLOW_ID,
    };

    if (!this.config.apiKey) {
      throw new Error("DIFY_API_KEY is required");
    }
  }

  /**
   * 执行代码研究工作流 (使用 streaming 模式避免超时)
   */
  async research(request: ResearchRequest): Promise<ResearchResponse> {
    const { codingTask, techStack = "", depth = 3 } = request;

    // 验证 depth 范围
    const validDepth = Math.max(1, Math.min(5, depth));

    console.error(`[Dify Client] Starting research workflow...`);
    console.error(`[Dify Client] Task: ${codingTask.substring(0, 100)}${codingTask.length > 100 ? "..." : ""}`);
    console.error(`[Dify Client] Tech Stack: ${techStack || "(not specified)"}`);
    console.error(`[Dify Client] Depth: ${validDepth}`);
    console.error(`[Dify Client] Connecting to ${this.config.baseUrl}...`);

    const startTime = Date.now();

    try {
      // 调用 Dify Workflow API (使用 streaming 模式)
      const response = await fetch(`${this.config.baseUrl}/workflows/run`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${this.config.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          inputs: {
            coding_task: codingTask,
            tech_stack: techStack,
            max_iterations: String(validDepth),
          },
          response_mode: "streaming",
          user: "terminal-agent",
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[Dify Client] API Error: ${response.status}`);
        return {
          success: false,
          error: `Dify API error: ${response.status} - ${errorText}`,
        };
      }

      // 处理 SSE 流式响应
      const reader = response.body?.getReader();
      if (!reader) {
        return { success: false, error: "No response body" };
      }

      const decoder = new TextDecoder();
      let analysis = "";
      let guide = "";
      let workflowRunId = "";
      let buffer = "";

      console.error(`[Dify Client] Receiving streaming response...`);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // 保留不完整的行

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.slice(6).trim();
            if (jsonStr === "" || jsonStr === "[DONE]") continue;

            try {
              const event = JSON.parse(jsonStr) as {
                event: string;
                workflow_run_id?: string;
                data?: {
                  title?: string;
                  outputs?: {
                    analysis?: string;
                    guide?: string;
                  };
                };
              };

              if (event.workflow_run_id) {
                workflowRunId = event.workflow_run_id;
              }

              // 处理不同事件类型
              if (event.event === "node_started" && event.data?.title) {
                console.error(`[Dify Client] ▶ ${event.data.title}`);
              } else if (event.event === "node_finished" && event.data?.title) {
                console.error(`[Dify Client] ✓ ${event.data.title}`);
              } else if (event.event === "workflow_finished") {
                const outputs = event.data?.outputs || {};
                analysis = outputs.analysis || "";
                guide = outputs.guide || "";
                console.error(`[Dify Client] ✓ Workflow finished`);
              }
            } catch {
              // 忽略解析错误的行
            }
          }
        }
      }

      const duration = Date.now() - startTime;
      console.error(`[Dify Client] Completed in ${(duration / 1000).toFixed(1)}s`);

      if (!analysis && !guide) {
        return {
          success: false,
          error: "Workflow completed but no outputs received",
        };
      }

      return {
        success: true,
        data: {
          analysis,
          guide,
        },
        metadata: {
          duration_ms: duration,
          workflow_run_id: workflowRunId,
        },
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error(`[Dify Client] Error: ${errorMessage}`);
      return {
        success: false,
        error: `Research failed: ${errorMessage}`,
      };
    }
  }

  /**
   * 解析 Task Analysis JSON
   */
  parseAnalysis(analysisJson: string): TaskAnalysis | null {
    try {
      // 尝试提取 JSON 块
      const jsonMatch = analysisJson.match(/```json\s*([\s\S]*?)\s*```/);
      const jsonStr = jsonMatch ? jsonMatch[1] : analysisJson;
      return JSON.parse(jsonStr) as TaskAnalysis;
    } catch {
      console.error("[Dify Client] Failed to parse task analysis JSON");
      return null;
    }
  }
}

// === CLI 入口 ===
const currentFilePath = fileURLToPath(import.meta.url);
const executeFilePath = process.argv[1];

// 兼容 Windows 和 Unix 路径比较
if (path.resolve(currentFilePath) === path.resolve(executeFilePath)) {
  const args = process.argv.slice(2);

  // 解析参数
  const codingTask = args[0];
  const techStack = args[1] || "";
  const depth = parseInt(args[2] || "3", 10);

  if (!codingTask) {
    console.error("Usage: npx tsx dify-client.ts <coding_task> [tech_stack] [depth]");
    console.error("");
    console.error("Arguments:");
    console.error("  coding_task  The coding task or question to research (required)");
    console.error("  tech_stack   Technology stack context (optional)");
    console.error("  depth        Research depth 1-5 (optional, default: 3)");
    console.error("");
    console.error("Examples:");
    console.error("  npx tsx dify-client.ts \"How to implement OAuth2 in Next.js\"");
    console.error("  npx tsx dify-client.ts \"Add WebSocket support\" \"React, Node.js\" 4");
    console.error("");
    console.error("Environment variables:");
    console.error("  DIFY_API_KEY    Dify API key (required)");
    console.error("  DIFY_BASE_URL   Dify API base URL (default: https://api.dify.ai/v1)");
    process.exit(1);
  }

  // 检查 API Key
  if (!process.env.DIFY_API_KEY) {
    console.error("Error: DIFY_API_KEY not found in environment variables.");
    console.error("Please set DIFY_API_KEY in your .env file or environment.");
    process.exit(1);
  }

  // 执行研究
  const client = new DifyResearchClient();

  client
    .research({
      codingTask,
      techStack,
      depth,
    })
    .then((result) => {
      if (result.success) {
        // 成功：输出 JSON 到 stdout
        console.log(JSON.stringify(result, null, 2));
      } else {
        // 失败：输出错误到 stderr
        console.error("Research Failed:", result.error);
        process.exit(1);
      }
    })
    .catch((err) => {
      console.error("Unexpected Error:", err);
      process.exit(1);
    });
}
