---
id: "test-double-boundaries"
title: "Choosing test doubles and integration seams"
category: "testing"
summary: "Choose test doubles according to the behavior the test is intended to prove."
aliases: ["test doubles","fake vs mock","overmocking","integration test","test seam","test dublörü seçimi","mock yerine gerçek veritabanı testi","sahte bağımlılık"]
decisions: [{"when":"An isolated policy has stable inputs and outputs","use":"Test it directly using a small fake or data fixture at an external boundary.","tradeoff":"A unit test will not prove real database or transport behavior."},{"when":"A transaction, protocol or consistency contract is part of the invariant","use":"Use an integration test with a representative dependency and assert observable outcomes.","tradeoff":"These tests are more expensive and need controlled setup and teardown."}]
checks: ["Demonstrate a meaningful fault the chosen test would catch.","Confirm a refactor that preserves the public behavior leaves the test valid."]
sources: [{"title":"Martin Fowler, Mocks Aren’t Stubs","url":"https://martinfowler.com/articles/mocksArentStubs.html"},{"title":"pytest fixtures documentation","url":"https://docs.pytest.org/en/stable/how-to/fixtures.html"}]
---

<!-- Generated record title. -->
# Choosing test doubles and integration seams

## Scenario

An invoicing service depends on a database and job broker. Mock call assertions pass although a real uniqueness rule rejects the operation.

## Failure modes

Mocking internal call order makes safe refactors brittle. A fake's consistency or encoding can differ from the real dependency.

## Explain it simply

Replace pieces only where needed to control a test, and use the real pieces where their behavior determines correctness.

## Implementation guidance

A fake can model failure timing cheaply, but use the representative real database to test uniqueness and the real broker when durability matters. Assert the invoice state or durable event across that public boundary. A two-writer assertion that passes with an in-memory fake yet fails at the store is evidence to keep the integration case.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **An isolated policy has stable inputs and outputs** Test it directly using a small fake or data fixture at an external boundary. A unit test will not prove real database or transport behavior.
- **A transaction, protocol or consistency contract is part of the invariant** Use an integration test with a representative dependency and assert observable outcomes. These tests are more expensive and need controlled setup and teardown.

## Verification

- Demonstrate a meaningful fault the chosen test would catch.
- Confirm a refactor that preserves the public behavior leaves the test valid.

## Sources

- [Martin Fowler, Mocks Aren’t Stubs](https://martinfowler.com/articles/mocksArentStubs.html)
- [pytest fixtures documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)

<!-- End generated record details. -->
