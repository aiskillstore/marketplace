const drawings = JSON.parse(document.getElementById('drawing-data').textContent);
const $ = id => document.getElementById(id), ns = 'http://www.w3.org/2000/svg';
const SHEET = {width: 420, height: 297};
const RENDER_DELAY = 120;
const viewport = $('viewport'), stage = $('stage'), drawing = $('drawing'), selection = $('selection'), selectionBox = $('selection-box');
const palette = [['Graphite', '#202020'], ['Blue', '#3568b0'], ['Green', '#397362'], ['Terracotta', '#b25940'], ['Ochre', '#99752b'], ['Violet', '#805699']];
const presets = {
  technical: {outline: .35, edge: .22, detail: .13, texture: .09},
  patent: {outline: .24, edge: .15, detail: .10, texture: .065},
  service: {outline: .5, edge: .28, detail: .16, texture: 0}
};
const geometryKeys = ['params', 'explosion', 'isolated'];
const storageKey = 'object-studies-colors-v2';

const defaultInk = () => ({base: palette[0][1], parts: {}});
const defaultParams = d => Object.fromEntries(d.parameters.map(p => [p.key, p.default]));
const slug = name => name.toLowerCase().replace(/[^a-z0-9]+/g, '-');

let preferences = {};
try { preferences = JSON.parse(localStorage.getItem(storageKey) || '{}'); } catch {}
const states = new Map(drawings.map(d => [d.id, {
  params: defaultParams(d),
  explosion: (d.initialView ?? (d.parts.length === 1 ? 'assembled' : 'exploded')) === 'assembled' ? 0 : 1,
  preset: 'technical',
  selectedPart: 'all',
  isolated: null
}]));
let selected = drawings.find(d => d.id === location.hash.slice(1)) || drawings[0];
let zoom = 1, svg = null, geometry = null, drawingStatus = 'rendering', exportBusy = false, messageTimer;

const workerUrl = URL.createObjectURL(new Blob([JSON.parse($('drawing-worker').textContent)], {type: 'text/javascript'}));
const renderer = DrawingRenderQueue.create(new Worker(workerUrl));
URL.revokeObjectURL(workerUrl);

const state = () => states.get(selected.id);
const colors = () => preferences[selected.id] ??= defaultInk();

function save() {
  try { localStorage.setItem(storageKey, JSON.stringify(preferences)); } catch {}
}

function announce(text, persistent = false) {
  clearTimeout(messageTimer);
  $('message').textContent = text;
  if (!persistent) messageTimer = setTimeout(() => { $('message').textContent = ''; }, 5000);
}

function createSvg(name, attributes = {}) {
  const node = document.createElementNS(ns, name);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  return node;
}

function requestGeometry(subject, target, options) {
  return renderer.request({id: subject.id, parameters: target.params, explosion: target.explosion, isolated: target.isolated}, options);
}

function mountGeometry(result, subject, target) {
  const node = createSvg('svg', {
    xmlns: ns, width: SHEET.width + 'mm', height: SHEET.height + 'mm', viewBox: `0 0 ${SHEET.width} ${SHEET.height}`,
    role: 'img', 'aria-labelledby': 'art-title art-description'
  });
  const part = subject.parts.find(p => String(p.id) === String(target.isolated));
  const title = createSvg('title', {id: 'art-title'});
  title.textContent = subject.title + ' · ' + (part ? part.name : (target.explosion ? 'exploded' : 'assembled') + ' view');
  const desc = createSvg('desc', {id: 'art-description'});
  desc.textContent = subject.description + (part ? ' Isolated component: ' + part.name + '.' : '');
  const group = createSvg('g', {id: 'geometry'});
  group.innerHTML = result.markup;
  node.append(title, desc, createSvg('rect', {id: 'paper', width: SHEET.width, height: SHEET.height, fill: 'white'}), group);
  return {node, group};
}

function styleGeometry(group, preset, ink) {
  const weights = presets[preset], inkFor = el => ink.parts[el.closest('[data-item]')?.dataset.item] || ink.base;
  group.style.setProperty('--drawing-ink', ink.base);
  for (const part of group.querySelectorAll('[data-item]')) part.style.setProperty('--drawing-ink', ink.parts[part.dataset.item] || ink.base);
  for (const el of group.querySelectorAll('[data-ink-fill]')) {
    el.style.removeProperty('fill');
    el.setAttribute('fill', inkFor(el));
  }
  for (const el of group.querySelectorAll('[data-line-role]')) {
    const weight = weights[el.dataset.lineRole] ?? weights.detail;
    el.style.removeProperty('stroke');
    el.setAttribute('stroke', inkFor(el));
    el.setAttribute('stroke-width', weight);
    el.setAttribute('stroke-linecap', 'butt');
    el.setAttribute('stroke-linejoin', 'round');
    el.style.display = weight ? '' : 'none';
  }
}

