import type { Architecture, ActivityEvent, Module, Relationship, Constraint } from '../contracts/models.mjs';
import { routeArchitecture } from './routing.mjs';
import * as BirdviewI18n from './i18n.mjs';
import { mountConstraintCanvas, type ConstraintCanvas } from './constraint-canvas.mjs';
import type { ConstraintFreshness, ConstraintGraph } from '../constraint-types.mjs';
declare const DATA: {
  map: Architecture;
  events?: ActivityEvent[];
  icons: Record<string, string>;
  brandLogo: string;
  simulation?: boolean;
  constraintFreshness?: ConstraintFreshness;
  constraintView?: { graph: ConstraintGraph; snapshot: string; scope: string; rules: Array<{ id: string; modules: string[] }> };
};
const { map, icons, brandLogo } = DATA;
function required<T>(value: T | null | undefined): T {
  if (value === null || value === undefined) throw new Error('Missing required viewer data or element.');
  return value;
}
function element<T extends Element>(value: Element | null, ctor: { new(...args: never[]): T }): T {
  if (!(value instanceof ctor)) throw new Error('Unexpected viewer element.');
  return value;
}
function $(id: 'activity-step'): HTMLSelectElement;
function $(id: 'activity-disclosure'): HTMLDetailsElement;
function $(id: 'guide-progress'): HTMLProgressElement;
function $(id: 'connections' | 'overview-connections'): SVGSVGElement;
function $(id: string): HTMLElement;
function $(id: string): HTMLElement | SVGSVGElement {
  const node = document.getElementById(id);
  if (id === 'connections' || id === 'overview-connections') return element(node, SVGSVGElement);
  if (id === 'activity-step') return element(node, HTMLSelectElement);
  if (id === 'activity-disclosure') return element(node, HTMLDetailsElement);
  if (id === 'guide-progress') return element(node, HTMLProgressElement);
  return element(node, HTMLElement);
}
const buttonById = (id: string) => element(document.getElementById(id), HTMLButtonElement);
const query = (selector: string, root: ParentNode = document) => element(root.querySelector(selector), HTMLElement);
const iconMarkup = (name: string) => required(icons[name]);
type Group = NonNullable<Architecture['groups']>[number];
type ViewMode = 'architecture' | 'activity' | 'compare';
type Edge = { path: SVGPathElement; relation: Relationship; dot: SVGCircleElement; animation?: Animation | undefined };

const roles = {
  frontend: { tone: 'blue', icon: 'panels-top-left', label: '前端' },
  backend: { tone: 'teal', icon: 'code', label: '后端' },
  cache: { tone: 'cyan', icon: 'zap', label: '缓存' },
  database: { tone: 'violet', icon: 'database', label: '数据存储' },
  queue: { tone: 'amber', icon: 'list-ordered', label: '任务与队列' },
  security: { tone: 'rose', icon: 'shield-check', label: '安全' },
  generic: { tone: 'slate', icon: 'box', label: '通用模块' }
};
const { uiTranslations } = BirdviewI18n;
const availableLanguages = BirdviewI18n.availableLanguages(map);
let storedLanguage = null;
try { storedLanguage = localStorage.getItem('birdview-language'); } catch {}
const requestedLanguage = new URLSearchParams(location.hash.slice(1)).get('lang');
let language = BirdviewI18n.selectLanguage(map.language, availableLanguages, storedLanguage, requestedLanguage);
const isChinese = () => BirdviewI18n.isChinese(language);
const t = (text: string) => BirdviewI18n.translate(text, language);
function localized(item: { openQuestions: string[]; translations?: Record<string, {openQuestions?: string[]}> }, field: 'openQuestions'): string[];
function localized<K extends BirdviewI18n.TextField>(item: Partial<Record<K, string>> & {translations?: Record<string, Partial<Record<K, string>>>}, field: K): string;
function localized(item: object, field: keyof BirdviewI18n.LocalizedText): string | string[] {
  return BirdviewI18n.localized(item, field, language);
}
const staticLabels: { node: Node; source: string }[] = [];
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
while (walker.nextNode()) {
  const node = walker.currentNode;
  if (node.textContent !== null && Object.hasOwn(uiTranslations, node.textContent)) staticLabels.push({ node, source: node.textContent });
}
const staticAttributes: { node: Element; attr: string; source: string }[] = [];
document.querySelectorAll('[title], [aria-label]').forEach((node) => {
  for (const attr of ['title', 'aria-label']) {
    const source = node.getAttribute(attr);
    if (source !== null && Object.hasOwn(uiTranslations, source)) staticAttributes.push({ node, attr, source });
  }
});
const languageSelect = document.createElement('select');
languageSelect.id = 'language';
languageSelect.setAttribute('aria-label', '语言 / Language');
for (const value of availableLanguages) {
  const option = document.createElement('option');
  option.value = value;
  let label = value;
  try { label = new Intl.DisplayNames([value], { type: 'language' }).of(value) ?? value; } catch {}
  option.textContent = value === 'zh' ? '中文' : value === 'en' ? 'English' : label;
  languageSelect.append(option);
}
query('.header-actions').prepend(languageSelect);
function applyLanguage() {
  document.documentElement.lang = language;
  languageSelect.value = language;
  for (const { node, source } of staticLabels) node.textContent = t(source);
  for (const { node, attr, source } of staticAttributes) node.setAttribute(attr, t(source));
  $('project').textContent = localized(map.project, 'name');
  document.title = `${localized(map.project, 'name')} | Birdview`;
  const count = map.modules.filter((module) => module.status === 'uncertain').length;
  $('uncertainty').textContent = isChinese() ? `${count} 个模块待确认` : `${count} uncertain modules`;
  $('uncertainty').hidden = count === 0;
  flowLabel.title = t('关系方向动画，不代表实时数据传输');
  required(flowLabel.lastChild).textContent = t('流向');
  required(relationView.options[0]).textContent = isChinese() ? '概览' : 'Overview';
  required(relationView.options[1]).textContent = isChinese() ? '全部关系' : 'All relations';
  relationView.setAttribute('aria-label', isChinese() ? '关系显示范围' : 'Relationship visibility');
  themeButton();
  updateActivity();
  roleLegend.replaceChildren();
  for (const key of new Set(map.modules.map((module) => module.role || 'generic'))) {
    const role = roles[key];
    const entry = document.createElement('span');
    entry.dataset.tone = role.tone;
    const icon = document.createElement('span');
    icon.innerHTML = iconMarkup(role.icon);
    entry.append(icon, document.createTextNode(`${t(role.label)} · ${map.modules.filter((module) => (module.role || 'generic') === key).length}`));
    roleLegend.append(entry);
  }
  closeDetails.title = closeDetails.ariaLabel = t('关闭详情');
  showDetails.title = showDetails.ariaLabel = t('查看详情');
  for (const { label, group } of groupFrames) {
    const groupRoles = { interaction: ['交互层', 'Interaction'], runtime: ['运行层', 'Runtime'], 'external-services': ['外部服务', 'External services'], generic: ['通用分组', 'General'] };
    const role = groupRoles[group.role || 'generic'][isChinese() ? 0 : 1];
    label.textContent = `${localized(group, 'name')} · ${role}`;
    label.title = `${label.textContent}\n${group.evidence.map((source) => `${source.path}: ${localized(source, 'note')}`).join('\n')}`;
  }
  for (const module of map.modules) {
    const button = required(buttons.get(module.id));
    const name = query('strong', button);
    name.textContent = localized(module, 'name');
    name.dir = 'auto';
    name.style.fontSize = '13px';
    query('small', button).textContent = localized(module, 'responsibility');
    query('small', button).dir = 'auto';
    button.title = `${localized(module, 'name')}\n${localized(module, 'responsibility')}`;
    button.setAttribute('aria-label', `${localized(module, 'name')}${module.status === 'uncertain' ? `, ${t('待确认')}` : ''}`);
    const mark = button.querySelector<HTMLElement>('.uncertain-mark');
    if (mark) { mark.title = t('待确认'); mark.setAttribute('aria-label', t('待确认')); }
    for (let size = 13; size > 10 && name.scrollHeight > name.clientHeight; size--) name.style.fontSize = `${size - 1}px`;
  }
  for (const { path, relation } of edges) required(path.querySelector('title')).textContent = localized(relation, 'label');
  select(map.modules.find((module) => module.id === selectedModuleId) || required(map.modules[0]));
  if (fitting) updateZoom();
}
languageSelect.onchange = () => {
  language = languageSelect.value;
  try { localStorage.setItem('birdview-language', language); } catch {}
  const hash = new URLSearchParams(location.hash.slice(1));
  hash.set('lang', language);
  try { history.replaceState(null, '', `#${hash}`); } catch {}
  applyLanguage();
};

