# Construct the program Timeline

Read this when deciding complete duration or naming absolute Instants and Windows. [Media
preparation](media.md) publishes local domains and Extents; [Timing](timing.md) explains direct and
projected values; [Visual](visual-clips.md) and [Audio](audio-clips.md) place media in the resolved work.

Timeline is the work's finite absolute frame domain. Its author declaration is an acyclic graph of
Instant and Window expressions with one required `end`.

```svml
<import as="time" from="@hypit/timeline-author@1"/>
<time:Clock id="clock" frame-rate="30"/>
<time:Timeline id="program" clock={clock}
  end="latest(answer.end,outro.end)">
  <time:Window id="opening" from="start" for={opening-media.extent}/>
  <time:Window id="answer" from="opening.end" for={answer-media.extent}/>
  <time:Instant id="claim" at="answer.end-12f"/>
  <time:Window id="outro" from="claim" for="3s"/>
</time:Timeline>
```

Each named declaration publishes an ordinary value: `program.opening` is a Window,
`program.opening.start` and `.end` are boundary Instants, and `program.claim` is an Instant.
`program.window`, `.start` and `.end` describe the complete Timeline.

A Window supplies exactly two of `from`, `until` and `for`. `for` accepts an exact frame, millisecond
or second duration, or a typed Extent. Point expressions can use `start`, the resolved `end`, literal
positions, named Instants, Window boundaries, exact offsets, `earliest(...)` and `latest(...)`.

Dependencies determine evaluation, so declarations can refer forward. Use `latest(...)` when several
branches can determine complete duration. A wholly authored animation can simply declare:

```svml
<time:Timeline id="animation" clock={clock} end="30s"/>
```

## Let resolved material determine duration

Generated speech or video can publish its Extent after the Source has been written. A Window consumes
that Extent, and any dependent boundary resolves through ordinary graph evaluation:

```svml
<time:Window id="speech" from="start" for={speech-media.extent}/>
```

Keep dependencies acyclic: a generation request that depends on Timeline end cannot also determine
that same end. Unknown references, empty Windows, values outside the final range and a non-positive
end are author errors.

## Project local evidence after Timeline resolves

Map one complete local domain to one equal-length Window when its self-contained evidence needs an
absolute position. Narrative projection uses this relation to publish requested Script Selections,
Moments or boundaries:

```text
NarrativeAlignment + LocalDomain + Window -> absolute Instants / Windows
```

This mapping preserves the local endpoints at native speed. Prepare trims, retiming or other altered
media before projecting evidence whose endpoints must remain meaningful.

Visual and Audio placement is a separate decision:

```text
SynchronizedMedia + Window -> visual / audio occurrence
```

Put a named Instant or Window inside Timeline when it participates in the construction DAG. After the
Timeline resolves, standalone time declarations and domain projectors can publish additional named
values against it. Components consume those values, including single-use ones, through ordinary
references. The project `TIMELINE.md` can retain human observations and their meaning; Source
constructs the executable Timeline.
