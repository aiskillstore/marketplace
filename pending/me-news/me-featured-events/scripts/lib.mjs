import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

export const API_BASE = 'https://api.me.news/skill/events';
export const DEFAULT_STATE = resolve(process.cwd(), 'memory/me-featured-events.json');
export const SKILL_VERSION = '1.1.0';
export const MIN_NODE_MAJOR = 18;

export function ensureNodeVersion(version = process.versions.node) {
  const major = Number.parseInt(String(version).split('.')[0], 10);
  if (!Number.isInteger(major) || major < MIN_NODE_MAJOR) {
    throw new Error(`Node.js ${MIN_NODE_MAJOR} or newer is required; found ${version}`);
  }
}

export function parseArgs(argv, allowedKeys) {
  const allowed = new Set(allowedKeys);
  const args = Object.create(null);
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith('--')) throw new Error(`Unexpected argument: ${token}`);
    const key = token.slice(2);
    if (!allowed.has(key)) throw new Error(`Unknown option: --${key}`);
    if (Object.hasOwn(args, key)) throw new Error(`Duplicate option: --${key}`);
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for --${key}`);
    args[key] = value;
    index += 1;
  }
  return args;
}

export function integerArg(value, name, minimum, maximum) {
  if (value === undefined) return undefined;
  if (!/^-?\d+$/.test(value)) throw new Error(`${name} must be an integer`);
  const number = Number(value);
  if (!Number.isSafeInteger(number) || number < minimum || number > maximum) {
    throw new Error(`${name} must be between ${minimum} and ${maximum}`);
  }
  return number;
}

export function dateArg(value, name) {
  if (value === undefined) return undefined;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error(`${name} must use YYYY-MM-DD`);
  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) {
    throw new Error(`${name} must be a valid calendar date`);
  }
  return value;
}

export function timezoneArg(value) {
  if (value === undefined) return undefined;
  try {
    new Intl.DateTimeFormat('en', { timeZone: value }).format();
  } catch {
    throw new Error('--timezone must be a valid IANA time zone');
  }
  return value;
}

export function csv(value) {
  return value ? [...new Set(value.split(',').map((item) => item.trim()).filter(Boolean))] : [];
}

export async function request(path, params = {}) {
  const url = new URL(`${API_BASE}/${path}`);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, String(value));
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30_000);
  let response;
  try {
    response = await fetch(url, {
      headers: { accept: 'application/json', 'user-agent': `me-featured-events/${SKILL_VERSION}` },
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }
  if (!response.ok) throw new Error(`HTTP ${response.status} from ${url.pathname}`);
  const body = await response.json();
  if (body?.code !== 200 || !body.data) throw new Error(body?.message || `Invalid response from ${url.pathname}`);
  return body.data;
}

export async function loadState(path) {
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch (error) {
    if (error.code === 'ENOENT') throw new Error(`State not found: ${path}. Run init-subscription.mjs first.`);
    throw error;
  }
}

export async function loadStateIfExists(path) {
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

export async function saveState(path, state) {
  await mkdir(dirname(path), { recursive: true });
  const temporary = `${path}.${process.pid}.tmp`;
  await writeFile(temporary, `${JSON.stringify(state, null, 2)}\n`, { mode: 0o600 });
  await rename(temporary, path);
}

export function filterParams(state) {
  return {
    type_ids: state.type_ids?.join(',') || undefined,
    region_ids: state.region_ids?.join(',') || undefined,
  };
}

function cleanText(value) {
  return String(value || '').replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
}

function descriptionExcerpt(event) {
  const description = cleanText(event.description);
  const characters = [...description];
  if (description) return characters.length > 50 ? `${characters.slice(0, 50).join('')}…` : description;
  const place = cleanText(event.address) || cleanText(event.region?.label);
  return `${event.title}${place ? `，地点：${place}` : ''}。`;
}

function parseEventTime(value) {
  const match = String(value || '').match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?$/);
  if (!match) return null;
  const parts = match.slice(1).map((part) => Number(part || 0));
  const [year, month, day, hour, minute, second] = parts;
  const timestamp = Date.UTC(year, month - 1, day, hour, minute, second);
  const parsed = new Date(timestamp);
  if (
    parsed.getUTCFullYear() !== year
    || parsed.getUTCMonth() !== month - 1
    || parsed.getUTCDate() !== day
    || parsed.getUTCHours() !== hour
    || parsed.getUTCMinutes() !== minute
    || parsed.getUTCSeconds() !== second
  ) return null;
  return { year, month, day, hour, minute, timestamp };
}

function dateTimeLabel(time) {
  return `${time.month}月${time.day}日 ${String(time.hour).padStart(2, '0')}:${String(time.minute).padStart(2, '0')}`;
}

function clockLabel(time) {
  return `${String(time.hour).padStart(2, '0')}:${String(time.minute).padStart(2, '0')}`;
}

function timezoneLabel(value) {
  if (!value || value === 'Asia/Shanghai') return 'UTC+8';
  return cleanText(value);
}

export function formatEventTime(event) {
  const start = parseEventTime(event.start_time);
  const zone = timezoneLabel(event.timezone);
  if (!start) return { label: '开始时间格式异常', warning: null };

  const startLabel = dateTimeLabel(start);
  if (!event.end_time) {
    return { label: `${startLabel}（${zone}）`, warning: '结束时间未提供' };
  }

  const end = parseEventTime(event.end_time);
  if (!end) {
    return { label: `${startLabel}（${zone}）`, warning: '⚠️ 结束时间格式异常' };
  }
  if (end.timestamp <= start.timestamp) {
    return { label: `${startLabel}（${zone}）`, warning: '⚠️ 结束时间疑似异常' };
  }

  const sameDay = start.year === end.year && start.month === end.month && start.day === end.day;
  const endLabel = sameDay ? clockLabel(end) : dateTimeLabel(end);
  return { label: `${startLabel}–${endLabel}（${zone}）`, warning: null };
}

export function formatEvent(event, numberedIndex) {
  const place = cleanText(event.address) || cleanText(event.region?.label);
  const time = formatEventTime(event);
  const lines = [
    `${numberedIndex ? `${numberedIndex}. ` : ''}${cleanText(event.title)}`,
    descriptionExcerpt(event),
    [time.label, place].filter(Boolean).join('｜'),
    time.warning,
  ];
  if (event.url) lines.push(String(event.url));
  return lines.filter(Boolean).join('\n');
}

export function formatUpcoming(items, now = new Date()) {
  if (!items.length) return '';
  const shanghaiDate = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(now);
  const tomorrow = new Date(now.getTime() + 86_400_000);
  const tomorrowDate = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(tomorrow);
  const groups = new Map();
  for (const event of items) {
    const date = String(event.start_time || '').slice(0, 10);
    const heading = date === shanghaiDate ? '今日开始' : date === tomorrowDate ? '明日开始' : `${Number(date.slice(5, 7))}月${Number(date.slice(8, 10))}日开始`;
    if (!groups.has(heading)) groups.set(heading, []);
    groups.get(heading).push(event);
  }
  return [...groups].map(([heading, events]) => `${heading}\n\n${events.map((event, index) => formatEvent(event, index + 1)).join('\n\n')}`).join('\n\n');
}

export function formatChanges(items) {
  if (!items.length) return '';
  return `新增会议\n\n${items.map((event) => formatEvent(event)).join('\n\n')}`;
}
