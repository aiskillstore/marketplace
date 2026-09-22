export type Point = [number, number];
export interface Position { x: number; y: number }
export interface Connection { from: string; to: string }
export interface Route { points: Point[]; d: string }
interface Box extends Position { id: string; w: number; h: number }
type Side = 'top' | 'right' | 'bottom' | 'left';
interface Port { box: Box; side: Side; peer: Box; point?: Point; stub?: Point }

// Bounds are guaranteed by the routing grid; fail explicitly if that invariant breaks.
function requiredAt<T>(values: readonly T[], index: number): T {
  const value = values[index];
  if (value === undefined) throw new Error(`Missing routing grid value at ${index}.`);
  return value;
}

// Orthogonal routing on the free corridors around module rectangles.
export function routeArchitecture(relationships: readonly Connection[], positions: ReadonlyMap<string, Position>): Route[] {
  const gap = 10;
  const boxes = [...positions].map(([id, p]) => ({ id, x: p.x, y: p.y, w: 164, h: 72 }));
  const boxById = new Map(boxes.map(b => [b.id, b]));
  const obstacles = boxes.map(b => ({ x: b.x - gap, y: b.y - gap, w: b.w + gap * 2, h: b.h + gap * 2 }));
  const ports = new Map<string, Port[]>();
  const routes = relationships.map(relation => {
    const from = boxById.get(relation.from), to = boxById.get(relation.to);
    if (!from || !to) throw new Error(`Missing position for ${relation.from} → ${relation.to}.`);
    const dx = to.x - from.x, dy = to.y - from.y;
    let sides: [Side, Side] = from === to ? ['top', 'right'] : Math.abs(dx) >= Math.abs(dy)
      ? (dx >= 0 ? ['right', 'left'] : ['left', 'right'])
      : (dy >= 0 ? ['bottom', 'top'] : ['top', 'bottom']);
    // Diagonal neighbors can connect with one turn instead of sharing a vertical
    // corridor with every horizontal neighbor. Balance endpoint load on ties.
    if (Math.abs(dx) >= from.w + gap * 2 && Math.abs(dy) >= from.h + gap * 2) {
      const horizontal: [Side, Side] = dx > 0 ? ['right', 'left'] : ['left', 'right'];
      const vertical: [Side, Side] = dy > 0 ? ['bottom', 'top'] : ['top', 'bottom'];
      const candidates: [Side, Side][] = [[vertical[0], horizontal[1]], [horizontal[0], vertical[1]]];
      const load = (pair: [Side, Side]) => (ports.get(`${from.id}:${pair[0]}`)?.length || 0)
        + (ports.get(`${to.id}:${pair[1]}`)?.length || 0);
      candidates.sort((a,b) => load(a) - load(b));
      sides = requiredAt(candidates, 0);
    }
    const pair = [from, to].map((box, index) => {
      const port: Port = { box, side: requiredAt(sides, index), peer: index ? from : to };
      const key = `${box.id}:${port.side}`;
      const list = ports.get(key) ?? [];
      list.push(port);
      ports.set(key, list);
      return port;
    });
    return { relation, start: requiredAt(pair, 0), end: requiredAt(pair, 1) };
  });
  for (const list of ports.values()) {
    const horizontal = ['top', 'bottom'].includes(requiredAt(list, 0).side);
    list.sort((a, b) => horizontal ? a.peer.x - b.peer.x : a.peer.y - b.peer.y);
    list.forEach((port, index) => {
      const { box, side } = port;
      const offset = (index + 1) / (list.length + 1);
      port.point = horizontal
        ? [box.x + 16 + (box.w - 32) * offset, box.y + (side === 'bottom' ? box.h : 0)]
        : [box.x + (side === 'right' ? box.w : 0), box.y + 12 + (box.h - 24) * offset];
      port.stub = [port.point[0] + (side === 'left' ? -gap : side === 'right' ? gap : 0),
        port.point[1] + (side === 'top' ? -gap : side === 'bottom' ? gap : 0)];
    });
  }
  const used: [Point, Point][] = [];
  // Include the middle of each free row/column corridor, rather than routing
  // exclusively along card edges. Long connections can use the outside lane.
  const centers = (values: number[], size: number) => {
    const sorted = [...new Set(values)].sort((a,b) => a-b);
    return sorted.slice(1).map((value,i) => (requiredAt(sorted, i) + size + value) / 2);
  };
  const lanesX = centers(boxes.map(b => b.x), 164);
  const lanesY = centers(boxes.map(b => b.y), 72);
  const outerY = Math.max(...boxes.map(b => b.y + b.h)) + 24;
  return routes.map(({ start, end, relation }) => {
    const startStub = start.stub, endStub = end.stub, startPoint = start.point, endPoint = end.point;
    if (!startStub || !endStub || !startPoint || !endPoint) throw new Error('Routing ports have not been positioned.');
    const xs = [...new Set([...lanesX, ...obstacles.flatMap(b => [b.x - 8, b.x, b.x + b.w, b.x + b.w + 8]), startStub[0], endStub[0]])].sort((a,b) => a-b);
    const ys = [...new Set([...lanesY, outerY, outerY + 10, ...obstacles.flatMap(b => [b.y - 8, b.y, b.y + b.h, b.y + b.h + 8]), startStub[1], endStub[1]])].sort((a,b) => a-b);
    const pointAt = (id: number): Point => [requiredAt(xs, id % xs.length), requiredAt(ys, Math.floor(id / xs.length))];
    const indexOf = (p: Point) => ys.indexOf(p[1]) * xs.length + xs.indexOf(p[0]);
    const clear = (a: Point, b: Point) => !obstacles.some(r => a[0] === b[0]
      ? a[0] > r.x && a[0] < r.x + r.w && Math.max(a[1], b[1]) > r.y && Math.min(a[1], b[1]) < r.y + r.h
      : a[1] > r.y && a[1] < r.y + r.h && Math.max(a[0], b[0]) > r.x && Math.min(a[0], b[0]) < r.x + r.w);
    const source = indexOf(startStub), target = indexOf(endStub);
    const axis = (p: Port) => p.side === 'left' || p.side === 'right' ? 0 : 1;
    const initial = source * 2 + axis(start);
    const distance = new Map([[initial, 0]]), previous = new Map<number, number>();
    const queue = [{ state: initial, cost: 0, rank: 0 }];
    let found: number | undefined;
    while (queue.length) {
      queue.sort((a,b) => b.rank - a.rank);
      const current = queue.pop();
      if (!current) break;
      if (current.cost !== distance.get(current.state)) continue;
      const id = Math.floor(current.state / 2), a = pointAt(id);
      if (id === target) { found = current.state; break; }
      const col = id % xs.length, row = Math.floor(id / xs.length);
      const neighbors = [col > 0 ? id - 1 : -1, col + 1 < xs.length ? id + 1 : -1,
        row > 0 ? id - xs.length : -1, row + 1 < ys.length ? id + xs.length : -1];
      for (const next of neighbors) {
        if (next < 0) continue;
        const b = pointAt(next), direction = a[0] === b[0] ? 1 : 0;
        if (!clear(a, b)) continue;
        let penalty = current.state % 2 === direction ? 0 : 18;
        if (next === target && direction !== axis(end)) penalty += 18;
        for (const [c, d] of used) {
          const otherDirection = c[0] === d[0] ? 1 : 0;
          if (direction === otherDirection) {
            const fixed = direction === 0 ? 1 : 0;
            const overlap = Math.min(Math.max(a[direction], b[direction]), Math.max(c[direction], d[direction])) - Math.max(Math.min(a[direction], b[direction]), Math.min(c[direction], d[direction]));
            const separation = Math.abs(a[fixed] - c[fixed]);
            // Penalize length, not grid steps, so adding lanes does not change
            // the price of following the same occupied corridor.
            if (overlap > 0 && separation < 8) penalty += overlap * (1 - separation / 8) * 2;
          } else if (Math.min(a[0], b[0]) <= Math.max(c[0], d[0]) && Math.max(a[0], b[0]) >= Math.min(c[0], d[0]) && Math.min(a[1], b[1]) <= Math.max(c[1], d[1]) && Math.max(a[1], b[1]) >= Math.min(c[1], d[1])) penalty += 24;
        }
        const cost = current.cost + Math.abs(b[0]-a[0]) + Math.abs(b[1]-a[1]) + penalty;
        const state = next * 2 + direction;
        if (cost >= (distance.get(state) ?? Infinity)) continue;
        distance.set(state, cost); previous.set(state, current.state);
        queue.push({ state, cost, rank: cost + Math.abs(b[0]-endStub[0]) + Math.abs(b[1]-endStub[1]) });
      }
    }
    if (found === undefined) throw new Error(`Cannot route ${relation.from} → ${relation.to} without crossing a module.`);
    const middle: Point[] = [];
    for (let state: number | undefined = found; state !== undefined; state = previous.get(state)) middle.push(pointAt(Math.floor(state / 2)));
    const points = [startPoint, ...middle.reverse(), endPoint];
    for (let i = points.length - 2; i > 0; i--) {
      const a = requiredAt(points, i-1), b = requiredAt(points, i), c = requiredAt(points, i+1);
      if ((a[0] === b[0] && b[0] === c[0]) || (a[1] === b[1] && b[1] === c[1])) points.splice(i,1);
    }
    for (let i=1;i<points.length;i++) used.push([requiredAt(points, i-1), requiredAt(points, i)]);
    let d = `M ${requiredAt(points, 0).join(' ')}`;
    for (let i=1;i<points.length-1;i++) {
      const a = requiredAt(points, i-1), b = requiredAt(points, i), c = requiredAt(points, i+1);
      const before = Math.hypot(b[0]-a[0],b[1]-a[1]), after = Math.hypot(c[0]-b[0],c[1]-b[1]);
      const radius = Math.min(6,before/2,after/2);
      const entry = b.map((v,k) => v+(requiredAt(a, k)-v)*radius/before);
      const exit = b.map((v,k) => v+(requiredAt(c, k)-v)*radius/after);
      d += ` L ${entry.join(' ')} Q ${b.join(' ')} ${exit.join(' ')}`;
    }
    d += ` L ${requiredAt(points, points.length-1).join(' ')}`;
    return { points, d };
  });
}
