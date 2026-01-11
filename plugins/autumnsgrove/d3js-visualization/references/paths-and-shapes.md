# Paths and Shapes Reference

## Line Generator

```javascript
const line = d3.line()
  .x(d => xScale(d.date))
  .y(d => yScale(d.value))
  .curve(d3.curveMonotoneX); // Smooth curve

const pathData = line(data);
svg.append("path")
  .attr("d", pathData)
  .attr("fill", "none")
  .attr("stroke", "steelblue");
```

### Curve Types

```javascript
d3.curveLinear          // Straight lines (default)
d3.curveBasis           // B-spline
d3.curveCardinal        // Cardinal spline
d3.curveCatmullRom      // Catmull-Rom spline
d3.curveMonotoneX       // Monotone cubic (good for time series)
d3.curveStep            // Step function
d3.curveStepBefore      // Step before
d3.curveStepAfter       // Step after
```

## Area Generator

```javascript
const area = d3.area()
  .x(d => xScale(d.date))
  .y0(height)              // Baseline
  .y1(d => yScale(d.value)) // Top line
  .curve(d3.curveMonotoneX);

svg.append("path")
  .attr("d", area(data))
  .attr("fill", "steelblue")
  .attr("opacity", 0.3);
```

## Arc Generator

```javascript
const arc = d3.arc()
  .innerRadius(0)           // 0 for pie, >0 for donut
  .outerRadius(100)
  .padAngle(0.02)           // Gap between slices
  .cornerRadius(3);         // Rounded corners

// Use with pie layout
const pie = d3.pie()
  .value(d => d.value)
  .sort(null);              // Don't sort

const arcs = svg.selectAll(".arc")
  .data(pie(data))
  .enter()
  .append("g")
  .attr("class", "arc");

arcs.append("path")
  .attr("d", arc)
  .attr("fill", (d, i) => colorScale(i));
```

## Force Simulation

```javascript
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links)
    .id(d => d.id)
    .distance(50))
  .force("charge", d3.forceManyBody()
    .strength(-100))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide()
    .radius(20))
  .on("tick", ticked);

function ticked() {
  // Update positions on each simulation step
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  node
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);
}
```
