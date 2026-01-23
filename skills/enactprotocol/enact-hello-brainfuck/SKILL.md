---
name: enact-hello-brainfuck
version: 1.0.0
description: A greeting tool written entirely in Brainfuck - the esoteric programming language
enact: "2.0"

from: debian:bookworm-slim

build:
  - apt-get update && apt-get install -y beef

command: beef /workspace/hello.bf

timeout: 30s

license: MIT

tags:
  - brainfuck
  - esoteric
  - hello
  - greeting
  - example

inputSchema:
  type: object
  properties: {}
  additionalProperties: false

outputSchema:
  type: object
  properties:
    message:
      type: string
      description: A greeting message from Brainfuck

examples:
  - input: {}
    description: Get a greeting from Brainfuck
---

# Hello Brainfuck

A greeting tool written entirely in **Brainfuck** - the famously minimalist esoteric programming language created by Urban Müller in 1993.

## About Brainfuck

Brainfuck has only 8 commands:
- `>` - Move pointer right
- `<` - Move pointer left
- `+` - Increment cell
- `-` - Decrement cell
- `.` - Output cell as ASCII
- `,` - Input to cell
- `[` - Jump past `]` if cell is zero
- `]` - Jump back to `[` if cell is non-zero

Everything else (including comments) is ignored.

## How It Works

The program builds each ASCII character using multiplication loops. For example, to print `H` (ASCII 72):
```brainfuck
>+++++++[-<++++++++++>]<++.[-]
```
This creates 7 in a cell, multiplies by 10 (using a loop), adds 2, then prints.

## Usage

### CLI

```bash
enact run enact/hello-brainfuck
```

### MCP (for LLMs/Agents)

Call `enact__hello-brainfuck` with no arguments.

## Output

Returns JSON:
```json
{"message":"Hello from Brainfuck!"}
```

## Why?

Because we can. And because every tool registry deserves at least one Brainfuck program.
