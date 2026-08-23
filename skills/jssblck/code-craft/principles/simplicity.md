# Earn your abstractions; profile before optimizing

> Prefer the smallest correct thing. Add indirection only when real callers need
> it. Optimize only what you have measured.

Premature abstraction and premature optimization are the same error: paying a
cost now for a benefit that may never arrive, and obscuring the code in the
meantime.

## Earn abstractions

- **Rule of two (lean toward three).** Do not introduce a generic, a
  trait/interface, a base class, a config option, or a new layer until there are
  at least two real, present callers that need it. One caller does not justify
  an abstraction; it justifies a concrete function. Duplication is cheaper to
  fix later than the wrong abstraction.
- **Concrete first.** Write the specific version. When the second case appears,
  factor out exactly what they share, no more. The shape of the right
  abstraction is obvious once you have two examples and guesswork before.
- **Indirection has a cost.** Every interface, callback, generic parameter, and
  layer is something the next reader must hold in their head and follow to find
  the real behavior. Add it when it removes more complexity than it adds.
- **Avoid speculative generality.** "We might need to swap the database",
  "someone might want another backend": until that someone exists, the
  flexibility is dead weight that constrains the code that does exist.
- **Type erasure / dynamic dispatch on a hunch.** Reaching for `dyn Trait`,
  `interface{}`/`any`, or a plugin registry where a concrete type would do trades
  clarity and performance for flexibility you are not using.

When the abstraction does arrive, make it as small as the real callers require,
named for what it does, sealed where it should not be extended.

## Profile before optimizing

- **Measure first.** Intuition about hot paths is wrong more often than right.
  Profile or benchmark to find where time/allocations actually go before
  changing anything for speed.
- **Optimize the proven hot path, then measure again.** Confirm the change
  helped and did not regress elsewhere. An optimization you did not verify is a
  complexity increase you are guessing about.
- **Do not trade clarity for unmeasured speed.** Manual index loops over clear
  iterators, hand-inlining, micro-tricks: only once a measurement says this spot
  matters. Readable code that is fast enough beats clever code that is
  marginally faster and wrong next quarter.
- **Algorithm and data layout beat micro-tweaks.** The O(n^2) that should be
  O(n), the repeated work that should be cached, the chatty IO that should be
  batched: these dominate. Find them before tuning constants.

## Smallest correct thing

The default for any change: the simplest implementation that is correct, clear,
and tested. Reach for more (a generic, an optimization, a layer) only when the
code in front of you, not an imagined future, demands it. This is not an excuse
to under-build the requested outcome; it is a rule against building things
nobody asked for and nobody measured.
