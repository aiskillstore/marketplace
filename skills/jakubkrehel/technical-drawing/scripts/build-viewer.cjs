#!/usr/bin/env node
const fs = require('node:fs'), path = require('node:path');

const assets = path.resolve(__dirname, '../assets');
const read = file => fs.readFileSync(file, 'utf8');
const asset = name => read(path.join(assets, name));
const script = source => source.replace(/<\/script/gi, '<\\/script');
const json = value => JSON.stringify(value).replaceAll('<', '\\u003c');

function validate(config) {
  if (!Array.isArray(config.drawings) || !config.drawings.length) throw Error('Provide at least one drawing');
  const ids = new Set();
  for (const d of config.drawings) {
    if (!/^[a-z][a-z0-9-]*$/.test(d.id) || ids.has(d.id)) throw Error('Drawing IDs must be unique slugs');
    ids.add(d.id);
    if (!d.title || !d.description || !Array.isArray(d.parts) || !d.parts.length) throw Error('Drawing metadata is incomplete');
    if (d.initialView !== undefined && !['assembled', 'exploded'].includes(d.initialView)) throw Error('Initial view must be assembled or exploded');
    d.parameters ??= [];

    const parts = new Set();
    for (const p of d.parts) {
      if (!/^[a-zA-Z0-9_-]+$/.test(String(p.id)) || parts.has(String(p.id)) || !p.name) throw Error('Part IDs must be unique safe identifiers');
      parts.add(String(p.id));
    }
    const keys = new Set();
    for (const p of d.parameters) {
      if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(p.key) || keys.has(p.key) || !p.label) throw Error('Parameter keys must be unique safe identifiers');
      keys.add(p.key);
      const step = p.step ?? 1;
      if (![p.min, p.max, p.default, step].every(Number.isFinite) || p.max <= p.min || p.default < p.min || p.default > p.max || step <= 0) {
        throw Error('Invalid parameter range');
      }
    }
  }
  if (!Array.isArray(config.modelScripts) || !config.modelScripts.length) throw Error('Provide model scripts defining self.DrawingModels');
}

function build(configPath, outputPath) {
  const base = path.dirname(path.resolve(configPath)), config = JSON.parse(read(configPath));
  validate(config);
  const resolve = file => path.resolve(base, file), deps = resolve(config.dependencies);
  const dependency = file => path.join(deps, file);
  const worker = [asset('geometry.js'), asset('projection.js'), ...config.modelScripts.map(f => read(resolve(f))), asset('worker.js')].join('\n');
  const replacements = {
    __INTER_LICENSE__: script(read(dependency('@fontsource-variable/inter/LICENSE'))),
    __INTER_FONT__: fs.readFileSync(dependency('@fontsource-variable/inter/files/inter-latin-wght-normal.woff2')).toString('base64'),
    __DRAWING_DATA__: json(config.drawings),
    __JSPDF__: script(read(dependency('jspdf/dist/jspdf.umd.min.js'))),
    __SVG2PDF__: script(read(dependency('svg2pdf.js/dist/svg2pdf.umd.min.js'))),
    __WORKER_SOURCE__: json(worker),
    __THEME_SCRIPT__: script(asset('theme.js')),
    __EXPORT_SCRIPT__: script(asset('export.js')),
    __RENDER_QUEUE_SCRIPT__: script(asset('render-queue.js')),
    __VIEWER_SCRIPT__: script(asset('viewer.js'))
  };
  const html = asset('viewer.html').replace(/__[A-Z0-9_]+__/g, key => {
    if (!(key in replacements)) throw Error('Unknown template token ' + key);
    return replacements[key];
  });
  fs.mkdirSync(path.dirname(path.resolve(outputPath)), {recursive: true});
  fs.writeFileSync(outputPath, html);
  return path.resolve(outputPath);
}

if (require.main === module) {
  try {
    if (process.argv.length !== 4) throw Error('Usage: node build-viewer.cjs drawing.json output/index.html');
    console.log(build(process.argv[2], process.argv[3]));
  } catch (e) {
    console.error(e.message);
    process.exitCode = 1;
  }
}
module.exports = build;
