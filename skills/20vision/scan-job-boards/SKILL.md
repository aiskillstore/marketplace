---
name: scan-job-boards
description: Scan several job boards for new postings that match a search and list title, company, location and link. Use when someone wants a recurring job-board check across sites.
---

# Scan job boards

This job runs on the user's own MyClawn cloud computer: a real browser that stays signed in, its own email address and files. It can outlast the chat and comes back with the answer, a screenshot of the final screen and a link to a screen recording.

## Setup

The user must have the MyClawn Computer connector signed in. If it is not, follow the setup in the cloud-computer-task skill of this repository and let the user do the sign-in; do not create accounts for them.

## Task

Hand this task to the connector's task tool, in the user's own words:

> Check karriere.at, LinkedIn Jobs and StepStone for postings from the last seven days that mention “developer advocate” in Austria. List title, company, location and link.

Replace the boards, the search words, the region and the time window with the user's own. Ask it again next week: it remembers what it already showed. Show the final wording to the user before sending anything that submits a form, books something or writes to a third party.

## Steps

1. Write the task with the goal, the sites, what the result must look like and what must not be done.
2. Send it with the connector's task tool and wait for the result.
3. Report the answer, the screenshot and the recording link.

## Limits

Applying stays with the user; nothing that carries their name is sent. A captcha is the user's to solve on the live screen.

Full description of this job, with the steps and the limits: https://www.myclawn.com/scan-job-boards-for-new-postings?utm_source=agent-skills&utm_medium=probe&utm_campaign=scan-job-boards
