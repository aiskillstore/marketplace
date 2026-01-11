/**
 * D3.js Data Transformation Utilities
 * Helper functions for common data manipulation tasks
 */

/**
 * Parse CSV data with type conversion
 *
 * @param {string} csvPath - Path to CSV file
 * @param {object} typeMap - Object mapping column names to type converters
 * @returns {Promise<Array>} Parsed data
 *
 * Usage:
 *   const data = await parseCSV('data.csv', {
 *     date: d3.timeParse('%Y-%m-%d'),
 *     value: d => +d,
 *     active: d => d === 'true'
 *   });
 */
async function parseCSV(csvPath, typeMap = {}) {
  return d3.csv(csvPath, row => {
    const parsed = {};
    for (const [key, value] of Object.entries(row)) {
      if (typeMap[key]) {
        parsed[key] = typeMap[key](value);
      } else {
        parsed[key] = value;
      }
    }
    return parsed;
  });
}

/**
 * Group data by one or more keys and aggregate
 *
 * @param {Array} data - Input data
 * @param {Function|Array} keyFn - Key function(s) for grouping
 * @param {Object} aggregations - Aggregation functions
 * @returns {Array} Aggregated data
 *
 * Usage:
 *   const grouped = groupAndAggregate(data,
 *     d => d.category,
 *     {
 *       total: arr => d3.sum(arr, d => d.value),
 *       average: arr => d3.mean(arr, d => d.value),
 *       count: arr => arr.length
 *     }
 *   );
 */
function groupAndAggregate(data, keyFn, aggregations) {
  const grouped = d3.group(data, keyFn);

  return Array.from(grouped, ([key, values]) => {
    const result = { key };
    for (const [name, fn] of Object.entries(aggregations)) {
      result[name] = fn(values);
    }
    return result;
  });
}

/**
 * Rollup data with multiple aggregations
 *
 * @param {Array} data - Input data
 * @param {Function} keyFn - Key function for grouping
 * @returns {Array} Rolled up data
 *
 * Usage:
 *   const stats = rollupStats(data, d => d.category);
 *   // Returns: [{key: 'A', sum: 100, mean: 25, min: 10, max: 40, count: 4}, ...]
 */
function rollupStats(data, keyFn) {
  return groupAndAggregate(data, keyFn, {
    sum: arr => d3.sum(arr, d => d.value || 0),
    mean: arr => d3.mean(arr, d => d.value || 0),
    median: arr => d3.median(arr, d => d.value || 0),
    min: arr => d3.min(arr, d => d.value || 0),
    max: arr => d3.max(arr, d => d.value || 0),
    count: arr => arr.length
  });
}

/**
 * Convert flat data to hierarchical structure
 *
 * @param {Array} data - Flat data with parent references
 * @param {Function} idFn - Function to get node ID
 * @param {Function} parentIdFn - Function to get parent ID
 * @returns {Object} Hierarchical root node
 *
 * Usage:
 *   const hierarchy = flatToHierarchy(
 *     data,
 *     d => d.id,
 *     d => d.parentId
 *   );
 */
function flatToHierarchy(data, idFn, parentIdFn) {
  const stratify = d3.stratify()
    .id(idFn)
    .parentId(parentIdFn);

  return stratify(data);
}

/**
 * Normalize values to 0-1 range
 *
 * @param {Array} data - Input data
 * @param {Function} valueFn - Function to get value
 * @returns {Array} Data with normalized values
 *
 * Usage:
 *   const normalized = normalizeMinMax(data, d => d.value);
 */
function normalizeMinMax(data, valueFn) {
  const values = data.map(valueFn);
  const min = d3.min(values);
  const max = d3.max(values);
  const range = max - min;

  return data.map(d => ({
    ...d,
    normalized: range === 0 ? 0 : (valueFn(d) - min) / range
  }));
}

/**
 * Standardize values (z-score normalization)
 *
 * @param {Array} data - Input data
 * @param {Function} valueFn - Function to get value
 * @returns {Array} Data with standardized values
 *
 * Usage:
 *   const standardized = standardizeZScore(data, d => d.value);
 */
