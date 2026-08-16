## Description: <br>
Recommend hotel rooms and complete a real booking end to end against the `pricewin` MCP server: reserve an OpenTravel direct property, issue a payment link via bank QR, international card, or PayPal, check payment status, regenerate an expired link, and cancel a reservation. For Booking.com, Agoda, and Traveloka results it only hands back the provider's own booking link. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[cotghw](https://clawhub.ai/user/cotghw) <br>

### License/Terms of Use: <br>
MIT-0 <br>

## Use Case: <br>
Travel-planning agents use this skill to shortlist and recommend rooms for a stay, then take a user through an actual reservation: collecting guest details, confirming the total, issuing a payment link, and afterwards checking payment status or cancelling. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: This skill initiates real financial transactions. It creates bookings and payment links for actual money against a live property inventory. <br>
Mitigation: Deploy only where an agent is authorised to transact on the user's behalf. SKILL.md requires the agent to summarise hotel, room, dates, guests, and the full total, then obtain explicit user confirmation before calling `create_booking`. Do not remove that confirmation step. <br>
Risk: The booking flow collects guest personal data - full name, phone number, and email address - and transmits it to the booking backend and downstream payment providers. <br>
Mitigation: Collect only the four required fields, never store them beyond the booking turn, and never populate the guest email from an account or profile identity. SKILL.md mandates that the email come from what the user typed in the conversation, because the guest is frequently not the account owner and the confirmation is delivered to that address. <br>
Risk: Calling `create_booking` a second time for the same stay creates a duplicate reservation with a new confirmation code and a duplicate confirmation email, potentially double-charging the guest. <br>
Mitigation: An expired payment link must be repaired with `recreate_payment_link`, which reuses the existing confirmation code. Treat a second `create_booking` for a stay that already has a confirmation code as an error. <br>
Risk: Only OpenTravel direct properties are bookable through this skill; presenting an Agoda, Booking.com, or Traveloka result as reservable here would mislead a user into believing a stay is confirmed when it is not. <br>
Mitigation: Book only results carrying `source: "OPENTRAVEL_DIRECT"` and a `propertyId`. For every other source, present the provider's link and state plainly that the reservation happens on the provider's site. <br>
Risk: Payment is completed through third-party gateways (SePay bank transfer, Polar card processing, PayPal), each with its own terms and data handling. <br>
Mitigation: Present the three methods as equal options without steering, and let the user choose. Payment credentials are never handled by this skill or the agent. <br>
Risk: Prices and availability change between recommendation and booking; a room can disappear before payment completes. <br>
Mitigation: Read the total from `get_hotel_detail` immediately before booking rather than from an earlier search, and surface the 409 availability failure from `recreate_payment_link` to the user instead of retrying. <br>
Risk: An agent able to cancel a reservation unilaterally could act against the guest's interest. <br>
Mitigation: Cancellation deliberately requires a single-use token that is emailed to the booking's primary guest and must be pasted back by them. Do not attempt to work around this two-step flow. <br>

## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/cotghw/skills/pricewin-booking-assistant) <br>
- [Project homepage](https://github.com/Price-Win/pricewin-skills-hub) <br>
- [reference.md](artifact/reference.md) <br>

## Skill Output: <br>
**Output Type(s):** [markdown, guidance, payment links, booking confirmation codes] <br>
**Output Format:** [Markdown room recommendations with rating, price, and cancellation terms; a payment link and an eight-character confirmation code on successful booking] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Prices are presented as returned by the property's base currency without conversion. A confirmation code identifies a real reservation and should be surfaced to the user verbatim.] <br>

## Skill Version(s): <br>
1.0.2 (source: SKILL.md frontmatter) <br>

## Ethical Considerations: <br>
This skill spends a user's money and handles their personal data, so it warrants stricter review than a read-only skill. Users should confirm that agent-initiated booking is permitted in their environment, keep the explicit-confirmation and guest-supplied-email requirements intact, and apply their organization's safety, security, privacy, and compliance requirements before deployment. <br>
