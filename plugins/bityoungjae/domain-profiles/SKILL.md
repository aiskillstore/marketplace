---
name: domain-profiles
description: "Domain-specific configuration profiles for learning resource creation. Defines search strategies, special fields, terminology policies, and content structures for different academic domains: technology, history, science, arts, and general. Use when researcher or writer agents need domain-adapted behavior."
allowed-tools: Read, WebSearch, WebFetch
---

# Domain Profiles Skill

This skill provides domain-specific configurations for learning resource creation.

## When to Use

- During `/init` Phase 2 (Research Collection)
- When researcher agent needs domain-specific search strategies
- When writer agent needs domain-adapted content structure
- When creating persona.md with Domain Guidelines section

## Available Profiles

| Profile    | File                           | Description                                    |
| ---------- | ------------------------------ | ---------------------------------------------- |
| Technology | [technology.md](technology.md) | Programming, frameworks, tools, APIs           |
| History    | [history.md](history.md)       | Historical events, periods, civilizations      |
| Science    | [science.md](science.md)       | Physics, chemistry, biology, mathematics       |
| Arts       | [arts.md](arts.md)             | Visual arts, music, performing arts            |
| General    | [language.md](language.md)     | General topics, linguistics, language learning |

**Note**: The "general" domain uses `language.md` profile, which contains broadly applicable patterns for educational content.

## Profile Structure

Each profile contains:

### 1. Search Strategy

Authoritative sources and search query patterns for the domain.

### 2. Special Fields

Domain-specific metadata fields to collect and include.

### 3. Terminology Policy

How to handle technical terms, translations, and citations.

### 4. Content Structure

Recommended document organization and pedagogical approach.

## Standard Loading Pattern

All agents should load domain profiles using this standardized pattern:

```
Read("skills/domain-profiles/{domain}.md")
```

**Domain to File Mapping**:

| Input Domain | File to Read |
|--------------|--------------|
| technology | technology.md |
| history | history.md |
| science | science.md |
| arts | arts.md |
| general | language.md |

**IMPORTANT**: When domain is "general", agents MUST read `language.md`, not "general.md" (which doesn't exist).

### Agent-Specific Usage

| Agent | Sections to Extract |
|-------|---------------------|
| researcher | Search Strategy, Special Fields, Quality Indicators |
| research-collector | Search Strategy, Special Fields |
| writer | Content Structure, Terminology Policy |
| reviewer | Review Criteria (Critical Checks, Quality Checks, Style Checks) |

## Usage Example

```
# In researcher agent prompt
Read("skills/domain-profiles/technology.md")
# Extract Search Strategy section for domain-appropriate queries

# In writer agent prompt
Read("skills/domain-profiles/technology.md")
# Apply Content Structure and Terminology Policy to document
```

## Domain Detection

Domains are determined by the project-interviewer during the interview:

| Domain           | Typical Topics                         |
| ---------------- | -------------------------------------- |
| technology       | Python, React, Docker, API, 프로그래밍 |
| history          | 조선시대, 르네상스, 세계대전, 문명     |
| science          | 양자역학, 미적분, 세포생물학, 화학     |
| arts             | 유화, 작곡, 조각, 연기, 디자인         |
| language/general | 언어학, 글쓰기, 일반 교양              |

## Fallback Behavior

If domain is unclear or "general", use:

- Broad academic search strategies
- Minimal special fields
- Standard terminology policy
- Flexible content structure