function standardizeZScore(data, valueFn) {
  const values = data.map(valueFn);
  const mean = d3.mean(values);
  const deviation = d3.deviation(values);

  return data.map(d => ({
    ...d,
    zscore: deviation === 0 ? 0 : (valueFn(d) - mean) / deviation
  }));
}

/**
 * Fill missing values using interpolation
 *
 * @param {Array} data - Input data (must be sorted)
 * @param {Function} valueFn - Function to get value
 * @param {string} method - Interpolation method ('linear', 'forward', 'backward')
 * @returns {Array} Data with filled values
 *
 * Usage:
 *   const filled = fillMissing(data, d => d.value, 'linear');
 */
function fillMissing(data, valueFn, method = 'linear') {
  const result = [...data];

  for (let i = 0; i < result.length; i++) {
    if (valueFn(result[i]) == null) {
      if (method === 'forward') {
        // Use previous value
        let prevIndex = i - 1;
        while (prevIndex >= 0 && valueFn(result[prevIndex]) == null) prevIndex--;
        if (prevIndex >= 0) {
          result[i] = { ...result[i], value: valueFn(result[prevIndex]) };
        }
      } else if (method === 'backward') {
        // Use next value
        let nextIndex = i + 1;
        while (nextIndex < result.length && valueFn(result[nextIndex]) == null) nextIndex++;
        if (nextIndex < result.length) {
          result[i] = { ...result[i], value: valueFn(result[nextIndex]) };
        }
      } else {
        // Linear interpolation
        let prevIndex = i - 1;
        while (prevIndex >= 0 && valueFn(result[prevIndex]) == null) prevIndex--;

        let nextIndex = i + 1;
        while (nextIndex < result.length && valueFn(result[nextIndex]) == null) nextIndex++;

        if (prevIndex >= 0 && nextIndex < result.length) {
          const prevValue = valueFn(result[prevIndex]);
          const nextValue = valueFn(result[nextIndex]);
          const ratio = (i - prevIndex) / (nextIndex - prevIndex);
          result[i] = { ...result[i], value: prevValue + ratio * (nextValue - prevValue) };
        }
      }
    }
  }

  return result;
}

/**
 * Calculate moving average
 *
 * @param {Array} data - Input data (must be sorted)
 * @param {Function} valueFn - Function to get value
 * @param {number} windowSize - Window size for moving average
 * @returns {Array} Data with moving average
 *
 * Usage:
 *   const smoothed = movingAverage(data, d => d.value, 3);
 */
function movingAverage(data, valueFn, windowSize) {
  return data.map((d, i, arr) => {
    const start = Math.max(0, i - Math.floor(windowSize / 2));
    const end = Math.min(arr.length, i + Math.ceil(windowSize / 2));
    const window = arr.slice(start, end);
    const avg = d3.mean(window, valueFn);

    return {
      ...d,
      movingAverage: avg
    };
  });
}

/**
 * Bin data into intervals (histogram)
 *
 * @param {Array} data - Input data
 * @param {Function} valueFn - Function to get value
 * @param {number|Array} thresholds - Number of bins or array of thresholds
 * @returns {Array} Binned data
 *
 * Usage:
 *   const bins = binData(data, d => d.value, 10);
 */
function binData(data, valueFn, thresholds = 10) {
  const histogram = d3.bin()
    .value(valueFn)
    .thresholds(thresholds);

  return histogram(data).map(bin => ({
    x0: bin.x0,
    x1: bin.x1,
    count: bin.length,
    data: bin
  }));
}

/**
 * Create time series with regular intervals
 *
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @param {Function} interval - D3 time interval (e.g., d3.timeDay)
 * @returns {Array} Array of dates
 *
 * Usage:
 *   const dates = createTimeSeries(
 *     new Date('2024-01-01'),
 *     new Date('2024-01-31'),
 *     d3.timeDay
 *   );
 */