function stripPreviewHooks(node) {
  node.removeAttribute('role');
  node.removeAttribute('aria-labelledby');
  for (const el of node.querySelectorAll('[data-ink-fill]')) el.removeAttribute('data-ink-fill');
  for (const el of node.querySelectorAll('[style]')) {
    el.style.removeProperty('--drawing-ink');
    if (!el.style.length) el.removeAttribute('style');
  }
  return node;
}

function setDrawingStatus(status) {
  drawingStatus = status;
  viewport.setAttribute('aria-busy', String(status === 'rendering'));
  $('render-status').textContent = status === 'rendering' ? 'Updating drawing' : status === 'ready' ? 'Drawing updated' : '';
  updateAvailability();
}

async function render(delay = 0) {
  const subject = selected;
  setDrawingStatus('rendering');
  try {
    const target = structuredClone(state());
    const mounted = mountGeometry(await requestGeometry(subject, target, {preview: true, delay}), subject, target);
    svg = mounted.node;
    geometry = mounted.group;
    drawing.replaceChildren(svg, selection);
    styleGeometry(geometry, state().preset, colors());
    document.title = subject.title + ' · Technical drawing';
    setDrawingStatus('ready');
    updateSelection();
    renderZoom();
  } catch (error) {
    if (error.name === 'AbortError') return;
    console.error(error);
    announce('Could not update the drawing. Restore the settings and try again.', true);
    setDrawingStatus('failed');
  }
}

function update(patch, {delay = 0} = {}) {
  Object.assign(state(), patch);
  syncControls();
  if (geometryKeys.some(key => key in patch)) render(delay);
  else restyle();
}

function restyle() {
  if (geometry) styleGeometry(geometry, state().preset, colors());
  updateSelection();
  updateColorControls();
}

function editColors(change) {
  change(colors());
  restyle();
  save();
}

function updateAvailability() {
  const noPart = state().selectedPart === 'all', unavailable = drawingStatus !== 'ready' || exportBusy;
  for (const button of document.querySelectorAll('.export-choice[data-format]')) button.disabled = unavailable;
  $('download-part').disabled = unavailable || noPart;
  $('isolate-part').disabled = noPart || exportBusy;
  $('color-part').disabled = noPart;
}

function syncControls() {
  const s = state(), isolated = s.isolated !== null;
  $('linework').value = s.preset;
  $('explosion').value = s.explosion * 100;
  $('explosion-value').value = Math.round(s.explosion * 100) + '%';
  $('view').value = s.explosion === 0 ? 'assembled' : 'exploded';
  $('part-target').value = s.selectedPart;
  $('isolate-part').setAttribute('aria-pressed', String(isolated));
  $('isolate-part').textContent = isolated ? 'Isolated' : 'Isolate';
  $('parts-toggle').setAttribute('aria-pressed', String(s.selectedPart !== 'all'));
  updateAvailability();
}

function updateSelection() {
  const s = state(), part = s.isolated === null ? geometry?.querySelector(`[data-item="${s.selectedPart}"]`) : null;
  selection.toggleAttribute('hidden', !part);
  if (!part) return;
  const box = part.getBBox();
  for (const [name, value] of Object.entries({x: box.x - 2, y: box.y - 2, width: box.width + 4, height: box.height + 4})) {
    selectionBox.setAttribute(name, value);
  }
}

function updateColorControls() {
  const target = $('color-target').value, c = colors(), ink = target === 'all' ? c.base : (c.parts[target] || c.base);
  const mixed = target === 'all' && Object.values(c.parts).some(value => value !== c.base);
  $('custom-color').value = ink;
  $('hex-color').value = mixed ? '' : ink.toUpperCase();
  $('hex-color').placeholder = mixed ? 'Mixed colors' : palette[0][1];
  $('hex-color').setAttribute('aria-invalid', 'false');
  for (const button of $('swatches').children) {
    button.setAttribute('aria-pressed', String(!mixed && button.dataset.color.toLowerCase() === ink.toLowerCase()));
  }
  $('color-dot').style.background = Object.keys(c.parts).length ? 'conic-gradient(' + palette.slice(1).map(p => p[1]).join(',') + ')' : c.base;
}

function setColor(value) {
  if (!/^#[0-9a-f]{6}$/i.test(value)) {
    $('hex-color').setAttribute('aria-invalid', 'true');
    return;
  }
  const target = $('color-target').value;
  editColors(c => {
    if (target === 'all') {
      c.base = value;
      c.parts = {};
    } else {
      c.parts[target] = value;
    }
  });
}

