# Authentication and transport

## Read the right identities

Record RFC5322.From (visible author), SMTP MAIL FROM (usually represented by Return-Path after delivery), DKIM d= and s=, connecting IP, receiving system and timestamp. Trust Authentication-Results only when its provenance is the relevant receiver's trusted boundary; a pasted or sender-injected header is not independently verified. DKIM-Signature presence does not prove cryptographic validation.

## SPF

SPF authorizes sending hosts for the envelope domain, not the visible From address. Check the actual envelope domain rather than assuming the apex domain is used. Fetch all TXT records, distinguish multiple strings in one TXT record from multiple SPF records, and flag multiple SPF policies at the same name. Trace include/redirect expansion and lookup-causing mechanisms: the protocol limit is 10 during evaluation, not 10 visible includes. Also consider void lookups and loops. Preserve every legitimate sender when proposing consolidation. Do not add a second SPF record, use +all, blindly flatten changing provider IP ranges or invent a provider include value. Use provider-issued values. Forwarding commonly breaks SPF; do not infer malicious sending from that alone. See [RFC 7208](https://www.rfc-editor.org/info/rfc7208/), including updates and errata.

## DKIM

Check each relevant signature and the selector's public TXT/CNAME chain. Obtain exact selector/value from the sending service. Verify signing is enabled and new received messages pass; DNS publication alone does not prove this. Confirm the signing domain, algorithm and key length against current receiver/platform requirements. Prefer 2048-bit RSA when supported; check platform compatibility. Private keys never belong in DNS or chat. Keep old selectors until in-flight messages can complete during rotation. Examine transit modification and mailing-list behavior before attributing a failure. See [RFC 6376 and updates](https://www.rfc-editor.org/info/rfc6376/) and [RFC 8301](https://www.rfc-editor.org/info/rfc8301/).

## DMARC

A message passes when at least one passing authentication method aligns with the visible From domain: SPF's authenticated MAIL FROM domain or a valid DKIM d= domain. Both methods may pass while DMARC fails if neither aligns. Relaxed alignment uses the organizational domain; strict alignment requires an exact domain match. Do not approximate organizational domains by simply taking the final two labels.

Check the applicable policy, subdomain handling, alignment mode, report destinations and receiver implementation. A p=none policy requests monitoring rather than enforcement; it does not make a failing message pass or guarantee inbox placement. Inventory legitimate senders and inspect aggregate results before moving toward quarantine/reject. If the domain already has a functioning enforced policy, do not weaken it reflexively. Stage enforcement with representative coverage of business-critical senders, a rollback plan and authorization; do not assume every receiver implements legacy percentage-rollout tags or newer protocol features identically.

The RFC Editor now lists [RFC 9989](https://www.rfc-editor.org/info/rfc9989/) as the DMARC protocol specification, with [RFC 9990](https://www.rfc-editor.org/info/rfc9990/) for aggregate reporting and [RFC 9991](https://www.rfc-editor.org/info/rfc9991/) for failure reporting, replacing RFC 7489. Verify actual provider/tool support before relying on newer policy-discovery behavior. Reports are incomplete telemetry, not a complete sender inventory or proof of inbox placement. Verify authorization for external report destinations; failure reports may expose message content and personal information.

## Transport and forwarding

Check forward-confirmed reverse DNS for the actual sending IP, HELO/EHLO identity, TLS and RFC-compliant message format. On a shared ESP, the provider may own PTR/TLS/IP changes. Do not recommend changing the website's A record to fix mail PTR. Distinguish direct delivery from forwarding and mailing-list transformations. ARC can convey prior authentication assessments but is not an automatic DMARC bypass or inbox guarantee; assess receiver trust and documented support.

## Safe DNS change packet

Include current record, proposed record, exact DNS name/type, issuing platform source, legitimate senders preserved, TTL, expected effect, dependencies, rollback and verification. Mark unknown values explicitly; never provide fabricated production-ready keys or includes. Use reserved example.com/example.net domains for examples. An illustrative record is not a deployment instruction.
