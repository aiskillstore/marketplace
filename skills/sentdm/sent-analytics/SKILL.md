---
name: sent-analytics
description: Queries Sent phone-number capabilities and aggregate messaging, deliverability, and contact analytics with the Sent MCP tools. Use when a user asks for number lookup, line or channel capability, messages sent, delivery rate, contact growth, dashboard metrics, period comparisons, or date-bounded trends. Use messaging-performance-analyzer for message-level evidence and root-cause diagnosis.
---

# Sent Analytics

Use `numbers.lookup`, `dashboard.messages_sent`, `dashboard.deliverability`, and `dashboard.contacts` for read-only analytics.

## Establish context

Use client-managed OAuth 2.1/PKCE. Never request or expose a token, API key, authorization header, client ID, or secret. Identify the active organization and Sender Profile when the client exposes them. If the requested scope differs, reauthorize through the client rather than adding credentials or hidden scope fields.

Minimize sensitive output: mask phone numbers, aggregate where possible, and omit contact, KYC, account, and message-body data that is not needed to answer the question.

## Look up a number

Use `numbers.lookup` to obtain available capability, formatting, type, or routing signals for the supplied number. A lookup describes capability; it is not evidence of opt-in, consent, ownership, identity, or permission to message. State that distinction whenever the result could be used to plan outreach.

## Query dashboard metrics

1. Resolve an explicit date range and timezone before calling a dashboard tool. If the user omits either, ask or clearly state the assumption.
2. Use `dashboard.messages_sent` for sent-volume metrics.
3. Use `dashboard.deliverability` for aggregate acceptance and delivery outcomes.
4. Use `dashboard.contacts` for aggregate contact metrics.
5. Keep comparisons on the same organization, Sender Profile, date range, timezone, channel, and aggregation grain unless the user explicitly requests otherwise.

Every result must state the date range and timezone used. Label accepted, sent, delivered, failed, and unknown states according to what the response actually establishes; never collapse accepted into delivered.

## Choose aggregate analytics or diagnosis

Use this skill for dashboard totals, rates, and trends. Use `messaging-performance-analyzer` when the request involves message-level delivery records, funnel drop-off, error-code clustering, or root-cause diagnosis. A deliverability dashboard can locate a change; it does not by itself prove the operational cause.