function createTimeSeries(startDate, endDate, interval = d3.timeDay) {
  return interval.range(startDate, endDate);
}

/**
 * Resample time series data
 *
 * @param {Array} data - Input data (must be sorted by date)
 * @param {Function} dateFn - Function to get date
 * @param {Function} valueFn - Function to get value
 * @param {Function} interval - D3 time interval
 * @param {Function} aggregateFn - Aggregation function
 * @returns {Array} Resampled data
 *
 * Usage:
 *   const monthly = resampleTimeSeries(
 *     data,
 *     d => d.date,
 *     d => d.value,
 *     d3.timeMonth,
 *     arr => d3.sum(arr, d => d.value)
 *   );
 */
function resampleTimeSeries(data, dateFn, valueFn, interval, aggregateFn) {
  // Group by interval
  const grouped = d3.rollup(
    data,
    values => aggregateFn(values),
    d => interval.floor(dateFn(d))
  );

  // Convert to array
  return Array.from(grouped, ([date, value]) => ({
    date,
    value
  })).sort((a, b) => a.date - b.date);
}

/**
 * Convert wide format to long format
 *
 * @param {Array} data - Input data in wide format
 * @param {Array} idVars - Columns to keep as identifiers
 * @param {Array} valueVars - Columns to pivot
 * @param {string} varName - Name for variable column
 * @param {string} valueName - Name for value column
 * @returns {Array} Data in long format
 *
 * Usage:
 *   const long = wideToLong(
 *     [{date: '2024-01', A: 10, B: 20}, {date: '2024-02', A: 15, B: 25}],
 *     ['date'],
 *     ['A', 'B'],
 *     'series',
 *     'value'
 *   );
 *   // Returns: [{date: '2024-01', series: 'A', value: 10}, ...]
 */
function wideToLong(data, idVars, valueVars, varName = 'variable', valueName = 'value') {
  const result = [];

  for (const row of data) {
    for (const varCol of valueVars) {
      const newRow = {};
      for (const idCol of idVars) {
        newRow[idCol] = row[idCol];
      }
      newRow[varName] = varCol;
      newRow[valueName] = row[varCol];
      result.push(newRow);
    }
  }

  return result;
}

/**
 * Convert long format to wide format
 *
 * @param {Array} data - Input data in long format
 * @param {string} indexCol - Column to use as index
 * @param {string} columnCol - Column to pivot
 * @param {string} valueCol - Column with values
 * @returns {Array} Data in wide format
 *
 * Usage:
 *   const wide = longToWide(
 *     [{date: '2024-01', series: 'A', value: 10}, ...],
 *     'date',
 *     'series',
 *     'value'
 *   );
 *   // Returns: [{date: '2024-01', A: 10, B: 20}, ...]
 */
function longToWide(data, indexCol, columnCol, valueCol) {
  const grouped = d3.group(data, d => d[indexCol]);

  return Array.from(grouped, ([key, values]) => {
    const row = { [indexCol]: key };
    for (const item of values) {
      row[item[columnCol]] = item[valueCol];
    }
    return row;
  });
}

/**
 * Create correlation matrix
 *
 * @param {Array} data - Input data
 * @param {Array} variables - Variable names to correlate
 * @returns {Array} Correlation matrix in long format
 *
 * Usage:
 *   const correlations = correlationMatrix(
 *     data,
 *     ['height', 'weight', 'age']
 *   );
 */
function correlationMatrix(data, variables) {
  const result = [];

  for (const var1 of variables) {
    for (const var2 of variables) {
      const correlation = pearsonCorrelation(
        data,
        d => d[var1],
        d => d[var2]
      );

      result.push({
        var1,
        var2,
        correlation
      });
    }
  }

  return result;
}

/**
 * Calculate Pearson correlation coefficient
 *
 * @param {Array} data - Input data
 * @param {Function} xFn - Function to get x value
 * @param {Function} yFn - Function to get y value
 * @returns {number} Correlation coefficient (-1 to 1)
 */
