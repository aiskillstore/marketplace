# Common Pitfalls and Solutions

## 1. Data Binding Confusion

**Problem:** Elements not updating correctly

### Wrong Approach

```javascript
// WRONG: No key function
svg.selectAll("circle")
  .data(newData)
  .attr("cx", d => xScale(d.value));
```

### Correct Approach

```javascript
// CORRECT: Handle all cases
const circles = svg.selectAll("circle")
  .data(newData, d => d.id); // Key function!

circles.enter()
  .append("circle")
  .attr("r", 5)
  .merge(circles)
  .attr("cx", d => xScale(d.value));

circles.exit().remove();
```

## 2. Scale Domain/Range Issues

**Problem:** Y-axis starts at wrong value

### Wrong Approach

```javascript
// WRONG: Doesn't start at 0
yScale.domain(d3.extent(data, d => d.value))

// WRONG: Y-axis inverted
yScale.range([0, height])
```

### Correct Approach

```javascript
// CORRECT: Start at 0 for bar charts
yScale.domain([0, d3.max(data, d => d.value)])

// CORRECT: SVG coordinates are top-down
yScale.range([height, 0])
```

## 3. SVG vs Canvas Performance

**Rule of Thumb:**
- < 1,000 elements: Use SVG (easier, more features)
- 1,000 - 10,000: Consider Canvas
- > 10,000: Use Canvas or WebGL

## 4. Animation Performance

**Problem:** Transitions are too fast or feel jerky

### Wrong Approach

```javascript
// WRONG: Too fast
circles.transition()
  .duration(50)
  .attr("cx", d => xScale(d.value));
```

### Correct Approach

```javascript
// CORRECT: Appropriate duration and easing
circles.transition()
  .duration(300)
  .ease(d3.easeCubicOut)
  .attr("cx", d => xScale(d.value));
```

## 5. Missing Margin Convention

**Problem:** Chart elements cut off at edges

### Wrong Approach

```javascript
// WRONG: No margins
const svg = d3.select("#chart")
  .append("svg")
  .attr("width", 800)
  .attr("height", 600);
```

### Correct Approach

```javascript
// CORRECT: Use margin convention
const margin = {top: 20, right: 30, bottom: 40, left: 50};
const width = 800 - margin.left - margin.right;
const height = 600 - margin.top - margin.bottom;

const svg = d3.select("#chart")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", `translate(${margin.left},${margin.top})`);
```

## 6. Forgetting to Handle Updates

**Problem:** Adding new data doesn't update existing elements

### Wrong Approach

```javascript
// WRONG: Only handles enter
svg.selectAll("circle")
  .data(data)
  .enter()
  .append("circle")
  .attr("r", 5);
```

### Correct Approach

```javascript
// CORRECT: Handle enter, update, and exit
const circles = svg.selectAll("circle")
  .data(data, d => d.id);

// Enter
circles.enter()
  .append("circle")
  .attr("r", 5)
  .merge(circles) // Merge with existing
  .attr("cx", d => xScale(d.x))
  .attr("cy", d => yScale(d.y));

// Exit
circles.exit().remove();
```

## 7. Not Using Key Functions

**Problem:** Incorrect element-to-data matching during updates

### Wrong Approach

```javascript
// WRONG: No key function
.data(newData)
```

### Correct Approach

```javascript
// CORRECT: Use unique key
.data(newData, d => d.id)
```

## 8. Incorrect This Context

**Problem:** Arrow functions don't preserve element context

### Wrong Approach

```javascript
// WRONG: Arrow function loses 'this'
circles.on("click", (event, d) => {
  d3.select(this).attr("fill", "red"); // 'this' is undefined!
});
```

### Correct Approach

```javascript
// CORRECT: Use traditional function
circles.on("click", function(event, d) {
  d3.select(this).attr("fill", "red"); // 'this' is the element
});
```

## 9. Forgetting Nice() on Scales

**Problem:** Axis values end at awkward numbers

### Wrong Approach

```javascript
// WRONG: Domain ends at exact data maximum
yScale.domain([0, d3.max(data, d => d.value)])
```

### Correct Approach

```javascript
// CORRECT: Use nice() for rounded axis values
yScale.domain([0, d3.max(data, d => d.value)])
  .nice()
```

## 10. Not Handling Async Data Loading

**Problem:** Trying to use data before it's loaded

### Wrong Approach

```javascript
// WRONG: Data isn't loaded yet
const data = d3.csv("data.csv");
createChart(data); // undefined!
```

### Correct Approach

```javascript
// CORRECT: Use promises
d3.csv("data.csv").then(data => {
  createChart(data);
});
```
