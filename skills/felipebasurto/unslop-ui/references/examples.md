# Before and after

## Contents
- Hero with eyebrow (U1, U3, U8)
- Numbered feature section (U2, U4)
- Card that explains itself (U4, U5)
- Status line (U6, U10)
- Badge with and without state (U9)
- KPI tile (U11, U14)
- Chart header (U12, U13)
- Chart scaffolding and legend (U15, U16)
- Form field (U7)
- Empty state (U4)
- Claim you cannot verify

## Hero with eyebrow (U1, U3, U8)

Before:
```html
<p class="text-xs uppercase tracking-widest text-indigo-500">Introducing Ledger</p>
<h1>Finance. Simplified. Finally.</h1>
<p>The all-in-one platform that helps modern teams seamlessly manage their money — without the hassle.</p>
```

After:
```html
<h1>Manage your team's money</h1>
```

The eyebrow goes (U1). The staccato slogan becomes the one thing the old subtitle actually said (U8). The subtitle goes, because without "all-in-one", "seamlessly" and "without the hassle" it repeats the heading (U3, unslop 7, 30).

Nothing here says what Ledger does beyond "manage their money", so the heading says no more than that. If the same page has a feature list that names card controls and receipt capture, the heading may use those words: "Ledger tracks your team's cards and receipts". It may not use a number, a speed or a feature that appears nowhere in the source.

## Numbered feature section (U2, U4)

Before:
```jsx
<span className="font-mono text-sm">01 //</span>
<h3>Smart sync</h3>
<p>Our smart sync feature automatically keeps your files in sync across all of your devices.</p>
```

After:
```jsx
<h3>Smart sync</h3>
<p>Your files stay in sync across your devices.</p>
```

The order of features isn't real, so the number goes (U2). The description drops the part that repeated the title and keeps the fact the title doesn't give: files, across devices (U4). It adds nothing the original didn't claim.

## Card that explains itself (U4, U5)

Before:
```jsx
<Card>
  <CardTitle>Recent activity</CardTitle>
  <CardDescription>This card shows your most recent activity across the workspace (updates in real time).</CardDescription>
  <ActivityList />
</Card>
```

After:
```jsx
<Card>
  <CardTitle>Recent activity</CardTitle>
  <ActivityList />
</Card>
```

If `CardDescription` is now imported and unused, its import goes too.

## Status line (U6, U10)

Before:
```jsx
<div className="flex items-center gap-2 text-xs">
  <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
  Live · 3 agents · Synced · v2.4.1 · Updated just now
</div>
```

After, when nothing in the app tracks a live connection:
```jsx
<p className="text-xs">3 agents</p>
```

If the dot is bound to a real websocket state, keep the dot with an `aria-label` and drop the word "Live".

## Badge with and without state (U9)

```jsx
<h3>Exports <Badge>New</Badge></h3>
{plan.isBeta && <Badge>Beta</Badge>}
```

The first badge always renders with fixed text, so it is decoration and goes. The second renders from `plan.isBeta`, so it stays and the report lists it under kept.

## KPI tile (U11, U14)

Before:
```jsx
<Tile>
  <span>💰 Total revenue</span>
  <strong>$48,200</strong>
  <span className="text-green-600">▲ 12% up</span>
  <p>Revenue grew 12% compared to last month, showing strong momentum.</p>
</Tile>
```

After:
```jsx
<Tile>
  <span>Revenue</span>
  <strong>$48,200</strong>
  <span className="text-green-600">▲ 12% vs last month</span>
</Tile>
```

"vs last month" is the one fact from the deleted sentence that the tile did not already show.

## Chart header (U12, U13)

Before:
```js
title: { text: 'Line chart of weekly active users' },
subtitle: { text: 'Each point represents one week. Hover over a point to see the exact value.' },
legend: { display: true }, // single series
```

After:
```js
title: { text: 'Weekly active users' },
legend: { display: false },
```

## Chart scaffolding and legend (U15, U16)

Before:
```js
datasets: [{ label: 'This year', data: thisYear }, { label: 'Last year', data: lastYear }],
plugins: { legend: { display: true, position: 'bottom' } },
scales: {
  y: { grid: { color: '#9ca3af', lineWidth: 2 }, border: { display: true, width: 2 }, ticks: { stepSize: 25 } },
},
```

After:
```js
datasets: [{ label: 'This year', data: thisYear }, { label: 'Last year', data: lastYear }],
plugins: {
  legend: { display: false },
  // Name each line at its last point instead of in a legend.
  datalabels: { display: (ctx) => ctx.dataIndex === ctx.dataset.data.length - 1, formatter: (v, ctx) => `${ctx.dataset.label} ${v}` },
},
scales: {
  y: { grid: { color: '#eeeeee', lineWidth: 1 }, border: { display: false } },
},
```

Same chart type, data and series colors. The gridlines become hairlines, the axis border goes, and the legend becomes two labels at the line ends.

## Form field (U7)

Before:
```html
<label>Email address</label>
<input placeholder="Enter your email address" />
<small>We'll use this email address to contact you.</small>

<label>Password</label>
<input type="password" placeholder="Enter your password" />
<small>At least 12 characters.</small>
```

After:
```html
<label for="email">Email</label>
<input id="email" type="email" />

<label for="password">Password</label>
<input id="password" type="password" />
<small>At least 12 characters.</small>
```

The visible label stays and is tied to its input. The placeholders repeated the labels and go. The first helper text restated the label and goes; the second is a constraint the user can't guess and stays. Do not replace a label with a placeholder or an `aria-label`.

## Empty state (U4)

Before:
```jsx
<EmptyState title="Oops! Nothing here yet 👀" description="It looks like you haven't created any projects yet. Get started by creating your very first project!" />
```

After:
```jsx
<EmptyState title="No projects" description="Create a project to see it here." />
```

Empty states keep a sentence, but a plain one: what is the case, what to do next.

## Claim you cannot verify

```html
<p>Trusted by 10,000+ teams</p>
<blockquote>"Ledger cut our month-end close in half." Sarah Chen, CFO at Northwind</blockquote>
```

Leave both as they are. Whether they are true is not in the code, and deleting real social proof costs as much as keeping a made-up one. Report them:

```
- [ ] landing.html:31  "Trusted by 10,000+ teams": confirm the number or remove
- [ ] landing.html:32  testimonial from Sarah Chen: confirm it is a real customer quote or remove
```