const brandImage = document.createElement('img');
brandImage.className = 'brand-logo';
brandImage.src = brandLogo;
brandImage.alt = '';
$('brand-icon').replaceChildren(brandImage);
$('project').textContent = map.project.name;
document.title = `${map.project.name} | Birdview`;
$('identity').textContent = `${map.project.id} / ${map.mapId} / v${map.revision}`;
$('uncertainty').textContent = `${map.modules.filter((module) => module.status === 'uncertain').length} 个模块待确认`;
function themeButton() {
  const light = document.documentElement.dataset.theme === 'light';
  $('theme').innerHTML = iconMarkup(light ? 'moon' : 'sun');
  $('theme').title = $('theme').ariaLabel = t(light ? '切换到深色' : '切换到浅色');
}
$('theme').onclick = () => {
  const theme = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
  document.documentElement.dataset.theme = theme;
  try { localStorage.setItem('birdview-theme', theme); } catch {}
  themeButton();
};
themeButton();

// Compact unused grid tracks while preserving authored row/column ordering.
const rows = [...new Set(map.modules.map((module) => module.layout.row))].sort((a, b) => a - b);
const columns = [...new Set(map.modules.map((module) => module.layout.column))].sort((a, b) => a - b);
// Reserve space for all authored relationships, so changing reading mode never
// moves modules. Only crowded boundaries receive extra width/height.
function trackOffsets(tracks: number[], modules: Module[], axis: 'row' | 'column', step: number) {
  const offsets = [0];
  const members = new Map(modules.map(module => [module.id, module]));
  for (let i = 1; i < tracks.length; i++) {
    const boundary = required(tracks[i]);
    const load = map.relationships.filter(relation => {
      const from = members.get(relation.from), to = members.get(relation.to);
      return from && to && Math.min(from.layout[axis], to.layout[axis]) < boundary
        && Math.max(from.layout[axis], to.layout[axis]) >= boundary;
    }).length;
    offsets.push(required(offsets[i - 1]) + step + Math.min(96, Math.max(0, load - 2) * 12));
  }
  return offsets;
}
const columnOffsets = trackOffsets(columns, map.modules, 'column', 220);
const rowOffsets = trackOffsets(rows, map.modules, 'row', 140);
const positions = new Map(map.modules.map(module => [module.id, { x: 28 + required(columnOffsets[columns.indexOf(module.layout.column)]), y: 30 + required(rowOffsets[rows.indexOf(module.layout.row)]) }]));
let width = Math.max(300, required(columnOffsets.at(-1)) + 220);
let height = Math.max(220, required(rowOffsets.at(-1)) + 140);
const groupFrames: {label: HTMLSpanElement; group: Group}[] = [];
const groupLayer = document.createElement('div');
groupLayer.id = 'groups';
$('map').prepend(groupLayer);
if (map.groups?.length) {
  const assigned = new Set(map.groups.flatMap((group) => group.members));
  const ungrouped = map.modules.filter((module) => !assigned.has(module.id));
  let offset = 28;
  const sections: { group?: Group; modules: Module[] }[] = [...map.groups.map((group) => ({ group, modules: map.modules.filter((module) => group.members.includes(module.id)) })), ...(ungrouped.length ? [{ modules: ungrouped }] : [])];
  height = 220;
  for (const section of sections) {
    const sectionRows = [...new Set(section.modules.map((module) => module.layout.row))].sort((a,b) => a-b);
    const sectionColumns = [...new Set(section.modules.map((module) => module.layout.column))].sort((a,b) => a-b);
    const xs = trackOffsets(sectionColumns, section.modules, 'column', 204);
    const ys = trackOffsets(sectionRows, section.modules, 'row', 128);
    const sectionWidth = required(xs.at(-1)) + 220;
    const sectionHeight = required(ys.at(-1)) + 176;
    for (const module of section.modules) positions.set(module.id, { x: offset + 20 + required(xs[sectionColumns.indexOf(module.layout.column)]), y: 70 + required(ys[sectionRows.indexOf(module.layout.row)]) });
    if (section.group) {
      const frame = document.createElement('div');
      frame.className = 'group-frame';
      frame.dataset.role = section.group.role || 'generic';
      Object.assign(frame.style, { left: `${offset}px`, top: '22px', width: `${sectionWidth}px`, height: `${sectionHeight}px` });
      const label = document.createElement('span');
      label.className = 'group-label';
      frame.append(label);
      groupLayer.append(frame);
      groupFrames.push({ label, group: section.group });
    }
    height = Math.max(height, sectionHeight + 44);
    offset += sectionWidth + 44;
  }
  width = offset - 16;
}
$('map').style.width = `${width}px`;
$('map').style.height = `${height}px`;
let zoom = 1;
let fitting = true;
const viewport = query('.map-scroll');
function updateZoom() {
  if (fitting) {
    const availableHeight = Math.max(180, Math.min(viewport.clientHeight - 40, window.innerHeight - viewport.getBoundingClientRect().top - 70));
    zoom = Math.min(1, viewport.clientWidth / width, availableHeight / height);
  }
  $('map').style.transform = `scale(${zoom})`;
  $('map-stage').style.width = `${width * zoom}px`;
  $('map-stage').style.height = `${height * zoom}px`;
  const overview = document.getElementById('overview-map');
  if (overview) {
    overview.style.transform = `scale(${zoom})`;
    $('overview-stage').style.width = `${width * zoom}px`;
    $('overview-stage').style.height = `${height * zoom}px`;
  }
  $('zoom-value').textContent = `${Math.round(zoom * 100)}%`;
  buttonById('zoom-in').disabled = zoom >= 2;
  buttonById('zoom-out').disabled = zoom <= .1;
  $('fit').setAttribute('aria-pressed', String(fitting));
}
for (const [id, icon] of Object.entries({ 'zoom-in': 'zoom-in', 'zoom-out': 'zoom-out', fit: 'maximize', actual: 'scan' })) $(id).innerHTML = icons[icon] || '';
$('zoom-in').onclick = () => { fitting = false; zoom = Math.min(2, zoom + .15); updateZoom(); };
$('zoom-out').onclick = () => { fitting = false; zoom = Math.max(.1, zoom - .15); updateZoom(); };
$('actual').onclick = () => { fitting = false; zoom = 1; updateZoom(); };
$('fit').onclick = () => { fitting = true; updateZoom(); viewport.scrollTo(0, 0); document.getElementById('overview-scroll')?.scrollTo(0, 0); };
new ResizeObserver(() => { if (fitting) updateZoom(); }).observe(viewport);
window.addEventListener('resize', () => { if (fitting) updateZoom(); });
updateZoom();
const svgNS = 'http://www.w3.org/2000/svg';
$('connections').setAttribute('viewBox', `0 0 ${width} ${height}`);
$('connections').style.width = `${width}px`;
$('connections').style.height = `${height}px`;
const defs = document.createElementNS(svgNS, 'defs');
const marker = document.createElementNS(svgNS, 'marker');
for (const [key, value] of Object.entries({ id: 'arrow', viewBox: '0 0 10 10', refX: '9', refY: '5', markerWidth: '6', markerHeight: '6', orient: 'auto-start-reverse' })) marker.setAttribute(key, value);
const arrow = document.createElementNS(svgNS, 'path');
arrow.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
arrow.setAttribute('fill', '#809487');
marker.append(arrow);
defs.append(marker);
$('connections').append(defs);
const edges: Edge[] = [];
let selectedModuleId: string | undefined;
let hoveredModuleId: string | undefined;
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const flowLabel = document.createElement('label');
flowLabel.className = 'flow-toggle';
flowLabel.title = '关系方向动画，不代表实时数据传输';
const flowToggle = document.createElement('input');
flowToggle.type = 'checkbox';
flowToggle.checked = true;
flowToggle.id = 'flow-toggle';
flowLabel.append(flowToggle, document.createTextNode('流向'));
query('.map-tools').prepend(flowLabel);
const relationView = document.createElement('select');
relationView.id = 'relation-view';
relationView.add(new Option('', 'overview'));
relationView.add(new Option('', 'all'));
relationView.value = 'overview';
const relationCount = document.createElement('span');
relationCount.id = 'relation-count';
relationCount.setAttribute('aria-live', 'polite');
query('.map-tools').prepend(relationView, relationCount);
relationView.onchange = () => { hoveredModuleId = undefined; updateFlow(); };
function updateFlow() {
  const activeModuleId = hoveredModuleId;
  const activeButton = activeModuleId ? buttons.get(activeModuleId) : undefined;
  const accent = activeButton ? getComputedStyle(activeButton).getPropertyValue('--node-accent').trim() : 'var(--mint)';
  const neighbors = new Set([activeModuleId]);
  for (const relation of map.relationships) {
    if (relation.from === activeModuleId || relation.to === activeModuleId) {
      neighbors.add(relation.from); neighbors.add(relation.to);
    }
  }
  for (const [id, button] of buttons) {
    button.classList.toggle('flow-hover', id === activeModuleId);
    button.classList.toggle('context-muted', Boolean(activeModuleId) && !neighbors.has(id));
  }
  $('connections').style.setProperty('--flow-accent', accent);
  let visibleCount = 0;
  for (const edge of edges) {
    edge.path.classList.toggle('relevant', edge.relation.from === activeModuleId || edge.relation.to === activeModuleId);
    const relevant = edge.path.classList.contains('relevant');
    const visible = relationView.value === 'all' || edge.relation.visibility === 'overview' || relevant || edge.path.classList.contains('constraint-highlight');
    edge.path.style.display = visible ? '' : 'none';
    edge.path.classList.toggle('context-muted', Boolean(activeModuleId) && !relevant);
    if (visible) visibleCount++;
    const active = visible && flowToggle.checked && !reducedMotion.matches && !document.hidden && relevant;
    edge.dot.style.display = active ? '' : 'none';
    if (!active) {
      edge.animation?.cancel();
      edge.animation = undefined;
      continue;
    }
    if (edge.animation) continue;
    // Sample the existing path so the moving marker follows every routing shape.
    const length = edge.path.getTotalLength();
    const frames = Array.from({ length: 61 }, (_, index) => {
      const point = edge.path.getPointAtLength(length * index / 60);
      return { transform: `translate(${point.x}px, ${point.y}px)` };
    });
    // A shared traversal time makes longer connections move faster and arrive
    // together. This illustrates direction, not measured transport latency.
    edge.animation = edge.dot.animate(frames, { duration: 1600, iterations: Infinity, easing: 'linear' });
  }
  relationCount.textContent = isChinese() ? `显示 ${visibleCount}/${edges.length} 条关系` : `${visibleCount}/${edges.length} relations shown`;
  relationCount.title = isChinese() ? '悬浮模块可临时显示其全部直接关系' : 'Hover a module to reveal all its direct relationships';
  for (const module of map.modules) {
    const button = required(buttons.get(module.id));
    const badge = query('.hidden-relations', button);
    const count = edges.filter(edge => edge.path.style.display === 'none' &&
      (edge.relation.from === module.id || edge.relation.to === module.id)).length;
    const hint = isChinese() ? `还有 ${count} 条直接关系未显示` : `${count} more direct relationships hidden`;
    badge.hidden = count === 0;
    badge.textContent = count ? `+${count}` : '';
    badge.title = hint;
    button.setAttribute('aria-label', `${localized(module, 'name')}${module.status === 'uncertain' ? `, ${t('待确认')}` : ''}${count ? `, ${hint}` : ''}`);
  }
  syncOverview();
}
flowToggle.onchange = updateFlow;
reducedMotion.addEventListener('change', updateFlow);
document.addEventListener('visibilitychange', updateFlow);

