# Handling Incomplete Skills

After discovery, check whether the skill appears to still be under construction. A wall of
failures on a half-written skill isn't helpful — the user already knows it's not done. What
they need is a progress check: what's in place, what's missing, and what to build next.

## Signs of an incomplete skill

- SKILL.md has frontmatter but no body (or body is under 10 lines)
- SKILL.md body contains TODO, FIXME, TBD, or placeholder markers like `[fill in]`
- Scripts exist but are empty, contain only comments, or are clearly stubs
  (e.g., a Python file that's just `pass` or `# TODO: implement`)
- Referenced files in SKILL.md don't exist yet (not a broken link — they haven't
  been created)
- No description in frontmatter, or description is a placeholder
- Directory structure exists but most folders are empty

## Adjusted approach

1. **Tell the user what you see.** Be straightforward but constructive:
   > "This skill looks like it's still in progress — the SKILL.md has a workflow outline
   > but the script it references doesn't exist yet, and there are a couple of TODOs in
   > the instructions. I'll focus on what's here so far and flag what needs building next."

2. **Default to Quick Check.** Running Standard or Deep on stubs wastes time. If the user
   specifically asked for a deeper check, acknowledge the request but explain:
   > "A Standard Check would try to run scripts and test I/O, but since the script is
   > still a stub, those tests would all fail for the same reason. I'll do a Quick Check
   > on what exists and give you a roadmap for what to build next. We can run Standard
   > once there's more to test."

3. **Reframe findings as a build checklist, not a failure report.** Instead of the standard
   report format, present results as:

   > **SkillCheck Progress Report: [skill-name]**
   >
   > **What's in place:**
   > - SKILL.md with frontmatter (name + description) ✓
   > - Workflow outline with 5 steps ✓
   > - references/api-guide.md ✓
   >
   > **What's missing or incomplete:**
   > - scripts/generate_chart.py — referenced in step 4 but doesn't exist yet
   > - No declared inputs or outputs — the workflow describes them in prose but
   >   doesn't specify file types or schemas
   > - Two TODO markers in the SKILL.md body
   > - No evals directory
   >
   > **Suggested next steps (in order):**
   > 1. Write the generate_chart.py script
   > 2. Add explicit input/output declarations to SKILL.md
   > 3. Resolve the TODO items
   > 4. Run SkillCheck again at Standard depth

4. **Still run what you can.** Even incomplete skills benefit from:
   - Frontmatter validation (is the description good enough to trigger?)
   - Best practices review on what exists (catch structural issues early)
   - Security review on any scripts that do exist (catch problems before they spread)
   - Constraint consistency on any rules already written

   Skip tests that would obviously fail due to missing components — those aren't bugs,
   they're unfinished work.

5. **Don't use the standard verdict scale.** CRITICAL / NEEDS ATTENTION / etc. are
   for finished skills. For incomplete skills, the verdict is simply:
   > **Status: IN PROGRESS** — [X] of [Y] components in place.
