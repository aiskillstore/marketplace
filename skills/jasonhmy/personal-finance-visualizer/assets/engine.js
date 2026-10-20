/* SPDX-License-Identifier: MIT-0 */
(function (root) {
  'use strict';
  const DAY = 86400000;
  const kinds = ['expense', 'income', 'refund', 'transfer_in', 'transfer_out', 'internal'];
  const groups = ['daily', 'fixed', 'ai', 'housing', 'education', 'equipment', 'other'];
  function fail(message) { throw new Error(message); }
  function cents(value) {
    if (typeof value !== 'string' || !/^-?\d+(\.\d{1,2})?$/.test(value)) fail('Amounts must be decimal strings with at most two decimal places.');
    const [whole, fraction = ''] = value.replace('-', '').split('.');
    const result = (Number(whole) * 100 + Number(fraction.padEnd(2, '0'))) * (value.startsWith('-') ? -1 : 1);
    if (!Number.isSafeInteger(result) || Math.abs(result) > 1e11) fail('Amount exceeds the supported range.');
    return result;
  }
  function date(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) fail('Use ISO calendar dates.');
    const d = new Date(value + 'T00:00:00Z');
    if (!Number.isFinite(+d) || d.toISOString().slice(0, 10) !== value || value < '1900-01-01' || value > '2200-12-31') fail('Date is outside the supported range.');
    return d;
  }
  const iso = d => d.toISOString().slice(0, 10);
  function text(value, fallback = '') {
    if (value == null) return fallback;
    if (typeof value !== 'string' || value.length > 1000) fail('Text fields must be strings of at most 1000 characters.');
    return value;
  }
  function validate(input) {
    if (!input || input.schemaVersion !== 1 || !Array.isArray(input.transactions) || input.transactions.length > 100000) fail('Expected schemaVersion 1 and at most 100000 transactions.');
    if (!/^[A-Z]{3}$/.test(input.currency || '')) fail('Use one uppercase three-letter currency code.');
    let currency;
    try { currency = new Intl.NumberFormat('en', {style: 'currency', currency: input.currency}).resolvedOptions(); } catch { fail('Invalid currency.'); }
    if (currency.maximumFractionDigits !== 2) fail('Version 1 supports currencies with two decimal places only.');
    const start = input.coverage?.start, end = input.coverage?.end;
    if (+date(start) > +date(end)) fail('Coverage start must not be after its end.');
    if (+date(end) - +date(start) > 366 * 50 * DAY) fail('Split reports covering more than 50 years.');
    const ids = new Set();
    let absoluteTotal = 0;
    const transactions = input.transactions.map(t => {
      if (!t || typeof t !== 'object') fail('Invalid transaction.');
      const id = text(t.id);
      if (!id || ids.has(id)) fail('Transaction IDs must be present and unique.');
      ids.add(id); date(t.date);
      if (t.date < start || t.date > end) fail('A transaction is outside confirmed coverage.');
      const amountCents = cents(t.amount);
      absoluteTotal += Math.abs(amountCents);
      if (absoluteTotal > 1e11) fail('Report total exceeds supported precision.');
      if (!kinds.includes(t.kind)) fail('Invalid transaction kind.');
      if (['income', 'refund', 'transfer_in'].includes(t.kind) && amountCents <= 0) fail('Incoming records must be positive.');
      if (['expense', 'transfer_out'].includes(t.kind) && amountCents >= 0) fail('Outgoing records must be negative.');
      const group = t.group || 'other';
      const incomeType = t.incomeType || 'other', purpose = t.purpose || 'other';
      if (!['salary','support','other'].includes(incomeType) || !['loan','reimbursement','other'].includes(purpose)) fail('Invalid income or transfer classification.');
      if (!groups.includes(group)) fail('Invalid expense group.');
      const share = t.share == null || t.share === '' ? 1 : Number(t.share);
      if (!Number.isFinite(share) || share < 0 || share > 1 || Math.abs(share * 10000 - Math.round(share * 10000)) > 1e-8) fail('Share must be between zero and one with at most four decimal places.');
      if (t.kind !== 'expense' && share !== 1) fail('Personal shares apply only to expenses.');
      return {id, date: t.date, description: text(t.description), amount: t.amount, amountCents, kind: t.kind, group, share, category: text(t.category, 'Uncategorized'), merchant: text(t.merchant), incomeType, purpose, account: text(t.account), source: text(t.source)};
    });
    const byId = new Map(transactions.map(t => [t.id, t]));
    if (!Array.isArray(input.refunds || []) || !Array.isArray(input.settlements || []) || !Array.isArray(input.notes || [])) fail('Refunds, settlements and notes must be arrays.');
    const used = new Set();
    const refunds = (input.refunds || []).map(r => {
      const purchase = byId.get(r.purchaseId);
      if (!purchase || purchase.kind !== 'expense' || used.has(purchase.id) || !Array.isArray(r.refundIds) || !r.refundIds.length) fail('Invalid or repeated full refund mapping.');
      used.add(purchase.id);
      let sum = 0;
      for (const id of r.refundIds) {
        const refund = byId.get(id);
        if (!refund || refund.kind !== 'refund' || used.has(id)) fail('Invalid or repeated refund record.');
        used.add(id); sum += refund.amountCents;
      }
      if (sum !== -purchase.amountCents) fail('A full refund must exactly offset the purchase. Keep partial or currency-difference refunds separate.');
      return {purchaseId: purchase.id, refundIds: [...r.refundIds]};
    });
    const settled = new Map();
    const settlements = (input.settlements || []).map(s => {
      const out = byId.get(s.outId), incoming = byId.get(s.inId), amount = cents(s.amount);
      if (!out || out.kind !== 'transfer_out' || !incoming || incoming.kind !== 'transfer_in' || amount <= 0) fail('Invalid transfer settlement.');
      for (const t of [out, incoming]) {
        const allocated = (settled.get(t.id) || 0) + amount;
        if (allocated > Math.abs(t.amountCents)) fail('Settlement allocations exceed a transfer amount.');
        settled.set(t.id, allocated);
      }
      return {outId: out.id, inId: incoming.id, amount: s.amount};
    });
    return {schemaVersion: 1, currency: input.currency, language: input.language === 'zh-CN' ? 'zh-CN' : 'en', coverage: {start,end}, transactions, refunds, settlements, notes: (input.notes || []).map(n => text(n)), demo: input.demo === true};
  }
  function periods(data, grain) {
    if (!['day','week','month','year'].includes(grain)) fail('Invalid period scale.');
    const start = date(data.coverage.start), end = date(data.coverage.end);
    let current = new Date(start);
    if (grain === 'week') current.setUTCDate(current.getUTCDate() - (current.getUTCDay() + 6) % 7);
    if (grain === 'month') current.setUTCDate(1);
    if (grain === 'year') current = new Date(Date.UTC(current.getUTCFullYear(),0,1));
    const result = [];
    while (current <= end) {
      const next = new Date(current);
      if (grain === 'day' || grain === 'week') next.setUTCDate(next.getUTCDate() + (grain === 'day' ? 1 : 7));
      else if (grain === 'month') next.setUTCMonth(next.getUTCMonth() + 1);
      else next.setUTCFullYear(next.getUTCFullYear() + 1);
      const key = iso(current), a = iso(new Date(Math.max(+current, +start))), b = iso(new Date(Math.min(+next - DAY, +end)));
      result.push({key, label: grain === 'year' ? key.slice(0,4) : grain === 'month' ? key.slice(0,7) : grain === 'week' ? a + ' – ' + b : a, start:a, end:b});
      current = next;
    }
    return result;
  }
  function summarize(data, period) {
    const matched = new Set(data.refunds.flatMap(r => [r.purchaseId, ...r.refundIds]));
    const settled = new Map();
    for (const s of data.settlements) for (const id of [s.outId, s.inId]) settled.set(id,(settled.get(id)||0)+cents(s.amount));
    const result = {inflow:0,outflow:0,net:0,spending:0,daily:0,dailyAverage:0,income:0,transferIn:0,transferOut:0,unpairedRefunds:0,groups:Object.fromEntries(groups.map(g=>[g,0])),rows:[],days:(+date(period.end)-+date(period.start))/DAY+1};
    // Use 1/10000-cent units for exact proportional accumulation; round only for display.
    const units = Object.fromEntries(groups.map(g=>[g,0]));
    for (const t of data.transactions) {
      if (t.date < period.start || t.date > period.end) continue;
      const settledCents = settled.get(t.id)||0;
      const cashCents = t.kind === 'internal' ? 0 : Math.sign(t.amountCents) * (Math.abs(t.amountCents)-settledCents);
      const personalUnits = t.kind === 'expense' && !matched.has(t.id) ? -t.amountCents * Math.round(t.share * 10000) : 0;
      const transferCents = t.kind.startsWith('transfer_') ? cashCents : 0;
      result.rows.push({...t, personalCents:personalUnits/10000,cashCents,transferCents,matchedRefund:matched.has(t.id),settledCents});
      if (cashCents >= 0) result.inflow += cashCents; else result.outflow -= cashCents;
      if (t.kind === 'income') result.income += t.amountCents;
      if (transferCents > 0) result.transferIn += transferCents; else result.transferOut -= transferCents;
      if (t.kind === 'refund' && !matched.has(t.id)) result.unpairedRefunds += t.amountCents;
      units[t.group] += personalUnits;
    }
    for (const g of groups) result.groups[g] = units[g]/10000;
    result.spending = Object.values(units).reduce((a,b)=>a+b,0)/10000;
    result.daily = result.groups.daily;
    result.dailyAverage = result.daily / result.days;
    result.net = result.inflow - result.outflow;
    result.rows.sort((a,b)=>b.date.localeCompare(a.date)||a.id.localeCompare(b.id));
    return result;
  }
  const api = {validate, periods, summarize, cents};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.Finance = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
