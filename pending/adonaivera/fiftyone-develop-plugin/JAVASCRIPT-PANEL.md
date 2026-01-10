# JavaScript Panel Development

## Overview

JavaScript panels provide rich, interactive UIs using React and the FiftyOne JavaScript SDK. They offer more flexibility than Python panels but require additional setup.

## When to Use JavaScript Panels

Use JavaScript panels when you need:
- Complex interactive visualizations
- Custom React components
- Real-time updates without page refresh
- Integration with existing React libraries
- Advanced styling with CSS/Tailwind

For simpler UIs, prefer Python panels.

## Project Setup

### Directory Structure

```
my-js-plugin/
├── fiftyone.yml          # Plugin manifest
├── package.json          # Node.js dependencies
├── tsconfig.json         # TypeScript config
├── vite.config.ts        # Build configuration
├── src/
│   ├── index.tsx         # Main entry point
│   └── components/       # React components
│       └── MyPanel.tsx
└── dist/
    └── index.umd.js      # Compiled bundle
```

### fiftyone.yml

```yaml
name: "@myorg/js-panel"
type: plugin
version: 1.0.0
panels:
  - my_panel
```

### package.json

```json
{
  "name": "@myorg/js-panel",
  "version": "1.0.0",
  "main": "dist/index.umd.js",
  "scripts": {
    "build": "vite build",
    "dev": "vite build --watch"
  },
  "dependencies": {
    "@fiftyone/components": "*",
    "@fiftyone/operators": "*",
    "@fiftyone/plugins": "*",
    "@fiftyone/state": "*"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "react": "^18.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

### vite.config.ts

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: "src/index.tsx",
      name: "MyPlugin",
      fileName: "index",
      formats: ["umd"],
    },
    rollupOptions: {
      external: [
        "react",
        "react-dom",
        "@fiftyone/components",
        "@fiftyone/operators",
        "@fiftyone/plugins",
        "@fiftyone/state",
        "recoil",
      ],
      output: {
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
          recoil: "recoil",
          "@fiftyone/components": "__foc__",
          "@fiftyone/operators": "__foo__",
          "@fiftyone/plugins": "__fop__",
          "@fiftyone/state": "__fos__",
        },
      },
    },
  },
});
```

## Component Registration

### src/index.tsx

```typescript
import { registerComponent, PluginComponentTypes } from "@fiftyone/plugins";
import MyPanel from "./components/MyPanel";

// Register the panel
registerComponent({
  name: "my_panel",           // Must match fiftyone.yml
  label: "My Panel",          // Display name
  component: MyPanel,         // React component
  type: PluginComponentTypes.Panel,
  activator: ({ dataset }) => {
    // Return true to show panel, false to hide
    return dataset !== null;
  },
  surfaces: "grid",           // "grid", "modal", or "grid modal"
});
```

## React Component Development

### Basic Panel Component

```typescript
// src/components/MyPanel.tsx
import React from "react";
import { useRecoilValue } from "recoil";
import * as fos from "@fiftyone/state";
import { Button } from "@fiftyone/components";

const MyPanel: React.FC = () => {
  // Access FiftyOne state
  const dataset = useRecoilValue(fos.dataset);
  const view = useRecoilValue(fos.view);
  const selected = useRecoilValue(fos.selectedSamples);

  return (
    <div style={{ padding: "16px" }}>
      <h2>My Panel</h2>
      <p>Dataset: {dataset?.name}</p>
      <p>Samples in view: {view?.length ?? 0}</p>
      <p>Selected: {selected.size}</p>
      <Button onClick={() => console.log("Clicked!")}>
        Click Me
      </Button>
    </div>
  );
};

export default MyPanel;
```

### Using FiftyOne State

```typescript
import { useRecoilValue, useSetRecoilState } from "recoil";
import * as fos from "@fiftyone/state";

const MyComponent: React.FC = () => {
  // Read state
  const dataset = useRecoilValue(fos.dataset);
  const view = useRecoilValue(fos.view);
  const selected = useRecoilValue(fos.selectedSamples);
  const filters = useRecoilValue(fos.filters);

  // Write state
  const setSelected = fos.useSetSelected();
  const setView = fos.useSetView();

  const handleSelectAll = () => {
    // Select all samples in current view
    if (view) {
      const ids = view.map((s) => s.id);
      setSelected(ids);
    }
  };

  const handleClearFilters = () => {
    setView([]);  // Reset to full dataset
  };

  return (
    <div>
      <button onClick={handleSelectAll}>Select All</button>
      <button onClick={handleClearFilters}>Clear Filters</button>
    </div>
  );
};
```

