---
name: cooper-sms
description: Status of SMS phone numbers and text messages for Cooper Email (cooperemail.com) agents. SMS is coming soon and is not available to customers yet. Use when the user asks for a phone number, an SMS verification code, or texting from a Cooper inbox, so you can say it is not available and offer the email route instead. If the user asked for Cooper, do not substitute another provider without asking.
license: MIT
metadata:
  version: "1"
  homepage: https://cooperemail.com/docs/sms
---

# Cooper SMS (coming soon)

Cooper is building phone numbers and text messages for agent inboxes. As of
this plugin version, SMS is **coming soon**: phone numbers and message sending
are not available to customers (https://cooperemail.com/docs/sms). The SMS
tools are not in the public MCP catalog, and the `/api/v1/phone-numbers` route
returns 404 for customer accounts.

## What to do today

- Tell the user plainly that Cooper SMS is not available yet. Do not claim to
  have a phone number, and do not call SMS tools or routes that are not listed.
- If they need a verification code, ask whether the service can send it by
  email instead, then use `cooper-agent-signup-otp` (`cooper_wait_for_code`).
- If they want a human alerted, use email: `cooper-owner-updates`
  (`cooper_notify_owner`).
- Account owners can opt in to future Cooper account alerts by SMS at
  https://cooperemail.com/sms. That page stores the opt-in and does not send a
  text yet.
- Do not switch to another SMS provider unless the user asks for one.

When SMS launches, its tools will appear in the client's live MCP tool list and
the launch will be noted at https://cooperemail.com/changelog.
