---
id: "modular-monolith"
title: "Modular monolith or independent service"
category: "architecture"
summary: "Choose a deployment boundary according to ownership, failure isolation and operational constraints."
aliases: ["microservice boundary","modular monolith","service ownership","independent deployment","architecture choice","modüler monolit","mikroservise bölmek","bağımsız dağıtım sınırı"]
decisions: [{"when":"One team and shared transactional logic dominate","use":"Use a modular monolith with deliberate interfaces and ownership of data.","tradeoff":"Deployments remain shared and independent scaling is limited."},{"when":"A boundary has distinct ownership, uptime or scaling needs","use":"Extract the service only after defining contracts, observability and fallback behavior.","tradeoff":"The service introduces network, deployment and reconciliation costs."}]
checks: ["Measure actual reasons for an extraction and compare simpler remedies.","Test independent failure and backward-compatible deployment before switching callers."]
sources: [{"title":"Martin Fowler, Monolith First","url":"https://martinfowler.com/bliki/MonolithFirst.html"},{"title":"Martin Fowler and James Lewis, Microservices","url":"https://martinfowler.com/articles/microservices.html"}]
---

<!-- Generated record title. -->
# Modular monolith or independent service

## Scenario

A small marketplace team maintains orders and notifications. The latter scales differently but the team currently deploys weekly from one repository.

## Failure modes

Splitting tightly coupled features into services can create distributed transactions and coordinated releases. A monolith can still have clear boundaries.

## Explain it simply

Keep related parts together until a specific scaling, ownership or reliability need justifies running one separately.

## Implementation guidance

Keep orders and notifications in one deployable until a separate ownership, scaling, release, or failure constraint is observable. Start with public module operations and explicit data ownership inside that process. Before extraction, list callers, the changes that need one transaction, fallback when the other side is down, and how old and new versions coexist. A library or worker in the same deployable can solve an isolated throughput problem with fewer operational obligations.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **One team and shared transactional logic dominate** Use a modular monolith with deliberate interfaces and ownership of data. Deployments remain shared and independent scaling is limited.
- **A boundary has distinct ownership, uptime or scaling needs** Extract the service only after defining contracts, observability and fallback behavior. The service introduces network, deployment and reconciliation costs.

## Verification

- Measure actual reasons for an extraction and compare simpler remedies.
- Test independent failure and backward-compatible deployment before switching callers.

## Sources

- [Martin Fowler, Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- [Martin Fowler and James Lewis, Microservices](https://martinfowler.com/articles/microservices.html)

<!-- End generated record details. -->
