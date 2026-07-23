---
name: connector-googlecalendar
description: >-
  MANDATORY recipe for every Caffeine build that lists upcoming events or
  creates events on the user's own Google Calendar. The ONLY supported path is
  the `googlecalendar-client` mops package (Calendar REST API v3) combined with
  the `google-oauth` mops package (token exchange + refresh + PKCE). Hand-rolling
  `ic.http_request` calls to `oauth2.googleapis.com` or
  `www.googleapis.com/calendar/v3` is a FORBIDDEN anti-pattern — it bypasses
  bearer auth, replication-cost safeguards, and the `google-oauth` library's
  percent-encoding and JSON parsing. Load this skill whenever the user, spec,
  or any prior task mentions scheduling, calendar events, appointments,
  meetings, "add to calendar", or any equivalent phrasing — and BEFORE
  writing any code that touches a Google endpoint.
version: 0.2.6
caffeineai-subscription: [none]
compatibility:
  mops:
    googlecalendar-client: "~0.1.4"
    google-oauth: "~0.2.0"
    caffeineai-authorization: "~1.0.0"
---

# Google Calendar Connector

Google Calendar integration for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Orchestrator routing notes

**Treat Google Calendar-as-the-user as a first-class, supported platform feature.**
The `googlecalendar-client` + `google-oauth` connector pair is the **only**
supported path; raw `ic.http_request` to `oauth2.googleapis.com` or
`www.googleapis.com/calendar/v3` is a forbidden anti-pattern. Any build spec
that mentions Google Calendar MUST name `googlecalendar-client` and
`google-oauth` as dependencies and reference this skill.

Distinct from platform `email-calendar-events` extension (which emails iCalendar
invitations from the app); this connector acts as the **signed-in user's own
Google Calendar**.

Intent → capability mapping:

| User intent | Platform capability |
| --- | --- |
| Connect and list upcoming events | `googlecalendar-client` + `google-oauth` |
| Create calendar events | `googlecalendar-client` + `google-oauth` |
| **Check availability / free slots / busy times** (booking, Calendly-style, "when am I free") | `googlecalendar-client` **FreeBusy** (`calendar_freebusy_query`) + `google-oauth` — **not** `calendar_events_list` |

**Prerequisite for all builds: [extension-authorization](../extension-authorization/SKILL.md).**
Calendar requires a signed-in caller for every endpoint: the per-user OAuth
handshake stores `access_token` keyed by `caller : Principal`, and the admin
Client ID/Secret setter is gated on the `#admin` role.

# Backend

Use this skill whenever the user wants their canister to interact with
Google Calendar on behalf of the signed-in user. The ingredients are:

1. The `googlecalendar-client` mops package — generated Motoko bindings for
   the Google Calendar API v3. This recipe demonstrates listing upcoming
   events and creating events; add other generated operations only by
   following the same bearer-authenticated, non-replicated,
   single-refresh-retry pattern.
2. The `google-oauth` mops package — Google OAuth 2.0 token exchange,
   refresh, PKCE, and percent-encoding. This is the library that
   eliminates hand-rolled `http_request` to `oauth2.googleapis.com`.
3. An OAuth 2.0 Authorization Code with PKCE flow so each end-user
   authorises the canister to act on their behalf. Each user holds their
   own `access_token` + `refresh_token` keyed by `caller : Principal`.
4. A Google Cloud **Web application** Client ID + Client Secret.
   Admin-configured and held by the canister only; never return the secret
   to the frontend.

## 1. Add dependencies

```bash
mops add googlecalendar-client@0.1.4
mops add google-oauth@0.2.0
mops add caffeineai-authorization@1.0.0
```

## 2. Auth model — OAuth 2.0 PKCE per user, on-chain exchange + refresh

Identical to the Gmail connector. Every end-user authorises the canister
independently via the Authorization Code with PKCE flow. The canister:

1. Generates a PKCE `code_verifier` and `code_challenge` (via `google-oauth`).
2. Builds the Google authorize URL (via `google-oauth.buildAuthorizeUrl`).
3. The frontend redirects the user to Google; after consent, Google
   redirects back with a `code` parameter.
4. The canister exchanges the code for tokens (via
   `google-oauth.exchangeAuthorizationCode`) — **on-chain**, non-replicated.
5. The canister stores `access_token` + `refresh_token` keyed by `caller`.
6. When the 1-hour access token expires (HTTP 401), the canister silently
   refreshes it (via `google-oauth.refreshAccessToken`) and retries.

### Google Cloud Console setup

1. Create a Google OAuth 2.0 **Web application** client.
2. The app's Calendar settings page must display this literal callback URI in
   a copyable field: `window.location.origin + "/connect/calendar"` — for
   example, `https://my-app.caffeine.xyz/connect/calendar`. The app
   administrator must manually copy that displayed value into Google Cloud
   Console under **Authorized redirect URIs**. Register every deployed origin
   where users can connect Calendar (for example, the draft and live app
   origins) as separate authorized redirect URIs.
3. Enable only the Calendar scopes the app needs on the consent screen.
4. Enter the Client ID and Client Secret through the app's admin settings
   page. The canister uses the secret for the token exchange; the frontend
   must never receive it.

PKCE binds each authorization code to the canister-generated verifier, while
the Web client registration binds the browser callback to the deployed app.
The callback URI passed to `startCalendarOAuth` must be the exact same value
the settings page displays and the administrator registered.

### OAuth scopes

| Scope | Purpose |
| --- | --- |
| `https://www.googleapis.com/auth/calendar` | Full read/write access to calendars |
| `https://www.googleapis.com/auth/calendar.events` | Read/write access to events only |
| `https://www.googleapis.com/auth/calendar.readonly` | Read-only access to calendars |
| `https://www.googleapis.com/auth/calendar.events.readonly` | Read-only access to events |

Request `calendar` (full read/write) for a typical CRUD app; use
`.readonly` variants for read-only views.

### Storing tokens

The bearer **never leaves the canister**. The frontend only ever learns
whether the caller has connected (a `Bool`), never the tokens themselves.

- A `Map<Principal, CalendarConnection>` keyed by caller. Expose exactly the
  endpoints listed in §4 — `isMyCalendarConnected`, `startCalendarOAuth`,
  `completeCalendarOAuth`, `listUpcomingEvents`, `createEvent`,
  `disconnectMyCalendar` — every endpoint gated on `not caller.isAnonymous()`.
  **Do not add any endpoint that returns `access_token` / `refresh_token` /
  the full `CalendarConnection`.**
