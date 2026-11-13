---
name: book-appointment-online
description: Find providers with online booking and a free slot, fill in the booking form and stop before confirming. Use when someone wants an appointment (dentist, doctor, service) found and prepared.
---

# Book appointment online

This job runs on the user's own MyClawn cloud computer: a real browser that stays signed in, its own email address and files. It can outlast the chat and comes back with the answer, a screenshot of the final screen and a link to a screen recording.

## Setup

The user must have the MyClawn Computer connector signed in. If it is not, follow the setup in the cloud-computer-task skill of this repository and let the user do the sign-in; do not create accounts for them.

## Task

Hand this task to the connector's task tool, in the user's own words:

> Find a dentist in Vienna 1070 with online booking and a free slot on a Tuesday morning in the next three weeks. Go as far as the confirmation page and stop there.

Replace the provider type, the place and the time window with the user's own. Show the final wording to the user before sending anything that submits a form, books something or writes to a third party.

## Steps

1. Write the task with the goal, the sites, what the result must look like and what must not be done.
2. Send it with the connector's task tool and wait for the result.
3. Report the answer, the screenshot and the recording link.

## Limits

It stops before the booking is committed; the user confirms in their own name. A booking site that wants a login needs the user once. A captcha is the user's to solve on the live screen.

Full description of this job, with the steps and the limits: https://www.myclawn.com/find-and-book-an-appointment-online?utm_source=agent-skills&utm_medium=probe&utm_campaign=book-appointment-online
