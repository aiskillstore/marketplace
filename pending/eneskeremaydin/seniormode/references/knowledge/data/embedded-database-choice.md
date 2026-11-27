---
id: "embedded-database-choice"
title: "SQLite or a database server"
category: "data"
summary: "Choose local embedded storage or a server according to writer coordination and deployment requirements."
aliases: ["sqlite vs postgres","embedded database","local storage","single writer","database server","SQLite mı PostgreSQL mi","yerel gömülü veritabanı","uzak birden çok yazıcı"]
decisions: [{"when":"A process owns a local file with modest write concurrency","use":"Use an embedded database and document file ownership, backups and transaction boundaries.","tradeoff":"Write contention and cross-host access still require care."},{"when":"Independent hosts routinely write shared state","use":"Use a database server with controlled access, concurrency and restore procedures.","tradeoff":"Deployment and operational complexity increase."}]
checks: ["Exercise realistic concurrency and recovery on the intended filesystem.","Restore a representative backup and verify read/write access and migrations."]
sources: [{"title":"SQLite appropriate uses","url":"https://sqlite.org/whentouse.html"},{"title":"PostgreSQL backup and restore","url":"https://www.postgresql.org/docs/current/backup.html"}]
---

<!-- Generated record title. -->
# SQLite or a database server

## Scenario

A local note tool opens a single workspace file. A later team edition would support many remote editors and centralized backups.

## Failure modes

Sharing an embedded database over unsupported network filesystems can corrupt assumptions. A database server adds operational cost to simple local tooling.

## Explain it simply

Use a local database when the data belongs to one runtime and move to a server when many remote writers need coordination.

## Implementation guidance

List cooperating processes, host locations and who owns backups before choosing the file format. For one workstation, an embedded database can give migrations and transactions with minimal operations. Back it up with its supported mechanism. When remote clients need shared writers or centralized access, a service-managed database moves that coordination to a defined owner. Test abrupt shutdown recovery and verify that a restore can be opened with the expected schema.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A process owns a local file with modest write concurrency** Use an embedded database and document file ownership, backups and transaction boundaries. Write contention and cross-host access still require care.
- **Independent hosts routinely write shared state** Use a database server with controlled access, concurrency and restore procedures. Deployment and operational complexity increase.

## Verification

- Exercise realistic concurrency and recovery on the intended filesystem.
- Restore a representative backup and verify read/write access and migrations.

## Sources

- [SQLite appropriate uses](https://sqlite.org/whentouse.html)
- [PostgreSQL backup and restore](https://www.postgresql.org/docs/current/backup.html)

<!-- End generated record details. -->
