/**
 * Device Code Flow - Direct Azure HTTP API
 *
 * Handles device code OAuth flow without MSAL for non-blocking operation.
 * Uses direct HTTP requests to Azure AD endpoints.
 */

export interface DeviceCodeResponse {
  deviceCode: string;
  userCode: string;
  verificationUri: string;
  expiresIn: number;
  interval: number;
  message: string;
}

export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  scope: string;
}

export type PollResult =
  | { status: "success"; token: TokenResponse }
  | { status: "pending" }
  | { status: "expired" }
  | { status: "error"; error: string };

/**
 * Request a device code from Azure AD
 */
export async function requestDeviceCode(
  clientId: string,
  tenantId: string,
  scopes: string[]
): Promise<DeviceCodeResponse> {
  const url = `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/devicecode`;

  const body = new URLSearchParams({
    client_id: clientId,
    scope: scopes.join(" "),
  });

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Device code request failed: ${response.status} - ${error}`);
  }

  const data = await response.json();

  return {
    deviceCode: data.device_code,
    userCode: data.user_code,
    verificationUri: data.verification_uri,
    expiresIn: data.expires_in,
    interval: data.interval || 5,
    message: data.message,
  };
}

/**
 * Poll Azure AD to check if user has completed authentication
 */
export async function pollForToken(
  clientId: string,
  tenantId: string,
  deviceCode: string
): Promise<PollResult> {
  const url = `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`;

  const body = new URLSearchParams({
    client_id: clientId,
    grant_type: "urn:ietf:params:oauth:grant-type:device_code",
    device_code: deviceCode,
  });

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: body.toString(),
    });

    const data = await response.json();

    if (response.ok) {
      return {
        status: "success",
        token: {
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          expiresIn: data.expires_in,
          scope: data.scope,
        },
      };
    }

    // Handle specific error codes
    const errorCode = data.error;

    if (errorCode === "authorization_pending") {
      return { status: "pending" };
    }

    if (errorCode === "expired_token") {
      return { status: "expired" };
    }

    // Other errors (authorization_declined, bad_verification_code, etc.)
    return {
      status: "error",
      error: data.error_description || data.error || "Unknown error",
    };
  } catch (error) {
    return {
      status: "error",
      error: error instanceof Error ? error.message : "Network error",
    };
  }
}

/**
 * Refresh an access token using a refresh token
 */
export async function refreshAccessToken(
  clientId: string,
  tenantId: string,
  refreshToken: string,
  scopes: string[]
): Promise<TokenResponse | null> {
  const url = `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`;

  const body = new URLSearchParams({
    client_id: clientId,
    grant_type: "refresh_token",
    refresh_token: refreshToken,
    scope: scopes.join(" "),
  });

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: body.toString(),
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();

    return {
      accessToken: data.access_token,
      refreshToken: data.refresh_token || refreshToken,
      expiresIn: data.expires_in,
      scope: data.scope,
    };
  } catch {
    return null;
  }
}
