# Author timing relationships

Read this when deciding when a component exists or acts. [Script syntax](script-syntax.md) names
Narrative relationships; [Timeline](timeline.md) constructs the finite absolute domain. Components
consume absolute Instants and Windows.

## Choose the time source that matches the event

Use Narrative time when a picture or event should follow meaning as wording or performance changes.
Use direct Timeline time when it should follow the film clock. Both choices resolve to the same
absolute value types.

`semantic:Projection` maps aligned local evidence into Timeline. Independent declarations explicitly
choose it when revealing the semantic values this production asks to reuse:

```svml
<semantic:Projection id="story-time" narrative={story} timeline={film.timeline}>
  <semantic:Map alignment={speech.alignment} domain={speech-media.domain} window={film.speech}/>
</semantic:Projection>
<semantic:Window id="proof" projection={story-time} during={story.selection.proof}/>
<semantic:Instant id="claim" projection={story-time} at={story.moment.claim}/>
<semantic:Instant id="answer-end" projection={story-time}
  at={story.segment.answer} boundary="end"/>
```

Components then use `proof`, `claim` and `answer-end` as ordinary
Window and Instant values.

## Declare, then consume

Timeline authoring and domain projectors produce named values. Components only consume them:

| Form | Result |
| --- | --- |
| `<time:Window id="beat" timeline={film.timeline} from="2s" for="12f"/>` | A named absolute Window |
| `<time:Window id="answer" timeline={film.timeline} from={claim} until={answer-end}/>` | A named Window between projected Instants |
| `during={proof}` | Consume a projected Window |
| `during={beat}` | Consume a directly authored Window |

Window declarations supply exactly two of `from`, `until` and `for`. `for` can also reference a
TemporalExtent, including generated media duration. The complete film is already named as
`film.window`.

## Instant forms

| Form | Result |
| --- | --- |
| `at={claim}` | A projected event |
| `<time:Instant id="cut" timeline={film.timeline} at="2s"/>` | A named direct clock event |
| `<time:Instant id="credits" timeline={film.timeline} at="timeline.end-12f"/>` | A named event relative to the Timeline boundary |
| `<time:Instant id="after-claim" timeline={film.timeline} at={claim} offset="+5f"/>` | A separate absolute offset from a resolved event |
| `at={cut}` | Consume the named event |

The component decides what the event changes and whether that state persists.

## Name shared values

Name even a single-use absolute value outside the consuming component. Put it in Timeline when it
helps determine film extent; otherwise use a standalone declaration against the completed Timeline.
Publish a projected value when its domain identity matters to the production.

## Choose what a later edit changes

The authored value determines the editing relationship:

- editing a direct literal changes that literal;
- editing a named Timeline value changes its Timeline declaration;
- editing a Narrative-produced value changes the mapping or Narrative source that produced it;
- editing a reused value changes its producer and all consumers follow after recompilation.

Studio can display any resolved value. It offers source editing only where the package declares a
meaningful author relation. Keep semantic relationships, absolute offsets and response duration as
separate decisions.