const routedConnections = routeArchitecture(map.relationships, positions);
for (const [relationIndex, relation] of map.relationships.entries()) {
  const path = document.createElementNS(svgNS, 'path');
  const { d } = required(routedConnections[relationIndex]);
  path.setAttribute('d', d);
  path.setAttribute('class', 'edge');
  path.setAttribute('marker-end', 'url(#arrow)');
  if (relation.status === 'uncertain') path.setAttribute('stroke-dasharray', '5 4');
  const title = document.createElementNS(svgNS, 'title');
  title.textContent = relation.label;
  path.append(title);
  $('connections').append(path);
  const dot = document.createElementNS(svgNS, 'circle');
  dot.setAttribute('r', '3');
  dot.setAttribute('class', 'flow-dot');
  dot.setAttribute('aria-hidden', 'true');
  dot.style.display = 'none';
  $('connections').append(dot);
  edges.push({ path, relation, dot });
}
const buttons = new Map<string, HTMLButtonElement>();
for (const module of map.modules) {
  const button = document.createElement('button');
  button.className = 'node';
  const hiddenRelations = document.createElement('span');
  hiddenRelations.className = 'hidden-relations';
  hiddenRelations.hidden = true;
  hiddenRelations.setAttribute('aria-hidden', 'true');
  button.append(hiddenRelations);
  button.dataset.module = module.id;
  button.dataset.kind = module.kind;
  const role = roles[module.role || 'generic'];
  button.dataset.tone = role.tone;
  button.style.left = `${required(positions.get(module.id)).x}px`;
  button.style.top = `${required(positions.get(module.id)).y}px`;
  button.setAttribute('aria-label', module.name);
  const icon = document.createElement('span');
  icon.className = 'node-top';
  icon.innerHTML = iconMarkup(role.icon);
  const name = document.createElement('strong');
  name.textContent = module.name;
  const status = document.createElement('small');
  status.textContent = module.responsibility;
  button.title = `${module.name}\n${module.responsibility}`;
  button.append(icon, name, status);
  if (module.status === 'uncertain') {
    const mark = document.createElement('span');
    mark.className = 'uncertain-mark';
    mark.textContent = '?';
    mark.title = '待确认';
    mark.setAttribute('aria-label', '待确认');
    button.append(mark);
    button.setAttribute('aria-label', `${module.name}，待确认`);
  }
  button.onclick = () => {
    if (constraintPanelOpen) { constraintFilter = 'module'; selectedConstraintId = undefined; }
    select(module); setInspector(true);
  };
  button.onpointerenter = (event) => {
    if (event.pointerType === 'touch') return;
    hoveredModuleId = module.id;
    updateFlow();
  };
  button.onpointerleave = () => {
    if (hoveredModuleId !== module.id) return;
    hoveredModuleId = undefined;
    updateFlow();
  };
  $('nodes').append(button);
  for (let size = 13; size > 10 && name.scrollHeight > name.clientHeight; size--) name.style.fontSize = `${size - 1}px`;
  buttons.set(module.id, button);
}
const moduleMeta = document.createElement('div');
const roleLegend = document.createElement('div');
roleLegend.className = 'role-legend';
query('.legend').prepend(roleLegend);
moduleMeta.className = 'module-meta';
$('module-name').after(moduleMeta);
const workspace = query('.workspace');
const inspector = query('aside');
// Keyboard actions stay immediate; pointer openings may use a short reveal.
document.addEventListener('pointerdown', () => { document.documentElement.dataset.motionInput = 'pointer'; }, true);
document.addEventListener('keydown', () => { document.documentElement.dataset.motionInput = 'keyboard'; }, true);
const closeDetails = document.createElement('button');
closeDetails.id = 'close-details';
closeDetails.innerHTML = iconMarkup('x');
inspector.prepend(closeDetails);
const showDetails = document.createElement('button');
showDetails.id = 'show-details';
showDetails.innerHTML = icons['panel-right'] || '';
query('.map-tools').append(showDetails);
function setInspector(open: boolean) {
  workspace.classList.toggle('inspector-open', open);
  showDetails.setAttribute('aria-expanded', String(open));
  updateConstraints();
  if (fitting) updateZoom();
}
closeDetails.onclick = () => { setInspector(false); showDetails.focus(); };
showDetails.onclick = () => setInspector(!workspace.classList.contains('inspector-open'));
inspector.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeDetails.click(); });
function select(module: Module) {
  selectedModuleId = module.id;
  for (const [id, button] of buttons) {
    button.classList.toggle('selected', id === module.id);
    button.setAttribute('aria-pressed', String(id === module.id));
  }
  $('module-name').textContent = localized(module, 'name');
  moduleMeta.textContent = `${t(roles[module.role || 'generic'].label)} · ${t(module.kind === 'external' ? '外部服务' : '本地模块')} · ${t(module.status === 'uncertain' ? '待确认' : '有来源证据')}`;
  $('responsibility').textContent = localized(module, 'responsibility');
  $('ownership').replaceChildren();
  for (const owner of module.ownership) {
    const li = document.createElement('li');
    li.textContent = owner.path;
    $('ownership').append(li);
  }
  if (!module.ownership.length) $('ownership').textContent = t('无本地文件归属');
  $('evidence').textContent = module.evidence.map((item) => `${item.path}${item.line ? `:${item.line}` : ''}${item.symbol ? ` · ${item.symbol}` : ''}\n${localized(item, 'note')}`).join('\n\n') || t('无来源证据');
  $('questions').textContent = localized(module, 'openQuestions').join('\n') || t('无已记录的待确认项');
  $('relations').replaceChildren();
  for (const { path, relation } of edges) {
    const relevant = relation.from === module.id || relation.to === module.id;
    path.classList.toggle('relevant', relevant);
    if (!relevant) continue;
    const li = document.createElement('li');
    const title = document.createElement('strong');
    title.textContent = `${localized(required(map.modules.find((item) => item.id === relation.from)), 'name')} → ${localized(required(map.modules.find((item) => item.id === relation.to)), 'name')}`;
    const label = document.createElement('span');
    label.textContent = [localized(relation, 'label'), ...relation.evidence.map((item) => `${item.path}${item.line ? `:${item.line}` : ''} · ${localized(item, 'note')}`), ...localized(relation, 'openQuestions')].join(' · ');
    li.append(title, label);
    $('relations').append(li);
  }
  if (!$('relations').children.length) $('relations').textContent = t('无已记录的关系');
  updateConstraints();
  updateFlow();
}
const activityEvents = DATA.events || [];
let activityIndex = DATA.simulation ? 0 : Math.max(0, activityEvents.length - 1);
let activityMode: ViewMode = activityEvents.length ? 'activity' : 'architecture';
const activityPanel = document.createElement('section');
activityPanel.className = 'activity-panel';
activityPanel.hidden = !activityEvents.length;
activityPanel.innerHTML = '<div class="activity-toolbar"><div id="activity-mode" role="group"></div><span id="activity-source"></span><div class="activity-history"><button id="activity-prev"></button><select id="activity-step"></select><button id="activity-next"></button><button id="activity-latest"></button></div></div><div id="activity-summary" aria-live="polite"></div><details id="activity-disclosure"><summary></summary><div id="activity-details"></div></details>';
query('.workspace').before(activityPanel);
const mapHeading = query('.map-heading');
new ResizeObserver(() => workspace.style.setProperty('--toolbar-height', `${mapHeading.offsetHeight}px`)).observe(mapHeading);
const mapTools = query('.map-tools');
const relationTools = document.createElement('div');
relationTools.className = 'relation-tools';
relationTools.append(relationView, flowLabel);
const zoomTools = document.createElement('div');
zoomTools.className = 'zoom-tools';
$('actual').replaceChildren($('zoom-value'));
zoomTools.append($('zoom-out'), $('actual'), $('zoom-in'), $('fit'));
mapTools.replaceChildren(relationTools, zoomTools, showDetails);
if (activityEvents.length) {
  element(mapHeading.firstElementChild, HTMLElement).hidden = true;
  mapHeading.prepend($('activity-mode'));
}
required(query('.legend').lastElementChild).before(relationCount);
query('.activity-toolbar', activityPanel).append($('activity-summary'));
const viewModes: Record<ViewMode, [string, string, string]> = { architecture: ['完整架构', 'Architecture', 'layers'], activity: ['更改视图', 'Changes', 'focus'], compare: ['并排对照', 'Compare', 'columns-2'] };
for (const [mode, labels] of Object.entries(viewModes)) {
  const button = document.createElement('button');
  button.type = 'button';
  button.dataset.view = mode;
  button.innerHTML = `${icons[labels[2]] || ''}<span>${labels[0]}</span>`;
  button.onclick = () => { if (mode !== 'architecture' && mode !== 'activity' && mode !== 'compare') throw new Error('Unknown view mode.'); activityMode = mode; hoveredModuleId = undefined; updateActivity(); updateFlow(); };
  $('activity-mode').append(button);
}
const activityStep = $('activity-step');
const phaseNames = { planned: ['计划', 'Planned'], editing: ['修改', 'Editing'], verifying: ['验证', 'Verifying'], completed: ['结束', 'Completed'], failed: ['失败', 'Failed'], cancelled: ['取消', 'Cancelled'] };
for (const [id, icon] of Object.entries({ 'activity-prev': 'chevron-left', 'activity-next': 'chevron-right', 'activity-latest': 'skip-forward' })) $(id).innerHTML = iconMarkup(icon);
activityStep.onchange = () => { activityIndex = Number(activityStep.value); updateActivity(); };
$('activity-prev').onclick = () => { activityIndex = Math.max(0, activityIndex - 1); updateActivity(); };
$('activity-next').onclick = () => { activityIndex = Math.min(activityEvents.length - 1, activityIndex + 1); updateActivity(); };
$('activity-latest').onclick = () => { activityIndex = activityEvents.length - 1; updateActivity(); };
$('activity-disclosure').ontoggle = () => { if (fitting) updateZoom(); };

