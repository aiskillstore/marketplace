# Project Setup: Compiler Flags

**Read this only when you are setting up a Motoko project yourself.** These are one-time `mops.toml` settings, not something to revisit while writing code.

**If your platform manages `mops.toml` for you, skip this file entirely** — do not inspect, add, or change `[moc] args`. The flags below are already set on your behalf, and editing them is not yours to do. This is the normal case for hosted platforms; it is only self-managed projects that need anything here.

## Persistence

Enhanced orthogonal persistence is `moc`'s default, so a top-level `let`/`var` in an actor is stable without the `stable` keyword. What is **not** default is letting a plain `actor { ... }` be persistent:

```toml
[moc]
args = ["--default-persistent-actors"]
```

Every actor example in this skill assumes that flag. Without it a plain `actor` fails to compile, with one of two errors depending on whether it holds state:

```text
// actor { var count = 0 }
type error [M0219], this declaration is currently implicitly transient, please declare it explicitly `transient`

// actor { public func f() : async Nat { 1 } }  — no stable declaration to complain about
type error [M0220], this actor or actor class should be declared `persistent`
```

If you cannot set the flag, write `persistent actor { ... }` instead — same semantics, declared per actor. (`persistent` is transitional; actors become persistent-by-default in a future major `moc` release.) `--default-persistent-actors` is not listed in `moc --help`, but it is supported.

## Style warnings

The style rules this skill enforces are compiler warnings that are **off by default**. Enabling them makes `moc` flag violations for you, and `mops check --fix` then auto-corrects all three:

```toml
[moc]
args = ["--default-persistent-actors", "-W", "M0236,M0237,M0223"]
```

`M0236` non-dot-notation calls, `M0237` redundant explicit implicit arguments, `M0223` redundant type instantiation.

Without `-W` in `[moc] args` these never fire, so `mops check --fix` has nothing to correct — the rules still hold, you just have to follow them unaided.
