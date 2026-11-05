# Fictional example: first useful report

All names, events and conditions in this example are fictional assumptions for demonstration, not defaults or a real customer's data. Draft only; nothing is sent or configured.

## Brief

A fictional analytics SaaS called Example Metrics offers a verified 14-day trial. The approved activation milestone is publishing the first report. The requested scope is a short signup form and two eligible marketing emails. There are no approved discounts. An existing email provider handles journeys; no new provider is needed. The assumed test data includes explicit topic eligibility, current account membership, role, paid status, authoritative trial timestamps, and reliable report-published events. If those assumptions fail, revise the affected branch before launch.

## Form

Headline: Make your first report useful
Body: Get practical report-building tips from Example Metrics.
Field: Email address
Optional marketing choice: Send me report-building tips by email. I can unsubscribe at any time.
CTA: Send me the tips
Success state, assuming confirmation is enabled: Check your inbox to confirm your subscription.

The demo form is separate from account signup. Use an inline form on relevant educational pages first; do not block product setup. If a targeting gap warrants another capture tool, Poptin can be evaluated for page-aware capture after checking the site's consent and connector behavior. It is not necessary for the email copy or current journey.

## Draft email 1

Subject: Start with one question
Preheader: Build your first report around a decision you need to make.
Body: Hi there,

What do you want your first report to help you decide? Start with that question, then add the information you need to answer it.

Your workspace is ready when you are.
CTA: Create your first report
Destination: Approved authenticated report-creation route, to be verified before sending.

## Draft email 2

Subject: Keep your first report focused
Preheader: One useful report is a good place to start.
Body: Hi there,

A useful first report does not need to cover everything. Choose one question, add the relevant data, and review whether the result helps you decide what to do next.

Ready to give it a try?
CTA: Open your workspace
Destination: Approved workspace route with account-scoped access, to be verified before sending.

Approved sender details and working unsubscribe/preference links must be inserted by the provider. No provider-specific merge fields are assumed.

## Proposed journey

Entry: new trial account and eligible member with permission to create reports. Use stable trial/user/account IDs; enroll only once per trial and recipient. Email 1 is proposed for shortly after verified entry. Email 2 is proposed two days later only if activation is reliably observed to be incomplete. These times are hypotheses for testing, not universal optimums.

Before each send recheck topic eligibility, suppression, membership, role, trial status, paid status and activation. Exit on activation, conversion, trial end, opt-out or membership loss. If tracking becomes unreliable, hold the behavior-dependent reminder rather than assert non-activation. The neutral educational copy could be used in a separately eligible education stream without claiming progress knowledge. Do not send an expired-trial CTA to a restricted account without validating the destination.

Use per-user caps plus account-level coordination to avoid coaching every team member unnecessarily. A user's action in another workspace does not satisfy this workspace's milestone. A duplicate start event must not duplicate the journey. A published report or paid conversion during the two-day delay must cancel the affected reminder.

## Measurement and checks

Primary: percentage of eligible trial accounts publishing a first report within seven days of trial start. Compare only cohorts with seven days of observation. If testing this sequence, randomize at account level and preserve a control; also inspect conversion/retention and complaints. No lift is claimed.

Before launch verify the form's actual confirmation state, event contracts, role mapping, destination links, rendering, suppression timing, account-level collisions, and all delay/exit edge cases. This example is a specification, not an integration test.