// Share authored positions and routes; only the right pane gets activity emphasis.
const mapPanes = document.createElement('div');
mapPanes.className = 'map-panes';
viewport.before(mapPanes);
const changePane = document.createElement('section');
changePane.className = 'map-pane';
changePane.innerHTML = '<h2 class="pane-title" id="change-title"></h2>';
changePane.append(viewport);
mapPanes.append(changePane);
if (activityEvents.length) {
  const overviewPane = document.createElement('section');
  overviewPane.id = 'overview-pane';
  overviewPane.className = 'map-pane';
  overviewPane.hidden = true;
  overviewPane.innerHTML = '<h2 class="pane-title" id="overview-title"></h2><div class="map-scroll" id="overview-scroll"><div id="overview-stage"></div></div>';
  mapPanes.prepend(overviewPane);
  const clone = $('map').cloneNode(true);
  if (!(clone instanceof HTMLElement)) throw new Error('Invalid map clone.');
  const overview = clone;
  for (const element of [overview, ...overview.querySelectorAll('[id]')]) element.id = `overview-${element.id}`;
  overview.querySelectorAll('[marker-end]').forEach(edge => edge.setAttribute('marker-end', 'url(#overview-arrow)'));
  overview.querySelectorAll('.flow-dot').forEach(dot => dot.remove());
  $('overview-stage').append(overview);
  overview.querySelectorAll<HTMLButtonElement>('.node').forEach(button => {
    button.onclick = () => {
      if (constraintPanelOpen) { constraintFilter = 'module'; selectedConstraintId = undefined; }
      select(required(map.modules.find(module => module.id === button.dataset.module))); setInspector(true);
    };
    button.onpointerenter = event => { if (event.pointerType !== 'touch') { hoveredModuleId = button.dataset.module; updateFlow(); } };
    button.onpointerleave = () => { hoveredModuleId = undefined; updateFlow(); };
  });
  for (const [source, destination] of [[viewport, $('overview-scroll')], [$('overview-scroll'), viewport]] as const) {
    source.addEventListener('scroll', () => {
      if (activityMode !== 'compare') return;
      if (destination.scrollLeft !== source.scrollLeft) destination.scrollLeft = source.scrollLeft;
      if (destination.scrollTop !== source.scrollTop) destination.scrollTop = source.scrollTop;
    });
  }
}
for (const scroll of mapPanes.querySelectorAll<HTMLElement>('.map-scroll')) {
  scroll.tabIndex = 0;
  let pan: {x: number; y: number; left: number; top: number} | undefined;
  scroll.addEventListener('pointerdown', event => {
    if (event.button !== 0 || event.pointerType === 'touch' || (event.target instanceof Element && event.target.closest('button'))) return;
    pan = { x: event.clientX, y: event.clientY, left: scroll.scrollLeft, top: scroll.scrollTop };
    scroll.setPointerCapture(event.pointerId);
  });
  scroll.addEventListener('pointermove', event => {
    if (!pan) return;
    scroll.scrollLeft = pan.left + pan.x - event.clientX;
    scroll.scrollTop = pan.top + pan.y - event.clientY;
  });
  scroll.addEventListener('lostpointercapture', () => { pan = undefined; });
  scroll.addEventListener('pointerup', event => { pan = undefined; if (scroll.hasPointerCapture(event.pointerId)) scroll.releasePointerCapture(event.pointerId); });
}

function syncOverview() {
  const overview = document.getElementById('overview-map');
  if (!overview) return;
  for (const button of overview.querySelectorAll<HTMLButtonElement>('.node')) {
    const source = required(buttons.get(required(button.dataset.module)));
    button.className = source.className;
    button.classList.remove('activity-outside', 'activity-scope', 'activity-target', 'context-muted');
    for (const attr of ['title', 'aria-label', 'aria-pressed']) {
      if (source.hasAttribute(attr)) button.setAttribute(attr, required(source.getAttribute(attr)));
    }
    if (button.innerHTML !== source.innerHTML) button.innerHTML = source.innerHTML;
  }
  overview.querySelectorAll<HTMLElement>('.group-label').forEach((label, index) => {
    label.textContent = required(groupFrames[index]).label.textContent;
    label.title = required(groupFrames[index]).label.title;
  });
  overview.querySelectorAll<SVGPathElement>('.edge').forEach((edge, index) => {
    edge.setAttribute('class', required(edges[index]).path.getAttribute('class') ?? '');
    edge.classList.remove('activity-edge-outside', 'context-muted');
    edge.style.display = required(edges[index]).path.style.display;
    required(edge.querySelector('title')).textContent = required(required(edges[index]).path.querySelector('title')).textContent;
  });
  $('overview-connections').style.setProperty('--flow-accent', $('connections').style.getPropertyValue('--flow-accent'));
}

