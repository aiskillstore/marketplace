import {
  PublicClientApplication,
  DeviceCodeRequest,
  AuthenticationResult,
} from "@azure/msal-node";
import {
  getCredential,
  setCredential,
  isTokenExpired,
} from "./credentials";
import type { Credential } from "./types";

// Microsoft Graph API scopes
export const GRAPH_SCOPES = {
  mail: ["Mail.Read", "Mail.ReadBasic"],
  mailSend: ["Mail.Send"],
  calendar: ["Calendars.Read"],
  calendarWrite: ["Calendars.ReadWrite"],
  user: ["User.Read"],
};

// Default client ID for device code flow (Microsoft Graph Explorer)
// Users should register their own app for production use
const DEFAULT_CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e";
const DEFAULT_TENANT = "common";

export interface GraphClientOptions {
  profile?: string;
  clientId?: string;
  tenantId?: string;
}

export class GraphClient {
  private profile: string;
  private clientId: string;
  private tenantId: string;
  private pca: PublicClientApplication | null = null;

  constructor(options: GraphClientOptions = {}) {
    this.profile = options.profile ?? "default";
    this.clientId = options.clientId ?? DEFAULT_CLIENT_ID;
    this.tenantId = options.tenantId ?? DEFAULT_TENANT;
  }

  private async initPca(): Promise<PublicClientApplication> {
    if (this.pca) return this.pca;

    // Try to load clientId from stored credentials if using defaults
    if (this.clientId === DEFAULT_CLIENT_ID) {
      const credential = await getCredential("microsoft-graph", this.profile);
      if (credential?.clientId) {
        this.clientId = credential.clientId;
      }
      if (credential?.tenantId) {
        this.tenantId = credential.tenantId;
      }
    }

    this.pca = new PublicClientApplication({
      auth: {
        clientId: this.clientId,
        authority: `https://login.microsoftonline.com/${this.tenantId}`,
      },
    });

    return this.pca;
  }

  async getAccessToken(requiredScopes: string[]): Promise<string> {
    const credential = await getCredential("microsoft-graph", this.profile);

    if (credential && !isTokenExpired(credential)) {
      // Check if we have all required scopes
      const hasAllScopes = requiredScopes.every((scope) =>
        credential.scopes.some(
          (s) => s.toLowerCase() === scope.toLowerCase()
        )
      );
      if (hasAllScopes) {
        return credential.accessToken;
      }
    }

    // Try silent token acquisition with refresh token
    if (credential?.refreshToken) {
      try {
        const pca = await this.initPca();
        const result = await pca.acquireTokenByRefreshToken({
          refreshToken: credential.refreshToken,
          scopes: requiredScopes,
        });

        if (result) {
          await this.saveAuthResult(result, requiredScopes);
          return result.accessToken;
        }
      } catch {
        // Refresh failed, need interactive auth
      }
    }

    // Need interactive auth - throw error with instructions
    throw new Error(
      `No valid token for profile "${this.profile}". Run auth first:\n` +
        `bun run ${process.env.CLAUDE_PLUGIN_ROOT}/skills/microsoft-graph/scripts/auth.ts --profile ${this.profile}`
    );
  }

  async authenticate(scopes: string[]): Promise<AuthenticationResult> {
    const pca = await this.initPca();

    const deviceCodeRequest: DeviceCodeRequest = {
      scopes,
      deviceCodeCallback: (response) => {
        console.log("\n" + response.message);
        console.log("\nWaiting for authentication...\n");
      },
    };

    const result = await pca.acquireTokenByDeviceCode(deviceCodeRequest);
    if (!result) {
      throw new Error("Authentication failed: no result returned");
    }
    await this.saveAuthResult(result, scopes);
    return result;
  }

  private async saveAuthResult(
    result: AuthenticationResult,
    requestedScopes: string[]
  ): Promise<void> {
    // Get scopes from the result, or use requested scopes if not available
    const scopes = result.scopes?.length > 0 ? result.scopes : requestedScopes;

    const credential: Credential = {
      accessToken: result.accessToken,
      refreshToken: (result as any).refreshToken ?? "",
      expiresAt: result.expiresOn?.toISOString() ?? new Date(Date.now() + 3600000).toISOString(),
      account: result.account?.username ?? "unknown",
      scopes,
      clientId: this.clientId !== DEFAULT_CLIENT_ID ? this.clientId : undefined,
      tenantId: this.tenantId !== DEFAULT_TENANT ? this.tenantId : undefined,
    };

    await setCredential("microsoft-graph", this.profile, credential);
  }

  async graphRequest<T>(
    endpoint: string,
    scopes: string[],
    options: RequestInit = {}
  ): Promise<T> {
    const token = await this.getAccessToken(scopes);

    const response = await fetch(`https://graph.microsoft.com/v1.0${endpoint}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Graph API error (${response.status}): ${error}`);
    }

    return response.json();
  }

  getClientId(): string {
    return this.clientId;
  }

  getTenantId(): string {
    return this.tenantId;
  }
}