### Panel State Management

```typescript
import React, { useState, useEffect } from "react";
import { usePanelState } from "@fiftyone/state";

const StatefulPanel: React.FC = () => {
  // Use panel-scoped state that persists across renders
  const [count, setCount] = usePanelState("count", 0);
  const [config, setConfig] = usePanelState("config", { theme: "light" });

  // Local state (resets on re-render)
  const [localValue, setLocalValue] = useState("");

  return (
    <div>
      <p>Persistent count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>

      <p>Config theme: {config.theme}</p>
      <button onClick={() => setConfig({ ...config, theme: "dark" })}>
        Toggle Theme
      </button>
    </div>
  );
};
```

### Triggering Operators

```typescript
import { useOperatorExecutor } from "@fiftyone/operators";

const OperatorTrigger: React.FC = () => {
  const executor = useOperatorExecutor("@voxel51/brain/compute_similarity");

  const handleCompute = async () => {
    await executor.execute({
      brain_key: "my_similarity",
      model: "clip-vit-base32-torch",
    });
  };

  return (
    <button onClick={handleCompute} disabled={executor.isLoading}>
      {executor.isLoading ? "Computing..." : "Compute Similarity"}
    </button>
  );
};
```

## Styling

### Using Tailwind CSS

```typescript
import "@fiftyone/components/dist/styles.css";  // Base styles

const StyledPanel: React.FC = () => {
  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h2 className="text-lg font-bold mb-2">Styled Panel</h2>
      <p className="text-gray-600">This uses Tailwind classes</p>
    </div>
  );
};
```

### Using CSS-in-JS

```typescript
const styles = {
  container: {
    padding: "16px",
    backgroundColor: "#f5f5f5",
    borderRadius: "8px",
  },
  title: {
    fontSize: "18px",
    fontWeight: "bold",
    marginBottom: "8px",
  },
};

const StyledPanel: React.FC = () => {
  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Styled Panel</h2>
    </div>
  );
};
```

## JavaScript Operators

You can also define operators in JavaScript:

```typescript
import { Operator, OperatorConfig, registerOperator } from "@fiftyone/operators";
import * as fos from "@fiftyone/state";

class SelectRandomSamples extends Operator {
  get config(): OperatorConfig {
    return new OperatorConfig({
      name: "select_random_samples",
      label: "Select Random Samples",
    });
  }

  useHooks() {
    return {
      setSelected: fos.useSetSelected(),
    };
  }

  async execute({ hooks, params }) {
    const { count = 10 } = params;
    // Get random sample IDs (simplified example)
    const randomIds = ["sample1", "sample2", "sample3"].slice(0, count);
    hooks.setSelected(randomIds);
    return { selected: randomIds.length };
  }
}

registerOperator(SelectRandomSamples);
```

## Building and Installing

### Development Build

```bash
npm install
npm run dev  # Watch mode - rebuilds on changes
```

### Production Build

```bash
npm run build
```

### Installing Plugin

```bash
# Copy to FiftyOne plugins directory
cp -r ./my-js-plugin ~/.fiftyone/plugins/

# Or install from GitHub
fiftyone plugins download https://github.com/org/my-js-plugin
```

### Hot Reload During Development

```bash
# Terminal 1: Watch for changes
cd my-js-plugin
npm run dev

# Terminal 2: Symlink plugin
ln -s $(pwd) ~/.fiftyone/plugins/my-js-plugin

# Refresh FiftyOne App in browser to see changes
```

## Complete Example: Sample Browser Panel

```typescript
// src/index.tsx
import { registerComponent, PluginComponentTypes } from "@fiftyone/plugins";
import SampleBrowser from "./components/SampleBrowser";

registerComponent({
  name: "sample_browser",
  label: "Sample Browser",
  component: SampleBrowser,
  type: PluginComponentTypes.Panel,
  activator: ({ dataset }) => dataset !== null,
  surfaces: "grid",
});
```

