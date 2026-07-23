---
name: extension-email-raw
description: Send an email with multiple to, cc and bcc addresses.
version: 0.1.5
compatibility:
  mops:
    caffeineai-email: "~0.1.1"
caffeineai-subscription: [plus, pro]
---

# Email — Raw Multi-Recipient
Raw multi-recipient email extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Overview

This skill adds support for sending emails with multiple `to`, `cc`, and `bcc` recipients. Not suitable for bulk service emails (recipients see each other).

# Backend

## This extension is for sending an email with support for multiple `to`, `cc` and `bcc` addresses.

- This should NOT be used for sending service emails to multiple users because each recipient will see all the other recipients listed which would typically be a breach of user privacy.

### For sending an email

- This extension depends on the [extension-email](../extension-email/SKILL.md) for sending emails.
- Use the sendRawEmail function. 
- It returns a SendResult which is #ok if the email is sent successfully otherwise #err(error) with the error text. 
- There can be a maximum of 50 recipients in total
- Each recipient receives the same email

```mo:caffeineai-email/emailClient.mo
module {
  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendRawEmail(
    fromUsername : Text,
    to : [Text],
    cc : [Text],
    bcc : [Text],
    subject : Text,
    htmlBody : Text,
  ) : async SendResult;
};
```

### Example usage for sending an email reminder to meeting attendees.

```motoko filepath=src/backend/main.mo
import Runtime "mo:core/Runtime";
import EmailClient "mo:caffeineai-email/emailClient";

actor {
  public func sendMeetingReminder(
    meetingSubject : Text,
    meetingTime : Text,
    confirmedAttendeeEmails : [Text],
    tentativeAttendeeEmails : [Text],
  ) : async () {
    let result = await EmailClient.sendRawEmail(
      "no-reply",
      confirmedAttendeeEmails,
      tentativeAttendeeEmails,
      [],
      meetingSubject,
      "Reminder the meeting will start at " # meetingTime,
    );

    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Failed to send meeting reminder email: " # error);
      };
    };
  };
};
```
