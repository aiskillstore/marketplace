---
name: explain-expert
description: Analyze codebases and provide technical overviews covering core components, interactions, deployment architecture, and runtime behavior. Use when the user asks for codebase analysis, project overview, technical architecture explanation, or system documentation.
---

# Explain Expert

Provide comprehensive technical codebase analysis following a structured approach. Stay focused on providing a technical overview that helps a developer quickly understand how the system works. Avoid personal opinions or implementation suggestions unless specifically asked.

## Analysis Framework

When analyzing a codebase, follow these steps:

1. **Scan the repository structure** - Identify main directories, configuration files, and entry points
2. **Read key files** - Examine package.json, requirements.txt, docker files, README, and main source files
3. **Map dependencies** - Note external libraries and frameworks used
4. **Trace execution flow** - Follow how the application starts and processes requests

## Core Components Analysis

Describe the major components or modules, their responsibilities, and any key classes or functions they contain. Note any relevant design patterns or architectural approaches.

## Component Interactions

Explain how the components interact, including data and control flow, communication methods, and any APIs or interfaces used. Highlight use of dependency injection or service patterns if applicable.

## Deployment Architecture

Deployment Architecture: Summarize the deployment setup, including build steps, external dependencies, required environments (e.g., dev, staging, prod), and infrastructure or containerization details.

## Runtime Behavior

Describe how the application initializes, handles requests and responses, runs business workflows, and manages errors or background tasks.

## When to Use This Skill

Apply this analysis when:

- User asks "explain this codebase"
- User requests "project overview"
- User needs "technical documentation"
- User asks "how does this system work"
- User requests "architecture analysis"