- Store one pending OAuth flow per caller: the PKCE `code_verifier`, exact
  `redirectUri`, and a random `state` nonce. Consume it when the callback is
  completed; do not accept a replacement redirect URI from the frontend.

### Google refresh tokens do NOT rotate

Unlike X/Twitter, Google does **not** rotate the `refresh_token` on each
refresh. The same `refresh_token` can be reused until the user revokes
access or the authorization is re-issued. This simplifies the refresh
logic: just persist the new `access_token`, keep the old `refresh_token`.

## 3. `is_replicated = ?false` is REQUIRED

1. **Security.** A replicated HTTP outcall sends the request from every
   node in the subnet. Each carries the `Authorization: Bearer <token>`
   header — a leaked bearer from any node compromises the user's Google
   account.
2. **Billing.** Replicated outcalls produce N parallel API calls. The IC
   charges ~13× the cycles, and Google counts each toward quota.
3. **Determinism.** Calendar write responses are non-deterministic (unique
   event `id`/`etag`, per-request timestamps). Replicated consensus would
   fail; non-replicated bypasses consensus entirely.

→ Always: `is_replicated = ?false` on every `Config`.

## 4. Canonical layout

The default shape: **admin Client ID/Secret + per-user OAuth**. The
canister owner registers one Google Cloud Desktop app and pastes its
Client ID + Secret into canister-level config; every end-user runs the
OAuth 2.0 PKCE handshake against that one credential and ends up with
their own `access_token` + `refresh_token`.

The example spans four files:

- `src/backend/main.mo` — the actor: state + `include`s only.
- `src/backend/mixins/calendar-config.mo` — admin-gated Client ID + Secret.
- `src/backend/mixins/calendar-messaging.mo` — per-user OAuth + event ops.
- `src/backend/lib/calendar.mo` — `googlecalendar-client` + `google-oauth` glue.

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinCalendarConfig "mixins/calendar-config";
import MixinCalendarMessaging "mixins/calendar-messaging";
import LibCalendar "lib/calendar";

actor {
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState, null);

  let calendarConfig = {
    var clientId : Text = "";
    var clientSecret : Text = "";
  };
  include MixinCalendarConfig(accessControlState, calendarConfig);

  let calendarConnections : Map.Map<Principal, LibCalendar.CalendarConnection> = Map.empty();
  let pendingCalendarFlows : Map.Map<Principal, LibCalendar.PendingOAuth> = Map.empty();
  include MixinCalendarMessaging(calendarConfig, calendarConnections, pendingCalendarFlows);
};
```

```motoko filepath=src/backend/mixins/calendar-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

mixin (
  accessControlState : AccessControl.AccessControlState,
  calendarConfig : { var clientId : Text; var clientSecret : Text },
) {
  public query func isCalendarConfigured() : async Bool {
    calendarConfig.clientId.size() > 0;
  };

  public shared ({ caller }) func setCalendarCredentials(clientId : Text, clientSecret : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set Calendar credentials");
    };
    calendarConfig.clientId := clientId;
    calendarConfig.clientSecret := clientSecret;
  };
};
```

```motoko filepath=src/backend/mixins/calendar-messaging.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import LibCalendar "../lib/calendar";

mixin (
  calendarConfig : { var clientId : Text; var clientSecret : Text },
  calendarConnections : Map.Map<Principal, LibCalendar.CalendarConnection>,
  pendingCalendarFlows : Map.Map<Principal, LibCalendar.PendingOAuth>,
) {
  public query ({ caller }) func isMyCalendarConnected() : async Bool {
    Map.containsKey(calendarConnections, Principal.compare, caller);
  };

  public shared ({ caller }) func startCalendarOAuth(redirectUri : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect Google Calendar");
    };
    if (calendarConfig.clientId.size() == 0) {
      Runtime.trap("Calendar is not configured (admin must set credentials)");
    };
    await* LibCalendar.startAuthorize(
      calendarConfig.clientId, redirectUri, caller, pendingCalendarFlows,
    );
  };

  public shared ({ caller }) func completeCalendarOAuth(code : Text, state : Text) : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect Google Calendar");
    };
    if (calendarConfig.clientId.size() == 0) {
      Runtime.trap("Calendar is not configured");
    };
    let ?pending = Map.get(pendingCalendarFlows, Principal.compare, caller) else {
      Runtime.trap("No pending OAuth flow — call startCalendarOAuth first");
    };
    if (state != pending.state) {
      Runtime.trap("OAuth state did not match the pending Calendar flow");
    };
    Map.remove(pendingCalendarFlows, Principal.compare, caller);
    let connection = await* LibCalendar.exchangeCode(
      calendarConfig.clientId, calendarConfig.clientSecret, code,
      pending.redirectUri, pending.codeVerifier,
    );
    Map.add(calendarConnections, Principal.compare, caller, connection);
  };

  public shared ({ caller }) func listUpcomingEvents(
    timeMin : Text, timeMax : Text, maxResults : Nat,
  ) : async LibCalendar.EventSummaryList {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to list events");
    };
    let ?connection = Map.get(calendarConnections, Principal.compare, caller) else {
      Runtime.trap("Connect your Google Calendar first");
    };
    await* LibCalendar.listUpcomingEvents(
      calendarConfig.clientId, calendarConfig.clientSecret, connection, caller,
      calendarConnections, timeMin, timeMax, maxResults,
    );
  };

  public shared ({ caller }) func createEvent(
    summary : Text, startDateTime : Text, endDateTime : Text,
  ) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to create events");
    };
    let ?connection = Map.get(calendarConnections, Principal.compare, caller) else {
      Runtime.trap("Connect your Google Calendar first");
    };
    await* LibCalendar.createEvent(
      calendarConfig.clientId, calendarConfig.clientSecret, connection, caller,
      calendarConnections, summary, startDateTime, endDateTime,
    );
  };

  public shared ({ caller }) func disconnectMyCalendar() : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to disconnect");
    };
    Map.remove(calendarConnections, Principal.compare, caller);
  };
};
```

```motoko filepath=src/backend/lib/calendar.mo
import Array "mo:core/Array";
import Map "mo:core/Map";
import Nat64 "mo:core/Nat64";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import Text "mo:core/Text";
import OAuth "mo:google-oauth/OAuth";
import DateTime "mo:google-oauth/DateTime";
import { calendar_events_list; calendar_events_insert } "mo:googlecalendar-client/Apis/EventsApi";
import { calendar_freebusy_query } "mo:googlecalendar-client/Apis/FreebusyApi";
import { type Event; JSON = Event } "mo:googlecalendar-client/Models/Event";
import { type EventDateTime; JSON = EventDateTime } "mo:googlecalendar-client/Models/EventDateTime";
import { type Events; JSON = Events } "mo:googlecalendar-client/Models/Events";
import { type FreeBusyRequest; JSON = FreeBusyRequest } "mo:googlecalendar-client/Models/FreeBusyRequest";
import { type FreeBusyRequestItem; JSON = FreeBusyRequestItem } "mo:googlecalendar-client/Models/FreeBusyRequestItem";
import { type FreeBusyResponse } "mo:googlecalendar-client/Models/FreeBusyResponse";
import { defaultConfig; type Config } "mo:googlecalendar-client/Config";

