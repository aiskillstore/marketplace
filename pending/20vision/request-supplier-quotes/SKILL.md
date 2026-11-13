---
name: request-supplier-quotes
description: Write to suppliers from the computer's own email address, ask each for a quote and show every mail sent. Use when someone needs quotes from several suppliers.
---

# Request supplier quotes

This job runs on the user's own MyClawn cloud computer: a real browser that stays signed in, its own email address and files. It can outlast the chat and comes back with the answer, a screenshot of the final screen and a link to a screen recording.

## Setup

The user must have the MyClawn Computer connector signed in. If it is not, follow the setup in the cloud-computer-task skill of this repository and let the user do the sign-in; do not create accounts for them.

## Task

Hand this task to the connector's task tool, in the user's own words:

> Write to the three best suppliers from our spreadsheet from your own email address. Ask for a quote for 2,000 units delivered to Vienna, and ask them to reply to me at <the user's address>. Show me each mail in Sent.

Replace the suppliers, the quantity and the delivery place with the user's own. Say "draft first" if the user wants to check the tone before anything goes out. Show the final wording to the user before sending anything that submits a form, books something or writes to a third party.

## Steps

1. Write the task with the goal, the sites, what the result must look like and what must not be done.
2. Send it with the connector's task tool and wait for the result.
3. Report the answer, the screenshot and the recording link.

## Limits

Mail goes from the computer's own address, not the user's. Replies are read in the task chat. Anything involving the user's customers or money is theirs to check before it sends. A captcha is the user's to solve on the live screen.

Full description of this job, with the steps and the limits: https://www.myclawn.com/request-supplier-quotes-by-email?utm_source=agent-skills&utm_medium=probe&utm_campaign=request-supplier-quotes
