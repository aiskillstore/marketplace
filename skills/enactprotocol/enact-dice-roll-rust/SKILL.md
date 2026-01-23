---
name: enact/dice-roll-rust
version: 1.0.0
description: Roll dice with configurable sides and count - a simple Rust example tool
enact: "2.0"

from: rust:1.75-slim

build:
  - rustc -o /workspace/dice /workspace/dice.rs

command: /workspace/dice ${sides} ${count}

timeout: 60s

license: MIT

tags:
  - dice
  - random
  - rust
  - example
  - games

inputSchema:
  type: object
  properties:
    sides:
      type: integer
      description: Number of sides on each die (e.g., 6 for a standard die, 20 for a d20)
      default: 6
      minimum: 2
      maximum: 100
    count:
      type: integer
      description: Number of dice to roll
      default: 1
      minimum: 1
      maximum: 100

outputSchema:
  type: object
  properties:
    rolls:
      type: array
      items:
        type: integer
      description: Array of individual roll results
    total:
      type: integer
      description: Sum of all dice rolls
    sides:
      type: integer
      description: Number of sides on each die
    count:
      type: integer
      description: Number of dice rolled

examples:
  - input:
      sides: 6
      count: 2
    description: Roll two standard 6-sided dice
  - input:
      sides: 20
      count: 1
    description: Roll a single d20 (classic tabletop gaming)
  - input:
      sides: 6
      count: 4
    description: Roll 4d6 (common for D&D character stats)
---

# Dice Roll (Rust)

A simple dice rolling tool written in Rust. Demonstrates how to create an Enact tool with Rust.

## Features

- Roll any number of dice with configurable sides
- Returns individual rolls and total sum
- Supports common dice types: d4, d6, d8, d10, d12, d20, d100

## Usage Examples

### CLI

#### Roll a single d6
```bash
enact run enact/dice-roll-rust
```

#### Roll 2d6 (two six-sided dice)
```bash
enact run enact/dice-roll-rust -a '{"sides": 6, "count": 2}'
```

#### Roll a d20
```bash
enact run enact/dice-roll-rust -a '{"sides": 20}'
```

#### Roll 4d6 for D&D stats
```bash
enact run enact/dice-roll-rust -a '{"sides": 6, "count": 4}'
```

### MCP (for LLMs/Agents)

When using via MCP, call `enact__dice-roll-rust` with:
- `sides`: Number of sides per die (default: 6)
- `count`: Number of dice to roll (default: 1)

## Output

Returns JSON with:
- `rolls`: Array of individual die results
- `total`: Sum of all rolls
- `sides`: The die type used
- `count`: Number of dice rolled
