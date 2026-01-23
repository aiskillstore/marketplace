---
name: coding-with-tailiwnd
description: Use this skill when you need to code with tailwind css
---

# Instructions

- Follow the rules below to code with tailwind css:

## Rules

- Create a seperate css file to style the component
- Use the tailwind `apply` directive to style the component
- Use the `@layer components` directive to style the component
- For tailwind 4.1 context, read the following docs:
  - `.claude/context/tailwind/tw-v4-theme-variable.md` to get the design principles
  - `.claude/context/tailwind/tw-v4-custom-styles.md` to get the custom styles
  - `.claude/context/tailwind/tw-v4-function-and-directives.md` to get the functions and directives
  - `.claude/context/tailwind/tw-v4-detecting-classes-in-source-files.md` to get the detecting classes in source files
  - `.claude/context/tailwind/tw-v4-upgrade-guide.md` to get the upgrade guide
- Use nested classes in `@layer components` for styling parents and children elements
- Use @utility directives to add custom utilities to the component
- Use @variant directives to add custom variants to the component
- Create a new component in `srs/components` root directory
- Never touch the files in `srs/components/ui` directory
