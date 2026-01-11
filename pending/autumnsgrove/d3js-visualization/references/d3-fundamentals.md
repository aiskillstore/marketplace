# D3.js Fundamentals Reference

## SVG Basics for D3

D3 primarily works with SVG (Scalable Vector Graphics), an XML-based markup language for describing 2D graphics.

### Essential SVG Elements

```html
<!-- Rectangle -->
<rect x="10" y="10" width="100" height="50" fill="blue" />

<!-- Circle -->
<circle cx="50" cy="50" r="30" fill="red" />

<!-- Line -->
<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="2" />

<!-- Path (complex shapes) -->
<path d="M 10 10 L 50 50 L 10 90 Z" fill="green" />

<!-- Text -->
<text x="50" y="50" font-size="14" fill="black">Hello</text>

<!-- Group (for transformations) -->
<g transform="translate(50, 50) rotate(45)">
  <!-- elements here -->
</g>
```

### SVG Coordinate System

- Origin (0,0) is at **top-left** corner
- X increases to the right
- Y increases **downward** (different from Cartesian)
- Use `transform="translate(x, y)"` to reposition

## Data Binding Concepts

D3's core power comes from binding data to DOM elements.

### Basic Data Binding

```javascript
// Bind array to paragraphs
const data = [10, 20, 30, 40];

d3.select("body")
  .selectAll("p")
  .data(data)
  .enter()
  .append("p")
  .text(d => `Value: ${d}`);
```

### The Enter-Update-Exit Pattern

This is D3's fundamental data join pattern:

```javascript
// Initial data
const data = [1, 2, 3, 4, 5];

// Create selection
const circles = svg.selectAll("circle")
  .data(data);

// ENTER: Create new elements for new data
circles.enter()
  .append("circle")
  .attr("r", 5)
  .merge(circles) // Merge with existing
  .attr("cx", (d, i) => i * 50)
  .attr("cy", d => d * 10);

// EXIT: Remove elements without data
circles.exit().remove();
```

**Modern D3 v6+ Join Pattern:**

```javascript
svg.selectAll("circle")
  .data(data)
  .join(
    enter => enter.append("circle")
      .attr("r", 0)
      .call(enter => enter.transition().attr("r", 5)),
    update => update.attr("fill", "blue"),
    exit => exit.call(exit => exit.transition().attr("r", 0).remove())
  )
  .attr("cx", (d, i) => i * 50)
  .attr("cy", d => d * 10);
```

## Selections and Manipulation

### Selection Methods

```javascript
// Select single element (first match)
d3.select("body")
d3.select("#myId")
d3.select(".myClass")

// Select all elements (all matches)
d3.selectAll("p")
d3.selectAll(".item")

// Select within selection
const container = d3.select("#container");
container.selectAll(".item")
```

### Manipulation Methods

```javascript
// Set attributes
selection.attr("class", "highlight")
selection.attr("cx", 50)
selection.attr("cy", d => d.value * 10) // Function of data

// Set styles
selection.style("color", "red")
selection.style("font-size", "14px")

// Set properties
selection.property("value", "text")
selection.property("checked", true)

// Set text/HTML
selection.text("Hello")
selection.html("<strong>Bold</strong>")

// Append/Insert/Remove
selection.append("div")
selection.insert("p", ":first-child")
selection.remove()

// Class manipulation
selection.classed("active", true)
selection.classed("highlight", d => d.value > 100)
```

## Transitions and Animations

Transitions smoothly interpolate between states.

### Basic Transitions

```javascript
// Simple transition
d3.select("circle")
  .transition()
  .duration(1000)        // 1 second
  .attr("r", 50)
  .attr("fill", "red");

// With easing
selection
  .transition()
  .duration(500)
  .ease(d3.easeBounceOut)
  .attr("cx", 100);
```

### Easing Functions

```javascript
// Common easing functions
d3.easeLinear        // Constant speed
d3.easeCubic         // Slow-fast-slow
d3.easeBounce        // Bounce at end
d3.easeElastic       // Elastic oscillation
d3.easeBack          // Overshoot and return
d3.easeSin           // Sinusoidal
d3.easeExp           // Exponential
d3.easeCircle        // Circular

// In/Out/InOut variants
d3.easeCubicIn       // Slow start
d3.easeCubicOut      // Slow end
d3.easeCubicInOut    // Slow start and end
```

### Chaining Transitions

```javascript
selection
  .transition()
  .duration(500)
  .attr("r", 50)
  .transition()        // Chain next transition
  .duration(500)
  .attr("fill", "red")
  .transition()
  .duration(500)
  .attr("cx", 100);
```

### Transition Events

```javascript
selection
  .transition()
  .duration(1000)
  .attr("r", 50)
  .on("start", function() {
    console.log("Transition started");
  })
  .on("end", function() {
    console.log("Transition ended");
  })
  .on("interrupt", function() {
    console.log("Transition interrupted");
  });
```

### Staggered Transitions

```javascript
// Delay each element
circles
  .transition()
  .duration(500)
  .delay((d, i) => i * 100)  // 100ms delay between each
  .attr("r", 10);
```

## Event Handling and Interactivity

### Mouse Events

```javascript
selection
  .on("click", function(event, d) {
    console.log("Clicked:", d);
    console.log("Element:", this);
    console.log("Event:", event);
  })
  .on("mouseover", function(event, d) {
    d3.select(this)
      .transition()
      .attr("r", 15);
  })
  .on("mouseout", function(event, d) {
    d3.select(this)
      .transition()
      .attr("r", 10);
  })
  .on("mousemove", function(event, d) {
    const [x, y] = d3.pointer(event);
    console.log(`Mouse at: ${x}, ${y}`);
  });
```

### Drag Behavior

```javascript
const drag = d3.drag()
  .on("start", function(event, d) {
    d3.select(this).raise().attr("stroke", "black");
  })
  .on("drag", function(event, d) {
    d3.select(this)
      .attr("cx", event.x)
      .attr("cy", event.y);
  })
  .on("end", function(event, d) {
    d3.select(this).attr("stroke", null);
  });

circles.call(drag);
```

### Zoom Behavior

```javascript
const zoom = d3.zoom()
  .scaleExtent([0.5, 10])  // Min/max zoom
  .on("zoom", function(event) {
    svg.attr("transform", event.transform);
  });

svg.call(zoom);

// Programmatic zoom
svg.transition()
  .duration(750)
  .call(zoom.scaleTo, 2); // Zoom to 2x
```

### Brush Selection

```javascript
const brush = d3.brush()
  .extent([[0, 0], [width, height]])
  .on("start brush end", function(event) {
    if (event.selection) {
      const [[x0, y0], [x1, y1]] = event.selection;
      console.log(`Selected area: ${x0},${y0} to ${x1},${y1}`);
    }
  });

svg.append("g")
  .attr("class", "brush")
  .call(brush);
```
