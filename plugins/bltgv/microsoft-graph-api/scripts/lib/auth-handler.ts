/**
 * Auth Handler - Reusable authentication wrapper
 *
 * Provides a simple interface for scripts to ensure authentication
 * before making API calls. Handles token refresh and device code flow.
 */

import {
  getCredential,
  setCredential,
  isTokenExpired,
} from "./credentials";
import {
  getPendingAuth,
  setPendingAuth,
  deletePendingAuth,
  isPendingExpired,
  type PendingAuth,
} from "./pending-auth";
import {
  requestDeviceCode,
  pollForToken,
  refreshAccessToken,
} from "./device-code";
import type { Credential } from "./types";

const DEFAULT_CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e";
const DEFAULT_TENANT = "common";

export interface AuthHandlerOptions {
  service: string;
  profile: string;
  requiredScopes: string[];
  clientId?: string;
  tenantId?: string;
}

// Response types for scripts
export type ScriptResponse<T> =
  | { status: "success"; data: T }
  | {
      status: "auth_required";
      userCode: string;
      verificationUri: string;
      expiresAt: string;
      message: string;
    }
  | {
      status: "auth_pending";
      userCode: string;
      verificationUri: string;
      expiresAt: string;
      message: string;
    }
  | { status: "auth_expired"; message: string }
  | { status: "error"; error: string };

export type AuthResult<T> =
  | { ok: true; token: string }
  | { ok: false; response: ScriptResponse<T> };

/**
 * Ensure authentication is ready before making API calls.
 *
 * Usage:
 * ```typescript
 * const auth = await ensureAuth({
 *   service: "microsoft-graph",
 *   profile: "default",
 *   requiredScopes: ["Mail.Read"],
 * });
 *
 * if (!auth.ok) {
 *   console.log(JSON.stringify(auth.response));
 *   process.exit(1);
 * }
 *
 * // Use auth.token for API calls
 * ```
 */
export async function ensureAuth<T>(
  options: AuthHandlerOptions
): Promise<AuthResult<T>> {
  const {
    service,
    profile,
    requiredScopes,
    clientId = DEFAULT_CLIENT_ID,
    tenantId = DEFAULT_TENANT,
  } = options;

  // Step 1: Check for existing valid credential
  const credential = await getCredential(service, profile);

  if (credential) {
    // Step 2: Check if token is still valid (with 5 min buffer)
    if (!isTokenExpired(credential)) {
      return { ok: true, token: credential.accessToken };
    }

    // Token expired - try to refresh
    if (credential.refreshToken) {
      const refreshedToken = await refreshAccessToken(
        credential.clientId ?? clientId,
        credential.tenantId ?? tenantId,
        credential.refreshToken,
        requiredScopes
      );

      if (refreshedToken) {
        const expiresAt = new Date(
          Date.now() + refreshedToken.expiresIn * 1000
        ).toISOString();

        const newCredential: Credential = {
          accessToken: refreshedToken.accessToken,
          refreshToken: refreshedToken.refreshToken,
          expiresAt,
          account: credential.account,
          scopes: refreshedToken.scope?.split(" ") ?? credential.scopes,
          clientId: credential.clientId,
          tenantId: credential.tenantId,
        };

        await setCredential(service, profile, newCredential);
        return { ok: true, token: newCredential.accessToken };
      }
    }
  }

  // Step 3: Check for pending auth flow
  const pending = await getPendingAuth(service, profile);

  if (pending) {
    if (isPendingExpired(pending)) {
      // Pending auth expired - clean up and start fresh
      await deletePendingAuth(service, profile);
    } else {
      // Poll to see if user has completed authentication
      const pollResult = await pollForToken(
        pending.clientId,
        pending.tenantId,
        pending.deviceCode
      );

      if (pollResult.status === "success") {
        // User completed auth - save credential and return token
        const expiresAt = new Date(
          Date.now() + pollResult.token.expiresIn * 1000
        ).toISOString();

        // Extract account from token (basic JWT decode)
        let account = "unknown";
        try {
          const payload = JSON.parse(
            Buffer.from(
              pollResult.token.accessToken.split(".")[1],
              "base64"
            ).toString()
          );
          account =
            payload.preferred_username ||
            payload.upn ||
            payload.email ||
            "unknown";
        } catch {
          // Ignore decode errors
        }

        const newCredential: Credential = {
          accessToken: pollResult.token.accessToken,
          refreshToken: pollResult.token.refreshToken,
          expiresAt,
          account,
          scopes: pollResult.token.scope?.split(" ") ?? requiredScopes,
          clientId: pending.clientId,
          tenantId: pending.tenantId,
        };

        await setCredential(service, profile, newCredential);
        await deletePendingAuth(service, profile);
        return { ok: true, token: newCredential.accessToken };
      }

      if (pollResult.status === "pending") {
        // Still waiting for user
        return {
          ok: false,
          response: {
            status: "auth_pending",
            userCode: pending.userCode,
            verificationUri: pending.verificationUri,
            expiresAt: pending.expiresAt,
            message: `Authentication in progress. Go to ${pending.verificationUri} and enter code: ${pending.userCode}`,
          },
        };
      }

      if (pollResult.status === "expired") {
        // Device code expired - clean up
        await deletePendingAuth(service, profile);
      }

      // Error case - clean up and fall through to start new flow
      if (pollResult.status === "error") {
        await deletePendingAuth(service, profile);
      }
    }
  }

  // Step 4: Start new device code flow
  try {
    const deviceCode = await requestDeviceCode(clientId, tenantId, requiredScopes);

    const expiresAt = new Date(
      Date.now() + deviceCode.expiresIn * 1000
    ).toISOString();

    const newPending: PendingAuth = {
      deviceCode: deviceCode.deviceCode,
      userCode: deviceCode.userCode,
      verificationUri: deviceCode.verificationUri,
      expiresAt,
      clientId,
      tenantId,
      scopes: requiredScopes,
      profile,
    };

    await setPendingAuth(service, profile, newPending);

    return {
      ok: false,
      response: {
        status: "auth_required",
        userCode: deviceCode.userCode,
        verificationUri: deviceCode.verificationUri,
        expiresAt,
        message: deviceCode.message,
      },
    };
  } catch (error) {
    return {
      ok: false,
      response: {
        status: "error",
        error:
          error instanceof Error
            ? error.message
            : "Failed to start authentication",
      },
    };
  }
}
