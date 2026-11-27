---
id: "authorization-object-scope"
title: "Object-level authorization and tenancy"
category: "security"
summary: "Enforce read and write permissions at the boundary for every object backed by user-controlled identifiers."
aliases: ["access control","object authorization","tenant isolation","record ownership","permissions check","başka kiracıya ait faturayı görüyor","kurumlar arası kayıt erişimi","nesne bazlı yetki kontrolü","başka şirketin faturası","cross workspace invoice number","invoice accessible from another workspace","başka çalışma alanından fatura numarası"]
decisions: [{"when":"Permissions align to a simple owner or tenant","use":"Scope lookups and mutations to the caller's allowed tenant and enforce role checks for actions.","tradeoff":"Scopes must be applied to bulk, export and background paths too."},{"when":"Objects have delegated membership or shared ACLs","use":"Centralize reusable policy evaluation with clear deny-by-default and membership freshness behavior.","tradeoff":"Policy caching and delegation expand the test matrix."}]
checks: ["Verify a same-role user in another tenant receives no object on read or update.","Test missing membership, revoked sharing and bulk operation scoping."]
sources: [{"title":"OWASP Authorization Cheat Sheet","url":"https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html"},{"title":"OWASP broken object-level authorization prevention","url":"https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/"}]
---

<!-- Generated record title. -->
# Object-level authorization and tenancy

## Scenario

An invoice API returns a single invoice by ID. Staff in each organization may only access invoices owned by that organization.

## Failure modes

UI filtering does not enforce permission. A lookup by ID followed by an unscoped update may leave gaps on secondary paths or exports.

## Explain it simply

Check whether the requester may access the exact record each time the service reads or changes it.

## Implementation guidance

At the data boundary query by object identity and the caller’s authorized workspace scope, then check permission for the requested action. Apply the same policy to reads, mutations and exports. An invoice number identifies a record while membership governs access. Verify with two organizations that another workspace cannot read or mutate the invoice even with its number.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Permissions align to a simple owner or tenant** Scope lookups and mutations to the caller's allowed tenant and enforce role checks for actions. Scopes must be applied to bulk, export and background paths too.
- **Objects have delegated membership or shared ACLs** Centralize reusable policy evaluation with clear deny-by-default and membership freshness behavior. Policy caching and delegation expand the test matrix.

## Verification

- Verify a same-role user in another tenant receives no object on read or update.
- Test missing membership, revoked sharing and bulk operation scoping.

## Sources

- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP broken object-level authorization prevention](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)

<!-- End generated record details. -->
