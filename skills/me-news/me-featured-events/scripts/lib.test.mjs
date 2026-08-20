import assert from 'node:assert/strict';
import test from 'node:test';
import { ensureNodeVersion, formatEvent, formatEventTime } from './lib.mjs';

const base = { start_time: '2026-08-27 14:00:00', timezone: 'Asia/Shanghai' };

test('requires Node.js 18 or newer', () => {
  assert.throws(() => ensureNodeVersion('16.20.2'), /Node\.js 18 or newer is required/);
  assert.doesNotThrow(() => ensureNodeVersion('18.0.0'));
});

test('formats a same-day time range', () => {
  assert.deepEqual(formatEventTime({ ...base, end_time: '2026-08-27 18:00:00' }), {
    label: '8月27日 14:00–18:00（UTC+8）', warning: null,
  });
});

test('formats a cross-day time range', () => {
  assert.deepEqual(formatEventTime({ ...base, start_time: '2026-08-27 14:30:00', end_time: '2026-08-28 15:30:00' }), {
    label: '8月27日 14:30–8月28日 15:30（UTC+8）', warning: null,
  });
});

test('marks a missing end time', () => {
  assert.deepEqual(formatEventTime({ ...base, end_time: null }), {
    label: '8月27日 14:00（UTC+8）', warning: '结束时间未提供',
  });
});

test('marks an end time earlier than the start time as suspicious', () => {
  assert.deepEqual(formatEventTime({ ...base, start_time: '2026-08-26 20:00:00', end_time: '2026-08-26 00:00:00' }), {
    label: '8月26日 20:00（UTC+8）', warning: '⚠️ 结束时间疑似异常',
  });
});

test('marks an end time equal to the start time as suspicious', () => {
  assert.equal(formatEventTime({ ...base, end_time: base.start_time }).warning, '⚠️ 结束时间疑似异常');
});

test('marks an invalid end time', () => {
  assert.equal(formatEventTime({ ...base, end_time: 'not-a-time' }).warning, '⚠️ 结束时间格式异常');
});

test('cleans HTML and truncates the description to 50 characters', () => {
  const output = formatEvent({
    ...base,
    title: '测试活动',
    description: `<p>${'活动介绍'.repeat(13)}</p>`,
    end_time: '2026-08-27 18:00:00',
    address: '香港',
  });
  assert.match(output, new RegExp(`^测试活动\\n${'活动介绍'.repeat(12)}活动…\\n`));
});

test('uses a factual fallback when the description is empty', () => {
  const output = formatEvent({
    ...base,
    title: '测试活动',
    description: '',
    end_time: '2026-08-27 18:00:00',
    address: '香港',
  });
  assert.match(output, /^测试活动\n测试活动，地点：香港。\n/);
});