function updateActivity() {
  const zh = isChinese();
  updateConstraints();
  document.body.classList.toggle('show-activity-context', activityMode === 'activity');
  $('change-title').textContent = viewModes[activityMode === 'architecture' ? 'architecture' : 'activity'][zh ? 0 : 1];
  viewport.setAttribute('aria-label', $('change-title').textContent);
  if (!activityEvents.length) return;
  const event = required(activityEvents[activityIndex]);
  const active = activityMode !== 'architecture';
  const context = $('activity-context');
  // View-state policy: only the changes view owns activity history controls.
  query('.activity-toolbar', activityPanel).hidden = activityMode !== 'activity';
  const terminalPhase = ['completed', 'failed', 'cancelled'].includes(event.phase);
  const targetLabel = terminalPhase ? (zh ? '无当前目标' : 'No current targets') : event.phase === 'planned' ? (zh ? '下一步目标' : 'Next-step targets') : event.phase === 'verifying' ? (zh ? '验证目标' : 'Verification targets') : (zh ? '修改目标' : 'Edit targets');
  mapPanes.classList.toggle('compare', activityMode === 'compare');
  $('overview-pane').hidden = activityMode !== 'compare';
  $('overview-title').textContent = viewModes.architecture[zh ? 0 : 1];
  $('overview-scroll').setAttribute('aria-label', $('overview-title').textContent);
  $('activity-mode').setAttribute('aria-label', zh ? '视图' : 'View');
  for (const button of $('activity-mode').querySelectorAll<HTMLButtonElement>('button')) {
    const mode = button.dataset.view;
    const labels = mode === 'activity' || mode === 'compare' ? viewModes[mode] : viewModes.architecture;
    query('span', button).textContent = required(labels[zh ? 0 : 1]) || labels[0];
    button.setAttribute('aria-pressed', String(button.dataset.view === activityMode));
  }
  activityStep.setAttribute('aria-label', zh ? '活动历史' : 'Activity history');
  activityStep.replaceChildren(...activityEvents.map((record, index) => new Option(`${record.sequence} · ${record.taskId} · ${phaseNames[record.phase][zh ? 0 : 1]}`, String(index))));
  activityStep.value = String(activityIndex);
  for (const [id, labels] of Object.entries({ 'activity-prev': ['上一条', 'Previous record'], 'activity-next': ['下一条', 'Next record'], 'activity-latest': ['最新记录', 'Latest record'] })) $(id).title = $(id).ariaLabel = required(labels[zh ? 0 : 1]);
  buttonById('activity-prev').disabled = activityIndex === 0;
  buttonById('activity-next').disabled = buttonById('activity-latest').disabled = activityIndex === activityEvents.length - 1;
  const source = DATA.simulation ? (zh ? '模拟活动 · 非真实执行' : 'Simulation · no real execution') : (zh ? 'Agent 声明 · 文件快照' : 'Agent-declared · file snapshot');
  $('activity-source').hidden = false;
  $('activity-source').textContent = source;
  query('header .simulation').textContent = source;
  const names = (ids: string[]) => ids.map(id => localized(required(map.modules.find(module => module.id === id)), 'name')).join(', ');
  $('activity-summary').textContent = localized(event, 'reason');
  $('activity-context-label').textContent = zh ? '当前修改' : 'Current change';
  $('activity-context-summary').textContent = localized(event, 'reason');
  const contextDetails = $('activity-context-details');
  contextDetails.replaceChildren();
  query('summary', $('activity-disclosure')).textContent = `${targetLabel}${terminalPhase ? '' : ` · ${event.targets.length}`} · ${zh ? '详情' : 'Details'}`;
  const details = $('activity-details');
  details.replaceChildren();
  const fields: [string, string][] = [
    [zh ? '计划范围' : 'Planned scope', names(event.scope)],
    [targetLabel, terminalPhase ? '-' : names(event.targets)],
    [zh ? '本步骤文件（声明）' : 'Step files (declared)', event.files.join('\n') || '-'],
    [zh ? '未归属文件' : 'Unmapped files', event.unmappedFiles.join('\n') || '-'],
    [zh ? '验证记录' : 'Checks', event.checks.map(check => `${check.command}\n${check.status} · exit ${check.exitCode ?? '-'} · ${localized(check, 'summary')}`).join('\n\n') || (zh ? '未记录验证结果' : 'No checks recorded')]
  ];
  for (const [label, value] of fields) {
    const field = document.createElement('div');
    const heading = document.createElement('strong'); heading.textContent = label;
    const content = document.createElement('div'); content.textContent = value;
    field.append(heading, content); details.append(field);
  }
  const contextFields: [string, string][] = [
    [targetLabel, terminalPhase ? '-' : names(event.targets)],
    [zh ? '计划范围' : 'Planned scope', names(event.scope)],
    [zh ? '文件' : 'Files', event.files.join('\n') || '-'],
    [zh ? 'Git 提交' : 'Git commit', event.gitCommit || '-'],
    [zh ? '发生时间' : 'Timestamp', ('timestamp' in event && typeof event.timestamp === 'string' ? event.timestamp : '') || '-'],
    [zh ? '验证' : 'Checks', event.checks.map(check => `${check.status} · ${localized(check, 'summary')}`).join('\n') || (zh ? '未记录' : 'Not recorded')]
  ];
  for (const [label, value] of contextFields) {
    const field = document.createElement('div');
    const heading = document.createElement('strong'); heading.textContent = label;
    const content = document.createElement('div'); content.textContent = value;
    field.append(heading, content); contextDetails.append(field);
  }
  context.hidden = activityMode !== 'activity';
  $('activity-summary').hidden = $('activity-disclosure').hidden = activityMode !== 'activity';
  for (const [id, button] of buttons) {
    const target = !terminalPhase && event.targets.includes(id);
    button.classList.toggle('activity-outside', active && !target);
    button.classList.toggle('activity-scope', active && event.scope.includes(id));
    button.classList.toggle('activity-target', active && target);
  }
  for (const edge of edges) edge.path.classList.toggle('activity-edge-outside', active &&
    (terminalPhase || !event.targets.includes(edge.relation.from) && !event.targets.includes(edge.relation.to)));
  const legend = required(query('.legend').lastElementChild);
  legend.replaceChildren();
  if (active) {
    for (const [kind, label] of [['planned', zh ? '计划范围' : 'Planned scope'], ['active', targetLabel], ['', zh ? '非当前目标' : 'Other modules']] as const) {
      const entry = document.createElement('span');
      const swatch = document.createElement('i'); swatch.className = kind;
      entry.append(swatch, document.createTextNode(label)); legend.append(entry);
    }
  } else legend.textContent = source;
  syncOverview();
  updateZoom();
  if (activityMode === 'compare') $('overview-scroll').scrollTo(viewport.scrollLeft, viewport.scrollTop);
}

const constraintRules = map.constraints || [];
let constraintPanelOpen = false;
let selectedConstraintId: string | undefined;
let constraintFilter = 'applicable';
const constraintText = (zh: string, en: string) => isChinese() ? zh : en;
const freshnessStates: Record<'unchanged' | 'changed' | 'missing' | 'unverified', [string, string]> = {
  unchanged: ['关联文件未变', 'Linked files unchanged'], changed: ['待复核', 'Needs review'],
  missing: ['文件缺失', 'File missing'], unverified: ['未核对变化', 'Changes not checked']
};
const constraintStates: Record<Constraint['applicability'] | 'unverified' | 'supported' | 'violated', [string, string]> = {
  applicable: ['适用', 'Applicable'], superseded: ['已被覆盖', 'Superseded'],
  'not-applicable': ['不适用', 'Not applicable'], uncertain: ['待确认', 'Uncertain'], conflict: ['冲突', 'Conflict'],
  unverified: ['未验证', 'Unverified'], supported: ['有证据支持', 'Evidence-supported'], violated: ['不满足', 'Not satisfied']
};
const constraintButton = document.createElement('button');
constraintButton.id = 'show-constraints';
constraintButton.setAttribute('aria-controls', 'constraints-panel');
mapTools.append(constraintButton);
const moduleContent = document.createElement('div');
moduleContent.id = 'module-content';
moduleContent.append(...[...inspector.children].filter(child => child !== closeDetails));
inspector.append(moduleContent);
const moduleConstraints = document.createElement('section');
moduleConstraints.id = 'module-constraints';
moduleConstraints.className = 'detail';
moduleContent.append(moduleConstraints);
const constraintsPanel = document.createElement('section');
constraintsPanel.id = 'constraints-panel';
constraintsPanel.hidden = true;
inspector.append(constraintsPanel);
constraintButton.onclick = () => {
  constraintPanelOpen = !(constraintPanelOpen && workspace.classList.contains('inspector-open'));
  selectedConstraintId = undefined;
  setInspector(constraintPanelOpen);
  if (constraintPanelOpen) constraintsPanel.querySelector('select')?.focus();
};
showDetails.onclick = () => {
  const open = constraintPanelOpen || !workspace.classList.contains('inspector-open');
  constraintPanelOpen = false;
  selectedConstraintId = undefined;
  setInspector(open);
};
closeDetails.onclick = () => {
  setInspector(false);
  (constraintPanelOpen ? constraintButton : showDetails).focus();
};
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && workspace.classList.contains('inspector-open') && !document.querySelector('dialog[open]')) closeDetails.click();
});

function constraintModules(rule: Constraint) {
  return new Set([...rule.modules, ...map.relationships.filter(relation => rule.relationships.includes(relation.id)).flatMap(relation => [relation.from, relation.to])]);
}

function constraintApplies(rule: Constraint, event: ActivityEvent | undefined) {
  if (rule.applicability !== 'applicable') return false;
  if (rule.scope === 'task') return event?.taskId === rule.taskId;
  return !event || rule.scope === 'project' || [...constraintModules(rule)].some(id => event.scope.includes(id));
}

