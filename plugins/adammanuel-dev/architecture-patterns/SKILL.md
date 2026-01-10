---
name: architecture-patterns
description: AI-friendly architecture patterns for TypeScript projects including Domain-Driven Design, Clean Architecture, Hexagonal Architecture, and Page Object Model testing patterns
---

# Architecture Patterns for AI-Assisted Development

## Overview

Modern software architecture patterns are extraordinarily effective when working with AI code generation. This skill provides comprehensive guidance on architecture patterns that help AI agents generate correct, coherent, and maintainable code for full-stack TypeScript projects.

## Why Architecture Matters for AI

Certain software architecture and design patterns greatly assist AI code-generation tools in producing high-quality output. By structuring projects with clear domain models, layered boundaries, and well-defined patterns, you reduce ambiguity for AI assistants and dramatically increase the consistency and correctness of their output.

Key principles:

- **Explicit modeling** reduces ambiguity about where logic should go
- **Clear separation of concerns** helps AI focus on one layer at a time
- **Consistent patterns** allow AI to reliably replicate your architectural decisions
- **Well-defined interfaces** act as contracts that guide AI implementation
- **Testability** becomes easier to achieve when architecture is sound

## Available Patterns

### [Domain-Driven Design (DDD)](./ddd.md)

DDD focuses on a clear domain model using Entities, Value Objects, Domain Services, and Repositories—all expressed in the ubiquitous language of the business. This explicit modeling gives AI agents a well-defined vocabulary and structure to follow.

**Best for:**

- Complex business domains with evolving rules
- Systems where business language matters
- Long-lived applications requiring flexibility
- Teams with domain expertise to capture

**Key benefit:** AI naturally follows domain terminology and structure, producing cohesive code that business stakeholders understand.

### [Clean Architecture (Layered & Onion)](./clean-architecture.md)

Clean Architecture organizes code into concentric layers with strict dependency inversion. This pattern provides a clear recipe for where any piece of logic belongs, giving AI a strong guardrail for consistent implementation.

**Best for:**

- Any TypeScript backend or full-stack application
- Teams wanting clear separation of concerns
- Projects that need to remain testable and maintainable
- Systems likely to need infrastructure changes

**Key benefit:** AI can implement one layer at a time, with clear responsibilities and interfaces for each layer.

### [Hexagonal Architecture (Ports & Adapters)](./hexagonal-architecture.md)

Hexagonal Architecture isolates core business logic from external integrations through explicit Port interfaces and Adapter implementations. The core depends only on abstractions, not on external technology details.

**Best for:**

- Applications with multiple external integrations (APIs, databases, message queues)
- Systems where switching implementations is important
- Complex systems where testing core logic matters
- Microservices architecture

**Key benefit:** AI can safely generate testable core logic separately from imperative adapters, with clear integration points.

### [Page Object Model (POM) for Testing](./page-object-model.md)

POM represents each page or significant UI component as a class that encapsulates interactions and locators. Tests use these page objects instead of raw browser commands.

**Best for:**

- End-to-end testing with Playwright, Cypress, or Selenium
- Web automation scripts
- UI testing that needs to remain maintainable
- Projects using AI to generate test code

**Key benefit:** AI can generate clear, reusable page objects and coherent test scenarios that are easy to understand and maintain.

## How to Use This Skill

1. **Choose your pattern** based on your project type and complexity
2. **Review the detailed guide** for that pattern with TypeScript examples
3. **Share the architecture with your AI assistant** as context for code generation
4. **Guide AI implementation** layer-by-layer or component-by-component
5. **Maintain consistency** by referencing the pattern in every prompt

## Real-World Results

Teams implementing these patterns with AI code generation have reported:

- **3x faster feature delivery** without sacrificing code quality
- **90%+ pattern compliance** when using clear architectural guidance
- **Significantly fewer refactors** due to better initial structure
- **Improved testability** making code easier to review and modify
- **Clear integration points** reducing architectural drift

## Key Principles Across All Patterns

### 1. Separation of Concerns

Each layer/component has a single, well-defined responsibility. AI generates more correct code when responsibility is clear.

### 2. Dependency Inversion

Inner layers don't depend on outer layers. This prevents the AI from generating tightly coupled code.

### 3. Interface Contracts

Well-defined interfaces between components act as contracts. AI can implement both sides correctly because the contract is explicit.

### 4. Consistency

Patterns are repetitive. When AI sees one repository interface, it naturally creates similar ones elsewhere.

### 5. Testability

Good architecture is inherently testable. AI-generated tests are more reliable when the code follows good patterns.

## Comparison at a Glance

| Pattern | Best For | Core Concept | AI Benefit |
|---------|----------|--------------|-----------|
| **DDD** | Complex business domains | Rich domain model in ubiquitous language | Clear vocabulary and structure |
| **Clean Architecture** | General full-stack apps | Layered with dependency inversion | Clear responsibility per layer |
| **Hexagonal** | Multi-integration systems | Core logic isolated via ports/adapters | Separate core from imperative code |
| **Page Object Model** | E2E testing | Page classes encapsulate UI interactions | Reusable, readable test code |

## Recommended Combinations

### Full-Stack Web Application

**DDD + Clean Architecture + Page Object Model**

- DDD defines your domain model and use cases
- Clean Architecture structures backend with proper layering
- POM provides maintainable E2E tests

### Microservice with Multiple Integrations

**DDD + Hexagonal Architecture**

- DDD defines bounded context
- Hexagonal isolates core from external services

### Testing-Heavy Project

**Clean Architecture + Page Object Model**

- Clean Architecture ensures testable code
- POM makes test generation reliable

### Legacy System Modernization

**Start with Hexagonal, then introduce DDD**

- Hexagonal helps gradually extract core logic
- DDD helps establish domain vocabulary

## Next Steps

1. **Read the pattern guide** most relevant to your project
2. **Review the TypeScript examples** provided
3. **Show the architecture template to your AI assistant**
4. **Guide generation step-by-step** within each layer/component
5. **Enforce patterns** through code review (human or automated)

## Related Resources

- See `ddd.md` for Domain-Driven Design deep-dive
- See `clean-architecture.md` for layered architecture examples
- See `hexagonal-architecture.md` for ports and adapters
- See `page-object-model.md` for E2E testing patterns

---

**Remember:** The goal isn't to follow patterns dogmatically, but to use them as guardrails that help both humans and AI write better code together.
