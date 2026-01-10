#!/usr/bin/env bun
/**
 * Microsoft Graph Email Script
 *
 * Read, list, search, and send emails via Microsoft Graph API.
 * Authentication is handled automatically - if needed, returns auth instructions.
 *
 * Usage:
 *   bun run emails.ts <command> [options]
 *
 * Commands:
 *   list      List emails from a folder
 *   read      Read a specific email by ID
 *   search    Search emails
 *   folders   List mail folders
 *   send      Send an email
 *
 * Options:
 *   --profile    Credential profile (default: "default")
 *   --folder     Folder name or ID (default: "inbox")
 *   --top        Number of results (default: 10)
 *   --query      Search query for 'search' command
 *   --id         Email ID for 'read' command
 *   --to         Recipient email(s) for 'send' (comma-separated)
 *   --cc         CC recipient(s) for 'send' (comma-separated)
 *   --bcc        BCC recipient(s) for 'send' (comma-separated)
 *   --subject    Email subject for 'send'
 *   --body       Email body for 'send'
 *   --html       Send body as HTML (default: plain text)
 *
 * Output:
 *   Always JSON with structure:
 *   - Success: { "status": "success", "data": [...] }
 *   - Auth needed: { "status": "auth_required", "userCode": "...", "verificationUri": "..." }
 *   - Error: { "status": "error", "error": "..." }
 */

import { parseArgs } from "util";
import { GRAPH_SCOPES } from "./lib/graph-client";
import { ensureAuth, type ScriptResponse } from "./lib/auth-handler";
import type { GraphEmail, MailFolder } from "./lib/types";

const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    profile: { type: "string", default: "default" },
    folder: { type: "string", default: "inbox" },
    top: { type: "string", default: "10" },
    query: { type: "string" },
    id: { type: "string" },
    to: { type: "string" },
    cc: { type: "string" },
    bcc: { type: "string" },
    subject: { type: "string" },
    body: { type: "string" },
    html: { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: true,
});

const command = positionals[0];

if (values.help) {
  console.log(`
Microsoft Graph Email Access

Usage:
  bun run emails.ts <command> [options]

Commands:
  list      List emails from a folder
  read      Read a specific email by ID
  search    Search emails
  folders   List mail folders
  send      Send an email

Options:
  --profile <name>    Credential profile (default: "default")
  --folder <name>     Folder name or ID (default: "inbox")
  --top <n>           Number of results (default: 10)
  --query <q>         Search query (for 'search' command)
  --id <id>           Email ID (for 'read' command)
  --to <emails>       Recipient email(s), comma-separated (for 'send')
  --cc <emails>       CC recipient(s), comma-separated (for 'send')
  --bcc <emails>      BCC recipient(s), comma-separated (for 'send')
  --subject <text>    Email subject (for 'send')
  --body <text>       Email body (for 'send')
  --html              Send body as HTML instead of plain text
  -h, --help          Show this help message

Output:
  JSON with status field indicating success, auth_required, auth_pending, or error.

Search Query Examples:
  from:sender@example.com
  subject:meeting
  hasAttachments:true
  received>=2024-01-01
  "exact phrase"

Examples:
  bun run emails.ts list
  bun run emails.ts list --folder "Sent Items" --top 5
  bun run emails.ts read --id AAMkAG...
  bun run emails.ts search --query "from:boss@company.com subject:urgent"
  bun run emails.ts folders
  bun run emails.ts send --to "user@example.com" --subject "Hello" --body "Hi there!"
  bun run emails.ts send --to "a@ex.com,b@ex.com" --cc "c@ex.com" --subject "Team Update" --body "<h1>Update</h1>" --html
`);
  process.exit(0);
}

function output<T>(response: ScriptResponse<T>): void {
  console.log(JSON.stringify(response));
  process.exit(response.status === "success" ? 0 : 1);
}

async function graphRequest<T>(token: string, endpoint: string): Promise<T> {
  const url = `https://graph.microsoft.com/v1.0${endpoint}`;

  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Graph API error: ${response.status} - ${error}`);
  }

  return response.json();
}

async function graphPost(token: string, endpoint: string, body: unknown): Promise<void> {
  const url = `https://graph.microsoft.com/v1.0${endpoint}`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Graph API error: ${response.status} - ${error}`);
  }
}

function parseRecipients(input: string): Array<{ emailAddress: { address: string } }> {
  return input
    .split(",")
    .map((email) => email.trim())
    .filter((email) => email.length > 0)
    .map((address) => ({ emailAddress: { address } }));
}