function updateConstraints() {
  const event = activityMode === 'architecture' ? undefined : activityEvents[activityIndex];
  const applicable = constraintRules.filter(rule => constraintApplies(rule, event));
  const open = constraintPanelOpen && workspace.classList.contains('inspector-open');
  constraintButton.innerHTML = iconMarkup('shield-check');
  const buttonLabel = document.createElement('span');
  const discoveryRecorded = !!map.constraintDiscovery;
  const emptyState = DATA.constraintView
    ? constraintText('约束图已整理规则；此处尚未记录架构关联。', 'Rules are available in the constraint graph; architecture links are not recorded here.')
    : discoveryRecorded
      ? constraintText('已记录来源检查，但尚无整理后的架构规则；不代表没有约束。', 'Source inspection recorded, but no architecture rules curated; this does not mean there are no constraints.')
      : constraintText('尚未记录本地约束扫描，不能判断是否存在适用约束。', 'Local constraint discovery is not recorded; applicable constraints are unknown.');
  buttonLabel.textContent = constraintRules.length
    ? `${constraintText('适用约束', 'Applicable constraints')} · ${applicable.length}`
    : DATA.constraintView ? constraintText('约束 · 未关联', 'Constraints · Unlinked')
      : discoveryRecorded ? constraintText('约束 · 待整理', 'Constraints · Pending review')
        : constraintText('约束 · 未扫描', 'Constraints · Not scanned');
  constraintButton.append(buttonLabel);
  const attention = constraintRules.filter(rule => ['uncertain', 'conflict'].includes(rule.applicability)).length;
  if (attention) {
    const count = document.createElement('span');
    count.className = 'constraint-attention-count';
    count.textContent = String(attention);
    count.title = constraintText(`${attention} 条待确认或冲突规则`, `${attention} uncertain or conflicting rules`);
    count.ariaLabel = count.title;
    constraintButton.append(count);
  }
  constraintButton.title = constraintButton.ariaLabel = constraintText('查看约束与来源', 'Inspect constraints and sources');
  constraintButton.setAttribute('aria-expanded', String(open));
  workspace.classList.toggle('constraints-open', open);
  moduleContent.hidden = constraintPanelOpen;
  constraintsPanel.hidden = !constraintPanelOpen;
  moduleConstraints.replaceChildren();
  const moduleHeading = document.createElement('div');
  moduleHeading.className = 'field-label';
  moduleHeading.textContent = constraintText('适用约束', 'Applicable constraints');
  moduleConstraints.append(moduleHeading);
  const moduleRules = applicable.filter(rule => ['project', 'task'].includes(rule.scope) || constraintModules(rule).has(selectedModuleId ?? ''));
  for (const rule of moduleRules) {
    const button = document.createElement('button');
    button.className = 'constraint-module-link';
    button.textContent = localized(rule, 'name');
    button.onclick = () => {
      selectedConstraintId = rule.id; constraintPanelOpen = true; setInspector(true);
      constraintsPanel.querySelector<HTMLButtonElement>(`[data-constraint="${rule.id}"]`)?.focus();
    };
    moduleConstraints.append(button);
  }
  if (!moduleRules.length) {
    const empty = document.createElement('p');
    empty.textContent = constraintRules.length ? constraintText('此模块未记录适用约束', 'No applicable constraints recorded for this module') : emptyState;
    moduleConstraints.append(empty);
  }
  constraintsPanel.replaceChildren();
  const eyebrow = document.createElement('div');
  eyebrow.className = 'eyebrow';
  eyebrow.textContent = constraintText('规则与依据', 'RULES & EVIDENCE');
  const heading = document.createElement('h2');
  heading.textContent = constraintText('约束', 'Constraints');
  const context = document.createElement('p');
  context.className = 'constraint-context';
  context.textContent = event ? `${event.taskId} · ${constraintText('步骤', 'Step')} ${event.sequence}` : constraintText('项目架构快照', 'Project architecture snapshot');
  constraintsPanel.append(eyebrow, heading, context);
  const freshness = DATA.constraintFreshness;
  const snapshot = document.createElement('div');
  snapshot.className = 'constraint-snapshot';
  const snapshotTitle = document.createElement('strong');
  const pending = constraintRules.filter(rule => freshness?.rules[rule.id]?.status === 'changed').length;
  const unchecked = constraintRules.filter(rule => !freshness?.rules[rule.id] || freshness.rules[rule.id]?.status === 'unverified').length;
  snapshotTitle.textContent = freshness
    ? constraintText(`${pending} 条待复核 · ${unchecked} 条未核对`, `${pending} need review · ${unchecked} unchecked`)
    : constraintText('尚未核对关联文件变化', 'Linked file changes not yet checked');
  const snapshotNote = document.createElement('p');
  snapshotNote.textContent = freshness
    ? `${constraintText('文件变化快照', 'File change snapshot')} · ${freshness.checkedAt}\n${constraintText('检测提交', 'Inspected commit')} ${freshness.head.slice(0, 12)}\n${constraintText('包含当时的暂存区与工作区；不代表当前状态或合规结论。', 'Includes the index and working tree at inspection; not a live status or compliance verdict.')}`
    : constraintText('适用性、文件变化与验证结果分别记录。', 'Applicability, file changes and verification are recorded separately.');
  snapshot.append(snapshotTitle, snapshotNote); constraintsPanel.append(snapshot);
  const discovery = document.createElement('details');
  discovery.className = 'constraint-discovery';
  const discoverySummary = document.createElement('summary');
  discoverySummary.textContent = map.constraintDiscovery
    ? `${constraintText('已检查', 'Inspected')} ${map.constraintDiscovery.checkedPaths.length} · ${constraintText('未检查', 'Uninspected')} ${map.constraintDiscovery.uninspectedPaths.length}`
    : constraintText('未记录本地约束检查', 'Local constraint discovery not recorded');
  discovery.append(discoverySummary);
  if (map.constraintDiscovery) {
    const details = document.createElement('p');
    details.textContent = `${map.constraintDiscovery.checkedAt}\n${constraintText('已检查', 'Inspected')}: ${map.constraintDiscovery.checkedPaths.join(', ') || '—'}\n${constraintText('未检查', 'Uninspected')}: ${map.constraintDiscovery.uninspectedPaths.join(', ') || '—'}`;
    discovery.append(details);
  }
  constraintsPanel.append(discovery);
  const filter = document.createElement('select');
  filter.id = 'constraint-filter';
  filter.ariaLabel = constraintText('约束筛选', 'Filter constraints');
  for (const [value, zh, en] of [['applicable', '本次适用', 'Applicable'], ['module', '选中模块', 'Selected module'], ['review', '变化待复核', 'Changes needing review'], ['attention', '待确认与冲突', 'Uncertain & conflicting'], ['all', '全部规则', 'All rules']] as const) filter.add(new Option(constraintText(zh, en), value));
  filter.value = constraintFilter;
  filter.onchange = () => { constraintFilter = filter.value; selectedConstraintId = undefined; updateConstraints(); $('constraint-filter').focus(); };
  constraintsPanel.append(filter);
  const visible = constraintRules.filter(rule => constraintFilter === 'all' ||
    (constraintFilter === 'review' ? freshness?.rules[rule.id]?.status === 'changed' : constraintFilter === 'attention' ? ['uncertain', 'conflict'].includes(rule.applicability) :
      constraintFilter === 'module' ? applicable.includes(rule) && (['project', 'task'].includes(rule.scope) || constraintModules(rule).has(selectedModuleId ?? '')) : applicable.includes(rule)));
  const selected = constraintRules.find(rule => rule.id === selectedConstraintId);
  if (selected && !visible.includes(selected)) visible.unshift(selected);
  const list = document.createElement('div');
  list.className = 'constraint-list';
  for (const rule of visible) {
    const row = document.createElement('button');
    row.className = 'constraint-row';
    row.dataset.constraint = rule.id;
    row.setAttribute('aria-pressed', String(rule.id === selectedConstraintId));
    const meta = document.createElement('span');
    meta.className = 'constraint-row-meta';
    meta.textContent = `${rule.origin === 'local' ? constraintText('本地规范', 'Local rule') : rule.origin === 'user' ? constraintText('用户要求', 'User request') : constraintText('代码推断', 'Inferred')} · ${rule.strength === 'required' ? constraintText('硬性要求', 'Required') : constraintText('偏好', 'Preferred')}`;
    const name = document.createElement('strong');
    name.textContent = localized(rule, 'name');
    const state = document.createElement('span');
    state.className = 'constraint-state';
    state.dataset.state = rule.applicability;
    state.textContent = constraintStates[rule.applicability][isChinese() ? 0 : 1];
    const review = event?.constraintReviews?.find(item => item.constraintId === rule.id);
    state.dataset.result = review?.status || 'unverified';
    if (event && applicable.includes(rule)) state.textContent += ` · ${constraintStates[review?.status || 'unverified'][isChinese() ? 0 : 1]}`;
    row.append(meta, name, state);
    const fileReview = freshness?.rules[rule.id];
    const fileState = document.createElement('span');
    fileState.className = 'constraint-freshness';
    fileState.dataset.state = fileReview?.status || 'unverified';
    fileState.textContent = freshnessStates[fileReview?.status || 'unverified'][isChinese() ? 0 : 1];
    row.append(fileState);
    row.onclick = () => { selectedConstraintId = selectedConstraintId === rule.id ? undefined : rule.id; updateConstraints(); constraintsPanel.querySelector<HTMLButtonElement>(`[data-constraint="${rule.id}"]`)?.focus(); };
    list.append(row);
    if (rule.id === selectedConstraintId) {
      const detail = document.createElement('div');
      detail.className = 'constraint-detail';
      const field = (label: string, value: string) => {
        const title = document.createElement('h3'); title.textContent = label;
        const content = document.createElement('p'); content.textContent = value;
        detail.append(title, content);
      };
      field(constraintText('适用依据', 'Applicability'), localized(rule, 'note'));
      if (rule.explanation) field(constraintText('具体解释', 'Explanation'), localized(rule, 'explanation'));
      const names = [...constraintModules(rule)].map(id => localized(required(map.modules.find(module => module.id === id)), 'name'));
      field(constraintText('作用范围', 'Scope'), names.join(' · ') || (rule.scope === 'task' ? required(rule.taskId) : constraintText('整个项目', 'Project-wide')));
      for (const source of rule.evidence) {
        const sourceDetails = document.createElement('details');
        sourceDetails.className = 'constraint-source';
        const location = document.createElement('summary');
        location.textContent = `${source.path}${source.line ? `:${source.line}${source.endLine ? `–${source.endLine}` : ''}` : ''}${source.symbol ? ` · ${source.symbol}` : ''}`;
        const sourceNote = document.createElement('p'); sourceNote.textContent = localized(source, 'note');
        sourceDetails.append(location);
        if (source.quote) {
          sourceDetails.open = true;
          const quoteLabel = document.createElement('h3'); quoteLabel.textContent = constraintText('来源摘录（原语言）', 'Source excerpt (original language)');
          const quote = document.createElement('blockquote'); quote.textContent = source.quote;
          sourceDetails.append(quoteLabel, quote);
        }
        sourceDetails.append(sourceNote); detail.append(sourceDetails);
      }
      field(constraintText('关联代码', 'Linked code'), (rule.code || []).map(source =>
        `${source.path}${source.line ? `:${source.line}` : ''}${source.symbol ? ` · ${source.symbol}` : ''}\n${localized(source, 'note')}`
      ).join('\n\n') || constraintText('未记录代码关联', 'No code links recorded'));
      field(constraintText('变化核对', 'Change inspection'), fileState.textContent || '');
      if (rule.baselineCommit) field(constraintText('基准提交', 'Baseline commit'), rule.baselineCommit);
      for (const id of [rule.supersededBy, ...(rule.conflictsWith || [])].filter(Boolean)) {
        const linked = constraintRules.find(item => item.id === id);
        const link = document.createElement('button'); link.className = 'constraint-module-link';
        link.textContent = `${constraintText('关联规则', 'Related rule')}: ${localized(required(linked), 'name')}`;
        link.onclick = () => { selectedConstraintId = id; constraintFilter = 'all'; updateConstraints(); };
        detail.append(link);
      }
      field(constraintText('验证方式', 'Verification'), localized(rule, 'verification'));
      if (event && applicable.includes(rule)) {
        field(constraintText('本次方案', 'Task plan'), review ? localized(review, 'plan') : constraintText('未记录', 'Not recorded'));
        field(constraintText('验证结果', 'Result'), `${constraintStates[review?.status || 'unverified'][isChinese() ? 0 : 1]}${review ? ` · ${review.method === 'test' ? constraintText('测试', 'Test') : constraintText('人工核对', 'Manual review')}` : ''}`);
        if (review?.evidence) field(constraintText('结果依据', 'Result evidence'), localized(review, 'evidence'));
        if (review?.checkedAt) field(constraintText('复核记录', 'Review record'), `${review.checkedAt}${review.gitCommit ? `\n${review.gitCommit}` : ''}`);
        for (const index of review?.checkIndexes || []) {
          const check = required(event.checks[index]);
          field(check.command, `${check.status} · exit ${check.exitCode ?? '—'}\n${localized(check, 'summary')}`);
        }
      }
      list.append(detail);
    }
  }
  if (!visible.length) {
    const empty = document.createElement('p'); empty.className = 'constraint-empty';
    empty.textContent = constraintRules.length ? constraintText('此范围未记录约束', 'No constraints recorded in this scope') : emptyState; list.append(empty);
  }
  constraintsPanel.append(list);
  const highlighted = open && selected ? constraintModules(selected) : new Set();
  for (const [id, button] of buttons) button.classList.toggle('constraint-highlight', highlighted.has(id));
  for (const edge of edges) edge.path.classList.toggle('constraint-highlight', Boolean(open && selected?.relationships.includes(edge.relation.id)));
  updateFlow();
}

