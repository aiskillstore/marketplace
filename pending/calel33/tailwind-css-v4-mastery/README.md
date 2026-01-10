# Tailwind CSS V4 Mastery Skill

## Overview

This skill equips Claude with expert-level knowledge of Tailwind CSS V4, enabling it to:

- **Design component systems** using CSS-first configuration
- **Execute migrations** from v3 to v4 with minimal risk and maximum efficiency
- **Optimize performance** leveraging the Oxide engine
- **Debug CSS-first patterns** systematically
- **Teach Tailwind V4** philosophy and best practices
- **Architect design systems** using CSS variables and modern patterns

---

## Directory Structure

```
tailwind-v4-mastery/
├── SKILL.md                           # Core skill definition
├── README.md                          # This file
├── scripts/
│   └── migrate-v3-to-v4.sh           # Automated migration script
├── references/
│   ├── breaking-changes.md           # v3 → v4 breaking changes
│   ├── configuration-guide.md        # @theme patterns & setup
│   └── performance-tuning.md         # Oxide engine optimization
└── assets/
    └── (future: templates, examples)
```

---

## Core Components

### SKILL.md
The master file that defines:
- **Philosophy:** CSS-first thinking
- **Mental Models:** How to think about V4
- **Workflows:** Migration, component design, optimization
- **Decision Trees:** When to choose which approach
- **Gotchas:** Common pitfalls and solutions

### Scripts

#### `migrate-v3-to-v4.sh`
Automated migration utility that:
- Backs up existing configuration
- Updates package.json with correct plugins
- Finds and updates CSS imports
- Migrates utility class names
- Removes old configuration files
- Provides migration summary

**Usage:**
```bash
bash scripts/migrate-v3-to-v4.sh /path/to/project
```

### References

#### `breaking-changes.md`
Complete reference of:
- Utility renames (shadows, rounded, outline, ring, etc.)
- Removed utilities (opacity, etc.)
- Default value changes
- Package structure changes
- Configuration system removal
- Impact assessment

#### `configuration-guide.md`
Practical patterns for:
- Simple color overrides
- Multi-theme with data attributes
- Complex spacing scales
- Custom typography systems
- Responsive breakpoints
- Animation & easing
- Component-scoped theming
- Enterprise multi-brand setup
- Anti-patterns to avoid

#### `performance-tuning.md`
Optimization guide covering:
- Performance baselines (10-100x faster)
- Plugin selection for max speed
- Configuration optimization
- Oxide engine configuration
- Build-level optimizations
- Measurement & profiling
- Common pitfalls
- Performance checklist

---

## When This Skill Activates

The skill activates when users ask about:

✅ **Do Use:**
- Tailwind V4 specifically (not v3)
- Component system design
- V3 → V4 migration
- CSS-first configuration
- `@theme` directives
- Oxide engine optimization
- Design system architecture
- Custom theme patterns

❌ **Don't Use:**
- Tailwind v3 or older (use general CSS)
- HTML/JS/Framework issues
- General CSS tutoring
- Non-web projects

---

## Usage Examples

### Example 1: User Wants to Migrate V3 Project

Claude routes to:
1. **Workflow:** Migration from V3 to V4
2. **Reference:** breaking-changes.md
3. **Script:** migrate-v3-to-v4.sh
4. **Guidance:** Step-by-step process with gotchas

### Example 2: User Wants to Build Design System

Claude routes to:
1. **Workflow:** Component System Design
2. **Reference:** configuration-guide.md
3. **Patterns:** Multi-theme setup, Enterprise multi-brand
4. **Code:** Copy-paste ready examples

### Example 3: User Wants Performance Optimization

Claude routes to:
1. **Workflow:** Performance Optimization
2. **Reference:** performance-tuning.md
3. **Decision Tree:** Plugin selection based on build tool
4. **Checklist:** Measurement and validation

---

## Key Capabilities

### 1. Architectural Expertise
Claude can explain:
- Why CSS-first configuration is better
- How Oxide engine works
- Modern CSS features used (OKLch, @property, color-mix)
- Browser support implications

### 2. Practical Migration
Claude can:
- Audit existing v3 projects
- Identify all breaking changes
- Provide automated tooling
- Guide step-by-step migration
- Troubleshoot common issues

### 3. Performance Optimization
Claude can:
- Select best plugin for build tool
- Optimize @theme configurations
- Measure and baseline improvements
- Debug performance issues
- Explain Oxide engine optimizations

### 4. Design System Architecture
Claude can:
- Design multi-theme systems
- Build component libraries
- Use CSS variables strategically
- Handle enterprise scenarios
- Implement brand customization

---

## Knowledge Base

### Core Concepts (In SKILL.md)
- Oxide Engine Revolution
- CSS-First Configuration Paradigm
- Browser Requirements
- Mental Model Shifts

### Decision Logic (In SKILL.md)
- Plugin Selection
- Configuration Approach
- Component Extraction
- Migration Timing

### Practical Knowledge (In References)
- Breaking changes with solutions
- Configuration patterns (9 patterns)
- Performance techniques
- Common gotchas and prevention

---

## Testing the Skill

### Test 1: Migration Guidance
**User Query:** "I need to migrate my Tailwind v3 project to v4"

**Expected Response:**
- Route to Migration Workflow
- Ask clarifying questions (scope, timeline)
- Provide breaking-changes.md reference
- Suggest migrate-v3-to-v4.sh script
- Walk through each step with gotchas

### Test 2: Component Design
**User Query:** "Help me design a dark mode component system for Tailwind V4"

**Expected Response:**
- Route to Component System Workflow
- Provide configuration-guide.md patterns
- Show multi-theme example
- Explain CSS variable strategy
- Copy-paste ready code

### Test 3: Performance Question
**User Query:** "How do I make my Tailwind V4 build faster?"

**Expected Response:**
- Route to Optimization Workflow
- Ask about build tool (Vite? Webpack?)
- Recommend best plugin
- Show optimization patterns
- Provide measurement checklist

---

## Future Extensions

### Additional Scripts
- Component generator
- Theme converter (v3 config → v4 CSS)
- Breaking change checker
- Performance auditor

### Additional References
- Color space migration guide
- Framework-specific setup (Next.js, SvelteKit, etc.)
- Advanced custom modifier patterns
- Third-party plugin compatibility

### Assets
- Component templates
- Design system starters
- Figma/design file resources
- Presentation slides

---

## Maintenance

This skill should be updated when:
- Tailwind V4 releases major updates
- New breaking changes or features appear
- Community discovers new patterns
- Performance benchmarks change

### Version History
- **1.0.0** — Initial release (Jan 2025)
  - Core workflows
  - Breaking changes reference
  - Configuration patterns
  - Performance tuning guide
  - Migration script

---

## Resources

- **Official Docs:** https://tailwindcss.com/docs
- **GitHub:** https://github.com/tailwindlabs/tailwindcss
- **Playground:** https://play.tailwindcss.com
- **Discord:** https://tailwindcss.com/discord

---

## Philosophy

> "Tailwind V4 is not just faster—it's a philosophical shift to CSS-first thinking. The skill installs this mental model, enabling Claude to think in CSS rather than JavaScript, to leverage the Oxide engine, and to build systems aligned with modern web standards."

This skill represents the difference between knowing Tailwind V4 syntax and understanding Tailwind V4 architecture.

