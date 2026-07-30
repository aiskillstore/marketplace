# Research record

Candidate C011 was researched on 2026-07-27 and received a parent gate score of
44 out of 50.

## Repeated job

Hosts repeatedly need package and ingredient quantities before parties. Current
calculators confirm the job while exposing large differences in assumptions and
outputs.

The package therefore treats every rate as an input with a named source or
approver. It does not publish one universal demand formula.

## Current evidence

- [Party Genius AI methodology](https://partygeniusai.com/tools/party-drink-calculator/methodology), reviewed 2026-04-17, exposes separate guest, duration, weather, and beverage assumptions.
- [OnePageParty drink calculator](https://www.onepageparty.com/tools/party-drink-calculator), verified 2026-07-27, branches across bar types and alcohol-free service.
- [Brorano](https://brorano.com/), verified 2026-07-27, presents low, base, and high scenarios instead of one certain result.
- [CDC standard drink sizes](https://www.cdc.gov/alcohol/standard-drink-sizes/index.html), verified 2026-07-27, demonstrates that package size and alcohol content cannot be collapsed into an unlabeled universal serving.
- [NIAAA inclusive hosting guidance](https://www.niaaa.nih.gov/about-niaaa/directors-page/niaaa-directors-blog/holiday-party-here-are-tips-hosting-party-including-guests-who-may-not-be-drinking), published 2022-12-12, supports visible alcohol-free options without defining an event quantity formula.

## Design boundary

The skill owns scenario arithmetic, package rounding, inventory subtraction, and
unit reconciliation. A user or cited method owns the rates.

Live service pacing, preparation scheduling, recurring home-bar replenishment,
and personal drinking guidance remain outside this invocation.

## Maintenance

Garçon owns the shared procedure and calculator. Review the input schema,
official health boundaries, and linked calculator methodologies every six
months. A source change cannot silently alter a default because the calculator
contains no default demand rate.

The FixMeADrink connection is distributional. The product link stays outside
the core calculation procedure.
