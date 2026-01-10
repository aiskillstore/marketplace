#!/usr/bin/env bun
/**
 * Microsoft Graph Authentication Script
 *
 * Manual authentication and credential management.
 * Note: For normal use, authentication is handled automatically by
 * emails.ts and calendar.ts - this script is only needed for:
 * - Listing credential profiles
 * - Deleting credential profiles
 * - Interactive authentication with custom Azure AD apps
 *
 * Usage:
 *   bun run auth.ts [--profile <name>] [--client-id <id>] [--tenant-id <id>]
 *
 * Options:
 *   --profile     Credential profile name (default: "default")
 *   --client-id   Azure AD application (client) ID
 *   --tenant-id   Azure AD tenant ID (default: "common" for multi-tenant)
 *   --scopes      Comma-separated list of scopes (default: all scopes)
 *   --list        List all stored credential profiles
 *   --delete      Delete a credential profile
 *
 * Examples:
 *   bun run auth.ts --list
 *   bun run auth.ts --delete --profile old-account
 *   bun run auth.ts --client-id your-app-id --tenant-id your-tenant-id
 */

import { parseArgs } from "util";
import { PublicClientApplication } from "@azure/msal-node";
import { GRAPH_SCOPES } from "./lib/graph-client";
import {
  listProfiles,
  getCredential,
  setCredential,
  deleteCredential,
} from "./lib/credentials";
import type { Credential } from "./lib/types";

const DEFAULT_CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e";
const DEFAULT_TENANT = "common";

const { values } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    profile: { type: "string", default: "default" },
    "client-id": { type: "string" },
    "tenant-id": { type: "string" },
    scopes: { type: "string" },
    list: { type: "boolean", default: false },
    delete: { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
});

if (values.help) {
  console.log(`
Microsoft Graph Authentication

Usage:
  bun run auth.ts [options]

Options:
  --profile <name>      Credential profile name (default: "default")
  --client-id <id>      Azure AD application (client) ID
  --tenant-id <id>      Azure AD tenant ID (default: "common" for multi-tenant)
  --scopes <scopes>     Comma-separated list of scopes
  --list                List all stored credential profiles
  --delete              Delete a credential profile
  -h, --help            Show this help message

Note:
  For normal email and calendar access, authentication is handled automatically.
  This script is only needed for managing profiles or using custom Azure AD apps.

Using Your Own App Registration:
  1. Go to https://portal.azure.com
  2. Navigate to Azure Active Directory > App registrations
  3. Create a new registration:
     - Name: Your app name
     - Supported account types: Choose based on your needs
     - Redirect URI: Select "Public client/native" and add:
       https://login.microsoftonline.com/common/oauth2/nativeclient
  4. Go to "Authentication" and enable "Allow public client flows"
  5. Go to "API permissions" and add:
     - Microsoft Graph > Delegated > Mail.Read
     - Microsoft Graph > Delegated > Calendars.Read
     - Microsoft Graph > Delegated > User.Read
  6. Copy the "Application (client) ID" from Overview
  7. Use it with: --client-id your-app-id

Examples:
  # List all profiles
  bun run auth.ts --list

  # Delete a profile
  bun run auth.ts --delete --profile old

  # Authenticate with your own app
  bun run auth.ts --client-id 12345678-1234-1234-1234-123456789abc

  # Authenticate with single-tenant app
  bun run auth.ts --client-id your-app-id --tenant-id your-tenant-id
`);
  process.exit(0);
}

async function main() {
  if (values.list) {
    const profiles = await listProfiles("microsoft-graph");
    if (profiles.length === 0) {
      console.log("No credential profiles found.");
      console.log("Authentication is handled automatically when using email or calendar scripts.");
    } else {
      console.log("Microsoft Graph credential profiles:\n");
      for (const profile of profiles) {
        const cred = await getCredential("microsoft-graph", profile);
        if (cred) {
          const expired = new Date(cred.expiresAt) < new Date();
          console.log(`  ${profile}:`);
          console.log(`    Account: ${cred.account}`);
          console.log(`    Scopes: ${cred.scopes.join(", ")}`);
          if (cred.clientId) {
            console.log(`    Client ID: ${cred.clientId}`);
          }
          if (cred.tenantId) {
            console.log(`    Tenant ID: ${cred.tenantId}`);
          }
          console.log(`    Token Status: ${expired ? "EXPIRED (will refresh)" : "Valid"}`);
          console.log();
        }
      }
    }
    return;
  }

  if (values.delete) {
    const deleted = await deleteCredential("microsoft-graph", values.profile!);
    if (deleted) {
      console.log(`Deleted credential profile: ${values.profile}`);
    } else {
      console.log(`Profile not found: ${values.profile}`);
    }
    return;
  }

  // Interactive authentication
  const scopes = values.scopes
    ? values.scopes.split(",").map((s) => s.trim())
    : [...GRAPH_SCOPES.user, ...GRAPH_SCOPES.mail, ...GRAPH_SCOPES.calendar];

  const clientId = values["client-id"] ?? DEFAULT_CLIENT_ID;
  const tenantId = values["tenant-id"] ?? DEFAULT_TENANT;

  console.log(`Authenticating with Microsoft Graph...`);
  console.log(`Profile: ${values.profile}`);
  if (values["client-id"]) {
    console.log(`Client ID: ${clientId}`);
  } else {
    console.log(`Client ID: (using default Graph Explorer client)`);
  }
  if (values["tenant-id"]) {
    console.log(`Tenant ID: ${tenantId}`);
  }
  console.log(`Scopes: ${scopes.join(", ")}\n`);

  try {
    const pca = new PublicClientApplication({
      auth: {
        clientId,
        authority: `https://login.microsoftonline.com/${tenantId}`,
      },
    });

    const result = await pca.acquireTokenByDeviceCode({
      scopes,
      deviceCodeCallback: (response) => {
        console.log(`\nTo authenticate, please:`);
        console.log(`1. Go to: ${response.verificationUri}`);
        console.log(`2. Enter code: ${response.userCode}`);
        console.log(`\nWaiting for authentication...`);
      },
    });

    if (result) {
      const credential: Credential = {
        accessToken: result.accessToken,
        refreshToken: (result as any).refreshToken ?? "",
        expiresAt: result.expiresOn?.toISOString() ?? new Date(Date.now() + 3600000).toISOString(),
        account: result.account?.username ?? "unknown",
        scopes: result.scopes?.length > 0 ? result.scopes : scopes,
        clientId: values["client-id"] ? clientId : undefined,
        tenantId: values["tenant-id"] ? tenantId : undefined,
      };

      await setCredential("microsoft-graph", values.profile!, credential);

      console.log("\nAuthentication successful!");
      console.log(`  Account: ${credential.account}`);
      console.log(`  Expires: ${new Date(credential.expiresAt).toLocaleString()}`);
      console.log(`\nCredentials saved to profile: ${values.profile}`);
    }
  } catch (error) {
    console.error("Authentication failed:", error);
    process.exit(1);
  }
}

main();