function pearsonCorrelation(data, xFn, yFn) {
  const n = data.length;
  const xValues = data.map(xFn);
  const yValues = data.map(yFn);

  const xMean = d3.mean(xValues);
  const yMean = d3.mean(yValues);

  let numerator = 0;
  let xDenominator = 0;
  let yDenominator = 0;

  for (let i = 0; i < n; i++) {
    const xDiff = xValues[i] - xMean;
    const yDiff = yValues[i] - yMean;
    numerator += xDiff * yDiff;
    xDenominator += xDiff * xDiff;
    yDenominator += yDiff * yDiff;
  }

  if (xDenominator === 0 || yDenominator === 0) return 0;

  return numerator / Math.sqrt(xDenominator * yDenominator);
}

/**
 * Filter outliers using IQR method
 *
 * @param {Array} data - Input data
 * @param {Function} valueFn - Function to get value
 * @param {number} multiplier - IQR multiplier (default 1.5)
 * @returns {Array} Data without outliers
 *
 * Usage:
 *   const filtered = filterOutliers(data, d => d.value, 1.5);
 */
function filterOutliers(data, valueFn, multiplier = 1.5) {
  const values = data.map(valueFn).sort(d3.ascending);
  const q1 = d3.quantile(values, 0.25);
  const q3 = d3.quantile(values, 0.75);
  const iqr = q3 - q1;

  const lowerBound = q1 - multiplier * iqr;
  const upperBound = q3 + multiplier * iqr;

  return data.filter(d => {
    const value = valueFn(d);
    return value >= lowerBound && value <= upperBound;
  });
}

/**
 * Calculate percentile ranks
 *
 * @param {Array} data - Input data
 * @param {Function} valueFn - Function to get value
 * @returns {Array} Data with percentile ranks
 *
 * Usage:
 *   const ranked = percentileRank(data, d => d.value);
 */
function percentileRank(data, valueFn) {
  const sorted = [...data].sort((a, b) => valueFn(a) - valueFn(b));

  return data.map(d => {
    const value = valueFn(d);
    const rank = sorted.findIndex(item => valueFn(item) === value);
    const percentile = (rank / (sorted.length - 1)) * 100;

    return {
      ...d,
      percentile
    };
  });
}

/**
 * Sample data randomly
 *
 * @param {Array} data - Input data
 * @param {number} sampleSize - Number of samples
 * @param {boolean} withReplacement - Sample with replacement
 * @returns {Array} Sampled data
 *
 * Usage:
 *   const sample = randomSample(data, 100, false);
 */
function randomSample(data, sampleSize, withReplacement = false) {
  if (withReplacement) {
    return Array.from({ length: sampleSize }, () =>
      data[Math.floor(Math.random() * data.length)]
    );
  } else {
    const shuffled = d3.shuffle([...data]);
    return shuffled.slice(0, Math.min(sampleSize, data.length));
  }
}

/**
 * Create train/test split
 *
 * @param {Array} data - Input data
 * @param {number} trainRatio - Ratio for training set (0-1)
 * @param {boolean} shuffle - Shuffle before splitting
 * @returns {Object} Object with train and test arrays
 *
 * Usage:
 *   const {train, test} = trainTestSplit(data, 0.8, true);
 */
function trainTestSplit(data, trainRatio = 0.8, shuffle = true) {
  const dataset = shuffle ? d3.shuffle([...data]) : [...data];
  const splitIndex = Math.floor(dataset.length * trainRatio);

  return {
    train: dataset.slice(0, splitIndex),
    test: dataset.slice(splitIndex)
  };
}

/**
 * Calculate running totals (cumulative sum)
 *
 * @param {Array} data - Input data (must be sorted)
 * @param {Function} valueFn - Function to get value
 * @returns {Array} Data with running totals
 *
 * Usage:
 *   const cumulative = runningTotal(data, d => d.value);
 */
function runningTotal(data, valueFn) {
  let total = 0;

  return data.map(d => {
    total += valueFn(d);
    return {
      ...d,
      runningTotal: total
    };
  });
}

