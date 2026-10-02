# Diagnose React rendering

Use this reference when an interaction is slow or a proposed optimization needs evidence. Capture the same representative interaction before and after the change.

## Locate the cost

Use React DevTools Profiler to distinguish frequent renders, large rendered trees,
and expensive individual components. Use the browser Performance trace to separate
React work from event-handler computation, style/layout, paint, and network delay.
Development checks and tooling can affect timings; compare like-for-like runs.

| Evidence | Candidate change |
|---|---|
| Fast-changing state rerenders unrelated content | Move state closer to its owner or split the changing subtree. |
| A costly child rerenders with equivalent props | Check prop identity and compiler coverage; memoize only the work that benefits. |
| Thousands of rows mount or update together | Window or paginate the list; preserve focus, keyboard navigation, and accessible row information. |
| Sorting/filtering dominates an event handler | Use a worker, yielding chunks, or precomputation. Scheduling a React transition cannot interrupt that calculation. |
| Layout follows repeated geometry reads/writes | Batch reads before writes and reduce layout scope. |
| Heavy subtrees repeatedly remount | Check unstable keys/component definitions, then compare keeping state mounted with its memory/hidden-work cost. |

Use refs for transient values that do not drive rendered UI. Keep controlled
input updates urgent. Stabilize props only where identity causes measured
downstream work; allocating a small object during render is not inherently a bug.
Static content can benefit from CSS content visibility, but that does not remove
React reconciliation or replace list virtualization.

## Schedule the render, not blocking JavaScript

```tsx
const [query, setQuery] = useState('');
const [resultsQuery, setResultsQuery] = useState('');
const [isPending, startTransition] = useTransition();
const onChange = (value: string) => {
  setQuery(value); // urgent controlled input
  startTransition(() => setResultsQuery(value));
};
// A separate Results component renders from resultsQuery.
```

`startTransition` invokes its callback immediately. Calling an expensive
`filter(value)` inside that callback still blocks input. React can interrupt
rendering between components, not a single long computation. `useMemo` avoids
repeated calculations but does not make the first one asynchronous.

`useDeferredValue` is another way to let a costly view lag behind an urgent
input. Keep stale/pending feedback meaningful and check that the expensive child
can avoid rerendering for the urgent update.

## Compare the result

Check render duration/frequency, interaction latency, memory, and behavior after
the change. Confirm keyboard/focus behavior after virtualization and state
preservation after key or mounting changes. Report the tested scenario and device;
do not generalize one desktop measurement into a universal speed claim.

References: [useTransition](https://react.dev/reference/react/useTransition),
[useDeferredValue](https://react.dev/reference/react/useDeferredValue),
[Profiler](https://react.dev/reference/react/Profiler).
