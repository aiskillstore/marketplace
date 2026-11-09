# Working with custom and proprietary engines

Use this path for an in-house engine, engine maker, unfamiliar framework, or a known engine
without a catalog skill. The project remains on its existing engine. Genre and discipline
skills describe portable systems; their named Godot/Unity/etc. bindings are examples, not
requirements to install or migrate to those engines.

## Establish the engine contract

Before engine-specific implementation, inspect the project's instructions, README, build
configuration, version/revision, and one working feature closest to the request. Local engine
documentation, public headers, implementation, and tests are the primary sources. Record a
small integration map in the project's normal design notes:

| Contract | Evidence to record |
|----------|--------------------|
| Build and run | Exact existing commands, target/platform, engine revision, test entry point |
| Lifecycle | Creation/destruction hooks, ownership, scene or entity changes, reload behavior |
| Time and input | Tick/render order, time units, action mapping, press/release edges |
| State and assets | Content definitions vs runtime state, stable IDs, asset loading/unloading |
| Relevant subsystem | Existing physics, UI, events, audio, or persistence API needed by this task |

For each row needed by the task, name the actual symbol/file and a working call site. Mark
unverified behavior as unknown. A similar engine's API is not evidence. Read only the subsystems
the feature needs; do not reverse engineer the entire engine to add an inventory.

If source is unavailable, use the supplied SDK/manual and shipped examples. If those do not
establish a required API, ask for the smallest missing declaration or working example. Continue
with data models and labeled pseudocode that do not depend on that API; do not claim it compiles.
Use only material the user can share; proprietary source need not be published to use this path.

## Bind concepts to the project

1. Load the relevant genre and disciplines, such as `rpg` + `save-systems` for inventory.
2. Separate engine-neutral rules from integration: quantities, stacking, equipment modifiers,
   and stable item IDs can be tested independently from rendering and input.
3. Map those rules onto the project's existing data, event, UI, and persistence conventions.
   Reuse its working interfaces instead of introducing a parallel framework.
4. Implement one small end-to-end slice with verified APIs, then run the established build,
   tests, and game. Check lifecycle changes such as scene reload or entity destruction.
5. Report tested behavior, commands, and any remaining unknown API binding explicitly.

For an RPG inventory, first locate the project's content schema/loader, player-state owner,
UI event handler, and save serializer. Keep item definitions separate from mutable quantities;
store stable IDs and versioned state rather than engine pointers. Test add/remove/stack and
equip/unequip rules, then a save/load round trip using the real serializer. This is an
integration recipe, not a proposed proprietary-engine API.

## Failure modes

- **Unknown engine becomes a Godot scaffold:** distinguish an existing unsupported engine from
  an empty new project. Keep the existing engine, language, assets, and build system.
- **A sample compiles only in another engine:** treat concrete examples as concepts and bind
  them to the verified local contract before writing production code.
- **No SDK access:** state precisely which binding is blocked; provide pseudocode and request
  the required signature/example rather than guessing names or return values.
- **New code bypasses engine ownership:** follow the working example's lifecycle and cleanup;
  test scene changes and restart as well as the first successful interaction.