/**
 * Calculate percent change
 *
 * @param {Array} data - Input data (must be sorted)
 * @param {Function} valueFn - Function to get value
 * @returns {Array} Data with percent change
 *
 * Usage:
 *   const changes = percentChange(data, d => d.value);
 */
function percentChange(data, valueFn) {
  return data.map((d, i, arr) => {
    if (i === 0) {
      return { ...d, percentChange: 0 };
    }

    const current = valueFn(d);
    const previous = valueFn(arr[i - 1]);

    const change = previous === 0 ? 0 : ((current - previous) / previous) * 100;

    return {
      ...d,
      percentChange: change
    };
  });
}

/**
 * Create lookup index for fast access
 *
 * @param {Array} data - Input data
 * @param {Function} keyFn - Function to get key
 * @returns {Map} Map of key to item
 *
 * Usage:
 *   const lookup = createIndex(data, d => d.id);
 *   const item = lookup.get('item-123');
 */
function createIndex(data, keyFn) {
  return d3.index(data, keyFn);
}

/**
 * Join two datasets
 *
 * @param {Array} left - Left dataset
 * @param {Array} right - Right dataset
 * @param {Function} leftKey - Key function for left dataset
 * @param {Function} rightKey - Key function for right dataset
 * @param {string} how - Join type ('inner', 'left', 'right', 'outer')
 * @returns {Array} Joined dataset
 *
 * Usage:
 *   const joined = joinData(
 *     users,
 *     orders,
 *     d => d.userId,
 *     d => d.userId,
 *     'left'
 *   );
 */
function joinData(left, right, leftKey, rightKey, how = 'inner') {
  const rightIndex = d3.index(right, rightKey);
  const result = [];

  // Process left dataset
  for (const leftItem of left) {
    const key = leftKey(leftItem);
    const rightItem = rightIndex.get(key);

    if (how === 'inner' && !rightItem) continue;

    result.push({
      ...leftItem,
      ...(rightItem || {})
    });
  }

  // Process unmatched right items (for outer join)
  if (how === 'outer' || how === 'right') {
    const leftIndex = d3.index(left, leftKey);

    for (const rightItem of right) {
      const key = rightKey(rightItem);
      const leftItem = leftIndex.get(key);

      if (!leftItem) {
        result.push(rightItem);
      }
    }
  }

  return result;
}

/**
 * Generate sample data for testing
 *
 * @param {number} count - Number of data points
 * @param {Object} config - Configuration for data generation
 * @returns {Array} Generated data
 *
 * Usage:
 *   const data = generateSampleData(100, {
 *     startDate: new Date('2024-01-01'),
 *     trend: 'increasing',
 *     noise: 0.1
 *   });
 */
function generateSampleData(count, config = {}) {
  const defaults = {
    startDate: new Date('2024-01-01'),
    interval: d3.timeDay,
    baseValue: 100,
    trend: 'none', // 'none', 'increasing', 'decreasing', 'seasonal'
    trendStrength: 0.5,
    noise: 0.1,
    seasonalPeriod: 7,
    seasonalAmplitude: 20
  };

  const cfg = { ...defaults, ...config };
  const data = [];

  for (let i = 0; i < count; i++) {
    const date = cfg.interval.offset(cfg.startDate, i);

    let value = cfg.baseValue;

    // Add trend
    if (cfg.trend === 'increasing') {
      value += i * cfg.trendStrength;
    } else if (cfg.trend === 'decreasing') {
      value -= i * cfg.trendStrength;
    } else if (cfg.trend === 'seasonal') {
      value += Math.sin((i / cfg.seasonalPeriod) * 2 * Math.PI) * cfg.seasonalAmplitude;
    }

    // Add noise
    value += (Math.random() - 0.5) * cfg.baseValue * cfg.noise;

    data.push({
      date,
      value: Math.max(0, value),
      category: `Category ${String.fromCharCode(65 + (i % 5))}`,
      id: `item-${i}`
    });
  }

  return data;
}
