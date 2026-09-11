/** Default for short API model steps; durable agents declare their own model. */
export const DEFAULT_WORKFLOW_MODEL = "deepseek/deepseek-v4.1-flash";

export function workflowModel(model?: string): string {
  return model ?? (process.env.GTM_WORKFLOW_MODEL?.trim() || process.env.GTM_AGENT_MODEL?.trim() || DEFAULT_WORKFLOW_MODEL);
}
