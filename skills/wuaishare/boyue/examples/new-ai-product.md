# Example: New AI Product

## Scenario

A team wants to build an AI research workspace. Early brainstorming produces many ideas:

- connected-data research;
- browser research;
- citation-backed reports;
- memory;
- workflow automation;
- voice;
- multi-agent orchestration;
- marketplace;
- CRM features.

## Explore / 博观

The team researches real user workflows, competing tools, model limitations, data permissions, and cost.

Evidence shows the strongest repeated need is:

> Combine company data and web research into a trustworthy report with traceable citations.

The option space remains broad, but no brainstorm item is treated as roadmap by default.

## Select / 约取

### COMMIT

- connected-data research;
- browser research;
- citation-backed report generation.

Evidence: these directly support the repeated user job.

### DEFER

- memory;
- workflow automation.

Revisit trigger: users repeatedly perform the same multi-step research flow and explicitly ask to save/reuse it.

### DISCARD

- CRM;
- voice-first interaction;
- marketplace.

Reason: they increase scope without strengthening the current product thesis.

## Shape / 厚积

The highest-risk decisions are data permissions and citation reliability, so the team spends shaping effort there.

Low-risk UI details are tested directly rather than subjected to heavyweight design reviews.

## Deliver / 薄发

First MCVS:

```text
Connect two approved data sources
  ↓
Run one research task
  ↓
Combine internal + web evidence
  ↓
Produce a report with citations
  ↓
Allow the user to verify sources
```

No marketplace, voice layer, workflow builder, or autonomous multi-agent system is included.

## Evidence

After release, the team measures report completion, citation verification behavior, repeated use, latency, and support issues before expanding the ownership surface.
