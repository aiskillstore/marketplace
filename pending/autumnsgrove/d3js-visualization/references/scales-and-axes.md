# Scales and Axes Reference

## Understanding Scales

Scales map data values (domain) to visual values (range).

## Continuous Scales

### Linear Scale

```javascript
const xScale = d3.scaleLinear()
  .domain([0, 100])        // Data range
  .range([0, 500]);        // Pixel range
xScale(50); // Returns 250
```

### Log Scale

Use for exponential data:

```javascript
const logScale = d3.scaleLog()
  .domain([1, 1000])
  .range([0, 500]);
```

### Power Scale

```javascript
const powScale = d3.scalePow()
  .exponent(2)
  .domain([0, 100])
  .range([0, 500]);
```

### Square Root Scale

Common for area mapping:

```javascript
const sqrtScale = d3.scaleSqrt()
  .domain([0, 100])
  .range([0, 500]);
```

### Time Scale

```javascript
const timeScale = d3.scaleTime()
  .domain([new Date(2020, 0, 1), new Date(2021, 0, 1)])
  .range([0, 500]);
```

## Discrete Scales

### Ordinal Scale

For categorical data:

```javascript
const colorScale = d3.scaleOrdinal()
  .domain(["A", "B", "C"])
  .range(["red", "green", "blue"]);
```

### Band Scale

Perfect for bar charts:

```javascript
const xScale = d3.scaleBand()
  .domain(["Mon", "Tue", "Wed", "Thu", "Fri"])
  .range([0, 500])
  .padding(0.1);

xScale("Mon"); // Returns x position
xScale.bandwidth(); // Returns bar width
```

### Point Scale

For scatter plots:

```javascript
const pointScale = d3.scalePoint()
  .domain(["A", "B", "C"])
  .range([0, 500])
  .padding(0.5);
```

## Color Scales

### Sequential Scale

For continuous data:

```javascript
const colorScale = d3.scaleSequential()
  .domain([0, 100])
  .interpolator(d3.interpolateBlues);
```

### Diverging Scale

For data with meaningful center:

```javascript
const divergingScale = d3.scaleDiverging()
  .domain([0, 50, 100])
  .interpolator(d3.interpolateRdYlGn);
```

### Quantize Scale

Discrete bins:

```javascript
const quantizeScale = d3.scaleQuantize()
  .domain([0, 100])
  .range(["low", "medium", "high"]);
```

### Threshold Scale

Custom breakpoints:

```javascript
const thresholdScale = d3.scaleThreshold()
  .domain([10, 50, 90])
  .range(["#eee", "#ccc", "#999", "#666"]);
```

## Creating Axes

### Basic Axis Setup

```javascript
// Define scales
const xScale = d3.scaleLinear()
  .domain([0, 100])
  .range([0, 500]);

const yScale = d3.scaleLinear()
  .domain([0, 50])
  .range([400, 0]); // Inverted for bottom-up

// Create axis generators
const xAxis = d3.axisBottom(xScale)
  .ticks(10)
  .tickFormat(d => `$${d}`);

const yAxis = d3.axisLeft(yScale)
  .ticks(5);

// Append axes to SVG
svg.append("g")
  .attr("class", "x-axis")
  .attr("transform", `translate(0, ${height})`)
  .call(xAxis);

svg.append("g")
  .attr("class", "y-axis")
  .call(yAxis);
```

### Axis Customization

```javascript
const axis = d3.axisBottom(xScale)
  .ticks(10)                    // Number of ticks
  .tickSize(6)                  // Tick length
  .tickPadding(3)               // Space between tick and label
  .tickFormat(d3.format(".2f")) // Format numbers
  .tickValues([0, 25, 50, 75, 100]); // Specific tick values
```

## Color Palette Selection

### Sequential Palettes (For Continuous Data)

```javascript
// Single hue (0 to high)
d3.interpolateBlues
d3.interpolateGreens
d3.interpolateReds

// Multi-hue
d3.interpolateViridis  // Purple to yellow (colorblind-safe)
d3.interpolatePlasma   // Purple to orange
d3.interpolateInferno  // Black to yellow
d3.interpolateTurbo    // Blue to red (high contrast)
```

### Categorical Palettes (For Discrete Groups)

```javascript
// Qualitative schemes
d3.schemeCategory10   // 10 colors
d3.schemeAccent       // 8 colors
d3.schemeSet1         // 9 colors
d3.schemeSet2         // 8 colors (pastels)
d3.schemeSet3         // 12 colors

const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
```
