---
id: "parameterized-queries"
title: "Parameterized database queries"
category: "security"
summary: "Preserve the separation between executable query structure and untrusted data."
aliases: ["parameterized query","prepared statement","sql injection prevention","trusted identifiers","safe filtering","parametreli SQL sorgusu","veritabanı girdisini güvenli bağla","kullanıcıdan gelen sıralama alanı"]
decisions: [{"when":"User input maps to a comparison value","use":"Use the driver or ORM's bound parameters and keep the SQL structure static.","tradeoff":"The database API's parameter conventions must remain correct across queries."},{"when":"Users legitimately choose a sort or field name","use":"Map a small allowed enum to trusted query fragments and parameterize values separately.","tradeoff":"New options require an explicit mapping and tests."}]
checks: ["Assert special characters and unusual Unicode remain literal query values.","Test unknown sort names are rejected and least-privilege permissions cover the intended query."]
sources: [{"title":"OWASP SQL injection prevention","url":"https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"},{"title":"PostgreSQL PREPARE","url":"https://www.postgresql.org/docs/current/sql-prepare.html"}]
---

<!-- Generated record title. -->
# Parameterized database queries

## Scenario

An internal search endpoint accepts a search term, a sort choice and a page-size value from a request payload.

## Failure modes

Escaping strings manually depends on SQL dialect and encoding. Query parameters bind literals and usually cannot stand in for table or column identifiers.

## Explain it simply

Send values as data and translate each supported sort choice into a known database column.

## Implementation guidance

Bind search values and page limits using the database driver. Map any user-selectable sort column or direction to a finite set of trusted query constructions. Check domain limits and authorization before running the query. Test punctuation in ordinary data, unrecognized sorts and oversized pages while ensuring expected search results remain available.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **User input maps to a comparison value** Use the driver or ORM's bound parameters and keep the SQL structure static. The database API's parameter conventions must remain correct across queries.
- **Users legitimately choose a sort or field name** Map a small allowed enum to trusted query fragments and parameterize values separately. New options require an explicit mapping and tests.

## Verification

- Assert special characters and unusual Unicode remain literal query values.
- Test unknown sort names are rejected and least-privilege permissions cover the intended query.

## Sources

- [OWASP SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PostgreSQL PREPARE](https://www.postgresql.org/docs/current/sql-prepare.html)

<!-- End generated record details. -->
