/**
 * D3.js Chart Templates
 * Reusable chart components following the reusable chart pattern
 */

/**
 * Reusable Line Chart
 *
 * Usage:
 *   const chart = lineChart()
 *     .width(800)
 *     .height(400)
 *     .xValue(d => d.date)
 *     .yValue(d => d.value);
 *
 *   d3.select('#chart')
 *     .datum(data)
 *     .call(chart);
 */
function lineChart() {
  // Default configuration
  let width = 600;
  let height = 400;
  let margin = { top: 20, right: 30, bottom: 40, left: 50 };
  let xValue = d => d.x;
  let yValue = d => d.y;
  let xScale = d3.scaleLinear();
  let yScale = d3.scaleLinear();
  let curve = d3.curveLinear;
  let color = 'steelblue';
  let strokeWidth = 2;
  let showPoints = false;
  let pointRadius = 4;
  let animate = true;
  let animationDuration = 1000;
  let xAxisLabel = '';
  let yAxisLabel = '';
  let xAxisFormat = null;
  let yAxisFormat = null;
  let yDomainPadding = 0.1;

  function chart(selection) {
    selection.each(function(data) {
      // Calculate inner dimensions
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Update scales
      xScale
        .domain(d3.extent(data, xValue))
        .range([0, innerWidth]);

      const yExtent = d3.extent(data, yValue);
      const yPadding = (yExtent[1] - yExtent[0]) * yDomainPadding;
      yScale
        .domain([yExtent[0] - yPadding, yExtent[1] + yPadding])
        .range([innerHeight, 0]);

      // Create or update SVG
      let svg = d3.select(this).selectAll('svg').data([null]);
      const svgEnter = svg.enter().append('svg');
      svg = svg.merge(svgEnter)
        .attr('width', width)
        .attr('height', height);

      // Create main group
      let g = svg.selectAll('.chart-group').data([null]);
      const gEnter = g.enter().append('g').attr('class', 'chart-group');
      g = g.merge(gEnter)
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

      // X axis
      const xAxis = d3.axisBottom(xScale);
      if (xAxisFormat) xAxis.tickFormat(xAxisFormat);

      let xAxisG = g.selectAll('.x-axis').data([null]);
      const xAxisGEnter = xAxisG.enter().append('g').attr('class', 'x-axis');
      xAxisG = xAxisG.merge(xAxisGEnter)
        .attr('transform', `translate(0, ${innerHeight})`)
        .call(xAxis);

      // X axis label
      if (xAxisLabel) {
        let xLabel = xAxisG.selectAll('.x-label').data([null]);
        xLabel.enter()
          .append('text')
          .attr('class', 'x-label')
          .merge(xLabel)
          .attr('x', innerWidth / 2)
          .attr('y', 35)
          .attr('text-anchor', 'middle')
          .attr('fill', 'currentColor')
          .text(xAxisLabel);
      }

      // Y axis
      const yAxis = d3.axisLeft(yScale);
      if (yAxisFormat) yAxis.tickFormat(yAxisFormat);

      let yAxisG = g.selectAll('.y-axis').data([null]);
      const yAxisGEnter = yAxisG.enter().append('g').attr('class', 'y-axis');
      yAxisG = yAxisG.merge(yAxisGEnter).call(yAxis);

      // Y axis label
      if (yAxisLabel) {
        let yLabel = yAxisG.selectAll('.y-label').data([null]);
        yLabel.enter()
          .append('text')
          .attr('class', 'y-label')
          .merge(yLabel)
          .attr('transform', 'rotate(-90)')
          .attr('x', -innerHeight / 2)
          .attr('y', -40)
          .attr('text-anchor', 'middle')
          .attr('fill', 'currentColor')
          .text(yAxisLabel);
      }

      // Line generator
      const lineGenerator = d3.line()
        .x(d => xScale(xValue(d)))
        .y(d => yScale(yValue(d)))
        .curve(curve);

      // Draw line
      let path = g.selectAll('.line-path').data([data]);
      const pathEnter = path.enter()
        .append('path')
        .attr('class', 'line-path');

      path = path.merge(pathEnter)
        .attr('d', lineGenerator)
        .attr('fill', 'none')
        .attr('stroke', color)
        .attr('stroke-width', strokeWidth);

      // Animate line drawing
      if (animate && pathEnter.size() > 0) {
        const totalLength = path.node().getTotalLength();
        path
          .attr('stroke-dasharray', totalLength + ' ' + totalLength)
          .attr('stroke-dashoffset', totalLength)
          .transition()
          .duration(animationDuration)
          .ease(d3.easeLinear)
          .attr('stroke-dashoffset', 0);
      }

      // Draw points
      if (showPoints) {
        let points = g.selectAll('.line-point').data(data);
        const pointsEnter = points.enter()
          .append('circle')
          .attr('class', 'line-point')
          .attr('r', 0);

        points = points.merge(pointsEnter)
          .attr('cx', d => xScale(xValue(d)))
          .attr('cy', d => yScale(yValue(d)))
          .attr('fill', color);

        if (animate) {
          points.transition()
            .duration(300)
            .delay((d, i) => i * 50)
            .attr('r', pointRadius);
        } else {
          points.attr('r', pointRadius);
        }

        points.exit().remove();
      }
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

  chart.margin = function(value) {
    if (!arguments.length) return margin;
    margin = value;
    return chart;
  };

  chart.xValue = function(value) {
    if (!arguments.length) return xValue;
    xValue = value;
    return chart;
  };

  chart.yValue = function(value) {
    if (!arguments.length) return yValue;
    yValue = value;
    return chart;
  };

  chart.xScale = function(value) {
    if (!arguments.length) return xScale;
    xScale = value;
    return chart;
  };

  chart.yScale = function(value) {
    if (!arguments.length) return yScale;
    yScale = value;
    return chart;
  };

  chart.curve = function(value) {
    if (!arguments.length) return curve;
    curve = value;
    return chart;
  };

  chart.color = function(value) {
    if (!arguments.length) return color;
    color = value;
    return chart;
  };

  chart.strokeWidth = function(value) {
    if (!arguments.length) return strokeWidth;
    strokeWidth = value;
    return chart;
  };

  chart.showPoints = function(value) {
    if (!arguments.length) return showPoints;
    showPoints = value;
    return chart;
  };

  chart.pointRadius = function(value) {
    if (!arguments.length) return pointRadius;
    pointRadius = value;
    return chart;
  };

  chart.animate = function(value) {
    if (!arguments.length) return animate;
    animate = value;
    return chart;
  };

  chart.animationDuration = function(value) {
    if (!arguments.length) return animationDuration;
    animationDuration = value;
    return chart;
  };

  chart.xAxisLabel = function(value) {
    if (!arguments.length) return xAxisLabel;
    xAxisLabel = value;
    return chart;
  };

  chart.yAxisLabel = function(value) {
    if (!arguments.length) return yAxisLabel;
    yAxisLabel = value;
    return chart;
  };

  chart.xAxisFormat = function(value) {
    if (!arguments.length) return xAxisFormat;
    xAxisFormat = value;
    return chart;
  };

  chart.yAxisFormat = function(value) {
    if (!arguments.length) return yAxisFormat;
    yAxisFormat = value;
    return chart;
  };

  chart.yDomainPadding = function(value) {
    if (!arguments.length) return yDomainPadding;
    yDomainPadding = value;
    return chart;
  };

  return chart;
}

/**
 * Reusable Bar Chart
 *
 * Usage:
 *   const chart = barChart()
 *     .width(800)
 *     .height(400)
 *     .xValue(d => d.category)
 *     .yValue(d => d.value);
 *
 *   d3.select('#chart')
 *     .datum(data)
 *     .call(chart);
 */
function barChart() {
  // Default configuration
  let width = 600;
  let height = 400;
  let margin = { top: 20, right: 30, bottom: 40, left: 50 };
  let xValue = d => d.x;
  let yValue = d => d.y;
  let color = 'steelblue';
  let hoverColor = 'orange';
  let padding = 0.1;
  let animate = true;
  let animationDuration = 800;
  let animationDelay = 50;
  let xAxisLabel = '';
  let yAxisLabel = '';
  let yAxisFormat = null;
  let onClick = null;
  let onHover = null;

  function chart(selection) {
    selection.each(function(data) {
      // Calculate inner dimensions
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Scales
      const xScale = d3.scaleBand()
        .domain(data.map(xValue))
        .range([0, innerWidth])
        .padding(padding);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, yValue)])
        .nice()
        .range([innerHeight, 0]);

      // Create or update SVG
      let svg = d3.select(this).selectAll('svg').data([null]);
      const svgEnter = svg.enter().append('svg');
      svg = svg.merge(svgEnter)
        .attr('width', width)
        .attr('height', height);

      // Create main group
      let g = svg.selectAll('.chart-group').data([null]);
      const gEnter = g.enter().append('g').attr('class', 'chart-group');
      g = g.merge(gEnter)
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

      // X axis
      let xAxisG = g.selectAll('.x-axis').data([null]);
      const xAxisGEnter = xAxisG.enter().append('g').attr('class', 'x-axis');
      xAxisG = xAxisG.merge(xAxisGEnter)
        .attr('transform', `translate(0, ${innerHeight})`)
        .call(d3.axisBottom(xScale));

      // X axis label
      if (xAxisLabel) {
        let xLabel = xAxisG.selectAll('.x-label').data([null]);
        xLabel.enter()
          .append('text')
          .attr('class', 'x-label')
          .merge(xLabel)
          .attr('x', innerWidth / 2)
          .attr('y', 35)
          .attr('text-anchor', 'middle')
          .attr('fill', 'currentColor')
          .text(xAxisLabel);
      }

      // Y axis
      const yAxis = d3.axisLeft(yScale);
      if (yAxisFormat) yAxis.tickFormat(yAxisFormat);

      let yAxisG = g.selectAll('.y-axis').data([null]);
      const yAxisGEnter = yAxisG.enter().append('g').attr('class', 'y-axis');
      yAxisG = yAxisG.merge(yAxisGEnter).call(yAxis);

      // Y axis label
      if (yAxisLabel) {
        let yLabel = yAxisG.selectAll('.y-label').data([null]);
        yLabel.enter()
          .append('text')
          .attr('class', 'y-label')
          .merge(yLabel)
          .attr('transform', 'rotate(-90)')
          .attr('x', -innerHeight / 2)
          .attr('y', -40)
          .attr('text-anchor', 'middle')
          .attr('fill', 'currentColor')
          .text(yAxisLabel);
      }

      // Bars
      let bars = g.selectAll('.bar').data(data);
      const barsEnter = bars.enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => xScale(xValue(d)))
        .attr('width', xScale.bandwidth())
        .attr('y', innerHeight)
        .attr('height', 0)
        .attr('fill', color);

      bars = bars.merge(barsEnter);

      if (animate) {
        bars
          .transition()
          .duration(animationDuration)
          .delay((d, i) => i * animationDelay)
          .attr('x', d => xScale(xValue(d)))
          .attr('y', d => yScale(yValue(d)))
          .attr('width', xScale.bandwidth())
          .attr('height', d => innerHeight - yScale(yValue(d)));
      } else {
        bars
          .attr('x', d => xScale(xValue(d)))
          .attr('y', d => yScale(yValue(d)))
          .attr('width', xScale.bandwidth())
          .attr('height', d => innerHeight - yScale(yValue(d)));
      }

      // Interactions
      bars
        .on('mouseover', function(event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('fill', hoverColor);

          if (onHover) onHover(event, d);
        })
        .on('mouseout', function() {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('fill', color);
        })
        .on('click', function(event, d) {
          if (onClick) onClick(event, d);
        });

      bars.exit().remove();
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

  chart.margin = function(value) {
    if (!arguments.length) return margin;
    margin = value;
    return chart;
  };

  chart.xValue = function(value) {
    if (!arguments.length) return xValue;
    xValue = value;
    return chart;
  };

  chart.yValue = function(value) {
    if (!arguments.length) return yValue;
    yValue = value;
    return chart;
  };

  chart.color = function(value) {
    if (!arguments.length) return color;
    color = value;
    return chart;
  };

  chart.hoverColor = function(value) {
    if (!arguments.length) return hoverColor;
    hoverColor = value;
    return chart;
  };

  chart.padding = function(value) {
    if (!arguments.length) return padding;
    padding = value;
    return chart;
  };

  chart.animate = function(value) {
    if (!arguments.length) return animate;
    animate = value;
    return chart;
  };

  chart.animationDuration = function(value) {
    if (!arguments.length) return animationDuration;
    animationDuration = value;
    return chart;
  };

  chart.animationDelay = function(value) {
    if (!arguments.length) return animationDelay;
    animationDelay = value;
    return chart;
  };

  chart.xAxisLabel = function(value) {
    if (!arguments.length) return xAxisLabel;
    xAxisLabel = value;
    return chart;
  };

  chart.yAxisLabel = function(value) {
    if (!arguments.length) return yAxisLabel;
    yAxisLabel = value;
    return chart;
  };

  chart.yAxisFormat = function(value) {
    if (!arguments.length) return yAxisFormat;
    yAxisFormat = value;
    return chart;
  };

  chart.onClick = function(value) {
    if (!arguments.length) return onClick;
    onClick = value;
    return chart;
  };

  chart.onHover = function(value) {
    if (!arguments.length) return onHover;
    onHover = value;
    return chart;
  };

  return chart;
}

/**
 * Reusable Scatter Plot
 *
 * Usage:
 *   const chart = scatterPlot()
 *     .width(800)
 *     .height(400)
 *     .xValue(d => d.x)
 *     .yValue(d => d.y);
 *
 *   d3.select('#chart')
 *     .datum(data)
 *     .call(chart);
 */
function scatterPlot() {
  // Default configuration
  let width = 600;
  let height = 400;
  let margin = { top: 20, right: 30, bottom: 40, left: 50 };
  let xValue = d => d.x;
  let yValue = d => d.y;
  let radiusValue = () => 5;
  let colorValue = () => 'steelblue';
  let xScale = d3.scaleLinear();
  let yScale = d3.scaleLinear();
  let radiusScale = null;
  let colorScale = null;
  let opacity = 0.7;
  let hoverOpacity = 1;
  let animate = true;
  let animationDuration = 800;
  let xAxisLabel = '';
  let yAxisLabel = '';
  let xAxisFormat = null;
  let yAxisFormat = null;
  let onClick = null;
  let onHover = null;

  function chart(selection) {
    selection.each(function(data) {
      // Calculate inner dimensions
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Update scales
      xScale
        .domain(d3.extent(data, xValue))
        .nice()
        .range([0, innerWidth]);

      yScale
        .domain(d3.extent(data, yValue))
        .nice()
        .range([innerHeight, 0]);

      // Create or update SVG
      let svg = d3.select(this).selectAll('svg').data([null]);
      const svgEnter = svg.enter().append('svg');
      svg = svg.merge(svgEnter)
        .attr('width', width)
        .attr('height', height);

      // Create main group
      let g = svg.selectAll('.chart-group').data([null]);
      const gEnter = g.enter().append('g').attr('class', 'chart-group');
      g = g.merge(gEnter)
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

      // X axis
      const xAxis = d3.axisBottom(xScale);
      if (xAxisFormat) xAxis.tickFormat(xAxisFormat);

      let xAxisG = g.selectAll('.x-axis').data([null]);
      const xAxisGEnter = xAxisG.enter().append('g').attr('class', 'x-axis');
      xAxisG = xAxisG.merge(xAxisGEnter)
        .attr('transform', `translate(0, ${innerHeight})`)
        .call(xAxis);

      // X axis label
      if (xAxisLabel) {
        let xLabel = xAxisG.selectAll('.x-label').data([null]);
        xLabel.enter()
          .append('text')
          .attr('class', 'x-label')
          .merge(xLabel)
          .attr('x', innerWidth / 2)
          .attr('y', 35)
          .attr('text-anchor', 'middle')
          .attr('fill', 'currentColor')
          .text(xAxisLabel);
      }

      // Y axis
      const yAxis = d3.axisLeft(yScale);
      if (yAxisFormat) yAxis.tickFormat(yAxisFormat);

      let yAxisG = g.selectAll('.y-axis').data([null]);
      const yAxisGEnter = yAxisG.enter().append('g').attr('class', 'y-axis');
      yAxisG = yAxisG.merge(yAxisGEnter).call(yAxis);

      // Y axis label
      if (yAxisLabel) {
        let yLabel = yAxisG.selectAll('.y-label').data([null]);
        yLabel.enter()
          .append('text')
          .attr('class', 'y-label')
          .merge(yLabel)
          .attr('transform', 'rotate(-90)')
          .attr('x', -innerHeight / 2)
          .attr('y', -40)
          .attr('text-anchor', 'middle')
          .attr('fill', 'currentColor')
          .text(yAxisLabel);
      }

      // Points
      let points = g.selectAll('.point').data(data);
      const pointsEnter = points.enter()
        .append('circle')
        .attr('class', 'point')
        .attr('cx', d => xScale(xValue(d)))
        .attr('cy', d => yScale(yValue(d)))
        .attr('r', 0)
        .attr('opacity', opacity);

      points = points.merge(pointsEnter);

      const getRadius = d => {
        if (radiusScale) return radiusScale(radiusValue(d));
        return radiusValue(d);
      };

      const getColor = d => {
        if (colorScale) return colorScale(colorValue(d));
        return colorValue(d);
      };

      if (animate) {
        points
          .transition()
          .duration(animationDuration)
          .delay((d, i) => i * 10)
          .attr('cx', d => xScale(xValue(d)))
          .attr('cy', d => yScale(yValue(d)))
          .attr('r', getRadius)
          .attr('fill', getColor);
      } else {
        points
          .attr('cx', d => xScale(xValue(d)))
          .attr('cy', d => yScale(yValue(d)))
          .attr('r', getRadius)
          .attr('fill', getColor);
      }

      // Interactions
      points
        .on('mouseover', function(event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('opacity', hoverOpacity)
            .attr('r', d => getRadius(d) * 1.5);

          if (onHover) onHover(event, d);
        })
        .on('mouseout', function(event, d) {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('opacity', opacity)
            .attr('r', getRadius);
        })
        .on('click', function(event, d) {
          if (onClick) onClick(event, d);
        });

      points.exit().remove();
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

  chart.margin = function(value) {
    if (!arguments.length) return margin;
    margin = value;
    return chart;
  };

  chart.xValue = function(value) {
    if (!arguments.length) return xValue;
    xValue = value;
    return chart;
  };

  chart.yValue = function(value) {
    if (!arguments.length) return yValue;
    yValue = value;
    return chart;
  };

  chart.radiusValue = function(value) {
    if (!arguments.length) return radiusValue;
    radiusValue = value;
    return chart;
  };

  chart.colorValue = function(value) {
    if (!arguments.length) return colorValue;
    colorValue = value;
    return chart;
  };

  chart.xScale = function(value) {
    if (!arguments.length) return xScale;
    xScale = value;
    return chart;
  };

  chart.yScale = function(value) {
    if (!arguments.length) return yScale;
    yScale = value;
    return chart;
  };

  chart.radiusScale = function(value) {
    if (!arguments.length) return radiusScale;
    radiusScale = value;
    return chart;
  };

  chart.colorScale = function(value) {
    if (!arguments.length) return colorScale;
    colorScale = value;
    return chart;
  };

  chart.opacity = function(value) {
    if (!arguments.length) return opacity;
    opacity = value;
    return chart;
  };

  chart.hoverOpacity = function(value) {
    if (!arguments.length) return hoverOpacity;
    hoverOpacity = value;
    return chart;
  };

  chart.animate = function(value) {
    if (!arguments.length) return animate;
    animate = value;
    return chart;
  };

  chart.animationDuration = function(value) {
    if (!arguments.length) return animationDuration;
    animationDuration = value;
    return chart;
  };

  chart.xAxisLabel = function(value) {
    if (!arguments.length) return xAxisLabel;
    xAxisLabel = value;
    return chart;
  };

  chart.yAxisLabel = function(value) {
    if (!arguments.length) return yAxisLabel;
    yAxisLabel = value;
    return chart;
  };

  chart.xAxisFormat = function(value) {
    if (!arguments.length) return xAxisFormat;
    xAxisFormat = value;
    return chart;
  };

  chart.yAxisFormat = function(value) {
    if (!arguments.length) return yAxisFormat;
    yAxisFormat = value;
    return chart;
  };

  chart.onClick = function(value) {
    if (!arguments.length) return onClick;
    onClick = value;
    return chart;
  };

  chart.onHover = function(value) {
    if (!arguments.length) return onHover;
    onHover = value;
    return chart;
  };

  return chart;
}

/**
 * Create a simple tooltip helper
 *
 * Usage:
 *   const tooltip = createTooltip();
 *
 *   circles.on('mouseover', (event, d) => {
 *     tooltip.show(event, `Value: ${d.value}`);
 *   }).on('mouseout', () => {
 *     tooltip.hide();
 *   });
 */
function createTooltip(options = {}) {
  const defaults = {
    className: 'd3-tooltip',
    offsetX: 10,
    offsetY: -28,
    style: {
      position: 'absolute',
      display: 'none',
      padding: '10px',
      background: 'white',
      border: '1px solid #ccc',
      borderRadius: '4px',
      pointerEvents: 'none',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      fontSize: '12px',
      zIndex: '1000'
    }
  };

  const config = { ...defaults, ...options };

  // Create tooltip div
  const tooltip = d3.select('body')
    .append('div')
    .attr('class', config.className);

  // Apply styles
  Object.entries(config.style).forEach(([key, value]) => {
    tooltip.style(key, value);
  });

  return {
    show(event, content) {
      tooltip
        .style('display', 'block')
        .html(content)
        .style('left', (event.pageX + config.offsetX) + 'px')
        .style('top', (event.pageY + config.offsetY) + 'px');
    },

    hide() {
      tooltip.style('display', 'none');
    },

    update(content) {
      tooltip.html(content);
    },

    move(event) {
      tooltip
        .style('left', (event.pageX + config.offsetX) + 'px')
        .style('top', (event.pageY + config.offsetY) + 'px');
    },

    remove() {
      tooltip.remove();
    }
  };
}

/**
 * Create a legend helper
 *
 * Usage:
 *   const legend = createLegend(svg, colorScale, {
 *     x: 700,
 *     y: 20,
 *     title: 'Categories'
 *   });
 */
function createLegend(svg, scale, options = {}) {
  const defaults = {
    x: 0,
    y: 0,
    title: '',
    itemHeight: 20,
    itemSpacing: 5,
    swatchSize: 15,
    swatchPadding: 5,
    fontSize: 12,
    titleFontSize: 14,
    orientation: 'vertical' // or 'horizontal'
  };

  const config = { ...defaults, ...options };

  const legendGroup = svg.append('g')
    .attr('class', 'legend')
    .attr('transform', `translate(${config.x}, ${config.y})`);

  // Title
  if (config.title) {
    legendGroup.append('text')
      .attr('class', 'legend-title')
      .attr('y', -10)
      .style('font-size', `${config.titleFontSize}px`)
      .style('font-weight', 'bold')
      .text(config.title);
  }

  const domain = scale.domain();
  const items = legendGroup.selectAll('.legend-item')
    .data(domain)
    .enter()
    .append('g')
    .attr('class', 'legend-item');

  if (config.orientation === 'vertical') {
    items.attr('transform', (d, i) =>
      `translate(0, ${i * (config.itemHeight + config.itemSpacing)})`
    );
  } else {
    items.attr('transform', (d, i) =>
      `translate(${i * 100}, 0)`
    );
  }

  // Swatches
  items.append('rect')
    .attr('width', config.swatchSize)
    .attr('height', config.swatchSize)
    .attr('fill', d => scale(d));

  // Labels
  items.append('text')
    .attr('x', config.swatchSize + config.swatchPadding)
    .attr('y', config.swatchSize / 2)
    .attr('dy', '0.35em')
    .style('font-size', `${config.fontSize}px`)
    .text(d => d);

  return legendGroup;
}
