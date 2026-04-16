import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/cli.ts'],
  format: ['esm'],
  target: 'node18',
  clean: true,
  outDir: 'dist',
  loader: {
    '.ts': 'tsx',
  },
});
