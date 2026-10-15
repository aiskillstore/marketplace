(function (root) {
  'use strict';
  const G = typeof module !== 'undefined' && module.exports ? require('./geometry.js') : root.TechnicalGeometry;
  const {add, sub, dot, cross, ROLES} = G;
  const SHEET = {width: 420, height: 297, margin: 28};

  function createCamera({azimuth = -135, elevation = Math.asin(1 / Math.sqrt(3)) * 180 / Math.PI, roll = 16} = {}) {
    if (![azimuth, elevation, roll].every(Number.isFinite) || Math.abs(elevation) > 90) throw Error('Invalid camera angles');
    const a = azimuth * Math.PI / 180, e = elevation * Math.PI / 180, r = roll * Math.PI / 180;
    const direction = [Math.cos(e) * Math.cos(a), Math.cos(e) * Math.sin(a), Math.sin(e)];
    const right = [-Math.sin(a), Math.cos(a), 0], up = cross(direction, right);
    return {
      direction,
      project: p => {
        const x = dot(p, right), y = -dot(p, up);
        return [x * Math.cos(r) - y * Math.sin(r), x * Math.sin(r) + y * Math.cos(r), dot(p, direction)];
      }
    };
  }
  const defaultCamera = createCamera();
  const project = (point, camera) => (camera ? createCamera(camera) : defaultCamera).project(point);

  const escape = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
  const round = n => Number(n.toFixed(4));
  const rank = line => ROLES.indexOf(line.role);

  function contours(part, direction) {
    const edges = new Map();
    for (const f of part.triangles) {
      const ab = sub(part.vertices[f[1]], part.vertices[f[0]]), ac = sub(part.vertices[f[2]], part.vertices[f[0]]), n = cross(ab, ac);
      const length = Math.hypot(...n);
      if (length <= Math.hypot(...ab) * Math.hypot(...ac) * 1e-12) continue;
      for (let j = 0; j < 3; j++) {
        const a = f[j], b = f[(j + 1) % 3], key = a < b ? `${a}:${b}` : `${b}:${a}`;
        if (!edges.has(key)) edges.set(key, {a, b, signs: []});
        edges.get(key).signs.push(dot(n, direction) / length);
      }
    }
    return [...edges.values()]
      .filter(e => {
        const low = Math.min(...e.signs), high = Math.max(...e.signs);
        return low <= 1e-8 && high >= -1e-8 && (low < -1e-8 || high > 1e-8);
      })
      .map(({a, b}) => ({a: part.vertices[a], b: part.vertices[b], role: 'outline'}));
  }

  function render(parts, {explosion = 1, isolated = null, sample = .045, camera} = {}) {
    if (!Number.isFinite(explosion) || explosion < 0 || explosion > 2) throw Error('Explosion must be 0–2');
    if (!Number.isFinite(sample) || sample < .01 || sample > .2) throw Error('Invalid paper-space sampling');
    const view = camera ? createCamera(camera) : defaultCamera;
    const visibleParts = isolated === null ? parts : parts.filter(p => String(p.id) === String(isolated));
    if (!visibleParts.length) throw Error('Unknown part');
    const meshes = visibleParts.map(p => {
      const offset = p.explosion.map(n => n * explosion);
      return {part: p, offset, points: p.vertices.map(v => view.project(add(v, offset)))};
    });

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const mesh of meshes) {
      for (const p of mesh.points) {
        minX = Math.min(minX, p[0]);
        minY = Math.min(minY, p[1]);
        maxX = Math.max(maxX, p[0]);
        maxY = Math.max(maxY, p[1]);
      }
    }
    if (![minX, minY, maxX, maxY].every(Number.isFinite)) throw Error('Drawing geometry must contain finite vertices');
    const scale = Math.min((SHEET.width - SHEET.margin * 2) / (maxX - minX || 1), (SHEET.height - SHEET.margin * 2) / (maxY - minY || 1));
    const bounds = {width: (maxX - minX) * scale, height: (maxY - minY) * scale};
    bounds.x = (SHEET.width - bounds.width) / 2;
    bounds.y = (SHEET.height - bounds.height) / 2;
    const offset = [bounds.x - minX * scale, bounds.y - minY * scale];
    const depthTolerance = .01 / scale;
    const paper = p => [offset[0] + p[0] * scale, offset[1] + p[1] * scale, p[2]];

    const triangles = [], cells = new Map(), cellSize = 1.5;
    const cell = n => Math.floor(n / cellSize);
    for (const mesh of meshes) {
      mesh.points = mesh.points.map(paper);
      for (const face of mesh.part.triangles) {
        const [a, b, c] = face.map(i => mesh.points[i]);
        const den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1]);
        if (Math.abs(den) < 1e-10) continue;
        const id = triangles.push({a, b, c, den}) - 1;
        for (let x = cell(Math.min(a[0], b[0], c[0])); x <= cell(Math.max(a[0], b[0], c[0])); x++) {
          for (let y = cell(Math.min(a[1], b[1], c[1])); y <= cell(Math.max(a[1], b[1], c[1])); y++) {
            const key = x + ',' + y;
            if (!cells.has(key)) cells.set(key, []);
            cells.get(key).push(id);
          }
        }
      }
    }
    const visible = p => {
      for (const id of cells.get(cell(p[0]) + ',' + cell(p[1])) || []) {
        const {a, b, c, den} = triangles[id];
        const u = ((b[1] - c[1]) * (p[0] - c[0]) + (c[0] - b[0]) * (p[1] - c[1])) / den;
        if (u < -.000001 || u > 1.000001) continue;
        const v = ((c[1] - a[1]) * (p[0] - c[0]) + (a[0] - c[0]) * (p[1] - c[1])) / den;
        if (v < -.000001 || u + v > 1.000001) continue;
        if (u * a[2] + v * b[2] + (1 - u - v) * c[2] > p[2] + depthTolerance) return false;
      }
      return true;
    };
    const segment = (from, to) => `M${round(from[0])} ${round(from[1])}L${round(to[0])} ${round(to[1])}`;

    const groups = meshes.map(mesh => {
      const p = mesh.part, paths = new Map(), seen = new Set();
      const lines = [...p.lines, ...contours(p, view.direction)].sort((a, b) => rank(a) - rank(b));
      for (const line of lines) {
        const a = paper(view.project(add(line.a, mesh.offset))), b = paper(view.project(add(line.b, mesh.offset)));
        const key = [a, b].map(point => point.map(round).join(',')).sort().join('|');
        if (seen.has(key)) continue;
        seen.add(key);
        const steps = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / sample));
        let run = null, previous = null, d = '';
        for (let i = 0; i <= steps; i++) {
          const point = a.map((n, k) => n + (b[k] - n) * i / steps);
          if (visible(point)) {
            run ??= point;
          } else if (run !== null) {
            if (previous) d += segment(run, previous);
            run = null;
          }
          previous = point;
        }
        if (run !== null) d += segment(run, previous);
        if (d) paths.set(line.role, (paths.get(line.role) || '') + d);
      }
      const slug = p.name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      const ink = [...paths].map(([role, d]) => `<path data-line-role="${role}" fill="none" d="${d}"/>`).join('');
      return `<g id="part-${escape(p.id)}-${escape(slug)}" data-item="${escape(p.id)}" data-name="${escape(p.name)}"><title>${escape(p.name)}</title>${ink}</g>`;
    });
    return {markup: groups.join(''), bounds, scale, offset};
  }

  const api = {SHEET, createCamera, project, render};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.TechnicalProjection = api;
})(globalThis);