```typescript
// src/components/SampleBrowser.tsx
import React, { useState, useEffect } from "react";
import { useRecoilValue } from "recoil";
import * as fos from "@fiftyone/state";
import { Button, Input, Select } from "@fiftyone/components";

interface Sample {
  id: string;
  filepath: string;
  [key: string]: any;
}

const SampleBrowser: React.FC = () => {
  const dataset = useRecoilValue(fos.dataset);
  const view = useRecoilValue(fos.view);
  const selected = useRecoilValue(fos.selectedSamples);
  const setSelected = fos.useSetSelected();

  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState("filepath");
  const [filteredSamples, setFilteredSamples] = useState<Sample[]>([]);

  // Get field names for sorting
  const fieldNames = Object.keys(dataset?.sampleFields || {});

  useEffect(() => {
    if (view) {
      // Filter samples by search term
      const filtered = view.filter((sample: Sample) =>
        sample.filepath.toLowerCase().includes(searchTerm.toLowerCase())
      );

      // Sort samples
      filtered.sort((a: Sample, b: Sample) => {
        const aVal = a[sortField] || "";
        const bVal = b[sortField] || "";
        return String(aVal).localeCompare(String(bVal));
      });

      setFilteredSamples(filtered);
    }
  }, [view, searchTerm, sortField]);

  const handleSelectSample = (id: string) => {
    const newSelected = new Set(selected);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelected(Array.from(newSelected));
  };

  const handleSelectAll = () => {
    setSelected(filteredSamples.map((s) => s.id));
  };

  const handleClearSelection = () => {
    setSelected([]);
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Sample Browser</h2>

      {/* Controls */}
      <div className="flex gap-4 mb-4">
        <Input
          placeholder="Search by filepath..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1"
        />

        <Select
          value={sortField}
          onChange={(e) => setSortField(e.target.value)}
        >
          {fieldNames.map((field) => (
            <option key={field} value={field}>
              Sort by: {field}
            </option>
          ))}
        </Select>
      </div>

      {/* Selection controls */}
      <div className="flex gap-2 mb-4">
        <Button onClick={handleSelectAll}>Select All</Button>
        <Button onClick={handleClearSelection} variant="secondary">
          Clear Selection
        </Button>
        <span className="ml-auto text-gray-600">
          {selected.size} of {filteredSamples.length} selected
        </span>
      </div>

      {/* Sample list */}
      <div className="border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-2 text-left">Select</th>
              <th className="p-2 text-left">ID</th>
              <th className="p-2 text-left">Filepath</th>
            </tr>
          </thead>
          <tbody>
            {filteredSamples.slice(0, 100).map((sample) => (
              <tr
                key={sample.id}
                className={`border-t ${
                  selected.has(sample.id) ? "bg-blue-50" : ""
                }`}
              >
                <td className="p-2">
                  <input
                    type="checkbox"
                    checked={selected.has(sample.id)}
                    onChange={() => handleSelectSample(sample.id)}
                  />
                </td>
                <td className="p-2 font-mono text-sm">
                  {sample.id.slice(0, 8)}...
                </td>
                <td className="p-2 text-sm">{sample.filepath}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredSamples.length > 100 && (
          <div className="p-4 text-center text-gray-500 border-t">
            Showing 100 of {filteredSamples.length} samples
          </div>
        )}
      </div>
    </div>
  );
};

export default SampleBrowser;
```

## Troubleshooting

**Panel not appearing:**
- Check `name` in `registerComponent` matches `fiftyone.yml`
- Verify `dist/index.umd.js` was built
- Check browser console for JavaScript errors
- Refresh the FiftyOne App

**Build errors:**
- Ensure all peer dependencies are installed
- Check TypeScript errors in source files
- Verify Vite configuration

**State not updating:**
- Use `useRecoilValue` for reading state
- Use FiftyOne hooks like `useSetSelected` for writing
- Verify component re-renders when state changes

**Operator not found:**
- Register operators with `registerOperator`
- Add operator name to `fiftyone.yml` under `operators:`
- Restart FiftyOne App after changes
