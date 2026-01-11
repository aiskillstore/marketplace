# Data Transformation Reference

## Loading Data

### CSV

```javascript
d3.csv("data.csv").then(data => {
  console.log(data);
  // Auto-parsed into array of objects
});
```

### JSON

```javascript
d3.json("data.json").then(data => {
  console.log(data);
});
```

### Multiple Files

```javascript
Promise.all([
  d3.csv("data1.csv"),
  d3.json("data2.json")
]).then(([csv, json]) => {
  console.log(csv, json);
});
```

## Parsing and Type Conversion

```javascript
d3.csv("data.csv", function(d) {
  return {
    date: new Date(d.date),
    value: +d.value,           // Convert to number
    category: d.category,       // Keep as string
    active: d.active === "true" // Convert to boolean
  };
}).then(data => {
  console.log(data);
});
```

## Data Transformation Operations

### Filtering

```javascript
const filtered = data.filter(d => d.value > 50);
```

### Mapping

```javascript
const values = data.map(d => d.value);
```

### Sorting

```javascript
const sorted = data.sort((a, b) => b.value - a.value);
```

### Grouping

```javascript
const grouped = d3.group(data, d => d.category);
// Returns Map: category -> array of objects
```

### Rollup (Aggregation)

```javascript
const summed = d3.rollup(
  data,
  v => d3.sum(v, d => d.value),  // Aggregation function
  d => d.category                 // Grouping key
);
// Returns Map: category -> sum
```

### Extent

```javascript
const [min, max] = d3.extent(data, d => d.value);
```

### Statistical Functions

```javascript
d3.min(data, d => d.value)
d3.max(data, d => d.value)
d3.sum(data, d => d.value)
d3.mean(data, d => d.value)
d3.median(data, d => d.value)
```

## Advanced Data Aggregation

### Grouping by Single Key

```javascript
const byCategory = d3.group(data, d => d.category);
// Map { "A" => [{...}, {...}], "B" => [{...}] }
```

### Grouping by Multiple Keys

```javascript
const byYearAndCategory = d3.group(
  data,
  d => d.year,
  d => d.category
);
// Map { 2020 => Map { "A" => [...], "B" => [...] }, ... }
```

### Index (Single Value Per Key)

```javascript
const byId = d3.index(data, d => d.id);
// Map { "id1" => {...}, "id2" => {...} }
```

### Sum by Category

```javascript
const sumByCategory = d3.rollup(
  data,
  v => d3.sum(v, d => d.value),
  d => d.category
);
// Map { "A" => 150, "B" => 200 }
```

### Multiple Aggregations

```javascript
const statsByCategory = d3.rollup(
  data,
  v => ({
    count: v.length,
    sum: d3.sum(v, d => d.value),
    mean: d3.mean(v, d => d.value),
    min: d3.min(v, d => d.value),
    max: d3.max(v, d => d.value)
  }),
  d => d.category
);
```

## Date/Time Handling

### Parsing Dates

```javascript
// Built-in formats
const parser = d3.timeParse("%Y-%m-%d");
const date = parser("2023-01-15");

// Format specifiers
// %Y - 4-digit year (2023)
// %y - 2-digit year (23)
// %m - month (01-12)
// %d - day (01-31)
// %H - hour 24h (00-23)
// %I - hour 12h (01-12)
// %M - minute (00-59)
// %S - second (00-59)
// %p - AM/PM

const parser2 = d3.timeParse("%m/%d/%Y %I:%M %p");
const date2 = parser2("01/15/2023 02:30 PM");
```

### Formatting Dates

```javascript
const formatter = d3.timeFormat("%b %d, %Y");
formatter(new Date(2023, 0, 15)); // "Jan 15, 2023"

// Common formats
d3.timeFormat("%Y-%m-%d")(date)        // "2023-01-15"
d3.timeFormat("%B %d, %Y")(date)       // "January 15, 2023"
d3.timeFormat("%b %d")(date)           // "Jan 15"
d3.timeFormat("%m/%d/%Y")(date)        // "01/15/2023"
d3.timeFormat("%I:%M %p")(date)        // "02:30 PM"
```
