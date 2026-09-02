# 10DLC evidence checklist

The evidence packet is an internal readiness artifact with `schema_version: "sent-10dlc-evidence/v1"`. Its snake_case fields are not the Sent API contract.

## Business identity

- [ ] Legal business name and EIN match registration records.
- [ ] Public website represents the same recognizable brand.
- [ ] Physical address, business phone, and compliance contact are current.
- [ ] Privacy policy and terms links are public HTTPS pages.

## Consent

- [ ] Opt-in method is named: web form, keyword, paper, or spoken consent.
- [ ] Proof URL or equivalent evidence is accessible to a reviewer.
- [ ] Consent text names the brand and message type.
- [ ] The checkbox is not preselected.
- [ ] Frequency, message/data-rate notice, HELP, and STOP disclosures are present where required.
- [ ] Marketing spoken consent includes the additional confirmation required by policy.

## Message flow

Describe the sequence from consumer action through confirmation and recurring messages. A link alone is not a message flow.

## Autoresponses

- [ ] `optinMessage` names the brand and explains HELP/STOP, frequency, and rates where required.
- [ ] `optoutMessage` confirms unsubscribe and no further messages.
- [ ] `helpMessage` names the brand and provides a support method.
- [ ] `optinKeywords`, `optoutKeywords`, and `helpKeywords` are documented.
- [ ] STOP is in opt-out keywords and HELP is in help keywords.

## Campaign translation

Map evidence into these Sent camelCase fields only at API serialization time:

```text
message_flow                  -> messageFlow
privacy_policy_url            -> privacyPolicyLink
terms_and_conditions_url      -> termsAndConditionsLink
autoresponses.optinMessage    -> optinMessage
use_cases[].messaging_use_case_us -> useCases[].messagingUseCaseUs
use_cases[].sample_messages   -> useCases[].sampleMessages
```

Run the evidence validator before translation and the campaign validator after translation.