applyLanguage();
// A versioned browser preference, independent of map revisions and activity history.
const guideKey = 'birdview-guide-v1';
const guideLaunch = document.createElement('button');
guideLaunch.id = 'guide-launch';
query('.header-actions').append(guideLaunch);
const guideInvite = document.createElement('div');
guideInvite.id = 'guide-invite';
guideInvite.innerHTML = '<span></span><button id="guide-start"></button><button id="guide-dismiss"></button>';
query('main').prepend(guideInvite);
try { guideInvite.hidden = localStorage.getItem(guideKey) === 'seen'; } catch {}
const guideDialog = document.createElement('dialog');
guideDialog.id = 'guide-dialog';
guideDialog.setAttribute('aria-labelledby', 'guide-title');
guideDialog.setAttribute('aria-describedby', 'guide-copy');
guideDialog.innerHTML = '<div id="guide-spot" aria-hidden="true"></div><section id="guide-card"><div class="guide-top"><span id="guide-count" aria-live="polite"></span><button id="guide-close">×</button></div><progress id="guide-progress"></progress><h2 id="guide-title"></h2><p id="guide-copy"></p><div class="guide-actions"><button id="guide-prev"></button><button id="guide-skip"></button><button id="guide-next" class="primary"></button></div></section>';
document.body.append(guideDialog);
type GuideStep = 'architecture' | 'activity' | 'compare' | 'details' | 'history';
const guideSteps: GuideStep[] = activityEvents.length ? ['architecture', 'activity', 'compare', 'details', 'history'] : ['architecture', 'details'];
const guideCopy: Record<GuideStep, [string, string, string, string]> = {
  architecture: ['完整架构', '了解系统有哪些模块，以及它们如何连接。分组底色表示职责类别，不表示修改状态。', 'Architecture', 'See the system modules and their connections. Group backgrounds classify responsibilities, not change status.'],
  activity: ['本次修改', '亮起的是所选步骤的目标，灰色模块不是当前目标；验证阶段的亮起表示验证目标。终态不再高亮目标。', 'Current changes', 'Bright modules are targets of the selected step; gray modules are not. During verification, highlights mean verification targets. Terminal steps clear highlights.'],
  compare: ['同时对照', '完整架构与更改视图并排展示，选择、缩放和滚动保持联动。窄屏时上下排列。', 'Compare views', 'Compare architecture and changes with linked selection, zoom and scrolling. Narrow screens stack the views.'],
  details: ['查看依据', '点击模块可查看职责、文件归属与源码证据。悬浮模块可追踪直接连接，工具栏可切换全部关系或适配全图。', 'Inspect evidence', 'Select a module for responsibilities, file ownership and source evidence. Hover to trace direct connections; use the toolbar for all relations or fit to view.'],
  history: ['跟踪过程', '历史记录展示计划、编辑和验证步骤。展开详情查看文件和检查结果；任务完成不代表检查通过。', 'Follow progress', 'History shows planning, editing and verification steps. Expand details for files and check results; completion alone does not prove checks passed.']
};
let guideIndex = 0;
interface GuideSaved {
  mode: ViewMode; index: number; selected: string | undefined; inspector: boolean; zoom: number; fitting: boolean; disclosure: boolean;
  focus: Element | null; x: number; y: number; panes: [HTMLElement, number, number][];
  constraints: {open: boolean; selected: string | undefined; filter: string};
}
let guideSaved: GuideSaved | undefined;
let guideTarget: HTMLElement | undefined;
let guideFrame = 0;
const guideViewState: Record<GuideStep, {mode: ViewMode; inspector: boolean; history: boolean}> = {
  architecture: { mode: 'architecture', inspector: false, history: false },
  activity: { mode: 'activity', inspector: false, history: false },
  compare: { mode: 'compare', inspector: false, history: false },
  details: { mode: 'architecture', inspector: true, history: false },
  history: { mode: 'activity', inspector: false, history: true }
};
function guideLabels() {
  const zh = isChinese();
  guideLaunch.textContent = zh ? '使用指引' : 'Guide';
  query('span', guideInvite).textContent = zh ? '了解怎么看图' : 'Learn to read the map';
  $('guide-start').textContent = zh ? '开始' : 'Start';
  $('guide-dismiss').textContent = zh ? '暂不' : 'Not now';
  for (const [id, labels] of Object.entries({ 'guide-close': ['关闭指引', 'Close guide'], 'guide-prev': ['上一步', 'Previous'], 'guide-skip': ['跳过指引', 'Skip guide'] })) {
    $(id).ariaLabel = required(labels[zh ? 0 : 1]);
    if (id !== 'guide-close') $(id).textContent = required(labels[zh ? 0 : 1]);
  }
  const copy = guideCopy[required(guideSteps[guideIndex])];
  $('guide-title').textContent = copy[zh ? 0 : 2];
  $('guide-copy').textContent = copy[zh ? 1 : 3];
  $('guide-count').textContent = zh ? `第 ${guideIndex + 1} / ${guideSteps.length} 步` : `Step ${guideIndex + 1} of ${guideSteps.length}`;
  $('guide-progress').max = guideSteps.length;
  $('guide-progress').value = guideIndex + 1;
  $('guide-progress').ariaLabel = $('guide-count').textContent;
  buttonById('guide-prev').disabled = guideIndex === 0;
  $('guide-next').textContent = guideIndex === guideSteps.length - 1 ? (zh ? '完成' : 'Done') : (zh ? '下一步' : 'Next');
}
function positionGuide() {
  if (!guideDialog.open || !guideTarget) return;
  const rect = guideTarget.getBoundingClientRect();
  const w = innerWidth, h = innerHeight;
  const left = Math.max(6, Math.min(w - 12, rect.left - 5));
  const top = Math.max(6, Math.min(h - 12, rect.top - 5));
  const right = Math.max(left + 6, Math.min(w - 6, rect.right + 5));
  const bottom = Math.max(top + 6, Math.min(h - 6, rect.bottom + 5));
  Object.assign($('guide-spot').style, { left: `${left}px`, top: `${top}px`, width: `${right - left}px`, height: `${bottom - top}px` });
  const card = $('guide-card');
  const cw = card.offsetWidth, ch = card.offsetHeight;
  let x = left, y = bottom + 14;
  if (y + ch > h - 12) {
    if (top - ch - 14 >= 12) y = top - ch - 14;
    else if (right + cw + 14 < w - 12) { x = right + 14; y = top; }
    else { x = w - cw - 12; y = h - ch - 12; }
  }
  card.style.left = `${Math.max(12, Math.min(w - cw - 12, x))}px`;
  card.style.top = `${Math.max(12, Math.min(h - ch - 12, y))}px`;
}
let guideAnimation: Animation | undefined;
function showGuideStep(animate = false) {
  const card = $('guide-card');
  const previous = card.getBoundingClientRect();
  guideAnimation?.cancel();
  guideAnimation = undefined;
  const saved = required(guideSaved);
  const step = required(guideSteps[guideIndex]);
  const state = guideViewState[step];
  hoveredModuleId = undefined;
  setInspector(state.inspector);
  activityMode = state.mode;
  if (step === 'activity') {
    const plan = activityEvents.findIndex(event => event.phase === 'planned' && event.targets.length);
    activityIndex = plan >= 0 ? plan : saved.index;
  } else activityIndex = saved.index;
  $('activity-disclosure').open = state.history;
  fitting = true;
  updateActivity();
  updateFlow();
  updateZoom();
  if (step === 'details') select(map.modules.find(module => module.id === saved.selected) || required(map.modules[0]));
  guideTarget = step === 'details' ? inspector : step === 'history' ? activityPanel : step === 'compare' ? $('activity-mode') : step === 'activity' ? viewport : activityEvents.length ? query('[data-view="architecture"]') : viewport;
  guideTarget.scrollIntoView({ block: 'nearest', behavior: 'instant' });
  guideLabels();
  positionGuide();
  if (animate && !reducedMotion.matches) {
    const next = card.getBoundingClientRect();
    const x = Math.max(12, Math.min(innerWidth - next.width - 12, previous.left)) - next.left;
    const y = Math.max(12, Math.min(innerHeight - next.height - 12, previous.top)) - next.top;
    guideAnimation = card.animate([
      { transform: `translate(${x}px, ${y}px)` },
      { transform: 'translate(0, 0)' },
    ], { duration: 200, easing: 'cubic-bezier(0.23, 1, 0.32, 1)' });
  }
  requestAnimationFrame(positionGuide);
  $('guide-next').focus({ preventScroll: true });
}
function dismissGuideInvite() {
  guideInvite.hidden = true;
  try { localStorage.setItem(guideKey, 'seen'); } catch {}
}
function startGuide() {
  if (guideDialog.open) return;
  dismissGuideInvite();
  guideSaved = { mode: activityMode, index: activityIndex, selected: selectedModuleId, inspector: workspace.classList.contains('inspector-open'), zoom, fitting, disclosure: $('activity-disclosure').open, focus: document.activeElement, x: scrollX, y: scrollY, constraints: {open: constraintPanelOpen, selected: selectedConstraintId, filter: constraintFilter}, panes: [...mapPanes.querySelectorAll<HTMLElement>('.map-scroll')].map(el => [el, el.scrollLeft, el.scrollTop]) };
  guideIndex = 0;

  constraintPanelOpen = false;
  guideDialog.showModal();
  showGuideStep();
}
function finishGuide() {
  if (!guideDialog.open) return;
  guideAnimation?.cancel();
  guideAnimation = undefined;
  guideDialog.close();
  const saved = required(guideSaved);
  activityMode = saved.mode;
  activityIndex = saved.index;
  constraintPanelOpen = saved.constraints.open;
  selectedConstraintId = saved.constraints.selected;
  constraintFilter = saved.constraints.filter;
  fitting = false;
  setInspector(saved.inspector);
  $('activity-disclosure').open = saved.disclosure;
  updateActivity();
  select(map.modules.find(module => module.id === saved.selected) || required(map.modules[0]));
  zoom = saved.zoom;
  updateZoom();
  fitting = saved.fitting;
  for (const [el, x, y] of saved.panes) el.scrollTo(x, y);
  window.scrollTo(saved.x, saved.y);
  (saved.focus instanceof HTMLElement && saved.focus.isConnected && !saved.focus.closest('#guide-invite') ? saved.focus : guideLaunch).focus({ preventScroll: true });
}
guideLaunch.onclick = $('guide-start').onclick = startGuide;
$('guide-dismiss').onclick = dismissGuideInvite;
$('guide-close').onclick = $('guide-skip').onclick = finishGuide;
$('guide-prev').onclick = event => { if (guideIndex) { guideIndex--; showGuideStep(event.detail > 0); } };
$('guide-next').onclick = event => { if (guideIndex === guideSteps.length - 1) finishGuide(); else { guideIndex++; showGuideStep(event.detail > 0); } };
reducedMotion.addEventListener('change', () => { if (reducedMotion.matches) guideAnimation?.cancel(); });
guideDialog.addEventListener('cancel', event => { event.preventDefault(); finishGuide(); });
languageSelect.addEventListener('change', () => { guideAnimation?.cancel(); guideLabels(); positionGuide(); });
const repositionGuide = () => { guideAnimation?.cancel(); cancelAnimationFrame(guideFrame); guideFrame = requestAnimationFrame(positionGuide); };
window.addEventListener('resize', repositionGuide);
document.addEventListener('scroll', repositionGuide, true);
new ResizeObserver(() => { cancelAnimationFrame(guideFrame); guideFrame = requestAnimationFrame(positionGuide); }).observe($('guide-card'));
guideLabels();

