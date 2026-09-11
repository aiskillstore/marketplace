export type HeadCheckFailure = { status: 409; code: "deployment_head_required" | "deployment_not_ready"; message: string };

/**
 * Production starts must name the workspace commit the caller expects to be live.
 * A local server has no deployed commit, so it never checks the header.
 */
export function headCheck(input: { method: "GET" | "POST"; expectedHead: string | null; deployedHead: string | undefined }): HeadCheckFailure | null {
  if (input.method !== "POST" || !input.deployedHead) return null;
  if (input.expectedHead === null) {
    return { status: 409, code: "deployment_head_required", message: "Production starts require the accepted workspace commit." };
  }
  if (input.expectedHead !== input.deployedHead) {
    return { status: 409, code: "deployment_not_ready", message: "Production is not serving the requested workspace commit." };
  }
  return null;
}