function choosePart(id) {
  update(state().isolated === null ? {selectedPart: id} : {selectedPart: id, isolated: id === 'all' ? null : id});
}

function buildParameterControls() {
  $('parameters').replaceChildren();
  for (const id of ['parameter-divider', 'reset-parameters', 'parameter-note']) $(id).hidden = !selected.parameters.length;
  $('parameter-note').textContent = selected.parameterNote || 'Concept dimensions. Changes update matching parts in every view.';
  for (const p of selected.parameters) {
    const field = document.createElement('div');
    field.className = 'field';
    const row = document.createElement('div');
    row.className = 'field-title';
    const label = document.createElement('label');
    label.htmlFor = 'parameter-' + p.key;
    label.textContent = p.label;
    const value = document.createElement('output');
    value.id = 'value-' + p.key;
    value.htmlFor = 'parameter-' + p.key;
    const input = document.createElement('input');
    Object.assign(input, {type: 'range', id: 'parameter-' + p.key, min: p.min, max: p.max, step: p.step || 1, value: state().params[p.key]});
    const show = () => { value.textContent = input.value + (p.unit ? ' ' + p.unit : ''); };
    show();
    input.addEventListener('input', () => {
      show();
      update({params: {...state().params, [p.key]: Number(input.value)}}, {delay: RENDER_DELAY});
    });
    row.append(label, value);
    field.append(row, input);
    $('parameters').append(field);
  }
}

function selectDrawing(id) {
  selected = drawings.find(d => d.id === id) || drawings[0];
  zoom = 1;
  $('subject').value = selected.id;
  for (const control of [$('color-target'), $('part-target')]) {
    control.replaceChildren(new Option('All parts', 'all'), ...selected.parts.map(p => new Option(p.name, p.id)));
  }
  const assembly = selected.parts.length > 1;
  for (const control of ['view', 'view-label', 'spacing-field']) $(control).hidden = !assembly;
  syncControls();
  buildParameterControls();
  updateColorControls();
  render();
  history.replaceState(null, '', '#' + selected.id);
}

function renderZoom(reset = false) {
  const pad = innerWidth <= 740 ? 12 : 24, bar = $('controls').getBoundingClientRect();
  viewport.style.height = Math.max(100, bar.top - 20) + 'px';
  document.documentElement.style.setProperty('--popup-bottom', (innerHeight - bar.top + 12) + 'px');
  const fit = Math.min((viewport.clientWidth - pad * 2) / SHEET.width, (viewport.clientHeight - pad * 2) / SHEET.height);
  const w = SHEET.width * fit * zoom, h = SHEET.height * fit * zoom;
  drawing.style.width = w + 'px';
  drawing.style.height = h + 'px';
  stage.style.width = Math.max(viewport.clientWidth, w + pad * 2) + 'px';
  stage.style.height = Math.max(viewport.clientHeight, h + pad * 2) + 'px';
  $('zoom-level').value = Math.round(zoom * 100) + '%';
  $('zoom-out').disabled = zoom <= .25;
  $('zoom-in').disabled = zoom >= 4;
  if (reset) {
    viewport.scrollLeft = 0;
    viewport.scrollTop = 0;
  }
}

function setZoom(value) {
  const center = [
    (viewport.scrollLeft + viewport.clientWidth / 2) / stage.offsetWidth,
    (viewport.scrollTop + viewport.clientHeight / 2) / stage.offsetHeight
  ];
  zoom = Math.max(.25, Math.min(4, value));
  renderZoom();
  viewport.scrollLeft = center[0] * stage.offsetWidth - viewport.clientWidth / 2;
  viewport.scrollTop = center[1] * stage.offsetHeight - viewport.clientHeight / 2;
}

function fitZoom() {
  zoom = 1;
  renderZoom(true);
}

async function download(format, partOnly = false) {
  if (drawingStatus !== 'ready' || exportBusy) return;
  exportBusy = true;
  updateAvailability();
  const subject = selected, target = structuredClone(state()), ink = structuredClone(colors());
  const crop = partOnly || $('tight-crop').checked, transparent = $('transparent').checked;
  try {
    let source;
    if (partOnly) {
      target.isolated = target.selectedPart;
      const mounted = mountGeometry(await requestGeometry(subject, target), subject, target);
      styleGeometry(mounted.group, target.preset, ink);
      source = mounted.node;
    } else {
      source = svg.cloneNode(true);
    }
    const part = target.isolated !== null ? subject.parts.find(p => String(p.id) === String(target.isolated)) : null;
    const filename = [
      subject.id,
      part ? slug(part.name) : (target.explosion ? 'exploded' : 'assembled'),
      target.preset,
      crop ? 'cropped' : null,
      transparent ? 'transparent' : null
    ].filter(Boolean).join('-');
    const metadata = {
      subject: subject.id, concept: subject.concept !== false, parameters: target.params, explosion: target.explosion,
      linework: target.preset, isolated: target.isolated, colors: ink
    };
    await DrawingExport.save(stripPreviewHooks(source), format, {filename, crop, transparent, metadata});
    announce(format.toUpperCase() + ' saved');
  } catch (error) {
    console.error(error);
    announce('The ' + format.toUpperCase() + ' export failed. Please try again.', true);
  } finally {
    exportBusy = false;
    updateAvailability();
  }
}

