# GitHub Benchmark Scan

- Query: `skills`
- Source: `github-api`
- Top repositories: `3`

## Suggested Next Step

Review the 3 benchmark objects below, then decide whether any of their patterns are worth borrowing into the new skill.

## Top 3 Benchmark Repositories

### obra/superpowers
- URL: https://github.com/obra/superpowers
- Stars: `226125`
- Description: An agentic skills framework & software development methodology that works.
- Topics: None

#### Patterns worth studying

- **method** (`process`): Borrow the way it turns a messy workflow into a repeatable operating path.
- **execution** (`cli`): Borrow the clear execution entrypoints and command structure.
- **evaluation** (`test`): Borrow explicit validation and quality gates that make iteration safer.
- **structure** (`docs`): Borrow the way it separates explanation, examples, and reusable structure.

#### Borrow

- Borrow the way it turns a messy workflow into a repeatable operating path.
- Borrow the clear execution entrypoints and command structure.
- Borrow explicit validation and quality gates that make iteration safer.

#### Avoid

- Do not import process overhead that only exists for that project's scale.
- Do not copy repo-specific commands or environment assumptions verbatim.
- Do not clone heavyweight evaluation scaffolding if a lighter gate is enough here.

#### README glimpse

# Superpowers

Superpowers is a complete software development methodology for your coding agents, built on top of a set of composable skills and some initial instructions that make sure your agent uses them.

## Quickstart

Give your agent Superpowers: [Claude Code](#claude-code), [Codex CLI](#codex-cli), [Codex App](#codex-app), [Factory Droid](#factory-droid), [Gemini CLI](#gemini-cli), [OpenCode](#opencode), [Cursor](#cursor), [GitHub Copilot CLI](#github-copilot-cli).

## How it works

It starts from the moment you fire up your coding agent. As soon as it sees that you're building something, it *doesn't* just jump into trying to write code. Instead, it steps back and asks you what you're really trying to do.

Once it's teased a spec out of the conversation, it shows it to you in chunks short enough to actually read and digest.

After you've signed off on the design, your agent puts together an implementation plan that's clear enough for an enthusiastic junior engineer with poor taste, no judgement, no project context, and an aversion to testing to follow. It emphasizes true red/green TDD, YAGNI (You Aren't Gonna Need It), and DRY.

Next up, once you say "go", it launches a *

### affaan-m/ECC
- URL: https://github.com/affaan-m/ECC
- Stars: `214381`
- Description: The agent harness performance optimization system. Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond.
- Topics: ai-agents, anthropic, claude, claude-code, developer-tools, llm, mcp, productivity

#### Patterns worth studying

- **method** (`workflow`): Borrow the way it turns a messy workflow into a repeatable operating path.
- **execution** (`command, shell, script`): Borrow the clear execution entrypoints and command structure.
- **structure** (`guide, docs`): Borrow the way it separates explanation, examples, and reusable structure.
- **governance** (`security, review`): Borrow the explicit review, safety, or operational trust boundaries.

#### Borrow

- Borrow the way it turns a messy workflow into a repeatable operating path.
- Borrow the clear execution entrypoints and command structure.
- Borrow the way it separates explanation, examples, and reusable structure.

#### Avoid

- Do not import process overhead that only exists for that project's scale.
- Do not copy repo-specific commands or environment assumptions verbatim.
- Do not mirror documentation bulk that adds context cost without improving reliability.

#### README glimpse

**Language:** English | [Português (Brasil)](docs/pt-BR/README.md) | [简体中文](README.zh-CN.md) | [繁體中文](docs/zh-TW/README.md) | [日本語](docs/ja-JP/README.md) | [한국어](docs/ko-KR/README.md) | [Türkçe](docs/tr/README.md) | [Русский](docs/ru/README.md) | [Tiếng Việt](docs/vi-VN/README.md) | [ไทย](docs/th/README.md) | [Deutsch](docs/de-DE/README.md) | [Español](docs/es/README.md)

![ECC — the agent harness operating system](assets/hero.png)

[![Stars](https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.ecc.tools%2Fbadge%2Fstars&style=flat)](https://github.com/affaan-m/ECC/stargazers)
[![Forks](https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.ecc.tools%2Fbadge%2Fforks&style=flat)](https://github.com/affaan-m/ECC/network/members)
[![Contributors](https://img.shields.io/github/contributors/affaan-m/ECC?style=flat)](https://github.com/affaan-m/ECC/graphs/contributors)
[![npm ecc-universal](https://img.shields.io/npm/dw/ecc-universal?label=ecc-universal%20weekly%20downloads&logo=npm)](https://www.npmjs.com/package/ecc-universal)
[![npm ecc-agentshield](https://img.shields.io/npm/dw/ecc-agentshield?label=ecc-agentshield%20weekly%20downloads&logo=npm)](https://www.npmjs.com/package/ecc-agen

### multica-ai/andrej-karpathy-skills
- URL: https://github.com/multica-ai/andrej-karpathy-skills
- Stars: `174264`
- Description: A single CLAUDE.md file to improve Claude Code behavior, derived from Andrej Karpathy's observations on LLM coding pitfalls.
- Topics: None

#### Patterns worth studying

- **evaluation** (`test, validation`): Borrow explicit validation and quality gates that make iteration safer.
- **structure** (`guide`): Borrow the way it separates explanation, examples, and reusable structure.
- **portability** (`plugin`): Borrow how it keeps core semantics stable across environments or integrations.

#### Borrow

- Borrow explicit validation and quality gates that make iteration safer.
- Borrow the way it separates explanation, examples, and reusable structure.
- Borrow how it keeps core semantics stable across environments or integrations.

#### Avoid

- Do not clone heavyweight evaluation scaffolding if a lighter gate is enough here.
- Do not mirror documentation bulk that adds context cost without improving reliability.
- Do not inherit platform lock-in or vendor-specific branching unless truly required.

#### README glimpse

# Karpathy-Inspired Claude Code Guidelines

> Check out my new project [Multica](https://github.com/multica-ai/multica) — an open-source platform for running and managing coding agents with reusable skills.
>
> Follow me on X: [https://x.com/jiayuan_jy](https://x.com/jiayuan_jy)

A single `CLAUDE.md` file to improve Claude Code behavior, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

English | [简体中文](./README.zh.md)

## The Problems

From Andrej's post:

> "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should."

> "They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do."

> "They still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task."

## The Solution

Four principles in one file that directly address these issues:

| Principle | Addr

## Cross-Repo Borrow Recommendations

- Borrow the way it turns a messy workflow into a repeatable operating path.
- Borrow the clear execution entrypoints and command structure.
- Borrow explicit validation and quality gates that make iteration safer.
- Borrow the way it separates explanation, examples, and reusable structure.
- Borrow how it keeps core semantics stable across environments or integrations.
- Ask the user which of these patterns feels most worth borrowing before freezing the package shape.

## Cross-Repo Avoid Recommendations

- Do not import process overhead that only exists for that project's scale.
- Do not copy repo-specific commands or environment assumptions verbatim.
- Do not clone heavyweight evaluation scaffolding if a lighter gate is enough here.
- Do not mirror documentation bulk that adds context cost without improving reliability.
- Do not inherit platform lock-in or vendor-specific branching unless truly required.

## Borrow Prompt

I found 3 public GitHub projects worth studying. Do you want to borrow any of these patterns for method, structure, execution, or portability?
