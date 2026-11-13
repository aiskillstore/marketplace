---
name: find-flats-and-fill-forms
description: Search rental portals for flats, pick the best listings and fill in the contact forms without sending them. Use when someone is looking for a flat to rent.
---

# Find flats and fill forms

This job runs on the user's own MyClawn cloud computer: a real browser that stays signed in, its own email address and files. It can outlast the chat and comes back with the answer, a screenshot of the final screen and a link to a screen recording.

## Setup

The user must have the MyClawn Computer connector signed in. If it is not, follow the setup in the cloud-computer-task skill of this repository and let the user do the sign-in; do not create accounts for them.

## Task

Hand this task to the connector's task tool, in the user's own words:

> Find two-room flats to rent in Vienna under €1,100 warm, listed in the last three days. Give me the five best with links. For the top three, fill in the contact form on the portal with this text: <the user's message>, and stop before sending.

Replace the city, the size, the budget and the message with the user's own. Show the final wording to the user before sending anything that submits a form, books something or writes to a third party.

## Steps

1. Write the task with the goal, the sites, what the result must look like and what must not be done.
2. Send it with the connector's task tool and wait for the result.
3. Report the answer, the screenshot and the recording link.

## Limits

It stops before anything is sent in the user's name; the user presses send. A portal that wants a login needs the user once. A captcha is the user's to solve on the live screen.

Full description of this job, with the steps and the limits: https://www.myclawn.com/find-flats-and-fill-enquiry-forms?utm_source=agent-skills&utm_medium=probe&utm_campaign=find-flats-and-fill-forms