for (const [name, color] of palette) {
  const button = document.createElement('button');
  button.className = 'swatch';
  button.style.setProperty('--swatch', color);
  button.dataset.color = color;
  button.setAttribute('aria-label', name);
  button.setAttribute('aria-pressed', 'false');
  button.addEventListener('click', () => setColor(color));
  $('swatches').append(button);
}

$('subject').addEventListener('change', event => selectDrawing(event.target.value));
$('view').addEventListener('change', event => update({explosion: event.target.value === 'assembled' ? 0 : 1}));
$('linework').addEventListener('change', event => update({preset: event.target.value}));
$('explosion').addEventListener('input', event => update({explosion: Number(event.target.value) / 100}, {delay: RENDER_DELAY}));
$('reset-parameters').addEventListener('click', () => {
  update({params: defaultParams(selected)});
  buildParameterControls();
});
$('part-target').addEventListener('change', event => choosePart(event.target.value));
$('isolate-part').addEventListener('click', () => update({isolated: state().selectedPart === 'all' ? null : state().selectedPart}));
$('show-all').addEventListener('click', () => update({isolated: null, selectedPart: 'all'}));
$('color-part').addEventListener('click', () => {
  $('color-target').value = state().selectedPart;
  updateColorControls();
  $('color-panel').showPopover();
});
$('download-part').addEventListener('click', () => download('svg', true));
drawing.addEventListener('click', event => {
  if (drawingStatus === 'rendering') return;
  const part = event.target.closest('[data-item]');
  if (!part) return;
  choosePart(part.dataset.item);
  $('parts-panel').showPopover();
});

$('color-target').addEventListener('change', updateColorControls);
$('custom-color').addEventListener('input', event => setColor(event.target.value));
$('hex-color').addEventListener('change', event => setColor(event.target.value));
$('hex-color').addEventListener('keydown', event => {
  if (event.key !== 'Enter') return;
  setColor(event.target.value);
  event.target.blur();
});
$('color-parts').addEventListener('click', () => editColors(c => {
  selected.parts.forEach((p, i) => { c.parts[p.id] = palette[1 + i % (palette.length - 1)][1]; });
}));
$('reset-colors').addEventListener('click', () => editColors(c => Object.assign(c, defaultInk())));

$('zoom-in').addEventListener('click', () => setZoom(zoom * 1.25));
$('zoom-out').addEventListener('click', () => setZoom(zoom / 1.25));
$('fit').addEventListener('click', fitZoom);
viewport.addEventListener('keydown', event => {
  if (!['+', '=', '-', '0'].includes(event.key)) return;
  event.preventDefault();
  if (event.key === '0') fitZoom();
  else setZoom(event.key === '-' ? zoom / 1.25 : zoom * 1.25);
});

for (const panel of document.querySelectorAll('[popover]')) {
  panel.addEventListener('toggle', () => {
    if (!panel.matches(':popover-open')) return;
    const trigger = $(panel.id.replace('-panel', '-toggle')).getBoundingClientRect();
    panel.style.left = Math.max(12, Math.min(innerWidth - panel.offsetWidth - 12, trigger.right - panel.offsetWidth)) + 'px';
    panel.style.right = 'auto';
  });
}
new ResizeObserver(() => renderZoom()).observe($('controls'));
window.addEventListener('resize', () => renderZoom());

$('tight-crop').addEventListener('change', () => { $('pdf-size').textContent = $('tight-crop').checked ? 'Cropped vector' : 'A3 vector'; });
for (const button of document.querySelectorAll('.export-choice[data-format]')) button.addEventListener('click', () => download(button.dataset.format));

DrawingTheme.subscribe((mode, theme) => {
  $('appearance').value = mode;
  $('theme-toggle').setAttribute('aria-pressed', String(theme === 'dark'));
  $('theme-toggle').title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
});
$('theme-toggle').addEventListener('click', () => DrawingTheme.set(DrawingTheme.theme === 'dark' ? 'light' : 'dark'));
$('appearance').addEventListener('change', event => DrawingTheme.set(event.target.value));

$('subject').replaceChildren(...drawings.map(d => new Option(d.title, d.id)));
selectDrawing(selected.id);
