# Integration Patterns

## With React

```javascript
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function LineChart({ data, width, height }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous

    const margin = {top: 20, right: 30, bottom: 40, left: 50};
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([innerHeight, 0]);

    const line = d3.line()
      .x(d => xScale(d.date))
      .y(d => yScale(d.value));

    g.append("path")
      .datum(data)
      .attr("d", line)
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 2);

    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale));

    g.append("g")
      .call(d3.axisLeft(yScale));

  }, [data, width, height]);

  return <svg ref={svgRef} width={width} height={height} />;
}

export default LineChart;
```

## With Vue

```javascript
<template>
  <svg ref="chart" :width="width" :height="height"></svg>
</template>

<script>
import * as d3 from 'd3';

export default {
  props: {
    data: Array,
    width: Number,
    height: Number
  },
  watch: {
    data() {
      this.renderChart();
    }
  },
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      if (!this.data || !this.data.length) return;

      const svg = d3.select(this.$refs.chart);
      svg.selectAll("*").remove();

      // Chart implementation...
    }
  }
};
</script>
```

## With Angular

```typescript
import { Component, ElementRef, Input, OnChanges, ViewChild } from '@angular/core';
import * as d3 from 'd3';

@Component({
  selector: 'app-line-chart',
  template: '<svg #chart></svg>'
})
export class LineChartComponent implements OnChanges {
  @ViewChild('chart', { static: true }) chartRef: ElementRef;
  @Input() data: any[];
  @Input() width: number;
  @Input() height: number;

  ngOnChanges() {
    this.renderChart();
  }

  renderChart() {
    if (!this.data || !this.data.length) return;

    const svg = d3.select(this.chartRef.nativeElement);
    svg.selectAll("*").remove();

    // Chart implementation...
  }
}
```

## With Svelte

```svelte
<script>
  import { onMount, afterUpdate } from 'svelte';
  import * as d3 from 'd3';

  export let data;
  export let width = 800;
  export let height = 400;

  let chartElement;

  function renderChart() {
    if (!data || !data.length || !chartElement) return;

    const svg = d3.select(chartElement);
    svg.selectAll("*").remove();

    // Chart implementation...
  }

  onMount(renderChart);
  afterUpdate(renderChart);
</script>

<svg bind:this={chartElement} {width} {height}></svg>
```

## Best Practices for Framework Integration

### 1. Use refs, not direct DOM selection

```javascript
// GOOD: Use ref
const svg = d3.select(svgRef.current);

// BAD: Direct DOM query (may not work in virtual DOM)
const svg = d3.select("#chart");
```

### 2. Clear previous content on updates

```javascript
svg.selectAll("*").remove(); // Clear before re-rendering
```

### 3. Handle unmounting/cleanup

```javascript
// React example
useEffect(() => {
  renderChart();

  return () => {
    // Cleanup if needed
    svg.selectAll("*").remove();
  };
}, [data]);
```

### 4. Separate D3 manipulation from framework

```javascript
// Keep D3 code in separate functions
function createChart(element, data, options) {
  // Pure D3 implementation
}

// Call from component
useEffect(() => {
  createChart(svgRef.current, data, { width, height });
}, [data, width, height]);
```
