---
name: softsync-meetings
description: "Find calendar events, and manage booking pages: free times, bookings, booking a meeting for someone, rescheduling and cancelling. Use when the user asks when they meet someone, or wants to book, move or cancel a meeting."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Meetings

Two different things live here: **calendar events** synced from Google and Outlook, and **bookings** made through the workspace's booking pages.

## Calendar events
`calendar_events` with action `list` answers "what meetings do I have this week?", "when did we last meet Acme?" and "who was at the kickoff?".
- A time window: `from` and `to` as ISO 8601 times. Use `order: oldest_first` for what is coming up, `newest_first` for the most recent.
- About a company or contact: look it up with `search_records`, then pass its id as the recordId.
- By words in the title or description: `search`.
- Each event lists its attendees, the video link and the records it is linked to. `get_message_by_id` with the `eventId` returns everything.
Recorded meeting summaries are not calendar events: a saved summary is a note on the company or contact.

To put something in your own calendar: `calendar_events` with action `calendars` on a connected mailbox, then `manage_calendar_events` with action `create`. Actions `update` and `cancel` change or call it off. Everyone invited is emailed each time.

## Booking pages
A meeting type is a booking page guests use to book time with the team.
1. `meeting_types` with action `list`: each type, its length and its public `bookingUrl`. Sharing that link is usually all a user needs.
2. `meeting_bookings` with action `find_slots`: free times in a window of up to 31 days. For an event type, it returns sessions with seats left and their `sessionId`.
3. `meeting_types` with action `get`: the questions a guest must answer.
4. `manage_meeting_bookings` with action `book`: book for a guest with a free `start` and `answers` keyed by question label, e.g. {"Email": "ann@acme.com"}. Pass `sessionId` for an event. If an answer is missing, the error lists the questions.

## Managing bookings
- `meeting_bookings` with action `list`: booked meetings, soonest first, with the guest, the hosts and the video link.
- `manage_meeting_bookings` with action `reschedule`: move a booking to a new start time; it keeps its length. Check the time with action `find_slots` first.
- `manage_meeting_bookings` with action `cancel`: cancel and notify everyone. For an event session this cancels it for every guest.

## Running booking pages (Admin)
- `manage_meeting_settings` with action `enable` switches booking pages on for the workspace; `meeting_settings` with action `hosts` shows who can take bookings.
- `manage_meeting_types` with action `create`, `update`, `delete` or `new_link`. An update replaces the hosts, questions and other lists you send, so read the type first.
- The emails sent before a meeting: `meeting_types` with action `reminders` lists them, and `manage_meeting_types` with action `create_reminder`, `update_reminder` or `delete_reminder` changes them.
- `manage_meeting_bookings` with action `reassign` hands a booking to another host; the guest gets a new invitation. Actions `add_guests` and `remove_attendee` change who comes.
- `manage_meeting_bookings` with action `create_session` adds a date to an event type; action `update` changes how many places a session has.
- Your own bookable hours and the calendar bookings land in: `meeting_settings` with action `my_availability` or `shared_calendar` reads them, and `manage_meeting_settings` with action `set_my_availability` or `set_shared_calendar` changes them. An Admin reads a teammate's hours with `meeting_settings` action `host_availability` and changes them with `manage_meeting_settings` action `set_host_hours`.

## Rules
- Booking, rescheduling and cancelling send invites and emails to real people. Say who, when and what, and wait for a clear yes.
- An Admin can reschedule or cancel any booking; any other member only the bookings they host.
- Give times in the user's time zone and say which zone you mean.
