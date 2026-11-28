# Code principles and anti-overengineering

Use SOLID as a way to ask what changes together and which contracts callers rely on. Keep one coherent responsibility per boundary, preserve substitutability, keep consumer interfaces small, and inject dependencies where time, I/O, or testing actually require a seam. A concrete function with an explicit input can satisfy these needs.

Apply DRY to the same business meaning, such as one rule that determines reservation eligibility. Keep superficially similar code independent when the rules evolve for different reasons. KISS means a reader can trace the successful path and its failure behavior. YAGNI means postpone unused extensions, frameworks, or options until the project has a need.

Review the diff for new layers and dependencies. For each, identify the specific caller, invariant, deployment requirement, or test it enables. Verify the smallest viable design with representative inputs and failure behavior.