async function main() {
  if (!command) {
    output({ status: "error", error: "No command specified. Use --help for usage." });
    return;
  }

  // Determine required scopes based on command
  const requiredScopes = [...GRAPH_SCOPES.user];
  if (command === "send") {
    requiredScopes.push(...GRAPH_SCOPES.mailSend);
  } else {
    requiredScopes.push(...GRAPH_SCOPES.mail);
  }

  // Ensure we're authenticated
  const auth = await ensureAuth({
    service: "microsoft-graph",
    profile: values.profile!,
    requiredScopes,
  });

  if (!auth.ok) {
    output(auth.response);
    return;
  }

  const token = auth.token;
  const top = parseInt(values.top!, 10);

  try {
    switch (command) {
      case "list": {
        const folder = encodeURIComponent(values.folder!);
        const response = await graphRequest<{ value: GraphEmail[] }>(
          token,
          `/me/mailFolders/${folder}/messages?$top=${top}&$orderby=receivedDateTime desc`
        );

        output({
          status: "success",
          data: response.value.map((email) => ({
            id: email.id,
            subject: email.subject,
            from: email.from.emailAddress,
            receivedDateTime: email.receivedDateTime,
            bodyPreview: email.bodyPreview,
            isRead: email.isRead,
            hasAttachments: email.hasAttachments,
          })),
        });
        break;
      }

      case "read": {
        if (!values.id) {
          output({ status: "error", error: "--id is required for 'read' command" });
          return;
        }

        const email = await graphRequest<GraphEmail>(
          token,
          `/me/messages/${values.id}?$select=id,subject,from,receivedDateTime,body,bodyPreview,isRead,hasAttachments`
        );

        output({
          status: "success",
          data: {
            id: email.id,
            subject: email.subject,
            from: email.from.emailAddress,
            receivedDateTime: email.receivedDateTime,
            body: email.body,
            bodyPreview: email.bodyPreview,
            isRead: email.isRead,
            hasAttachments: email.hasAttachments,
          },
        });
        break;
      }

      case "search": {
        if (!values.query) {
          output({ status: "error", error: "--query is required for 'search' command" });
          return;
        }

        const query = encodeURIComponent(values.query);
        const response = await graphRequest<{ value: GraphEmail[] }>(
          token,
          `/me/messages?$search="${query}"&$top=${top}&$orderby=receivedDateTime desc`
        );

        output({
          status: "success",
          data: response.value.map((email) => ({
            id: email.id,
            subject: email.subject,
            from: email.from.emailAddress,
            receivedDateTime: email.receivedDateTime,
            bodyPreview: email.bodyPreview,
            isRead: email.isRead,
            hasAttachments: email.hasAttachments,
          })),
        });
        break;
      }

      case "folders": {
        const response = await graphRequest<{ value: MailFolder[] }>(
          token,
          `/me/mailFolders?$top=50`
        );

        output({
          status: "success",
          data: response.value.map((folder) => ({
            id: folder.id,
            displayName: folder.displayName,
            unreadItemCount: folder.unreadItemCount,
            totalItemCount: folder.totalItemCount,
            childFolderCount: folder.childFolderCount,
          })),
        });
        break;
      }

      case "send": {
        if (!values.to) {
          output({ status: "error", error: "--to is required for 'send' command" });
          return;
        }
        if (!values.subject) {
          output({ status: "error", error: "--subject is required for 'send' command" });
          return;
        }
        if (!values.body) {
          output({ status: "error", error: "--body is required for 'send' command" });
          return;
        }

        const message: {
          subject: string;
          body: { contentType: string; content: string };
          toRecipients: Array<{ emailAddress: { address: string } }>;
          ccRecipients?: Array<{ emailAddress: { address: string } }>;
          bccRecipients?: Array<{ emailAddress: { address: string } }>;
        } = {
          subject: values.subject,
          body: {
            contentType: values.html ? "HTML" : "Text",
            content: values.body,
          },
          toRecipients: parseRecipients(values.to),
        };

        if (values.cc) {
          message.ccRecipients = parseRecipients(values.cc);
        }
        if (values.bcc) {
          message.bccRecipients = parseRecipients(values.bcc);
        }

        await graphPost(token, "/me/sendMail", { message });

        output({
          status: "success",
          data: {
            sent: true,
            to: values.to,
            subject: values.subject,
          },
        });
        break;
      }

      default:
        output({ status: "error", error: `Unknown command: ${command}. Use --help for usage.` });
    }
  } catch (error) {
    output({
      status: "error",
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
}

main();
