#!/usr/bin/env bun
/**
 * Microsoft Graph Calendar Script
 *
 * View, search, and create calendar events via Microsoft Graph API.
 * Authentication is handled automatically - if needed, returns auth instructions.
 *
 * Usage:
 *   bun run calendar.ts <command> [options]
 *
 * Commands:
 *   list      List upcoming calendar events
 *   view      View a specific event by ID
 *   search    Search calendar events
 *   today     Show today's events
 *   week      Show this week's events
 *   create    Create a new calendar event
 *
 * Options:
 *   --profile    Credential profile (default: "default")
 *   --top        Number of results (default: 10)
 *   --start      Start date/time (ISO format or relative: today, tomorrow)
 *   --end        End date/time (ISO format or relative: +7d, +1m)
 *   --query      Search query for 'search' command
 *   --id         Event ID for 'view' command
 *   --subject    Event subject/title for 'create'
 *   --location   Event location for 'create'
 *   --body       Event description for 'create'
 *   --attendees  Attendee emails for 'create' (comma-separated)
 *   --all-day    Create as all-day event
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
import type { GraphCalendarEvent } from "./lib/types";

const { values, positionals } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    profile: { type: "string", default: "default" },
    top: { type: "string", default: "10" },
    start: { type: "string" },
    end: { type: "string" },
    query: { type: "string" },
    id: { type: "string" },
    subject: { type: "string" },
    location: { type: "string" },
    body: { type: "string" },
    attendees: { type: "string" },
    "all-day": { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
  allowPositionals: true,
});

const command = positionals[0] || "list";

if (values.help) {
  console.log(`
Microsoft Graph Calendar Access

Usage:
  bun run calendar.ts <command> [options]

Commands:
  list      List upcoming calendar events (default)
  view      View a specific event by ID
  search    Search calendar events
  today     Show today's events
  week      Show this week's events
  create    Create a new calendar event

Options:
  --profile <name>    Credential profile (default: "default")
  --top <n>           Number of results (default: 10)
  --start <date>      Start date/time (ISO format or: today, tomorrow, +1d)
  --end <date>        End date/time (ISO format or: +7d, +1m, +1y)
  --query <q>         Search query (for 'search' command)
  --id <id>           Event ID (for 'view' command)
  --subject <text>    Event subject/title (for 'create')
  --location <text>   Event location (for 'create')
  --body <text>       Event description (for 'create')
  --attendees <list>  Attendee emails, comma-separated (for 'create')
  --all-day           Create as all-day event
  -h, --help          Show this help message

Output:
  JSON with status field indicating success, auth_required, auth_pending, or error.

Date/Time Examples:
  --start today --end +7d                       Next 7 days
  --start 2024-01-01 --end 2024-01-31
  --start tomorrow
  --start 2024-01-15T14:00:00 --end 2024-01-15T15:00:00

Examples:
  bun run calendar.ts                           # List upcoming events
  bun run calendar.ts today                     # Today's events
  bun run calendar.ts week                      # This week's events
  bun run calendar.ts list --start tomorrow --end +7d
  bun run calendar.ts search --query "1:1"
  bun run calendar.ts view --id AAMkAG...
  bun run calendar.ts create --subject "Team Meeting" --start 2024-01-15T14:00:00 --end 2024-01-15T15:00:00
  bun run calendar.ts create --subject "Review" --start tomorrow --end +1d --attendees "a@ex.com,b@ex.com"
  bun run calendar.ts create --subject "Holiday" --start 2024-12-25 --all-day
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

async function graphPost<T>(token: string, endpoint: string, body: unknown): Promise<T> {
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

  return response.json();
}

function parseAttendees(input: string): Array<{ emailAddress: { address: string }; type: string }> {
  return input
    .split(",")
    .map((email) => email.trim())
    .filter((email) => email.length > 0)
    .map((address) => ({
      emailAddress: { address },
      type: "required",
    }));
}

function parseDate(input: string, baseDate: Date = new Date()): Date {
  const lower = input.toLowerCase();

  if (lower === "today") {
    const d = new Date(baseDate);
    d.setHours(0, 0, 0, 0);
    return d;
  }

  if (lower === "tomorrow") {
    const d = new Date(baseDate);
    d.setDate(d.getDate() + 1);
    d.setHours(0, 0, 0, 0);
    return d;
  }

  // Relative dates: +7d, +1m, +1y
  const relativeMatch = lower.match(/^\+(\d+)([dmy])$/);
  if (relativeMatch) {
    const [, amount, unit] = relativeMatch;
    const d = new Date(baseDate);
    switch (unit) {
      case "d":
        d.setDate(d.getDate() + parseInt(amount));
        break;
      case "m":
        d.setMonth(d.getMonth() + parseInt(amount));
        break;
      case "y":
        d.setFullYear(d.getFullYear() + parseInt(amount));
        break;
    }
    return d;
  }

  // ISO date
  return new Date(input);
}

function formatEventData(event: GraphCalendarEvent) {
  return {
    id: event.id,
    subject: event.subject,
    start: event.start,
    end: event.end,
    isAllDay: event.isAllDay ?? false,
    location: event.location?.displayName ?? null,
    organizer: event.organizer?.emailAddress ?? null,
    attendees: event.attendees?.map((a) => ({
      email: a.emailAddress,
      status: a.status?.response ?? null,
    })) ?? [],
    bodyPreview: event.bodyPreview ?? null,
  };
}

async function main() {
  // Determine required scopes based on command
  const requiredScopes = [...GRAPH_SCOPES.user];
  if (command === "create") {
    requiredScopes.push(...GRAPH_SCOPES.calendarWrite);
  } else {
    requiredScopes.push(...GRAPH_SCOPES.calendar);
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

  // Determine date range based on command
  let startDate: Date;
  let endDate: Date;

  const now = new Date();

  switch (command) {
    case "today":
      startDate = new Date(now);
      startDate.setHours(0, 0, 0, 0);
      endDate = new Date(now);
      endDate.setHours(23, 59, 59, 999);
      break;

    case "week":
      startDate = new Date(now);
      startDate.setHours(0, 0, 0, 0);
      endDate = new Date(now);
      endDate.setDate(endDate.getDate() + 7);
      break;

    default:
      startDate = values.start ? parseDate(values.start) : now;
      endDate = values.end ? parseDate(values.end, startDate) : parseDate("+30d", startDate);
  }

  try {
    switch (command) {
      case "list":
      case "today":
      case "week": {
        const startISO = startDate.toISOString();
        const endISO = endDate.toISOString();

        const response = await graphRequest<{ value: GraphCalendarEvent[] }>(
          token,
          `/me/calendarView?startDateTime=${startISO}&endDateTime=${endISO}&$top=${top}&$orderby=start/dateTime`
        );

        output({
          status: "success",
          data: response.value.map(formatEventData),
        });
        break;
      }

      case "view": {
        if (!values.id) {
          output({ status: "error", error: "--id is required for 'view' command" });
          return;
        }

        const event = await graphRequest<GraphCalendarEvent>(
          token,
          `/me/events/${values.id}`
        );

        output({
          status: "success",
          data: formatEventData(event),
        });
        break;
      }

      case "search": {
        if (!values.query) {
          output({ status: "error", error: "--query is required for 'search' command" });
          return;
        }

        // Use filter instead of search for calendar (search not supported on events)
        const query = values.query.replace(/'/g, "''");
        const response = await graphRequest<{ value: GraphCalendarEvent[] }>(
          token,
          `/me/events?$filter=contains(subject,'${query}')&$top=${top}&$orderby=start/dateTime desc`
        );

        output({
          status: "success",
          data: response.value.map(formatEventData),
        });
        break;
      }

      case "create": {
        if (!values.subject) {
          output({ status: "error", error: "--subject is required for 'create' command" });
          return;
        }
        if (!values.start) {
          output({ status: "error", error: "--start is required for 'create' command" });
          return;
        }

        const isAllDay = values["all-day"];
        const eventStart = parseDate(values.start);
        const eventEnd = values.end
          ? parseDate(values.end, eventStart)
          : isAllDay
            ? new Date(eventStart.getTime() + 24 * 60 * 60 * 1000) // Next day for all-day
            : new Date(eventStart.getTime() + 60 * 60 * 1000); // 1 hour default

        // Get timezone
        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        const eventBody: {
          subject: string;
          start: { dateTime: string; timeZone: string };
          end: { dateTime: string; timeZone: string };
          isAllDay?: boolean;
          location?: { displayName: string };
          body?: { contentType: string; content: string };
          attendees?: Array<{ emailAddress: { address: string }; type: string }>;
        } = {
          subject: values.subject,
          start: {
            dateTime: isAllDay
              ? eventStart.toISOString().split("T")[0]
              : eventStart.toISOString(),
            timeZone,
          },
          end: {
            dateTime: isAllDay
              ? eventEnd.toISOString().split("T")[0]
              : eventEnd.toISOString(),
            timeZone,
          },
        };

        if (isAllDay) {
          eventBody.isAllDay = true;
        }

        if (values.location) {
          eventBody.location = { displayName: values.location };
        }

        if (values.body) {
          eventBody.body = { contentType: "Text", content: values.body };
        }

        if (values.attendees) {
          eventBody.attendees = parseAttendees(values.attendees);
        }

        const createdEvent = await graphPost<GraphCalendarEvent>(
          token,
          "/me/events",
          eventBody
        );

        output({
          status: "success",
          data: formatEventData(createdEvent),
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
