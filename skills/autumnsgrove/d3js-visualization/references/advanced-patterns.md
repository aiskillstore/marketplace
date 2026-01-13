# Advanced Patterns and Techniques

## Reusable Chart Pattern

Create modular, configurable chart components:

```javascript
function lineChart() {
  // Configuration variables
  let width = 800;
  let height = 400;
  let margin = {top: 20, right: 30, bottom: 40, left: 50};
  let xValue = d => d.date;
  let yValue = d => d.value;
  let lineColor = "steelblue";

  function chart(selection) {
    selection.each(function(data) {
      // Calculate inner dimensions
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Update scales
      const xScale = d3.scaleTime()
        .domain(d3.extent(data, xValue))
        .range([0, innerWidth]);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, yValue)])
        .range([innerHeight, 0]);

      // Select or create SVG
      const svg = d3.select(this)
        .selectAll("svg")
        .data([null]);

      const svgEnter = svg.enter()
        .append("svg");

      const g = svgEnter.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Axes
      g.append("g").attr("class", "x-axis")
        .attr("transform", `translate(0,${innerHeight})`);
      g.append("g").attr("class", "y-axis");
      g.append("path").attr("class", "line");

      // Update
      const svgUpdate = svg.merge(svgEnter)
        .attr("width", width)
        .attr("height", height);

      const gUpdate = svgUpdate.select("g");

      gUpdate.select(".x-axis").call(d3.axisBottom(xScale));
      gUpdate.select(".y-axis").call(d3.axisLeft(yScale));

      const line = d3.line()
        .x(d => xScale(xValue(d)))
        .y(d => yScale(yValue(d)))
        .curve(d3.curveMonotoneX);

      gUpdate.select(".line")
        .datum(data)
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", lineColor)
        .attr("stroke-width", 2);
    });
  }

  // Getter/setter methods
  chart.width = function(value) {
    if (!arguments.length) return width;
    width = value;
    return chart;
  };

  chart.height = function(value) {
    if (!arguments.length) return height;
    height = value;
    return chart;
  };

  chart.lineColor = function(value) {
    if (!arguments.length) return lineColor;
    lineColor = value;
    return chart;
  };

  return chart;
}

// Usage
const myChart = lineChart()
  .width(600)
  .height(300)
  .lineColor("steelblue");

d3.select("#chart")
  .datum(data)
  .call(myChart);
```

## Performance Optimization

### For Large Datasets (>1000 points)

#### Use Canvas Instead of SVG

```javascript
const canvas = d3.select("#chart")
  .append("canvas")
  .attr("width", width)
  .attr("height", height);

const context = canvas.node().getContext("2d");

// Draw with canvas API
data.forEach(d => {
  context.beginPath();
  context.arc(xScale(d.x), yScale(d.y), 3, 0, 2 * Math.PI);
  context.fillStyle = "steelblue";
  context.fill();
});
```

#### Aggregate Data

```javascript
// Bin data for histograms
const bins = d3.bin()
  .domain(xScale.domain())
  .thresholds(20)(data);

// Sample data
const sampledData = data.filter((d, i) => i % 10 === 0);
```

### Performance Rule of Thumb

- < 1,000 elements: Use SVG (easier, more features)
- 1,000 - 10,000: Consider Canvas
- > 10,000: Use Canvas or WebGL

## Responsive Design Patterns

### Container Query

```javascript
function createResponsiveChart() {
  const container = document.getElementById("chart");
  const width = container.clientWidth;

  // Adjust based on width
  const margin = width < 600
    ? {top: 10, right: 10, bottom: 30, left: 40}
    : {top: 20, right: 30, bottom: 40, left: 60};

  const height = width < 600 ? 300 : 500;

  // Adjust tick counts
  const xTicks = width < 600 ? 5 : 10;
  const yTicks = width < 600 ? 5 : 10;

  // ... rest of chart
}
```

### ViewBox Scaling

```javascript
// Use fixed internal dimensions
const width = 800;
const height = 600;

const svg = d3.select("#chart")
  .append("svg")
  .attr("viewBox", `0 0 ${width} ${height}`)
  .attr("preserveAspectRatio", "xMidYMid meet")
  .style("width", "100%")
  .style("height", "auto");
```

### Resize Handler with Debouncing

```javascript
function createChart() {
  // Get container width
  const container = d3.select("#chart");
  const containerWidth = container.node().getBoundingClientRect().width;

  // Calculate dimensions
  const margin = {top: 20, right: 30, bottom: 40, left: 50};
  const width = containerWidth - margin.left - margin.right;
  const height = Math.min(width * 0.6, 500); // Aspect ratio

  // Clear previous chart
  container.selectAll("*").remove();

  // Create SVG
  const svg = container
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // ... rest of chart code
}

// Initial render
createChart();

// Re-render on resize with debouncing
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(createChart, 250);
});
```

## Accessibility

### ARIA Labels

```javascript
svg
  .attr("role", "img")
  .attr("aria-label", "Line chart showing sales over time");

// Add description
svg.append("desc")
  .text("A line chart displaying monthly sales from January to December 2023. Sales increased from $100k to $180k over the year.");
```

### Keyboard Navigation

```javascript
circles
  .attr("tabindex", 0)
  .attr("role", "button")
  .attr("aria-label", d => `Data point: ${d.name}, value: ${d.value}`)
  .on("keydown", function(event, d) {
    if (event.key === "Enter" || event.key === " ") {
      // Trigger interaction
      handleClick(d);
    }
  });
```

## Export to PNG/SVG

```javascript
// Export as SVG
function exportSVG() {
  const svg = document.querySelector("svg");
  const serializer = new XMLSerializer();
  const source = serializer.serializeToString(svg);

  const blob = new Blob([source], {type: "image/svg+xml"});
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "chart.svg";
  a.click();

  URL.revokeObjectURL(url);
}
```