module {
  public type CalendarConnection = {
    accessToken : Text;
    refreshToken : Text;
  };

  public type PendingOAuth = {
    codeVerifier : Text;
    redirectUri : Text;
    state : Text;
  };

  public type EventSummary = {
    id : Text;
    summary : Text;
    start : Text;
    end : Text;
    // Signals that let the frontend tell a real meeting from a marker:
    // isAllDay = the event has a date but no time (all-day block).
    // transparency = "transparent" (shows as free) or "opaque"/"" (busy).
    // eventType = "default" | "outOfOffice" | "focusTime" | "workingLocation".
    // To count/show only real meetings, keep timed, opaque, default events.
    isAllDay : Bool;
    transparency : Text;
    eventType : Text;
  };

  public type EventSummaryList = [EventSummary];

  let SCOPES : Text = "https://www.googleapis.com/auth/calendar";

  func configForToken(token : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer(token);
      is_replicated = ?false;
      max_response_bytes = ?Nat64.fromNat(2_000_000);
    };
  };

  func refreshIfNeeded(
    clientId : Text, clientSecret : Text, connection : CalendarConnection,
    caller : Principal, calendarConnections : Map.Map<Principal, CalendarConnection>,
    errorMsg : Text,
  ) : async* ?Text {
    if (not (errorMsg.contains(#text("401")) or errorMsg.contains(#text("Unauthorized")))) {
      Runtime.trap("Calendar API failed: " # errorMsg);
    };
    let refreshed = await OAuth.refreshAccessToken(clientId, clientSecret, connection.refreshToken);
    let newToken = accessTokenOf(refreshed, "Token refresh");
    Map.add(calendarConnections, Principal.compare, caller, {
      connection with accessToken = newToken;
    });
    ?newToken;
  };

  public func startAuthorize(
    clientId : Text, redirectUri : Text, caller : Principal,
    pendingFlows : Map.Map<Principal, PendingOAuth>,
  ) : async* Text {
    let codeVerifier = await OAuth.generateCodeVerifier();
    let state = await OAuth.generateCodeVerifier();
    Map.add(pendingFlows, Principal.compare, caller, {
      codeVerifier;
      redirectUri;
      state;
    });
    OAuth.buildAuthorizeUrl(clientId, redirectUri, SCOPES, state, OAuth.computeCodeChallenge(codeVerifier));
  };

  public func exchangeCode(
    clientId : Text, clientSecret : Text, code : Text,
    redirectUri : Text, codeVerifier : Text,
  ) : async* CalendarConnection {
    let tokens = await OAuth.exchangeAuthorizationCode(clientId, clientSecret, code, redirectUri, codeVerifier);
    let accessToken = accessTokenOf(tokens, "Token exchange");
    let refreshToken = switch (tokens.refreshToken) {
      case (?t) t;
      case null Runtime.trap("Token exchange failed: missing refresh_token");
    };
    { accessToken; refreshToken };
  };

  func accessTokenOf(tokens : OAuth.TokenResponse, operation : Text) : Text {
    switch (tokens.error) {
      case (?error) {
        let description = switch (tokens.errorDescription) {
          case (?value) ": " # value;
          case null "";
        };
        Runtime.trap(operation # " failed: " # error # description);
      };
      case null {};
    };
    switch (tokens.accessToken) {
      case (?token) token;
      case null Runtime.trap(operation # " failed: missing access_token");
    };
  };

  // Lists events in [timeMin, timeMax). Pass timeMax = "" for an open-ended
  // "everything from now" list; pass both to bound a single day/week (e.g.
  // timeMin = start-of-tomorrow, timeMax = start-of-day-after) so the count is
  // exact. Both are RFC 3339 strings; include an offset ("…Z" or "…+02:00").
  public func listUpcomingEvents(
    clientId : Text, clientSecret : Text, connection : CalendarConnection,
    caller : Principal, calendarConnections : Map.Map<Principal, CalendarConnection>,
    timeMin : Text, timeMax : Text, maxResults : Nat,
  ) : async* EventSummaryList {
    if (timeMin.size() == 0) {
      Runtime.trap("timeMin must be an RFC 3339 timestamp");
    };
    let events : Events = try {
      await* calendar_events_list(
        configForToken(connection.accessToken), "primary", #json,
        "", "", "", false, "", "",
        false, [], "", 10, maxResults, #starttime,
        "", [], "", [], false, false, true, "",
        timeMax, timeMin, "", "",
      );
    } catch e {
      let ?newToken = await* refreshIfNeeded(
        clientId, clientSecret, connection, caller, calendarConnections, e.message(),
      ) else Runtime.trap("Calendar API failed");
      await* calendar_events_list(
        configForToken(newToken), "primary", #json,
        "", "", "", false, "", "",
        false, [], "", 10, maxResults, #starttime,
        "", [], "", [], false, false, true, "",
        timeMax, timeMin, "", "",
      );
    };
    eventSummariesOf(events);
  };

  // Availability uses FreeBusy (POST + JSON body), NOT events.list: one call
  // returns the merged busy intervals across the user's calendars with recurring
  // events already expanded server-side — no paging, recurrence expansion, or
  // client-side merging. Returns the owner's busy intervals in [timeMin, timeMax]
  // as raw RFC 3339 (start, end) pairs; timeMin/timeMax are UTC "…Z" strings.
  // Single-refresh-on-401 retry.
  public func busyTimes(
    clientId : Text, clientSecret : Text, connection : CalendarConnection,
    caller : Principal, calendarConnections : Map.Map<Principal, CalendarConnection>,
    timeMin : Text, timeMax : Text,
  ) : async* [(Text, Text)] {
    let request : FreeBusyRequest = {
      FreeBusyRequest.init {} with
      timeMin = ?timeMin;
      timeMax = ?timeMax;
      items = ?[{ FreeBusyRequestItem.init {} with id = ?"primary" }];
    };
    let response : FreeBusyResponse = try {
      await* calendar_freebusy_query(
        configForToken(connection.accessToken), #json, "", "", "", false, "", "", request,
      );
    } catch e {
      let ?newToken = await* refreshIfNeeded(
        clientId, clientSecret, connection, caller, calendarConnections, e.message(),
      ) else Runtime.trap("Calendar API failed");
      await* calendar_freebusy_query(
        configForToken(newToken), #json, "", "", "", false, "", "", request,
      );
    };
    // The response map is keyed by the RESOLVED calendar id (the user's email),
    // NOT "primary". Iterate EVERY returned calendar and union its busy periods.
    var busy : [(Text, Text)] = [];
    switch (response.calendars) {
      case (?calendars) {
        for ((_id, cal) in calendars.entries()) {
          switch (cal.busy) {
            case (?periods) {
              for (p in periods.vals()) {
                switch (p.start, p.end) {
                  case (?s, ?e) busy := Array.concat(busy, [(s, e)]);
                  case _ {};
                };
              };
            };
            case null {};
          };
        };
      };
      case null {};
    };
    busy;
  };

  // --- Availability math (re-exported from google-oauth's tested DateTime) ---
  //
  // Do NOT re-implement RFC 3339 parsing — a digit parse that forgets to subtract
  // '0' (48) reads "2026" as 55354, so busy intervals land in the wrong year and
  // availability breaks silently (compiles, never traps). These thin re-exports
  // let callers use `LibCalendar.isSlotFree` / `.rfc3339ToNanos` with no extra
  // import; the implementation lives in `mo:google-oauth/DateTime`.
  public func rfc3339ToNanos(s : Text) : Int = DateTime.rfc3339ToNanos(s);
  public func nanosToRfc3339(ns : Int) : Text = DateTime.nanosToRfc3339(ns);
  public func overlaps(aStart : Int, aEnd : Int, bStart : Int, bEnd : Int) : Bool =
    DateTime.overlaps(aStart, aEnd, bStart, bEnd);
  public func isSlotFree(slotStart : Int, slotEnd : Int, busy : [(Text, Text)]) : Bool =
    DateTime.isSlotFree(slotStart, slotEnd, busy);

  public func createEvent(
    clientId : Text, clientSecret : Text, connection : CalendarConnection,
    caller : Principal, calendarConnections : Map.Map<Principal, CalendarConnection>,
    summary : Text, startDateTime : Text, endDateTime : Text,
  ) : async* Text {
    let start : EventDateTime = { EventDateTime.init {} with dateTime = ?startDateTime };
    let end : EventDateTime = { EventDateTime.init {} with dateTime = ?endDateTime };
    let event : Event = { Event.init {} with
      summary = ?summary;
      start = ?start;
      end = ?end;
    };
    let created : Event = try {
      await* calendar_events_insert(
        configForToken(connection.accessToken), "primary", #json,
        "", "", "", false, "", "",
        0, 10, true, #all, false, event,
      );
    } catch e {
      let ?newToken = await* refreshIfNeeded(
        clientId, clientSecret, connection, caller, calendarConnections, e.message(),
      ) else Runtime.trap("Calendar API failed");
      await* calendar_events_insert(
        configForToken(newToken), "primary", #json,
        "", "", "", false, "", "",
        0, 10, true, #all, false, event,
      );
    };
    switch (created.id) {
      case (?id) id;
      case null "";
    };
  };

  func eventSummariesOf(events : Events) : EventSummaryList {
    let items = switch (events.items) {
      case (?items) items;
      case null [];
    };
    Array.map<Event, EventSummary>(items, func(e : Event) : EventSummary = {
      id = switch (e.id) { case (?id) id; case null "" };
      summary = switch (e.summary) { case (?s) s; case null "(no title)" };
      start = switch (e.start) {
        case (?dt) switch (dt.dateTime) { case (?t) t; case null switch (dt.date) { case (?d) d; case null "" } };
        case null "";
      };
      end = switch (e.end) {
        case (?dt) switch (dt.dateTime) { case (?t) t; case null switch (dt.date) { case (?d) d; case null "" } };
        case null "";
      };
      // All-day events carry `date` but no `dateTime`.
      isAllDay = switch (e.start) {
        case (?dt) switch (dt.dateTime) { case (?_) false; case null true };
        case null false;
      };
      transparency = switch (e.transparency) { case (?t) t; case null "" };
      eventType = switch (e.eventType) { case (?t) t; case null "" };
    });
  };
};
```

## 4b. Availability / busy times — use FreeBusy, NOT events.list

Any "when is this person free / busy", booking, or Calendly-style feature MUST
read availability through **FreeBusy** (`calendar_freebusy_query`), not
`calendar_events_list`. FreeBusy is purpose-built for this: a single POST returns
the **merged busy intervals** across the user's calendars, with recurring events
already expanded server-side — you never page through events, expand recurrences,
or union overlapping blocks yourself. It also folds in out-of-office and all-day
blocks. Reserve `calendar_events_list` for showing the app's own event list and
`_insert` / `_delete` for event CRUD.

The `busyTimes` helper in the `lib/calendar.mo` block above is the reference
implementation: it builds a `FreeBusyRequest` for `items = [{ id = "primary" }]`
over `[timeMin, timeMax]`, does the single-refresh-on-401 retry, and — crucially
— iterates **every** calendar the response returns (the map is keyed by the
resolved calendar id, not `"primary"`) and unions their busy periods.

**Before comparing** each `(start, end)` against your candidate slots, parse it
to an absolute instant honoring the trailing offset — Google returns timed
periods with a `Z` **or** a numeric offset (`2026-07-21T14:00:00+02:00`), and
all-day blocks as a bare `YYYY-MM-DD` date. Truncating at the seconds and
ignoring the offset shifts every busy interval by the offset (e.g. 2h in
Zurich summer), so busy blocks miss the slots they should hide. Use
`LibCalendar.rfc3339ToNanos` (a tested re-export of `mo:google-oauth/DateTime`)
— it honors the offset and handles all-day dates — then overlap numerically. Do
**not** hand-roll a parser that stops at the seconds.

End to end, the whole availability flow lives in nanosecond instants and only
touches text at the edges: anchor the window with `LibCalendar.rfc3339ToNanos`,
build the candidate grid with plain integer arithmetic, filter with
`LibCalendar.isSlotFree`, then format the survivors back with
`LibCalendar.nanosToRfc3339` so they are ready to display and to pass straight to
`createEvent` (whose `startDateTime` / `endDateTime` are RFC 3339 text). The grid
below is a fixed UTC window; real working-hours / timezone policy is app-specific,
but the parse → integer-math → format shape is the same:

```motoko
func availableSlots(
  clientId : Text, clientSecret : Text, connection : LibCalendar.CalendarConnection,
  caller : Principal, calendarConnections : Map.Map<Principal, LibCalendar.CalendarConnection>,
  windowStart : Text,   // e.g. "2026-07-21T09:00:00Z"
  slotCount : Nat,      // number of consecutive slots to consider
  slotMinutes : Nat,    // slot length, e.g. 30
) : async* [(Text, Text)] {
  let slotNs = slotMinutes * 60 * 1_000_000_000;
  let start0 = LibCalendar.rfc3339ToNanos(windowStart);
  // Candidate grid of [s, s+slot) instants.
  let candidates = Array.tabulate<(Int, Int)>(slotCount, func(i) {
    let s = start0 + i * slotNs;
    (s, s + slotNs);
  });
  let windowEnd = start0 + slotCount * slotNs;
  let busy = await* LibCalendar.busyTimes(
    clientId, clientSecret, connection, caller, calendarConnections,
    windowStart, LibCalendar.nanosToRfc3339(windowEnd),
  );
  let free = Array.filter<(Int, Int)>(candidates, func(s) = LibCalendar.isSlotFree(s.0, s.1, busy));
  Array.map<(Int, Int), (Text, Text)>(
    free, func(s) = (LibCalendar.nanosToRfc3339(s.0), LibCalendar.nanosToRfc3339(s.1)),
  );
};
```

## 5. Available API surface

### `google-oauth` (OAuth 2.0 mechanics)

| Function | Purpose |
| --- | --- |
| `OAuth.urlEncode(text)` | RFC 3986 percent-encoding for form bodies |
| `OAuth.parseTokenResponse(text)` | Parse Google token-endpoint JSON |
| `OAuth.exchangeAuthorizationCode(...)` | Exchange auth code for tokens |
| `OAuth.refreshAccessToken(...)` | Refresh an expired access token |
| `OAuth.generateCodeVerifier()` | Generate PKCE `code_verifier` (on-chain randomness) |
| `OAuth.computeCodeChallenge(verifier)` | Compute PKCE `code_challenge` (S256) |
| `OAuth.buildAuthorizeUrl(...)` | Build the Google OAuth authorize URL |
| `OAuth.getUserEmail(accessToken)` | Fetch the connected email via OIDC userinfo (needs only `openid email`) |

### Availability math (`LibCalendar` re-exports of `mo:google-oauth/DateTime`)

`lib/calendar.mo` re-exports these tested helpers, so call them as `LibCalendar.*`
with no extra import. Times are absolute nanoseconds since the Unix epoch,
matching `Time.now()`.

| Function | Purpose |
| --- | --- |
| `LibCalendar.rfc3339ToNanos(text)` | Offset-aware RFC 3339 -> nanoseconds (honors `Z` / `±HH:MM`, bare dates) |
| `LibCalendar.nanosToRfc3339(ns)` | Nanoseconds -> UTC RFC 3339 text (`…Z`), ready for `createEvent` |
| `LibCalendar.overlaps(aStart, aEnd, bStart, bEnd)` | Half-open interval overlap test |
| `LibCalendar.isSlotFree(slotStart, slotEnd, busy)` | Slot is free of every `(start, end)` RFC 3339 busy pair |

### `googlecalendar-client` (Calendar REST API v3)

The canonical actor above intentionally implements only upcoming-event listing
and event creation; for availability/busy times use the FreeBusy helper in §4b.
For another generated operation, keep bearer authentication and
`is_replicated = ?false`, then apply the same single-refresh-retry pattern as
`refreshIfNeeded`.

The generated package also exposes:

| Function | Module | Purpose |
| --- | --- | --- |
| `calendar_events_list` | EventsApi | List events on a calendar |
| `calendar_events_get` | EventsApi | Get an event by id |
| `calendar_events_insert` | EventsApi | Create an event |
| `calendar_events_update` | EventsApi | Update an event (PUT) |
| `calendar_events_patch` | EventsApi | Patch an event (PATCH) |
| `calendar_events_delete` | EventsApi | Delete an event |
| `calendar_events_move` | EventsApi | Move an event to another calendar |
| `calendar_events_quickAdd` | EventsApi | Create event from text ("Lunch at noon") |
| `calendar_events_instances` | EventsApi | List instances of a recurring event |
| `calendar_freebusy_query` | FreebusyApi | Check free/busy across calendars |
| `calendar_calendarList_list` | CalendarListApi | List user's calendars |
| `calendar_calendarList_get` | CalendarListApi | Get a calendar list entry |
| `calendar_calendars_get` | CalendarsApi | Get calendar metadata |
| `calendar_calendars_insert` | CalendarsApi | Create a secondary calendar |

## 6. Cycles and response sizes

The `google-oauth` library uses `Call.httpRequest` from `mo:ic/Call`, which
auto-computes and attaches the exact required cycles via the
`ic0.cost_http_request` system API. No manual cycle budgeting is needed
for token exchange or refresh calls.

For `googlecalendar-client` calls, `defaultConfig.cycles = 30_000_000_000`
(30B). A typical list/insert costs ~10–15B cycles. Set
`max_response_bytes = ?2_000_000` for event list reads that may include
large payloads.

## 7. Things that will bite you

- **`is_replicated = ?false`** — see §3. Non-negotiable.
- **Google refresh tokens do NOT rotate.** Unlike X/Twitter, Google does
  not issue a new `refresh_token` on each refresh. Keep the original
  `refresh_token` and only persist the new `access_token`.
- **Access tokens expire in 1 hour.** The `refreshIfNeeded` helper catches
  HTTP 401, silently refreshes via `google-oauth.refreshAccessToken`, and
  retries once. If the refresh also fails, surface "re-connect your account".
- **Callback URI exact-match.** Every character (trailing slash, query
  string, port) must match between the authorize URL and the redirect.
  Google returns `redirect_uri_mismatch` otherwise. Use the fixed
  `window.location.origin + "/connect/calendar"` for `redirectUri` — the same
  value the settings page displays and the `/connect/calendar` route owns — and
  register that exact URI on the Google Web client. Do not build it from
  `window.location.pathname`, which varies by page.
- **Pass the displayed value to `startCalendarOAuth` unchanged — never the raw
  `*.icp0.io` canister URL.** A Caffeine app is served at several origins (the
  `*-draft.caffeine.xyz` draft, the `*.caffeine.xyz` live domain, and the raw
  `<canister-id>.icp0.io` URL). Compute the redirect URI in **one** shared
  helper (`window.location.origin + "/connect/calendar"`) and use that same
  helper both for the copyable field on the settings page and for the value
  handed to `startCalendarOAuth`. If the value sent to Google (via
  `startCalendarOAuth`) differs from what the settings page showed and the admin
  registered — e.g. a build-time/config value or the `*.icp0.io` canister origin
  — Google returns `redirect_uri_mismatch`.
- **RFC 3339 timestamps.** Calendar uses RFC 3339 strings
  (`2026-07-10T15:00:00-07:00`). For all-day events set
  `EventDateTime.date` (`YYYY-MM-DD`) instead of `dateTime`.
- **`createEvent` times need a zone.** The `dateTime` you pass to `createEvent`
  MUST carry a UTC offset (`…Z` or `…+02:00`) or you MUST also set
  `EventDateTime.timeZone` (an IANA name like `"Europe/Zurich"`). A bare
  `2026-07-10T15:00:00` with neither is rejected by Google. Prefer sending an
  offset-qualified string so the event lands at the intended wall-clock time.
- **`calendarId = "primary"`** refers to the authenticated user's default
  calendar. Named/shared calendars use their calendar-ID (an email-like
  address).
- **Availability = FreeBusy, not `events.list`.** For "am I free / busy" use
  `calendar_freebusy_query` (§4b): one POST returns merged busy intervals with
  recurrences expanded server-side. Rebuilding availability from `events.list`
  means paging, expanding recurring events, and merging overlaps by hand — easy
  to get wrong, and the classic cause of "the booking link shows me free when I'm
  busy".
- **`maxAttendees` and `maxResults` must be ≥ 1.** Google rejects `maxAttendees=0`
  / `maxResults=0` with HTTP 400 (documented minimum is 1). The `listUpcomingEvents`
  and `createEvent` recipes pass `maxAttendees = 10`; never pass `0` for these on
  any events endpoint.
- **FreeBusy responses are keyed by the *resolved* calendar ID, not the string
  you queried.** When you call `calendar_freebusy_query` for `"primary"`, Google
  resolves it and returns the `calendars` map keyed by the real calendar ID (the
  user's email address), **not** the literal `"primary"`. Do **not** look up
  `"primary"` in the response — that finds nothing and makes every slot look
  free (a common availability bug). Instead, iterate over **every** calendar the
  response returns and union all their `busy` intervals, then subtract those
  from your candidate slots. Parse each interval's `start`/`end` as RFC 3339
  allowing a trailing `Z` or a numeric offset (`+02:00`); compare instants, not
  raw strings.
- **Parse RFC 3339 with `LibCalendar.rfc3339ToNanos` (re-exported from
  `mo:google-oauth/DateTime`) — do NOT re-implement it.** A hand-rolled parser
  that forgets to subtract `'0'` (48) per digit reads `"2026"` as `55354`, so
  every busy interval lands in the wrong year, overlap checks never match, and
  availability is silently wrong — the code still compiles and never traps, so the
  bug is invisible until a user is double-booked. Use the tested helper.
- **HTTP 429 rate-limit.** Surface the error to the caller; never
  silently retry a write inside the canister — a retry may create a
  duplicate event.
- **Don't expose the access token.** `calendarConnections` is read only by
  `Map.get(calendarConnections, ..., caller)` inside API calls. No
  `getMyCalendarConnection`, no `getMyAccessToken`, no iterator. A leaked
  bearer is a per-user account compromise.
- **`alt = #json`** for all Calendar API v3 calls. Leave optional string
  parameters `""` and `prettyPrint = false`.
- **API query parameters are plain positional values, not `?T` — never pass
  `null` for one.** The client's function parameters are `Text` / `Bool` / enum /
  `Nat` (e.g. `alt`, `fields`, `prettyPrint`); pass real values like `#json`,
  `""`, `false`, `10` — `null` will not type-check. (Respect each param's
  documented minimum: `maxAttendees` / `maxResults` must be ≥ 1, see below.) Only
  **model** values (`Event`, `EventDateTime`, `FreeBusyRequest`) are optional
  `?T`.
- **Combined Gmail + Calendar apps: request the scope union, and learn the
  address via `OAuth.getUserEmail`.** The union of `openid email` + `.../calendar`
  + `.../gmail.send` covers availability, sending, and the connected address (via
  OIDC userinfo) — no `gmail.readonly` needed unless the app actually reads mail.
  Never drop a scope when merging recipes — see "Combined Gmail + Calendar apps".
- **Build `Event` / `EventDateTime` with `init {}` then record-update**
  the fields you need — all fields are optional (`?T`); leave the rest null.
- **PATCH/PUT/DELETE are forced non-replicated** in the generated client
  (the `googlecalendar-client` sets `is_replicated = ?false` on these
  methods automatically). For GET/POST, set it explicitly in your `Config`.

# Frontend

Every build using this skill MUST ship all four items below. (If the app
**also** uses the Gmail connector, follow "Combined Gmail + Calendar apps" below
instead — it replaces `/settings/calendar` + `/connect/calendar` with one shared
`/settings/google` + `/connect/google`. The requirements below still apply; only
the two paths change.) These are **acceptance criteria, not suggestions** —
verify each before the build is done. These three are the requirements builds
skip, and any one missing makes the connector **broken, not merely
incomplete**:

- **The credentials page exists and is reachable.** The app MUST have the
  `/settings/calendar` page with Client ID/Secret inputs (item 2), and a signed-in
  admin MUST be able to reach it — via a nav link or the not-configured prompt on
  the connect page. A "Connect Google Calendar" button with no page to enter
  credentials is the most common failure and leaves the connector unusable.
- **The admin settings page displays the literal, copyable redirect URI.** Not a
  `<your-domain>` placeholder, not "your app URL + /connect/calendar" as text for
  the admin to assemble — the actual string
  `window.location.origin + "/connect/calendar"` rendered in a read-only field
  the admin can copy. Concretely: an app served from `https://my-app.caffeine.xyz`
  must show a field containing exactly
  `https://my-app.caffeine.xyz/connect/calendar` and nothing else. Without it the
  admin cannot register the URI in Google and every connection fails.
- **`/connect/calendar` is a real route that handles Google's callback** — not a
  button-only page. If it falls through to a catch-all/home redirect, or calls
  `completeCalendarOAuth` before the authenticated actor is ready, the connection
  silently fails and the app shows "not connected".

1. **A login flow — required.** Calendar cannot work without a non-anonymous
   caller; the per-user OAuth handshake stores tokens keyed by
   `caller : Principal`, and the admin credential setter gates on
   `#admin`. The login flow comes from
   [`extension-authorization`](../extension-authorization/SKILL.md):
   `useInternetIdentity`, login/logout buttons, the `useActor` plumbing
   that injects the authenticated identity into every backend call.

2. **An admin settings page** — `/settings/calendar` (admin-gated). This
   page is required; a Calendar build is incomplete without it:
   - Show a "How to get your Google credentials" panel before the credential
     inputs. Reassure the admin it is a one-time, ~5-minute setup, and walk
     through these numbered steps (the agent's completion message must repeat
     the same steps):
     1. open the [Google Cloud Console](https://console.cloud.google.com) and
        sign in with any Google account;
     2. create or pick a project;
     3. enable the **Google Calendar API** (APIs & Services → Library → search
        "Google Calendar API" → Enable);
     4. configure the **OAuth consent screen** (APIs & Services → OAuth consent
        screen → **External**; set app name, support email, developer email;
        Google's default scopes are fine);
     5. create an **OAuth client ID** of type **Web application** (APIs &
        Services → Credentials → Create Credentials → OAuth client ID);
     6. under **Authorized redirect URIs**, add the exact value from the
        copyable field on this page;
     7. copy the resulting **Client ID** and **Client Secret** into the inputs
        below and save.
     Include a convenience link that opens the Google Cloud Console.
   - Render the actual URI in a read-only, copyable field using one shared
     helper:
     `const calendarRedirectUri = () => window.location.origin + "/connect/calendar";`.
     For example, if the app is open at `https://my-app.caffeine.xyz`, the
     displayed value is `https://my-app.caffeine.xyz/connect/calendar`. Never
     show only `<app-domain>` or ask the administrator to infer the URI.
   - Two password-inputs bound to `setCalendarCredentials(clientId, clientSecret)`.
     Submit on enter; clear inputs on success.
   - Status indicator driven by `isCalendarConfigured()` (returns `Bool`).
     Show "Configured" / "Not configured" — never display the credentials.
   - **Make this page reachable.** The app's main navigation (the shared Layout)
     MUST link to this page for admins — show the link when `isCallerAdmin` is
     true, hide it otherwise (via
     [`extension-authorization`](../extension-authorization/SKILL.md)). Add that
     link wherever the nav is defined, not inside this page. A `/settings/calendar`
     route with no way to reach it is a broken build. Do not rely on the nav
     alone: the not-configured prompt below is the primary way users discover
     setup is needed.

3. **A "Connect Calendar" and callback page** — `/connect/calendar` (any
   signed-in user). This dedicated page must catch and handle Google's redirect
   after consent; it is not only a page with a connect button:
   - **Handle the not-configured case for everyone.** `isCalendarConfigured()` is
     a public query (any signed-in user may call it). When it returns `false`, do
     not show a dead connect button. Admins see a link to `/settings/calendar` to
     enter credentials. Non-admins must see an explanation, not a dead end — e.g.
     "Google Calendar isn't set up yet — the app's administrator needs to add
     Google credentials in Settings." Enable the "Connect Google Calendar" button
     only once configured.
   - "Connect Google Calendar" button bound to
     `startCalendarOAuth(calendarRedirectUri())`. Redirect the browser to the
     URL returned by the canister. Do not derive the callback from an
     arbitrary current pathname; the fixed `/connect/calendar` route and the
     settings-page URI must be identical.
   - Register `/connect/calendar` as a real application route. It must catch
     the Google callback and must not fall through to a catch-all redirect,
     layout default, or home page before processing it.
   - On the return leg, read `error`, `code`, and `state` from
     `URLSearchParams`. If `error` is present, show the failed/declined
     connection state and do not call the canister. Only when both `code`
     and `state` are present, call and **await**
     `completeCalendarOAuth(code, state)` before navigating anywhere or
     clearing the URL. Keep a visible "Connecting Google Calendar…" state
     while it is pending. Do not replace the route, redirect to the home
     page, or discard the query parameters first — that loses the one-time
     code and leaves the user disconnected.
   - **Wait for actor readiness before the one-time callback call.** The page
     must wait for `useInternetIdentity().isAuthenticated` and
     `useActor(createActor)` to provide a non-null, non-fetching actor before
     calling `completeCalendarOAuth`. Do not set a `startedRef`/one-shot guard
     until then: on first render the actor is often unavailable, and an
     "Actor not ready" failure otherwise consumes the only retry while the
     authorization code is still in the URL.
   - After either terminal path, call `history.replaceState` to remove the
     OAuth query parameters. This prevents a page refresh from reusing a
     one-time authorization code.
   - Status driven by `isMyCalendarConnected()` (returns `Bool`).
   - Optional "Disconnect Calendar" button bound to `disconnectMyCalendar()`.

4. **Calendar UI** — the main page shows upcoming events. When
   `isCalendarConfigured()` is `false` and the caller is an admin, render a
   "Set up Google Calendar" link to `/settings/calendar` so the credentials
   page is discoverable, not just reachable. Pass the current
   time as the RFC 3339 `timeMin` value, `""` for an open-ended `timeMax`:
   `listUpcomingEvents(new Date().toISOString(), "", 10)`. To bound a single day
   (e.g. "meetings tomorrow"), pass both — the local start of the day and the
   start of the next day, each RFC 3339 with an offset — and count only entries
   whose `isAllDay` is false and `transparency` is not `"transparent"` and
   `eventType` is `"default"` (that filters out all-day, free, out-of-office,
   and working-location markers). This is required when
   using `singleEvents = true` and `orderBy = startTime`. Also include a
   "create event" form. `datetime-local` values have no offset, so convert
   each browser-local value to an RFC 3339 instant before calling the actor:
   `createEvent(summary, new Date(startInput).toISOString(),
   new Date(endInput).toISOString())`.
   When `isMyCalendarConnected()` is `false`, render an inline
   "Connect Google Calendar" link to `/connect/calendar`.

Suggested route layout:

```
/                   →  Main UI (upcoming events + create form)
/settings/calendar  →  Admin credential config (admin-only)
/connect/calendar   →  Per-user OAuth handshake (any signed-in user)
# If the app ALSO uses Gmail: drop the two routes above and use a single
# /settings/google + /connect/google — see "Combined Gmail + Calendar apps".
```

## Combined Gmail + Calendar apps

When an app uses both connectors, build **one** shared Google connection, not
two (an auth code is single-use, so two flows would force two consent screens).
Frontend:

- **One admin page `/settings/google`** — a single Client ID / Client Secret
  form, one `isGoogleConfigured` status, and one copyable redirect-URI field
  showing exactly `window.location.origin + "/connect/google"`.
- **One connect route `/connect/google`** — the same real callback route the
  Frontend section above requires: it renders "Connect Google", catches the
  redirect, waits for actor readiness, then calls completion once. No second
  callback route.
- **Do NOT build** `/settings/gmail`, `/connect/gmail`, `/settings/calendar`, or
  `/connect/calendar`. Every other Frontend requirement above still applies —
  only these paths change.

Backend — write the shared flow **once** (it replaces both per-connector OAuth
flows). It is the same shape as the per-connector `startAuthorize` /
`exchangeCode` / refresh functions, with these exact differences:

- One `#admin`-gated config setter storing a single Client ID/Secret.
- `SCOPES` = the union below — both APIs in one consent.
- `completeGoogleOAuth(code, state)` learns the connected email via
  `OAuth.getUserEmail` (OIDC userinfo — needs only `openid email`, not
  `gmail.readonly`) and stores one connection
  `{ accessToken; refreshToken; emailAddress }` in a single
  `Map<Principal, GoogleConnection>`.
- Gmail sends and Calendar calls each build **their own** client `Config` from
  that one `accessToken`, each keeping its single-refresh-on-401 retry.
- Keep the connection and client config in **one** shared state value and pass it
  as a parameter to both the Gmail and Calendar mixins, so both read and write the
  same connection (see the `writing-motoko` mixins rule).

```motoko filepath=src/backend/google.mo
let SCOPES : Text =
  "openid email "                                    // learn the address via userinfo
  # "https://www.googleapis.com/auth/gmail.send "
  # "https://www.googleapis.com/auth/calendar";
// Add "https://www.googleapis.com/auth/gmail.readonly " ONLY if the app reads mail.
```

Wire it as **one** connection shared by both services — declare the config,
connection map, and pending-flow map once and pass the **same** bindings to
every mixin. The Gmail and Calendar messaging mixins do **not** declare their own
config or connection; they receive the shared `googleConfig` and
`googleConnections` (config is needed for the refresh-on-401 retry):

```motoko filepath=src/backend/main.mo
actor {
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState, null);

  // ONE shared credential + connection state for both services.
  let googleConfig = { var clientId : Text = ""; var clientSecret : Text = "" };
  let googleConnections : Map.Map<Principal, Google.Connection> = Map.empty();
  let pendingGoogleFlows : Map.Map<Principal, Google.PendingOAuth> = Map.empty();

  include MixinGoogleConfig(accessControlState, googleConfig);                    // setGoogleCredentials / isGoogleConfigured (#admin-gated setter)
  include MixinGoogleOAuth(googleConfig, googleConnections, pendingGoogleFlows);  // startGoogleOAuth / completeGoogleOAuth, SCOPES = union above
  include MixinGmailMessaging(googleConfig, googleConnections);                  // sendEmail — refresh-on-401 needs config; reads the shared connection
  include MixinCalendarMessaging(googleConfig, googleConnections);               // calendar calls — same shared config + connection
};
```

Do not give Gmail and Calendar separate config/connection state or separate
OAuth flows — one auth code is single-use, and separate state desyncs (see the
`writing-motoko` mixins rule).

Enable both APIs on the one OAuth client and register only the single
`.../connect/google` redirect URI. Split into two separate panels **only** if
the user explicitly asks to connect two different Google accounts.

## Common to all variants

- **Sign-in is required** for every Calendar-related route. Wire the
  `/settings/...` and the connect route (`/connect/calendar`, or
  `/connect/google` in a combined app) through
  [`extension-authorization`](../extension-authorization/SKILL.md)'s
  auth guard (`useInternetIdentity` + redirect when `!isAuthenticated`).
- **The frontend never persists tokens.** No `localStorage`, no
  `IndexedDB`, no cookies — the canister mediates everything. The browser
  only ever sees `Bool` status flags and the OAuth redirect URLs.
- **The OAuth `state` parameter is canister-generated and validated.** The
  canister stores a random nonce with the pending verifier and callback URI.
  The frontend must pass both `code` and `state` to the completion call
  (`completeCalendarOAuth`, or `completeGoogleOAuth` in a combined app);
  it never creates or modifies either value.
- **The calendar UI is trivial:** a list of upcoming events, a create-event
  form with summary + start/end datetime inputs. No client-side Google SDK,
  no token handling, no JSON serialization — the canister is the Calendar client.

## Related

- [`mops add googlecalendar-client@0.1.4`](https://mops.one/googlecalendar-client) — Calendar REST API v3 bindings.
- [`mops add google-oauth@0.2.0`](https://mops.one/google-oauth) — Google OAuth 2.0 library (token exchange, refresh, PKCE, `getUserEmail` userinfo, `DateTime` RFC 3339 helpers).
- [Google OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server) — Web-client redirect URI and authorization-code flow reference.
- [Google Calendar API v3 reference](https://developers.google.com/calendar/api/v3/reference) — what `googlecalendar-client` wraps.
- [RFC 7636 — Proof Key for Code Exchange](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE spec.
- [extension-authorization](../extension-authorization/SKILL.md) — **required prerequisite**. Provides Internet Identity login, `useInternetIdentity` / `useActor` frontend plumbing, and the `#admin` role gate.
- [connector-googlemail](../connector-googlemail/SKILL.md) — sister connector using the same `google-oauth` library for Gmail.
