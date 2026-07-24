---
name: extension-email-calendar-events
description: Support for organising events/meetings and sending invitations by email.
version: 0.1.5
compatibility:
  mops:
    caffeineai-email-calendar-events: "~0.1.1"
    caffeineai-authorization: "~0.1.1"
caffeineai-subscription: [plus, pro]
---

# Email — Calendar Events
Calendar events email extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds support for organising events/meetings and sending iCalendar invitations by email. It provides CRUD operations for calendar events and email-based invitation delivery.

# Backend

## This component is for organising events/meetings and sending invitations by email

- Internally it builds and attaches an iCalendar file to each attendees's email
- This component does not yet support receiving RSVPs from attendees

### To add/update/cancel/delete/get/list calendar events

- Use the prefabricated module `mo:caffeineai-email-calendar-events/calendarEvents.mo` which cannot be modified.

```mo:caffeineai-email-calendar-events/calendarEvents.mo
module {
  public type State = {
    var events : List.List<CalendarEvent>;
    var uidMap : Map.Map<Text, Nat>;
  };

  public func add(
    self : State,
    uid : Text,
    summary : Text,
    description : Text,
    location : Text,
    startTime : Nat64,
    endTime : Nat64,
    organizer : Mailbox,
    attendees : [Attendee]
  ) : ?CalendarEvent;

  public func update(
    self : State,
    uid : Text,
    summary : ?Text,
    description : ?Text,
    location : ?Text,
    startTime : ?Nat64,
    endTime : ?Nat64,
    organizer : ?Mailbox,
    attendees : ?[Attendee]
  ) : ?CalendarEvent;

  public func addAttendees(
    self : State,
    uid : Text,
    attendees : [Attendee]
  ) : ?CalendarEvent;

  public func removeAttendees(
    self : State,
    uid : Text,
    attendees : [Text]
  ) : ?CalendarEvent;

  public func cancel(self : State, uid : Text) : ?CalendarEvent;

  public func delete(self : State, uid : Text);

  public func get(self : State, uid : Text) : ?CalendarEvent;

  // Iterate over all calendar events older to newer
  public func iter(self : State) : Iter.Iter<CalendarEvent>;

  // Iterate over all calendar events newer to older
  public func reverse(self : State) : Iter.Iter<CalendarEvent>;
}
```

### For sending calendar event invittions to attendees by email

- This component depends on [extension-email](../extension-email/SKILL.md) for sending calendar event emails.
- Use the sendCalendarEvent function. 

```mo:caffeineai-email/emailClient.mo
module {
  public type CalendarEvent = {
    uid : Text;
    sequence : Nat32;
    method : CalendarEventMethod;
    summary : Text;
    description : Text;
    location : Text;
    startTime : Nat64;
    endTime : Nat64;
    organizer : Mailbox;
    attendees : [Attendee];
  };

  public type CalendarEventMethod = {
    #request;
    #publish;
    #cancel;
  };

  public type Mailbox = {
    email : Text;
    name : ?Text;
  };

  public type Attendee = {
    who : Mailbox;
    role : CalendarEventRole;
  };

  public type CalendarEventRole = {
    #chair;
    #required;
    #optional;
    #notParticipating;
  };
  
  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendCalendarEvent(fromUsername : Text, event : CalendarEvent) : async SendResult;
};
```

### Example usage for an app which can add/update/cancel/delete/get/list calendar events and send invitations to them by email

```motoko filepath=src/backend/main.mo
import Runtime "mo:core/Runtime";
import Principal "mo:core/Principal";
import Map "mo:core/Map";
import Random "mo:core/Random";
import Set "mo:core/Set";
import Iter "mo:core/Iter";
import Option "mo:core/Option";
import Text "mo:core/Text";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import EmailClient "mo:caffeineai-email/emailClient";
import CalendarEvents "mo:caffeineai-email-calendar-events/calendarEvents";
import Uuid "mo:caffeineai-email-calendar-events/uuid";

actor {
  public type UserProfile = {
    name : Text;
    email : Text;
  };

  // Include authorization component
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState);

  // Store a map of caller principal to UserProfile
  var userProfiles = Map.empty<Principal, UserProfile>();

  // Store a set of emails for uniqueness check
  var emails = Set.empty<Text>();

  // Store the calendar events
  let calendarEvents = CalendarEvents.new();

  public shared ({ caller }) func registerUser(name : Text, email : Text) : async () {
    // Check if the user already exists
    if (userProfiles.containsKey(caller)) {
      Runtime.trap("User already registered");
    };

    // Check if the email is already used
    if (emails.contains(email)) {
      Runtime.trap("Email already taken");
    };

    // Add a user record
    userProfiles.add(
      caller,
      {
        name;
        email;
      }
    );
    emails.add(email);
  };

  public shared ({ caller }) func addCalendarEvent(summary : Text, description : Text, location : Text, startTimeMs : Nat64, endTimeMs : Nat64) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can add calendar events");
    };

    let organiser = switch (userProfiles.get(caller)) {
      case (?o) {
        o
      };
      case (null) {
        Runtime.trap("Admin profile not found")
      };
    };

    let seed = await Random.blob();
    let uid = Uuid.generateV4(seed);

    if (
      calendarEvents.add(
        uid,
        summary,
        description,
        location,
        startTimeMs,
        endTimeMs,
        {
          name = ?organiser.name;
          email = organiser.email;
        },
        userProfiles.values().map(
          func({ name; email }) {
            {
              who = { name = ?name; email };
              role = #required;
            };
          }
        ).toArray()
      ).isNull()
    ) {
      Runtime.trap("Failed to add calendar event");
    };
  };

  public shared ({ caller }) func updateEventDetails(uid : Text, summary : ?Text, description : ?Text, location : ?Text, startTimeMs : ?Nat64, endTimeMs : ?Nat64) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can update calendar events");
    };

    if (
      calendarEvents.update(
        uid,
        summary,
        description,
        location,
        startTimeMs,
        endTimeMs,
        null,
        null
      ).isNull()
    ) {
      Runtime.trap("Failed to update calendar event");
    };
  };

  public shared ({ caller }) func addEventAttendees(uid : Text, attendees : [EmailClient.Attendee]) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can add calendar event attendees");
    };

    if (calendarEvents.addAttendees(uid, attendees).isNull()) {
      Runtime.trap("Failed to add attendees to calendar event");
    };
  };

  public shared ({ caller }) func removeEventAttendees(uid : Text, attendees : [Text]) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can remove calendar event attendees");
    };

    if (calendarEvents.removeAttendees(uid, attendees).isNull()) {
      Runtime.trap("Failed to remove attendees from calendar event");
    };
  };

  public shared ({ caller }) func cancelEvent(uid : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can cancel calendar events");
    };

    if (calendarEvents.cancel(uid).isNull()) {
      Runtime.trap("Failed to cancel calendar event");
    };
  };

  public shared ({ caller }) func listEvents() : async [CalendarEvents.CalendarEvent] {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can list calendar events");
    };

    calendarEvents.iter().toArray();
  };

  public shared ({ caller }) func deleteEvent(uid : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can delete calendar events");
    };

    calendarEvents.delete(uid);
  };

  public shared ({ caller }) func sendEventInvitation(uid : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can send calendar event invitations");
    };

    let event = switch (calendarEvents.get(uid)) {
      case (?e) {
        e
      };
      case (null) {
        Runtime.trap("Calendar event not found")
      };
    };

    ignore await EmailClient.sendCalendarEvent(
      "no-reply",
      event
    );
  };
};
```