if (DATA.constraintView) {
  const view = DATA.constraintView;
  const main = query('body > main');
  const nav = document.createElement('nav'); nav.id = 'project-views';
  const architecture = document.createElement('button');
  const constraints = document.createElement('button');
  architecture.type = constraints.type = 'button'; nav.append(architecture, constraints);
  query('header .task').after(nav);
  main.id = 'architecture-view'; architecture.setAttribute('aria-controls', main.id);
  const panel = document.createElement('section'); panel.id = 'constraint-view'; panel.hidden = true;
  constraints.setAttribute('aria-controls', panel.id); main.after(panel);
  const related = document.createElement('button'); related.id = 'open-related-constraints'; related.type = 'button';
  $('module-content').append(related);
  let active = false;
  let canvas: ConstraintCanvas | undefined;
  const label = (zh: string, en: string): string => isChinese() ? zh : en;
  const sync = (): void => {
    nav.setAttribute('aria-label', label('项目视图', 'Project views'));
    architecture.textContent = label('架构', 'Architecture'); constraints.textContent = label('约束', 'Constraints');
    architecture.setAttribute('aria-pressed', String(!active)); constraints.setAttribute('aria-pressed', String(active));
    const count = view.rules.filter(rule => rule.modules.includes(selectedModuleId ?? '')).length;
    related.textContent = count ? label(`查看关联约束图 · ${count}`, `View related rules · ${count}`) : label('尚未记录模块与规则的关联', 'No module-rule links recorded');
    related.disabled = !count;
  };
  const show = (value: boolean): void => {
    active = value; main.hidden = value; panel.hidden = !value;
    if (value && !canvas) canvas = mountConstraintCanvas(panel, view.graph);
    const hash = new URLSearchParams(location.hash.slice(1)); hash.set('view', value ? 'constraints' : 'architecture');
    try { history.replaceState(null, '', `#${hash}`); } catch {}
    sync(); requestAnimationFrame(() => canvas?.resize()); window.dispatchEvent(new Event('resize'));
  };
  architecture.onclick = () => show(false); constraints.onclick = () => show(true);
  related.onclick = () => { show(true); canvas?.filter(view.rules.filter(rule => rule.modules.includes(selectedModuleId ?? '')).map(rule => rule.id)); };
  new MutationObserver(sync).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
  new MutationObserver(sync).observe($('module-constraints'), { childList: true, subtree: true });
  show(new URLSearchParams(location.hash.slice(1)).get('view') === 'constraints');
}

