#!/usr/bin/env node

/**
 * Initialize a Vitest + TypeScript project for TDD
 * Usage: node setup-vitest.js [project-name]
 */

import { execSync } from 'child_process';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

const projectName = process.argv[2] || '.';
const isCurrentDir = projectName === '.';

function run(command, options = {}) {
  console.log(`Running: ${command}`);
  execSync(command, { stdio: 'inherit', ...options });
}

function createFile(path, content) {
  console.log(`Creating: ${path}`);
  writeFileSync(path, content.trim() + '\n');
}

function main() {
  // Create project directory if needed
  if (!isCurrentDir) {
    if (existsSync(projectName)) {
      console.error(`Error: Directory ${projectName} already exists`);
      process.exit(1);
    }
    mkdirSync(projectName, { recursive: true });
    process.chdir(projectName);
  }

  console.log('Initializing Vitest + TypeScript project...\n');

  // Initialize npm project
  if (!existsSync('package.json')) {
    run('npm init -y');
  }

  // Install dependencies
  console.log('\nInstalling dependencies...');
  run('npm install -D vitest @vitest/ui @vitest/coverage-v8 typescript @types/node');

  // Create TypeScript config
  createFile(
    'tsconfig.json',
    `{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020"],
    "moduleResolution": "node",
    "types": ["vitest/globals", "node"],
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}`
  );

  // Create Vitest config
  createFile(
    'vitest.config.ts',
    `import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/types.ts',
      ],
    },
  },
});`
  );

  // Create directory structure
  mkdirSync('src', { recursive: true });
  mkdirSync('src/__tests__', { recursive: true });

  // Create example files
  createFile(
    'src/calculator.ts',
    `export class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }

  subtract(a: number, b: number): number {
    return a - b;
  }

  multiply(a: number, b: number): number {
    return a * b;
  }

  divide(a: number, b: number): number {
    if (b === 0) {
      throw new Error('Division by zero');
    }
    return a / b;
  }
}`
  );

  createFile(
    'src/__tests__/calculator.test.ts',
    `import { describe, it, expect } from 'vitest';
import { Calculator } from '../calculator';

describe('Calculator', () => {
  const calc = new Calculator();

  describe('add', () => {
    it('adds two positive numbers', () => {
      expect(calc.add(2, 3)).toBe(5);
    });

    it('adds negative numbers', () => {
      expect(calc.add(-2, -3)).toBe(-5);
    });
  });

  describe('subtract', () => {
    it('subtracts two numbers', () => {
      expect(calc.subtract(5, 3)).toBe(2);
    });
  });

  describe('multiply', () => {
    it('multiplies two numbers', () => {
      expect(calc.multiply(4, 3)).toBe(12);
    });
  });

  describe('divide', () => {
    it('divides two numbers', () => {
      expect(calc.divide(10, 2)).toBe(5);
    });

    it('throws error when dividing by zero', () => {
      expect(() => calc.divide(10, 0)).toThrow('Division by zero');
    });
  });
});`
  );

  // Update package.json scripts
  const packageJson = JSON.parse(
    require('fs').readFileSync('package.json', 'utf-8')
  );
  packageJson.scripts = {
    ...packageJson.scripts,
    test: 'vitest',
    'test:ui': 'vitest --ui',
    'test:run': 'vitest run',
    coverage: 'vitest --coverage',
  };
  packageJson.type = 'module';
  writeFileSync('package.json', JSON.stringify(packageJson, null, 2) + '\n');

  // Create .gitignore if it doesn't exist
  if (!existsSync('.gitignore')) {
    createFile(
      '.gitignore',
      `node_modules/
dist/
coverage/
.vitest/
*.log`
    );
  }

  // Create README
  createFile(
    'README.md',
    `# ${isCurrentDir ? 'Vitest TypeScript Project' : projectName}

A Test-Driven Development project using Vitest and TypeScript.

## Getting Started

### Run tests in watch mode
\`\`\`bash
npm test
\`\`\`

### Run tests once
\`\`\`bash
npm run test:run
\`\`\`

### View test UI
\`\`\`bash
npm run test:ui
\`\`\`

### Generate coverage report
\`\`\`bash
npm run coverage
\`\`\`

## TDD Workflow

1. **Red**: Write a failing test
2. **Green**: Make the test pass with minimal code
3. **Refactor**: Improve code while keeping tests green

## Project Structure

\`\`\`
src/
├── __tests__/           # Test files
│   └── calculator.test.ts
└── calculator.ts        # Source files
\`\`\`

## Example Test

\`\`\`typescript
import { describe, it, expect } from 'vitest';

describe('MyFeature', () => {
  it('does something', () => {
    expect(true).toBe(true);
  });
});
\`\`\`
`
  );

  console.log('\n✅ Setup complete!\n');
  console.log('Next steps:');
  if (!isCurrentDir) {
    console.log(`  cd ${projectName}`);
  }
  console.log('  npm test          # Start TDD with watch mode');
  console.log('  npm run test:ui   # Open test UI in browser');
  console.log('  npm run coverage  # Generate coverage report\n');
}

main();
